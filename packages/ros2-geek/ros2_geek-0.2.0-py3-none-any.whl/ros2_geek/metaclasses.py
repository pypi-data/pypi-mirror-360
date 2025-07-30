from threading import Lock
from weakref import WeakValueDictionary, WeakSet
from typing import Dict, Type, Any, Set
from dataclasses import dataclass
import logging
from abc import ABCMeta, abstractmethod
from collections import Counter


WeakSetType = Set
WeakDictType = Dict


class OverrideCheckMeta(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        mro: tuple = mcs.__mro__
        metaclasses = mro[: mro.index(OverrideCheckMeta) + 1]
        OverrideCheckMeta.check_meta_override_namespace(metaclasses, namespace)
        return super().__new__(mcs, name, bases, namespace)

    @staticmethod
    def get_class_basic_namespace():
        # TODO: add more basic methods for fast checking
        return {
            "__init__",
            "__call__",
            "__new__",
            "__module__",
            "__doc__",
            "__init_subclass__",
            "__annotations__",
        }

    @staticmethod
    def check_meta_override_namespace(
        metaclasses: tuple, namespace, ignore: Set[str] = None, raise_err: bool = True
    ):
        ignore = set() if ignore is None else ignore
        overide_ns: Set[str] = set()
        basic_ns = OverrideCheckMeta.get_class_basic_namespace()
        namespace = set(namespace)
        for mcs in metaclasses:
            meta_ns = set(mcs.__dict__)
            overide_ns |= namespace.intersection((meta_ns - basic_ns - ignore))
            if overide_ns:
                for ns in overide_ns:
                    if not ns.startswith("__"):
                        if raise_err:
                            raise TypeError(f"Can't override {mcs} method: {ns}")
                        else:
                            return True
        return False


class CachedMeta(type):
    __cache: Dict[Type, WeakDictType[tuple, Any]] = {}
    __lock: Lock = Lock()
    __call_num: Dict[Type, int] = {}

    def __call__(self, *args, **kwargs):
        cache_key = (self, args, frozenset(kwargs.items()))
        if self not in self.__cache:
            self.__cache[self] = WeakValueDictionary()
        cached = self.__cache[self]
        call_num = self.__call_num
        if cache_key not in cached:
            with self.__lock:
                if cache_key not in cached:
                    self.__get_logger().debug(
                        f"Instancing with: args={args} kwargs={kwargs}"
                    )
                    instance = super().__call__(*args, **kwargs)
                    cached[cache_key] = instance
                    call_num[self] = 0
        else:
            self.__get_logger().debug(f"Already instanced: args={args} kwargs={kwargs}")
        call_num[self] += 1
        return cached[cache_key]

    def get_instance_call_number(self) -> int:
        return self.__call_num[self]

    def __get_logger(self) -> logging.Logger:
        """Get the logger of the class"""
        return logging.getLogger(self.__name__)


class ManagedMeta(type):
    # each inherited metaclass has its own classes,
    # instances and called_num (per class)
    __classes: Dict[Type, Set[Type]] = {}
    __instances: Dict[Type, Dict[Type, WeakSetType[Any]]] = {}
    __add_number: Dict[Type, Counter] = {}

    def __init__(self, *args, **kwargs):
        # TODO: use __ for class variables and directly use self to get their values
        meta_cls = self.__class__
        self.__get_logger().debug(f"Singletonizing from metaclass: {meta_cls}")
        classes = self.__classes
        if meta_cls not in classes:
            classes[meta_cls] = set()
            self.__instances[meta_cls] = {}
            self.__add_number[meta_cls] = Counter()
        classes[meta_cls].add(self)
        self.__get_logger().debug("Added to classes")
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        # pass instance to cascade with other metaclasses, e.g. SingletonMeta
        self.__get_logger().debug(f"Calling with: args={args} kwargs={kwargs}")
        # will use inherit metaclass name
        instance = super().__call__(*args, **kwargs)
        self.add_instance(instance)
        return instance

    # def __prepare__(name, bases):
    #     # may conflict with decorator, so usually do not use
    #     return dict()

    def add_instance(self, instance: Any):
        """Add instance to the class (Note: for meta cascade call usage only)"""
        meta_cls = self.__class__
        self.__add_number[meta_cls][self] += 1
        instances = self.__instances[meta_cls]
        if self not in instances:
            instances[self] = WeakSet()
        self.__instances[meta_cls][self].add(instance)

    def is_instanced(self) -> bool:
        """Check if the class is instanced"""
        instances = self.__instances[self.__class__]
        return self in instances

    def get_instances(self) -> WeakSetType[Any]:
        """Get all instances of the class"""
        return self.__instances[self.__class__][self]

    def get_all_instances(self) -> Dict[Type, WeakSetType[Any]]:
        """Get all instances of all classes under the direct metaclass"""
        return self.__instances[self.__class__]

    def get_classes(self) -> Set[Type]:
        """Get all classes under the direct metaclass"""
        return self.__classes[self.__class__]

    def get_instance_number(self) -> int:
        """Get number of instances of the class"""
        # directly use meta name to avoid override problem
        return len(ManagedMeta.get_instances())

    def get_all_instance_number(self) -> Dict[Type, int]:
        """Get number of instances of all classes under the direct metaclass"""
        return {
            clas: len(instances)
            for clas, instances in ManagedMeta.get_all_instances(self).items()
        }

    def get_instance_add_number(self) -> int:
        return self.__add_number[self.__class__][self]

    def __get_logger(self) -> logging.Logger:
        """Get logger for the class"""
        return logging.getLogger(self.__name__)


class SingletonMeta(type):
    __instances: WeakDictType[Type, Any] = WeakValueDictionary()
    __call_num: Counter = Counter()

    def __init__(self, *args, **kwargs):
        self.__lock = Lock()

    def __call__(self, *args, **kwargs):
        instances = self.__instances
        # if not in, don't need to lock every time
        if self not in instances:
            # self.__get_logger().error(f"Not instanced: {self}")
            with self.__lock:
                if self not in instances:
                    self.__get_logger().debug("Instancing")
                    instance = super().__call__(*args, **kwargs)
                    instances[self] = instance
        else:
            self.__get_logger().debug(f"Already instanced")
        self.__call_num[self] += 1
        return instances[self]

    def get_instance_call_number(self) -> int:
        return self.__call_num[self]

    def __get_logger(self) -> logging.Logger:
        """Get the logger of the class"""
        return logging.getLogger(self.__name__)


class ManagedSingletonMeta(ManagedMeta, SingletonMeta):
    def __call__(self, *args, **kwargs):
        instance = SingletonMeta.__call__(self, *args, **kwargs)
        ManagedMeta.add_instance(self, instance)
        return instance


class ManagedCachedMeta(ManagedMeta, CachedMeta):
    def __call__(self, *args, **kwargs):
        instance = CachedMeta.__call__(self, *args, **kwargs)
        ManagedMeta.add_instance(self, instance)
        return instance


class SingletonABCMeta(SingletonMeta, ABCMeta, OverrideCheckMeta):
    pass


class ManagedSingletonABCMeta(ManagedSingletonMeta, ABCMeta, OverrideCheckMeta):
    pass


class ManagedCachedABCMeta(ManagedCachedMeta, ABCMeta, OverrideCheckMeta):
    pass


if __name__ == "__main__":

    class ModuleBasis(metaclass=ManagedSingletonABCMeta):
        defined_modules: Set[Type] = set()

        @dataclass
        class ModuleStatistics:
            # modules defined by inheriting ModuleBasis
            defined_names: Set[str]
            # modules that have been instanced
            used_names: Set[str]
            # number of modules that have been instanced
            used_number: int

        def __init__(self):
            self.__get_logger().debug(f"Initializd")

        def __init_subclass__(cls, **kwargs):
            cls.defined_modules.add(cls)
            cls.__get_logger().debug(f"Inherited from {cls.__base__}")
            cls.__get_logger().debug(f"Meta class is {cls.__class__}")

        @classmethod
        def get_defined_modules(cls) -> Set[type]:
            return cls.defined_modules

        @classmethod
        def get_defined_module_names(cls) -> Set[str]:
            names = {module.__name__ for module in cls.get_defined_modules()}
            return names

        @classmethod
        def get_used_module_classes(cls) -> Set[type]:
            return set(cls.get_all_instances().keys()) & cls.get_defined_modules()

        @classmethod
        def get_used_module_names(cls) -> Set[str]:
            return {module.__name__ for module in cls.get_used_module_classes()}

        @classmethod
        def get_used_module_instances(cls) -> Set[Any]:
            instances = cls.get_all_instances()
            usd = set()
            for clas in cls.get_used_module_classes():
                usd |= set(instances[clas])
            return usd

        @classmethod
        def get_used_module_number(cls) -> int:
            return len(cls.get_used_module_classes())

        @classmethod
        def get_call_module_number(cls) -> int:
            return cls.get_instance_call_number()

        @classmethod
        def get_module_statistics(cls) -> ModuleStatistics:
            return cls.ModuleStatistics(
                defined_names=cls.get_defined_module_names(),
                used_names=cls.get_used_module_names(),
                used_number=cls.get_used_module_number(),
            )

        @classmethod
        def __get_logger(cls) -> logging.Logger:
            """Get logger for the class"""
            return logging.getLogger(cls.__name__)

        @abstractmethod
        def activate(self):
            pass
