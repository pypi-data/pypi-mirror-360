from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional, Set, Tuple, Union

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from kumoapi.common import StrEnum
from kumoapi.pquery import QueryType
from kumoapi.task import TaskType
from kumoapi.typing import DateOffset  # type: ignore
from kumoapi.typing import WITH_PYDANTIC_V2, Stype, TimeUnit


class SamplingSpec(NamedTuple):
    edge_type: Tuple[str, str, str]
    hop: int
    start_offset: Optional[DateOffset]
    end_offset: Optional[DateOffset]


class AggregationType(StrEnum):
    SUM = 'SUM'
    AVG = 'AVG'
    MIN = 'MIN'
    MAX = 'MAX'
    COUNT = 'COUNT'
    LIST_DISTINCT = 'LIST_DISTINCT'


class RelOp(StrEnum):
    EQ = '='
    NEQ = '!='
    LEQ = '<='
    GEQ = '>='
    LT = '<'
    GT = '>'


class MemberOp(StrEnum):
    IN = 'IN'


class BoolOp(StrEnum):
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'


@dataclass(repr=False, frozen=True)
class Column:
    table_name: str
    column_name: str

    @property
    def end_offset(self) -> DateOffset:
        return DateOffset(0)

    @property
    def query_type(self) -> QueryType:
        return QueryType.STATIC

    @property
    def columns(self) -> List[Self]:
        if self.column_name == '*':
            return []
        return [self]

    @property
    def time_tables(self) -> List[str]:
        return []

    def get_sampling_specs(
        self,
        hop: int,
        seed_table_name: str,
        edge_types: List[Tuple[str, str, str]],
    ) -> List[SamplingSpec]:

        if seed_table_name == self.table_name:
            return []

        target_edge_types = [
            edge_type for edge_type in edge_types if
            edge_type[2] == seed_table_name and edge_type[0] == self.table_name
        ]
        if len(target_edge_types) != 1:
            raise ValueError(f"Could not find a unique foreign key from table "
                             f"'{seed_table_name}' to '{self.table_name}'")

        spec = SamplingSpec(
            edge_type=target_edge_types[0],
            hop=hop + 1,
            start_offset=None,
            end_offset=None,
        )
        return [spec]

    def __repr__(self) -> str:
        return f'{self.table_name}.{self.column_name}'


@dataclass(repr=False, frozen=True)
class Aggregation:
    type: AggregationType
    column: Column
    filter: Optional['Filter']
    start: Union[int, float]
    end: int
    time_unit: TimeUnit = TimeUnit.DAYS

    def __post_init__(self) -> None:
        assert self.start < self.end

        if self.filter is not None:  # Only static filters allowed for now:
            assert self.filter.condition.query_type == QueryType.STATIC

    @property
    def end_offset(self) -> DateOffset:
        return self.end * self.time_unit.to_offset()

    @property
    def query_type(self) -> QueryType:
        return QueryType.TEMPORAL

    @property
    def columns(self) -> List[Column]:
        columns = self.column.columns
        if self.filter is not None:
            columns += self.filter.columns
        return list(set(columns))

    @property
    def time_tables(self) -> List[str]:
        tables = [self.column.table_name]
        if self.filter is not None:
            tables += self.filter.time_tables
        return list(set(tables))

    def get_sampling_specs(
        self,
        hop: int,
        seed_table_name: str,
        edge_types: List[Tuple[str, str, str]],
    ) -> List[SamplingSpec]:

        target_edge_types = [
            edge_type for edge_type in edge_types
            if edge_type[2] == seed_table_name
            and edge_type[0] == self.column.table_name
        ]
        if len(target_edge_types) != 1:
            raise ValueError(f"Could not find a unique foreign key from table "
                             f"'{self.column.table_name}' to "
                             f"'{seed_table_name}'")

        spec = SamplingSpec(
            edge_type=target_edge_types[0],
            hop=hop + 1,
            start_offset=None if self.start == float('-inf') else self.start *
            self.time_unit.to_offset(),
            end_offset=self.end_offset,
        )
        specs = [spec]

        if self.filter is not None:
            specs += self.get_sampling_specs(
                hop=hop + 1,
                seed_table_name=self.column.table_name,
                edge_types=edge_types,
            )

        return specs

    def __repr__(self) -> str:
        filter_repr = '' if self.filter is None else f' {self.filter}'
        start_repr = str(self.start) if self.start != float('-inf') else '-INF'
        return (f'{self.type}({self.column}{filter_repr}, '
                f'{start_repr}, {self.end}, {self.time_unit})')


