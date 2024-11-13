from typing import Callable, Dict, List

class EventSystem:
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event_name: str, handler: Callable) -> None:
        if event_name not in self.handlers:
            self.handlers[event_name] = []
        self.handlers[event_name].append(handler)
        
    def emit(self, event_name: str, *args, **kwargs) -> None:
        if event_name in self.handlers:
            for handler in self.handlers[event_name]:
                handler(*args, **kwargs) 