from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Load a 3D model
        self.model = self.loader.loadModel("models/environment")
        self.model.reparentTo(self.render)

        # Position the model
        self.model.setPos(Point3(0, 50, -100))

app = MyApp()
app.run()

