"""Typing."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, TypeVar, Tuple, Union

# 1 level
DAny = Dict[str, Any]
DInt = Dict[str, int]
DObj = Dict[str, object]
DStr = Dict[str, str]
Int = int
IntStr = Union[int, str]
LBool = List[bool]
LInt = List[int]
LPath = List[Path]
LStr = List[str]
LTInt2 = List[Tuple[int, int]]
ODatetime = Optional[datetime]
ODict = Optional[dict]
Param = Tuple[str, Any]
SInt = Set[int]
SStr = Set[str]
SeqStr = Sequence[str]
Str = str
T = TypeVar("T")
T2Str = Tuple[str, str]
T3Str = Tuple[str, str, str]
T3StrInt = Tuple[str, str, int]
TLists = (list, set, tuple)
TStr = Tuple[str, ...]
TValues = (str, int, float)
Value = Union[str, int, float]

# 2 level
DDAny = Dict[str, DAny]
DDStr = Dict[str, DStr]
DLInt = Dict[str, LInt]
DLStr = Dict[str, LStr]
DList = Dict[str, list]
DSStr = Dict[str, SStr]
DiAny = Dict[int, Any]
DiDAny = Dict[int, DAny]
DiStr = Dict[int, str]
LDAny = List[DAny]
LDStr = List[DStr]
LParam = List[Param]
LT = List[T]
LT2Str = List[T2Str]
LT2StrDAny = List[Tuple[str, DAny]]
LValue = List[Value]
ODAny = Optional[DAny]
OSeqStr = Optional[SeqStr]
SParam = Set[Param]
SeqDAny = Sequence[DAny]
SeqT = Sequence[T]
SeqUIntStr = Sequence[IntStr]
T3SStr = Tuple[SStr, SStr, SStr]
TParam = Tuple[Param, ...]
UStr = Union[str, SeqStr]

# 3 level
DDDLStr = Dict[str, Dict[str, DLStr]]
DDLInt = Dict[str, DLInt]
DiLDAny = Dict[int, LDAny]
LDList = List[DList]
LLDAny = List[LDAny]
LLParam = List[LParam]
ODDAny = Optional[DDAny]
ODLStr = Optional[DLStr]
OUStr = Optional[UStr]
ULDAny = Union[LDAny, DAny]

# 4 level
DDDLInt = Dict[str, DDLInt]
UParam = Union[LParam, SParam, TParam]

# 5 level
OUParam = Optional[UParam]
