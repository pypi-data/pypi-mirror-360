from abc import ABCMeta, abstractmethod
from functools import singledispatchmethod

from budget.table import Table


class Renderer(metaclass=ABCMeta):
    @singledispatchmethod
    def render(self, arg):
        raise TypeError("unknown renderable type")

    @render.register
    def _(self, table: Table):
        return self.render_table(table)

    @abstractmethod
    def render_table(self, table: Table):
        pass
