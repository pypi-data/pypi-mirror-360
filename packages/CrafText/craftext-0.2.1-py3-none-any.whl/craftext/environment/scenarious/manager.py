import numpy as np
from numpy.typing import NDArray

from abc import ABC
from typing import TypeVar, List, Generic

import os

import jax
import jax.numpy as jnp
from dataclasses import dataclass, field

from typing import List, Tuple
from .loaders import get_default_scenario_path
from .loaders import ScenariousConfigLoader, ScenariousDataBase, RawScenariousData, RawScenariousDataFromModuleLoader, ScenariousConfigBase, ScenariousLoaderBase
from ..scenarious.checkers.target_state import TargetState
from ..encoders.craftext_base_model_encoder import BaseEncodeModel


import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)



@dataclass
class ScenariousData(ScenariousDataBase):
    instructions_list:      List[str] = field(default_factory=list)
    scenario_checker:       List[int] = field(default_factory=list)  # Assuming scenario_checker is a list of integers
    arguments:              List[TargetState] = field(default_factory=list)  # Assuming TargetState is a class that can be used in a list
    str_check_lambda_list:  List[str] = field(default_factory=list)  # Assuming str_check_lambda_list is a list of strings
    indices_list:           List[int] = field(default_factory=list)  # Assuming indices_list is a list of integers
    scenario_names:         List[str] = field(default_factory=list)  # Assuming scenario_names is a list of strings
    embeddings_list:        List[NDArray] = field(default_factory=list)  # Assuming embeddings_list is a list of NumPy arrays


@dataclass
class ScenarioDataJAX(ScenariousDataBase):
    embeddings_list:        jax.Array = field(default_factory=lambda: jnp.zeros((0, 0)))  # Placeholder for embeddings, shape will be set later
    scenario_checker:       jax.Array = field(default_factory=lambda: jnp.zeros(0))  # Placeholder for scenario_checker, shape will be set later
    arguments:              TargetState = field(default_factory=TargetState) # Assuming TargetState is compatible with JAX arrays

TScenarioDataFrom = TypeVar('TScenarioDataFrom', bound=ScenariousDataBase)
TScenarioDataTo = TypeVar('TScenarioDataTo', bound=ScenariousDataBase)


class ScenariousDataBseTransformer(ABC, Generic[TScenarioDataFrom, TScenarioDataTo]):

    @staticmethod
    def transform_scenario_data(scenario_data: TScenarioDataFrom) -> TScenarioDataTo:
        """
        Transforms the scenario data to a specific format.
        This method should be implemented in subclasses.
        
        :param scenario_data: The raw scenario data to be transformed.
        :type scenario_data: TScenarioDataFrom
         
        :return: Transformed scenario data in the desired format.
        :rtype: TScenarioDataTo
        """
        raise NotImplementedError("This method should be implemented in subclasses.")   

class ScenariousDataTransformer(ScenariousDataBseTransformer[RawScenariousData, ScenariousData]):
    

    @staticmethod
    def transform_scenario_data(scenario_data: RawScenariousData) -> ScenariousData:
        """
        Processes raw scenario data into a structured format.
        This method takes raw scenario data and transforms it into a structured format suitable for further processing.
        
        :param scenario_data: The raw scenario data to be transformed.
        :type scenario_data: RawScenariousData
         
        :return: Transformed scenario data in the desired format.
        :rtype: ScenariousData
        """

        data = ScenariousData(
            instructions_list = [],
            indices_list = [],
            arguments = [],
            scenario_checker = [],
            str_check_lambda_list = [],
            scenario_names=[],
            embeddings_list=[],
        )
        for i, instruction in enumerate(scenario_data.instructions_list):
            num_repeat = 1 + len(scenario_data.instructions_paraphrases[i])
            
            data.instructions_list.append(instruction)
            data.instructions_list.extend(scenario_data.instructions_paraphrases[i])
            
            data.indices_list.extend([i for _ in range(num_repeat)])
            
            data.arguments.extend([scenario_data.arguments[i] for _ in range(num_repeat)])
            
            data.scenario_checker.extend([scenario_data.scenarios_checker[i] for _ in range(num_repeat)])
            
            data.str_check_lambda_list.extend([scenario_data.str_check_lambda[i] for _ in range(num_repeat)])
            
            data.scenario_names.extend([f"Scenario_{i}" for _ in range(num_repeat)])
        # print(*data.arguments, sep="\n")
        data.embeddings_list = [np.zeros(0) for _ in range(len(data.instructions_list))]  # Placeholder for embeddings
        return data
    

    
   

