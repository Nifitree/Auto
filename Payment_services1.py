import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os

CONFIG_FILE = "config.ini"

# ==================== CONFIG & HELPER FUNCTIONS ====================

def read_config(filename=CONFIG_FILE):
    """อ่านและโหลดค่าจากไฟล์ config.ini"""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] ไม่พบไฟล์ config ที่: {os.path.abspath(filename)}")
            return configparser.ConfigParser()
            
        config.read(filename, encoding='utf-8')
        return config
    except Exception as e:
        print(f"[X] FAILED: ไม่สามารถอ่านไฟล์ {filename} ได้: {e}")
        return configparser.ConfigParser()

# โหลด Config
CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้ โปรดตรวจสอบไฟล์")
    exit()

# ค่า Global
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
SLEEP_TIME = CONFIG.getfloat('GLOBAL', 'LOAD_TIME_SEC')

# ==================== DEBUG: DUMP TREE ====================

def dump_tree(window):
    print("\n========== UI ELEMENT TREE ==========")
    try:
        window.print_control_identifiers()
    except Exception as e:
        print(f"ไม่สามารถ dump tree ได้: {e}")
    print("=====================================\n")

# ==================== SCROLL HELPERS ====================

def force_scroll_down(window, config):
    """เลื่อนหน้าจอลงโดยใช้ Mouse wheel"""
    try:
        center_x_offset = config.getint('MOUSE_SCROLL', 'CENTER_X_OFFSET')
        center_y_offset = config.getint('MOUSE_SCROLL', 'CENTER_Y_OFFSET')
        wheel_dist = config.getint('MOUSE_SCROLL', 'WHEEL_DIST')
        focus_delay = config.getfloat('MOUSE_SCROLL', 'FOCUS_DELAY')
        scroll_delay = config.getfloat('MOUSE_SCROLL', 'SCROLL_DELAY')
    except ValueError:
        print("[!] Scroll config invalid. Using defaults.")
        center_x_offset, center_y_offset, wheel_dist, focus_delay, scroll_delay = 300, 300, -20, 0.5, 1.0

    print(f"...กำลังเลื่อนหน้าจอลง (Mouse Wheel {wheel_dist})...")

    try:
        rect = window.rectangle()
        center_x = rect.left + center_x_offset
        center_y = rect.top + center_y_offset
        
        mouse.click(coords=(center_x, center_y))
        time.sleep(focus_delay)
        
        mouse.scroll(coords=(center_x, center_y), wheel_dist=wheel_dist)
        time.sleep(scroll_delay)
        print("[/] Scroll สำเร็จ")
    except Exception as e:
        print(f"[!] Scroll failed: {e}, ใช้ PageDown แทน")
        window.type_keys("{PGDN}")

# ==================== MAIN TEST FUNCTION ====================

def test_agency_barcode(config):
    print("=" * 50)
    print("[*] เริ่มทดสอบ: agency barcode")

    AB = config['agency']
    ID = config['ID']
    PH = config['phone']
    NX = config['NEXT']

    try:
        # 1. เชื่อมต่อ App
        print("[*] กำลังเชื่อมต่อหน้าจอหลัก...")
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        win = app.window(title_re=WINDOW_TITLE)
        win.set_focus()
        print("[/] เชื่อมต่อสำเร็จ")

        # 2. กด A
        win.child_window(title=AB['HOTKEY_AGENCY_TITLE'],
                         auto_id=AB['HOTKEY_AGENCY_AUTO_ID'],
                         control_type=AB['HOTKEY_AGENCY_CONTROL_TYPE']).click_input()
        time.sleep(SLEEP_TIME)

        # 3. กด D
        win.child_window(title=AB['HOTKEY_SAB_TITLE'],
                         auto_id=AB['HOTKEY_SAB_AUTO_ID'],
                         control_type=AB['HOTKEY_SAB_CONTROL_TYPE']).click_input()
        time.sleep(SLEEP_TIME)

        print("[*] Dump UI Tree ก่อนค้นหา...")
        dump_tree(win)

        print("[*] ค้นหา Custom หลักของเบอร์โทร...")
        try:
            phone_custom_spec = win.child_window(
                auto_id="PhoneNumber_UserControlBase",
                control_type="Custom"
            )
            phone_custom_spec.wait("ready", timeout=3)
        except:
            print("[!] ไม่พบ PhoneNumber_UserControlBase — Scroll ลง")
            force_scroll_down(win, config)
            time.sleep(SLEEP_TIME)
            phone_custom_spec = win.child_window(
                auto_id="PhoneNumber_UserControlBase",
                control_type="Custom"
            )
            phone_custom_spec.wait("ready", timeout=3)

        print("[/] พบ Custom ของเบอร์โทร")

        # หา Edit ตัวจริง (call child_window on WindowSpecification)
        phone_edit = phone_custom_spec.child_window(
            auto_id="PhoneNumber",
            control_type="Edit"
        ).wait("ready", timeout=3)

        print("[*] กำลังกรอกเบอร์โทร...")

        phone_edit.click_input()
        time.sleep(0.2)
        phone_edit.type_keys("^a{BACKSPACE}")  # clear
        time.sleep(0.2)
        phone_edit.type_keys(PH['PHONE_NUM'], with_spaces=True)

        print("[/] กรอกเบอร์โทรสำเร็จ")

        # ====== END ส่วนเบอร์โทร ======

        # 5. อ่านบัตรประชาชน
        win.child_window(title=ID['ID_TITLE'],
                         auto_id=ID['ID_AUTO_ID'],
                         control_type=ID['ID_CONTROL_TYPE']).click_input()
        time.sleep(SLEEP_TIME)
        print("[/] กดปุ่มอ่านบัตรประชาชนสำเร็จ")

        # 6.กดปุ่มถัดไป
        win.child_window(title=NX['NEXT_TITLE'],
                         auto_id=NX['NEXT_AUTO_ID'],
                         control_type=NX['NEXT_CONTROL_TYPE']).click_input()
        time.sleep(SLEEP_TIME)
        print("[/] กดปุ่มถัดไปสำเร็จ")
        
        # สิิ้นสุดหน้านี้ ต้องการ barcode เพื่อไปต่อ
        print("[V] สิิ้นสุดหน้านี้ ต้องการ barcode เพื่อไปต่อ")

    except Exception as e:
        print(f"[X] Error: {e}")


if __name__ == "__main__":
    test_agency_barcode(CONFIG)