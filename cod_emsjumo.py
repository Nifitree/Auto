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

# ==================== 2. HELPERS (แก้ไขใหม่) ====================

def connect_main_window():
    return ctx.connect()

def force_scroll_down(window):
    """Scroll แบบใช้เมาส์ (Backup)"""
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
    if control is None: return False
    if control.exists(timeout=1): return True
    print(f"[*] กำลังเลื่อนหน้าจอหา Element... (Max {max_scrolls})")
    for _ in range(max_scrolls):
        force_scroll_down(window)
        if control.exists(timeout=1): return True
    return False

def fill_if_empty(window, control, value):
    try: text = control.texts()[0].strip()
    except: text = ""
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
        if btn.exists(): btn.click_input()
        else: main_window.type_keys("{ENTER}")
    except: main_window.type_keys("{ENTER}") 
    time.sleep(WAIT_TIME)

def click_menu_button(main_window, title):
    print(f"[*] คลิกเมนู: {title}")
    btn = main_window.child_window(title=title, control_type="Text")
    if not scroll_until_found(btn, main_window):
        raise Exception(f"หาปุ่มเมนู '{title}' ไม่เจอ")
    btn.click_input()
    time.sleep(WAIT_TIME)

# --- [NEW Helper 1] กดลูกศรเลื่อนหน้าจอ ---
SCROLL_DOWN_BTN_ID = S_CFG.get('SCROLL_DOWN_BTN_ID', 'LineDown')

def click_scroll_arrow_smart(window, repeat=3):
    """คลิกปุ่ม LineDown เพื่อเลื่อนหน้าจอลง"""
    try:
        scroll_btn = window.child_window(auto_id=SCROLL_DOWN_BTN_ID)
        if scroll_btn.exists(timeout=0.5):
            for _ in range(repeat):
                scroll_btn.click_input()
                time.sleep(0.2)
            return True
        else:
            print(f"[!] Warning: ไม่พบปุ่ม Scroll (ID: {SCROLL_DOWN_BTN_ID})")
            return False
    except Exception as e:
        print(f"[!] Warning: Scroll ผิดพลาด: {e}")
        return False

# --- [NEW Helper 2] ค้นหาปุ่ม + เช็ค Safe Zone + เลื่อนลงอัตโนมัติ ---
def find_and_click_smart(window, target_title, max_loops=15):
    """
    ค้นหาปุ่มจาก Title แบบฉลาด:
    1. หาปุ่ม
    2. ถ้าเจอ -> เช็คว่าอยู่ใน Safe Zone (ไม่ตกขอบล่าง) ไหม?
    3. ถ้าไม่เจอ หรือ ตกขอบ -> สั่งเลื่อนลง แล้วหาใหม่
    """
    print(f"[*] Scanning for '{target_title}' (Smart Scroll)...")
    
    for i in range(max_loops):
        # 1. ลองหาปุ่ม
        btn = window.child_window(title=target_title, control_type="Text")
        
        # 2. เช็คการมีอยู่
        if btn.exists(timeout=0.5):
            rect = btn.rectangle()
            win_rect = window.rectangle()
            
            # [Vertical Safe Zone] : พื้นที่ปลอดภัยคือ ส่วนบนถึง 90% ของความสูงหน้าต่าง
            # (เผื่อ Footer ด้านล่างบัง 10%)
            safe_limit = win_rect.top + (win_rect.height() * 0.90)
            
            # เช็คว่าขอบล่างของปุ่ม (rect.bottom) อยู่ในเขตปลอดภัยไหม
            if rect.bottom < safe_limit and rect.top > win_rect.top:
                print(f"[/] Found '{target_title}' in Safe Zone -> Clicking")
                try:
                    btn.click_input()
                except:
                    # ถ้าคลิกไม่ได้ ให้กด Enter ย้ำ
                    btn.set_focus()
                    window.type_keys("{ENTER}")
                return True
            else:
                print(f"[*] Found '{target_title}' but out of bounds (Hidden) -> Scrolling Down")
        else:
            print(f"[*] '{target_title}' not found in view -> Scrolling Down")
        
        # 3. สั่งเลื่อนลง
        click_scroll_arrow_smart(window, repeat=4) # กดลง 4 ที
        time.sleep(0.8) # รอหน้าจอขยับ
        
    raise Exception(f"Could not find or click '{target_title}' after {max_loops} scrolls.")

# ==================== 3. LOGIC ====================

