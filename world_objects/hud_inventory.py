from meshes.hud_inventory_mesh import HudInventoryMesh
from settings import DIRT, WOOD, ROCK

class HudInventory:
    def __init__(self, app):
        self.app = app
        self.mesh = HudInventoryMesh(app, slots=3)
        self.inventory_ids = [DIRT, WOOD, ROCK]
        self.selected = 0

    def set_selected(self, index):
        if 0 <= index < len(self.inventory_ids):
            self.selected = index
            try:
                self.app.scene.world.voxel_handler.new_voxel_id = self.inventory_ids[index]
            except Exception:
                pass

    def render(self):
        self.mesh.render(self.inventory_ids, self.selected)