import datetime
import grpc
import pandas as pd
import pyarrow as pa

from .input import (
    DateTimeArgType,
    StrListArgType,
    ParamArgType,
    parse_datetime_arg,
    parse_str_list_arg,
    parse_param_arg
)
from .pb import service_pb2, service_pb2_grpc
from .time_util import LOCAL_TIME_OFFSET


__all__ = [
    'DataClient'
]


class _TableService:
    def __init__(self, channel: grpc.Channel, name: str):
        self._name = name
        self._stub = service_pb2_grpc.PDataServiceStub(channel)

    def snapshot(
        self,
        ids: StrListArgType = None,
        fields: StrListArgType = None,
        until: DateTimeArgType = None,
        use_local_time: bool = False,
        params: ParamArgType = None
    ):
        return self._perform_query(
            query_type=service_pb2.QueryType.QUERY_TYPE_SNAPSHOT,
            index_count=1,
            ids=ids,
            fields=fields,
            until=until,
            use_local_time=use_local_time,
            params=params
        )

    def intersect(
        self,
        fields: StrListArgType = None,
        since: DateTimeArgType = None,
        until: DateTimeArgType = None,
        params: ParamArgType = None
    ):
        return self._perform_query(
            query_type=service_pb2.QueryType.QUERY_TYPE_INTERVAL,
            index_count=1,
            fields=fields,
            since=since,
            until=until,
            params=params
        )

    def range(
        self,
        ids: StrListArgType = None,
        fields: StrListArgType = None,
        since: DateTimeArgType = None,
        until: DateTimeArgType = None,
        use_local_time: bool = False,
        params: ParamArgType = None
    ):
        return self._perform_query(
            query_type=service_pb2.QueryType.QUERY_TYPE_TIME,
            index_count=2,
            ids=ids,
            fields=fields,
            since=since,
            until=until,
            use_local_time=use_local_time,
            params=params
        )

    def _perform_query(
        self,
        query_type: service_pb2.QueryType,
        index_count: int,
        ids: StrListArgType = None,
        fields: StrListArgType = None,
        since: DateTimeArgType = None,
        until: DateTimeArgType = None,
        use_local_time: bool = False,
        params: ParamArgType = None
    ):
        params = parse_param_arg(params)
        param_list = []
        for k, v in params.items():
            param_list.append(service_pb2.RequestParam(
                name=k,
                values=v
            ))
        request = service_pb2.GetTableDataRequest(
            name=self._name,
            query_type=query_type,
            ids=parse_str_list_arg(ids),
            fields=parse_str_list_arg(fields),
            since=parse_datetime_arg(since, use_local=use_local_time),
            until=parse_datetime_arg(until, use_local=use_local_time, default_now=True),
            params=param_list
        )

        cursor = self._stub.GetTableData(request=request)

        batches = []
        is_date_series = False
        for chunk in cursor:
            is_date_series = chunk.is_date_series
            with pa.ipc.open_stream(chunk.data) as reader:
                try:
                    while True:
                        batch = reader.read_next_batch()
                        batches.append(batch)
                except StopIteration:
                    pass
        table = pa.Table.from_batches(batches)
        df: pd.DataFrame = table.to_pandas()

        if not is_date_series and use_local_time:
            for i in range(index_count):
                if df.iloc[:, i].dtype == 'datetime64[ms]':
                    df.iloc[:, i] = df.iloc[:, i] + datetime.timedelta(milliseconds=LOCAL_TIME_OFFSET)

        return df.set_index(list(df.columns)[:index_count])


class _TradingDayService:
    def __init__(self, channel: grpc.Channel):
        self._service = _TableService(channel, 'CALENDAR')

    def is_trading_day(
            self,
            dt: DateTimeArgType = None,
            calendar: str = 'CN'
    ) -> bool:
        df = self._service.range(
            ids=[calendar],
            since=dt,
            until=dt
        )
        nr, _ = df.shape
        return nr > 0

    def range(
        self,
        start_dt: DateTimeArgType = None,
        end_dt: DateTimeArgType = None,
        calendar: str = 'CN'
    ):
        df = self._service.range(
            ids=[calendar],
            since=start_dt,
            until=end_dt
        )
        return [x.to_pydatetime() for (_, x) in df.index]


_TABLE_TYPE_MAP = {
    1: 'INTERVAL',
    2: 'SNAPSHOT',
    3: 'TIME',
    4: 'TIME_SNAPSHOT'
}


_FIELD_TYPE_MAP = {
    0: 'NULL',
    1: 'INT8',
    2: 'UINT8',
    3: 'INT32',
    4: 'INT64',
    5: 'FLOAT64',
    6: 'DATE',
    7: 'DATETIME_MS',
    8: 'STRING'
}


_FIELD_PARAM_TYPE_MAP = {
    0: 'VALUE',
    1: 'VALUE_PARAM',
    2: 'REQUIRED_PARAM'
}


class DataClient:
    def __init__(self, host: str, port: int):
        self._channel = grpc.insecure_channel(f'{host}:{port}')
        self._table_service = _TableService(self._channel, '_SERVICE')
        self._field_service = _TableService(self._channel, '_FIELD')

    def list_fields(self, table: str):
        """
        列出指定数据表的所有字段信息。

        参数类型解释：
        - VALUE：普通字段，在查询中填写在fields内；
        - VALUE_PARAM：可选参数。既可以当作普通字段，也可以对它进行筛选（填写在params中，可以指定多个值）；
        - REQUIRED_PARAM：必填参数。用来区分同ID的不同记录，只能填写在params中，且只能指定一个值；
        """
        if not table or not isinstance(table, str):
            raise ValueError('table must be a str')

        field_df = self._field_service.snapshot(fields=[
            'zh', 'type', 'param_type'
        ], params={
            'service': [table]
        })

        field_df['type'] = field_df['type'].map(_FIELD_TYPE_MAP)
        field_df['param_type'] = field_df['param_type'].map(_FIELD_PARAM_TYPE_MAP)

        return field_df

    def list_tables(self):
        """
        列出当前可用的的所有数据表。
        """
        table_df = self._table_service.snapshot(fields=['zh', 'type'])
        table_df['type'] = table_df['type'].map(_TABLE_TYPE_MAP)
        idx = [x for x in table_df.index if not x.startswith('_')]
        return table_df.loc[idx]

    def table(self, name: str):
        return _TableService(self._channel, name)

    @property
    def trading_day(self):
        return _TradingDayService(self._channel)
