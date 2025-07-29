import jax
import jax.numpy as jnp
from typing import Union
from craftext.environment.states.state import GameData
from craftext.environment.states.state_classic import GameDataClassic

from craftext.environment.scenarious.checkers.target_state import Achievements, AchievementState

def checker_achievments(game_data: Union[GameDataClassic, GameData],  target_state: Achievements) -> jax.Array:
    
    achievement_mask  = target_state.achievement_mask
    

    return conditional_achievments(game_data, achievement_mask)

def conditional_achievments(gd: Union[GameDataClassic, GameData], achievement_mask):

    mask = jnp.array(achievement_mask, dtype=jnp.int32)

    current_state      = gd.states[0]
    state_achievements = current_state.achievements.achievements  # jnp.array of 0/1

    # False Positive with achievements complete and state not need it
    must_achieve     = (mask == AchievementState.NEED_TO_ACHIEVE) & (state_achievements == 0)
    
    # False Positive with achievements complete and state need it
    must_not_achieve = (mask == AchievementState.AVOID_TO_ACHIEVE) & (state_achievements == 1)

    # any == False
    fail_condition = jnp.any(must_achieve) | jnp.any(must_not_achieve)

    return jnp.logical_not(fail_condition)


