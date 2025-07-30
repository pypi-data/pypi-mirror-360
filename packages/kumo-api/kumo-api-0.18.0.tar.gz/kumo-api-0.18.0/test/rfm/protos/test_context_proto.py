from typing import Any

import kumoapi.rfm.protos.context_pb2 as _context_pb2

context_pb2: Any = _context_pb2


def test_context() -> None:
    input = context_pb2.Context()
    input.task_type = context_pb2.TaskType.REGRESSION
    input.entity_table_names.extend(['USERS'])

    data = input.SerializeToString()
    assert len(data) > 0

    out = context_pb2.Context()
    out.ParseFromString(data)
    assert out.task_type == context_pb2.TaskType.REGRESSION
    assert out.entity_table_names == ['USERS']
