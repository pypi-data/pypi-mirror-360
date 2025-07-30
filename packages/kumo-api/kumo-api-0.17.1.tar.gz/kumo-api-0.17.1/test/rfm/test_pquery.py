import pandas as pd

from kumoapi.pquery import QueryType
from kumoapi.rfm import PQueryDefinition
from kumoapi.rfm.context import REV_REL
from kumoapi.rfm.pquery import (
    Aggregation,
    AggregationType,
    Column,
    Condition,
    Entity,
    RelOp,
    SamplingSpec,
)
from kumoapi.task import TaskType


def test_pquery_definition() -> None:
    query = PQueryDefinition(
        target=Condition(
            left=Aggregation(
                type=AggregationType.COUNT,
                column=Column(table_name='ORDERS', column_name='*'),
                filter=None,
                start=0,
                end=7,
            ),
            op=RelOp.EQ,
            right=0,
        ),
        entity=Entity(
            pkey=Column(table_name='USERS', column_name='USER_ID'),
            ids=[0],
        ),
    )
    assert str(query) == ('PREDICT COUNT(ORDERS.*, 0, 7, days)=0 '
                          'FOR USERS.USER_ID=0')
    edge_types = [
        ('ORDERS', 'USER_ID', 'USERS'),
        ('USERS', f'{REV_REL}USER_ID', 'ORDERS'),
    ]
    assert query.query_type == QueryType.TEMPORAL
    assert query.get_task_type(
        stypes={},
        edge_types=edge_types,
    ) == TaskType.BINARY_CLASSIFICATION
    assert query.target.end_offset == 7 * pd.DateOffset(days=1)
    assert query.column_dict == {}
    assert query.time_tables == ['ORDERS']
    assert query.get_entity_table_names(edge_types) == ('USERS', )
    assert query.get_sampling_specs(edge_types) == [
        SamplingSpec(
            edge_type=('ORDERS', 'USER_ID', 'USERS'),
            hop=1,
            start_offset=0 * pd.DateOffset(days=1),
            end_offset=7 * pd.DateOffset(days=1),
        )
    ]
    assert query.exclude_cols_dict == {}
