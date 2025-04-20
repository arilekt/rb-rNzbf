import keyboard
import json
import layout_map
import pyperclip
import time
import threading
import os
from PIL import Image, ImageDraw

try:
    from win10toast import ToastNotifier
    toast = ToastNotifier()
except ImportError:
    toast = None

try:
    import pystray
except ImportError:
    pystray = None

# Load config
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

with open(config["dictionary_path"], encoding="utf-8") as f:
    dictionary = json.load(f)

toggle_key = config.get("toggle_key", "ctrl+alt")
enabled = True

def switch_layout(text):
    return ''.join([layout_map.th_to_en.get(c, layout_map.en_to_th.get(c, c)) for c in text])

def notify(text):
    if toast:
        toast.show_toast("rb-rNzbf", text, duration=1, threaded=True)
    else:
        print("[NOTI]", text)

def toggle():
    global enabled
    enabled = not enabled
    notify(f"rb-rNzbf {'เปิด' if enabled else 'ปิด'}")

def on_space(e):
    if not enabled:
        return

    keyboard.send('ctrl+shift+left')
    keyboard.send('ctrl+c')
    time.sleep(0.1)  # เพิ่มเวลาให้ clipboard ทำงานทัน
    word = pyperclip.paste().strip()

    if not word:
        return

    converted = switch_layout(word)

    if converted in dictionary:
        corrected = dictionary[converted]
        keyboard.send('backspace')
        keyboard.write(corrected, delay=0.005)
        notify(f"แก้คำว่า: {word} → {corrected}")

keyboard.add_hotkey(toggle_key, toggle)
keyboard.on_press_key("space", on_space)

def create_icon():
    image = Image.new('RGB', (64, 64), "black")
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill="white")
    return image

def tray_run():
    if not pystray:
        return

    icon = pystray.Icon("rb-rNzbf")
    icon.icon = create_icon()
    icon.title = "rb-rNzbf"
    icon.menu = pystray.Menu(
        pystray.MenuItem("เปิด/ปิด (Toggle)", lambda: toggle()),
        pystray.MenuItem("ออก", lambda: os._exit(0))
    )
    icon.run()

notify(f"rb-rNzbf พร้อมใช้งานแล้ว (Toggle: {toggle_key})")
threading.Thread(target=tray_run, daemon=True).start()

# รอแบบ soft ไม่ block exit
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
