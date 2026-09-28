from game_state import game, STATE_GAMEPLAY, STATE_DOOR_TRANSITION

class DoorTransitionManager:
    def __init__(self):
        self.is_animating = False
        self.target_room_id = 1
        self.target_floor_id = 1
        self.anim_timer = 0
        self.max_anim_timer = 90  # 90 frames (~1.5 seconds)
        self.active_door_ref = None
        self.transition_text = ""

    def start_transition(self, door_ref, target_room, target_floor=None, player_ref=None):
        self.is_animating = True
        self.anim_timer = 0
        self.active_door_ref = door_ref
        self.target_room_id = target_room
        self.target_floor_id = target_floor if target_floor else game.current_floor
        
        if target_floor and target_floor != game.current_floor:
            self.transition_text = f"Descending to Floor {target_floor}: Crypt Catacombs..."
        else:
            self.transition_text = f"Opening Door to Room {target_room}..."
            
        game.state = STATE_DOOR_TRANSITION
        game.trigger_hud_message(self.transition_text, 120)

    def update(self, player_ref):
        if not self.is_animating:
            return
            
        self.anim_timer += 1
        
        # Phase 1 (0 to 30): Door opening swing animation
        if self.anim_timer <= 30:
            if self.active_door_ref:
                self.active_door_ref["open"] = True
                self.active_door_ref["anim_angle"] = min(90.0, (self.anim_timer / 30.0) * 90.0)

        # Phase 2 (30 to 60): Loading & Room State Swap
        elif self.anim_timer == 45:
            game.current_floor = self.target_floor_id
            if isinstance(self.target_room_id, int):
                game.current_room_id = self.target_room_id
            else:
                game.current_floor = 2
                game.current_room_id = 1
                
            # Reposition player at south doorway of new room
            if player_ref:
                player_ref.x = 0
                player_ref.y = -220
                player_ref.z = 0
                player_ref.angle = 90.0  # Facing North into room

        # Phase 3 (60 to 90): Transition finish & control restore
        elif self.anim_timer >= self.max_anim_timer:
            self.is_animating = False
            if self.active_door_ref:
                self.active_door_ref["anim_angle"] = 90.0
            game.state = STATE_GAMEPLAY
            game.trigger_hud_message(f"Entered Room {game.current_room_id}", 90)

transition_manager = DoorTransitionManager()
