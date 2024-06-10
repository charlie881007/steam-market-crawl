import cv2
import numpy as np
import pyautogui
import win32api
from win32con import *
import time
#
# img_rgb = cv2.imread('big.jpg')
# img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
# template = cv2.imread('small.jpg',0)
# w, h = template.shape[::-1]
#
# res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
# threshold = 0.8
# loc = np.where( res >= threshold)
# for pt in zip(*loc[::-1]):
#     cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

time.sleep(5)
template_pic = 'img/s1mpleholo.jpg'

speed = 0
limit = 800

is_done = False
i = 0
while not is_done:
    pyautogui.screenshot('current.jpg')

    img_rgb = cv2.imread('current.jpg')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template_pic, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)

    print(loc)

    if loc[0].size == 0:
        is_done = True

    else:
        for pt in zip(*loc[::-1]):
            pyautogui.moveTo(pt)
            pyautogui.sleep(speed)
            pyautogui.click()
            pyautogui.sleep(speed)

            i += 1
            if i >= limit:
                is_done = True
                break

        pyautogui.moveTo(130, 500)
        time.sleep(1)
        win32api.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, -900, 0)

        time.sleep(0.4)


img = cv2.imread('current.jpg',0)
img2 = img.copy()
template = cv2.imread('comfirm.jpg',0)
w, h = template.shape[::-1]

method = cv2.TM_SQDIFF
img = img2.copy()

# Apply template Matching
res = cv2.matchTemplate(img,template,method)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
    top_left = min_loc
else:
    top_left = max_loc
pyautogui.moveTo(top_left)
time.sleep(0.2)
pyautogui.click()