class JaxScenariousTransformer(ScenariousDataBseTransformer[ScenariousData, ScenarioDataJAX]):
    """
    Transforms scenario data to JAX-compatible structures.
    This class converts the scenario data from a standard format to a format suitable for JAX operations.
    """
    
    @staticmethod
    def transform_scenario_data(scenario_data: ScenariousData) -> ScenarioDataJAX:
        """
        Converts scenario data to JAX-compatible structures.
        
        :param scenario_data: The raw scenario data to be transformed.
        :type scenario_data: ScenariousData
         
        :return: Transformed scenario data in the desired format.
        :rtype: ScenarioDataJAX
        """
        embeddings_jax = jnp.array(scenario_data.embeddings_list)
        scenario_checker_jax = jnp.array(scenario_data.scenario_checker)

        return ScenarioDataJAX(
            embeddings_list=embeddings_jax,
            scenario_checker=scenario_checker_jax,
            arguments=TargetState.stack(scenario_data.arguments)
        )   

class ScenariousManager:
    """
    Manages scenarios for the CrafText environment.
    This class initializes the scenario data, encodes instructions, and provides access to processed scenarios.
    It uses an encoding model to transform instructions into embeddings and prepares the scenario data for use in the environment.
    """

    def __init__(
            self, 
            encode_model: BaseEncodeModel, 
            config_name: str = 'None', 
            use_plans: bool = False
        ) -> None: 
        
        """
        Initializes the CrafTextScenarios with an EncodeModel and scenario configuration.
        
        :param encode_model: An instance of BaseEncodeModel used for encoding instructions.
        :type encode_model: BaseEncodeModel
        
        :param config_name: The name of the configuration to load scenarios from.
        :type config_name: str
        
        :param use_plans: A boolean indicating whether to use predefined plans for instructions.
        :type use_plans: bool
        
        :param plans_path: Path to the file containing action plans for instructions.
        :type plans_path: bool
        """
        self.encode_model = encode_model
        
        self.config = ScenariousConfigLoader.load_config(config_name)
        self.use_paraphrases = self.config.use_parafrases
        
        self.environment_key = 0 if "Classic" in self.config.base_environment else 1
        
        self.use_plans = use_plans
        self.instruction_to_update_file = 'None'
        
        self.all_scenario = RawScenariousData()
        self.scenario_data = ScenariousData()
        self.scenario_data_jax = ScenarioDataJAX()
        
    def load(self):
        """
        Loads scenarios and encodes instructions using the provided encoding model.
        This method initializes the scenario data, encodes the instructions, and prepares the data for use in the environment.
        It retrieves the raw scenario data, transforms it into a structured format, and encodes the instructions into embeddings.
        """
        
        logger.info("Loading scenarios...")
        
        self.all_scenario = RawScenariousDataFromModuleLoader.load_scenarios(self.config)
        
        # note: self.scenario_data.embedings_list - zero_initialized        
        self.scenario_data = ScenariousDataTransformer.transform_scenario_data(self.all_scenario)
        
        # encode the instructions use encode_model
        logger.info("Encoding instructions...")

        embeddings_list, _, _ = self.encode_instructions(self.scenario_data.instructions_list)
        self.scenario_data.embeddings_list = embeddings_list

        logger.info(f"Encoded {len(self.scenario_data.embeddings_list)} instructions.")
        
        # need JAX conversions
        self.scenario_data_jax = JaxScenariousTransformer.transform_scenario_data(self.scenario_data)
        
        self.n_instructions = 0
        logger.info(f"Final number of instructions: {len(self.scenario_data_jax.embeddings_list)}")    

    @property
    def initial_instruction(self):
        """
        Generates the default encoded instruction for initializing network parameters.


        :return: A NumPy array containing the encoded instruction.
        :rtype: NDArray
        """
        return self.encode(['None'])[:1]
    

    def castom_initial_instruction(self, instruction: str):
        """
        Generates the default encoded instruction for initializing network parameters.
        
        :param instruction: A string representing the custom instruction to be encoded.
        :type param: str
        
        :return: A NumPy array containing the encoded instruction.
        :rtype: NDArray        
        """
        return self.encode([instruction])[:1]

    @property
    def get_scenarios(self):
        """
        Retrieves the processed scenario data.
        
        :return: ScenariousData structure
        :rtype: ScenariousData
        """
        return self.scenario_data

    def encode(self, instructions: List[str]):
        """
        Encodes an instruction using the provided encoding model.
        
        :param instructions: List of instruction strings to be encoded.
        :type instructions: List[str]

        :return: A NumPy array containing the encoded instruction.
        :rtype: NDArray
        """
        return self.encode_model.encode(instructions)

    def encode_instructions(self, instructions: List[str]) -> Tuple[NDArray, List[str], int]:
        """
        Encodes a list of instructions using the encoding model.
        
        
        :param instructions: List of instruction strings to be encoded.
        :type instructions: List[str]
        
        :return:
        
        :param encoded_instructions: NDArray of embedings encoded instructions
        :type encoded_instructions: NDArray

        :param original_instructions: original instruction from params
        :type original_instructions: List[str]
        
        :param num_variant: paraphrases variants of instrctuction
        :type num_variant: int
    
        :rtype: Tuple[NDArray, List[str], int]
        
        """
        encoded_instructions = self.encode(instructions)
        
        # There is possible, than self.encode_model retunrn different version of instructions-plans and related embeddings
        num_variants = len(encoded_instructions) // len(instructions)
       
        assert len(encoded_instructions) == len(instructions) * num_variants, \
            f"Unexpected size of encoded instructions ({len(encoded_instructions)} vs {len(instructions)}). Ensure encode_model is consistent."

        return encoded_instructions, instructions, num_variants

