import math
import random
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

class Enemy:
    def __init__(self, room_id, name, enemy_type, x, y, hp, attack_power):
        self.room_id = room_id
        self.name = name
        self.enemy_type = enemy_type  # "BANDIT", "DRAUGR", "BOSS"
        self.x = x
        self.y = y
        self.z = 0.0
        self.angle = 0.0
        self.hp = hp
        self.max_hp = hp
        self.attack_power = attack_power
        self.is_alive = True
        self.is_pacified = False
        self.is_human = (enemy_type == "BANDIT")
        self.dialogue_triggered = False
        self.is_hostile = not self.is_human  # Non-human enemies start hostile
        self.corpse_cannibalized = False
        
        # Animations & Attack Cooldown
        self.walk_anim = 0.0
        self.attack_cooldown = 0
        self.swing_anim = 0.0

    def take_damage(self, amount):
        if not self.is_alive:
            return
        self.hp -= amount
        # Taking damage immediately makes bandit hostile
        if self.is_human:
            self.is_hostile = True
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            game.trigger_hud_message(f"Defeated {self.name}!", 180)

    def update(self, player_ref):
        if not self.is_alive or self.is_pacified or game.state != 2:
            return
            
        dx = player_ref.x - self.x
        dy = player_ref.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Human Bandit Dialogue Initiation (Only ONE bandit per room initiates dialogue)
        if self.is_human and not self.is_pacified and not self.is_hostile:
            if dist < 180:
                self.angle = math.degrees(math.atan2(dy, dx))
                if not self.dialogue_triggered and not game.dialogue_active:
                    # Check if another bandit in this room has already triggered dialogue
                    self.dialogue_triggered = True
                    dialogue_lines = {
                        "Human Bandit Scout": "Halt, traveler! State your business in these dark sewers or draw your steel!",
                        "Human Bandit Leader": "Hold it right there! This is Bandit territory. Pay your toll or turn back!"
                    }
                    text = dialogue_lines.get(self.name, "Halt! State your business!")
                    game.start_dialogue(self.name, text, self)
            return

        # Chase player if within detection distance
        if dist < 220 and dist > 35:
            target_angle = math.degrees(math.atan2(dy, dx))
            self.angle = target_angle
            
            speed = 1.8 if self.enemy_type == "DRAUGR" else (2.4 if self.enemy_type == "BANDIT" else 1.2)
            rad = math.radians(self.angle)
            self.x += math.cos(rad) * speed
            self.y += math.sin(rad) * speed
            self.walk_anim += 0.2

        # Melee Attack on Player
        elif dist <= 35 and self.attack_cooldown <= 0:
            self.attack_cooldown = 60  # Attack once every frame window
            damage = self.attack_power
            
            # Check if player is blocking
            if player_ref.is_blocking and game.stamina >= 10:
                game.stamina -= 10
                damage = damage * 0.2  # 80% damage reduction
                game.trigger_hud_message(f"Blocked attack from {self.name}! Took {damage:.1f} damage", 90)
            else:
                game.trigger_hud_message(f"{self.name} hit you for {damage:.1f} damage!", 90)

            if not game.god_mode:
                game.health -= damage
                if game.health <= 0:
                    game.handle_player_death()



    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angle - 90, 0, 0, 1)
        
        if not self.is_alive:
            # Defeated Corpse: Rotate 90 degrees to lie on their SIDE on the ground
            glRotatef(90, 0, 1, 0)  # Rotate sideways onto side flank
            glTranslatef(-35, 0, 8)  # Rest flush on the floor
            swing = 0.0
            enemy_vert_swing = 0.0
        else:
            swing = math.sin(self.walk_anim) * 15
            
            # Calculate Vertical Up-and-Down Sword Swing Animation for Enemy Attack
            enemy_vert_swing = 0.0
            if self.attack_cooldown > 30:
                progress = (60 - self.attack_cooldown) / 30.0
                if progress <= 0.5:
                    enemy_vert_swing = -70.0 * (progress / 0.5)  # Raise sword UP
                else:
                    enemy_vert_swing = -70.0 + 150.0 * ((progress - 0.5) / 0.5)  # Slash DOWN
        
        if self.enemy_type == "BANDIT":
            # Pelvis Belt
            glPushMatrix()
            glTranslatef(0, 0, 29)
            glScalef(26, 17, 6)
            glColor3f(0.25, 0.18, 0.12)
            glutSolidCube(1.0)
            glPopMatrix()

            # Human Bandit Legs (Pivoting at hip joints z=28 and extending downwards)
            for leg in [-8, 8]:
                glPushMatrix()
                glTranslatef(leg, 0, 28)
                glRotatef(swing if leg > 0 else -swing, 1, 0, 0)
                
                # Leg Cylinder
                glPushMatrix()
                glRotatef(180, 1, 0, 0)
                glColor3f(0.2, 0.15, 0.1)
                gluCylinder(get_quadric(), 5, 4, 28, 8, 8)
                glPopMatrix()
                
                # Bandit Leather Boot (Pointing strictly FORWARD along +Y)
                glPushMatrix()
                glTranslatef(0, 4, -26)
                glScalef(9, 14, 5)
                glColor3f(0.15, 0.12, 0.08)
                glutSolidCube(1.0)
                glPopMatrix()
                
                glPopMatrix()

            # Torso (Solid thick Leather tunic sitting on top of hips)
            glPushMatrix()
            glTranslatef(0, 0, 46)
            glScalef(28, 18, 34)
            glColor3f(0.4, 0.25, 0.15)  # Solid Opaque Leather Tunic
            glutSolidCube(1.0)
            glPopMatrix()

            # Head (Cloth Hood)
            glPushMatrix()
            glTranslatef(0, 0, 70)
            glColor3f(0.3, 0.2, 0.1)
            gluSphere(get_quadric(), 12, 10, 10)
            glPopMatrix()

            # Right Arm holding Bandit Iron Sword
            glPushMatrix()
            glTranslatef(17, 0, 50)
            glRotatef(-swing, 1, 0, 0)
            glRotatef(enemy_vert_swing, 1, 0, 0)  # Vertical pitch swing!
            glColor3f(0.35, 0.25, 0.15)
            gluCylinder(get_quadric(), 4, 3, 16, 8, 8)
            
            # Weapon Attachment (Despawns upon death)
            if self.is_alive:
                glTranslatef(0, 4, 16)
                glColor3f(0.8, 0.82, 0.85)  # Bandit Blade
                gluCylinder(get_quadric(), 3, 1, 42, 6, 6)
                glScalef(12, 3, 3)
                glColor3f(0.5, 0.35, 0.15)
                glutSolidCube(1.0)
            glPopMatrix()

        elif self.enemy_type in ["DRAUGR", "BOSS"]:
            scale_fac = 1.4 if self.enemy_type == "BOSS" else 1.0
            glScalef(scale_fac, scale_fac, scale_fac)
            
            # Skeletal Pelvis
            glPushMatrix()
            glTranslatef(0, 0, 29)
            glScalef(24, 15, 6)
            glColor3f(0.6, 0.62, 0.6)
            glutSolidCube(1.0)
            glPopMatrix()

            # Skeletal Legs (Pivoting at hip joints z=28 and extending downwards)
            for leg in [-8, 8]:
                glPushMatrix()
                glTranslatef(leg, 0, 28)
                glRotatef(swing if leg > 0 else -swing, 1, 0, 0)
                
                # Bone Leg Cylinder
                glPushMatrix()
                glRotatef(180, 1, 0, 0)
                glColor3f(0.65, 0.65, 0.6)
                gluCylinder(get_quadric(), 4, 3, 28, 6, 6)
                glPopMatrix()
                
                # Bone Foot (Pointing forward along +Y)
                glPushMatrix()
                glTranslatef(0, 4, -26)
                glScalef(8, 14, 4)
                glColor3f(0.6, 0.6, 0.58)
                glutSolidCube(1.0)
                glPopMatrix()
                
                glPopMatrix()

            # Bone Torso (Solid thick Ancient bone ribcage)
            glPushMatrix()
            glTranslatef(0, 0, 46)
            glScalef(26, 16, 36)
            glColor3f(0.7, 0.72, 0.7)  # Solid Ancient bone
            glutSolidCube(1.0)
            glPopMatrix()

            # Skeletal Skull with Glowing Cyan/Magenta Eyes
            glPushMatrix()
            glTranslatef(0, 0, 72)
            glColor3f(0.8, 0.8, 0.75)
            gluSphere(get_quadric(), 12, 10, 10)
            
            # Glowing Eyes
            eye_color = (1.0, 0.0, 0.8) if self.enemy_type == "BOSS" else (0.0, 0.9, 1.0)
            glColor3f(*eye_color)
            for ex in [-4, 4]:
                glPushMatrix()
                glTranslatef(ex, 8, 2)
                gluSphere(get_quadric(), 3, 6, 6)
                glPopMatrix()
                
            # Ancient Curved Horns for Draugr Lord Boss
            if self.enemy_type == "BOSS":
                for hx, hang in [(-9, -35), (9, 35)]:
                    glPushMatrix()
                    glTranslatef(hx, 2, 8)
                    glRotatef(hang, 0, 1, 0)
                    glRotatef(-20, 1, 0, 0)
                    glColor3f(0.3, 0.3, 0.35)
                    gluCylinder(get_quadric(), 3, 0.8, 14, 6, 6)
                    glPopMatrix()
            
            glPopMatrix()

            # Right Arm holding Ancient Greatsword / Boss Blade
            glPushMatrix()
            glTranslatef(17, 0, 52)
            glRotatef(-swing, 1, 0, 0)
            glRotatef(enemy_vert_swing, 1, 0, 0)  # Vertical pitch swing!
            glColor3f(0.5, 0.52, 0.5)
            gluCylinder(get_quadric(), 4, 3, 18, 6, 6)
            
            # Greatsword Attachment (Despawns upon death)
            if self.is_alive:
                glTranslatef(0, 4, 18)
                glColor3f(0.55, 0.65, 0.68) if self.enemy_type == "DRAUGR" else glColor3f(0.8, 0.2, 0.8)
                gluCylinder(get_quadric(), 4, 1, 55, 6, 6)
                glScalef(14, 4, 3)
                glColor3f(0.3, 0.3, 0.35)
                glutSolidCube(1.0)
            glPopMatrix()

        glPopMatrix()


class EnemySpawner:
    @staticmethod
    def get_floor_enemies(floor_id):
        enemies = []
        if floor_id == 1:
            # Floor 1 Enemies
            enemies.append(Enemy(2, "Human Bandit Scout", "BANDIT", -80, 50, 60, 12))
            enemies.append(Enemy(2, "Human Bandit Leader", "BANDIT", 80, 120, 90, 16))
            enemies.append(Enemy(3, "Sewer Skeletal Guard", "DRAUGR", 0, 80, 100, 18))
        else:
            # Floor 2 Enemies
            enemies.append(Enemy(1, "Crypt Draugr Warrior", "DRAUGR", -100, 0, 110, 20))
            enemies.append(Enemy(1, "Crypt Draugr Archer", "DRAUGR", 100, 50, 90, 16))
            enemies.append(Enemy(2, "Ancient Draugr Guard", "DRAUGR", 0, 100, 130, 22))
            enemies.append(Enemy(3, "Undead Draugr Lord", "BOSS", 0, 120, 260, 32))
        return enemies
