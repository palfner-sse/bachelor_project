from langgraph.graph import StateGraph

from python.mas.agents.code_change_plan_validator import code_change_plan_validator, code_change_plan_validator_routing, \
    code_change_plan_validator_path_map
from python.mas.agents.code_change_planer import code_change_planer
from python.mas.agents.code_change_validator import code_change_validator, code_change_validator_routing, \
    code_change_validator_path_map
from python.mas.agents.code_changer import code_changer
from python.mas.agents.model_diff_change_analysis_validator import model_diff_change_analysis_validator, \
    model_diff_change_analysis_validator_router, model_diff_change_analysis_validator_path_map
from python.mas.agents.model_diff_change_analyzer import model_diff_change_analyzer
from python.mas.agents.orchestrator import orchestrator, orchestrator_path, orchestrator_path_map
from python.mas.state import State

# TODO make the agents only use a provided path

def create_graph():
    mas_graph = StateGraph(State)

    mas_graph.add_nodes("code_change_plan_validator", code_change_plan_validator)
    mas_graph.add_nodes("code_change_planer", code_change_planer)
    mas_graph.add_nodes("code_change_validator", code_change_validator)
    mas_graph.add_nodes("code_changer", code_changer)
    mas_graph.add_nodes("model_diff_change_analysis_validator", model_diff_change_analysis_validator)
    mas_graph.add_nodes("model_diff_change_analyzer", model_diff_change_analyzer)
    mas_graph.add_nodes("orchestrator", orchestrator)

    mas_graph.add_conditional_edges(source="orchestrator", path=orchestrator_path, path_map=orchestrator_path_map)
    mas_graph.add_conditional_edges(source="code_change_plan_validator", path=code_change_plan_validator_routing,
                                    path_map=code_change_plan_validator_path_map)
    mas_graph.add_conditional_edges(source="model_diff_change_analysis_validator",
                                    path=model_diff_change_analysis_validator_router,
                                    path_map=model_diff_change_analysis_validator_path_map)
    mas_graph.add_conditional_edges(source="code_change_validator", path=code_change_validator_routing,
                                    path_map=code_change_validator_path_map)

    mas_graph.add_edge(start_key="code_change_planer", end_key="code_change_plan_validator")
    mas_graph.add_edge(start_key="code_changer", end_key="code_change_validator")
    mas_graph.add_edge(start_key="model_diff_change_analyzer", end_key="model_diff_change_analysis_validator")

    return mas_graph.compile()


graph = create_graph()