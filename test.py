import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys
from evidence import save_evidence_context
from app_context import AppContext

CONFIG_FILE = "config.ini"

# ==================== 1. CONFIGURATION ====================

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

# Specific Config
try:
    CFG = CONFIG["EMS_JUMBO_MOTORCYCLE1_2"]
except KeyError:
    print("[X] ไม่พบ Section [EMS_JUMBO_MOTORCYCLE1_2] ใน config.ini")
    sys.exit(1)

ctx = AppContext(window_title_regex=WINDOW_TITLE)

# ==================== 2. HELPERS (แก้ไขการเลื่อนหา) ====================

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

# [FIXED] เพิ่มจำนวนการเลื่อนสูงสุดเป็น 10 รอบ
def scroll_until_found(control, window, max_scrolls=10):
    # เช็คก่อนหนึ่งรอบ ถ้าเจอเลยก็จบ
    if control.exists(timeout=1):
        return True
        
    print(f"[*] กำลังเลื่อนหน้าจอหา Element... (Max {max_scrolls})")
    for i in range(max_scrolls):
        force_scroll_down(window)
        if control.exists(timeout=1):
            return True
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
    # scroll_until_found จะช่วยเลื่อนหาให้จนเจอ
    if not scroll_until_found(control, window):
        raise Exception(f"ไม่พบช่อง {description} (ID: {auto_id}) แม้จะเลื่อนหาแล้ว")
    control.click_input()
    window.type_keys(value)

def click_element_by_id(window, auto_id, description=""):
    print(f"[*] คลิก: {description} (ID: {auto_id})")
    control = window.child_window(auto_id=auto_id)
    if not scroll_until_found(control, window):
        raise Exception(f"ไม่พบปุ่ม {description} (ID: {auto_id}) แม้จะเลื่อนหาแล้ว")
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
    btn = main_window.child_window(title=title, found_index=0) 
    
    if not scroll_until_found(btn, main_window):
        raise Exception(f"หาปุ่มเมนู '{title}' ไม่เจอ")
    btn.click_input()
    time.sleep(WAIT_TIME)

def do_payment_process(main_window):
    print("[*] เข้าสู่ขั้นตอนรับเงิน")
    click_menu_button(main_window, CFG['BTN_RECEIVE_MONEY'])
    
    print("[*] ตรวจสอบปุ่ม Fast Cash")
    fast_cash_btn = main_window.child_window(auto_id=CFG['FAST_CASH_AUTO_ID'])
    
    # [FIXED] ใช้ scroll_until_found แทน exists เฉยๆ เผื่อปุ่มตกขอบ
    if scroll_until_found(fast_cash_btn, main_window, max_scrolls=3):
        print("[V] พบปุ่ม Fast Cash -> คลิก")
        fast_cash_btn.click_input()
    else:
        hotkey = CFG.get('PAYMENT_FAST_KEY', 'F')
        print(f"[!] ไม่พบปุ่ม Fast Cash -> ใช้ Hotkey: {hotkey}")
        main_window.type_keys(hotkey)

# ==================== 3. LOGIC (Updated) ====================

