import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow as gw
import random
import time
import game_utils
import re
import threading

from StateMachine import StateMachine
from automug import auto_music

running = False
def main():
    # cv2.namedWindow("Game Window")
    # def mouse_callback(event, x, y, flags, param):
    #     if event == cv2.EVENT_LBUTTONDOWN:
    #         print("Clicked at position:", x, y)
    # cv2.setMouseCallback("Game Window", mouse_callback)
    global running
    game_window_title = 'HeavenBurnsRed'



    # 创建状态机的实例
    state_machine = StateMachine()
    state_machine.__init__()
    state_machine.transition("auto_music")
    while running:
        # 获取当前的状态
        current_state = state_machine.get_state()
        if current_state == "init":
            # 执行init状态的操作
            game_frame = game_utils.capture_game_window(game_window_title)
            if game_frame is not None:
                game_utils.remember_characters(game_frame)
                #state_machine.transition("recognize")
            else:
                break
        elif current_state == "recognize":
            # 执行recognize状态的操作
            game_frame = game_utils.capture_game_window(game_window_title)
            if game_frame is not None:
                game_utils.recognize_and_click_character(game_frame)
                text_x, text_y, text_width, text_height = 558, 204, 600, 70
                japanese_text = game_utils.recognize_text(game_frame, text_x, text_y, text_width, text_height, lang="jpn")
                print(japanese_text)
            else:
                break
        elif current_state == "auto_music":
            game_frame = game_utils.capture_game_window(game_window_title)
            if game_frame is not None:
                auto_music(game_frame)
            else:
                break
        else:
            print("Unknown state")
        #调试窗口
        # if game_frame is not None:
        #     # 调整输出窗口的大小为原来的一半
        #     scaled_frame = cv2.resize(game_frame, (game_frame.shape[1] // 2, game_frame.shape[0] // 2))
        #
        #     # 在窗口中显示缩放后的画面
        #     cv2.imshow("Game Window", scaled_frame)
        #
        #     # 移动输出窗口到屏幕左上角
        #     cv2.moveWindow("Game Window", 0, 0)
        # 检查是否退出
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
def start_program():
    global running  # 使用全局的 running 变量
    running = True
    thread = threading.Thread(target=main)
    thread.start()

def stop_program():
    global running  # 使用全局的 running 变量
    running = False  # 设置 running 为 False 来结束 main() 函数