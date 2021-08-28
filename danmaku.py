#!/usr/bin/env ipython

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os import system
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import sys
from os import system
from datetime import datetime

host_uid = "12195399"
live_url = "http://live.bilibili.com/10225782"
update_time = time.time() - 300  # read 5 min history


def check_new_danma():
    global update_time, notify_command
    while True:
        driver.switch_to.window(driver.window_handles[0])
        chat_items = driver.find_element_by_id("chat-items")
        chat_item = chat_items.find_elements_by_class_name("chat-item")
        #chat_item = list(filter(lambda item: not item.get_attribute("data-danmaku") is None, chat_item))
        chat_item = list(filter(lambda item: not item.get_attribute("data-danmaku") is None and not item.get_attribute("data-uid") == host_uid, chat_item))
        current_time = time.time()
        item_list = list()
        for item in chat_item:
            timestamp = int(item.get_attribute("data-ts"))
            user_name = item.get_attribute("data-uname")
            danmaku = item.get_attribute("data-danmaku")
            item_list.append({"timestamp": timestamp, "user_name": user_name, "danmaku": danmaku})
        item_list = sorted(item_list, key=lambda item: item["timestamp"])
        for item in item_list:
            if item["timestamp"] <= update_time:
                continue
            update_time = item["timestamp"]
            print(datetime.utcfromtimestamp(item["timestamp"]).strftime('[%Y-%m-%d %H:%M:%S]'), "[" + item["user_name"] + "]:", item["danmaku"])
            system(notify_command.format(item["user_name"], item["danmaku"]))
            fanyi(item["user_name"] + "\n" + item["danmaku"])
        time.sleep(2)


def fanyi(message):
    driver.switch_to.window(driver.window_handles[1])
    input_wrap = driver.find_element_by_class_name("trans-input-wrap")
    input_blank = input_wrap.find_element_by_class_name("textarea")
    input_blank.send_keys(message)
    input_blank.send_keys(Keys.ENTER)
    time.sleep(1)
    speaker = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "operate-btn.op-sound.data-hover-tip")))
    try:
        speaker.click()
    except Exception as e:
        print(e)
    time.sleep(int(len(message) * 1))
    input_blank.clear()


if __name__ == "__main__":
    if sys.platform == "win32":
        notify_command = "powershell.exe New-BurntToastNotification -AppLogo ./bilibili.png -Text {}, {}"
    elif sys.platform == "linux":
        notify_command = """notify-send -i ./bilibili "{}" {} """
        sys.path.append("./linux")
    else:
        exit(0)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(live_url)
    driver.execute_script("window.open('https://fanyi.baidu.com/#zh/en', 'fanyi');")
    delay = 10  # 10 seconds
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "chat-items")))
    driver.switch_to.window(driver.window_handles[1])
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "desktop-guide-close")))
    driver.find_element_by_class_name("desktop-guide-close").click()
    try:
        check_new_danma()
    except Exception as e:
        print(e)
    driver.close()
