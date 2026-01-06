import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys
from evidence import save_evidence_context
from app_context import AppContext

CONFIG_FILE = "config.ini"

# ==================== 1. CONFIGURATION (เหมือนเดิม) ====================

def read_config(filename=CONFIG_FILE):
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

CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้")
    sys.exit(1)

# Global Config
WINDOW_TITLE = CONFIG["GLOBAL"]["WINDOW_TITLE"]
WAIT_TIME = CONFIG.getint("GLOBAL", "WAIT_TIME_SEC")
PHONE_NUMBER = CONFIG["GLOBAL"]["PHONE_NUMBER"]
ID_CARD_BUTTON_TITLE = CONFIG["GLOBAL"]["ID_CARD_BUTTON_TITLE"]
PHONE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["PHONE_EDIT_AUTO_ID"]
POSTAL_CODE = CONFIG["GLOBAL"]["POSTAL_CODE"]
POSTAL_CODE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["POSTAL_CODE_EDIT_AUTO_ID"]
NEXT_TITLE = "ถัดไป"
T_CFG = CONFIG["PAYMENT"]

# Specific Config
try:
    CFG = CONFIG["EMS_JUMBO_COM1"]
except KeyError:
    print("[X] ไม่พบ Section [EMS_JUMBO_COM1] ใน config.ini")
    sys.exit(1)

ctx = AppContext(window_title_regex=WINDOW_TITLE)

# ==================== 2. HELPERS (เพิ่ม try_click) ====================

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
    except Exception:
        window.type_keys("{PGDN}")

def scroll_until_found(control, window, max_scrolls=3):
    for _ in range(max_scrolls):
        if control.exists(timeout=1):
            return True
        force_scroll_down(window)
    return False

def fill_if_empty(window, control, value):
    try:
        current_text = control.texts()[0].strip()
        if not current_text:
            control.click_input()
            window.type_keys(value)
    except:
        control.click_input()
        window.type_keys(value)

def fill_field(window, auto_id, value, description=""):
    print(f"[*] {description}: {value}")
    control = window.child_window(auto_id=auto_id)
    if not scroll_until_found(control, window):
        raise Exception(f"ไม่พบช่อง {description} (ID: {auto_id})")
    control.click_input()
    window.type_keys(value)

def click_element_by_id(window, auto_id, description=""):
    print(f"[*] คลิก: {description} (ID: {auto_id})")
    control = window.child_window(auto_id=auto_id)
    if not scroll_until_found(control, window):
        raise Exception(f"ไม่พบปุ่ม {description}")
    control.click_input()
    time.sleep(0.5)

def press_next(main_window):
    print(f"[*] กดปุ่ม '{NEXT_TITLE}'")
    try:
        btn = main_window.child_window(title=NEXT_TITLE, control_type="Text")
        if btn.exists():
            btn.click_input()
        else:
            main_window.type_keys("{ENTER}")
    except:
        main_window.type_keys("{ENTER}") 
    time.sleep(WAIT_TIME)

def click_menu_button(main_window, title):
    print(f"[*] คลิกเมนู: {title}")
    btn = main_window.child_window(title=title, control_type="Text")
    if not scroll_until_found(btn, main_window):
        raise Exception(f"หาปุ่มเมนู '{title}' ไม่เจอ")
    btn.click_input()
    time.sleep(WAIT_TIME)

# ==================== 3. LOGIC (แก้ไขตรงนี้) ====================

