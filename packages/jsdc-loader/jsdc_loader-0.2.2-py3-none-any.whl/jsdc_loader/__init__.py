"""杂鱼♡～这是本喵的JSDC Loader库喵～可以轻松地在JSON和dataclass之间转换哦～"""

from .dumper import jsdc_dump, jsdc_dumps
from .loader import jsdc_load, jsdc_loads

__author__ = "Neko"
__version__ = "0.2.2"  # 杂鱼♡～升级到2.1喵～
__all__ = [
    # 杂鱼♡～传统函数，保持向后兼容喵～
    "jsdc_load", 
    "jsdc_loads", 
    "jsdc_dump", 
    "jsdc_dumps",
]

# 杂鱼♡～别忘了查看本喵的README.md喵～
# 本喵才不是因为担心杂鱼不会用这个库才写那么详细的文档的～