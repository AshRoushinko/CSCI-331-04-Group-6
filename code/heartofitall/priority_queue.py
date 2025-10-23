# code implements a min priority queue using heapq

import heapq
from typing import Any, List, Tuple


#uses a min-heap data struct so that smallest priority value is retreived first
# if priority is the same, FIFO
class PriorityQueue:

    def __init__(self) -> None:
        self._h: List[Tuple[float, int, Any]] = [] #_h is the internal heap, storing (priority, insertion_order, item)
        self._push_id = 0 #_push_id increasing counter to track insertion order

    # item in this case is  city
    def push(self, item: Any, priority: float) -> None:
        heapq.heappush(self._h, (float(priority), self._push_id, item))
        self._push_id += 1

    def pop(self) -> Any:
        _p, _i, item = heapq.heappop(self._h)
        return item

    def is_empty(self) -> bool:
        return not self._h
