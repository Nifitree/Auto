import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
from evidence import save_evidence_context

CONFIG_FILE = "config.ini"

# ==================== CONFIG ====================

def read_config(filename=CONFIG_FILE):
    config = configparser.ConfigParser()
    if not os.path.exists(filename):
        print(f"[X] ไม่พบไฟล์ config: {filename}")
        return config
    config.read(filename, encoding="utf-8")
    return config

CONFIG = read_config()
if not CONFIG.sections():
    print("[X] โหลด config.ini ไม่สำเร็จ")
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

# ==================== COMMON HELPERS ====================

def connect_main_window():
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    return app, app.top_window()

def force_scroll_down(window):
    cfg = CONFIG["MOUSE_SCROLL"]
    rect = window.rectangle()
    x = rect.left + cfg.getint("CENTER_X_OFFSET")
    y = rect.top + cfg.getint("CENTER_Y_OFFSET")

    mouse.click(coords=(x, y))
    time.sleep(cfg.getfloat("FOCUS_DELAY"))
    mouse.scroll(coords=(x, y), wheel_dist=cfg.getint("WHEEL_DIST"))
    time.sleep(cfg.getfloat("SCROLL_DELAY"))

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

# ==================== MAIN ENTRY ====================

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
            raise Exception("ไม่พบช่องไปรษณีย์")
        fill_if_empty(main_window, postal, POSTAL_CODE)

        phone = main_window.child_window(
            auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit"
        )
        if not scroll_until_found(phone, main_window):
            raise Exception("ไม่พบช่องเบอร์โทรศัพท์")
        fill_if_empty(main_window, phone, PHONE_NUMBER)

        main_window.child_window(
            title=B_CFG["NEXT_TITLE"],
            auto_id=B_CFG["ID_AUTO_ID"],
            control_type="Text",
        ).click_input()
        time.sleep(WAIT_TIME)

        return True

    except Exception as e:
        print(f"[X] utility_services_main FAILED: {e}")
        return False

# ==================== TRANSACTION ====================

def utility_services_transaction(main_window, title, use_enter=False):
    main_window.child_window(
        title=title,
        auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"],
        control_type="Text",
    ).click_input()
    time.sleep(WAIT_TIME)

    if use_enter:
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

def search_and_execute(main_window, service_title, use_enter=False):
    search = main_window.child_window(
        auto_id=S_CFG["SEARCH_EDIT_ID"], control_type="Edit"
    )
    search.click_input()
    search.type_keys(service_title, with_spaces=True)
    search.type_keys("{ENTER}")
    time.sleep(1)

    if not main_window.child_window(
        title=service_title, control_type="Text"
    ).exists(timeout=3):
        raise Exception(f"ไม่พบรายการ {service_title}")

    utility_services_transaction(main_window, service_title, use_enter)

# ==================== SERVICE RUNNER ====================

def run_service(step_name, service_title, use_enter=False, use_search=False):
    app = None
    try:
        if not utility_services_main():
            return

        app, main_window = connect_main_window()

        if use_search:
            search_and_execute(main_window, service_title, use_enter)
        else:
            utility_services_transaction(main_window, service_title, use_enter)

    except Exception as e:
        save_evidence_context(app, {
            "test_name": "Utility Services Automation",
            "step_name": step_name,
            "error_message": str(e)
        })

# ==================== MAIN ====================

if __name__ == "__main__":
    run_service("utility_services1", S_CFG["UTILITY_1_TITLE"])
    run_service("utility_services2", S_CFG["UTILITY_2_TITLE"])
    run_service("utility_services3", S_CFG["UTILITY_3_TITLE"])
    run_service("utility_services4", S_CFG["UTILITY_4_TITLE"], use_enter=True)
    run_service("utility_services5", S_CFG["UTILITY_5_TITLE"], use_enter=True)
    run_service("utility_services6", S_CFG["UTILITY_6_TITLE"], use_search=True)
    run_service("utility_services7", S_CFG["UTILITY_7_TITLE"], use_enter=True, use_search=True)
    run_service("utility_services8", S_CFG["UTILITY_8_TITLE"], use_search=True)
    run_service("utility_services9", S_CFG["UTILITY_9_TITLE"], use_search=True)
