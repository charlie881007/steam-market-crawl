import pyautogui
import time
import win32con
import random
import win32clipboard
import cv2
import numpy as np

frequency = 6

text_template = """
function clickfloat(){
    document.getElementById("allfloatbutton").click();
}

function buy(){
    document.querySelector("#market_buynow_dialog_purchase").children[0].click();
}

function findTarget(){
    let priceCap = 19;
    let floatCap = 0.025;
    let floatCapLow = 0.0192857;
    let floatCapHigh = 0.0331;

    let blocks = document.querySelectorAll(".market_listing_row");

    for (var i = 0; i < blocks.length; i++){
        let element = blocks[i];
        let float = element.querySelector(".csgofloat-itemfloat");
        let price = element.querySelector(".market_listing_price_with_fee");

      if (float){
            float = float.innerHTML.replace("Float: ", "");
            float = parseFloat(float);
            price = price.innerHTML.replace("NT$ ", "");
            price = parseFloat(price);

            console.log(float, price);

         if (float < floatCap && price < priceCap){
                let buyBtn = element.querySelector(".market_listing_buy_button span")
                console.log("找到目標")

            if (buyBtn){
                    console.log("下單中")

               buyBtn.click() 

               document.querySelector("#market_buynow_dialog_accept_ssa").checked = true; 
                    setTimeout(buy, 30);
            }
         }
        }
    }
}

function reload(){
    location.reload(true);
}

function main(){
   // 找符合的
    setTimeout(findTarget, 1200);

    // 刷新 
    setTimeout(reload, __);
}

main();


"""

text_template = text_template.replace('__', str(frequency*1000-500))


def copy(text):
    """複製"""
    win32clipboard.OpenClipboard()  # 開啟剪貼簿
    win32clipboard.EmptyClipboard()  # 清空剪貼簿內容。可以忽略這步操作，但是最好加上清除貼上板這一步
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)  # 以Unicode文字形式放入剪下板
    win32clipboard.CloseClipboard()  # 關閉剪貼簿


def check_blank():
    pyautogui.screenshot('current.jpg')

    img_rgb = cv2.imread('current.jpg')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread("blank.jpg", 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)

    if loc[0].size != 0:
        pyautogui.hotkey("ctrl", "w");

def check_reload():
    pyautogui.screenshot('current.jpg')

    img_rgb = cv2.imread('current.jpg')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread("problem.jpg", 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)

    if loc[0].size != 0:
        img_rgb = cv2.imread('current.jpg')
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread("reload.jpg", 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.where(res >= threshold)

        if loc[0].size != 0:
            pyautogui.press("f12")
            time.sleep(0.5)
            pyautogui.press("f12")

            pyautogui.moveTo(loc[1][0], loc[0][0])
            pyautogui.click()

def check_debug():
    pyautogui.screenshot('current.jpg')

    img_rgb = cv2.imread('current.jpg')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread("debug.jpg", 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)

    if loc[0].size != 0:
        img_rgb = cv2.imread('current.jpg')
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread("debug.jpg", 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.where(res >= threshold)

        if loc[0].size != 0:
            pyautogui.moveTo(loc[1][0], loc[0][0])
            pyautogui.click()


def main():

    time.sleep(5)

    while True:
        check_blank()
        check_reload()
        check_debug()

        sec = random.randint(frequency, frequency)
        text = text_template.replace("_sec", str(sec*1000))

        copy(text)

        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")
        time.sleep(sec)




pyautogui.FAILSAFE = False
main()