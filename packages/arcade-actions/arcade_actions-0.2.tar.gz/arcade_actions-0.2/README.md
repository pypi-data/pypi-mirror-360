# ArcadeActions Framework Documentation

## 🚀 Quick Appeal

So much of building an arcade game is saying "animate this sprite until X happens", where X is colliding with another sprite, reaching a boundary, or responding to an event. Instead of low-level behavior like "add 1 to sprite.x", what if you could declare "keep moving and rotating this asteroid, wrap it the other side of the window if it hits a boundary, and call a function if it collides with another sprite (and tell me what sprite it is)."? 

```python 
# assume player and asteroid are arcade.Sprites, and asteroid_list is a arcade.SpriteList
move = MoveUntil((5, 4), lambda: False)
rotate = RotateUntil(1.5, lambda: False, asteroid_collision_check, handle_asteroid_collision)
actions = parallel(move, rotate)
actions.apply(asteroid)

def asteroid_collision_check():
    player_hit = arcade.check_for_collision(player, asteroid)
    asteroid_hits = arcade.check_for_collision_with_list(asteroid, asteroid_list)
    
    if player_hit or asteroid_hits:
        return {
            "player_hit": player_hit,
            "asteroid_hit": asteroid_hits,
        }
    return None  # Continue moving

# The callback receives the collision data from the condition function
def handle_asteroid_collision(collision_data):
    if collision_data["player_hit"]
        print("Player destroyed!")
    for asteroid in collision_data["asteroid_hits"]:
        print("Asteroid collisions!")
```
Compare this to the amount of low-level game code you are writing now. If making your game code clean, efficient and high-level like this appeals to you, read on!

## 📚 Documentation Overview

### Essential Reading
1. **[API Usage Guide](docs/api_usage_guide.md)** - **START HERE** - Complete guide to using the framework
2. **[Testing Guide](docs/testing_guide.md)** - **Testing patterns and best practices**
3. **[PRD](docs/prd.md)** - Project requirements and architecture decisions


## 🚀 Getting Started

1. **Read the [API Usage Guide](api_usage_guide.md)** to understand the framework
2. **Study the Space Invaders example** above for a complete pattern
3. **Start with simple conditional actions** and build up to complex compositions
4. **Use formation functions** for organizing sprite positions and layouts

## 📖 Documentation Structure

```
docs/
├── README.md                 # This file - overview and quick start
├── api_usage_guide.md       # Complete API usage patterns (START HERE)
├── testing_guide.md         # Testing patterns and fixtures
└── prd.md                   # Requirements and architecture
```

## 🔧 Core Components

### ✅ Implementation

#### Base Action System (actions/base.py)
- **Action** - Core action class with global management
- **CompositeAction** - Base for sequential and parallel actions
- **Global management** - Automatic action tracking and updates
- **Composition helpers** - `sequence()` and `parallel()` functions

#### Conditional Actions (actions/conditional.py)
- **MoveUntil** - Velocity-based movement until condition met
- **FollowPathUntil** - Follow Bezier curve paths with optional automatic sprite rotation
- **RotateUntil** - Angular velocity rotation
- **ScaleUntil** - Scale velocity changes  
- **FadeUntil** - Alpha velocity changes
- **DelayUntil** - Wait for condition to be met
- **TweenUntil** - Direct property animation from start to end value

#### Composite Actions (actions/composite.py)
- **Sequential actions** - Run actions one after another (use `sequence()`)
- **Parallel actions** - Run actions in parallel (use `parallel()`)

#### Boundary Handling (actions/conditional.py)
- **MoveUntil with bounds** - Built-in boundary detection with bounce/wrap behaviors

#### Formation Management (actions/formation.py)
- **Formation functions** - Grid, line, circle, diamond, and V-formation positioning

#### Movement Patterns (actions/pattern.py)
- **Movement pattern functions** - Zigzag, wave, spiral, figure-8, orbit, bounce, and patrol patterns
- **Condition helpers** - Time-based and sprite count conditions for conditional actions

#### Easing Effects (actions/easing.py)
- **Ease wrapper** - Apply smooth acceleration/deceleration curves to any conditional action
- **Multiple easing functions** - Built-in ease_in, ease_out, ease_in_out support
- **Custom easing** - Create specialized easing curves and nested easing effects

## 📋 Decision Matrix

| Scenario | Use | Example |
|----------|-----|---------|
| Single sprite behavior | Direct action application | `action.apply(sprite, tag="move")` |
| Group coordination | Action on SpriteList | `action.apply(enemies, tag="formation")` |
| Sequential behavior | `sequence()` | `sequence(delay, move, fade)` |
| Parallel behavior | `parallel()` | `parallel(move, rotate, scale)` |
| Formation positioning | Pattern functions | `arrange_grid(enemies, rows=3, cols=5)` |
| Curved path movement | FollowPathUntil | `FollowPathUntil(points, 200, condition, rotate_with_path=True)` |
| Boundary detection | MoveUntil with bounds | `MoveUntil(vel, cond, bounds=bounds, boundary_behavior="bounce")` |
| Smooth acceleration | Ease wrapper | `Ease(action, seconds=2.0, ease_function=easing.ease_in_out)` |
| Complex curved movement | Ease + FollowPathUntil | `Ease(FollowPathUntil(points, vel, cond, rotate_with_path=True), 1.5)` |
| Property animation | TweenUntil | `TweenUntil(0, 100, "center_x", duration(1.0))` |
| Standard sprites (no actions) | arcade.Sprite + arcade.SpriteList | Regular Arcade usage |


## 🎮 Example: Space Invaders Pattern

```python
import arcade
from actions.base import Action
from actions.conditional import MoveUntil, DelayUntil, duration
from actions.formation import arrange_grid


class SpaceInvadersGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Space Invaders")
        
        # Create 5×10 grid of enemies with a single call
        enemies = arrange_grid(
            rows=5,
            cols=10,
            start_x=100,
            start_y=500,
            spacing_x=60,
            spacing_y=40,
            sprite_factory=lambda: arcade.Sprite(":resources:images/enemy.png"),
        )
        
        # Store enemies for movement management
        self.enemies = enemies
        self._setup_movement_pattern()
    
    def _setup_movement_pattern(self):
        # Create formation movement with boundary bouncing
        def on_boundary_hit(sprite, axis):
            if axis == 'x':
                # Move entire formation down and change direction
                drop_action = MoveUntil((0, -30), duration(0.3))
                drop_action.apply(self.enemies, tag="drop")
        
        # Create continuous horizontal movement with boundary detection
        bounds = (50, 0, 750, 600)  # left, bottom, right, top
        move_action = MoveUntil(
            (50, 0), 
            lambda: False,  # Move indefinitely
            bounds=bounds,
            boundary_behavior="bounce",
            on_boundary=on_boundary_hit
        )
        
        # Apply to enemies with global management
        move_action.apply(self.enemies, tag="formation_movement")
    
    def on_update(self, delta_time):
        # Single line handles all action updates
        Action.update_all(delta_time)
```
