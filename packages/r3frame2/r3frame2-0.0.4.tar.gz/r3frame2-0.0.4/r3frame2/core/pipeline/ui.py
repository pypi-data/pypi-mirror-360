from ..log import R3logger
from ..atom import R3atom
from ..globals import pg
# from ..utils import 
import r3frame2 as r3

class R3ui(R3atom):
    def __init__(
            self,
            app: "r3.app.R3app",
    ) -> None:
        super().__init__()
        self.app: r3.app.R3app = app
        self.database: r3.resource.R3database = app.database

    def render(self) -> None: pass
