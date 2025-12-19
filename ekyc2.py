import configparser
import time
import os
import sys
from pywinauto.application import Application
from pywinauto import mouse
from evidence import save_evidence_context

CONFIG_FILE = "config.ini"

# ==================================================
# CONFIG
# ==================================================

def read_config(filename=CONFIG_FILE):
    config = configparser.ConfigParser()
    if not os.path.exists(filename):
        print(f"[X] ไม่พบไฟล์ config: {os.path.abspath(filename)}")
        return None
    config.read(filename, encoding="utf-8")
    return config


CONFIG = read_config()
if not CONFIG or not CONFIG.sections():
    print("[X] โหลด config.ini ไม่สำเร็จ")
    sys.exit(1)

# GLOBAL
WINDOW_TITLE = CONFIG["GLOBAL"]["WINDOW_TITLE"]
WAIT_TIME = CONFIG.getint("GLOBAL", "WAIT_TIME_SEC")
PHONE_NUMBER = CONFIG["GLOBAL"]["PHONE_NUMBER"]
PHONE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["PHONE_EDIT_AUTO_ID"]
POSTAL_CODE = CONFIG["GLOBAL"]["POSTAL_CODE"]
POSTAL_CODE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["POSTAL_CODE_EDIT_AUTO_ID"]

# EKYC
B_CFG = CONFIG["EKYC_MAIN"]
S_CFG = CONFIG["EKYC_SERVICES"]

# SCROLL
SCROLL_CFG = CONFIG["MOUSE_SCROLL"]

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def connect_main_window():
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    return app, app.top_window()


def force_scroll_down(window):
    try:
        rect = window.rectangle()
        x = rect.left + SCROLL_CFG.getint("CENTER_X_OFFSET")
        y = rect.top + SCROLL_CFG.getint("CENTER_Y_OFFSET")

        mouse.click(coords=(x, y))
        time.sleep(SCROLL_CFG.getfloat("FOCUS_DELAY"))
        mouse.scroll(coords=(x, y), wheel_dist=SCROLL_CFG.getint("WHEEL_DIST"))
        time.sleep(SCROLL_CFG.getfloat("SCROLL_DELAY"))
    except Exception:
        window.type_keys("{PGDN}")


def find_control_with_scroll(control, window, max_scroll=3):
    for _ in range(max_scroll):
        if control.exists(timeout=1):
            return True
        force_scroll_down(window)
    return False


def fill_edit_if_empty(edit_ctrl, value, window):
    current = edit_ctrl.texts()[0].strip()
    if not current:
        edit_ctrl.click_input()
        window.type_keys(value)
        time.sleep(0.5)
    else:
        print(f" [-] มีค่าอยู่แล้ว: {current}")


# ==================================================
# MAIN FLOW
# ==================================================

def run_ekyc_step(service_name, service_title):
    print(f"\n{'='*50}")
    print(f"[*] เริ่ม EKYC: {service_name} ({service_title})")

    app = None
    try:
        app, main = connect_main_window()
        print("[/] เชื่อมต่อหน้าจอสำเร็จ")

        # 1. Agency
        main.child_window(
            title=B_CFG["HOTKEY_AGENCY_TITLE"],
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        # 2. BaS (K)
        main.child_window(
            title=B_CFG["HOTKEY_BaS_TITLE"],
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        # 3. Select Service
        main.child_window(
            title=service_title,
            auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"],
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        # 4. Postal Code
        postal = main.child_window(
            auto_id=POSTAL_CODE_EDIT_AUTO_ID,
            control_type="Edit"
        )

        if not find_control_with_scroll(postal, main):
            raise RuntimeError("ไม่พบช่อง Postal Code")

        fill_edit_if_empty(postal, POSTAL_CODE, main)

        # 5. Phone Number
        phone = main.child_window(
            auto_id=PHONE_EDIT_AUTO_ID,
            control_type="Edit"
        )

        if not find_control_with_scroll(phone, main):
            raise RuntimeError("ไม่พบช่อง Phone Number")

        fill_edit_if_empty(phone, PHONE_NUMBER, main)

        # 6. Next
        main.child_window(
            title=B_CFG["NEXT_TITLE"],
            auto_id=B_CFG["ID_AUTO_ID"],
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        # 7. Exit
        main.type_keys("{ESC}")
        time.sleep(WAIT_TIME)

        print(f"[V] {service_name} สำเร็จ")

    except Exception as e:
        save_evidence_context(app, {
            "test_name": "EKYC Automation",
            "step_name": service_name,
            "error_message": str(e)
        })
        print(f"[X] ERROR {service_name}: {e}")


# ==================================================
# EXECUTION
# ==================================================

if __name__ == "__main__":
    if "EKYC_1_TITLE" in S_CFG:
        run_ekyc_step("Service 1", S_CFG["EKYC_1_TITLE"])

    if "EKYC_2_TITLE" in S_CFG:
        run_ekyc_step("Service 2", S_CFG["EKYC_2_TITLE"])

    print(f"\n{'='*50}\n[V] จบการทำงานทั้งหมด")
