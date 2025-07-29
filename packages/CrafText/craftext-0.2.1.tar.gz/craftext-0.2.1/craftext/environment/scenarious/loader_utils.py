
import craftext.dataset
from pathlib import Path


def get_default_scenario_path() -> str:
    """Gets the default absolute path to the scenarios directory based on module installation.
    
    
    :return: Path to default scenarious location based on craftext.dataset module
    :rtype: str
    """
    
    assert craftext.dataset is not None, "craftext.dataset module is not available."
    
    module_path = craftext.dataset.__path__[0]
    if not module_path:
        raise ValueError("Module path for craftext.dataset could not be determined.")
    
    module_path = Path(module_path)  # Ensure the path is absolute and resolved
    # print(module_path)
    return module_path.joinpath('scenarious/').resolve().as_posix()  # Ensure the path is absolute and resolved

