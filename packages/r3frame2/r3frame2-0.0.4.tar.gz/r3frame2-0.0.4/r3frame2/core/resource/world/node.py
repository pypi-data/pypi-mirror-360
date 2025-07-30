from ...atom import R3atom
from ...globals import pg
from ...utils import div_v2i, div2_v2i
import r3frame2 as r3

class R3node(R3atom):
    def __init__(
            self, chunk,
            pos: list[int],
            size: list[int],
            ) -> None:
        super().__init__()
        self.data: list = []

        self.size: list[int] = size[:]
        self.a: int = self.size[0] * self.size[1]
        self.w: int = self.size[0]
        self.h: int = self.size[1]

        self.pos: list[int] = pos[:]
        self.x: int = self.pos[0]
        self.y: int = self.pos[1]
        self.c: list[int] = div2_v2i(self.pos, div_v2i(self.size, 2))

        self.chunk: r3.resource.R3chunk = chunk
        self.partition: r3.resource.R3gridPartition | r3.resource.R3treedPartition = None

    def _write_to_disk(self) -> None: pass
    def _read_from_disk(self) -> None: pass

    def transform(self, pos: list[float|int]) -> list[int]:
        return div_v2i(pos, self.node_size)

    def query(self, pos: list[int]) -> None: pass
    def insert(self, pos: list[int]) -> None: pass
    def remove(self, pos: list[int]) -> None: pass