@dataclass(repr=False, frozen=True)
class Condition:
    left: Union[Column, Aggregation]
    op: Union[RelOp, MemberOp]
    right: Union[int, float, str, List[int], List[float], List[str], None]

    def __post_init__(self) -> None:
        if (isinstance(self.left, Aggregation)
                and self.left.type == AggregationType.LIST_DISTINCT):
            raise NotImplementedError("'LIST_DISTINCT' queries do not support "
                                      "conditions yet")

        if isinstance(self.op, MemberOp):
            assert isinstance(self.right, list)

        if isinstance(self.op, RelOp):
            assert not isinstance(self.right, list)

        if isinstance(self.right, list):
            assert len(self.right) > 0

        if self.right is None:
            assert self.op in {RelOp.EQ, RelOp.NEQ}

    @property
    def end_offset(self) -> DateOffset:
        return self.left.end_offset

    @property
    def query_type(self) -> QueryType:
        return self.left.query_type

    @property
    def columns(self) -> List[Column]:
        return self.left.columns

    @property
    def time_tables(self) -> List[str]:
        return self.left.time_tables

    def get_sampling_specs(
        self,
        hop: int,
        seed_table_name: str,
        edge_types: List[Tuple[str, str, str]],
    ) -> List[SamplingSpec]:
        return self.left.get_sampling_specs(hop, seed_table_name, edge_types)

    def __repr__(self) -> str:
        if isinstance(self.op, MemberOp):
            assert isinstance(self.right, list)
            right_repr = ', '.join(str(x) for x in self.right)
            return f"{self.left} {self.op} ({right_repr})"
        return f"{self.left}{self.op}{self.right}"


@dataclass(repr=False, frozen=True)
class LogicalOperation:
    left: Union[Condition, 'LogicalOperation']
    op: BoolOp
    right: Union[Condition, 'LogicalOperation', None]

    def __post_init__(self) -> None:
        if self.right is None:
            assert self.op == BoolOp.NOT
        else:
            assert self.op != BoolOp.NOT

    @property
    def end_offset(self) -> DateOffset:
        if self.right is None:
            return self.left.end_offset

        end_offset = max_date_offset(
            self.left.end_offset,
            self.right.end_offset,
        )
        assert end_offset is not None
        return end_offset

    @property
    def query_type(self) -> QueryType:
        if self.right is None:
            return self.left.query_type

        if (self.left.query_type == QueryType.TEMPORAL
                or self.right.query_type == QueryType.TEMPORAL):
            return QueryType.TEMPORAL
        else:
            return QueryType.STATIC

    @property
    def columns(self) -> List[Column]:
        columns = self.left.columns
        if self.right is not None:
            columns += self.right.columns
        return list(set(columns))

    @property
    def time_tables(self) -> List[str]:
        tables = self.left.time_tables
        if self.right is not None:
            tables += self.right.time_tables
        return list(set(tables))

    def get_sampling_specs(
        self,
        hop: int,
        seed_table_name: str,
        edge_types: List[Tuple[str, str, str]],
    ) -> List[SamplingSpec]:
        specs = self.left.get_sampling_specs(hop, seed_table_name, edge_types)
        if self.right is not None:
            specs += self.right.get_sampling_specs(hop, seed_table_name,
                                                   edge_types)
        return specs

    def __repr__(self) -> str:
        if self.op == BoolOp.NOT:
            return f'{self.op} {self.left}'
        return f'({self.left} {self.op} {self.right})'


