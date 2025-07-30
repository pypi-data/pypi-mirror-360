from __future__ import annotations
from abc import ABC, abstractmethod


class SpecMixin(ABC):
    @abstractmethod
    def to_option(self):
        pass
