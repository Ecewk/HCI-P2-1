from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3, CardMaker, TransparencyAttrib

class ParallaxScene(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Disable the default mouse camera control
        self.disableMouse()

        # Set camera position to view the scene
        self.camera.setPos(Point3(0, -100, 50))  # Move the camera further back and slightly up
        self.camera.lookAt(Point3(0, 0, 0))      # Make sure it's looking at the origin

        # Load and position the layers
        self.background = self.load_layer("layers/cloudsBetter.png", Point3(0, -100, 10), scale=60)   # Background (sky)
        self.mountains1 = self.load_layer("layers/mountainBlue1.png", Point3(0, -90, 5), scale=40)    # Farther mountains
        self.mountains2 = self.load_layer("layers/mountainBlue2.png", Point3(0, -80, 2), scale=35)    # Closer mountains
        self.trees1 = self.load_layer("layers/Trees1.png", Point3(0, -70, 1), scale=30)               # Trees in the distance
        self.trees2 = self.load_layer("layers/Trees2.png", Point3(0, -60, 0), scale=25)               # Closer trees
        self.trees3 = self.load_layer("layers/Trees3.png", Point3(0, -50, -1), scale=25)              # Closest trees
        self.ground = self.load_layer("layers/groundSideView.png", Point3(0, -40, -3), scale=20)      # Ground in front

        # Update task to move the layers based on camera movement
        self.taskMgr.add(self.update_camera, "UpdateCamera")

    def load_layer(self, image_path, pos, scale):
        """Creates a textured card for a parallax layer and positions it."""
        texture = self.loader.loadTexture(image_path)
        if not texture:
            print(f"Failed to load texture: {image_path}")
        
        card_maker = CardMaker('layer')
        aspect_ratio = texture.getXSize() / texture.getYSize()
        card_maker.setFrame(-aspect_ratio, aspect_ratio, -1, 1)  # Adjust the frame size based on aspect ratio
        layer = self.render.attachNewNode(card_maker.generate())
        layer.setTexture(texture)
        layer.setTransparency(TransparencyAttrib.MAlpha)  # Enable transparency
        
        # Set initial position and scaling
        layer.setPos(pos)     # (x, y, z) position
        layer.setScale(scale)  # Adjust scale based on layer size
        
        print(f"Loaded layer {image_path} at position {layer.getPos()} with scale {scale} and aspect ratio {aspect_ratio}")
        
        return layer

    def update_camera(self, task):
        """Moves the camera to create the parallax effect."""
        # Simulate head movement or mouse input (replace with real head tracking if needed)
        mouse_x = self.mouseWatcherNode.getMouseX() if self.mouseWatcherNode.hasMouse() else 0
        mouse_y = self.mouseWatcherNode.getMouseY() if self.mouseWatcherNode.hasMouse() else 0

        # Adjust the camera movement, moving slower for deeper layers (parallax effect)
        self.background.setPos(-mouse_x * 2, -100, -mouse_y * 2)
        self.mountains1.setPos(-mouse_x * 1.8, -90, -mouse_y * 1.8)
        self.mountains2.setPos(-mouse_x * 1.6, -80, -mouse_y * 1.6)
        self.trees1.setPos(-mouse_x * 1.4, -70, -mouse_y * 1.4)
        self.trees2.setPos(-mouse_x * 1.2, -60, -mouse_y * 1.2)
        self.trees3.setPos(-mouse_x * 1.1, -50, -mouse_y * 1.1)
        self.ground.setPos(-mouse_x, -40, -mouse_y)

        return task.cont

# Run the scene
app = ParallaxScene()
app.run()