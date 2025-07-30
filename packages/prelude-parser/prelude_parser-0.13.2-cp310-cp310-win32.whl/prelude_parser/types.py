# UP035 and UP006 ignored because Python 3.9 doesn't support the upgrade

from datetime import date, datetime
from typing import Dict, List, Union  # noqa: UP035

FieldInfo = Union[str, int, float, date, datetime, None]
FlatFormInfo = List[Dict[str, FieldInfo]]  # noqa: UP006
