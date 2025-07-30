# Module Name: behavioural.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2024 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains abstract design pattern interfaces.

from abc import ABC, abstractmethod
from typing import (
    Any,
    AsyncIterator,
    Generic,
    Iterator,
    Optional,
    Union
)
from .framework import IWattleflow, T


"""
Behavioral Interfaces
    Chain of Responsibility
        IHandler
    Command
        ICommand
    Interpreter
        IExpression
    Iterator
        IIterator
        IAggregate
    Mediator
        IMediator
    Memento
        IMemento
        IOriginator
    Observer
        IObserver
        IObservable
    State
        IState
        IStateContext
    Strategy
        IStrategy
        IStrategyContext
    Template Method
        ITemplate
    Visitor
        IVisitor
        IElement
"""


# Behavioural interfaces
# Chain of responsiblity interfaces (IHandler, ICommand, IInvoker)
# IHandler
class IHandler(IWattleflow, ABC):
    """
    IHandler - Chain of responsibilty abstract interface.

    Interface:
        set_next(self, handler)
        handle(self, request)
    """

    @abstractmethod
    def set_next(self, handler: "IHandler"):
        pass

    @abstractmethod
    def handle(self, request):
        pass


class ICommand(IWattleflow, ABC):
    """
    ICommand - Chain of responsibilty abstract interface.

    Interface:
        execute(self, *args, **kwargs)
    """

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass


class IInvoker(IWattleflow, ABC):
    """
    IInvoker - Chain of responsibilty abstract interface.

    Interface:
        set_command(self, command)
        invoke(self)
    """

    @abstractmethod
    def set_command(self, command: ICommand):
        pass

    @abstractmethod
    def invoke(self) -> Any:
        pass


# Interpreter Interface
class IExpression(IWattleflow, ABC):
    """
    IExpression - abstract interface.

    Interface:
        interpret(self)
    """

    @abstractmethod
    def interpret(self, context):
        pass


# Iterator interfaces (IIterator, IAsyncIterator, IAggregate)
# IIterator
class IIterator(IWattleflow, Iterator[T], Generic[T], ABC):
    def __init__(self) -> None:
        self._iterator: Optional[Iterator[T]] = None

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if self._iterator is None:
            self._iterator = self.create_iterator()
        return next(self._iterator)

    @abstractmethod
    def create_iterator(self) -> Iterator[T]:
        pass


# IAsyncIterator
class IAsyncIterator(IWattleflow, AsyncIterator[T], Generic[T], ABC):
    def __init__(self) -> None:
        self._iterator: Optional[AsyncIterator[T]] = None

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        if self._iterator is None:
            self._iterator = await self.create_iterator()
        return await self._iterator.__anext__()

    @abstractmethod
    async def create_iterator(self) -> AsyncIterator[T]:
        pass


# IAggregate
class IAggregate(IWattleflow, Generic[T], ABC):
    @abstractmethod
    def create_iterator(self) -> Union[IIterator[T], IAsyncIterator[T]]:
        pass


# Mediator interfaces
class IMediator(IWattleflow, ABC):
    """
    IMediator - abstract interface.

    Interface:
        notify(self, sender, event)
    """

    @abstractmethod
    def notify(self, sender, event):
        pass


class IColleague(IWattleflow, ABC):
    """
    IColleage - abstract interface.

    Interface:
        set_mediator(self, mediator)
        event_occurred(self, event)
    """

    @abstractmethod
    def set_mediator(self, mediator):
        pass

    @abstractmethod
    def event_occurred(self, event):
        pass


# Memento Interfaces (IMemento, IOriginator)
# IMemento
class IMemento(IWattleflow, ABC):
    """
    IMemento - abstract interface.

    Interface:
        get_state(self)
    """

    @abstractmethod
    def get_state(self):
        pass


class IOriginator(IWattleflow, ABC):
    """
    IOriginator - abstract interface.

    Interface:
        save_state(self)
        restore_state(self, memento)
    """

    @abstractmethod
    def save_state(self):
        pass

    @abstractmethod
    def restore_state(self, memento: IMemento):
        pass


# Observer interfaces
# Reactive Programming Interfaces
class IObserver(IWattleflow, ABC):
    """
    IObserver - Observer/Reactive Programming Interface desing pattern
                abstract interface.

    Interface:
        subscribe(self,observer)
    """

    @abstractmethod
    def update(self, *args, **kwargs):
        pass


class IObservable(IWattleflow, ABC):
    """
    IObservable - Observer/Reactive Programming Interface desing pattern
                  abstract interface.

    Interface:
        subscribe(self, observer: IObserver):
    """

    @abstractmethod
    def subscribe(self, observer: IObserver):
        pass


# State interfaces
# State (IState, IStateContext)
class IState(IWattleflow, ABC):
    """
    IState - State abstract interface.
    """

    pass


class IStateContext(IWattleflow, ABC):
    """
    IStateContext - State abstract interface.
    """

    pass


# Strategy interfaces
# Strategy IStrategy, IStrategyContext
class IStrategy(IWattleflow, ABC):
    """
    IStrategy - Strategy abstract interface.
    """

    pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass


class IStrategyContext(IWattleflow, ABC):
    """
    IStrategyContext - Strategy abstract interface.
    """

    @abstractmethod
    def set_strategy(self, strategy: IStrategy) -> None:
        pass

    @abstractmethod
    def execute_strategy(self, *args, **kwargs) -> Any:
        pass


# Template method (ITemplate)
class ITemplate(IWattleflow, ABC):
    def process(self):
        """The template method defining the steps of the process."""
        self.initialise()
        self.perform_task()
        self.finalise()

    @abstractmethod
    def initialise(self):
        """Step to be implemented by subclasses for initial setup."""
        pass

    @abstractmethod
    def perform_task(self):
        """The main task to be implemented by subclasses."""
        pass

    @abstractmethod
    def finalise(self):
        """Step to be implemented by subclasses to clean up or finalise."""
        pass


# Visitor interfaces
# Visitor (IVisitor IElement)
class IVisitor(IWattleflow, ABC):
    """
    IVisitor - Abstract interface for Visitor pattern.
    """

    @abstractmethod
    def visit(self, element: "IElement") -> Any:
        pass


class IElement(IWattleflow, ABC):
    """
    IElement - Abstract interface for elements that accept visitors.
    """

    @abstractmethod
    def accept(self, visitor: IVisitor):
        pass


# ILogger interface (*)
class ILogger(IObservable, ABC):

    @abstractmethod
    def subscribe(self, observer):
        pass

    @abstractmethod
    def critical(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def debug(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def exception(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def error(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def fatal(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def info(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def warning(self, level, msg, *args, **kwargs):
        pass
