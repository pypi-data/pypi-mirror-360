from .manager import ScenariousManager, ScenariousManagerWithPlans, PlanConfig

def create_scenarios_with_dataset(use_plans: bool) -> type[ScenariousManager]:
    """
        Factory function return custom scenarious class
        
        
        :params: use_plan
        :type use_plan: bool 
        
        :return: ScenarioManager Class
        :rtype: ScenariousManager
    """
    if use_plans:
        planConfig = PlanConfig()
        class CustomScenatiousManagerWithPlan(ScenariousManagerWithPlans):
            def __init__(self, encode_model, config_name = 'None'):
                super().__init__(encode_model, config_name, plan_config_name=planConfig.config_path)
        return CustomScenatiousManagerWithPlan
    else:
        return ScenariousManager
