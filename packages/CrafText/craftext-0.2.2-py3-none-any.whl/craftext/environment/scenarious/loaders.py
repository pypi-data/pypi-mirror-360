import os
import importlib
import flax.struct
import yaml

import pathlib
import inspect
import flax

import craftext.dataset

from craftext.environment.scenarious.checkers.target_state import TargetState
from .loader_utils import get_default_scenario_path
from enum import Enum
from typing import Generic, Optional, List

from dataclasses import field
from typing import TypeVar

from typing import Tuple, List

from dataclasses import dataclass
from abc import ABC, abstractmethod

CONFIG_DIR_NAME = "configs"

@flax.struct.dataclass
class ScenariousConfigBase:
    ...

@flax.struct.dataclass
class ScenariousConfig(ScenariousConfigBase):
    """
    Scenarios configuration structure
    
    
    :arg dataset_key: task type
    :type dataset_key: str
    
    :arg subset_key: task complexity and if `test` - paraphrases / items
    :type subset_key: str
    
    :arg base_environment: use `Classic` or not
    :type base_environment: str
    
    :arg use_parafrases: use `paraPhrases` in loading or not
    :type use_parafrases: str
    
    :arg test: is it `test` data or not
    :type test: str
    
    """ 
    dataset_key: str
    subset_key: str
    base_environment: str
    use_parafrases: str
    test: str
    

class ScenariousConfigLoader:
    @staticmethod
    def get_config_path(config_name: str) -> str:
        """
        search file if exist in root of module in `CONFIG_DIR_NAME`
        
        
        :param config_name: Name of the configuration file (without extension)
        :return: Full path to the configuration file

        """
        module = inspect.getmodule(craftext.dataset)
        
        assert module is not None, "craftext.dataset module is not available."
        
        print(module.__path__)
    
        module_path = pathlib.PurePath(module.__path__[0])
        
        config_path = module_path.joinpath(f'{CONFIG_DIR_NAME}/{config_name}.yaml')

        return config_path.as_posix()

    @staticmethod
    def load_config(config_name: str) -> ScenariousConfig:
        """
        Loads the configuration from a YAML file.
        
        
        :param config_name: Name of the configuration file (without extension)
        :type config_name: str
        
        
        :return: ScenariousConfig object with loaded parameters
        :rtype: ScenariousConfig
        """
        
        config_path = ScenariousConfigLoader.get_config_path(config_name)
        
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
            
        return ScenariousConfig(
            dataset_key      =config_data.get("dataset_key"),
            subset_key       =config_data.get("subset_key"),
            base_environment =config_data.get("base_environment"),
            use_parafrases   =config_data.get("use_parafrases", False),
            test             =config_data.get("test", False)
        )


class ScenarioFieldType(Enum):
    SINGLE_VALUE            = "single_value" # The base instruction (not copied)
    PARAPHRASE_LIST         = "paraphrase_list" # A list of paraphrases (added to the base instruction)
    REPEAT_WITH_PARAPHRASES = "repeat_with_paraphrases" # Repeated for each instruction and its paraphrases

SCENARIO_SCHEMA = {
    "instruction":              ScenarioFieldType.SINGLE_VALUE,  
    "instruction_paraphrases":  ScenarioFieldType.PARAPHRASE_LIST,  
    "scenario_checker":         ScenarioFieldType.REPEAT_WITH_PARAPHRASES,  
    "arguments":                ScenarioFieldType.REPEAT_WITH_PARAPHRASES,  
    "str_check_lambda":         ScenarioFieldType.REPEAT_WITH_PARAPHRASES  
}


class ScenariousDataBase(ABC):
    """
    Abstract base class for scenario data.
    This class defines the structure for scenario data, which includes instructions, paraphrases,
    scenario checkers, arguments, and string check lambdas.
    """
    ...
    
TScenarioData = TypeVar("TScenarioData", bound=ScenariousDataBase)
TScenarioConfig = TypeVar("TScenarioConfig", bound=ScenariousConfigBase)