@dataclass(frozen=True)
class PlanConfig(ScenariousConfigBase):
    """
    Class representing the configuration for a plan.
    This class is used to define the structure of a plan configuration.
    """
    # Define the attributes and methods for PlanCofig as needed
    config_path: str = os.path.join(get_default_scenario_path(), 'extra_files', 'easy_gpt4_action_plans.json')
    
import json

class RawPlansScenarious(ScenariousDataBase):
    """
    Class representing raw plans scenarios.
    This class extends the ScenarioDataBase and provides a structure for raw plans scenarios.
    """
    plans: dict[str, List[str]] = field(default_factory=dict)
    
class RawPlansScenariousLoader(ScenariousLoaderBase[PlanConfig, RawPlansScenarious]):
    """
    Concrete implementation of ScenariousLoaderBase for loading raw plans scenarios.
    This class loads scenarios from a predefined source and  them as RawPlansScenarious objects.
    """
    
    @staticmethod
    def load_scenarios(scenarious_config: PlanConfig) -> RawPlansScenarious:
        """
        Loads raw plans scenarios based on the provided configuration.
        
        :param scenarious_config: object containing configuration parameters.
        :type scenarious_config: PlanConfig
        
        :returns: object containing the loaded plans scenarios.
        :rtype: RawPlansScenarious
        """
        with open(scenarious_config.config_path, 'r', encoding='utf-8') as f:
            plans_data = json.load(f)
        
        raw_plans_scenarios = RawPlansScenarious()
        raw_plans_scenarios.plans = plans_data
        
        return raw_plans_scenarios


