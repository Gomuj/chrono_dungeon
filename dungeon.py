import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

quadric = None

def get_quadric():
    global quadric
    if quadric is None:
        quadric = gluNewQuadric()
    return quadric

def get_light_intensity(px, py, pz, torch_x, torch_y, torch_z):
    dx = px - torch_x
    dy = py - torch_y
    dz = pz - torch_z
    dist_sq = dx*dx + dy*dy + dz*dz
    intensity = 1.0 / (1.0 + 0.000008 * dist_sq)
    return max(0.2, min(1.0, intensity))

def draw_lit_quad(x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, base_r, base_g, base_b, torch_pos):
    # Calculates average torch lighting for quad
    cx = (x1 + x2 + x3 + x4) / 4.0
    cy = (y1 + y2 + y3 + y4) / 4.0
    cz = (z1 + z2 + z3 + z4) / 4.0
    intensity = get_light_intensity(cx, cy, cz, torch_pos[0], torch_pos[1], torch_pos[2])
    
    glColor3f(base_r * intensity, base_g * intensity, base_b * intensity)
    glBegin(GL_QUADS)
    glVertex3f(x1, y1, z1)
    glVertex3f(x2, y2, z2)
    glVertex3f(x3, y3, z3)
    glVertex3f(x4, y4, z4)
    glEnd()

CORNER_POSITIONS = [
    (-260, -260, 220),  # South-West Corner
    (260, -260, 220),   # South-East Corner
    (-260, 260, 220),   # North-West Corner
    (260, 260, 220)     # North-East Corner
]

