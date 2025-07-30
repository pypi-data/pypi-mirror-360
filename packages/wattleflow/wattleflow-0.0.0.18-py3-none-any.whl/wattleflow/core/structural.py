# Module Name: structural.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2024 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains abstract structural design patterns.

from abc import abstractmethod, ABC
from .framework import IWattleflow
from typing import Any

"""
Structural interfaces
    Adapter
        ITarget
        IAdaptee
        IAdapter
    Bridge
        IImplementor
        IAbstraction
    Composite
        IComponent
        IComposite
    Decorator
        IDecorator
    Facade
        IFacade
    Flyweight
        IFlyweight
        IFlyweightFactory
    Proxy
        IProxy
"""


# Structural interfaces
# Adapter interfaces (ITarget, IAdaptee, IAdapter)
class ITarget(IWattleflow, ABC):
    @abstractmethod
    def request(self) -> Any:
        pass


class IAdaptee(IWattleflow, ABC):
    @abstractmethod
    def specific_request(self) -> Any:
        pass


class IAdapter(ITarget, ABC):
    def __init__(self, adaptee: IAdaptee):
        self._adaptee = adaptee

    @abstractmethod
    def request(self) -> ITarget:
        pass


# Bridge interfaces (IImplementor, IAbstraction)
class IImplementor(IWattleflow, ABC):
    @abstractmethod
    def operation_impl(self):
        pass


class IAbstraction(IWattleflow, ABC):
    @abstractmethod
    def operation(self):
        pass


# Composite interface (IComponent, IComposite)
class IComponent(IWattleflow, ABC):
    @abstractmethod
    def process(self, data):
        pass


class IComposite(IComponent, ABC):
    @abstractmethod
    def add(self, component):
        pass

    @abstractmethod
    def remove(self, component):
        pass

    @abstractmethod
    def get_child(self, index):
        pass


# Decorator interface
class IDecorator(IComponent, ABC):
    @abstractmethod
    def set_component(self, component: IComponent):
        pass


# Facade interface
class IFacade(IWattleflow, ABC):
    @abstractmethod
    def operation(self):
        pass


# Flyweight interface
class IFlyweight(IWattleflow, ABC):
    @abstractmethod
    def operation(self, extrinsic_state):
        pass


class IFlyweightFactory(IWattleflow, ABC):
    @abstractmethod
    def get_flyweight(self, key) -> Any:
        pass


# Proxy interface
class IProxy(IWattleflow, ABC):
    @abstractmethod
    def request(self) -> Any:
        pass