def execute_ems_jumbo_flow(main_window):
    # --- 1. เมนู S และข้อมูลผู้ส่ง ---
    click_menu_button(main_window, CFG['BTN_S_TITLE'])

    print("[*] อ่านบัตรประชาชน")
    main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()
    
    print("[*] ตรวจสอบรหัสไปรษณีย์ผู้ส่ง")
    postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    if scroll_until_found(postal, main_window):
        fill_if_empty(main_window, postal, POSTAL_CODE)

    print("[*] ตรวจสอบเบอร์โทร")
    phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    if scroll_until_found(phone, main_window):
        fill_if_empty(main_window, phone, PHONE_NUMBER)

    press_next(main_window) # ถัดไป (1)

    # --- 2. เมนู Y -> A -> A ---
    click_menu_button(main_window, CFG['BTN_Y_TITLE'])
    click_menu_button(main_window, CFG['BTN_A_TITLE'])
    click_menu_button(main_window, CFG['BTN_A_TITLE'])
    
    press_next(main_window) # ถัดไป (2)

    # --- 3. รหัสไปรษณีย์ปลายทาง ---
    fill_field(main_window, CFG['DEST_POSTAL_ID'], CFG['DEST_POSTAL_VALUE'], "รหัสไปรษณีย์ปลายทาง")
    press_next(main_window) # ถัดไป (3)

    # --- 4. เลือกบริการ EMS Jumbo และวงเงิน ---
    click_element_by_id(main_window, CFG['SERVICE_JUMBO_ID'], "EMS Jumbo อัตราสำเร็จรูป")
    click_element_by_id(main_window, CFG['COVERAGE_ICON_ID'], "ไอคอนบวก (Coverage)")
    fill_field(main_window, CFG['COVERAGE_AMOUNT_ID'], CFG['COVERAGE_AMOUNT_VALUE'], "จำนวนเงินคุ้มครอง")
    
    press_next(main_window) # ถัดไป (4)
    press_next(main_window) # ถัดไป (5)

    # --- 5. Logic เลือกบริการพิเศษ (1-4) ---
    selected_option = int(CFG['SELECTED_ADDON_OPTION'])
    print(f"\n[*] กำลังเลือกบริการพิเศษ Option ที่: {selected_option}")

    if selected_option == 1:
        click_element_by_id(main_window, CFG['ADDON_1_ID'], "EMS Jumbo รับฝาก ณ ที่อยู่")
        time.sleep(0.5)
        fill_field(main_window, CFG['ADDON_1_AMOUNT_ID'], CFG['ADDON_1_AMOUNT_VALUE'], "ยอดเงินเก็บปลายทาง")
        press_next(main_window) 
        press_next(main_window) 

    elif selected_option == 2:
        click_element_by_id(main_window, CFG['ADDON_2_ID'], "ตอบรับ")
        press_next(main_window) 

    elif selected_option == 3:
        click_element_by_id(main_window, CFG['ADDON_3_ID'], "ตอบรับ - Track")
        press_next(main_window) 

    elif selected_option == 4:
        click_element_by_id(main_window, CFG['ADDON_4_ID'], "ส่งไปยังที่อยู่ของผู้รับ")
        press_next(main_window) 
    
    press_next(main_window) 

    # --- 6. ค้นหาและเลือกที่อยู่ (จุดที่แก้ Error) ---
    fill_field(main_window, CFG['SEARCH_ADDR_ID'], CFG['SEARCH_ADDR_VALUE'], "ค้นหาที่อยู่")
    
    # กดถัดไป 1 ครั้งเพื่อเริ่มค้นหา
    press_next(main_window)
    time.sleep(1.5) # รอผลการค้นหา หรือการเปลี่ยนหน้า

    # !!! แก้ไขตรงนี้: เช็คก่อนว่ามันข้ามไปหน้าชื่อผู้รับหรือยัง !!!
    # ถ้าเจอปุ่มเลือกกลุ่ม (Address Group) -> กด
    # ถ้าไม่เจอ -> เช็คว่าเจอช่องกรอกชื่อ (CustomerFirstName) ไหม -> ถ้าเจอแสดงว่าผ่านแล้ว
    
    group_btn = main_window.child_window(auto_id=CFG['ADDRESS_SELECT_GROUP_ID'])
    next_step_field = main_window.child_window(auto_id=CFG['RCV_FNAME_ID'])

    if group_btn.exists(timeout=2):
        print("[*] พบปุ่มเลือกกลุ่มที่อยู่ -> กำลังกดเลือก")
        group_btn.click_input()
        time.sleep(1.0)
    elif next_step_field.exists(timeout=2):
        print("[/] ระบบเลือกที่อยู่อัตโนมัติแล้ว (ข้ามขั้นตอนกดเลือกกลุ่ม)")
    else:
        # ถ้าหาไม่เจอทั้งคู่ ค่อย Error
        print("[!] Warning: ไม่พบปุ่มเลือกกลุ่ม และยังไม่ถึงหน้ากรอกชื่อ (พยายามไปต่อ)")

    # --- 7. กรอกข้อมูลผู้รับ ---
    fill_field(main_window, CFG['RCV_FNAME_ID'], CFG['RCV_FNAME_VALUE'], "ชื่อผู้รับ")
    fill_field(main_window, CFG['RCV_LNAME_ID'], CFG['RCV_LNAME_VALUE'], "นามสกุลผู้รับ")
    fill_field(main_window, CFG['RCV_PHONE_ID'], CFG['RCV_PHONE_VALUE'], "เบอร์โทรศัพท์")

    press_next(main_window)
    press_next(main_window)
    press_next(main_window)

    # --- 8. จัดการ Popup ---
    print("[*] ตรวจสอบ Popup...")
    time.sleep(1.0)
    popup_no = main_window.child_window(auto_id=CFG['POPUP_NO_ID'])
    if popup_no.exists(timeout=3):
        print("[!] พบ Popup -> กด 'ไม่' (No)")
        popup_no.click_input()
    else:
        print("[-] ไม่พบ Popup (ข้าม)")

    # --- 9. ชำระเงิน ---
    fast_cash_btn = main_window.child_window(auto_id="EnableFastCash")
    if fast_cash_btn.exists(timeout=2):
        fast_cash_btn.click_input()
    else:
        print("[!] EnableFastCash not found, using Hotkey F")
        main_window.type_keys(T_CFG['PAYMENT_FAST'])
        

# ==================== 4. MAIN RUNNER ====================

def run_service():
    step_name = "EMS Jumbo Com1 Flow (Fixed)"
    app = None
    print(f"\n{'='*50}\n[*] เริ่มทำรายการ: {step_name}")

    try:
        app, main_window = connect_main_window()
        execute_ems_jumbo_flow(main_window)
        print(f"[V] SUCCESS: {step_name} สำเร็จ")

    except Exception as e:
        print(f"\n[X] FAILED: {step_name} -> {e}")
        if app:
            try:
                save_evidence_context(app, {
                    "test_name": "EMS Jumbo Automation",
                    "step_name": step_name,
                    "error_message": str(e)
                })
                print("[/] บันทึกภาพ Error เรียบร้อย")
            except: pass
        sys.exit(1)

if __name__ == "__main__":
    run_service()