@dataclass
class RawScenariousData(ScenariousDataBase): 
    instructions_list: List[str] = field(default_factory=list)
    instructions_paraphrases: List[List] = field(default_factory=list)
    scenarios_checker: List[int] = field(default_factory=list)
    arguments: List[TargetState] = field(default_factory=list)
    str_check_lambda: List[str] = field(default_factory=list)
    
    def add_scenario_item(self, 
                        instruction: str, 
                        instruction_paraphrases: List[Optional[str]], 
                        scenario_checker: int, 
                        arguments: TargetState,
                        str_check_lambda: str,
                        use_parafrases: str) -> None:
        """
        Adds a new scenario item to the raw scenario data.
            
            
        :param instruction: The main instruction string.
        :type instruction: str
        
        :param instruction_paraphrases: A tuple of paraphrased instructions.
        :type instruction_paraphrases: List[Optional[str]]
        
        :param scenario_checker: An integer representing the scenario checker.
        :type scenario_checker: int
        
        :param arguments: A TargetState object containing additional arguments.
        :type arguments: TargetState
        
        :param str_check_lambda: A string representing the lambda function for checking the scenario.
        :type str_check_lambda: str
        
        :param: A flag indicating whether to use paraphrases or not.
        :type: str
        """
        
        self.instructions_list.append(instruction)
        if use_parafrases:
            self.instructions_paraphrases.append(instruction_paraphrases)
        else:
            self.instructions_paraphrases.append([])
        self.scenarios_checker.append(scenario_checker)
        self.arguments.append(arguments)
        self.str_check_lambda.append(str_check_lambda)

class ScenariousLoaderBase(ABC, Generic[TScenarioConfig, TScenarioData]):
    """
    Abstract base class for loading scenario data.
    This class defines the interface for loading scenario data from various sources.
    """
    
    @staticmethod
    @abstractmethod
    def load_scenarios(config: TScenarioConfig) -> TScenarioData:
        """
        Loads scenarios based on the provided configuration.
            
            
        :param config: ScenariousConfig object containing configuration parameters.
        :type config: TScenarioConfig
        
        :return: List of TScenarioData objects representing the loaded scenarios.
        :rtype: TScenarioData
        """
        raise NotImplementedError("This method should be implemented in subclasses.")
    

class RawScenariousDataFromModuleLoader(ScenariousLoaderBase[ScenariousConfig, RawScenariousData]):
    """
    Concrete implementation of ScenariousLoaderBase for loading raw scenario data.
    This class loads scenarios from a predefined source and returns them as RawScenariousData objects.
    """
    @staticmethod
    # @overload
    def load_scenarios(scenarious_config: ScenariousConfig) -> RawScenariousData:
        """
        Loads scenarios based on the provided configuration.

        
        :param scenarious_config: ScenariousConfig object containing configuration parameters
        :type scenarious_config: ScenariousConfig
        
        :return: List of RawScenariousData objects representing the loaded scenarios.
        :rtype: RawScenariousData
        """
        
        
        scenarios = RawScenariousData()
        scenarios_dir = get_default_scenario_path()
    
        module = "test" if scenarious_config.test else "instructions"
        mode = scenarious_config.dataset_key
        data_key = scenarious_config.subset_key
    
        if scenarios_dir is None:
            raise ValueError("Scenario path could not be determined.")

        for file in os.listdir(scenarios_dir):
            if mode in file:
                scenario_module_name = f"craftext.dataset.scenarious.{file}.{module}"
                scenario_module = importlib.import_module(scenario_module_name)
                
                if hasattr(scenario_module, data_key):
                    instructions_data = getattr(scenario_module, data_key)
                    print(f"Found {len(instructions_data)} scenarios in {file} for {mode} mode.")
                    for scenario_item in instructions_data:
                        
                        # Assuming scenario_item is a dictionary with the required keys
                        scenarios.add_scenario_item(
                            instructions_data[scenario_item].get('instruction', "None"),
                            instructions_data[scenario_item].get('instruction_paraphrases', []),
                            instructions_data[scenario_item].get("scenario_checker"),
                            instructions_data[scenario_item].get('arguments'),
                            instructions_data[scenario_item].get('str_check_lambda', 'None'),
                            use_parafrases=scenarious_config.use_parafrases
                        )
                        # If you want to use the raw item structure, uncomment the next line
                        # print(f"Added scenario item: {scenarios.arguments[45]}")
        return scenarios

