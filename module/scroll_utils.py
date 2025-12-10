from pywinauto import mouse
import time

def force_scroll_down(window, config):
    """เลื่อนหน้าจอด้วย mouse wheel โดยใช้ค่าจาก config.ini"""

    try:
        center_x_offset = config.getint('MOUSE_SCROLL', 'CENTER_X_OFFSET')
        center_y_offset = config.getint('MOUSE_SCROLL', 'CENTER_Y_OFFSET')
        wheel_dist = config.getint('MOUSE_SCROLL', 'WHEEL_DIST')
        focus_delay = config.getfloat('MOUSE_SCROLL', 'FOCUS_DELAY')
        scroll_delay = config.getfloat('MOUSE_SCROLL', 'SCROLL_DELAY')
    except:
        print("[!] Scroll config invalid. Use default values")
        center_x_offset = 300
        center_y_offset = 300
        wheel_dist = -20
        focus_delay = 0.5
        scroll_delay = 1.0

    try:
        rect = window.rectangle()
        center_x = rect.left + center_x_offset
        center_y = rect.top + center_y_offset

        print(f"[i] Scroll at coords: ({center_x}, {center_y})")

        mouse.click(coords=(center_x, center_y))
        time.sleep(focus_delay)

        mouse.scroll(coords=(center_x, center_y), wheel_dist=wheel_dist)
        time.sleep(scroll_delay)

        print("[/] Scroll OK")

    except Exception as e:
        print("[!] Scroll failed, using PageDown")
        window.type_keys("{PGDN}")
