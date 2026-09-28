import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from game_state import game, STATE_GAMEPLAY
from door_transition import transition_manager

quadric = None

def get_quadric():
    global quadric
    if quadric is None:
        quadric = gluNewQuadric()
    return quadric

class Player:
    def __init__(self):
        self.x = 0.0
        self.y = -150.0
        self.z = 0.0
        self.angle = 90.0  # Facing North (positive Y)
        self.speed = 4.0
        self.turn_speed = 3.5
        self.radius = 25
        
        # Animations
        self.walk_anim = 0.0
        self.is_moving = False
        
        # Combat states
        self.is_attacking = False
        self.attack_timer = 0
        self.sword_angle = 0.0
        self.is_blocking = False
        
        # Twin Helmet Laser Beams (2-second finite beam duration)
        self.laser_active = False
        self.laser_timer = 0
        self.laser_length = 120.0

    def update(self, room_bounds, room_doors, room_chests, room_plates, room_enemies=None):
        if game.state != STATE_GAMEPLAY:
            return
            
        # Attack animation update
        if self.is_attacking:
            self.attack_timer += 1
            if self.attack_timer <= 10:
                self.sword_angle = (self.attack_timer / 10.0) * 120.0  # Swing out
            elif self.attack_timer <= 20:
                self.sword_angle = (1.0 - (self.attack_timer - 10) / 10.0) * 120.0  # Return
            else:
                self.is_attacking = False
                self.attack_timer = 0
                self.sword_angle = 0.0

        # Twin Helmet Laser Beams update & continuous beam damage (2 seconds duration)
        if self.laser_active:
            self.laser_timer -= 1
            if room_enemies:
                rad = math.radians(self.angle)
                vx, vy = math.cos(rad), math.sin(rad)
                origin_x = self.x
                origin_y = self.y
                d_per_frame = (35.0 + game.willpower * 5.0) / 120.0  # Equal total damage over 2s
                for enemy in room_enemies:
                    if not enemy.is_alive:
                        continue
                    edx = enemy.x - origin_x
                    edy = enemy.y - origin_y
                    proj = edx * vx + edy * vy  # Distance along forward line of sight
                    perp = abs(edx * (-vy) + edy * vx)  # Perpendicular offset from laser beam
                    # Hit any enemy within beam length + radius and within beam width
                    if 0 < proj <= (self.laser_length + 25.0) and perp <= 45.0:
                        enemy.take_damage(d_per_frame)
            if self.laser_timer <= 0:
                self.laser_active = False

        # Check pressure plates stepping
        for plate in room_plates:
            px, py = plate["pos"]
            dx = self.x - px
            dy = self.y - py
            if math.sqrt(dx*dx + dy*dy) < 40:
                if not plate["pressed"]:
                    plate["pressed"] = True
                    game.trigger_hud_message("Stepped on Pressure Plate! Door unlocked!", 180)

    def move(self, direction, room_bounds):
        # Direction: 1 for Forward (W), -1 for Backward (S)
        if game.state != STATE_GAMEPLAY:
            return
            
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.speed * direction
        dy = math.sin(rad) * self.speed * direction
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check Wall Bounding Box Collisions
        x_min, x_max, y_min, y_max = room_bounds
        margin = 35
        if new_x - margin < x_min or new_x + margin > x_max:
            new_x = self.x
        if new_y - margin < y_min or new_y + margin > y_max:
            new_y = self.y

        self.x = new_x
        self.y = new_y
        self.is_moving = True
        self.walk_anim += 0.25

    def turn(self, direction):
        # Direction: 1 for Left (A), -1 for Right (D)
        if game.state != STATE_GAMEPLAY:
            return
        self.angle += self.turn_speed * direction

    def attack_melee(self, enemies):
        if self.is_attacking or game.stamina < 15:
            return
            
        game.stamina -= 15
        self.is_attacking = True
        self.attack_timer = 0
        
        # Check enemy hitboxes in front of player
        rad = math.radians(self.angle)
        hit_x = self.x + math.cos(rad) * 45
        hit_y = self.y + math.sin(rad) * 45
        
        damage = 25 + game.strength * 4
        for enemy in enemies:
            if enemy.is_alive:
                edx = enemy.x - hit_x
                edy = enemy.y - hit_y
                if math.sqrt(edx*edx + edy*edy) < 60:
                    enemy.take_damage(damage)
                    game.trigger_hud_message(f"Hit {enemy.name} for {damage} melee damage!", 90)

    def cast_laser(self):
        if game.sanity < 20:
            game.trigger_hud_message("Not enough Power to fire Visor Lasers!", 120)
            return
            
        game.sanity -= 20
        self.laser_active = True
        self.laser_timer = 120  # 2 seconds duration
        game.trigger_hud_message("Fired Twin Visor Laser Beams!", 120)

    cast_firebolt = cast_laser  # Alias for backward compatibility

    def interact(self, active_room, enemies):
        # 1. Interact with Doors
        for door in active_room.doors:
            dx, dy = door["pos"]
            dist = math.sqrt((self.x - dx)**2 + (self.y - dy)**2)
            if dist < 70:
                if door.get("is_claw_door", False):
                    if game.has_golden_claw:
                        door["is_locked"] = False
                        game.trigger_hud_message("Unlocked Vault Gate using Golden Keystone Claw!", 180)
                        transition_manager.start_transition(door, door["target_room"], player_ref=self)
                    else:
                        game.trigger_hud_message("Door requires Golden Keystone Claw!", 180)
                elif door.get("is_locked", False):
                    # Check pressure plates in room
                    unlocked = any(p["pressed"] for p in active_room.pressure_plates)
                    if unlocked:
                        door["is_locked"] = False
                        transition_manager.start_transition(door, door["target_room"], player_ref=self)
                    else:
                        game.trigger_hud_message("Door is locked! Step on Pressure Plate to open.", 180)
                else:
                    transition_manager.start_transition(door, door["target_room"], player_ref=self)
                return

        # 2. Interact with Chests
        for chest in active_room.chests:
            cx, cy = chest["pos"]
            dist = math.sqrt((self.x - cx)**2 + (self.y - cy)**2)
            if dist < 60 and not chest["opened"]:
                chest["opened"] = True
                if chest.get("has_claw", False):
                    game.has_golden_claw = True
                    game.trigger_hud_message("Opened Chest! Found Golden Keystone Claw!", 240)
                elif chest.get("has_relic", False):
                    game.has_elder_relic = True
                    game.state = 5  # Victory!
                    game.trigger_hud_message("RECOVERED THE ELDER SCROLL OF AETHERIUS!", 300)
                else:
                    game.potions += 2
                    game.trigger_hud_message("Opened Chest! Found 2 Magicka Potions!", 180)
                return

        # 3. Interact with Human Bandits (Charisma Speech Check)
        for enemy in enemies:
            if enemy.is_alive and enemy.is_human and not enemy.is_pacified:
                dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
                if dist < 80:
                    # Trigger D20 Charisma Speech Check vs DC 12
                    def pacify_callback(success):
                        if success:
                            enemy.is_pacified = True
                            game.trigger_hud_message(f"Charisma Check PASSED! {enemy.name} was pacified!", 240)
                        else:
                            game.trigger_hud_message(f"Charisma Check FAILED! {enemy.name} attacks!", 240)
                            
                    game.roll_d20(12, game.charisma, pacify_callback, "Charisma Persuasion Check")
                    return

    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angle - 90, 0, 0, 1)  # Orient towards facing angle
        
        swing = math.sin(self.walk_anim) * 20 if self.is_moving else 0
        
        # 1. Pelvis / Hip Waistband (Connecting Torso to Hip Joints at z=30)
        glPushMatrix()
        glTranslatef(0, 0, 31)
        glScalef(26, 17, 7)
        glColor3f(0.35, 0.32, 0.28)  # Solid Leather Belt / Pelvis
        glutSolidCube(1.0)
        glPopMatrix()

        # Legs (Pivoting at hip joints z=30 and extending DOWNWARDS to ground)
        for leg_offset in [-8, 8]:
            glPushMatrix()
            # Pivot at Hip Joint
            glTranslatef(leg_offset, 0, 30)
            glRotatef(swing if leg_offset > 0 else -swing, 1, 0, 0)
            
            # Leg Cylinder (Extending downwards from hip z=30 to floor z=0)
            glPushMatrix()
            glRotatef(180, 1, 0, 0)  # Orient downwards towards floor
            glColor3f(0.3, 0.28, 0.25)  # Leather pants
            gluCylinder(get_quadric(), 5.5, 4.5, 30, 8, 8)
            glPopMatrix()
            
            # Leather Boot (Pointing strictly FORWARD along +Y in facing direction)
            glPushMatrix()
            glTranslatef(0, 4, -28)  # +4 forward in +Y, -28 down to floor
            glScalef(10, 16, 6)
            glColor3f(0.2, 0.18, 0.15)  # Dark leather boot
            glutSolidCube(1.0)
            glPopMatrix()
            
            glPopMatrix()

        # 2. Torso (Solid Steel Chestplate sitting ON TOP of hips at z=30)
        glPushMatrix()
        glTranslatef(0, 0, 48)
        glScalef(28, 18, 36)
        glColor3f(0.5, 0.52, 0.55)  # Solid Metallic Steel Body
        glutSolidCube(1.0)
        glPopMatrix()

        # 3. Head & Helmet Visor (Sitting on top of torso at z=76)
        glPushMatrix()
        glTranslatef(0, 0, 76)
        glColor3f(0.6, 0.62, 0.65)
        gluSphere(get_quadric(), 14, 10, 10)  # Helmet Sphere
        
        # Dark Iron Visor (Mounted on front surface of helmet sphere at y=11.5)
        glPushMatrix()
        glTranslatef(0, 11.5, 2)
        glScalef(16, 5, 6)
        glColor3f(0.08, 0.08, 0.08)  # Jet Black Visor Cutout
        glutSolidCube(1.0)
        glPopMatrix()
        
        glPopMatrix()

        # 4. Right Arm holding Iron Sword (Vertical Up and Down Swing)
        glPushMatrix()
        glTranslatef(18, 0, 58)
        glRotatef(-swing, 1, 0, 0)
        
        # Vertical Up-and-Down Sword Swing Calculation
        vert_swing = 0.0
        if self.is_attacking:
            if self.attack_timer <= 10:
                vert_swing = -70.0 * (self.attack_timer / 10.0)  # Raise sword UP
            else:
                vert_swing = -70.0 + 150.0 * ((self.attack_timer - 10) / 10.0)  # Slash DOWN
        
        glRotatef(vert_swing, 1, 0, 0)  # Vertical pitch swing around X-axis
        
        # Upper Arm
        glColor3f(0.4, 0.38, 0.35)
        gluCylinder(get_quadric(), 5, 4, 18, 8, 8)
        
        # Sword Attachment
        glTranslatef(0, 5, 18)
        # Blade Cylinder
        glColor3f(0.85, 0.88, 0.9)
        gluCylinder(get_quadric(), 3, 1, 50, 6, 6)
        # Crossguard
        glScalef(14, 4, 3)
        glColor3f(0.7, 0.5, 0.2)
        glutSolidCube(1.0)
        glPopMatrix()

        # 5. Left Arm holding 3D Circular Shield (Round Buckler with Encircling Steel Rim)
        glPushMatrix()
        if self.is_blocking:
            # Move arm and circular shield directly in FRONT of chest held higher by 3 points (z=51)
            glTranslatef(0, 18, 51)
            glColor3f(0.4, 0.38, 0.35)
            gluCylinder(get_quadric(), 5, 4, 10, 8, 8)
            
            # Circular Shield Assembly in front of chest
            glTranslatef(0, 4, 0)
            
            # Layer 1: Steel Circular Outer Rim (Encircling perimeter, radius 24)
            glPushMatrix()
            glScalef(1.0, 0.18, 1.0)
            glColor3f(0.75, 0.78, 0.82)  # Metallic Steel Outer Rim
            gluSphere(get_quadric(), 24, 16, 16)
            glPopMatrix()
            
            # Layer 2: Dark Steel-Blue Inner Shield Face (Radius 20, slightly raised)
            glPushMatrix()
            glTranslatef(0, 1.5, 0)
            glScalef(1.0, 0.2, 1.0)
            glColor3f(0.22, 0.28, 0.42)  # Dark Steel-Blue Shield Face
            gluSphere(get_quadric(), 20, 16, 16)
            glPopMatrix()
            
            # Layer 3: Golden Center Shield Boss / Emblem (Radius 7)
            glPushMatrix()
            glTranslatef(0, 3.5, 0)
            glColor3f(0.85, 0.7, 0.2)  # Gold Center Boss
            gluSphere(get_quadric(), 7, 12, 12)
            glPopMatrix()

        else:
            # Idle at left arm side (hanging low downwards from shoulder towards hip)
            glTranslatef(-18, 0, 52)
            glRotatef(swing, 1, 0, 0)
            
            # Left Arm Cylinder hanging DOWNWARDS towards waist (z=52 down to z=34)
            glPushMatrix()
            glRotatef(180, 1, 0, 0)  # Flip downwards
            glColor3f(0.4, 0.38, 0.35)
            gluCylinder(get_quadric(), 5, 4, 18, 8, 8)
            glPopMatrix()
            
            # Mount circular shield low on the outer left hip/flank (z = -12 below shoulder)
            glPushMatrix()
            glTranslatef(-5, 0, -12)  # Low at hip height, outside the body
            
            # Layer 1: Steel Circular Outer Rim (Radius 20, facing outwards to the left)
            glPushMatrix()
            glScalef(0.18, 1.0, 1.0)
            glColor3f(0.75, 0.78, 0.82)
            gluSphere(get_quadric(), 20, 16, 16)
            glPopMatrix()
            
            # Layer 2: Dark Blue Inner Face (Radius 16, slightly offset outward to -X)
            glPushMatrix()
            glTranslatef(-1.5, 0, 0)
            glScalef(0.2, 1.0, 1.0)
            glColor3f(0.22, 0.28, 0.42)
            gluSphere(get_quadric(), 16, 16, 16)
            glPopMatrix()
            
            # Layer 3: Golden Center Boss (Radius 6, protruding outward to -X)
            glPushMatrix()
            glTranslatef(-3.5, 0, 0)
            glColor3f(0.85, 0.7, 0.2)
            gluSphere(get_quadric(), 6, 12, 12)
            glPopMatrix()
            
            glPopMatrix()

        glPopMatrix()  # Close Left Arm glPushMatrix

        # Render Twin Helmet Laser Beams (Shooting straight out from visor cutout)
        if self.laser_active:
            for eye_x in [-4.0, 4.0]:
                glPushMatrix()
                # Origin at visor cutout of helmet (x=eye_x, y=8, z=78)
                glTranslatef(eye_x, 8, 78)
                glRotatef(-90, 1, 0, 0)  # Orient along local +Y (forward facing direction)
                
                # Outer Glowing Crimson Laser Cylinder Beam
                glColor3f(1.0, 0.1, 0.25)
                gluCylinder(get_quadric(), 1.8, 1.8, self.laser_length, 8, 8)
                
                # Inner Intense White Core Beam
                glColor3f(1.0, 0.95, 0.95)
                gluCylinder(get_quadric(), 0.8, 0.8, self.laser_length, 6, 6)
                
                # Laser Origin Spark & End Impact Glow
                glColor3f(1.0, 0.8, 0.2)
                gluSphere(get_quadric(), 2.5, 8, 8)
                glTranslatef(0, 0, self.laser_length)
                glColor3f(1.0, 0.2, 0.1)
                gluSphere(get_quadric(), 4.0, 8, 8)
                glPopMatrix()

        glPopMatrix()

player = Player()
