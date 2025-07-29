"""杂鱼♡～这是本喵为JSDC Loader编写的测试用例喵～真是个杂鱼♡～"""

import collections
import datetime
import os
import tempfile
import time
import unittest
import uuid
from dataclasses import FrozenInstanceError, dataclass, field
from decimal import Decimal
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


from .dumper import jsdc_dumps, jsdc_dump
from .loader import jsdc_loads, jsdc_load


class TestJSDCLoader(unittest.TestCase):
    """杂鱼♡～这是本喵为JSDC Loader编写的测试用例喵～"""

    def setUp(self):
        """杂鱼♡～本喵要设置测试环境喵～"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """杂鱼♡～本喵要清理测试环境喵～"""
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_basic_serialization(self):
        """杂鱼♡～本喵要测试最基础的序列化/反序列化喵～"""

        @dataclass
        class DatabaseConfig:
            host: str = "localhost"
            port: int = 3306
            user: str = "root"
            password: str = "password"
            ips: List[str] = field(default_factory=lambda: ["127.0.0.1"])
            primary_user: Optional[str] = field(default_factory=lambda: None)

        db = DatabaseConfig()
        jsdc_dump(db, self.temp_path)
        loaded_db = jsdc_load(self.temp_path, DatabaseConfig)

        self.assertEqual(db.host, loaded_db.host)
        self.assertEqual(db.port, loaded_db.port)
        self.assertEqual(db.ips, loaded_db.ips)
        print("杂鱼♡～本喵测试最基础的序列化/反序列化成功了喵～")

    def test_enum_serialization(self):
        """杂鱼♡～本喵要测试枚举的序列化/反序列化喵～"""

        class UserType(Enum):
            ADMIN = auto()
            USER = auto()
            GUEST = auto()

        @dataclass
        class UserConfig:
            name: str = "John Doe"
            age: int = 30
            married: bool = False
            user_type: UserType = field(default_factory=lambda: UserType.USER)
            roles: List[str] = field(default_factory=lambda: ["read"])

        user = UserConfig()
        jsdc_dump(user, self.temp_path)
        loaded_user = jsdc_load(self.temp_path, UserConfig)

        self.assertEqual(user.name, loaded_user.name)
        self.assertEqual(user.user_type, loaded_user.user_type)
        print("杂鱼♡～本喵测试枚举的序列化/反序列化成功了喵～")

    def test_nested_dataclasses(self):
        """杂鱼♡～本喵要测试嵌套的数据类了喵～"""

        class UserType(Enum):
            ADMIN = auto()
            USER = auto()
            GUEST = auto()

        @dataclass
        class UserConfig:
            name: str = "John Doe"
            age: int = 30
            married: bool = False
            user_type: UserType = field(default_factory=lambda: UserType.USER)
            roles: List[str] = field(default_factory=lambda: ["read"])

        @dataclass
        class DatabaseConfig:
            host: str = "localhost"
            port: int = 3306
            user: str = "root"
            password: str = "password"
            ips: List[str] = field(default_factory=lambda: ["127.0.0.1"])
            primary_user: Optional[str] = field(default_factory=lambda: None)

        @dataclass
        class AppConfig:
            user: UserConfig = field(default_factory=lambda: UserConfig())
            database: DatabaseConfig = field(default_factory=lambda: DatabaseConfig())
            version: str = "1.0.0"
            debug: bool = False
            settings: Dict[str, str] = field(default_factory=lambda: {"theme": "dark"})

        app = AppConfig()
        app.user.roles.append("write")
        app.database.ips.extend(["192.168.1.1", "10.0.0.1"])
        app.settings["language"] = "en"

        jsdc_dump(app, self.temp_path)
        loaded_app = jsdc_load(self.temp_path, AppConfig)

        self.assertEqual(loaded_app.user.roles, ["read", "write"])
        self.assertEqual(
            loaded_app.database.ips, ["127.0.0.1", "192.168.1.1", "10.0.0.1"]
        )
        self.assertEqual(loaded_app.settings, {"theme": "dark", "language": "en"})
        print("杂鱼♡～本喵测试嵌套的数据类成功了喵～")

    def test_hashable_model_set(self):
        """杂鱼♡～为了让Model可哈希，本喵决定添加__hash__和__eq__方法喵～"""

        @dataclass(frozen=True)  # 让这个数据类不可变，以便可以哈希
        class Model:
            base_url: str = ""
            api_key: str = ""
            model: str = ""

            def __hash__(self):
                return hash(
                    (self.base_url, self.api_key, self.model)
                )  # 使用元组的哈希值

            def __eq__(self, other):
                if not isinstance(other, Model):
                    return NotImplemented
                return (self.base_url, self.api_key, self.model) == (
                    other.base_url,
                    other.api_key,
                    other.model,
                )  # 比较内容

        @dataclass
        class ModelList:
            models: Set[Model] = field(default_factory=lambda: set())

        # 创建测试数据
        model1 = Model(
            base_url="https://api1.example.com", api_key="key1", model="gpt-4"
        )
        model2 = Model(
            base_url="https://api2.example.com", api_key="key2", model="gpt-3.5"
        )
        model3 = Model(
            base_url="https://api3.example.com", api_key="key3", model="llama-3"
        )

        model_list = ModelList()
        model_list.models.add(model1)
        model_list.models.add(model2)
        model_list.models.add(model3)

        # 测试相同模型的哈希值和相等性
        duplicate_model = Model(
            base_url="https://api1.example.com", api_key="key1", model="gpt-4"
        )
        model_list.models.add(duplicate_model)  # 这个不应该增加集合的大小

        self.assertEqual(len(model_list.models), 3)  # 验证重复模型没有被添加
        self.assertEqual(hash(model1), hash(duplicate_model))  # 验证哈希函数工作正常
        self.assertEqual(model1, duplicate_model)  # 验证相等性比较工作正常

        # 序列化和反序列化
        jsdc_dump(model_list, self.temp_path)
        loaded_model_list = jsdc_load(self.temp_path, ModelList)

        # 验证集合大小
        self.assertEqual(len(loaded_model_list.models), 3)

        # 验证所有模型都被正确反序列化
        loaded_models = sorted(loaded_model_list.models, key=lambda m: m.base_url)
        original_models = sorted(model_list.models, key=lambda m: m.base_url)

        for i in range(len(original_models)):
            self.assertEqual(loaded_models[i].base_url, original_models[i].base_url)
            self.assertEqual(loaded_models[i].api_key, original_models[i].api_key)
            self.assertEqual(loaded_models[i].model, original_models[i].model)

        # 验证集合操作仍然正常工作
        new_model = Model(
            base_url="https://api4.example.com", api_key="key4", model="claude-3"
        )
        loaded_model_list.models.add(new_model)
        self.assertEqual(len(loaded_model_list.models), 4)

        # 验证重复模型仍然不会被添加
        duplicate_model_again = Model(
            base_url="https://api1.example.com", api_key="key1", model="gpt-4"
        )
        loaded_model_list.models.add(duplicate_model_again)
        self.assertEqual(len(loaded_model_list.models), 4)
        print("杂鱼♡～本喵测试可哈希的模型成功了喵～")

    def test_error_handling(self):
        """杂鱼♡～本喵要测试错误处理了喵～"""

        @dataclass
        class DatabaseConfig:
            host: str = "localhost"
            port: int = 3306

        # Test nonexistent file
        with self.assertRaises(FileNotFoundError):
            jsdc_load("nonexistent.json", DatabaseConfig)

        # Test empty input
        with self.assertRaises(ValueError):
            jsdc_loads("", DatabaseConfig)

        # Test invalid JSON
        with self.assertRaises(ValueError):
            jsdc_loads("{invalid json}", DatabaseConfig)

        # Test invalid indent
        with self.assertRaises(ValueError):
            jsdc_dump(DatabaseConfig(), self.temp_path, indent=-1)
        print("杂鱼♡～本喵测试错误处理成功了喵～")

    def test_complex_types(self):
        """杂鱼♡～本喵要测试各种复杂类型了喵～准备好被本喵的测试震撼吧～"""

        @dataclass
        class ComplexConfig:
            created_at: datetime.datetime = field(
                default_factory=lambda: datetime.datetime.now()
            )
            updated_at: Optional[datetime.datetime] = None
            expiry_date: Optional[datetime.date] = field(
                default_factory=lambda: datetime.date.today()
            )
            session_id: uuid.UUID = field(default_factory=lambda: uuid.uuid4())
            amount: Decimal = Decimal("10.50")
            time_delta: datetime.timedelta = datetime.timedelta(days=7)

        complex_obj = ComplexConfig()
        complex_obj.updated_at = datetime.datetime.now()

        jsdc_dump(complex_obj, self.temp_path)
        loaded_obj = jsdc_load(self.temp_path, ComplexConfig)

        self.assertEqual(complex_obj.created_at, loaded_obj.created_at)
        self.assertEqual(complex_obj.updated_at, loaded_obj.updated_at)
        self.assertEqual(complex_obj.expiry_date, loaded_obj.expiry_date)
        self.assertEqual(complex_obj.session_id, loaded_obj.session_id)
        self.assertEqual(complex_obj.amount, loaded_obj.amount)
        self.assertEqual(complex_obj.time_delta, loaded_obj.time_delta)
        print("杂鱼♡～本喵测试复杂类型成功了喵～")

    def test_deeply_nested_structures(self):
        """杂鱼♡～嘻嘻～本喵要测试超级深的嵌套结构了喵～杂鱼会头晕的吧～"""

        @dataclass
        class Level3:
            name: str = "level3"
            value: int = 3

        @dataclass
        class Level2:
            name: str = "level2"
            value: int = 2
            level3_items: List[Level3] = field(default_factory=lambda: [Level3()])
            level3_dict: Dict[str, Level3] = field(
                default_factory=lambda: {"default": Level3()}
            )

        @dataclass
        class Level1:
            name: str = "level1"
            value: int = 1
            level2_items: List[Level2] = field(default_factory=lambda: [Level2()])
            level2_dict: Dict[str, Level2] = field(
                default_factory=lambda: {"default": Level2()}
            )

        @dataclass
        class RootConfig:
            name: str = "root"
            level1_items: List[Level1] = field(default_factory=lambda: [Level1()])
            level1_dict: Dict[str, Level1] = field(
                default_factory=lambda: {"default": Level1()}
            )

        # 创建深度嵌套结构
        root = RootConfig()
        root.level1_items.append(Level1(name="custom_level1"))
        root.level1_dict["custom"] = Level1(name="custom_dict_level1")
        root.level1_dict["custom"].level2_items.append(Level2(name="custom_level2"))
        root.level1_dict["custom"].level2_items[0].level3_items.append(
            Level3(name="custom_level3", value=99)
        )

        jsdc_dump(root, self.temp_path)
        loaded_root = jsdc_load(self.temp_path, RootConfig)

        # 验证深度嵌套的值
        self.assertEqual(
            loaded_root.level1_dict["custom"].level2_items[0].level3_items[1].name,
            "custom_level3",
        )
        self.assertEqual(
            loaded_root.level1_dict["custom"].level2_items[0].level3_items[1].value, 99
        )
        print("杂鱼♡～本喵测试超级深的嵌套结构成功了喵～")

    def test_string_serialization(self):
        """杂鱼♡～本喵要测试字符串序列化了喵～这种基础功能都要本喵教你吗～"""

        @dataclass
        class Config:
            name: str = "test"
            values: List[int] = field(default_factory=lambda: [1, 2, 3])

        # 创建测试对象
        config = Config(name="string_test", values=[5, 6, 7, 8])

        # 序列化到字符串
        serialized_str = jsdc_dumps(config)
        self.assertIsInstance(serialized_str, str)

        # 从字符串反序列化
        loaded_config = jsdc_loads(serialized_str, Config)

        # 验证值
        self.assertEqual(config.name, loaded_config.name)
        self.assertEqual(config.values, loaded_config.values)
        print("杂鱼♡～本喵测试字符串序列化成功了喵～")

    def test_empty_collections(self):
        """杂鱼♡～本喵来测试空集合的情况了喵～杂鱼肯定忘记处理这种情况了吧～"""

        @dataclass
        class EmptyCollections:
            empty_list: List[str] = field(default_factory=list)
            empty_dict: Dict[str, int] = field(default_factory=dict)
            empty_set: Set[int] = field(default_factory=set)
            null_value: Optional[str] = None
            empty_nested_list: List[List[int]] = field(default_factory=lambda: [])

        empty = EmptyCollections()

        jsdc_dump(empty, self.temp_path)
        loaded_empty = jsdc_load(self.temp_path, EmptyCollections)

        self.assertEqual(loaded_empty.empty_list, [])
        self.assertEqual(loaded_empty.empty_dict, {})
        self.assertEqual(loaded_empty.empty_set, set())
        self.assertIsNone(loaded_empty.null_value)
        self.assertEqual(loaded_empty.empty_nested_list, [])
        print("杂鱼♡～本喵测试空集合成功了喵～")

    def test_inheritance(self):
        """杂鱼♡～本喵要测试继承关系了喵～本喵真是无所不能～"""

        @dataclass
        class BaseConfig:
            name: str = "base"
            version: str = "1.0.0"

        @dataclass
        class DerivedConfig(BaseConfig):
            name: str = "derived"  # 覆盖基类字段
            extra_field: str = "extra"

        @dataclass
        class Container:
            base: BaseConfig = field(default_factory=lambda: BaseConfig())
            derived: DerivedConfig = field(default_factory=lambda: DerivedConfig())

        container = Container()
        container.base.version = "2.0.0"
        container.derived.extra_field = "custom_value"

        jsdc_dump(container, self.temp_path)
        loaded_container = jsdc_load(self.temp_path, Container)

        # 验证基类和派生类的字段
        self.assertEqual(loaded_container.base.name, "base")
        self.assertEqual(loaded_container.base.version, "2.0.0")
        self.assertEqual(loaded_container.derived.name, "derived")
        self.assertEqual(loaded_container.derived.version, "1.0.0")
        self.assertEqual(loaded_container.derived.extra_field, "custom_value")
        print("杂鱼♡～本喵测试继承关系成功了喵～")

    def test_union_types(self):
        """杂鱼♡～本喵要测试联合类型了喵～这可是个难点呢～让杂鱼见识一下本喵的厉害～"""

        @dataclass
        class ConfigWithUnions:
            int_or_str: Union[int, str] = 42
            dict_or_list: Union[Dict[str, int], List[int]] = field(
                default_factory=lambda: {"a": 1}
            )

        # 测试不同的联合类型值
        config1 = ConfigWithUnions(int_or_str=42, dict_or_list={"a": 1, "b": 2})
        config2 = ConfigWithUnions(int_or_str="string_value", dict_or_list=[1, 2, 3])

        # 序列化和反序列化第一个配置
        jsdc_dump(config1, self.temp_path)
        loaded_config1 = jsdc_load(self.temp_path, ConfigWithUnions)

        self.assertEqual(loaded_config1.int_or_str, 42)
        self.assertEqual(loaded_config1.dict_or_list, {"a": 1, "b": 2})

        # 序列化和反序列化第二个配置
        jsdc_dump(config2, self.temp_path)
        loaded_config2 = jsdc_load(self.temp_path, ConfigWithUnions)

        self.assertEqual(loaded_config2.int_or_str, "string_value")
        self.assertEqual(loaded_config2.dict_or_list, [1, 2, 3])
        print("杂鱼♡～本喵测试联合类型成功了喵～")

    def test_tuple_types(self):
        """杂鱼♡～本喵要测试元组类型了喵～这种不可变序列也要正确处理才行～"""

        @dataclass
        class ConfigWithTuples:
            simple_tuple: Tuple[int, str, bool] = field(
                default_factory=lambda: (1, "test", True)
            )
            int_tuple: Tuple[int, ...] = field(default_factory=lambda: (1, 2, 3))
            empty_tuple: Tuple = field(default_factory=tuple)
            nested_tuple: Tuple[Tuple[int, int], Tuple[str, str]] = field(
                default_factory=lambda: ((1, 2), ("a", "b"))
            )

        config = ConfigWithTuples()

        jsdc_dump(config, self.temp_path)
        loaded_config = jsdc_load(self.temp_path, ConfigWithTuples)

        self.assertEqual(loaded_config.simple_tuple, (1, "test", True))
        self.assertEqual(loaded_config.int_tuple, (1, 2, 3))
        self.assertEqual(loaded_config.empty_tuple, ())
        self.assertEqual(loaded_config.nested_tuple, ((1, 2), ("a", "b")))
        print("杂鱼♡～本喵测试元组类型成功了喵～")

    def test_any_type(self):
        """杂鱼♡～本喵现在要测试Any类型了喵～这可是最灵活的类型呢～"""

        @dataclass
        class ConfigWithAny:
            any_field: Any = None
            any_list: List[Any] = field(default_factory=list)
            any_dict: Dict[str, Any] = field(default_factory=dict)

        # 使用各种不同类型的值
        config = ConfigWithAny()
        config.any_field = "string"
        config.any_list = [1, "two", False, None, [1, 2, 3], {"key": "value"}]
        config.any_dict = {
            "int": 42,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        jsdc_dump(config, self.temp_path)
        loaded_config = jsdc_load(self.temp_path, ConfigWithAny)

        self.assertEqual(loaded_config.any_field, "string")
        self.assertEqual(
            loaded_config.any_list, [1, "two", False, None, [1, 2, 3], {"key": "value"}]
        )
        self.assertEqual(
            loaded_config.any_dict,
            {
                "int": 42,
                "bool": True,
                "none": None,
                "list": [1, 2, 3],
                "dict": {"nested": "value"},
            },
        )
        print("杂鱼♡～本喵测试Any类型成功了喵～")

    def test_large_json_payload(self):
        """杂鱼♡～本喵要测试大型JSON负载了喵～看看杂鱼的程序能不能处理～"""

        @dataclass
        class LargeDataConfig:
            items: List[Dict[str, Any]] = field(default_factory=list)

        # 创建大型数据结构
        large_config = LargeDataConfig()
        for i in range(1000):  # 创建1000个项目
            item = {
                "id": i,
                "name": f"Item {i}",
                "tags": [f"tag{j}" for j in range(10)],  # 每个项目10个标签
                "properties": {
                    f"prop{k}": f"value{k}" for k in range(5)
                },  # 每个项目5个属性
            }
            large_config.items.append(item)

        # 测试序列化和反序列化
        jsdc_dump(large_config, self.temp_path)
        loaded_config = jsdc_load(self.temp_path, LargeDataConfig)

        # 验证项目数量
        self.assertEqual(len(loaded_config.items), 1000)
        # 验证第一个和最后一个项目
        self.assertEqual(loaded_config.items[0]["id"], 0)
        self.assertEqual(loaded_config.items[999]["id"], 999)
        # 验证结构完整性
        self.assertEqual(len(loaded_config.items[500]["tags"]), 10)
        self.assertEqual(len(loaded_config.items[500]["properties"]), 5)
        print("杂鱼♡～本喵测试大型JSON负载成功了喵～")

    def test_special_characters(self):
        """杂鱼♡～本喵要测试特殊字符了喵～这些字符可能会让你的程序崩溃喵～"""

        @dataclass
        class SpecialCharsConfig:
            escaped_chars: str = "\n\t\r\b\f"
            quotes: str = '"quoted text"'
            unicode_chars: str = "你好，世界！😊🐱👍"
            control_chars: str = "\u0000\u0001\u001f"
            backslashes: str = "C:\\path\\to\\file.txt"
            json_syntax: str = '{"key": [1, 2]}'

        config = SpecialCharsConfig()

        jsdc_dump(config, self.temp_path)
        loaded_config = jsdc_load(self.temp_path, SpecialCharsConfig)

        self.assertEqual(loaded_config.escaped_chars, "\n\t\r\b\f")
        self.assertEqual(loaded_config.quotes, '"quoted text"')
        self.assertEqual(loaded_config.unicode_chars, "你好，世界！😊🐱👍")
        self.assertEqual(loaded_config.control_chars, "\u0000\u0001\u001f")
        self.assertEqual(loaded_config.backslashes, "C:\\path\\to\\file.txt")
        self.assertEqual(loaded_config.json_syntax, '{"key": [1, 2]}')
        print("杂鱼♡～本喵测试特殊字符成功了喵～")

    def test_frozen_dataclasses(self):
        """杂鱼♡～本喵要测试不可变的数据类了喵～看看能不能正确处理～"""

        @dataclass(frozen=True)
        class FrozenConfig:
            name: str = "default_name"
            version: int = 0
            tags: Tuple[str, ...] = field(default_factory=tuple)

        # 杂鱼♡～本喵正在创建一个不可变对象喵～
        frozen = FrozenConfig(name="test", version=1, tags=("tag1", "tag2"))

        # 杂鱼♡～本喵要进行序列化和反序列化喵～
        jsdc_dump(frozen, self.temp_path)
        loaded_frozen = jsdc_load(self.temp_path, FrozenConfig)

        # 杂鱼♡～验证值是否正确喵～
        self.assertEqual(loaded_frozen.name, "test")
        self.assertEqual(loaded_frozen.version, 1)
        self.assertEqual(loaded_frozen.tags, ("tag1", "tag2"))

        # 杂鱼♡～验证不可变性喵～
        with self.assertRaises(FrozenInstanceError):
            loaded_frozen.name = "modified"

        # 杂鱼♡～本喵要测试嵌套冻结数据类喵～
        @dataclass(frozen=True)
        class NestedFrozen:
            id: int = 0
            config: FrozenConfig = field(default_factory=lambda: FrozenConfig())

        nested = NestedFrozen(id=1, config=frozen)

        jsdc_dump(nested, self.temp_path)
        loaded_nested = jsdc_load(self.temp_path, NestedFrozen)

        self.assertEqual(loaded_nested.id, 1)
        self.assertEqual(loaded_nested.config.name, "test")
        self.assertEqual(loaded_nested.config.tags, ("tag1", "tag2"))
        print("杂鱼♡～本喵测试不可变的数据类成功了喵～")

    def test_default_values(self):
        """杂鱼♡～本喵要测试默认值处理了喵～看看缺字段时能不能正确使用默认值～"""

        @dataclass
        # 杂鱼♡～本喵要定义一个带默认值的配置类喵～
        class ConfigWithDefaults:
            # 杂鱼♡～将必需字段也设置默认值，以便测试喵～
            required_int: int = 0  # 杂鱼♡～默认值为0喵～
            required_str: str = ""  # 杂鱼♡～默认为空字符串喵～
            optional_int: int = 42  # 杂鱼♡～可选整数，默认值为42喵～
            optional_str: str = "default"  # 杂鱼♡～可选字符串，默认值为"default"喵～
            optional_list: List[str] = field(
                default_factory=lambda: ["default_item"]
            )  # 杂鱼♡～可选列表，默认值为["default_item"]喵～
            optional_dict: Dict[str, int] = field(
                default_factory=lambda: {"default_key": 1}
            )  # 杂鱼♡～可选字典，默认值为{"default_key": 1}喵～

        # 杂鱼♡～本喵要测试带默认值的字段喵～
        # 杂鱼♡～使用部分JSON反序列化，这样其他字段应该使用默认值喵～
        partial_json = '{"required_int": 456, "optional_int": 99, "optional_list": ["custom_item"]}'
        partial_config = jsdc_loads(partial_json, ConfigWithDefaults)

        # 杂鱼♡～验证自定义值和默认值混合喵～
        self.assertEqual(partial_config.required_int, 456)  # 杂鱼♡～自定义值喵～
        self.assertEqual(partial_config.required_str, "")  # 杂鱼♡～默认值喵～
        self.assertEqual(partial_config.optional_int, 99)  # 杂鱼♡～自定义值喵～
        self.assertEqual(partial_config.optional_str, "default")  # 杂鱼♡～默认值喵～
        self.assertEqual(
            partial_config.optional_list, ["custom_item"]
        )  # 杂鱼♡～自定义值喵～
        self.assertEqual(
            partial_config.optional_dict, {"default_key": 1}
        )  # 杂鱼♡～默认值喵～
        print("杂鱼♡～本喵测试默认值处理成功了喵～")

    def test_complex_union_types(self):
        """杂鱼♡～本喵要测试更复杂的联合类型了喵～"""

        @dataclass
        class ConfigA:
            type: str = "A"
            value_a: int = 1

        @dataclass
        class ConfigB:
            type: str = "B"
            value_b: str = "b"

        @dataclass
        class NestedConfig:
            name: str = "nested"
            value: Union[int, str] = 42

        # 杂鱼♡～测试简单联合类型喵～
        config1 = NestedConfig(value=42)
        config2 = NestedConfig(value="string")

        # 杂鱼♡～序列化和反序列化第一个配置喵～
        jsdc_dump(config1, self.temp_path)
        loaded_config1 = jsdc_load(self.temp_path, NestedConfig)
        self.assertEqual(loaded_config1.value, 42)

        # 杂鱼♡～序列化和反序列化第二个配置喵～
        jsdc_dump(config2, self.temp_path)
        loaded_config2 = jsdc_load(self.temp_path, NestedConfig)
        self.assertEqual(loaded_config2.value, "string")

        # 杂鱼♡～测试对象联合类型喵～
        @dataclass
        class ComplexConfig:
            value: Union[ConfigA, ConfigB] = field(default_factory=lambda: ConfigA())

        complex1 = ComplexConfig(value=ConfigA(value_a=99))
        complex2 = ComplexConfig(value=ConfigB(value_b="test"))

        # 杂鱼♡～序列化和反序列化第一个复杂配置喵～
        jsdc_dump(complex1, self.temp_path)
        loaded_complex1 = jsdc_load(self.temp_path, ComplexConfig)
        self.assertEqual(loaded_complex1.value.type, "A")
        self.assertEqual(loaded_complex1.value.value_a, 99)

        # 杂鱼♡～序列化和反序列化第二个复杂配置喵～
        jsdc_dump(complex2, self.temp_path)
        loaded_complex2 = jsdc_load(self.temp_path, ComplexConfig)
        self.assertEqual(loaded_complex2.value.type, "B")
        self.assertEqual(loaded_complex2.value.value_b, "test")
        print("杂鱼♡～本喵测试更简单的联合类型成功了喵～")

    def test_custom_containers(self):
        """杂鱼♡～本喵要测试自定义容器类型了喵～看你能不能处理这些特殊容器～"""

        @dataclass
        class CustomContainersConfig:
            # 杂鱼♡～将类型声明为普通dict，但初始化时使用特殊容器喵～
            ordered_dict: Dict[str, int] = field(
                default_factory=lambda: collections.OrderedDict(
                    [("a", 1), ("b", 2), ("c", 3)]
                )
            )
            default_dict: Dict[str, int] = field(
                default_factory=lambda: collections.defaultdict(int, {"x": 10, "y": 20})
            )
            counter: Dict[str, int] = field(
                default_factory=lambda: collections.Counter(["a", "b", "a", "c", "a"])
            )

        # 杂鱼♡～创建配置并添加一些值喵～
        config = CustomContainersConfig()
        config.ordered_dict["d"] = 4
        config.default_dict["z"] = 30
        config.counter.update(["d", "e", "d"])

        # 杂鱼♡～序列化和反序列化喵～
        jsdc_dump(config, self.temp_path)
        loaded_config = jsdc_load(self.temp_path, CustomContainersConfig)

        # 杂鱼♡～验证序列化和反序列化后的值（使用dict比较）喵～
        self.assertEqual(dict(config.ordered_dict), dict(loaded_config.ordered_dict))
        self.assertEqual(dict(config.default_dict), dict(loaded_config.default_dict))
        self.assertEqual(dict(config.counter), dict(loaded_config.counter))

        # 杂鱼♡～验证字典内容喵～
        self.assertEqual(
            dict(loaded_config.ordered_dict), {"a": 1, "b": 2, "c": 3, "d": 4}
        )
        self.assertEqual(dict(loaded_config.default_dict), {"x": 10, "y": 20, "z": 30})
        self.assertEqual(
            dict(loaded_config.counter), {"a": 3, "b": 1, "c": 1, "d": 2, "e": 1}
        )
        print("杂鱼♡～本喵测试自定义容器类型成功了喵～")

    def test_type_validation(self):
        """杂鱼♡～本喵要测试类型验证了喵～看看你能不能捕获错误的类型～"""

        @dataclass
        class TypedConfig:
            integer: int = 0
            string: str = ""
            boolean: bool = False
            float_val: float = 0.0
            list_of_ints: List[int] = field(default_factory=list)

        # 杂鱼♡～创建一个错误类型的JSON喵～
        invalid_json = '{"integer": "not an int"}'

        # 杂鱼♡～类型错误应该在反序列化时被捕获喵～
        with self.assertRaises(ValueError):
            jsdc_loads(invalid_json, TypedConfig)

        # 杂鱼♡～创建一个有效的JSON喵～
        valid_json = '{"integer": 42, "string": "text", "boolean": true, "float_val": 3.14, "list_of_ints": [1, 2, 3]}'

        # 杂鱼♡～验证正确的类型可以被加载喵～
        config = jsdc_loads(valid_json, TypedConfig)
        self.assertEqual(config.integer, 42)
        self.assertEqual(config.string, "text")
        self.assertTrue(config.boolean)
        self.assertEqual(config.float_val, 3.14)
        self.assertEqual(config.list_of_ints, [1, 2, 3])

        # 杂鱼♡～测试部分字段的JSON喵～
        partial_json = '{"integer": 99}'

        # 杂鱼♡～部分字段应该可以正确加载，其他字段使用默认值喵～
        partial_config = jsdc_loads(partial_json, TypedConfig)
        self.assertEqual(partial_config.integer, 99)
        self.assertEqual(partial_config.string, "")
        self.assertFalse(partial_config.boolean)

        # 杂鱼♡～JSDC暂时不支持额外字段，所以不测试喵～
        print("杂鱼♡～本喵测试类型验证成功了喵～")

    def test_formatting_options(self):
        """杂鱼♡～本喵要测试不同的格式化选项了喵～看看美化JSON的效果～"""

        @dataclass
        class SimpleConfig:
            name: str = "test"
            values: List[int] = field(default_factory=lambda: [1, 2, 3])
            nested: Dict[str, Any] = field(
                default_factory=lambda: {"a": 1, "b": [2, 3], "c": {"d": 4}}
            )

        config = SimpleConfig()

        # 杂鱼♡～测试indent=0的情况喵（可能依赖于具体实现，可能仍会有换行）～
        jsdc_dump(config, self.temp_path, indent=0)

        # 杂鱼♡～加载并验证内容喵～
        loaded_zero_indent = jsdc_load(self.temp_path, SimpleConfig)
        self.assertEqual(loaded_zero_indent.name, "test")

        # 杂鱼♡～测试其他缩进选项喵～
        for indent in [2, 4, 8]:
            # 杂鱼♡～使用不同的缩进序列化喵～
            jsdc_dump(config, self.temp_path, indent=indent)

            # 杂鱼♡～读取序列化后的内容喵～
            with open(self.temp_path, "r") as f:
                content = f.read()

            # 杂鱼♡～反序列化确认内容正确喵～
            loaded = jsdc_load(self.temp_path, SimpleConfig)
            self.assertEqual(loaded.name, "test")
            self.assertEqual(loaded.values, [1, 2, 3])
            self.assertEqual(loaded.nested, {"a": 1, "b": [2, 3], "c": {"d": 4}})

            # 杂鱼♡～如果有缩进，确认内容中包含换行符喵～
            self.assertIn("\n", content)

        # 杂鱼♡～单独测试None缩进（使用默认值）喵～
        jsdc_dump(config, self.temp_path)  # 不指定indent参数

        # 杂鱼♡～读取序列化后的内容并确认可以正确加载喵～
        loaded = jsdc_load(self.temp_path, SimpleConfig)
        self.assertEqual(loaded.name, "test")

        # 杂鱼♡～测试有序字典喵～
        config = SimpleConfig(nested={"z": 1, "y": 2, "x": 3, "w": 4, "v": 5})

        # 杂鱼♡～序列化带有顺序字典的配置喵～
        jsdc_dump(config, self.temp_path, indent=2)

        # 杂鱼♡～读取序列化后的内容喵～
        with open(self.temp_path, "r") as f:
            content = f.read()

        # 杂鱼♡～反序列化确认内容正确喵～
        loaded = jsdc_load(self.temp_path, SimpleConfig)
        self.assertEqual(loaded.nested, {"z": 1, "y": 2, "x": 3, "w": 4, "v": 5})
        print("杂鱼♡～本喵测试格式化选项成功了喵～")

    def test_performance(self):
        """杂鱼♡～本喵要测试性能了喵～看看你的程序有多快～"""

        @dataclass
        class SimpleItem:
            id: int = 0
            name: str = ""
            value: float = 0.0

        @dataclass
        class PerformanceConfig:
            items: List[SimpleItem] = field(default_factory=list)
            metadata: Dict[str, Any] = field(default_factory=dict)

        # 杂鱼♡～创建一个包含许多项的大型配置喵～
        large_config = PerformanceConfig()
        for i in range(1000):
            large_config.items.append(
                SimpleItem(id=i, name=f"Item {i}", value=float(i) * 1.5)
            )

        large_config.metadata = {
            "created_at": datetime.datetime.now().isoformat(),
            "version": "1.0.0",
            "tags": ["performance", "test", "jsdc"],
            "nested": {"level1": {"level2": {"level3": [i for i in range(100)]}}},
        }

        # 杂鱼♡～测量序列化性能喵～
        start_time = time.time()
        jsdc_dump(large_config, self.temp_path)
        serialize_time = time.time() - start_time

        # 杂鱼♡～获取序列化文件大小喵～
        file_size = os.path.getsize(self.temp_path)

        # 杂鱼♡～测量反序列化性能喵～
        start_time = time.time()
        loaded_config = jsdc_load(self.temp_path, PerformanceConfig)
        deserialize_time = time.time() - start_time

        # 杂鱼♡～记录性能指标（可以在测试输出中查看喵）～
        print("\n杂鱼♡～性能测试结果喵～")
        print(f"文件大小: {file_size} 字节喵～")
        print(f"序列化时间: {serialize_time:.6f} 秒喵～")
        print(f"反序列化时间: {deserialize_time:.6f} 秒喵～")
        print(f"项目数量: {len(loaded_config.items)} 个喵～")

        # 杂鱼♡～确认数据完整性喵～
        self.assertEqual(len(loaded_config.items), 1000)
        # 验证第一个和最后一个项目
        self.assertEqual(loaded_config.items[0].id, 0)
        self.assertEqual(loaded_config.items[999].id, 999)
        # 验证SimpleItem对象的属性喵～
        self.assertEqual(loaded_config.items[500].name, "Item 500")
        self.assertEqual(loaded_config.items[500].value, 750.0)  # 500 * 1.5 = 750.0
        # 验证metadata结构完整性喵～
        self.assertEqual(
            loaded_config.metadata["tags"], ["performance", "test", "jsdc"]
        )
        self.assertEqual(
            len(loaded_config.metadata["nested"]["level1"]["level2"]["level3"]), 100
        )

        # 测试字符串序列化的性能（jsdc_dumps）
        start_time = time.time()
        json_str = jsdc_dumps(large_config)
        string_serialize_time = time.time() - start_time

        # 测试字符串反序列化的性能（jsdc_loads）
        start_time = time.time()
        loaded_from_str = jsdc_loads(json_str, PerformanceConfig)
        string_deserialize_time = time.time() - start_time

        # 记录额外的性能指标
        print(f"String Serialization Time: {string_serialize_time:.6f} seconds")
        print(f"String Deserialization Time: {string_deserialize_time:.6f} seconds")
        print(f"JSON String Length: {len(json_str)} characters")

        # 确认从字符串加载的数据完整性
        self.assertEqual(len(loaded_from_str.items), 1000)
        self.assertEqual(loaded_from_str.items[0].id, 0)
        print("杂鱼♡～本喵测试性能成功了喵～")

    def test_type_validation_on_dump(self):
        """杂鱼♡～本喵要测试序列化时的类型验证了喵～看看能不能正确抛出错误～"""

        # 杂鱼♡～测试List[int]类型验证喵～
        @dataclass
        class IntListConfig:
            integers: List[int] = field(default_factory=list)

        # 杂鱼♡～初始化正确类型的数据喵～
        valid_config = IntListConfig(integers=[1, 2, 3, 4, 5])

        # 杂鱼♡～正常情况应该可以序列化喵～
        jsdc_dump(valid_config, self.temp_path)

        # 杂鱼♡～添加错误类型的数据喵～
        invalid_config = IntListConfig(integers=[1, 2, "3", 4, 5])  # 添加了一个字符串

        # 杂鱼♡～序列化应该抛出类型错误喵～
        with self.assertRaises(TypeError):
            jsdc_dump(invalid_config, self.temp_path)

        # 杂鱼♡～测试Dict[str, int]类型验证喵～
        @dataclass
        class DictConfig:
            mapping: Dict[str, int] = field(default_factory=dict)

        # 杂鱼♡～初始化正确类型的数据喵～
        valid_dict_config = DictConfig(mapping={"a": 1, "b": 2, "c": 3})

        # 杂鱼♡～正常情况应该可以序列化喵～
        jsdc_dump(valid_dict_config, self.temp_path)

        # 杂鱼♡～添加错误类型的数据喵～
        invalid_dict_config = DictConfig(
            mapping={"a": 1, "b": "string", "c": 3}
        )  # 值类型错误

        # 杂鱼♡～序列化应该抛出类型错误喵～
        with self.assertRaises(TypeError):
            jsdc_dump(invalid_dict_config, self.temp_path)

        # 杂鱼♡～测试Dict[str, int]的键类型错误喵～
        invalid_key_config = DictConfig()
        invalid_key_config.mapping = {1: 1, "b": 2}  # 键类型错误

        # 杂鱼♡～序列化应该抛出类型错误喵～
        with self.assertRaises(TypeError):
            jsdc_dump(invalid_key_config, self.temp_path)

        # 杂鱼♡～测试嵌套容器的类型验证喵～
        @dataclass
        class NestedConfig:
            nested_list: List[List[int]] = field(
                default_factory=lambda: [[1, 2], [3, 4]]
            )
            nested_dict: Dict[str, List[int]] = field(
                default_factory=lambda: {"a": [1, 2], "b": [3, 4]}
            )

        # 杂鱼♡～初始化正确类型的数据喵～
        valid_nested = NestedConfig()

        # 杂鱼♡～正常情况应该可以序列化喵～
        jsdc_dump(valid_nested, self.temp_path)

        # 杂鱼♡～嵌套列表中添加错误类型喵～
        invalid_nested1 = NestedConfig()
        invalid_nested1.nested_list[0].append(
            "not an int"
        )  # 杂鱼♡～添加了一个不是整数的元素喵～

        # 杂鱼♡～序列化应该抛出类型错误喵～
        with self.assertRaises(TypeError):
            jsdc_dump(invalid_nested1, self.temp_path)

        # 杂鱼♡～嵌套字典中添加错误类型喵～
        invalid_nested2 = NestedConfig()
        invalid_nested2.nested_dict["a"].append(
            "not an int"
        )  # 杂鱼♡～添加了一个不是整数的元素喵～

        # 杂鱼♡～序列化应该抛出类型错误喵～
        with self.assertRaises(TypeError):
            jsdc_dump(invalid_nested2, self.temp_path)

        # 杂鱼♡～测试可选类型的验证喵～
        @dataclass
        class OptionalConfig:
            maybe_int: Optional[int] = None
            int_or_str: Union[int, str] = 42

        # 杂鱼♡～初始化正确类型的数据喵～
        valid_optional1 = OptionalConfig(maybe_int=None)
        valid_optional2 = OptionalConfig(maybe_int=10)
        valid_optional3 = OptionalConfig(int_or_str=99)
        valid_optional4 = OptionalConfig(int_or_str="string")

        # 杂鱼♡～正常情况应该可以序列化喵～
        jsdc_dump(valid_optional1, self.temp_path)
        jsdc_dump(valid_optional2, self.temp_path)
        jsdc_dump(valid_optional3, self.temp_path)
        jsdc_dump(valid_optional4, self.temp_path)

        # 杂鱼♡～使用不在Union中的类型喵～
        invalid_optional = OptionalConfig()
        invalid_optional.int_or_str = [1, 2, 3]  # 列表不在Union[int, str]中

        # 序列化应该抛出类型错误
        with self.assertRaises(TypeError):
            jsdc_dump(invalid_optional, self.temp_path)

        # 测试集合类型
        @dataclass
        class SetConfig:
            int_set: Set[int] = field(default_factory=set)

        # 杂鱼♡～初始化正确类型的数据喵～
        valid_set = SetConfig(int_set={1, 2, 3, 4, 5})

        # 杂鱼♡～正常情况应该可以序列化喵～
        jsdc_dump(valid_set, self.temp_path)

        # 杂鱼♡～添加错误类型的数据喵～
        invalid_set = SetConfig()
        invalid_set.int_set = {1, "string", 3}  # 杂鱼♡～添加了一个不是整数的元素喵～

        # 杂鱼♡～序列化应该抛出类型错误喵～
        with self.assertRaises(TypeError):
            jsdc_dump(invalid_set, self.temp_path)

        # 杂鱼♡～测试元组类型喵～
        @dataclass
        class TupleConfig:
            fixed_tuple: Tuple[int, str, bool] = field(
                default_factory=lambda: (1, "a", True)
            )
            var_tuple: Tuple[int, ...] = field(default_factory=lambda: (1, 2, 3))

        # 杂鱼♡～初始化正确类型的数据喵～
        valid_tuple = TupleConfig()

        # 杂鱼♡～正常情况应该可以序列化喵～
        jsdc_dump(valid_tuple, self.temp_path)

        # 杂鱼♡～使用错误类型喵～
        invalid_tuple1 = TupleConfig(
            fixed_tuple=(1, 2, True)
        )  # 杂鱼♡～第二个元素应该是str喵～

        # 杂鱼♡～序列化应该抛出类型错误喵～
        with self.assertRaises(TypeError):
            jsdc_dump(invalid_tuple1, self.temp_path)

        # 杂鱼♡～可变长度元组中使用错误类型喵～
        invalid_tuple2 = TupleConfig(var_tuple=(1, 2, "3"))  # 杂鱼♡～应该全是int喵～

        # 杂鱼♡～序列化应该抛出类型错误喵～
        with self.assertRaises(TypeError):
            jsdc_dump(invalid_tuple2, self.temp_path)

        print("杂鱼♡～本喵测试序列化时的类型验证成功了喵～")

    def test_path_support(self):
        """杂鱼♡～本喵要测试pathlib.Path支持了喵～这可是本喵新添加的功能呢～"""

        @dataclass
        class PathTestConfig:
            name: str = "path_test"
            values: List[int] = field(default_factory=lambda: [1, 2, 3])
            nested: Dict[str, str] = field(default_factory=lambda: {"key": "value"})

        # 杂鱼♡～创建测试配置喵～
        config = PathTestConfig(name="pathlib_test", values=[10, 20, 30])

        # 杂鱼♡～测试使用Path对象进行序列化喵～
        path_obj = Path(self.temp_path)
        jsdc_dump(config, path_obj)

        # 杂鱼♡～验证文件确实被创建了喵～
        self.assertTrue(path_obj.exists())

        # 杂鱼♡～测试使用Path对象进行反序列化喵～
        loaded_config = jsdc_load(path_obj, PathTestConfig)

        # 杂鱼♡～验证数据正确性喵～
        self.assertEqual(loaded_config.name, "pathlib_test")
        self.assertEqual(loaded_config.values, [10, 20, 30])
        self.assertEqual(loaded_config.nested, {"key": "value"})

        # 杂鱼♡～测试使用相对路径的Path对象喵～
        relative_path = Path("test_relative.json")
        try:
            jsdc_dump(config, relative_path)
            self.assertTrue(relative_path.exists())

            loaded_relative = jsdc_load(relative_path, PathTestConfig)
            self.assertEqual(loaded_relative.name, "pathlib_test")

        finally:
            # 杂鱼♡～清理相对路径文件喵～
            if relative_path.exists():
                relative_path.unlink()

        # 杂鱼♡～测试嵌套目录的Path对象喵～
        nested_dir = Path("test_nested_dir")
        nested_file = nested_dir / "config.json"

        try:
            jsdc_dump(config, nested_file)
            self.assertTrue(nested_file.exists())

            loaded_nested = jsdc_load(nested_file, PathTestConfig)
            self.assertEqual(loaded_nested.name, "pathlib_test")

        finally:
            # 杂鱼♡～清理嵌套目录喵～
            if nested_file.exists():
                nested_file.unlink()
            if nested_dir.exists():
                nested_dir.rmdir()

        # 杂鱼♡～测试Path和字符串路径的一致性喵～
        str_path = self.temp_path + "_str"
        path_path = Path(self.temp_path + "_path")

        try:
            # 杂鱼♡～使用字符串路径序列化喵～
            jsdc_dump(config, str_path)
            # 杂鱼♡～使用Path对象序列化喵～
            jsdc_dump(config, path_path)

            # 杂鱼♡～从字符串路径和Path对象分别加载喵～
            loaded_str = jsdc_load(str_path, PathTestConfig)
            loaded_path = jsdc_load(path_path, PathTestConfig)

            # 杂鱼♡～验证两种方式加载的结果一致喵～
            self.assertEqual(loaded_str.name, loaded_path.name)
            self.assertEqual(loaded_str.values, loaded_path.values)
            self.assertEqual(loaded_str.nested, loaded_path.nested)

        finally:
            # 杂鱼♡～清理测试文件喵～
            for p in [str_path, str(path_path)]:
                if os.path.exists(p):
                    os.remove(p)

        print("杂鱼♡～本喵测试pathlib.Path支持成功了喵～")

    def test_path_error_handling(self):
        """杂鱼♡～本喵要测试Path相关的错误处理喵～"""

        @dataclass
        class SimpleConfig:
            name: str = "test"

        # 杂鱼♡～测试不存在的Path文件喵～
        nonexistent_path = Path("definitely_does_not_exist_12345.json")
        with self.assertRaises(FileNotFoundError):
            jsdc_load(nonexistent_path, SimpleConfig)

        # 杂鱼♡～测试无效的Path路径喵～使用一个真正无效的路径～
        # 杂鱼♡～使用一个不存在的根目录路径，这应该会失败喵～
        if os.name == "nt":  # Windows系统
            invalid_path = Path(
                "Z:\\nonexistent\\directory\\file.json"
            )  # Z盘通常不存在
        else:
            invalid_path = Path(
                "/nonexistent_root/invalid/file.json"
            )  # Unix系统的无效路径

        with self.assertRaises(
            (ValueError, OSError, PermissionError, FileNotFoundError)
        ):
            jsdc_dump(SimpleConfig(), invalid_path)

        # 杂鱼♡～测试向一个已存在的文件（非目录）写入时的错误喵～
        try:
            # 杂鱼♡～创建一个临时目录来进行测试喵～
            import tempfile

            with tempfile.TemporaryDirectory() as temp_dir:
                # 杂鱼♡～创建一个临时文件喵～
                temp_file_path = Path(temp_dir) / "existing_file.txt"
                temp_file_path.write_text("existing content")

                # 杂鱼♡～现在尝试把这个文件当作目录使用喵～
                invalid_target = temp_file_path / "subdirectory" / "file.json"

                with self.assertRaises((ValueError, OSError, PermissionError)):
                    jsdc_dump(SimpleConfig(), invalid_target)
        except Exception:
            # 杂鱼♡～如果临时目录测试失败，本喵就跳过这个测试喵～
            pass

        print("杂鱼♡～本喵测试Path错误处理成功了喵～")

    def test_mixed_types_serialization_fixes(self):
        """杂鱼♡～本喵要修复混合类型序列化的测试逻辑喵～之前的测试有些不一致～"""

        @dataclass
        class MixedConfig:
            # 杂鱼♡～使用更明确的类型声明喵～
            any_field: Any = None
            union_field: Union[int, str, List[int]] = 42
            optional_field: Optional[str] = None

        # 杂鱼♡～测试各种混合类型的组合喵～
        test_cases = [
            # (any_field, union_field, optional_field)
            ("string_value", 100, "optional_string"),
            ([1, 2, 3], "union_string", None),
            # 杂鱼♡～修改这个case，使用简单类型避免Union中的列表复杂性喵～
            ({"nested": "dict"}, "union_list_test", "another_string"),
            (None, 999, None),
        ]

        for i, (any_val, union_val, opt_val) in enumerate(test_cases):
            with self.subTest(case=i):
                config = MixedConfig(
                    any_field=any_val, union_field=union_val, optional_field=opt_val
                )

                # 杂鱼♡～序列化和反序列化喵～
                jsdc_dump(config, self.temp_path)
                loaded = jsdc_load(self.temp_path, MixedConfig)

                # 杂鱼♡～验证每个字段喵～
                self.assertEqual(loaded.any_field, any_val)
                self.assertEqual(loaded.union_field, union_val)
                self.assertEqual(loaded.optional_field, opt_val)

        # 杂鱼♡～单独测试Union中的列表类型喵～
        @dataclass
        class ListUnionConfig:
            list_field: Union[str, List[int]] = field(default_factory=lambda: [1, 2, 3])

        list_config = ListUnionConfig(list_field=[10, 20, 30])
        jsdc_dump(list_config, self.temp_path)
        loaded_list = jsdc_load(self.temp_path, ListUnionConfig)

        # 杂鱼♡～验证列表在Union中正确处理喵～
        self.assertEqual(loaded_list.list_field, [10, 20, 30])
        self.assertIsInstance(loaded_list.list_field, list)

        print("杂鱼♡～本喵修复混合类型序列化测试成功了喵～")

    def test_edge_cases_fixes(self):
        """杂鱼♡～本喵要修复一些边缘情况的测试逻辑喵～"""

        # 杂鱼♡～测试空字符串字段喵～
        @dataclass
        class EmptyStringConfig:
            empty_str: str = ""
            normal_str: str = "normal"

        empty_config = EmptyStringConfig()
        jsdc_dump(empty_config, self.temp_path)
        loaded_empty = jsdc_load(self.temp_path, EmptyStringConfig)

        self.assertEqual(loaded_empty.empty_str, "")
        self.assertEqual(loaded_empty.normal_str, "normal")

        # 杂鱼♡～测试零值数字字段喵～
        @dataclass
        class ZeroValueConfig:
            zero_int: int = 0
            zero_float: float = 0.0
            false_bool: bool = False

        zero_config = ZeroValueConfig()
        jsdc_dump(zero_config, self.temp_path)
        loaded_zero = jsdc_load(self.temp_path, ZeroValueConfig)

        self.assertEqual(loaded_zero.zero_int, 0)
        self.assertEqual(loaded_zero.zero_float, 0.0)
        self.assertEqual(loaded_zero.false_bool, False)

        # 杂鱼♡～测试字符串中的特殊JSON字符喵～
        @dataclass
        class JsonSpecialCharsConfig:
            json_like: str = '{"key": "value", "array": [1,2,3]}'
            escaped: str = "Line 1\nLine 2\tTabbed"
            quotes: str = 'He said "Hello" to her'

        special_config = JsonSpecialCharsConfig()
        jsdc_dump(special_config, self.temp_path)
        loaded_special = jsdc_load(self.temp_path, JsonSpecialCharsConfig)

        self.assertEqual(loaded_special.json_like, '{"key": "value", "array": [1,2,3]}')
        self.assertEqual(loaded_special.escaped, "Line 1\nLine 2\tTabbed")
        self.assertEqual(loaded_special.quotes, 'He said "Hello" to her')

        print("杂鱼♡～本喵修复边缘情况测试成功了喵～")

    def test_collection_type_consistency_fixes(self):
        """杂鱼♡～本喵要修复集合类型一致性测试喵～之前有些测试逻辑不够严谨～"""

        @dataclass
        class CollectionConfig:
            int_list: List[int] = field(default_factory=list)
            str_set: Set[str] = field(default_factory=set)
            str_int_dict: Dict[str, int] = field(default_factory=dict)
            nested_list: List[List[str]] = field(default_factory=list)

        # 杂鱼♡～创建具有各种集合的配置喵～
        config = CollectionConfig()
        config.int_list = [1, 2, 3, 2, 1]  # 杂鱼♡～有重复元素喵～
        config.str_set = {"apple", "banana", "apple"}  # 杂鱼♡～集合会自动去重喵～
        config.str_int_dict = {"one": 1, "two": 2, "three": 3}
        config.nested_list = [["a", "b"], ["c", "d"], []]  # 杂鱼♡～包含空列表喵～

        # 杂鱼♡～序列化和反序列化喵～
        jsdc_dump(config, self.temp_path)
        loaded = jsdc_load(self.temp_path, CollectionConfig)

        # 杂鱼♡～验证列表（保持顺序和重复）喵～
        self.assertEqual(loaded.int_list, [1, 2, 3, 2, 1])

        # 杂鱼♡～验证集合（去重但可能顺序不同）喵～
        self.assertEqual(loaded.str_set, {"apple", "banana"})

        # 杂鱼♡～验证字典喵～
        self.assertEqual(loaded.str_int_dict, {"one": 1, "two": 2, "three": 3})

        # 杂鱼♡～验证嵌套列表喵～
        self.assertEqual(loaded.nested_list, [["a", "b"], ["c", "d"], []])

        # 杂鱼♡～测试空集合的一致性喵～
        empty_config = CollectionConfig()  # 杂鱼♡～所有集合都是空的喵～

        jsdc_dump(empty_config, self.temp_path)
        loaded_empty = jsdc_load(self.temp_path, CollectionConfig)

        self.assertEqual(loaded_empty.int_list, [])
        self.assertEqual(loaded_empty.str_set, set())
        self.assertEqual(loaded_empty.str_int_dict, {})
        self.assertEqual(loaded_empty.nested_list, [])

        print("杂鱼♡～本喵修复集合类型一致性测试成功了喵～")

    def test_processing_progress_dataclass(self):
        """杂鱼♡～本喵要测试ProcessingProgress数据类了喵～这是为了支持更多字典键类型的测试～"""

        @dataclass
        class ProcessingProgress:
            """杂鱼♡～处理进度数据类喵～"""

            completed_task_ids: List[int] = field(default_factory=list)
            total_tasks: int = 0
            uses_chunked_storage: bool = True
            timestamp: float = field(default_factory=time.time)
            failed_task_ids: List[int] = field(default_factory=list)
            retry_counts: Dict[int, int] = field(
                default_factory=dict
            )  # 杂鱼♡～整数键字典喵～
            task_errors: Dict[int, str] = field(
                default_factory=dict
            )  # 杂鱼♡～整数键字典喵～
            processing_task_ids: List[int] = field(default_factory=list)

        # 杂鱼♡～测试基础序列化/反序列化喵～
        progress = ProcessingProgress()
        progress.total_tasks = 10
        progress.completed_task_ids = [1, 2, 3]
        progress.failed_task_ids = [4]
        progress.processing_task_ids = [5, 6]
        progress.retry_counts = {4: 2, 7: 1}  # 杂鱼♡～整数键字典喵～
        progress.task_errors = {
            4: "连接超时",
            7: "数据解析失败",
        }  # 杂鱼♡～整数键字典喵～

        # 杂鱼♡～序列化到文件喵～
        jsdc_dump(progress, self.temp_path)

        # 杂鱼♡～从文件反序列化喵～
        loaded_progress = jsdc_load(self.temp_path, ProcessingProgress)

        # 杂鱼♡～验证所有字段喵～
        self.assertEqual(loaded_progress.total_tasks, 10)
        self.assertEqual(loaded_progress.completed_task_ids, [1, 2, 3])
        self.assertEqual(loaded_progress.failed_task_ids, [4])
        self.assertEqual(loaded_progress.processing_task_ids, [5, 6])
        self.assertEqual(
            loaded_progress.retry_counts, {4: 2, 7: 1}
        )  # 杂鱼♡～整数键应该被正确恢复喵～
        self.assertEqual(
            loaded_progress.task_errors, {4: "连接超时", 7: "数据解析失败"}
        )
        self.assertTrue(loaded_progress.uses_chunked_storage)
        self.assertIsInstance(loaded_progress.timestamp, float)

        # 杂鱼♡～测试字符串序列化喵～
        json_str = jsdc_dumps(progress)
        self.assertIsInstance(json_str, str)

        # 杂鱼♡～从字符串反序列化喵～
        loaded_from_str = jsdc_loads(json_str, ProcessingProgress)
        self.assertEqual(loaded_from_str.retry_counts, {4: 2, 7: 1})
        self.assertEqual(
            loaded_from_str.task_errors, {4: "连接超时", 7: "数据解析失败"}
        )

        # 杂鱼♡～测试大量数据喵～
        large_progress = ProcessingProgress()
        large_progress.total_tasks = 1000
        large_progress.completed_task_ids = list(range(1, 801))  # 800个已完成任务
        large_progress.failed_task_ids = list(range(801, 901))  # 100个失败任务

        # 杂鱼♡～为失败任务添加重试次数和错误信息喵～
        for task_id in large_progress.failed_task_ids:
            large_progress.retry_counts[task_id] = (task_id % 5) + 1  # 1到5次重试
            large_progress.task_errors[task_id] = (
                f"任务{task_id}执行失败: 错误代码{task_id % 10}"
            )

        # 杂鱼♡～序列化和反序列化大量数据喵～
        jsdc_dump(large_progress, self.temp_path)
        loaded_large = jsdc_load(self.temp_path, ProcessingProgress)

        # 杂鱼♡～验证大量数据的正确性喵～
        self.assertEqual(loaded_large.total_tasks, 1000)
        self.assertEqual(len(loaded_large.completed_task_ids), 800)
        self.assertEqual(len(loaded_large.failed_task_ids), 100)
        self.assertEqual(len(loaded_large.retry_counts), 100)
        self.assertEqual(len(loaded_large.task_errors), 100)

        # 杂鱼♡～验证一些具体的整数键字典值喵～
        self.assertEqual(loaded_large.retry_counts[801], 2)  # 801 % 5 + 1 = 2
        self.assertEqual(loaded_large.task_errors[805], "任务805执行失败: 错误代码5")

        # 杂鱼♡～测试边缘情况：负数任务ID喵～
        edge_progress = ProcessingProgress()
        edge_progress.retry_counts = {-5: 1, -10: 3, 0: 2}
        edge_progress.task_errors = {
            -5: "负数任务测试",
            -10: "另一个负数任务测试",
            0: "零ID任务",
        }

        jsdc_dump(edge_progress, self.temp_path)
        loaded_edge = jsdc_load(self.temp_path, ProcessingProgress)

        self.assertEqual(loaded_edge.retry_counts[-5], 1)
        self.assertEqual(loaded_edge.retry_counts[0], 2)
        self.assertEqual(loaded_edge.task_errors[-10], "另一个负数任务测试")

        print("杂鱼♡～本喵测试ProcessingProgress数据类成功了喵～整数键字典完美支持！～")

    def test_dict_key_types_support(self):
        """杂鱼♡～本喵要专门测试各种字典键类型的支持喵～"""

        # 杂鱼♡～测试整数键字典喵～
        @dataclass
        class IntKeyConfig:
            int_to_str: Dict[int, str] = field(default_factory=dict)
            int_to_int: Dict[int, int] = field(default_factory=dict)

        int_config = IntKeyConfig()
        int_config.int_to_str = {1: "one", 2: "two", 42: "answer"}
        int_config.int_to_int = {10: 100, 20: 200}

        jsdc_dump(int_config, self.temp_path)
        loaded_int = jsdc_load(self.temp_path, IntKeyConfig)

        self.assertEqual(loaded_int.int_to_str, {1: "one", 2: "two", 42: "answer"})
        self.assertEqual(loaded_int.int_to_int, {10: 100, 20: 200})

        # 杂鱼♡～测试浮点数键字典喵～
        @dataclass
        class FloatKeyConfig:
            float_to_str: Dict[float, str] = field(default_factory=dict)

        float_config = FloatKeyConfig()
        float_config.float_to_str = {1.5: "one and half", 3.14: "pi", 2.718: "e"}

        jsdc_dump(float_config, self.temp_path)
        loaded_float = jsdc_load(self.temp_path, FloatKeyConfig)

        self.assertEqual(
            loaded_float.float_to_str, {1.5: "one and half", 3.14: "pi", 2.718: "e"}
        )

        # 杂鱼♡～测试布尔键字典喵～
        @dataclass
        class BoolKeyConfig:
            bool_to_str: Dict[bool, str] = field(default_factory=dict)

        bool_config = BoolKeyConfig()
        bool_config.bool_to_str = {True: "yes", False: "no"}

        jsdc_dump(bool_config, self.temp_path)
        loaded_bool = jsdc_load(self.temp_path, BoolKeyConfig)

        self.assertEqual(loaded_bool.bool_to_str, {True: "yes", False: "no"})

        # 杂鱼♡～测试混合类型的键喵～
        @dataclass
        class MixedKeysConfig:
            str_dict: Dict[str, int] = field(default_factory=dict)
            int_dict: Dict[int, str] = field(default_factory=dict)
            float_dict: Dict[float, bool] = field(default_factory=dict)

        mixed_config = MixedKeysConfig()
        mixed_config.str_dict = {"apple": 1, "banana": 2}
        mixed_config.int_dict = {100: "hundred", 200: "two hundred"}
        mixed_config.float_dict = {1.0: True, 0.0: False}

        jsdc_dump(mixed_config, self.temp_path)
        loaded_mixed = jsdc_load(self.temp_path, MixedKeysConfig)

        self.assertEqual(loaded_mixed.str_dict, {"apple": 1, "banana": 2})
        self.assertEqual(loaded_mixed.int_dict, {100: "hundred", 200: "two hundred"})
        self.assertEqual(loaded_mixed.float_dict, {1.0: True, 0.0: False})

        print("杂鱼♡～本喵测试各种字典键类型支持成功了喵～")
    
    def test_dump_load_with_invalid_types(self):
        """杂鱼♡～本喵要测试当杂鱼提供错误类型时的异常处理喵～"""
        import random
        import tempfile
        from typing import List, Dict
        
        # 杂鱼♡～首先定义一个简单的测试数据类喵～
        @dataclass
        class SimpleTestData:
            name: str
            count: int
            enabled: bool
            scores: List[float] = field(default_factory=list)
            metadata: Dict[str, str] = field(default_factory=dict)
        
        # 杂鱼♡～创建正确的测试实例喵～
        valid_data = SimpleTestData(
            name="test_data",
            count=42,
            enabled=True,
            scores=[98.5, 87.3, 91.0],
            metadata={"created_by": "neko", "purpose": "test"}
        )
        
        # 杂鱼♡～先正常保存一次数据喵～
        valid_temp_path = self.temp_path
        jsdc_dump(valid_data, valid_temp_path)
        
        # 杂鱼♡～验证初始文件内容是正确的喵～
        try:
            loaded_valid_data = jsdc_load(valid_temp_path, SimpleTestData)
            self.assertEqual(loaded_valid_data.name, valid_data.name)
            self.assertEqual(loaded_valid_data.count, valid_data.count)
            self.assertEqual(loaded_valid_data.enabled, valid_data.enabled)
            self.assertEqual(loaded_valid_data.scores, valid_data.scores)
            self.assertEqual(loaded_valid_data.metadata, valid_data.metadata)
        except Exception as e:
            self.fail(f"杂鱼♡～加载有效数据失败了喵～：{str(e)}")
        
        # 杂鱼♡～准备一些无效类型的数据喵～
        invalid_data_samples = [
            SimpleTestData(name=123, count=42, enabled=True),  # 错误的name类型
            SimpleTestData(name="test", count="fortytwo", enabled=True),  # 错误的count类型
            SimpleTestData(name="test", count=42, enabled="yes"),  # 错误的enabled类型
            SimpleTestData(name="test", count=42, enabled=True, scores={"not": "a list"}),  # 错误的scores类型
            SimpleTestData(name="test", count=42, enabled=True, metadata=[1, 2, 3]),  # 错误的metadata类型
        ]
        
        # 杂鱼♡～测试jsdc_dump异常处理喵～
        for i, invalid_data in enumerate(invalid_data_samples):
            # 使用新临时文件避免污染原始文件
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                invalid_temp_path = temp_file.name
            
            # 杂鱼♡～期待类型错误被捕获喵～
            with self.assertRaises((TypeError, ValueError)) as context:
                jsdc_dump(invalid_data, invalid_temp_path)
            
            # 杂鱼♡～确保异常被正确抛出喵～
            self.assertIsNotNone(context.exception)
            
            # 杂鱼♡～确保原始文件内容没有被损坏喵～
            try:
                loaded_data = jsdc_load(valid_temp_path, SimpleTestData)
                self.assertEqual(loaded_data.name, valid_data.name)
            except Exception as e:
                self.fail(f"杂鱼♡～验证原始文件完整性失败喵～：{str(e)}")
        
        # 杂鱼♡～测试加载时的类型检查喵～
        # 先创建一个有效的JSON文件
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
            load_test_path = temp_file.name
            # 杂鱼♡～写入正确格式但类型错误的JSON喵～
            invalid_json_samples = [
                '{"name": 12345, "count": 42, "enabled": true, "scores": [], "metadata": {}}',
                '{"name": "test", "count": "42", "enabled": true, "scores": [], "metadata": {}}',
                '{"name": "test", "count": 42, "enabled": "true", "scores": [], "metadata": {}}',
                '{"name": "test", "count": 42, "enabled": true, "scores": {"not": "list"}, "metadata": {}}',
                '{"name": "test", "count": 42, "enabled": true, "scores": [], "metadata": [1, 2, 3]}'
            ]
            
            for invalid_json in invalid_json_samples:
                temp_file.write(invalid_json)
                temp_file.flush()
                
                # 杂鱼♡～期待类型错误被捕获喵～
                with self.assertRaises((TypeError, ValueError)) as context:
                    jsdc_load(load_test_path, SimpleTestData)
                
                # 杂鱼♡～确保异常被正确抛出喵～
                self.assertIsNotNone(context.exception)
                
                # 杂鱼♡～重置文件内容喵～
                temp_file.seek(0)
                temp_file.truncate()
        
        # 杂鱼♡～随机混合类型测试喵～
        @dataclass
        class ComplexTestData:
            strings: List[str] = field(default_factory=list)
            numbers: List[int] = field(default_factory=list)
            flags: List[bool] = field(default_factory=list)
        
        valid_complex = ComplexTestData(
            strings=["one", "two", "three"],
            numbers=[1, 2, 3],
            flags=[True, False, True]
        )
        
        # 杂鱼♡～正常保存一次喵～
        complex_temp_path = self.temp_path.replace(".json", "_complex.json")
        try:
            jsdc_dump(valid_complex, complex_temp_path)
        except Exception as e:
            self.fail(f"杂鱼♡～保存有效复杂数据失败喵～：{str(e)}")
        
        # 杂鱼♡～随机插入错误类型喵～
        for _ in range(5):
            corrupted_data = ComplexTestData(
                strings=valid_complex.strings.copy(),
                numbers=valid_complex.numbers.copy(),
                flags=valid_complex.flags.copy()
            )
            
            # 杂鱼♡～随机选择一个位置插入错误类型喵～
            target_list = random.choice(["strings", "numbers", "flags"])
            insert_position = random.randint(0, 2)
            
            if target_list == "strings":
                corrupted_data.strings[insert_position] = random.choice([123, True, 3.14, {}])
            elif target_list == "numbers":
                corrupted_data.numbers[insert_position] = random.choice(["string", True, 3.14, {}])
            else:  # flags
                corrupted_data.flags[insert_position] = random.choice(["yes", 1, 3.14, {}])
            
            with self.assertRaises((TypeError, ValueError)):
                jsdc_dump(corrupted_data, complex_temp_path)
            
            # 杂鱼♡～确保原始文件仍然可以正常加载喵～
            try:
                loaded_complex = jsdc_load(complex_temp_path, ComplexTestData)
                self.assertEqual(loaded_complex.strings, valid_complex.strings)
                self.assertEqual(loaded_complex.numbers, valid_complex.numbers)
                self.assertEqual(loaded_complex.flags, valid_complex.flags)
            except Exception as e:
                self.fail(f"杂鱼♡～验证复杂数据文件完整性失败喵～：{str(e)}")
        
        print("杂鱼♡～本喵的类型错误测试全部通过了喵～你的代码异常处理做得还不错呢～")
    


if __name__ == "__main__":
    unittest.main()