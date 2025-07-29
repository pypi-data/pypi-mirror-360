from typing import Tuple, Union

import jax
from jax.typing import ArrayLike
import jax.numpy as jnp
from jax import lax

from flax import struct

from craftax.craftax.craftax_state import EnvState, EnvParams
from craftax.craftax.constants import Action

from craftax.craftax_env import (
    CraftaxPixelsEnv,
    CraftaxSymbolicEnv,
    CraftaxClassicPixelsEnv,
    CraftaxClassicSymbolicEnv
)

from gymnax.environments.environment import Environment 

from craftext.environment.encoders.craftext_base_model_encoder import EncodeForm, BaseEncodeModel
from craftext.environment.encoders.craftext_distilbert_model_encoder import DistilBertEncode

from craftext.environment.scenarious.manager import ScenariousManager

from craftext.environment.craftext_constants import Scenarios
from craftext.environment.states.state import GameData
from craftext.environment.states.state_classic import GameDataClassic

from craftext.environment.scenarious.checkers.achievments      import checker_achievments
from craftext.environment.scenarious.checkers.time_constrained import checker_time_placement
from craftext.environment.scenarious.checkers.building_star    import checker_star
from craftext.environment.scenarious.checkers.building_line    import checker_line
from craftext.environment.scenarious.checkers.building_square  import checker_square
from craftext.environment.scenarious.checkers.conditional      import checker_conditional_placement
from craftext.environment.scenarious.checkers.relevant         import cheker_localization
from craftext.environment.scenarious.checkers.target_state     import TargetState


import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

@struct.dataclass
class TextEnvState:
    env_state: EnvState
    timestep: int
    instruction: jax.Array
    idx: int
    success_rate: float
    total_success_rate: float
    environment_key: int
    rng: ArrayLike
    instruction_done: bool
    checker_id: int
    

def generic_check(
    game_data: Union[GameData, GameDataClassic],
    target_state: TargetState,        
    idx: int
) -> ArrayLike:
    
    """
    Select and execute one of several check functions based on the given index.

    Parameters
    ----------
    game_data : Union[GameData, GameDataClassic]
        The object containing the current game world state and environment parameters.
    target_state : TargetState
        A data structure specifying the target conditions (achievements, placements,
        building shapes, timing, etc.) to be checked.
    idx : int
        An integer index selecting which checker to invoke:
            0 — checker_acvievments (achievements)
            1 — checker_conditional_placement (conditional placement)
            2 — cheker_localization (localization)
            3 — checker_line (building a line)
            4 — checker_square (building a square)
            5 — checker_star (building a star)
            6 — checker_time_placement (timed placement)
            7 — checker_acvievments (achievements again)

    Returns
    -------
    jnp.ndarray
        A JAX array (boolean or float) indicating whether the selected target
        conditions are satisfied.
    """

    def ca(ts: TargetState):   return checker_achievments(game_data, ts.achievements)
    def cp(ts: TargetState):   return checker_conditional_placement(game_data, ts.conditional_placing)
    def port(ts: TargetState): return cheker_localization(game_data, ts.Localization_placing)
    def ilf(ts: TargetState):  return checker_line(game_data, ts.building_line)
    def isf(ts: TargetState):  return checker_square(game_data, ts.building_square)
    def icf(ts: TargetState):  return checker_star(game_data, ts.building_star)
    def atp(ts: TargetState):  return checker_time_placement(game_data, ts.time_placement)

    fns = (ca, cp, port, ilf, isf, icf, atp, ca)

    return lax.switch(idx, fns, target_state)


EnvT = Union[CraftaxClassicPixelsEnv, CraftaxClassicSymbolicEnv]

