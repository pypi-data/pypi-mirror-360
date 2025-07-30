# Module Name: transactional.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2024 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains transactional interfaces.

from abc import ABC, abstractmethod
from datetime import datetime
from typing import (
    Any,
    Dict,
    Generic,
    Optional,
)
from .framework import T
from .behavioral import (
    IWattleflow,
)
from .creational import ISingleton
from .structural import IAdaptee


"""
Additional Interfaces Specific to Flow-Based Programming
    Actor-System
        IActor
        ISystem
    Blackboard
        IBlackboard
    Event-Driven
        IEventListener
        IEventSource
    Pipeline
        IPipeline
    Query
        IQuery
    Repository
        IRepository
    Saga
        ISaga
    Unit-of-work
        IUnitOfWork
"""


# Actor-System (IActor, ISystem)
class IActor(IWattleflow, ABC):
    """
    IActor - Actor-System design pattern abstract interface.
    Interface:
        receive(self, message)
    """

    @abstractmethod
    def receive(self, message):
        pass


class ISystem(IWattleflow, ABC):
    """
    ISystem - Actor-System design pattern abstract interface.
    Interface:
        create_actor(self, actor_class)
    """

    @abstractmethod
    def create_actor(self, actor_class, *args, **kwargs):
        pass

    @abstractmethod
    def send_message(self, actor, message, *args, **kwargs):
        pass


# Document
class IDocument(IAdaptee, Generic[T], ABC):
    @property
    @abstractmethod
    def identifier(self) -> str:
        pass

    @abstractmethod
    def update_content(self, data: T):
        pass

    @abstractmethod
    def specific_request(self) -> T:
        pass


# Event-Driven Interface (IEvent, IEventListener, IDataflowComponent)
class IEvent(ABC):
    @property
    @abstractmethod
    def correlation_id(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def source(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def timestamp(self) -> datetime:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @property
    @abstractmethod
    def payload(self) -> Dict[str, Any]:
        pass


class IEventListener(IWattleflow, ABC):
    @abstractmethod
    def on_event(self, event: IEvent):
        pass


# Event-Source Interface
class IEventSource(IWattleflow, ABC):
    @abstractmethod
    def register_listener(self, listener: IEventListener):
        pass

    @abstractmethod
    def emit_event(self, event):
        pass


# Repository interface
class IRepository(IWattleflow, ABC):
    @property
    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def read(self, identifier: str, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def write(self, item: Any, *args, **kwargs) -> Any:
        pass


# Blackboard Interface (IBlackboard, IModule)
class IBlackboard(IWattleflow, ABC):
    @property
    @abstractmethod
    def canvas(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def create(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def read(self, identifier: str, *args, **kwargs) -> Optional[Any]:
        pass

    @abstractmethod
    def register(self, repository: IRepository, *args, **kwargs):
        pass

    @abstractmethod
    def write(self, item: Any, *args, **kwargs) -> str:
        pass


class IModule(IWattleflow, ABC):
    @abstractmethod
    def update(self, blackboard: IBlackboard, *args, **kwargs) -> None:
        pass


# Pipeline Interface
class IPipeline(IWattleflow, ABC):
    @abstractmethod
    def process(self, processor, item, *args, **kwargs) -> None:
        pass


# IProcessor Interface
class IProcessor(IWattleflow, ABC):
    @abstractmethod
    def create_generator(self) -> Any:
        pass

    @abstractmethod
    def start(self) -> None:
        pass


# Query interface
class IQuery(IWattleflow, ABC):
    @abstractmethod
    def execute(self):
        pass


# Saga pattern
class ISaga(IWattleflow, ABC):
    @abstractmethod
    def start(self, initial_state, *args, **kwargs):
        pass

    @abstractmethod
    def handle_event(self, event, *args, **kwargs):
        pass

    @abstractmethod
    def compensate(self):
        pass


# Unit of Work interface
class IUnitOfWork(IWattleflow, ABC):
    """
    Interface for the UnitOfWork pattern.
    """

    @abstractmethod
    def commit(self):
        """Commits the current transaction."""
        pass

    @abstractmethod
    def rollback(self):
        """Rolls back the current transaction."""
        pass

    @abstractmethod
    def register_new(self, entity, *args, **kwargs):
        """Registers a new entity to be added to the database."""
        pass

    @abstractmethod
    def register_dirty(self, entity, *args, **kwargs):
        """Registers an existing entity that has been modified."""
        pass

    @abstractmethod
    def register_deleted(self, entity, *args, **kwargs):
        """Registers an entity to be deleted from the database."""
        pass


class IScheduler(ISingleton, IEventSource):
    @abstractmethod
    def setup_orchestrator(self, *args, **kwargs):
        pass

    @abstractmethod
    def start_orchestration(self, parallel: bool = False):
        pass

    @abstractmethod
    def stop_orchestration(self):
        pass

    @abstractmethod
    def register_listener(self, listener: IEventListener) -> None:
        pass

    @abstractmethod
    def emit_event(self, event, **kwargs):
        pass
