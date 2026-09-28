import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from game_state import game

quadric = None

def get_quadric():
    global quadric
    if quadric is None:
        quadric = gluNewQuadric()
    return quadric

class SwingingBlade:
    def __init__(self, room_id, x, y, height=150):
        self.room_id = room_id
        self.x = x
        self.y = y
        self.height = height  # Ceiling height at z = 150
        self.swing_angle = 0.0
        self.speed = 0.05
        self.time = 0.0

    def update(self, player_ref):
        self.time += self.speed
        self.swing_angle = math.sin(self.time) * 55.0  # Swing between -55 and +55 deg
        
        # Check collision with player when blade is low
        if abs(self.swing_angle) < 15 and game.current_room_id == self.room_id and game.state == 2:
            dx = player_ref.x - self.x
            dy = player_ref.y - self.y
            if math.sqrt(dx*dx + dy*dy) < 45:
                if not game.god_mode:
                    game.health -= 0.5  # Periodic blade slice damage
                    game.trigger_hud_message("Sliced by Swinging Blade!", 60)
                    if game.health <= 0:
                        game.handle_player_death()

    def render(self):
        glPushMatrix()
        # Position at room ceiling height (z = 150)
        glTranslatef(self.x, self.y, self.height)
        
        # 1. Ceiling Mounting Bracket & Hinge Plate
        glPushMatrix()
        glScalef(40, 40, 8)
        glColor3f(0.2, 0.2, 0.22)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Hinge Beam Cylinder (Oriented along Y axis for sideways swing)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, 0, -25)
        glColor3f(0.3, 0.3, 0.35)
        gluCylinder(get_quadric(), 6, 6, 50, 8, 8)
        glPopMatrix()

        # 2. Flip Z axis so arm extends DOWNWARDS from ceiling towards floor
        glRotatef(180, 1, 0, 0)
        
        # Oscillating Pendulum Arm swinging SIDEWAYS around Y axis
        glRotatef(self.swing_angle, 0, 1, 0)
        
        # Long Steel Shaft hanging DOWN towards floor (height 110)
        glColor3f(0.4, 0.42, 0.45)
        gluCylinder(get_quadric(), 4, 3, 110, 8, 8)
        
        # 3. Double-Sided Heavy Razor Blade at Bottom (Oriented sideways)
        glTranslatef(0, 0, 110)
        glScalef(65, 6, 25)
        glColor3f(0.85, 0.88, 0.92)  # Sharp Steel Blade
        glutSolidCube(1.0)
        glPopMatrix()


class SpikeTrap:
    def __init__(self, room_id, x, y):
        self.room_id = room_id
        self.x = x
        self.y = y
        self.spike_height = 0.0
        self.is_active = False
        self.timer = 0

    def update(self, player_ref):
        self.timer += 1
        # Emerge every 120 frames for 40 frames
        cycle = self.timer % 140
        if cycle < 40:
            self.is_active = True
            self.spike_height = min(25.0, self.spike_height + 3.0)
        else:
            self.is_active = False
            self.spike_height = max(0.0, self.spike_height - 2.0)
            
        if self.is_active and game.current_room_id == self.room_id and game.state == 2:
            dx = player_ref.x - self.x
            dy = player_ref.y - self.y
            if math.sqrt(dx*dx + dy*dy) < 30:
                if not game.god_mode:
                    game.health -= 0.4
                    game.trigger_hud_message("Impaled by Floor Spike Trap!", 60)
                    if game.health <= 0:
                        game.handle_player_death()

    def render(self):
        # Floor Plate
        glPushMatrix()
        glTranslatef(self.x, self.y, 1.5)
        glScalef(45, 45, 3)
        glColor3f(0.15, 0.15, 0.15)
        glutSolidCube(1.0)
        glPopMatrix()

        # Thrusting Spikes
        if self.spike_height > 1.0:
            for sx in [-12, 12]:
                for sy in [-12, 12]:
                    glPushMatrix()
                    glTranslatef(self.x + sx, self.y + sy, 2)
                    glColor3f(0.7, 0.72, 0.75)
                    gluCylinder(get_quadric(), 3, 0.5, self.spike_height, 6, 6)
                    glPopMatrix()


class FireTrap:
    def __init__(self, room_id, x, y, height=60):
        self.room_id = room_id
        self.x = x
        self.y = y
        self.height = height
        self.flame_progress = 0.0
        self.is_active = False
        self.time = 0.0

    def update(self, player_ref):
        self.time += 0.03
        self.is_active = (math.sin(self.time) > 0.3)
        
        if self.is_active and game.current_room_id == self.room_id and game.state == 2:
            self.flame_progress = (self.flame_progress + 8.0) % 180.0
            flame_x = self.x + self.flame_progress
            flame_y = self.y
            
            dx = player_ref.x - flame_x
            dy = player_ref.y - flame_y
            if math.sqrt(dx*dx + dy*dy) < 35:
                if not game.god_mode:
                    game.health -= 0.6
                    game.trigger_hud_message("Burned by Fire Trap flame!", 60)
                    if game.health <= 0:
                        game.handle_player_death()

    def render(self):
        # Wall Carving Mount
        glPushMatrix()
        glTranslatef(self.x, self.y, self.height)
        glColor3f(0.3, 0.28, 0.25)
        gluSphere(get_quadric(), 15, 8, 8)
        glPopMatrix()

        # Flame Particles
        if self.is_active:
            for dist in range(20, 160, 30):
                glPushMatrix()
                glTranslatef(self.x + dist, self.y, self.height - 10)
                glColor3f(1.0, 0.4, 0.0)
                gluSphere(get_quadric(), 10, 8, 8)
                glColor3f(1.0, 0.9, 0.1)
                gluSphere(get_quadric(), 5, 6, 6)
                glPopMatrix()


class HazardManager:
    @staticmethod
    def get_floor_hazards(floor_id):
        hazards = []
        if floor_id == 1:
            # Floor 1 Hazards
            # Room 3: 1 Swinging Blade in front of Exit Door (0, 220)
            hazards.append(SwingingBlade(3, 0, 220))
            hazards.append(SpikeTrap(3, -80, 100))
            hazards.append(SpikeTrap(3, 80, 100))
        else:
            # Floor 2 Hazards (At most ONE swinging blade per room)
            # Room 1: 1 Fire Trap & 1 Swinging Blade in front of Door (0, 220)
            hazards.append(FireTrap(1, -280, 0))
            hazards.append(SwingingBlade(1, 0, 220))
            
            # Room 2: 1 Swinging Blade in front of Chest (180, -120)
            hazards.append(SwingingBlade(2, 180, -120))
            hazards.append(SpikeTrap(2, -100, -100))
            
            # Room 3: 1 Swinging Blade in front of Vault Door (0, 220)
            hazards.append(SwingingBlade(3, 0, 220))
        return hazards