class ScenariousManagerWithPlans(ScenariousManager):
    """
    Manages scenarios for the CrafText environment with predefined plans.
    This class extends ScenariousManager to include functionality for using predefined plans in scenarios.
    """

    def __init__(self, encode_model: BaseEncodeModel, config_name: str = 'None', plan_config_name: str = 'None') -> None:
        """
        Initializes the CrafTextScenarios with an EncodeModel and scenario configuration.
        
        
        :param encode_model: An instance of BaseEncodeModel used for encoding instructions.
        :type encode_model: BaseEncodeModel
        
        :param config_name: The name of the configuration to load scenarios from.
        :type config_name: str
        """
        super().__init__(encode_model, config_name=config_name, use_plans=True) 
        # assert not self.config.use_parafrases, "ScenariousManagerWithPlans does not support paraphrases. Set use_parafrases to False in the configuration."
        
        self.plan_config_name = PlanConfig() if plan_config_name == 'None' else PlanConfig(config_path=plan_config_name)
    
    def load(self):
        """
        Loads scenarios and encodes instructions using predefined plans.
        This method overrides the load method of the parent class to include functionality for using predefined plans.
        """ 
        
        self.all_scenario = RawScenariousDataFromModuleLoader.load_scenarios(self.config)
        
        # note: self.scenario_data.embedings_list - zero_initialized        
        self.scenario_data = ScenariousDataTransformer.transform_scenario_data(self.all_scenario)
        
        logger.info(f"loaded instruction count - {len(self.scenario_data.instructions_list)}")
        
        self.raw_plans = RawPlansScenariousLoader.load_scenarios(self.plan_config_name)
        logger.info(f'loaded raw plans count - {len(self.raw_plans.plans.values())}')
        
        skipped_plans = 0
        for plan in self.raw_plans.plans:
            if plan in self.scenario_data.instructions_list:
                idx = self.scenario_data.instructions_list.index(plan)
                # print(self.scenario_data.instructions_list[idx])
                self.scenario_data.instructions_list[idx] = self.raw_plans.plans[plan]
            else:
                skipped_plans += 1
                # logger.warning(f"Plan '{plan}' not found in scenario instructions. Skipping update.")
        logger.info(f"Skipped {skipped_plans} plans that were not found in the scenario instructions.")
        # encode the instructions use encode_model

        logger.info(f"loaded instruction count rewrite as plans- {len(self.scenario_data.instructions_list)}")

        logger.info("Encoding instructions...")

        embeddings_list, _, _ = self.encode_instructions(self.scenario_data.instructions_list)
        self.scenario_data.embeddings_list = embeddings_list
        
        # need JAX conversions
        self.scenario_data_jax = JaxScenariousTransformer.transform_scenario_data(self.scenario_data)
        
        self.n_instructions = 0
        logger.info(f"Final number of embeddings logits: {self.scenario_data_jax.embeddings_list.shape}")    
          



    # def _load_action_plans(self, instructions_list: List[str]) -> List[str]:
    #     """
    #     Loads action plans from a predefined file and updates instructions if applicable.
    #     """
    #     with open(self.instruction_to_update_file, 'r', encoding='utf-8') as f:
    #         action_plans = json.load(f)
    #     # print("Action_plans: \n",action_plans)
    #     # print("_______--")
    #     updated_instructions = [action_plans.get(instr, "none") for instr in instructions_list]
    #     logger.info("Using preloaded plans in craftext_scenarios.py")
    #     logger.info("Encoding instructions...")        
    #     return updated_instructions

    
    # def _pairwise_with_embeddings(self,
    #                               encode_instructions,
    #                               batch_instructions: List[str], 
    #                               batch_indices: List[int], 
    #                               checkers_data_dict: dict[str, Any], 
    #                               base_idx: int
    #                               ) -> dict[str, Any]:
    #     """
    #     Encodes a batch of instructions and processes extracted data.
    #     """
    #     old_instructions = batch_instructions
    #     encoded_instructions, batch_instructions, num_variants = encode_instructions(batch_instructions)
    #     # print("encode instr", encoded_instructions)
    #     batch_results: dict = {
    #         "instructions": [],
    #         "indices": [],
    #         "embeddings": [],
    #         "o_instructions": [],
    #         "checkers_data": {key: [] for key in checkers_data_dict.keys()}
    #     }

    #     for j, instruction in enumerate(old_instructions):
    #         for k in range(num_variants):
    #             variant_index = j * num_variants + k
    #             batch_results["indices"].append(batch_indices[j])
    #             batch_results["o_instructions"].append(instruction)
    #             batch_results["instructions"].append(batch_instructions[variant_index])
    #             batch_results["embeddings"].append(encoded_instructions[variant_index])

    #             for field in checkers_data_dict.keys():
    #                 batch_results["checkers_data"][field].append(checkers_data_dict[field][base_idx + j])

    #     return batch_results
    
from ..encoders.craftext_distilbert_model_encoder import DistilBertEncode
    
if __name__ == "__main__":
    # Example usage
    
    data = ScenariousManagerWithPlans(
        encode_model=DistilBertEncode(),  # Replace with actual model instance
        config_name='eazy_train',  # Replace with actual config name
        # plan_config_name='default_plan_config'  # Replace with actual plan config name
    )
    data.load()
    # print(len(data.scenario_data_jax.embeddings_list))  # Access the JAX-compatible embeddings list