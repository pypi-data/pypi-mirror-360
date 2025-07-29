from typing import Tuple, Literal

import jax.numpy as jnp
import jax.lax as lax
import jax

from flax.struct import dataclass

from craftext.environment.craftext_constants import BlockType
from craftext.environment.states.state import GameData
from craftext.environment.scenarious.checkers.target_state import TargetState

def transform_pattern(pattern: jax.Array, block_index: int, size: int) -> jax.Array:
    #TODO:
    # improve scalable pattern and transform it for current instructions
    
    #only pattern transform for block type
    return pattern * block_index

def get_pattern(pattern_type: jax.Array, block_index: int, size: int) -> jax.Array:
    return transform_pattern(pattern_type, block_index, size)

def check_pattern(sub_region: jax.Array, pattern: jax.Array) -> jax.Array:
    mask_indices = pattern > 0
    return (mask_indices == sub_region).all()

@dataclass
class Carry:
    region: jax.Array
    block_index: int
    region_size: int
    pattern: jax.Array

def scan_pattern_function(carry: Carry, x: jax.Array) -> Tuple[Carry, jax.Array]:
    position = x // carry.region_size, x % carry.region_size

    sub_region = lax.dynamic_slice(carry.region, position, carry.pattern.shape)
   
    if sub_region.shape[0] < carry.pattern.shape[0] or sub_region.shape[1] < carry.pattern.shape[1]:
        return carry, jnp.array(False)
     
    return carry, check_pattern(sub_region, carry.pattern)

def is_pattern_formed(game_data: GameData, target_state: TargetState) -> (jax.Array | Literal[False]):
    
   
    # Extract pattern parameters
    block_type    = target_state.unified_pattern_state.block_type
    pattern_type  = target_state.unified_pattern_state.pattern_type
    size          = target_state.unified_pattern_state.size
    radius        = target_state.unified_pattern_state.radius
    block_index   = block_type

    # Guard: missing game data or states
    if game_data is None or game_data.states is None:
        return False

    # Guard: missing map
    game_map = game_data.states[0].map.game_map
    if game_map is None:
        return False

    # Guard: missing player position
    player_position = game_data.states[0].variables.player_position
    if player_position is None:
        return False

    # Center coordinates
    x, y = player_position

    # Build the pattern kernel
    pattern = get_pattern(pattern_type, block_index, size)

    # Define slice size
    region_size = 2 * radius + 1

    # Extract the square region around the player
    region = lax.dynamic_slice(
        game_map,
        start_indices=(x - radius, y - radius),
        slice_sizes=(region_size, region_size)
    )

    # Flatten region indices for scanning
    indices = jnp.arange(region_size * region_size)

    # Prepare carry for the scan: includes region, block_index, region_size, and pattern
    carry = Carry(
        region=region,
        block_index=block_index,
        region_size=region_size,
        pattern=pattern
    )

    # Scan over every position, applying scan_pattern_function
    _, matches = lax.scan(scan_pattern_function, carry, indices)

    # If scan returned no matches array, treat as failure
    if matches is None:
        return False

    # Return True if any position matched the pattern
    return jnp.any(matches)