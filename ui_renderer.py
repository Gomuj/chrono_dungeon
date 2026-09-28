from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from game_state import (
    game, STATE_CHAR_CREATE, STATE_STORY_INTRO, STATE_GAMEPLAY,
    STATE_DOOR_TRANSITION, STATE_GAME_OVER, STATE_VICTORY
)

def draw_text(x, y, text, r=1.0, g=1.0, b=1.0, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(r, g, b)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_2d_rect(x1, y1, x2, y2, r, g, b):
    glColor3f(r, g, b)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glBegin(GL_QUADS)
    glVertex3f(x1, y1, 0)
    glVertex3f(x2, y1, 0)
    glVertex3f(x2, y2, 0)
    glVertex3f(x1, y2, 0)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


class UIRenderer:
    @staticmethod
    def render_hud(player_ref, active_room, active_enemies=None):
        # 1. Character Creation Screen
        if game.state == STATE_CHAR_CREATE:
            draw_2d_rect(100, 100, 900, 700, 0.08, 0.08, 0.12)
            draw_text(250, 650, "CHRONO-CRYPT OF AETHERIUS", 0.9, 0.8, 0.2)
            draw_text(350, 600, "CHARACTER CREATION", 1.0, 1.0, 1.0)
            
            draw_text(200, 520, f"Attribute Points Remaining: {game.available_points}", 0.2, 0.9, 0.3)
            
            draw_text(200, 440, f"1. STRENGTH  :  [{game.strength}]   (Increases Melee Damage & Stamina)", 1.0, 0.4, 0.4)
            draw_text(200, 380, f"2. CHARISMA  :  [{game.charisma}]   (Increases Speech Check D20 Rolls)", 0.4, 0.7, 1.0)
            draw_text(200, 320, f"3. WILLPOWER :  [{game.willpower}]   (Increases Max Sanity & Firebolt Power)", 0.8, 0.4, 1.0)
            
            draw_text(200, 230, "Controls: Press 1/2/3 to add point. Shift + 1/2/3 to subtract.", 0.8, 0.8, 0.8)
            draw_text(200, 180, "Press [ENTER] to finalize character and begin quest!", 1.0, 0.9, 0.1)
            return

        # 2. Story Intro Cinematic Screen
        if game.state == STATE_STORY_INTRO:
            draw_2d_rect(100, 100, 900, 700, 0.05, 0.05, 0.08)
            draw_text(280, 640, "QUEST FOR THE ELDER SCROLL", 0.9, 0.7, 0.2)
            
            lines = [
                "For centuries, the Elder Scroll of Aetherius lay sealed within the deep crypts.",
                "Bandits and undead skeletal Draugr now infest the multi-floor complex.",
                "",
                "You enter the Sewer Complex (Floor 1), seeking entry to the Crypt (Floor 2).",
                "Your Sanity decays in the dark; maintain it or face madness and death.",
                "Should you die with high Sanity, the Dragon Break will rewind time on the spot!",
                "",
                "Controls:",
                "  - W/S: Tank Move Forward/Backward | A/D: Turn Left/Right",
                "  - Left Click: Melee Sword Swing | Right Click: Shield Block",
                "  - F Key / Wheel: Cast Firebolt Magic | E Key: Interact / D20 Speech Check",
                "  - C Key: Cannibalize Corpse | P Key: Drink Magicka Potion",
                "  - M Key: Minimap | ~ Key: Dev Console"
            ]
            y_off = 570
            for line in lines:
                draw_text(150, y_off, line, 0.85, 0.85, 0.85)
                y_off -= 28
                
            draw_text(300, 140, "Press [SPACE / ENTER] to descend into the Sewer!", 1.0, 0.9, 0.1)
            return

        # 3. Main Gameplay HUD
        # Top-Left Stat Bars Background
        draw_2d_rect(10, 660, 320, 790, 0.1, 0.1, 0.12)
        
        # Health Bar (Red)
        hp_pct = max(0.0, game.health / game.max_health)
        draw_2d_rect(100, 760, 310, 778, 0.3, 0.1, 0.1)
        draw_2d_rect(100, 760, 100 + int(210 * hp_pct), 778, 0.9, 0.2, 0.2)
        draw_text(15, 762, "HP", 1.0, 0.8, 0.8)

        # Sanity Bar (Blue)
        san_pct = max(0.0, game.sanity / game.max_sanity)
        draw_2d_rect(100, 732, 310, 750, 0.1, 0.1, 0.3)
        draw_2d_rect(100, 732, 100 + int(210 * san_pct), 750, 0.2, 0.5, 0.95)
        draw_text(15, 734, "SAN", 0.8, 0.9, 1.0)

        # Stamina Bar (Green)
        stam_pct = max(0.0, game.stamina / game.max_stamina)
        draw_2d_rect(100, 704, 310, 722, 0.1, 0.3, 0.1)
        draw_2d_rect(100, 704, 100 + int(210 * stam_pct), 722, 0.2, 0.85, 0.3)
        draw_text(15, 706, "STM", 0.8, 1.0, 0.8)

        # Food Bar (Orange)
        food_pct = max(0.0, game.food / game.max_food)
        draw_2d_rect(100, 676, 310, 694, 0.3, 0.2, 0.05)
        draw_2d_rect(100, 676, 100 + int(210 * food_pct), 694, 0.95, 0.6, 0.1)
        draw_text(15, 678, "FOOD", 1.0, 0.8, 0.4)

        # Top-Right Potion & Dragon Break Info
        draw_2d_rect(680, 740, 990, 790, 0.1, 0.1, 0.12)
        draw_text(695, 755, f"Potions: {game.potions} | Dragon Breaks: {game.dragon_break_count}", 0.9, 0.9, 0.9)

        # Boss Health Bar (Top Center of Screen, active when player is in room with living boss)
        if active_enemies:
            boss = next((e for e in active_enemies if e.enemy_type == "BOSS" and e.is_alive), None)
            if boss:
                # Frame Container (x=330..670, y=715..785)
                draw_2d_rect(330, 715, 670, 785, 0.08, 0.06, 0.12)
                # Golden Trim Borders
                draw_2d_rect(330, 782, 670, 785, 0.85, 0.7, 0.2)
                draw_2d_rect(330, 715, 670, 718, 0.85, 0.7, 0.2)
                draw_2d_rect(330, 715, 333, 785, 0.85, 0.7, 0.2)
                draw_2d_rect(667, 715, 670, 785, 0.85, 0.7, 0.2)
                
                # Boss Name Header
                draw_text(375, 760, f"=== {boss.name.upper()} ===", 1.0, 0.25, 0.75)
                
                # Boss HP Bar Track
                boss_hp_pct = max(0.0, boss.hp / boss.max_hp)
                draw_2d_rect(350, 728, 650, 748, 0.25, 0.08, 0.14)
                # Boss HP Active Bar (Glowing Crimson / Magenta)
                draw_2d_rect(350, 728, 350 + int(300 * boss_hp_pct), 748, 0.95, 0.15, 0.45)

        # Bottom HUD Message Banner
        if game.hud_message_timer > 0:
            draw_2d_rect(150, 20, 850, 55, 0.08, 0.08, 0.12)
            draw_text(170, 32, game.hud_message, 1.0, 0.9, 0.3)

        # Dialogue Overlay Box
        if game.dialogue_active:
            draw_2d_rect(100, 80, 900, 240, 0.08, 0.08, 0.14)
            draw_text(130, 205, f"=== DIALOGUE: {game.dialogue_speaker.upper()} ===", 0.9, 0.7, 0.2)
            draw_text(130, 175, f"\"{game.dialogue_text}\"", 1.0, 1.0, 1.0)
            draw_text(130, 135, "[1] Persuade with Charisma (Roll D20 + Charisma vs DC 12)", 0.4, 0.85, 1.0)
            draw_text(130, 105, "[2] Draw Sword & Engage in Combat", 1.0, 0.4, 0.4)

        # D20 Skill Check Box Overlay
        if game.d20_rolling or game.d20_display_timer > 0:
            draw_2d_rect(120, 500, 880, 620, 0.12, 0.1, 0.18)
            draw_text(300, 580, game.d20_header if game.d20_header else "=== D20 SKILL CHECK ===", 0.9, 0.7, 0.2)
            draw_text(150, 540, game.d20_detail if game.d20_detail else game.d20_message, 1.0, 1.0, 1.0)

        # 4. Minimap Overlay (M Key)
        if game.show_minimap:
            draw_2d_rect(720, 420, 980, 680, 0.05, 0.08, 0.1)
            draw_text(740, 655, "ROOM MINIMAP", 0.3, 0.9, 0.4)
            # Map player pos to minimap coords
            mx = 850 + int(player_ref.x * 0.35)
            my = 550 + int(player_ref.y * 0.35)
            draw_2d_rect(mx - 4, my - 4, mx + 4, my + 4, 1.0, 0.2, 0.2)

        # 5. Dev Console Overlay (~ Key)
        if game.console_active:
            draw_2d_rect(50, 450, 950, 770, 0.05, 0.05, 0.05)
            draw_text(70, 745, "=== DEVELOPER CONSOLE ===", 0.3, 0.9, 0.3)
            y_log = 715
            for log in game.console_logs[-8:]:
                draw_text(70, y_log, log, 0.85, 0.85, 0.85)
                y_log -= 25
            draw_text(70, 470, f"> {game.console_input}_", 1.0, 1.0, 0.2)

        # 6. Game Over & Victory Screens
        if game.state == STATE_GAME_OVER:
            draw_2d_rect(0, 0, 1000, 800, 0.2, 0.0, 0.0)
            draw_text(320, 450, "PERMANENT DEATH", 1.0, 0.2, 0.2)
            draw_text(310, 390, "Press [R] to restart the quest from Character Creation", 1.0, 1.0, 1.0)

        elif game.state == STATE_VICTORY:
            draw_2d_rect(0, 0, 1000, 800, 0.0, 0.2, 0.1)
            draw_text(260, 460, "VICTORY! ELDER SCROLL RECOVERED!", 0.2, 1.0, 0.4)
            draw_text(270, 400, "You escaped the Chrono-Crypt of Aetherius!", 1.0, 1.0, 1.0)
            draw_text(310, 340, "Press [R] to play again", 0.9, 0.9, 0.2)
