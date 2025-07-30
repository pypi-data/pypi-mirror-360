from ...atom import R3atom
from ...globals import pg
from ...utils import add_v2, div_v2
import r3frame2 as r3

# entity data container -- surface assigned on database entry
# R3database.entity[key] -> R3entity
class R3entity(R3atom):
    def __init__(
            self,
            eid: int,
            pos: list[int] = [0, 0],
            size: list[int] = [32, 32],
            rgba: list[int] = [255, 255, 255, 255],
            rgba_key: list[int] = [0, 0, 0, 0],
    ) -> None:
        super().__init__()
        self.eid: int = eid
        self.pos: list[int] = pos[:]
        self.size: list[int] = size[:]
        
        self.rgba: list[int] = rgba[:]
        self.rgba_key: list[int] = rgba_key[:]
        
        self.anim: r3.resource.R3anim = None
        self.surface: r3.resource.R3surf = None
    
    @property
    def red(self) -> int:
        return self.rgba[0]
    @property
    def green(self) -> int:
        return self.rgba[1]
    @property
    def blue(self) -> int:
        return self.rgba[2]
    @property
    def alpha(self) -> int:
        return self.rgba[3]

    @property
    def w(self) -> float:
        return self.size[0]
    @property
    def h(self) -> float:
        return self.size[1]
    @property
    def a(self) -> float:
        return self.size[0] * self.size[1]

    @property
    def x(self) -> float:
        return self.pos[0]
    @property
    def y(self) -> float:
        return self.pos[1]
    @property
    def z(self) -> float:
        return self.pos[2]
    @property
    def c(self) -> list[float]:
        return add_v2(self.pos, div_v2(self.size, 2))
