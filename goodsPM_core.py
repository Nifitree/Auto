import configparser
import time
import os
import sys
from pywinauto.application import Application
from pywinauto import mouse
from evidence import save_evidence_context
from app_context import AppContext

CONFIG_FILE = "config.ini"

# ==================== CONFIGURATION ====================

def read_config(filename=CONFIG_FILE):
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] Config not found: {filename}")
            return configparser.ConfigParser()
        config.read(filename, encoding="utf-8")
        return config
    except Exception as e:
        print(f"[X] Config Error: {e}")
        return configparser.ConfigParser()

CONFIG = read_config()
if not CONFIG.sections():
    print("Cannot load config.ini")
    sys.exit(1)

# Global Configs
WINDOW_TITLE = CONFIG["GLOBAL"]["WINDOW_TITLE"]
WAIT_TIME = CONFIG.getint("GLOBAL", "WAIT_TIME_SEC")
PHONE_NUMBER = CONFIG["GLOBAL"]["PHONE_NUMBER"]
ID_CARD_BUTTON_TITLE = CONFIG["GLOBAL"]["ID_CARD_BUTTON_TITLE"]
PHONE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["PHONE_EDIT_AUTO_ID"]
POSTAL_CODE = CONFIG["GLOBAL"]["POSTAL_CODE"]
POSTAL_CODE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["POSTAL_CODE_EDIT_AUTO_ID"]

# GoodsPM Configs
B_CFG = CONFIG["GOODSPM_MAIN"]
S_CFG = CONFIG["GOODSPM_SERVICES"]

# Initialize AppContext
ctx = AppContext(window_title_regex=WINDOW_TITLE)

# ==================== HELPERS ====================

def connect_main_window():
    return ctx.connect()

def force_scroll_down(window):
    try:
        cfg = CONFIG["MOUSE_SCROLL"]
        center_x = cfg.getint("CENTER_X_OFFSET", fallback=300)
        center_y = cfg.getint("CENTER_Y_OFFSET", fallback=300)
        wheel_dist = cfg.getint("WHEEL_DIST", fallback=-20)
        mouse.click(coords=(window.rectangle().left + center_x, window.rectangle().top + center_y))
        time.sleep(0.5)
        mouse.scroll(coords=(window.rectangle().left + center_x, window.rectangle().top + center_y), wheel_dist=wheel_dist)
        time.sleep(1.0)
    except:
        window.type_keys("{PGDN}")

def scroll_until_found(control, window, max_scrolls=3):
    if control.exists(timeout=1): return True
    for _ in range(max_scrolls):
        force_scroll_down(window)
        if control.exists(timeout=1): return True
    return False

def fill_if_empty(window, control, value):
    try:
        if not control.texts()[0].strip():
            control.click_input()
            time.sleep(0.5)
            control.type_keys(value, with_spaces=True)
    except: pass

# --- [ADDED] Helper สำหรับกรอกข้อมูลเจาะจงช่อง ---
def fill_field_by_id(window, auto_id, value, description=""):
    print(f"[*] Filling {description} ({auto_id}): {value}")
    control = window.child_window(auto_id=auto_id)
    
    if not scroll_until_found(control, window):
        raise Exception(f"Field not found: {description} (ID: {auto_id})")
    
    control.click_input()
    time.sleep(0.5)
    control.type_keys("^a{BACKSPACE}") # ลบค่าเก่า
    control.type_keys(value, with_spaces=True)

# --- [ADDED] Helper กดปุ่มถัดไป ---
def press_next_button(window):
    print("[*] Clicking Next...")
    next_btn = window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"])
    if next_btn.exists():
        next_btn.click_input()
    else:
        window.type_keys("{ENTER}")
    time.sleep(WAIT_TIME)

# --- [ADDED] Helper ค้นหาและเลือกบริการ (สำหรับ goodsPM_8 และอื่นๆ) ---
def search_and_select_service(window, service_title):
    """ค้นหา Service Code แล้วคลิกเลือกรายการ"""
    print(f"[*] Searching for Service: {service_title}")
    
    # 1. พิมพ์ค้นหา
    search_input = window.child_window(auto_id=S_CFG["SEARCH_EDIT_ID"], control_type="Edit")
    search_input.click_input()
    search_input.type_keys("^a{BACKSPACE}")
    search_input.type_keys(service_title, with_spaces=True)
    search_input.type_keys("{ENTER}")
    time.sleep(1.5) # รอโหลดผลลัพธ์

    # 2. คลิกรายการที่เจอ (ใช้ Logic เดียวกับ run_goods_transaction)
    target_item = window.child_window(title=service_title, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text")
    
    if target_item.exists(timeout=3):
        target_item.click_input()
        print(f"[/] Selected: {service_title}")
    else:
        raise Exception(f"Service {service_title} not found in search results.")
    
    time.sleep(WAIT_TIME)

# ==================== CORE LOGIC ====================

def goods_pm_main():
    """Logic เข้าเมนู A -> G -> อ่านบัตร -> กรอกข้อมูล"""
    try:
        app, main_window = connect_main_window()
        print(f"[*] Navigating to GoodsPM Main ({B_CFG['BT_A_TITLE']} -> {B_CFG['BT_G_TITLE']})...")
        
        main_window.child_window(title=B_CFG['BT_A_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        main_window.child_window(title=B_CFG['BT_G_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print("[*] Reading ID Card...")
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()

        print("[*] Checking Postal Code...")
        postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(postal, main_window): raise Exception("Postal not found")
        fill_if_empty(main_window, postal, POSTAL_CODE)

        print("[*] Checking Phone...")
        phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(phone, main_window): raise Exception("Phone not found")
        fill_if_empty(main_window, phone, PHONE_NUMBER)

        print("[*] Clicking Next...")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        return True
    except Exception as e:
        print(f"[X] Navigation Failed: {e}")
        return False

def run_goods_transaction(main_window, title):
    """ทำรายการย่อย (เลือก -> ถัดไป -> เสร็จสิ้น)"""
    print(f"[*] Selecting Item: {title}")
    main_window.child_window(title=title, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

    print("[*] Clicking Next...")
    main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

    print("[*] Clicking Finish...")
    main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

def run_service(step_name, service_title, use_main=True, use_search=False):
    """Wrapper หลักสำหรับเรียกจากไฟล์ลูก"""
    app = None
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name} ({service_title})")
        
        app, main_window = connect_main_window()

        if use_main and not goods_pm_main():
            return

        if use_search:
            print(f"[*] Searching for code: {service_title}")
            search_input = main_window.child_window(auto_id=S_CFG["SEARCH_EDIT_ID"], control_type="Edit")
            search_input.click_input()
            search_input.type_keys("^a{BACKSPACE}")
            search_input.type_keys(service_title, with_spaces=True)
            search_input.type_keys("{ENTER}")
            time.sleep(1.5)

            target = main_window.child_window(title=service_title, control_type="Text")
            if not target.exists(timeout=3):
                raise Exception(f"Service {service_title} not found in search results")

        run_goods_transaction(main_window, service_title)
        print(f"[V] SUCCESS: {step_name}")

    except Exception as e:
        if app: save_evidence_context(app, {"test_name": "GoodsPM", "step_name": step_name, "error_message": str(e)})
        print(f"[X] FAILED: {e}")