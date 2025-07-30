# Module Name: core/abstract/framework.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2024 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains abstract interfaces.

from abc import ABC
from typing import TypeVar

__version__ = "1.0.0.0"


class IWattleflowCoreInterface(ABC):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__


class IWattleflow(IWattleflowCoreInterface, ABC):
    def __init__(self, *args, **kwargs):
        IWattleflowCoreInterface.__init__(self)


T = TypeVar("T")
C = TypeVar("C", bound=IWattleflow)
