from ...atom import R3atom
from ...globals import pg
from ...utils import div_v2i, div2_v2i
import r3frame2 as r3

class R3chunk(R3atom):
    def __init__(
            self, world,
            pos: list[int],
            node_size: list[int],
            chunk_size: list[int],
            ) -> None:
        super().__init__()
        self.size: list[int] = chunk_size[:]
        self.a: int = self.size[0] * self.size[1]
        self.w: int = self.size[0]
        self.h: int = self.size[1]

        self.pos: list[int] = pos[:]
        self.x: int = self.pos[0]
        self.y: int = self.pos[1]
        self.c: list[int] = div2_v2i(self.pos, div_v2i(self.size, 2))
        
        self.node_size: list[int] = node_size[:]
        self.node_a: int = self.node_size[0] * self.node_size[1]
        self.node_w: int = self.node_size[0]
        self.node_h: int = self.node_size[1]
        
        self.world: r3.resource.R3world = world
        
        self.nodes_loaded: list[list[int]] = []
        self.nodes: dict[list[int], r3.resource.R3node] = {}

        self.partition: r3.resource.R3gridPartition | r3.resource.R3treePartition = None

    def _write_to_disk(self) -> None: pass
    def _read_from_disk(self) -> None: pass

    def transform(self, pos: list[float|int]) -> list[int]: pass

    def query(self, pos: list[int]) -> None: pass
    def insert(self, pos: list[int]) -> None: pass
    def remove(self, pos: list[int]) -> None: pass
