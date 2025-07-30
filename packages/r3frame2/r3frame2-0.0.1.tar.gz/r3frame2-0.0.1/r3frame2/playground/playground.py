import r3frame2 as r3

class PlaygroundScene(r3.app.R3scene):
    def __init__(self, app):
        super().__init__(app)

    def init(self):
        # load an R3entity
        self.database.load_entity("player", [100, 100])
        
        # query said entity and toggle physics on it
        self.player = self.database.query_entity("player")
        self.physics.toggle(self.player)
    
    def exit(self): pass

    def events(self):
        # handle movement along the x-axis
        if self.app.events.key_held(self.app.keyboard.A):
            self.physics.set_velocity(self.player, dx=-100)
        if self.app.events.key_held(self.app.keyboard.D):
            self.physics.set_velocity(self.player, dx=100)

        # handle movement along the y-axis
        if self.app.events.key_held(self.app.keyboard.W):
            self.physics.set_velocity(self.player, dy=-100)
        if self.app.events.key_held(self.app.keyboard.S):
            self.physics.set_velocity(self.player, dy=100)

    def update(self, dt: float): pass

    def render(self):
        self.app.window.blit(self.player.surface.surface, self.player.pos)

class PlaygroundApp(r3.app.R3app):
    def __init__(self):
        super().__init__(title="R3 Playground")

    def init(self):
        self.add_scene("player", PlaygroundScene)
        self.set_scene("player")

    def exit(self): pass

def main() -> None:
    PlaygroundApp().run()
