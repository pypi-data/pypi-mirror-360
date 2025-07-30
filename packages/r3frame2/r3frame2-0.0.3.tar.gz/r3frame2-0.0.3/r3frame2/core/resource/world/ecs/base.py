from ....log import R3logger
from ....atom import R3atom
from ....globals import pg
# from ..utils import 
import r3frame2 as r3

class R3ecs(R3atom):
    def __init__(self, entity_max: int = 65535) -> None:
        super().__init__()
        self.next: int = 0
        self.max: int = entity_max
        self.free: list[int] = []
        self.mask: list[int] = [0] * self.max
        self.active: list[int] = [0] * self.max

        self.systems: dict[type, r3.resource.ec.R3system] = {}
        self.components: dict[type, r3.resource.ec.R3component] = {}

    def request_entity(self) -> int:
        if len(self.free) > 0:
            entity = self.free.pop(0)
        else:
            if self.next >= self.max or self.next < 0:
                R3logger.info(f"[R3ecs] entity max reached: {self.next}")
                return self.max
            entity = self.next
            self.next += 1
        
        self.active[entity] = 0
        
        R3logger.info(f"[R3ecs] requested entity: {entity}")
        return entity

    def return_entity(self, entity: int) -> None:
        if entity >= self.max or entity < 0:
            R3logger.info(f"[R3ecs] invalid entity: {entity}")
            return
        
        self.mask[entity] = 0
        self.active[entity] = 0
        self.free.append(entity)
        
        R3logger.info(f"[R3ecs] returned entity: {entity}")
