import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys
from evidence import save_evidence_context

CONFIG_FILE = "config.ini"

# ==================== CONFIG ====================

def read_config(filename=CONFIG_FILE):
    """อ่านและโหลดค่าจากไฟล์ config.ini"""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] ไม่พบไฟล์ config ที่: {os.path.abspath(filename)}")
            return configparser.ConfigParser()
        config.read(filename, encoding="utf-8")
        return config
    except Exception as e:
        print(f"[X] FAILED: อ่าน config ไม่ได้: {e}")
        return configparser.ConfigParser()

# โหลด Config
CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้")
    exit()

WINDOW_TITLE = CONFIG["GLOBAL"]["WINDOW_TITLE"]
WAIT_TIME = CONFIG.getint("GLOBAL", "WAIT_TIME_SEC")
PHONE_NUMBER = CONFIG["GLOBAL"]["PHONE_NUMBER"]
ID_CARD_BUTTON_TITLE = CONFIG["GLOBAL"]["ID_CARD_BUTTON_TITLE"]
PHONE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["PHONE_EDIT_AUTO_ID"]
POSTAL_CODE = CONFIG["GLOBAL"]["POSTAL_CODE"]
POSTAL_CODE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["POSTAL_CODE_EDIT_AUTO_ID"]

B_CFG = CONFIG["UTILITY_MAIN"]
S_CFG = CONFIG["UTILITY_SERVICES"]

# ==================== HELPERS ====================

def connect_main_window():
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    return app, app.top_window()

def force_scroll_down(window):
    try:
        cfg = CONFIG["MOUSE_SCROLL"]
        center_x_offset = cfg.getint("CENTER_X_OFFSET")
        center_y_offset = cfg.getint("CENTER_Y_OFFSET")
        wheel_dist = cfg.getint("WHEEL_DIST")
        focus_delay = cfg.getfloat("FOCUS_DELAY")
        scroll_delay = cfg.getfloat("SCROLL_DELAY")
    except Exception:
        center_x_offset, center_y_offset, wheel_dist, focus_delay, scroll_delay = 300, 300, -20, 0.5, 1.0

    try:
        rect = window.rectangle()
        x = rect.left + center_x_offset
        y = rect.top + center_y_offset
        mouse.click(coords=(x, y))
        time.sleep(focus_delay)
        mouse.scroll(coords=(x, y), wheel_dist=wheel_dist)
        time.sleep(scroll_delay)
    except Exception:
        window.type_keys("{PGDN}")

def scroll_until_found(control, window, max_scrolls=3):
    for _ in range(max_scrolls):
        if control.exists(timeout=1):
            return True
        force_scroll_down(window)
    return False

def fill_if_empty(window, control, value):
    if not control.texts()[0].strip():
        control.click_input()
        window.type_keys(value)

# ==================== MAIN FLOW ====================

def utility_services_main():
    try:
        app, main_window = connect_main_window()

        main_window.child_window(
            title=B_CFG["HOTKEY_AGENCY_TITLE"], control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)
        main_window.child_window(
            title=B_CFG["HOTKEY_BaS_TITLE"], control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        main_window.child_window(
            title=ID_CARD_BUTTON_TITLE, control_type="Text"
        ).click_input()

        postal = main_window.child_window(
            auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit"
        )
        if not scroll_until_found(postal, main_window):
            return False
        fill_if_empty(main_window, postal, POSTAL_CODE)

        phone = main_window.child_window(
            auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit"
        )
        if not scroll_until_found(phone, main_window):
            return False
        fill_if_empty(main_window, phone, PHONE_NUMBER)

        main_window.child_window(
            title=B_CFG["NEXT_TITLE"],
            auto_id=B_CFG["ID_AUTO_ID"],
            control_type="Text",
        ).click_input()
        time.sleep(WAIT_TIME)

        print("[V] SUCCESS: Utility Services Main สำเร็จ")
        return True

    except Exception as e:
        print(f"[X] FAILED: utility_services_main error: {e}")
        return False

# ==================== TRANSACTIONS ====================

def utility_services_transaction(main_window, title, enter=False):
    try:
        main_window.child_window(
            title=title,
            auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"],
            control_type="Text",
        ).click_input()
        time.sleep(WAIT_TIME)

        if enter:
            main_window.type_keys("{ENTER}")
        else:
            main_window.child_window(
                title=B_CFG["NEXT_TITLE"],
                auto_id=B_CFG["ID_AUTO_ID"],
                control_type="Text",
            ).click_input()

        time.sleep(WAIT_TIME)

        main_window.child_window(
            title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

    except Exception as e:
        print(f"[X] FAILED: Transaction {title} error: {e}")
        raise

def search_and_execute(main_window, service_title, enter=False):
    search = main_window.child_window(
        auto_id=S_CFG["SEARCH_EDIT_ID"], control_type="Edit"
    )
    search.click_input()
    search.type_keys(service_title, with_spaces=True)
    search.type_keys("{ENTER}")
    time.sleep(1)

    target = main_window.child_window(title=service_title, control_type="Text")
    if not target.exists(timeout=3):
        raise Exception(f"ไม่พบรายการ {service_title}")

    utility_services_transaction(main_window, service_title, enter)

# ==================== SERVICE WRAPPERS ====================

def run_service(step_name, service_title, use_main=True, enter=False, use_search=False):
    app = None
    try:
        if use_main and not utility_services_main():
            return

        app, main_window = connect_main_window()

        if use_search:
            search_and_execute(main_window, service_title, enter)
        else:
            utility_services_transaction(main_window, service_title, enter)

    except Exception as e:
        save_evidence_context(app, {
            "test_name": "Utility Services Automation",
            "step_name": step_name,
            "error_message": str(e)
        })

# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    run_service("utility_services1", S_CFG["UTILITY_1_TITLE"], use_main=False)
    run_service("utility_services2", S_CFG["UTILITY_2_TITLE"])
    run_service("utility_services3", S_CFG["UTILITY_3_TITLE"])
    run_service("utility_services4", S_CFG["UTILITY_4_TITLE"], enter=True)
    run_service("utility_services5", S_CFG["UTILITY_5_TITLE"], enter=True)
    run_service("utility_services6", S_CFG["UTILITY_6_TITLE"], use_search=True)
    run_service("utility_services7", S_CFG["UTILITY_7_TITLE"], enter=True, use_search=True)
    run_service("utility_services8", S_CFG["UTILITY_8_TITLE"], use_search=True)
    run_service("utility_services9", S_CFG["UTILITY_9_TITLE"], use_search=True)