def execute_ems_jumbo_flow(main_window):
    # --- 1. เมนู S และข้อมูลผู้ส่ง ---
    click_menu_button(main_window, CFG['BTN_S_TITLE'])

    print("[*] อ่านบัตรประชาชน")
    # [FIXED] เพิ่มการเลื่อนหาปุ่มอ่านบัตรประชาชน
    id_card_btn = main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text")
    if scroll_until_found(id_card_btn, main_window):
        id_card_btn.click_input()
    else:
        print(f"[!] คำเตือน: หาปุ่ม '{ID_CARD_BUTTON_TITLE}' ไม่เจอ (ข้าม)")
    
    print("[*] ตรวจสอบรหัสไปรษณีย์ผู้ส่ง")
    postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    if scroll_until_found(postal, main_window):
        fill_if_empty(main_window, postal, POSTAL_CODE)

    print("[*] ตรวจสอบเบอร์โทร")
    phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    if scroll_until_found(phone, main_window):
        fill_if_empty(main_window, phone, PHONE_NUMBER)

    press_next(main_window) # ถัดไป (1)

    # --- 2. เมนู Y -> A -> Q ---
    click_menu_button(main_window, CFG['BTN_Y_TITLE'])
    click_menu_button(main_window, CFG['BTN_A_TITLE'])
    click_menu_button(main_window, CFG['BTN_Q_TITLE'])
    
    press_next(main_window) # ถัดไป (2)

    # --- 3. กรอกน้ำหนัก ---
    fill_field(main_window, CFG['WEIGHT_ID'], CFG['WEIGHT_VAL'], "น้ำหนัก (กรัม)")
    press_next(main_window) # ถัดไป (3)

    # --- 4. กรอกขนาด (กว้าง ยาว สูง) ---
    fill_field(main_window, CFG['DIM_L_ID'], CFG['DIM_L_VAL'], "ความยาว (Length)")
    fill_field(main_window, CFG['DIM_W_ID'], CFG['DIM_W_VAL'], "ความกว้าง (Width)")
    fill_field(main_window, CFG['DIM_H_ID'], CFG['DIM_H_VAL'], "ความสูง (Height)")
    press_next(main_window) # ถัดไป (4)

    # --- 5. รหัสไปรษณีย์ปลายทาง ---
    fill_field(main_window, CFG['DEST_POSTAL_ID'], CFG['DEST_POSTAL_VALUE'], "รหัสไปรษณีย์ปลายทาง")
    press_next(main_window) # ถัดไป (5)

    print("[*] ตรวจสอบ Popup Error (API)...")
    api_popup_id = CFG.get('API_POPUP_OK_ID', 'AcceptButton')
    try:
        api_btn = main_window.child_window(auto_id=api_popup_id)
        # Popup ไม่ต้อง scroll
        if api_btn.exists(timeout=3):
            print(f"[!] พบ Popup Error (API Connect) -> กดปุ่ม 'ตกลง' (ID: {api_popup_id})")
            api_btn.click_input()
            time.sleep(1.0)
    except Exception as e:
        print(f"[-] Error check popup skipped: {e}")

    # --- 6. เลือกบริการ EMS Jumbo และวงเงิน ---
    service_id = CFG.get('SERVICE_JUMBO_ID1', 'SKIP')
    if service_id.upper() != 'SKIP':
        try:
            click_element_by_id(main_window, service_id, "EMS Jumbo Service")
        except:
            print("[-] หาปุ่ม Service ไม่เจอ หรือถูกเลือกแล้ว")

    # เช็คตัวแปร SKIP_COVERAGE
    is_skip_coverage = CFG.get('SKIP_COVERAGE', 'No')
    
    if is_skip_coverage.upper() == 'YES':
        print("[*] Config สั่งข้าม Coverage (SKIP_COVERAGE=Yes) -> กดถัดไป 1 ครั้ง")
        press_next(main_window)
    else:
        coverage_id = CFG.get('COVERAGE_ICON_ID', 'CoverageIcon')
        click_element_by_id(main_window, coverage_id, "ไอคอนบวก (Coverage)")
        fill_field(main_window, CFG['COVERAGE_AMOUNT_ID'], CFG['COVERAGE_AMOUNT_VALUE'], "เงินคุ้มครอง")
        
        print("[*] เลือก Coverage ครบ -> กดถัดไป 2 ครั้ง")
        press_next(main_window)
        press_next(main_window)

    # --- 7. Logic เลือกบริการพิเศษ (1-4) ---
    raw_options = CFG.get('SELECTED_ADDON_OPTIONS', CFG.get('SELECTED_ADDON_OPTION', '0'))
    try:
        selected_options = [int(x.strip()) for x in str(raw_options).split(',') if x.strip().isdigit() and int(x.strip()) > 0]
    except:
        selected_options = []

    has_addon_selected = False 
    if not selected_options:
        print("[*] ไม่มีการเลือกบริการพิเศษ (ข้าม)")
        has_addon_selected = False
    else:
        print(f"[*] กำลังเลือกบริการพิเศษ: {selected_options}")
        has_addon_selected = True
        
        for opt in selected_options:
            if opt == 1:
                click_element_by_id(main_window, CFG['ADDON_1_ID'], "Addon 1")
                time.sleep(0.5)
                fill_field(main_window, CFG['ADDON_1_AMOUNT_ID'], CFG['ADDON_1_AMOUNT_VALUE'], "ยอดเงิน")
            elif opt == 2:
                click_element_by_id(main_window, CFG['ADDON_2_ID'], "Addon 2")
            elif opt == 3:
                click_element_by_id(main_window, CFG['ADDON_3_ID'], "Addon 3")
            elif opt == 4:
                click_element_by_id(main_window, CFG['ADDON_4_ID'], "Addon 4")
            time.sleep(0.5)

    press_next(main_window) 
    press_next(main_window)

    # --- 8. ค้นหาและเลือกที่อยู่ ---
    fill_field(main_window, CFG['SEARCH_ADDR_ID'], CFG['SEARCH_ADDR_VALUE'], "ค้นหาที่อยู่")
    print("[*] กดถัดไปเพื่อเริ่มค้นหา...")
    press_next(main_window)
    time.sleep(2.0)

    # --- [MANUAL LOGIC] ตรวจสอบ Popup OK ---
    popup_ok_btn = main_window.child_window(auto_id=CFG['POPUP_OK_ID'])
    if popup_ok_btn.exists(timeout=2):
        print("\n[!!!] พบ Popup (OK) -> เข้าสู่โหมดกรอกมือ")
        popup_ok_btn.click_input(); time.sleep(1)
        
        # กรอกข้อมูล Manual
        fill_field(main_window, CFG['RCV_FNAME_ID'], CFG['RCV_FNAME_VALUE'], "ชื่อ")
        fill_field(main_window, CFG['RCV_LNAME_ID'], CFG['RCV_LNAME_VALUE'], "นามสกุล")
        fill_field(main_window, CFG['ADMIN_AREA_ID'], CFG['ADMIN_AREA_VALUE'], "จว.")
        fill_field(main_window, CFG['LOCALITY_ID'], CFG['LOCALITY_VALUE'], "อ.")
        fill_field(main_window, CFG['DEPENDENT_LOCALITY_ID'], CFG['DEPENDENT_LOCALITY_VALUE'], "ต.")
        fill_field(main_window, CFG['STREET_ADDR_ID'], CFG['STREET_ADDR_VALUE'], "ที่อยู่")
        fill_field(main_window, CFG['RCV_PHONE_ID'], CFG['RCV_PHONE_VALUE'], "โทร")

        print(f"[*] (Manual) ตรวจสอบเงื่อนไขการกดถัดไป (มี Addon? : {has_addon_selected})")
        if has_addon_selected:
            print("[Logic] มี Addon -> กดถัดไป 3 ครั้ง")
            press_next(main_window); press_next(main_window); press_next(main_window)
        else:
            print("[Logic] ไม่มี Addon (ข้าม) -> กดถัดไป 1 ครั้ง")
            press_next(main_window)
            
        popup_no = main_window.child_window(auto_id=CFG['POPUP_NO_ID'])
        if popup_no.exists(timeout=3): popup_no.click_input()
        do_payment_process(main_window)
        return 

    # --- [NORMAL FLOW] ---
    group_btn = main_window.child_window(auto_id=CFG['ADDRESS_SELECT_GROUP_ID'])
    
    # [FIXED] เพิ่ม scroll_until_found ให้กับปุ่มเลือกกลุ่ม เผื่อต้องเลื่อนหา
    if scroll_until_found(group_btn, main_window, max_scrolls=10):
        print("[*] พบปุ่มเลือกกลุ่มที่อยู่ -> กำลังกดเลือก")
        group_btn.click_input()
        time.sleep(1.0)
    else:
        # ถ้าหาไม่เจอ ลองเช็คว่าข้ามไปหน้าชื่อเลยไหม
        next_step_field = main_window.child_window(auto_id=CFG['RCV_FNAME_ID'])
        if next_step_field.exists(timeout=2):
            print("[/] ระบบเลือกที่อยู่อัตโนมัติแล้ว")
        else:
            print("[!] Warning: ไม่พบปุ่มเลือกกลุ่ม และไม่พบช่องกรอกชื่อ (พยายามไปต่อ)")

    fill_field(main_window, CFG['RCV_FNAME_ID'], CFG['RCV_FNAME_VALUE'], "ชื่อผู้รับ")
    fill_field(main_window, CFG['RCV_LNAME_ID'], CFG['RCV_LNAME_VALUE'], "นามสกุลผู้รับ")
    fill_field(main_window, CFG['RCV_PHONE_ID'], CFG['RCV_PHONE_VALUE'], "เบอร์โทรศัพท์")

    print(f"[*] ตรวจสอบเงื่อนไขการกดถัดไป (มี Addon? : {has_addon_selected})")
    if has_addon_selected:
        print("[Logic] มี Addon -> กดถัดไป 3 ครั้ง")
        press_next(main_window)
        press_next(main_window)
        press_next(main_window)
    else:
        print("[Logic] ไม่มี Addon (ข้าม) -> กดถัดไป 1 ครั้ง")
        press_next(main_window)

    time.sleep(1.0)
    popup_no = main_window.child_window(auto_id=CFG['POPUP_NO_ID'])
    if popup_no.exists(timeout=3):
        popup_no.click_input()

    do_payment_process(main_window)
    print("[V] SUCCESS: Normal Flow เสร็จสมบูรณ์")

# ==================== 4. MAIN RUNNER ====================

def run_service():
    step_name = "EMS Jumbo Automation"
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