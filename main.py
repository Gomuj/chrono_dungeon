import os
import math
import sys
import time

# Ensure PyOpenGL uses GLX instead of EGL for GLUT context binding on Linux
os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from game_state import (
    game, STATE_CHAR_CREATE, STATE_STORY_INTRO, STATE_GAMEPLAY,
    STATE_DOOR_TRANSITION, STATE_GAME_OVER, STATE_VICTORY
)
from dungeon import DungeonBuilder
from door_transition import transition_manager
from player import player
from enemies import EnemySpawner
from hazards import HazardManager
from ui_renderer import UIRenderer

# Global Dungeon & Entities Data
floors = {
    1: DungeonBuilder.build_floor_1(),
    2: DungeonBuilder.build_floor_2()
}

enemies_by_floor = {
    1: EnemySpawner.get_floor_enemies(1),
    2: EnemySpawner.get_floor_enemies(2)
}

hazards_by_floor = {
    1: HazardManager.get_floor_hazards(1),
    2: HazardManager.get_floor_hazards(2)
}

anim_tick = 0

def setup_camera(active_room):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # FOV 75 for fixed room-corner survival horror perspective
    gluPerspective(75.0, 1.25, 0.1, 1500.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Fixed Corner Camera for active room focusing on player
    cx, cy, cz = active_room.camera_pos
    lx = player.x
    ly = player.y
    lz = player.z + 30.0
    gluLookAt(cx, cy, cz, lx, ly, lz, 0, 0, 1)


def restart_game():
    global floors, enemies_by_floor, hazards_by_floor
    game.__init__()
    player.__init__()
    floors = {
        1: DungeonBuilder.build_floor_1(),
        2: DungeonBuilder.build_floor_2()
    }
    enemies_by_floor = {
        1: EnemySpawner.get_floor_enemies(1),
        2: EnemySpawner.get_floor_enemies(2)
    }
    hazards_by_floor = {
        1: HazardManager.get_floor_hazards(1),
        2: HazardManager.get_floor_hazards(2)
    }
    game.trigger_hud_message("Game Restarted! Allocate stats to begin.", 180)


def keyboardListener(key, x, y):
    # Cross-platform safe decoding for Windows, Linux FreeGLUT, and macOS
    try:
        if isinstance(key, bytes):
            k = key.decode("utf-8", errors="ignore")
        elif isinstance(key, int):
            k = chr(key)
        else:
            k = str(key)
    except Exception:
        k = ""

    # 1. Dev Console Input Interception
    if game.console_active:
        if k == '`' or k == '~':
            game.console_active = False
        elif k == '\r' or k == '\n':
            game.execute_dev_command(game.console_input)
            game.console_input = ""
        elif k == '\b':
            game.console_input = game.console_input[:-1]
        elif len(k) == 1 and ord(k) >= 32:
            game.console_input += k
        return

    # Toggle Dev Console with ~ key
    if k == '`' or k == '~':
        game.console_active = True
        return

    # Restart Game (R key)
    if k == 'r' or k == 'R':
        restart_game()
        return

    # Bandit Dialogue Options Interception
    if game.dialogue_active:
        room_bandits = [e for e in enemies_by_floor[game.current_floor] if e.room_id == game.current_room_id and e.is_human]
        if k == '1' or k == 'e' or k == 'E':
            game.resolve_dialogue(1, room_bandits)  # Charisma Persuasion D20 Check for all room bandits
        elif k == '2' or k == 'f' or k == 'F':
            game.resolve_dialogue(2, room_bandits)  # Engage in Combat for all room bandits
        return

    # 2. Character Creation Controls
    if game.state == STATE_CHAR_CREATE:
        if k == '1':
            if game.available_points > 0:
                game.strength += 1
                game.available_points -= 1
        elif k == '!':
            if game.strength > 1:
                game.strength -= 1
                game.available_points += 1
        elif k == '2':
            if game.available_points > 0:
                game.charisma += 1
                game.available_points -= 1
        elif k == '@':
            if game.charisma > 1:
                game.charisma -= 1
                game.available_points += 1
        elif k == '3':
            if game.available_points > 0:
                game.willpower += 1
                game.available_points -= 1
        elif k == '#':
            if game.willpower > 1:
                game.willpower -= 1
                game.available_points += 1
        elif k == '\r' or k == '\n':
            game.finalize_character()
        return

    # 3. Story Intro Controls
    if game.state == STATE_STORY_INTRO:
        if k == ' ' or k == '\r' or k == '\n':
            game.state = STATE_GAMEPLAY
            game.trigger_hud_message("Entered Sewer Entryway (Room 1)", 180)
        return

    # 4. Main Gameplay Tank Controls & Actions
    if game.state == STATE_GAMEPLAY:
        active_room = floors[game.current_floor][game.current_room_id]
        
        # W / S : Move Forward / Backward
        if k == 'w' or k == 'W':
            player.move(1, active_room.bounds)
        elif k == 's' or k == 'S':
            player.move(-1, active_room.bounds)

        # A / D : Turn Left / Right
        elif k == 'a' or k == 'A':
            player.turn(1)
        elif k == 'd' or k == 'D':
            player.turn(-1)

        # E : Interact with Doors, Chests, Human Bandits
        elif k == 'e' or k == 'E':
            room_enemies = [e for e in enemies_by_floor[game.current_floor] if e.room_id == game.current_room_id]
            player.interact(active_room, room_enemies)

        # F : Fire Twin Visor Laser Beams (2 Seconds Duration)
        elif k == 'f' or k == 'F':
            player.cast_laser()

        # C : Cannibalize Defeated Corpse
        elif k == 'c' or k == 'C':
            room_enemies = [e for e in enemies_by_floor[game.current_floor] if e.room_id == game.current_room_id]
            for enemy in room_enemies:
                if not enemy.is_alive and not enemy.corpse_cannibalized:
                    dx = player.x - enemy.x
                    dy = player.y - enemy.y
                    if math.sqrt(dx*dx + dy*dy) < 60:
                        enemy.corpse_cannibalized = True
                        game.cannibalize_corpse()
                        return

        # P : Drink Magicka Potion
        elif k == 'p' or k == 'P':
            game.drink_potion()

        # M : Toggle Minimap
        elif k == 'm' or k == 'M':
            game.show_minimap = not game.show_minimap


def specialKeyListener(key, x, y):
    # Arrow key camera adjustments
    active_room = floors[game.current_floor][game.current_room_id]
    cx, cy, cz = active_room.camera_pos
    if key == GLUT_KEY_LEFT:
        cx -= 20
    elif key == GLUT_KEY_RIGHT:
        cx += 20
    elif key == GLUT_KEY_UP:
        cy += 20
    elif key == GLUT_KEY_DOWN:
        cy -= 20
    active_room.camera_pos = (cx, cy, cz)


def mouseListener(button, state, x, y):
    if game.state != STATE_GAMEPLAY:
        return
        
    # Left Mouse Click : Melee Sword Attack
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        room_enemies = [e for e in enemies_by_floor[game.current_floor] if e.room_id == game.current_room_id]
        player.attack_melee(room_enemies)
        
    # Right Mouse Click : Shield Block Toggle
    elif button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            player.is_blocking = True
        else:
            player.is_blocking = False


last_frame_time = time.time()

def idle():
    global anim_tick, last_frame_time
    anim_tick += 1
    
    # Real-time delta time calculation (in seconds)
    current_time = time.time()
    dt = current_time - last_frame_time
    last_frame_time = current_time
    dt = min(dt, 0.1)  # Clamp max delta time to prevent large jumps
    
    # 1. Update Game Timers (Food decay and stamina tied to dt)
    game.update_timers(dt)
    
    # 2. Update Door Transitions
    transition_manager.update(player)

    # 3. Update Player & Room Entities
    if game.state == STATE_GAMEPLAY:
        active_room = floors[game.current_floor][game.current_room_id]
        active_enemies = [e for e in enemies_by_floor[game.current_floor] if e.room_id == game.current_room_id]
        player.update(active_room.bounds, active_room.doors, active_room.chests, active_room.pressure_plates, active_enemies)

        # Update hazards in current room
        for hazard in hazards_by_floor[game.current_floor]:
            if hazard.room_id == game.current_room_id:
                hazard.update(player)

        # Update enemies in current room
        for enemy in enemies_by_floor[game.current_floor]:
            if enemy.room_id == game.current_room_id:
                enemy.update(player)

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    # Enable Depth Testing for 3D Geometry
    glEnable(GL_DEPTH_TEST)

    # Fetch active room
    active_room = floors[game.current_floor][game.current_room_id]
    setup_camera(active_room)

    # 1. Render Active Room Geometry
    active_room.render_room(anim_tick)

    # 2. Render Active Room Hazards
    for hazard in hazards_by_floor[game.current_floor]:
        if hazard.room_id == game.current_room_id:
            hazard.render()

    # 3. Render Active Room Enemies
    active_enemies = [e for e in enemies_by_floor[game.current_floor] if e.room_id == game.current_room_id]
    for enemy in active_enemies:
        enemy.render()

    # 4. Render Player Model & Projectiles
    player.render()

    # 5. Disable Depth Testing for 2D HUD & UI Overlays
    glDisable(GL_DEPTH_TEST)
    UIRenderer.render_hud(player, active_room, active_enemies)

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"Chrono-Crypt of Aetherius - 3D OpenGL Dungeon Crawler")

    # Explicitly enable depth testing upon context creation
    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
