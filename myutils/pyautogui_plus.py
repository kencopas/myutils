import pyautogui as pag
import webbrowser
import os
import time
from pynput import mouse, keyboard


def wait(seconds):
    print(f"Waiting for {seconds} seconds...")
    if seconds <= 1:
        pag.sleep(seconds)
        return
    for i in range(seconds):
        pag.sleep(1)
        print(f"Seconds remaining: {seconds - i - 1}     ", end="\r")


def wait_for(image_path, timeout=15, confidence=0.9):
    print(f"Waiting for image {os.path.basename(image_path)} to appear on screen...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        location = pag.locateOnScreen(image_path, confidence=confidence)
        if location:
            print(f"Image {os.path.basename(image_path)} found.")
            return True
        wait(1)
    raise Exception(f"Timeout: Image {os.path.basename(image_path)} not found on screen within {timeout} seconds.")


def wait_for_or_time(wait_for, wait_time):
    if wait_for:
        wait_for(wait_for)
    else:
        wait(wait_time)


def click_image(image_path, wait_time=1, confidence=0.9, allow_fail=False, wait_for=None):
    for i in range(3):
        if allow_fail and i >= 1:
            break
        try:
            location = pag.locateOnScreen(image_path, confidence=confidence)
            if location:
                pag.click(pag.center(location))
                wait_for_or_time(wait_for, wait_time)
                return True
        except Exception as e:
            print(f"Error occurred while clicking image: {os.path.basename(image_path)} - {e}\nRetrying...")
        wait(1)
    if not allow_fail:
        raise Exception(f"Image {os.path.basename(image_path)} not found on screen after multiple attempts.")
    return False


def typewrite(text, wait_time=0.1, interval=0.05, wait_for=None):
    pag.typewrite(text, interval=interval)
    wait_for_or_time(wait_for, wait_time)


def hotkey(*args, wait_time=1, interval_time=0.1, wait_for=None):
    for arg in args:
        pag.hotkey(arg)
        wait(interval_time)
    wait_for_or_time(wait_for, wait_time)


def click(x, y, wait_time=0.1, wait_for=None):
    pag.click(x, y)
    wait_for_or_time(wait_for, wait_time)


def doubleClick(x, y, wait_time=0.1, wait_for=None):
    pag.doubleClick(x, y)
    wait_for_or_time(wait_for, wait_time)


def tripleClick(x, y, wait_time=0.1, wait_for=None):
    pag.tripleClick(x, y)
    wait_for_or_time(wait_for, wait_time)


def open_url(url, wait_time=5, wait_for=None):
    webbrowser.open(url)
    wait_for_or_time(wait_for, wait_time)


def scroll(amount, wait_time=0.5, wait_for=None):
    pag.scroll(amount)
    wait_for_or_time(wait_for, wait_time)
