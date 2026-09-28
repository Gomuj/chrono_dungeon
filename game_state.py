import math
import random

# Game States
STATE_CHAR_CREATE = 0
STATE_STORY_INTRO = 1
STATE_GAMEPLAY = 2
STATE_DOOR_TRANSITION = 3
STATE_GAME_OVER = 4
STATE_VICTORY = 5

class GameState:
    def __init__(self):
        self.state = STATE_CHAR_CREATE
        
        # Character Creation Attributes
        self.available_points = 10
        self.strength = 5
        self.charisma = 5
        self.willpower = 5
        
        # Stat Pools
        self.max_health = 100
        self.health = 100
        self.max_sanity = 100
        self.sanity = 100
        self.max_stamina = 100
        self.stamina = 100
        self.max_food = 100
        self.food = 100
        
        # Inventory & Key Items
        self.potions = 2
        self.has_golden_claw = False
        self.has_elder_relic = False
        
        # Floor & Room Tracking (1-indexed)
        self.current_floor = 1  # 1: Sewer, 2: Crypt
        self.current_room_id = 1
        
        # Dragon Break Mechanism
        self.dragon_break_count = 0
        self.required_sanity_threshold = 30
        
        # D20 Dice State
        self.d20_rolling = False
        self.d20_timer = 0
        self.d20_display_timer = 0
        self.d20_result = 0
        self.d20_success = False
        self.d20_header = ""
        self.d20_detail = ""
        self.d20_message = ""
        self.d20_callback = None
        
        # Dev Console & Minimap
        self.console_active = False
        self.console_input = ""
        self.console_logs = ["Dev Console Active. Type 'help' for commands."]
        self.god_mode = False
        self.show_minimap = False
        
        # Bandit Dialogue System
        self.dialogue_active = False
        self.dialogue_speaker = ""
        self.dialogue_text = ""
        self.dialogue_enemy_ref = None
        
        # Story Intro
        self.intro_slide = 0

        # Cannibalism & Sanity Debuffs
        self.cannibal_count = 0
        self.cannibal_debuff_timer = 0
        
        # HUD Message Banner
        self.hud_message = "Allocate stats and press ENTER to start!"
        self.hud_message_timer = 300

    def start_dialogue(self, speaker, text, enemy_ref):
        self.dialogue_active = True
        self.dialogue_speaker = speaker
        self.dialogue_text = text
        self.dialogue_enemy_ref = enemy_ref
        self.trigger_hud_message(f"Dialogue: {speaker} initiated conversation! Press 1 for Charisma Check, 2 to Fight", 300)

    def resolve_dialogue(self, choice, room_bandits=None):
        if not self.dialogue_active or not self.dialogue_enemy_ref:
            return
            
        enemy = self.dialogue_enemy_ref
        if choice == 1:
            # Charisma D20 Persuasion Check vs DC 12
            def pacify_cb(success):
                if success:
                    # Pacify ALL bandits in the room!
                    if room_bandits:
                        for b in room_bandits:
                            if b.is_human:
                                b.is_pacified = True
                    else:
                        enemy.is_pacified = True
                    self.trigger_hud_message(f"Charisma Check PASSED! All bandits in the room are pacified and stand aside!", 240)
                else:
                    # Make ALL bandits in the room hostile!
                    if room_bandits:
                        for b in room_bandits:
                            if b.is_human:
                                b.is_hostile = True
                    else:
                        enemy.is_hostile = True
                    self.trigger_hud_message(f"Charisma Check FAILED! All bandits in the room draw weapons!", 240)
                self.dialogue_active = False
                self.dialogue_enemy_ref = None

            self.roll_d20(12, self.charisma, pacify_cb, "Charisma Persuasion Check")
        else:
            # Player chooses combat -> ALL room bandits become hostile!
            if room_bandits:
                for b in room_bandits:
                    if b.is_human:
                        b.is_hostile = True
            else:
                enemy.is_hostile = True
            self.dialogue_active = False
            self.dialogue_enemy_ref = None
            self.trigger_hud_message(f"You refused dialogue! All bandits engage in combat!", 180)

    def finalize_character(self):
        self.max_health = 100 + self.strength * 10
        self.health = self.max_health
        self.max_sanity = 100 + self.willpower * 10
        self.sanity = self.max_sanity
        self.max_stamina = 100 + self.strength * 5 + self.willpower * 5
        self.stamina = self.max_stamina
        self.max_food = 100
        self.food = 100
        self.state = STATE_STORY_INTRO

    def trigger_hud_message(self, text, duration=180):
        self.hud_message = text
        self.hud_message_timer = duration

    def update_timers(self, dt=0.016):
        if self.hud_message_timer > 0:
            self.hud_message_timer -= 1
            
        # Food & Stamina Regen / Decay in Gameplay (Tied to Delta Time)
        if self.state == STATE_GAMEPLAY:
            if not self.god_mode:
                # Food decays at a constant real-time rate (1.2 units/sec) regardless of FPS
                food_decay_per_sec = 1.2
                self.food -= food_decay_per_sec * dt
                if self.food <= 0:
                    self.food = 0
                    self.health = 0
                    self.trigger_hud_message("Starved to death! Food reached 0!", 180)
                    self.handle_player_death()
                        
            # Stamina regen (18.0 units/sec)
            if self.stamina < self.max_stamina:
                self.stamina = min(self.max_stamina, self.stamina + 18.0 * dt)
                
            # Cannibalism debuff timer
            if self.cannibal_debuff_timer > 0:
                self.cannibal_debuff_timer -= 1
                if random.random() < 0.02 and not self.god_mode:
                    self.health = max(1.0, self.health - 0.2)
                    self.stamina = max(0.0, self.stamina - 0.5)

        # D20 Dice animation timer & auto-hide result timer
        if self.d20_rolling:
            self.d20_timer -= 1
            if self.d20_timer <= 0:
                self.d20_rolling = False
                if self.d20_callback:
                    self.d20_callback(self.d20_success)
                    
        if self.d20_display_timer > 0:
            self.d20_display_timer -= 1
            if self.d20_display_timer <= 0:
                self.d20_message = ""
                self.d20_header = ""
                self.d20_detail = ""

    def drink_potion(self):
        if self.potions > 0:
            self.potions -= 1
            self.sanity = min(self.max_sanity, self.sanity + 40)
            self.health = min(self.max_health, self.health + 0)
            self.trigger_hud_message("Drank Magicka Potion! (+40 Sanity)")
            return True
        else:
            self.trigger_hud_message("No Magicka Potions remaining!")
            return False

    def cannibalize_corpse(self):
        self.food = min(self.max_food, self.food + 50)
        self.sanity = max(0, self.sanity - 25)
        self.cannibal_count += 1
        self.cannibal_debuff_timer = 600  # 10 second debuff
        self.trigger_hud_message("Cannibalized corpse! (+50 Food, -25 Sanity, Debuffed)")

    def roll_d20(self, difficulty, attribute_bonus, success_callback=None, message="Skill Check"):
        self.d20_rolling = True
        self.d20_timer = 60  # 1 second animation
        self.d20_display_timer = 180  # Display result for 3 seconds then auto-hide
        raw_roll = random.randint(1, 20)
        total_roll = raw_roll + attribute_bonus
        self.d20_result = total_roll
        self.d20_success = (total_roll >= difficulty)
        self.d20_callback = success_callback
        
        status_str = "SUCCESS" if self.d20_success else "FAILED"
        self.d20_header = f"=== D20 SKILL CHECK: {message.upper()} ==="
        self.d20_detail = f"Rolled {raw_roll} + {attribute_bonus} = {total_roll} vs DC {difficulty} ({status_str})"
        self.d20_message = f"{message}: {self.d20_detail}"
        self.trigger_hud_message(self.d20_detail, 180)

    def handle_player_death(self):
        if self.god_mode:
            self.health = self.max_health
            return

        if self.sanity >= self.required_sanity_threshold:
            # Dragon Break Triggered!
            self.dragon_break_count += 1
            self.health = self.max_health
            self.sanity = max(10, self.sanity - 20)
            self.required_sanity_threshold += 55
            self.trigger_hud_message(f"DRAGON BREAK! Time rewound on death! Next req Sanity: {self.required_sanity_threshold}", 300)
            # Respawns in current room without enemy reset
        else:
            self.state = STATE_GAME_OVER
            self.trigger_hud_message("Permanent Death!", 300)

    def execute_dev_command(self, cmd_str):
        parts = cmd_str.strip().split()
        if not parts:
            return
        cmd = parts[0].lower()
        
        if cmd == "help":
            self.console_logs.append("Commands: tgm, addpot, heal, room <1-4>, floor <1-2>, sanity <val>")
        elif cmd == "tgm":
            self.god_mode = not self.god_mode
            self.console_logs.append(f"God Mode: {self.god_mode}")
        elif cmd == "addpot":
            self.potions += 5
            self.console_logs.append(f"Potions added. Total: {self.potions}")
        elif cmd == "heal":
            self.health = self.max_health
            self.sanity = self.max_sanity
            self.stamina = self.max_stamina
            self.food = self.max_food
            self.console_logs.append("Player fully restored!")
        elif cmd == "room" and len(parts) > 1:
            try:
                rid = int(parts[1])
                if 1 <= rid <= 4:
                    self.current_room_id = rid
                    self.console_logs.append(f"Teleported to Room {rid}")
            except ValueError:
                pass
        elif cmd == "floor" and len(parts) > 1:
            try:
                fid = int(parts[1])
                if 1 <= fid <= 2:
                    self.current_floor = fid
                    self.current_room_id = 1
                    self.console_logs.append(f"Teleported to Floor {fid}")
            except ValueError:
                pass
        elif cmd == "sanity" and len(parts) > 1:
            try:
                val = float(parts[1])
                self.sanity = min(self.max_sanity, max(0.0, val))
                self.console_logs.append(f"Sanity set to {self.sanity}")
            except ValueError:
                pass
        else:
            self.console_logs.append(f"Unknown command: '{cmd}'")

        if len(self.console_logs) > 8:
            self.console_logs.pop(0)

# Global Instance
game = GameState()
