from typing import TypeVarTuple  # New typing features introduced in 3.11

Ts = TypeVarTuple("Ts")
ReturnType = tuple[*Ts] | tuple[*Ts, list[str]]
