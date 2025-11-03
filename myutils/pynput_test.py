import keyboard


def on_key(e):
    print(f"Key {e.name} pressed")


keyboard.hook(on_key)
keyboard.wait('esc')
