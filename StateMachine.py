
import game_utils

class StateMachine:
    def __init__(self):
        self.state = "init"
    def get_state(self):
        return  self.state
    def transition(self, new_state):
        self.state = new_state

    def init_state(self, frame):
        print("Running init state...")
        game_utils.remember_characters(frame)
        self.transition("play")

    def play_state(self, frame):
        print("Running play state...")