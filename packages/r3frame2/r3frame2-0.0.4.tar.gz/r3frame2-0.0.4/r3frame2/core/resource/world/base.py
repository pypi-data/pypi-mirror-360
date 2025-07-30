from ...atom import R3atom
from ...globals import pg
from ...utils import div_v2i
import r3frame2 as r3

class R3world(R3atom):
    def __init__(self) -> None:
        super().__init__()
        self.ecs: r3.resource.R3ecs = r3.resource.R3ecs()

        self.chunks_loaded: list[list[int]] = []
        self.chunks: dict[list[int], r3.resource.R3chunk] = {}
        
    def _write_to_disk(self) -> None: pass
    def _read_from_disk(self) -> None: pass

    def transform(self, pos: list[float|int]) -> list[int]: pass

    def query(self, pos: list[int]) -> None: pass
    def insert(self, pos: list[int]) -> None: pass
    def remove(self, pos: list[int]) -> None: pass
