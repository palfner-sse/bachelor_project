from tkinter import END

from python.mas.state import MasState


def orchestrator(state: MasState):
    pass


def orchestrator_path(state: MasState):
    pass


orchestrator_path_map = {"model_diff_change_analyzer": "model_diff_change_analyzer",
                         "code_change_planer": "code_change_planer", "code_changer": "code_changer", "finish": END}
