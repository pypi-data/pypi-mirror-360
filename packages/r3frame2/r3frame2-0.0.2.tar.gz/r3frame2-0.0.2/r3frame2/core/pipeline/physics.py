from ..status import R3status
from ..log import R3logger
from ..atom import R3atom
from ..globals import pg
# from ..utils import 
import r3frame2 as r3

class R3physics(R3atom):
    def __init__(
            self,
            app: "r3.app.R3app",
    ) -> None:
        super().__init__()
        __meta__: dict = {
            "_count": 0,
        }
        self.data: dict[r3.resource.R3entity, list] = { k: v for k,v in __meta__.items() }
        
        self.app: r3.app.R3app = app
        self.database: r3.resource.R3database = app.database

        self.damp_value = 4
        self.damp_threshold = 0.8

    def _valid_entity(self, entity: "r3.resource.R3entity") -> int:
        if not isinstance(entity, r3.resource.R3entity):
            return R3status.physics.ENTITY_INVALID
        
        value = getattr(self, "data").get(entity, 0)
        if not value:
            return R3status.physics.ENTITY_NOT_FOUND
        else: return R3status.physics.ENTITY_FOUND

    def toggle(
            self,
            entity: "r3.resource.R3entity",
            speed: float = 100.0, mass: float = 50.0,
            ) -> int:
        if self._valid_entity(entity) == R3status.physics.ENTITY_FOUND:
            self.data.pop(entity)
            R3logger.debug("[R3physics] toggled entity physics off: (entity){entity}")
            return R3status.physics.ENTITY_FOUND
        elif self._valid_entity(entity) == R3status.physics.ENTITY_NOT_FOUND:
            self.data[entity] = [
                entity,
                [0.0, 0.0], # velocity
            ]
            R3logger.debug("[R3physics] toggled entity physics on: (entity){entity}")
            return R3status.physics.ENTITY_FOUND
        else:
            R3logger.error("[R3physics] entity not found: (entity){entity}")
            return R3status.physics.ENTITY_NOT_FOUND

    def velocity(self, entity: "r3.resource.R3entity") -> list[float]:
        valid = self._valid_entity(entity)
        if valid != R3status.physics.ENTITY_FOUND:
            R3logger.error(f"[R3physics] entity not found: (entity){entity}")
        else: return self.data[entity][1][0]

    def direction(self, entity: "r3.resource.R3entity") -> list[float]:
        valid = self._valid_entity(entity)
        if valid != R3status.physics.ENTITY_FOUND:
            R3logger.error(f"[R3physics] entity not found: (entity){entity}")
        else: return [(self.data[entity][1][0] > 0) - (self.data[entity][1][0] < 0),
                      (self.data[entity][1][1] > 0) - (self.data[entity][1][1] < 0)]
    
    def set_velocity(self, entity: "r3.resource.R3entity", dx: float = None, dy: float = None) -> bool:
        valid = self._valid_entity(entity)
        if valid != R3status.physics.ENTITY_FOUND:
            R3logger.error(f"[R3physics] entity not found: (entity){entity}")
        else:
            if dx is not None: self.data[entity][1][0] = dx
            if dy is not None: self.data[entity][1][1] = dy

    def update(self, dt: float) -> None:
        for e in self.data:
            if e == "_count": continue
            self.data[e][0].pos[0] += self.data[e][1][0] * dt
            self.data[e][0].pos[1] += self.data[e][1][1] * dt
            
            self.data[e][1][0] *= (1 - self.damp_value * dt)
            self.data[e][1][1] *= (1 - self.damp_value * dt)

            if abs(self.data[e][1][0]) < self.damp_threshold:
                self.data[e][1][0] = 0
            if abs(self.data[e][1][1]) < self.damp_threshold:
                self.data[e][1][1] = 0
