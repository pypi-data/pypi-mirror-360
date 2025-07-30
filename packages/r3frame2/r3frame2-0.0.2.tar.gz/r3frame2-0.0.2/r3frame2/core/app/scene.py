from ..atom import R3atom
from ..globals import pg
# from ..utils import 
import r3frame2 as r3

class R3scene(R3atom):
    def __init__(
            self,
            app: "r3.app.R3app",
    ) -> None:
        super().__init__()
        self.app: r3.app.R3app = app
        self.database: r3.resource.R3database = app.database

        self.world: r3.resource.R3world = r3.resource.R3world()
        self.physics: r3.pipeline.R3physics = r3.pipeline.R3physics(app)
        
        self.ui: r3.pipeline.R3ui = r3.pipeline.R3ui(app)
        self.camera: r3.pipeline.R3camera = r3.pipeline.R3camera(app)
        self.renderer: r3.pipeline.R3renderer = r3.pipeline.R3renderer(app)

    def exit(self) -> None: raise NotImplementedError
    def init(self) -> None: raise NotImplementedError
    def events(self) -> None: raise NotImplementedError
    def update(self, dt: float) -> None: raise NotImplementedError
    def render(self) -> None: raise NotImplementedError