class Room:
    def __init__(self, room_id, name, floor_type, bounds, camera_pos=None, camera_lookat=(0, 0, 0)):
        self.room_id = room_id
        self.name = name
        self.floor_type = floor_type  # 1: Sewer, 2: Crypt
        self.bounds = bounds  # (x_min, x_max, y_min, y_max)
        
        # Pick a random corner for this room's fixed camera
        if camera_pos is None:
            self.camera_pos = random.choice(CORNER_POSITIONS)
        else:
            self.camera_pos = camera_pos
        self.camera_lookat = camera_lookat
        
        # Interactive Objects
        self.doors = []  # dicts of door info: position, target_room, is_locked, angle, etc.
        self.chests = []  # dicts: pos, opened, has_claw, has_relic
        self.pressure_plates = []  # dicts: pos, pressed
        self.torches = [( -250, 0, 80), (250, 0, 80)]  # Torch positions
        
        # Door locks
        self.is_door_locked = False
        self.requires_golden_claw = False

    def render_room(self, anim_time=0):
        x_min, x_max, y_min, y_max = self.bounds
        torch_pos = self.torches[0] if self.torches else (0, 0, 100)
        
        # 1. Draw Floor Tiles (Procedural Geometric Tiling)
        tile_size = 60
        for x in range(int(x_min), int(x_max), tile_size):
            for y in range(int(y_min), int(y_max), tile_size):
                # Checker pattern color choice
                is_even = ((x // tile_size) + (y // tile_size)) % 2 == 0
                if self.floor_type == 1: # Sewer: mossy dark grey / green
                    r, g, b = (0.18, 0.22, 0.18) if is_even else (0.12, 0.16, 0.14)
                else: # Crypt: slate grey / dark purple tint
                    r, g, b = (0.22, 0.20, 0.25) if is_even else (0.15, 0.14, 0.18)
                    
                draw_lit_quad(
                    x, y, 0,
                    x + tile_size, y, 0,
                    x + tile_size, y + tile_size, 0,
                    x, y + tile_size, 0,
                    r, g, b, torch_pos
                )

        # 2. Draw Walls with Procedural Brick Reliefs
        wall_height = 150
        # North Wall
        draw_lit_quad(x_min, y_max, 0, x_max, y_max, 0, x_max, y_max, wall_height, x_min, y_max, wall_height, 0.25, 0.25, 0.28, torch_pos)
        # South Wall
        draw_lit_quad(x_min, y_min, 0, x_max, y_min, 0, x_max, y_min, wall_height, x_min, y_min, wall_height, 0.25, 0.25, 0.28, torch_pos)
        # West Wall
        draw_lit_quad(x_min, y_min, 0, x_min, y_max, 0, x_min, y_max, wall_height, x_min, y_min, wall_height, 0.22, 0.22, 0.25, torch_pos)
        # East Wall
        draw_lit_quad(x_max, y_min, 0, x_max, y_max, 0, x_max, y_max, wall_height, x_max, y_min, wall_height, 0.22, 0.22, 0.25, torch_pos)
        
        # Embossed Brick Relief Cubes along North Wall
        for bx in range(int(x_min) + 30, int(x_max) - 30, 80):
            glPushMatrix()
            glTranslatef(bx, y_max - 5, 40)
            glScalef(35, 8, 20)
            glColor3f(0.35, 0.35, 0.38)
            glutSolidCube(1.0)
            glPopMatrix()
            
            glPushMatrix()
            glTranslatef(bx + 40, y_max - 5, 90)
            glScalef(35, 8, 20)
            glColor3f(0.32, 0.32, 0.35)
            glutSolidCube(1.0)
            glPopMatrix()

        # 3. Corner Pillars (gluCylinder)
        for px, py in [(x_min, y_min), (x_max, y_min), (x_min, y_max), (x_max, y_max)]:
            glPushMatrix()
            glTranslatef(px, py, 0)
            glColor3f(0.30, 0.28, 0.32)
            gluCylinder(get_quadric(), 25, 25, wall_height, 12, 12)
            glPopMatrix()

        # 4. Draw Wall Torches
        for tx, ty, tz in self.torches:
            glPushMatrix()
            glTranslatef(tx, ty, tz)
            # Torch Sconce / Mount
            glColor3f(0.4, 0.25, 0.1)
            gluCylinder(get_quadric(), 4, 2, 25, 8, 8)
            # Flame particle sphere
            glTranslatef(0, 0, 25)
            # Flame flicker using sine wave
            flicker = 0.1 * math.sin(anim_time * 0.1 + tx)
            glColor3f(1.0, 0.5 + flicker, 0.1)
            gluSphere(get_quadric(), 10 + flicker * 5, 10, 10)
            glPopMatrix()

        # 5. Render Interactive Pressure Plates
        for plate in self.pressure_plates:
            px, py = plate["pos"]
            glPushMatrix()
            glTranslatef(px, py, 2 if plate["pressed"] else 6)
            glScalef(50, 50, 4)
            if plate["pressed"]:
                glColor3f(0.2, 0.8, 0.2)  # Glowing Green when active
            else:
                glColor3f(0.6, 0.6, 0.6)  # Stone slab
            glutSolidCube(1.0)
            glPopMatrix()

        # 6. Render Interactive Loot Chests
        # 6. Render Room Chests (Base box + Flush Hinged Lid)
        for chest in self.chests:
            cx, cy = chest["pos"]
            
            # Base Wood Box (Height z=0 to z=25)
            glPushMatrix()
            glTranslatef(cx, cy, 12.5)
            glScalef(40, 26, 25)
            glColor3f(0.38, 0.22, 0.1)
            glutSolidCube(1.0)
            glPopMatrix()
            
            # Iron Trim Bands around Base
            glPushMatrix()
            glTranslatef(cx, cy, 12.5)
            glScalef(41, 27, 6)
            glColor3f(0.2, 0.2, 0.22)
            glutSolidCube(1.0)
            glPopMatrix()
            
            # Golden Front Keyhole / Lock Face
            glPushMatrix()
            glTranslatef(cx, cy - 13.5, 16)
            glScalef(8, 2, 8)
            glColor3f(0.85, 0.7, 0.2)
            glutSolidCube(1.0)
            glPopMatrix()
            
            # Chest Lid (Pivoting accurately at back top hinge cy+13, z=25)
            glPushMatrix()
            glTranslatef(cx, cy + 13, 25)
            if chest["opened"]:
                glRotatef(-65, 1, 0, 0)  # Open lid backwards around hinge
            # Center lid flush over base box
            glTranslatef(0, -13, 4)
            
            # Wooden Lid Slab (Flushed over entire chest top)
            glPushMatrix()
            glScalef(42, 28, 8)
            glColor3f(0.48, 0.28, 0.12)
            glutSolidCube(1.0)
            glPopMatrix()
            
            # Iron Reinforcement Trim on Lid
            glPushMatrix()
            glScalef(43, 29, 3)
            glColor3f(0.25, 0.25, 0.28)
            glutSolidCube(1.0)
            glPopMatrix()
            
            # Gold Clasp Lip on Front of Lid
            glPushMatrix()
            glTranslatef(0, -14, -2)
            glScalef(6, 2, 6)
            glColor3f(0.85, 0.7, 0.2)
            glutSolidCube(1.0)
            glPopMatrix()
            
            glPopMatrix()

        # 7. Render Room Doors
        for door in self.doors:
            dx, dy = door["pos"]
            is_open = door.get("open", False)
            open_angle = door.get("anim_angle", 90 if is_open else 0)
            
            glPushMatrix()
            glTranslatef(dx, dy, 0)
            
            # Door Archway Frame (Open Portal: Left Post, Right Post, Top Lintel)
            # Left Stone Post
            glPushMatrix()
            glTranslatef(-38, 0, 50)
            glScalef(10, 18, 100)
            glColor3f(0.25, 0.25, 0.28)  # Stone Frame Post
            glutSolidCube(1.0)
            glPopMatrix()

            # Right Stone Post
            glPushMatrix()
            glTranslatef(38, 0, 50)
            glScalef(10, 18, 100)
            glColor3f(0.25, 0.25, 0.28)  # Stone Frame Post
            glutSolidCube(1.0)
            glPopMatrix()

            # Top Arch Lintel
            glPushMatrix()
            glTranslatef(0, 0, 96)
            glScalef(86, 20, 12)
            glColor3f(0.28, 0.28, 0.32)  # Stone Arch Header
            glutSolidCube(1.0)
            glPopMatrix()
            
            # Rotating Wooden Door Wing (Inside open portal)
            glPushMatrix()
            # Pivot at left edge of doorway
            glTranslatef(-33, 0, 46)
            glRotatef(open_angle, 0, 0, 1)  # Rotate open around Z axis
            glTranslatef(33, 0, 0)
            
            # Main Door Wooden Slab
            glPushMatrix()
            glScalef(66, 8, 88)
            if door.get("is_claw_door", False):
                glColor3f(0.9, 0.72, 0.15)  # Vibrant Golden Keystone Claw Door
            elif door.get("is_locked", False):
                glColor3f(0.75, 0.18, 0.15)  # Vibrant Locked Crimson Door
            else:
                glColor3f(0.55, 0.32, 0.14)  # Warm Wooden Dungeon Door
            glutSolidCube(1.0)
            glPopMatrix()
            
            # Iron Stud Reinforcement Bands on Door Wing
            for band_z in [-25, 25]:
                glPushMatrix()
                glTranslatef(0, 0, band_z)
                glScalef(67, 9, 6)
                glColor3f(0.2, 0.2, 0.22)  # Iron Strap
                glutSolidCube(1.0)
                glPopMatrix()

            # Golden/Bronze Door Handle / Keyhole
            glPushMatrix()
            glTranslatef(22, -5, 0)
            glScalef(4, 4, 10)
            glColor3f(0.95, 0.8, 0.2)  # Gold Keyhole / Handle
            glutSolidCube(1.0)
            glPopMatrix()

            glPopMatrix()
            
            glPopMatrix()


class DungeonBuilder:
    @staticmethod
    def build_floor_1():
        # Floor 1: Sewer Complex (4 Rooms)
        rooms = {}
        
        # Room 1: Sewer Entrance (SW Corner)
        r1 = Room(1, "Sewer Entryway", 1, (-300, 300, -300, 300), (-260, -260, 220), (0, 0, 0))
        r1.pressure_plates.append({"pos": (0, -100), "pressed": False, "target_door": 0})
        r1.chests.append({"pos": (-180, 180), "opened": False, "has_claw": True, "has_relic": False})
        r1.doors.append({"pos": (0, 290), "target_room": 2, "is_locked": True, "open": False, "anim_angle": 0})
        rooms[1] = r1

        # Room 2: Bandit Guard Post (NW Corner)
        r2 = Room(2, "Bandit Guard Post", 1, (-300, 300, -300, 300), (-260, 260, 220), (0, 0, 0))
        r2.doors.append({"pos": (0, 290), "target_room": 3, "is_locked": False, "open": False, "anim_angle": 0})
        rooms[2] = r2

        # Room 3: Aqueduct of Blades (SE Corner)
        r3 = Room(3, "Aqueduct of Blades", 1, (-300, 300, -300, 300), (260, -260, 220), (0, 0, 0))
        r3.doors.append({"pos": (0, 290), "target_room": 4, "is_locked": False, "open": False, "anim_angle": 0})
        rooms[3] = r3

        # Room 4: Sewer Gate Vault (NE Corner)
        r4 = Room(4, "Sewer Gate Vault", 1, (-300, 300, -300, 300), (260, 260, 220), (0, 0, 0))
        r4.doors.append({"pos": (0, 290), "target_room": "FLOOR_2", "is_locked": True, "is_claw_door": True, "open": False, "anim_angle": 0})
        rooms[4] = r4
        
        return rooms

    @staticmethod
    def build_floor_2():
        # Floor 2: Crypt Catacombs (4 Rooms)
        rooms = {}
        
        # Room 1: Catacomb Entry (SE Corner)
        r1 = Room(1, "Catacomb Entry", 2, (-300, 300, -300, 300), (260, -260, 220), (0, 0, 0))
        r1.doors.append({"pos": (0, 290), "target_room": 2, "is_locked": False, "open": False, "anim_angle": 0})
        rooms[1] = r1

        # Room 2: Tomb of the Forgotten (NE Corner)
        r2 = Room(2, "Tomb of the Forgotten", 2, (-300, 300, -300, 300), (260, 260, 220), (0, 0, 0))
        r2.chests.append({"pos": (180, -180), "opened": False, "has_claw": False, "has_relic": False})
        r2.doors.append({"pos": (0, 290), "target_room": 3, "is_locked": False, "open": False, "anim_angle": 0})
        rooms[2] = r2

        # Room 3: Sanctuary of Shadows (SW Corner)
        r3 = Room(3, "Sanctuary of Shadows", 2, (-300, 300, -300, 300), (-260, -260, 220), (0, 0, 0))
        r3.pressure_plates.append({"pos": (0, 0), "pressed": False, "target_door": 0})
        r3.doors.append({"pos": (0, 290), "target_room": 4, "is_locked": True, "open": False, "anim_angle": 0})
        rooms[3] = r3

        # Room 4: Crypt Archway Vault (NW Corner)
        r4 = Room(4, "Crypt Archway Vault", 2, (-300, 300, -300, 300), (-260, 260, 220), (0, 0, 0))
        r4.chests.append({"pos": (0, 150), "opened": False, "has_claw": False, "has_relic": True})
        rooms[4] = r4

        return rooms