@dataclass(repr=False, frozen=True)
class Filter:
    condition: Union[Condition, LogicalOperation]

    @property
    def columns(self) -> List[Column]:
        return self.condition.columns

    @property
    def time_tables(self) -> List[str]:
        return self.condition.time_tables

    def get_sampling_specs(
        self,
        hop: int,
        seed_table_name: str,
        edge_types: List[Tuple[str, str, str]],
    ) -> List[SamplingSpec]:
        return self.condition.get_sampling_specs(hop, seed_table_name,
                                                 edge_types)

    def __repr__(self) -> str:
        return f'WHERE {self.condition}'


@dataclass(repr=False, frozen=True)
class Entity:
    pkey: Column
    ids: Union[List[int], List[float], List[str], None]
    filter: Optional[Filter] = None

    def __post_init__(self) -> None:
        if isinstance(self.ids, list):
            assert len(self.ids) > 0

    @property
    def columns(self) -> List[Column]:
        return self.filter.columns if self.filter is not None else []

    @property
    def time_tables(self) -> List[str]:
        return self.filter.time_tables if self.filter is not None else []

    def __repr__(self) -> str:
        if self.ids is None:
            out = f'EACH {self.pkey}'
        elif len(self.ids) == 1:
            out = f'{self.pkey}={self.ids[0]}'
        else:
            ids_repr = ', '.join([str(id) for id in self.ids])
            out = f'EACH {self.pkey} IN ({ids_repr})'

        if self.filter is not None:
            out += f' {self.filter}'

        return out