class InstructionWrapper(Environment):
    """
        A wrapper for Craftax environments that integrates scenario management and instruction handling.
        This class initializes the environment with a scenario handler and an encoding model, allowing for
        the selection of instructions based on the scenario data. It provides methods to reset the environment
        and step through it, while managing the state and success rates of the instructions.
        The wrapper supports both pixel and symbolic environments, and can handle different encoding forms
        such as embeddings or tokens.
        Attributes:
            - env: The Craftax environment to wrap.
            - config_name: The name of the configuration for scenarios.
            - scenario_handler: An instance of ScenariousManager to handle scenarios.
            - encode_model: An instance of BaseEncodeModel for encoding instructions.
            - encode_form: The form of encoding to use (EMBEDDING or TOKEN).
            - encoded_instruction: The encoded instruction embeddings or tokens.
            - scenario_arguments: The arguments for the scenarios.
            - steps: The number of steps taken in the environment.
            - environment_key: The key representing the type of environment (1 for Craftax, 2 for Craftax Classic).
            - StateStructure: The structure of the state, either GameData or GameDataClassic based on the environment key.
            - n_instructions: The number of instructions available in the scenario data.
        Methods:
            - __init__: Initializes the InstructionWrapper with the environment and scenario handler.
            - reset: Resets the environment, selecting a random instruction embedding or token for the new episode.
            - step: Takes a step in the environment, checking if the instruction is done and updating success rates and rewards.
            
    """
    
    def __init__(self, 
                 env: EnvT,
                 config_name: str = 'None', 
                 scenario_handler_class: type[ScenariousManager] = ScenariousManager,
                 encode_model_class: type[BaseEncodeModel] = DistilBertEncode, 
                 encode_form: EncodeForm = EncodeForm.EMBEDDING
                 ) -> None:
        """
        Initializes the InstructionWrapper with the environment, creating EncodeModel and CrafTextScenarios.
            
        :params env: The environment to wrap.
        :type env: EnvT
        
        :params config_name: Optional configuration name for scenarios.
        :type config_name: Optioan[str]
        
        :params encode_model_class: A class for the encoding model. Defaults to DistilBertEncode.
        :type encode_model_class: type[ScenariousManager]
        
        :params encode_form: The form of encoding (EMBEDDING or TOKEN). Defaults to EMBEDDING.
        :type encode_form: type[BaseEncodeModel]
        
        """
        self.env = env
        
        self.encode_model = encode_model_class(form_to_use=encode_form)

        # Initialize the scenario handler with the encoding model
        self.scenario_handler = scenario_handler_class(self.encode_model, config_name)
        self.scenario_handler.load()
        self.encoded_instruction = self.scenario_handler.scenario_data_jax.embeddings_list
        self.scenario_arguments = self.scenario_handler.scenario_data_jax.arguments


        self.encoded_instruction = self.scenario_handler.initial_instruction
        
        self.steps = 0

        # Determine the environment key and state structure
        self.environment_key = self.scenario_handler.environment_key
        self.StateStructure = GameData if self.environment_key == 1 else GameDataClassic

        logging.info(f"Initialized Instruction Wrapper with environment key: {'GameData' if self.environment_key == 1 else 'GameDataClassic'}")

        self.n_instructions = len(self.scenario_handler.scenario_data.instructions_list)

    def reset(self, seed: ArrayLike, env_params: EnvParams, instruction_idx: ArrayLike = -1) -> Tuple[jax.Array, TextEnvState]:
        """
        Resets the environment and selects a random instruction embedding or token for the new episode.
        
        
        :param seed: Random seed for reproducibility.
        :type seed: ArrayLike
        
        :param env_params: Environment parameters for the reset.
        :type env_params: EnvParams
        
        :param instruction_idx: Optional index of the instruction to use. If -1, a random instruction is selected.
        :type instruction_idx: ArrayLike
        
        
        :return:
            Tuple[obs, state]
            
            - obs: The initial observation from the environment.
        
            - state: The initial state of the environment, including the selected instruction embedding/token.
            
        :rtype: Tuple[jax.Array, TextEnvState]
        """
        # Reset CrafTax enviroment
        # ---------------------------------------------------------------------------------- #
        
        obs, state = self.env.reset(seed, env_params)
        
        # ---------------------------------------------------------------------------------- #
        
        # Select random instruction in dataset
        # ---------------------------------------------------------------------------------- #
        idx = jax.lax.cond(
            instruction_idx == -1, 
            lambda: jax.random.randint(seed, shape=(), minval=0, maxval=len(self.scenario_handler.scenario_data_jax.embeddings_list)),
            lambda: instruction_idx
        )
        
        instructions_emb = self.scenario_handler.scenario_data_jax.embeddings_list[idx]
        checker_id: int = self.scenario_handler.scenario_data_jax.scenario_checker[idx]
        

        # ---------------------------------------------------------------------------------- #
        
        # Initialize the state with the selected instruction embedding/token and set success rates to zero
        state = TextEnvState(
            env_state=state,
            timestep=state.timestep,
            instruction=instructions_emb,
            idx=idx,
            environment_key=self.environment_key,
            success_rate=0.0,
            total_success_rate=0.0,
            rng=seed,
            instruction_done=False,
            checker_id=checker_id
        )
        return obs, state
    
    def step(self, seed: ArrayLike, env_state: TextEnvState, action: Action, env_params: EnvParams) -> tuple[jax.Array, TextEnvState, float, bool, dict]:
        """
        Takes a step in the environment, checking if the instruction is done, updating success rate and rewards.
            
        
        :params seed: Random seed for reproducibility.
        :type seed: ArrayLike
            
        :params env_state: The current state of the environment, including the instruction and success rates.
        :type env_state: TextEnvState
        
        :params action: The action to take in the environment.
        :type action: Action
        
        :params env_params: Environment parameters for the step.
        :type env_params: EnvParams
    
        :return:    
            - obs: The observation after taking the step.
        
            - state: The updated state of the environment, including success rates and instruction completion.
        
            - reward: The reward received for the action taken.
        
            - done: A boolean indicating if the episode is done.
        
            - info: Additional information about the step, including success rates and checker ID.
        :rtype:
            tuple[jax.Array, TextEnvState, float, bool, dict]
            
        """
        obs, state, reward, done, info = self.env.step(seed, env_state.env_state, action, env_params)
        # Obtain the game data vector for the current state and check instruction completion
        # ---------------------------------------------------------------------------------- #
        
        game_data_vector = self.StateStructure.from_state(env_state.env_state, state, action)
                    
        ts = self.scenario_arguments.select(env_state.idx)
        #
        instruction_done: bool = generic_check(game_data_vector, ts, env_state.checker_id)
        
        # If EXPLORE mode - give craftax reward
        reward = lax.cond(
                    env_state.checker_id != Scenarios.EXPLORE,
                    lambda r: r / 50,
                    lambda r: r,
                    reward
                )

        reward = jax.lax.cond(instruction_done, lambda _: reward + 1, lambda _: reward, operand=None)
        
        # Combine Game episode ends and complete instruction
        done = instruction_done | done
   
        # --------------------------------------------------------------------------------- #
        
        new_episode_sr = env_state.success_rate + jnp.float32(instruction_done)

        # Update state with the new success rates
        updated_state = TextEnvState(
            env_state=state,
            timestep=state.timestep,
            instruction=env_state.instruction,
            idx=env_state.idx,
            environment_key=env_state.environment_key,
            success_rate=new_episode_sr * (1 - done),
            total_success_rate=env_state.total_success_rate * (1 - done) + new_episode_sr * done,
            rng=env_state.rng,
            instruction_done=instruction_done,
            checker_id=env_state.checker_id
        )
        
        # Update step information in info dictionary
        info.update({"SR": updated_state.total_success_rate, "steps": self.steps})
        self.steps += 1
        return obs, updated_state, reward, done, info



if __name__ == "__main__":
    
    from craftax.craftax_env import make_craftax_env_from_name
    from craftax.craftax_classic.envs.craftax_pixels_env import CraftaxClassicPixelsEnv 
    # Example usage of the InstructionWrapper
    env: CraftaxClassicPixelsEnv = make_craftax_env_from_name("Craftax-Classic-Pixels-v1", auto_reset=False)  # Replace with actual environment initialization
    wrapper = InstructionWrapper(env, 
                                 config_name='easy_train', 
                                 scenario_handler_class=ScenariousManager, 
                                 encode_model_class=DistilBertEncode, 
                                 encode_form=EncodeForm.EMBEDDING
                                )
    # Example seed and environment parameters
    
    seed = jax.random.PRNGKey(0)
    env_params = env.default_params  # Replace with actual environment parameters
    obs, state = wrapper.reset(seed, env_params)
    
    print("Initial Observation:", obs)
    print("Initial State:", state)
    
    action = jnp.array(0, dtype=jnp.int32)  # Replace with actual action
    obs, state, reward, done, info = wrapper.step(seed, state, action, env_params)
