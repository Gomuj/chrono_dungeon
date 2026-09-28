# Project Specification: Chrono-Crypt of Aetherius
**Course:** CSE 423: Computer Graphics Final Project  
**Section:** [Section 20 / Section 21]  
**Group members:**  
1. [Name 1] - [ID 1]  
2. [Name 2] - [ID 2]  
3. [Name 3] - [ID 3]  

---

## 1. Project Overview & Theme
**Chrono-Crypt of Aetherius** is a 3D survival-RPG dungeon crawler built with PyOpenGL, inspired by classic *Elder Scrolls* titles (*Arena*, *Daggerfall*) and retro survival horror mechanics (classic *Resident Evil* **fixed camera angles** with tank controls, procedural geometric detailing, psychological sanity decay).

The player creates a custom character and descends through a dangerous 3-level complex (**Sewer $\rightarrow$ Crypt $\rightarrow$ Scroll Chamber**) to recover the legendary **Elder Scroll of Aetherius**. Facing human bandits, undead skeletons, and an **Undead Lich Boss**, the player must balance combat, magic, hunger, and sanity. The game emphasizes **immersive freedom**, allowing players to bypass fights using alternate stealth routes or **Charisma D20 speech checks**, while introducing a temporal **Dragon Break** sanity-based resurrection system.

---

## 2. Feature Expansion (3× Feature Rule & 100% Template Function Compliance)
To satisfy course requirements, the project expands on Lab 3 (*Bullet Frenzy*) with over 20 distinct gameplay, visual, and AI features **using strictly the PyOpenGL functions present in `3d_opengl_intro.py`**:

### Feature Expansion Table

| Category | Lab 3 Feature | Chrono-Crypt of Aetherius Expanded Features |
| :--- | :--- | :--- |
| **Player System** | Single preset character, basic translation/rotation. | 1. **Character Creation:** Custom attribute allocation (Strength, Charisma, Willpower).<br>2. **Composite Player Model:** Helmet visor, iron chestplate, limbs (`gluCylinder`), sword & shield.<br>3. **Fixed-Camera Tank Controls:** Fixed corner cameras with tank movement (`W/S` forward/back, `A/D` rotate orientation).<br>4. **Four Stat Pools:** Health (Red), Sanity (Blue), Stamina (Green), and Food (Hunger bar). |
| **Enemy AI & Models** | 5 identical chasing spheres. | 5. **Human Bandits:** Hooded leather-armored foes carrying daggers.<br>6. **Undead Draugr:** Ancient skeletal Nords with glowing cyan eyes & battleaxes.<br>7. **Undead Lich Boss:** Floating hooded sorcerer with glowing staff.<br>8. **Non-Combat Paths:** Charisma speech checks to pacify enemies or secret bypass routes. |
| **Graphics & Detailing** | Flat solid color quads and cubes. | 9. **Procedural Geometric Detailing:** Embossed brick patterns, baseboard trims, iron bands on chests, and carved stone wall panels using `GL_QUADS`, `glutSolidCube`, and `gluCylinder`.<br>10. **Torchlight Distance Shading:** Fading vertex colors based on distance to simulate ambient lighting. |
| **Combat & Magic** | Gun shooting, no blocking or spells. | 11. **Iron Sword Melee:** Rotating cylinder swing using Stamina.<br>12. **Shield Blocking:** Absorbs frontal damage.<br>13. **Firebolt Spell:** Projectile magic consuming Sanity.<br>14. **D20 Skill Checks:** Tabletop dice roll mechanic for Charisma speech checks. |
| **Survival & Horror** | No hunger, static game over on hit count. | 15. **Food Decay System:** Continuous hunger timer.<br>16. **Enemy Cannibalism:** Option to eat defeated foes for food at the cost of Sanity & stat debuffs.<br>17. **Sanity Hallucinations:** Low sanity causes color flickering, phantom enemies, or fear locks. |
| **Puzzles & Env** | Flat checkered floor, 4 plain walls. | 18. **3-Floor Progression:** Sewer $\rightarrow$ Crypt $\rightarrow$ Scroll Chamber.<br>19. **Matching Claw Lock:** Doors requiring matching keystone claws.<br>20. **Pressure Plates & Loot Chests:** Interactive slabs and animated potion chests. |
| **Traps & System** | Simple live counter, basic restart. | 21. **Hazards:** Swinging Blade pendulums, Spike Traps, Fire-breathing carvings.<br>22. **Dragon Break Rewind:** High Sanity lets players respawn on the spot without enemy resets.<br>23. **Story Intro & Dev Console:** Opening story cinematic and functional dev console (`~` key for `tgm`, `tcl`).<br>24. **Minimap:** 2D wireframe radar overlay. |

---

## 3. Procedural Character & Enemy 3D Models

All character models are assembled procedurally using nested `glPushMatrix` / `glPopMatrix` matrix hierarchies and template functions (`gluSphere`, `gluCylinder`, `glutSolidCube`):

### 1. Player Character (Adventurer)
* **Head & Helmet:** Metallic grey sphere (`gluSphere`) with dark iron visor cuboid.
* **Torso:** Iron chestplate cuboid (`glutSolidCube`) with leather pauldrons (`gluCylinder`).
* **Arms & Legs:** Connected cylinders (`gluCylinder`) with knee/elbow joints (`gluSphere`).
* **Equipment:** Iron Sword (cylinder blade + crossguard cuboid) in right hand; Iron Shield (rimmed cuboid) in left hand.
* **Animations:** Sine-wave leg/arm walking swing, 120-degree sword attack arc, shield block raise.

### 2. Human Bandits
* **Model:** Dark brown cloth hood (`gluSphere`), leather tunic (`glutSolidCube`), boots/gloves (`gluCylinder`), holding an iron dagger.
* **Behavior:** Patrols corridors; charges player when spotted; pacified if player passes D20 Charisma check.

### 3. Undead Draugr Warriors
* **Model:** Skeletal grey/blue bone cylinders, glowing cyan magic eye spheres (`gluSphere`), rusted Nordic horned helmet, holding a double-bladed battleaxe.
* **Behavior:** Heavy melee pathfinder; slow menacing walk; overhead axe strike animation.

### 4. Undead Lich Boss (Scroll Chamber)
* **Model:** Floating dark sorcerer cowl (tapered cylinder), skeletal skull sphere, floating hands, holding a tall staff with a glowing purple orb (`gluSphere`).
* **Behavior:** Hovering vertical sine-wave float (`y += \sin(2t)`), fires homing fireball projectiles.

---

## 4. Key Gameplay Loop & Controls
* **Movement:** `W`/`S` (move forward/backward relative to character orientation), `A`/`D` (rotate player facing angle).
* **Melee Sword:** Left Mouse Click (consumes Stamina).
* **Firebolt Magic:** Key `F` / Mouse Wheel (consumes Sanity).
* **Shield Block:** Hold Right Mouse Button (blocks frontal damage).
* **D20 Charisma Check:** Press `E` when approaching human bandits to initiate a speech roll.
* **Cannibalize Corpse:** Press `C` near defeated enemies to replenish Food (reduces Sanity and risks stat debuffs).
* **Minimap & Dev Console:** Press `M` for 2D minimap, `~` for Developer Console (`tgm`, `tcl`).

### Dragon Break Respawns
When Health drops to 0:
* **Sanity $\ge$ Threshold:** The player immediately respawns at their exact death location with full Health. Enemies do **not** respawn. The Sanity threshold increases after every Dragon Break.
* **Sanity $<$ Threshold:** Permanent death occurs, triggering the Game Over screen.