@dataclass(repr=False, frozen=True)
class PQueryDefinition:
    target: Union[Column, Aggregation, Condition, LogicalOperation]
    entity: Entity
    top_k: Optional[int] = None

    @property
    def query_type(self) -> QueryType:
        return self.target.query_type

    def get_task_type(
        self,
        stypes: Dict[str, Dict[str, Stype]],
        edge_types: List[Tuple[str, str, str]],
    ) -> TaskType:
        if isinstance(self.target, (Condition, LogicalOperation)):
            return TaskType.BINARY_CLASSIFICATION

        if isinstance(self.target, Aggregation):
            if self.target.type == AggregationType.LIST_DISTINCT:
                target_edge_types = [
                    edge_type for edge_type in edge_types
                    if edge_type[0] == self.target.column.table_name
                    and edge_type[1] == self.target.column.column_name
                ]
                if len(target_edge_types) != 1:
                    raise NotImplementedError(
                        "Multilabel-classification queries based on "
                        "'LIST_DISTINCT' are not supported yet")
                return TaskType.TEMPORAL_LINK_PREDICTION

            return TaskType.REGRESSION

        assert isinstance(self.target, Column)
        stype = stypes[self.target.table_name][self.target.column_name]

        if stype in {Stype.ID, Stype.categorical}:
            return TaskType.MULTICLASS_CLASSIFICATION

        if stype in {Stype.numerical}:
            return TaskType.REGRESSION

        raise NotImplementedError("Task type not yet supported")

    @property
    def column_dict(self) -> Dict[str, Set[str]]:
        column_dict = defaultdict(set)
        for column in self.target.columns + self.entity.columns:
            column_dict[column.table_name].add(column.column_name)
        return column_dict

    @property
    def time_tables(self) -> List[str]:
        return list(set(self.target.time_tables + self.entity.time_tables))

    def get_entity_table_names(
        self,
        edge_types: List[Tuple[str, str, str]],
    ) -> Tuple[str, ...]:

        if isinstance(self.target, Aggregation):
            if self.target.type == AggregationType.LIST_DISTINCT:
                target_edge_types = [
                    edge_type for edge_type in edge_types
                    if edge_type[0] == self.target.column.table_name
                    and edge_type[1] == self.target.column.column_name
                ]
                assert len(target_edge_types) == 1
                return (
                    self.entity.pkey.table_name,
                    target_edge_types[0][2],
                )

        return (self.entity.pkey.table_name, )

    def get_sampling_specs(
        self,
        edge_types: List[Tuple[str, str, str]],
    ) -> List[SamplingSpec]:

        specs = self.target.get_sampling_specs(
            hop=0,
            seed_table_name=self.entity.pkey.table_name,
            edge_types=edge_types,
        )
        if self.entity.filter is not None:
            specs += self.entity.filter.get_sampling_specs(
                hop=0,
                seed_table_name=self.entity.pkey.table_name,
                edge_types=edge_types,
            )

        # Group specs according to edge type and hop:
        spec_dict: Dict[
            Tuple[Tuple[str, str, str], int],
            Tuple[Optional[DateOffset], Optional[DateOffset]],
        ] = {}
        for spec in specs:
            if (spec.edge_type, spec.hop) not in spec_dict:
                spec_dict[(spec.edge_type, spec.hop)] = (
                    spec.start_offset,
                    spec.end_offset,
                )
            else:
                start_offset, end_offset = spec_dict[(
                    spec.edge_type,
                    spec.hop,
                )]
                spec_dict[(spec.edge_type, spec.hop)] = (
                    min_date_offset(start_offset, spec.start_offset),
                    max_date_offset(end_offset, spec.end_offset),
                )

        return [
            SamplingSpec(edge, hop, start_offset, end_offset)
            for (edge, hop), (start_offset, end_offset) in spec_dict.items()
        ]

    @property
    def exclude_cols_dict(self) -> Dict[str, List[str]]:
        r"""The columns of tables to exclude during model execution."""
        def _get_exclude_cols_dict(
            target: Union[Column, Aggregation, Condition, LogicalOperation],
        ) -> Dict[str, List[str]]:

            if isinstance(target, Column):
                return {target.table_name: [target.column_name]}
            if isinstance(target, Aggregation):
                return {}
            if isinstance(target, Condition):
                return _get_exclude_cols_dict(target.left)

            assert isinstance(target, LogicalOperation)
            left_dict = _get_exclude_cols_dict(target.left)
            if target.right is None:
                return left_dict
            right_dict = _get_exclude_cols_dict(target.right)

            out_dict = {}
            for table_name in set(left_dict) | set(right_dict):
                col_names = left_dict.get(table_name, [])
                col_names += right_dict.get(table_name, [])
                out_dict[table_name] = list(set(col_names))
            return out_dict

        return _get_exclude_cols_dict(self.target)

    def __repr__(self) -> str:
        rank_repr = f' RANK TOP {self.top_k}' if self.top_k is not None else ''
        return f'PREDICT {self.target}{rank_repr} FOR {self.entity}'


if not WITH_PYDANTIC_V2:
    Aggregation.__pydantic_model__.update_forward_refs()  # type: ignore


def min_date_offset(*args: Optional[DateOffset]) -> Optional[DateOffset]:
    import pandas as pd

    if any(arg is None for arg in args):
        return None

    anchor = pd.Timestamp('2000-01-01')
    timestamps = [anchor + arg for arg in args]
    assert len(timestamps) > 0
    argmin = min(range(len(timestamps)), key=lambda i: timestamps[i])
    return args[argmin]


def max_date_offset(*args: DateOffset) -> DateOffset:
    import pandas as pd

    if any(arg is None for arg in args):
        return None

    anchor = pd.Timestamp('2000-01-01')
    timestamps = [anchor + arg for arg in args]
    assert len(timestamps) > 0
    argmax = max(range(len(timestamps)), key=lambda i: timestamps[i])
    return args[argmax]
