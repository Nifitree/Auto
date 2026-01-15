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

# COD EMS Config
S_CFG = CONFIG["COD_EMS"]
ctx = AppContext(window_title_regex=WINDOW_TITLE)

# ==================== 2. HELPERS ====================

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
    if control.exists(timeout=1):
        return True
    print(f"[*] กำลังเลื่อนหน้าจอหา Element... (Max {max_scrolls})")
    for _ in range(max_scrolls):
        force_scroll_down(window)
        if control.exists(timeout=1):
            return True
    return False

def fill_if_empty(window, control, value):
    try:
        text = control.texts()[0].strip()
    except:
        text = ""
    if not text:
        control.click_input()
        time.sleep(0.5) 
        control.type_keys(value, with_spaces=True)

def fill_field(window, auto_id, value, description=""):
    print(f"[*] {description}: {value}")
    control = window.child_window(auto_id=auto_id)
    if not scroll_until_found(control, window):
        raise Exception(f"ไม่พบช่อง {description} (ID: {auto_id})")
    control.click_input()
    time.sleep(0.5)
    control.type_keys(value, with_spaces=True)

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

# ==================== 3. LOGIC ====================

def execute_cod_ems_flow(main_window):
    # --- 1. เข้าเมนู S และข้อมูลผู้ส่ง ---
    click_menu_button(main_window, S_CFG['BUTTON_S_TITLE'])

    print("[*] อ่านบัตรประชาชน")
    main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()
    
    print("[*] ตรวจสอบรหัสไปรษณีย์ผู้ส่ง")
    postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    if scroll_until_found(postal, main_window):
        fill_if_empty(main_window, postal, POSTAL_CODE)

    print("[*] ตรวจสอบเบอร์โทร (กำลังเลื่อนหา...)")
    phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    if scroll_until_found(phone, main_window, max_scrolls=5):
        fill_if_empty(main_window, phone, PHONE_NUMBER)
    else:
        print("[!] Warning: หาช่องเบอร์โทรไม่เจอ (ข้าม)")

    press_next(main_window)
    
    # --- 2. เข้าเมนู 4 -> A ---
    print("[*] เข้าเมนู 4 -> A")

    # =======================================================
    # [FIXED] ใช้การจิ้มปุ่ม Scroll Down (LineDown) จนกว่าจะเจอ
    # =======================================================
    btn_4_title = S_CFG['BUTTON_4_TITLE']
    print(f"[*] กำลังเลื่อนหาปุ่มเมนู: {btn_4_title}")
    
    target_btn = main_window.child_window(title=btn_4_title, control_type="Text").click_input()
    
    # อ่านชื่อปุ่มจาก Config (ถ้าไม่มีใช้ LineDown)
    scroll_id = S_CFG.get('SCROLL_DOWN_BTN_ID', 'LineDown')
    scroll_down_btn = main_window.child_window(auto_id=scroll_id) 
    
    found = False
    for i in range(20): # กดสูงสุด 20 ครั้ง
        if target_btn.exists(timeout=0.5):
            print(f"[/] เจอเมนู '{btn_4_title}' แล้ว!")
            found = True
            break
            
        print(f"[*] ยังไม่เจอ... จิ้มปุ่ม {scroll_id} (ครั้งที่ {i+1})")
        
        try:
            if scroll_down_btn.exists():
                scroll_down_btn.click_input()
            else:
                print(f"[!] ไม่เจอปุ่ม {scroll_id} -> ใช้คีย์บอร์ด PageDown แทน")
                main_window.type_keys("{PGDN}")
        except:
            main_window.type_keys("{DOWN 3}") # กดลูกศรลงแก้ขัด

        time.sleep(0.5)

    if found:
        try:
            target_btn.click_input()
        except:
            print("[!] เจอแล้วแต่คลิกยาก -> ขยับลงอีกนิด")
            main_window.type_keys("{DOWN}")
            target_btn.click_input()
        time.sleep(WAIT_TIME)
    else:
        raise Exception(f"หาปุ่มเมนู '{btn_4_title}' ไม่เจอ (ลองเลื่อนลงสุดแล้ว)")

    # ปุ่ม A
    click_menu_button(main_window, S_CFG['BUTTON_A_TITLE'])
    
    press_next(main_window) # ถัดไป (1)

    # --- 3. ยืนยันและกรอกน้ำหนัก ---
    print(f"[*] กดยืนยัน ID: {S_CFG['CONFIRM_BTN_ID']}")
    confirm_btn = main_window.child_window(auto_id=S_CFG['CONFIRM_BTN_ID'])
    if not scroll_until_found(confirm_btn, main_window):
        raise Exception("ไม่พบปุ่มยืนยัน (Confirmed)")
    confirm_btn.click_input()
    time.sleep(0.5)

    fill_field(main_window, S_CFG['WEIGHT_INPUT_ID'], S_CFG['WEIGHT_VALUE'], "กรอกน้ำหนัก")
    press_next(main_window) # ถัดไป (2)

    # --- 4. กรอกขนาด ---
    print("[*] กรอกขนาดพัสดุ (L/W/H)")
    fill_field(main_window, S_CFG['LENGTH_INPUT_ID'], S_CFG['DIM_L_VALUE'], "Length")
    fill_field(main_window, S_CFG['WIDTH_INPUT_ID'], S_CFG['DIM_W_VALUE'], "Width")
    fill_field(main_window, S_CFG['HEIGHT_INPUT_ID'], S_CFG['DIM_H_VALUE'], "Height")
    press_next(main_window) # ถัดไป (3)

    # --- 5. กรอกรหัสไปรษณีย์ปลายทาง ---
    fill_field(main_window, S_CFG['DEST_POSTAL_ID'], S_CFG['DEST_POSTAL_VALUE'], "รหัสไปรษณีย์ปลายทาง")
    press_next(main_window) # ถัดไป (4)

    # --- 6. เลือกบริการ COD EMS ---
    print(f"[*] เลือกบริการ (ID: {S_CFG['SERVICE_SELECTION_ID1']})")
    service_btn = main_window.child_window(auto_id=S_CFG['SERVICE_SELECTION_ID1'])
    if not scroll_until_found(service_btn, main_window):
        raise Exception("ไม่พบตัวเลือกบริการ COD EMS")
    service_btn.click_input()
    time.sleep(0.5)

    fill_field(main_window, S_CFG['PACKAGE_NUM_ID'], S_CFG['PACKAGE_NUM_VALUE'], "เลขที่ขนส่งตั้งต้น")
    fill_field(main_window, S_CFG['RETURN_REASON_ID'], S_CFG['RETURN_REASON_VALUE'], "เหตุผลในการส่งคืน")
    press_next(main_window) # ถัดไป (5)

    # --- 7. Popup ---
    print("[*] ตรวจสอบ Popup...")
    time.sleep(1.0) 
    popup_ok = main_window.child_window(title=S_CFG['POPUP_OK_TITLE'], control_type="Button")
    if popup_ok.exists(timeout=3):
        print("[!] พบ Popup -> กดตกลง")
        popup_ok.click_input()
    else:
        print("[-] ไม่พบ Popup (ข้าม)")

# ==================== 4. MAIN RUNNER ====================

def run_service():
    step_name = "COD EMS Flow"
    app = None
    print(f"\n{'='*50}\n[*] เริ่มทำรายการ: {step_name}")
    try:
        app, main_window = connect_main_window()
        execute_cod_ems_flow(main_window)
        print(f"[V] SUCCESS: {step_name} สำเร็จ")
    except Exception as e:
        print(f"\n[X] FAILED: {step_name} -> {e}")
        if app:
            try:
                save_evidence_context(app, {
                    "test_name": "COD EMS Automation",
                    "step_name": step_name,
                    "error_message": str(e)
                })
                print("[/] บันทึกภาพ Error เรียบร้อย")
            except: pass
        sys.exit(1)

if __name__ == "__main__":
    run_service()