def execute_cod_ems_flow(main_window):
    if main_window is None:
        raise Exception("Main Window is None (Connection Failed)")

    # --- 1. เข้าเมนู S และข้อมูลผู้ส่ง ---
    click_menu_button(main_window, S_CFG['BUTTON_S_TITLE'])

    print("[*] อ่านบัตรประชาชน")
    main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()
    
    print("[*] ตรวจสอบรหัสไปรษณีย์ผู้ส่ง")
    postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    if scroll_until_found(postal, main_window):
        fill_if_empty(main_window, postal, POSTAL_CODE)

    # [FIXED Logic] เลื่อนหาเบอร์โทรให้เจอก่อน
    print("[*] ตรวจสอบเบอร์โทร")
    phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    
    # เลื่อนหา (max_scrolls=5)
    if scroll_until_found(phone, main_window, max_scrolls=5):
        # ใช้ fill_if_empty แบบใหม่ จะพิมพ์ถูกช่องแน่นอน
        fill_if_empty(main_window, phone, PHONE_NUMBER)
    else:
        print("[!] Warning: หาช่องเบอร์โทรไม่เจอ (ข้าม)")

    press_next(main_window)
    
    # --- 2. เข้าเมนู 4 -> A ---
    print("[*] เข้าเมนู 4 -> A")

    # [USE SMART FUNCTION] ใช้ฟังก์ชันใหม่ที่นี่
    btn_4_title = S_CFG['BUTTON_4_TITLE']
    
    # เรียกใช้ Helper ใหม่: หา -> เช็คขอบ -> เลื่อนลง -> คลิก
    find_and_click_smart(main_window, btn_4_title)
    
    time.sleep(WAIT_TIME)

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

    # --- 4. กรอกขนาด (กว้าง x ยาว x สูง) ---
    print("[*] กรอกขนาดพัสดุ (L/W/H)")
    fill_field(main_window, S_CFG['LENGTH_INPUT_ID'], S_CFG['DIM_L_VALUE'], "Length")
    fill_field(main_window, S_CFG['WIDTH_INPUT_ID'], S_CFG['DIM_W_VALUE'], "Width")
    fill_field(main_window, S_CFG['HEIGHT_INPUT_ID'], S_CFG['DIM_H_VALUE'], "Height")

    press_next(main_window) # ถัดไป (3)

    # --- 5. กรอกรหัสไปรษณีย์ปลายทาง ---
    fill_field(main_window, S_CFG['DEST_POSTAL_ID'], S_CFG['DEST_POSTAL_VALUE'], "รหัสไปรษณีย์ปลายทาง")
    press_next(main_window) # ถัดไป (4)

    # --- 6. เลือกบริการ COD EMS และกรอกรายละเอียด ---
    # หมายเหตุ: ตรงนี้คุณใช้ ID2 หรือ ID1 เช็ค Config ให้ดีนะครับ (ในโค้ดเดิมใช้ ID2)
    print(f"[*] เลือกบริการ (ID: {S_CFG['SERVICE_SELECTION_ID2']})")
    service_btn = main_window.child_window(auto_id=S_CFG['SERVICE_SELECTION_ID2'])
    if not scroll_until_found(service_btn, main_window):
        raise Exception("ไม่พบตัวเลือกบริการ COD EMS")
    service_btn.click_input()
    time.sleep(0.5)

    fill_field(main_window, S_CFG['PACKAGE_NUM_ID'], S_CFG['PACKAGE_NUM_VALUE'], "เลขที่ขนส่งตั้งต้น")
    fill_field(main_window, S_CFG['RETURN_REASON_ID'], S_CFG['RETURN_REASON_VALUE'], "เหตุผลในการส่งคืน")
    press_next(main_window) # ถัดไป (5) - จบขั้นตอนการกรอก

    # --- 7. จัดการ Popup (ถ้ามี) ---
    print("[*] ตรวจสอบ Popup...")
    time.sleep(1.0) # รอ Popup เด้ง
    popup_ok = main_window.child_window(title=S_CFG['POPUP_OK_TITLE'], control_type="Button")
    
    if popup_ok.exists(timeout=3):
        print("[!] พบ Popup -> กดตกลง")
        popup_ok.click_input()
    else:
        print("[-] ไม่พบ Popup (ข้าม)")

    # [STEP 8] กดกลับ (Back) -> กดเสร็จสิ้น (Finish)
    # =======================================================
    print("[*] ขั้นตอนสุดท้าย: กด 'กลับ' -> กด 'เสร็จสิ้น'")
    time.sleep(1.0)

    # 8.1 กดปุ่มย้อนกลับ
    back_title = S_CFG.get('BTN_BACK_TITLE', 'กลับ')
    back_id = S_CFG.get('BTN_BACK_ID', 'LocalCommand_Previous')
    print(f"[*] กำลังหาปุ่มกลับ (Title: '{back_title}' / ID: '{back_id}')")

    back_clicked = False
    try:
        # ลองหาจาก Title ก่อน (แบบ Text)
        back_btn = main_window.child_window(title=back_title, control_type="Text")
        if back_btn.exists(timeout=1):
            print(f"[/] พบปุ่มกลับ (Title: Text) -> คลิก")
            back_btn.click_input()
            back_clicked = True
        else:
            # ลองหาจาก Title แบบ Button
            back_btn = main_window.child_window(title=back_title, control_type="Button")
            if back_btn.exists(timeout=1):
                print(f"[/] พบปุ่มกลับ (Title: Button) -> คลิก")
                back_btn.click_input()
                back_clicked = True
            else:
                # ลองหาจาก AutomationId
                back_btn = main_window.child_window(auto_id=back_id)
                if back_btn.exists(timeout=1):
                    print(f"[/] พบปุ่มกลับ (ID: {back_id}) -> คลิก")
                    back_btn.click_input()
                    back_clicked = True
                    
        if back_clicked:
            time.sleep(WAIT_TIME)
        else:
            print("[!] หาปุ่มย้อนกลับไม่เจอเลย ทุกวิธี")
    except Exception as e:
        print(f"[!] Error กดปุ่มย้อนกลับ: {e}")

    # 8.2 กดเสร็จสิ้น
    finish_title = S_CFG.get('BTN_FINISH_TITLE', 'เสร็จสิ้น')
    print(f"[*] กำลังหาปุ่ม: {finish_title}")
    
    try:
        finish_btn = main_window.child_window(title=finish_title, control_type="Text")
        if not finish_btn.exists(timeout=2):
             finish_btn = main_window.child_window(title=finish_title, control_type="Button")
             
        if finish_btn.exists():
            finish_btn.click_input()
            print("[V] กดเสร็จสิ้นเรียบร้อย")
        else:
             print(f"[!] หาปุ่ม '{finish_title}' ไม่เจอ")
    except Exception as e:
        print(f"[!] Error กดเสร็จสิ้น: {e}")

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