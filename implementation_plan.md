# Goal Description: Chrono-Crypt of Aetherius (Elder Scrolls RPG / Survival Dungeon Crawler)

Develop an Elder Scrolls-themed 3D survival dungeon crawler built using **strictly the PyOpenGL functions present in `3d_opengl_intro.py`** to ensure 100% safety from function-usage mark deductions.

The player creates a character and navigates a multi-level complex (**Sewer -> Crypt -> Scroll Chamber**) to recover the legendary **Elder Scroll of Aetherius**.

This plan incorporates procedural geometric texturing (embossed brick quads, wood chest iron bands, stone trims built via `glutSolidCube` and `GL_QUADS`), classic survival horror (Resident Evil 1/2 style **Fixed-Camera Angles** in corridor/room corners viewing the full corridor and player character, with Tank Controls `W/S` forward/back and `A/D` rotation), tabletop RPG elements (D20 skill checks, Charisma speech checks), psychological horror (Sanity decay, hallucinations), and survival mechanics (Food hunger timer, enemy cannibalism with permanent penalties), alongside Elder Scrolls combat, magic, traps, and Dragon Break time-rewind mechanics.

---

## User Review Required

> [!IMPORTANT]
> **API Constraints & Zero-Penalty Guarantee:** 
> * We use **ONLY** the functions from `3d_opengl_intro.py` (`glColor3f`, `glTranslatef`, `glRotatef`, `glScalef`, `glutSolidCube`, `gluCylinder`, `gluSphere`, `glBegin/glEnd` with `GL_QUADS` & `GL_POINTS`, `gluPerspective`, `gluLookAt`, `gluOrtho2D`, `draw_text`).
> * **Procedural Geometric Texturing:** Detailed stone wall reliefs, floor tile quads, wood chest borders, and rune symbols are constructed procedurally from geometric primitives (`GL_QUADS`, `glutSolidCube`, `gluCylinder`). This provides rich visual detail with 0% risk of mark deduction!

---

## Proposed Changes

We will create a clean project structure in `C:\Users\Endministrator\.gemini\antigravity\scratch\chrono_dungeon`:

### Components

#### [NEW] [main.py](file:///C:/Users/Endministrator/.gemini/antigravity/scratch/chrono_dungeon/main.py)
Game initialization, main loop, GLUT registrations, state management (Character Creation -> Intro Cinematic -> Gameplay -> Dragon Break / Game Over).

#### [NEW] [dungeon.py](file:///C:/Users/Endministrator/.gemini/antigravity/scratch/chrono_dungeon/dungeon.py)
3-floor grid generation (**Sewer, Crypt, Scroll Chamber**), corridor fixed camera node mapping, procedural stone wall/floor geometry rendering, secret bypass routes, pressure plates, key-claw doors, and loot chests.

#### [NEW] [player.py](file:///C:/Users/Endministrator/.gemini/antigravity/scratch/chrono_dungeon/player.py)
Tracks Health (Red), Sanity (Blue), Stamina (Green), and Food (Hunger). Implements Tank Controls, D20 stat check roll generator, character creation traits, and hunger/sanity decay.

#### [NEW] [enemies.py](file:///C:/Users/Endministrator/.gemini/antigravity/scratch/chrono_dungeon/enemies.py)
Handles Human Bandits, Undead Draugr, and the **Undead Lich Boss**. Implements pacification states (via Charisma checks) and cannibalize actions on corpses.

#### [NEW] [hazards.py](file:///C:/Users/Endministrator/.gemini/antigravity/scratch/chrono_dungeon/hazards.py)
Renders and simulates environmental hazards: Swinging Blades, Spike Traps, and Fire-breathing wall carvings.

#### [NEW] [renderer.py](file:///C:/Users/Endministrator/.gemini/antigravity/scratch/chrono_dungeon/renderer.py)
Handles 3D rendering (fixed corner cameras, character and weapon models), torchlight distance shading, hallucinations, D20 dice animations, 2D radar minimap, and developer console (`~` key).

---

## Detailed Feature List (3x of Assignment 3)

### 1. Character Creation & Stat Systems
* **Character Creation Screen:** Allocate starting points into Strength, Charisma, and Willpower.
* **Three Stat Pools + Hunger:** Health (Red), Sanity (Blue), Stamina (Green), and Food (Hunger bar).
* **D20 Skill Checks:** Tabletop dice roll mechanic for Charisma checks, trap disarming, and lockpicking.

### 2. Combat & Magic & Sanity
* **Melee Combat (Stamina):** Iron sword swing (cylinder rotation).
* **Magic Firebolt (Sanity):** Projectile spell consuming Sanity.
* **Shield Block (Stamina):** Directional shield raise to absorb incoming damage.
* **Sanity Effects & Hallucinations:** Low sanity causes color flickering, phantom enemy illusions, or fear locks when entering boss areas.

### 3. Dragon Break & Survival Rules
* **Dragon Break Death Mechanics:** Dying with sufficient Sanity respawns the player on the spot without resetting enemies. Sanity cost scaling increases over time.
* **Food & Cannibalism:** Hunger decays over time. Player can cannibalize defeated human/undead enemies for food at the cost of Sanity loss and permanent stat debuffs.

### 4. Non-Combat & Immersive Options
* **Charisma Speech Checks:** Talk to human bandits to negotiate passage without fighting.
* **Alternate Routes:** Secret ventilation shafts and side corridors bypassing main combat arenas.

### 5. Multi-Floor Environment & Enemies
* **3-Floor Progression:** Sewer -> Crypt -> Scroll Chamber (Undead Lich Boss).
* **3 Enemy Types:** Human Bandits, Undead Skeletal Draugr, Undead Lich Boss.
* **Hazards:** Swinging Blades, Spike Traps, Fire Traps.
* **Puzzles:** Claw Key doors, Pressure Plates, and Magicka Potion Loot Chests.

### 6. UI, Story & Console
* **Intro Cinematic:** Animated narrative sequence presenting the quest for the Elder Scroll.
* **Fixed Camera Angle Tank View:** Classic Resident Evil 1/2 style corner camera overview.
* **2D Minimap & Dev Console:** `M` key map overlay and `~` dev console (`tgm`, `tcl`).

---

## Verification Plan

### Automated Checks
* Run syntax and module import validations across `main.py`, `player.py`, `dungeon.py`, `enemies.py`, `hazards.py`, `renderer.py`.

### Manual Verification
* Test Character Creation menu & stat allocation.
* Verify procedural geometric wall/floor detailing.
* Verify D20 dice roll animations on speech checks.
* Validate Fixed Camera Tank Controls movement and combat actions.
* Verify Dragon Break respawn logic when Sanity is high vs. standard restart when low.
* Check Cannibalism mechanic (replenishes food, lowers sanity, triggers debuff).
