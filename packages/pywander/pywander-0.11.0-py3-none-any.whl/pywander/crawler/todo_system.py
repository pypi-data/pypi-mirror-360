import queue
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
todo_queue = queue.PriorityQueue()


@dataclass(order=True)
class TodoItem:
    priority: int  # 优先级 数字越小越优先执行
    func: callable
    args: list
    kwargs: dict
    env: dict  # 会影响主控程序总的环境和行为

    def __post_init__(self):
        if self.priority is None:
            self.priority = 0
        if self.args is None:
            self.args = list()
        if self.kwargs is None:
            self.kwargs = dict()
        if self.env is None:
            self.env = dict()


def do_nothing(*args, **kwargs):
    """
    良好的工作流程最终以本函数什么都不做为结束点. 因为上一个工作流程虽然是实质工作的结束,但仍可能有部分环境变量的更改需要向主控上报.
    """
    pass


