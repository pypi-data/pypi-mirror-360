"""杂鱼♡～这是本喵的JSDC Loader核心功能喵～才不是因为想让杂鱼的代码更整洁才分离出来的呢～"""

from .converter import convert_dataclass_to_dict, convert_dict_to_dataclass
from .types import T
from .validator import validate_dataclass, validate_type

__all__ = [
    "T",
    "convert_dict_to_dataclass",
    "convert_dataclass_to_dict",
    "validate_dataclass",
    "validate_type",
]

# 杂鱼♡～本喵把最重要的功能都放在这里了喵～
# 不要直接导入这些函数，应该使用公共API喵～
