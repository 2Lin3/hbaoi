import cv2
import numpy as np
import pyautogui
import game_utils
import time
from directkeys import PressKey, ReleaseKey

# z轨道
points_z = [(90, 383), (264, 391), (369, 187), (292, 168)]
# x轨道
points_x = [(514, 200), (460, 401), (264, 391), (369, 187)]
# c轨道
points_c = [(514, 200), (460, 401), (630, 391), (638, 200)]
# v轨道
points_v = [(765, 206), (816, 400), (630, 391), (638, 200)]
# b轨道
points_b = [(765, 206), (816, 400), (995, 391), (899, 223)]
# n轨道
points_n = [(1008, 200), (1183, 390), (995, 391), (899, 223)]

# 是否正在长按
is_holding_list = [False] * 6

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Clicked at position:", x, y)
def auto_music(game_frame):
    keys_positions = [0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31]  # 对应 "z", "x", "c", "v", "b", "n"
    roi_coordinates = [(160, 730), (1400, 750), (1400, 230), (160, 240)]

    roi = game_utils.get_roi(game_frame, roi_coordinates)
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower_bound_keys = np.array([0, 0, 200])
    upper_bound_keys = np.array([180, 255, 255])
    mask_keys = cv2.inRange(hsv_roi, lower_bound_keys, upper_bound_keys)

    lower_bound_ribbon = np.array([90, 0, 140])
    upper_bound_ribbon = np.array([140, 110, 210])
    mask_ribbon = cv2.inRange(hsv_roi, lower_bound_ribbon, upper_bound_ribbon)

    final_mask = cv2.bitwise_or(mask_keys, mask_ribbon)
    gold_color = np.array([0, 215, 255])
    white_color = np.array([255, 255, 255])

    color_mask = np.zeros_like(roi)

    # 金色轮廓
    contours_list = [
        get_contours(color_mask, points, mask_keys, gold_color)
        for points in [points_z, points_x, points_c, points_v, points_b, points_n]
    ]

    # 白色轮廓
    contours_white_list = [
        get_contours(color_mask, points, mask_ribbon, white_color)
        for points in [points_z, points_x, points_c, points_v, points_b, points_n]
    ]

    roi_height, roi_width, _ = color_mask.shape

    # 设定阈值
    area_threshold = 2500

    # track_color_mask = np.zeros_like(roi)
    # mask = create_polygon_mask(track_color_mask, points_n)
    # mask_keys_track = cv2.bitwise_and(mask_ribbon, mask)
    # track_color_mask = np.zeros_like(track_color_mask)
    #
    # track_color_mask[mask_keys_track > 0] = white_color
    # roi[mask_ribbon > 0] = gold_color
    # cv2.namedWindow("Color Mask", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Color Mask", 400, 200)
    # cv2.imshow("Color Mask", track_color_mask)
    # cv2.moveWindow("Color Mask", 0, 0)
    # cv2.setMouseCallback("Color Mask", mouse_callback)

    # 遍历轮廓列表和键位列表
    for i, (contours_gold, contours_white, key_position, is_holding) in enumerate(
            zip(contours_list, contours_white_list, keys_positions, is_holding_list)):
        is_holding_new = process_contours(contours_gold, contours_white, roi_height, area_threshold, key_position,
                                          is_holding)
        is_holding_list[i] = is_holding_new  # 更新长按状态

    #print(is_holding_list)
    #b'nxxtime.sleep(0.01)



def get_triangle_mask(roi, vertices):
    mask = np.ones(roi.shape[:2], dtype=np.uint8) * 255

    vertices = np.array([vertices], dtype=np.int32)

    cv2.fillPoly(mask, vertices, 0)

    return mask

def create_polygon_mask(roi, points):
    mask = np.zeros(roi.shape[:2], dtype=np.uint8)

    points = np.array([points], dtype=np.int32)

    cv2.fillPoly(mask, points, 255)

    return mask


def get_contours(color_mask, points, mask_keys, color):
    # 为轨道创建一个单独的颜色掩码
    track_color_mask = np.zeros_like(color_mask)
    mask = create_polygon_mask(track_color_mask, points)
    mask_keys_track = cv2.bitwise_and(mask_keys, mask)
    track_color_mask = np.zeros_like(track_color_mask)

    track_color_mask[mask_keys_track > 0] = color
    # 创建轨道的颜色掩码
    gold_mask_track = cv2.inRange(track_color_mask, color, color)
    contours_track, _ = cv2.findContours(gold_mask_track, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours_track
# def process_contours(contours, roi_height, area_threshold, key_position):
#     for contour in contours:
#         M = cv2.moments(contour)
#         if M["m00"] != 0:
#             cX = int(M["m10"] / M["m00"])
#             cY = int(M["m01"] / M["m00"])
#         else:
#             continue
#
#         # 计算轮廓面积
#         area = cv2.contourArea(contour)
#
#         if  cY > roi_height * 0.5 and area > area_threshold:
#             PressKey(key_position)
#             time.sleep(0.01)  # You might need to adjust this delay
#             ReleaseKey(key_position)

def process_contours(contours_gold, contours_white, roi_height, area_threshold, key_position, is_holding):
    # 检查白色轮廓
    pressneeded = 0
    min_area = 3000
    if not is_holding:
        for contour in contours_white:
            area = cv2.contourArea(contour)
            if area < min_area:  # 面积小于最小面积，跳过此轮廓
                continue
            pressneeded = 1
            # print(str(key_position))
    #检查金色轮廓
    for contour in contours_gold:
        M = cv2.moments(contour)
        area = cv2.contourArea(contour)
        if area < area_threshold:  # 跳过此轮廓
            continue
        if M["m00"] != 0:
            cY = int(M["m01"] / M["m00"])
        else:
            continue



        if cY > roi_height * 0.5:
                # PressKey(key_position)
                # time.sleep(0.01)
                # ReleaseKey(key_position)
            if is_holding:  # 如果当前正在长按，则释放按键
                ReleaseKey(key_position)
                PressKey(key_position)
                time.sleep(0.01)
                ReleaseKey(key_position)
                return False  # 返回False表示不再长按
            else:  # 如果当前没有长按，则按下按键
                PressKey(key_position)
                if pressneeded:
                    return True  # 返回True表示正在长按
                else:
                    ReleaseKey(key_position)
                    return False
    return is_holding