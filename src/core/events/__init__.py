from typing import Any, Callable, Dict, List

class EventEmitter:
    """事件发射器类,用于处理游戏中的事件系统"""
    
    def __init__(self):
        self._events: Dict[str, List[Callable[..., None]]] = {}
        
    def on(self, event_name: str, callback: Callable[..., None]) -> None:
        """注册事件监听器"""
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(callback)
        
    def off(self, event_name: str, callback: Callable[..., None]) -> None:
        """移除事件监听器"""
        if event_name in self._events:
            self._events[event_name].remove(callback)
            if not self._events[event_name]:
                del self._events[event_name]
                
    def emit(self, event_name: str, *args, **kwargs) -> None:
        if event_name in self._events:
            for callback in self._events[event_name]:
                callback(*args, **kwargs) 