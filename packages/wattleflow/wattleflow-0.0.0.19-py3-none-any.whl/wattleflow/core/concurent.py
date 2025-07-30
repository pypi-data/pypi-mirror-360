# Module Name: concurent.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2024 WattleFlow
# License: Apache 3 License
# Description: This modul contains abstract concurent design patterns.

from abc import ABC, abstractmethod
from typing import List
from .framework import IWattleflow

"""
Concurrency Interfaces
    Actor-System
        IActor
        ISystem
    Future/Promise
        IFuture
        IPromise
    Callback:
        ICallback
    Reactive Programming
        IObservableReactive
        IObserverReactive
    EventLoop
        IEventLoop
    Pub-Sub (Publisher-Subscriber)
        IPublisher
        ISubscriber
    MessageQueue
        IMessageQueue
    ThreadPool
        IThreadPool
    Coroutine
        ICoroutine
    MapReduce
        IMapper
        IReducer
    Bulk Synchronous Parallel Interfaces
        ISuperstep
        IBSPSystem
    Fork/Join Interfaces
        IForkJoinTask
        IForkJoinPool
    Barier
        IBarrier
    Divide-and-conquer
        IDivideAndConquer
    Data Parallel Task
        IDataParallelTask
    Work-Stealing
        IWorkStealingScheduler
        IWorker
    Stencil
        IStencil
    Graph-Processing
        IGraphProcessing
    SPMD (Single Program, Multiple Data)
        ISPMDProgram
"""


# Future/Promise Interfaces
class IFuture(IWattleflow, ABC):
    """
    IFuture -   Future/Promise desing pattern abstract interface.
    Interface:
        result()
    """

    @abstractmethod
    def result(self):
        pass


class IPromise(IWattleflow, ABC):
    """
    IPromise -   Future/Promise desing pattern abstract interface.
    Interface:
        set_result()
    """

    @abstractmethod
    def set_result(self, result):
        pass


# Callback Interface
class ICallback(IWattleflow, ABC):
    """
    ICallback -  Callback desing pattern abstract interface.
    Interface:
        set_result()
    """

    @abstractmethod
    def call(self, *args, **kwargs):
        pass


# Reactive Programming Interfaces
class IObserverReactive(IWattleflow, ABC):
    @abstractmethod
    def update(self, observable, *args, **kwargs) -> None:
        pass


class IObservableReactive(IWattleflow, ABC):
    def __init__(self):
        self._observers: List[IObserverReactive] = []

    def add_observer(self, observer: IObserverReactive) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: IObserverReactive) -> None:
        self._observers.remove(observer)

    def notify_observers(self, *args, **kwargs) -> None:
        for observer in self._observers:
            observer.update(self, *args, **kwargs)


# Event-Loop Interface
class IEventLoop(IWattleflow, ABC):
    """
    IEventLoop -  EventLoop desing pattern abstract interface.
    Interface:
        set_result()
    """

    @abstractmethod
    def run_forever(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def call_soon(self, callback, *args):
        pass


# Pub-Sub (IPublisher-ISubscriber)
class IPublisher(IWattleflow, ABC):
    @abstractmethod
    def subscribe(self, subscriber):
        pass

    @abstractmethod
    def unsubscribe(self, subscriber):
        pass

    @abstractmethod
    def notify(self, message):
        pass


class ISubscriber(IWattleflow, ABC):
    @abstractmethod
    def update(self, message):
        pass


# Message-Que Interface
class IMessageQueue(IWattleflow, ABC):
    @abstractmethod
    def send(self, message):
        pass

    @abstractmethod
    def receive(self):
        pass


# ThreadPool-Pool Interface
class IThreadPool(IWattleflow, ABC):
    @abstractmethod
    def submit(self, task):
        pass

    @abstractmethod
    def shutdown(self, wait=True):
        pass


# Coroutine Interface
class ICoroutine(IWattleflow, ABC):
    @abstractmethod
    def send(self, value):
        pass

    @abstractmethod
    def throw(self, typ, val=None, tb=None):
        pass

    @abstractmethod
    def close(self):
        pass


# MapReduce Interface (IMapper, IReducer)
class IMapper(IWattleflow, ABC):
    @abstractmethod
    def map(self, data):
        pass


class IReducer(IWattleflow, ABC):
    @abstractmethod
    def reduce(self, key, values):
        pass


# Bulk Synchronous Parallel Interfaces(ISuperstep, IBSPSystem)
class ISuperstep(IWattleflow, ABC):
    @abstractmethod
    def execute(self, data):
        pass


class IBSPSystem(IWattleflow, ABC):
    @abstractmethod
    def run_supersteps(self, supersteps, data):
        pass


# Fork/Join Interfaces (IForkJoinTask,IForkJoinPool)
class IForkJoinTask(IWattleflow, ABC):
    @abstractmethod
    def fork(self):
        pass

    @abstractmethod
    def join(self):
        pass


class IForkJoinPool(IWattleflow, ABC):
    @abstractmethod
    def invoke(self, task):
        pass


# Barier Interface
class IBarrier(IWattleflow, ABC):
    @abstractmethod
    def wait(self):
        pass


# Divide-and-conquer Interface
class IDivideAndConquer(IWattleflow, ABC):
    @abstractmethod
    def divide(self, problem):
        pass

    @abstractmethod
    def solve_subproblem(self, subproblem):
        pass

    @abstractmethod
    def combine(self, solutions):
        pass


# DataParallelTask Interface
class IDataParallelTask(IWattleflow, ABC):
    @abstractmethod
    def execute(self, data_chunk):
        pass


# Work-Stealing Interface (IWorkStealingScheduler, IWorker)
class IWorkStealingScheduler(IWattleflow, ABC):
    @abstractmethod
    def steal(self):
        pass


class IWorker(IWattleflow, ABC):
    @abstractmethod
    def do_work(self):
        pass


# Stencil Interface
class IStencil(IWattleflow, ABC):
    @abstractmethod
    def apply(self, grid, point):
        pass


# Graph-Processing Interface
class IGraphProcessing(IWattleflow, ABC):
    @abstractmethod
    def process_vertex(self, vertex):
        pass

    @abstractmethod
    def process_edge(self, edge):
        pass


# SPMD (Single Program, Multiple Data)
class ISPMDProgram(IWattleflow, ABC):
    @abstractmethod
    def execute(self, data_partition):
        pass
