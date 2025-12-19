import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys
from evidence import save_evidence_context

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

# Shipping Config
S_CFG = CONFIG["SHIPPING_AIRBUBBLE"]

# ==================== 2. HELPERS ====================

def connect_main_window():
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    return app, app.top_window()

def force_scroll_down(window):
    try:
        cfg = CONFIG["MOUSE_SCROLL"]
        center_x = cfg.getint("CENTER_X_OFFSET", fallback=300)
        center_y = cfg.getint("CENTER_Y_OFFSET", fallback=300)
        wheel_dist = cfg.getint("WHEEL_DIST", fallback=-20)
        focus_delay = cfg.getfloat("FOCUS_DELAY", fallback=0.5)
        scroll_delay = cfg.getfloat("SCROLL_DELAY", fallback=1.0)
        
        rect = window.rectangle()
        x = rect.left + center_x
        y = rect.top + center_y
        
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

def press_next(main_window):
    print(f"[*] กดปุ่ม '{NEXT_TITLE}'")
    try:
        main_window.child_window(title=NEXT_TITLE, control_type="Text").click_input()
    except:
        main_window.type_keys("{ENTER}") 
    time.sleep(WAIT_TIME)

def click_menu_button(main_window, title):
    """ฟังก์ชันช่วยสำหรับคลิกเมนูตาม Title"""
    print(f"[*] กำลังคลิกเมนู: {title}")
    btn = main_window.child_window(title=title, control_type="Text")
    if not scroll_until_found(btn, main_window):
        raise Exception(f"หาปุ่มเมนู '{title}' ไม่เจอ")
    btn.click_input()
    time.sleep(WAIT_TIME)

# ==================== 3. SHIPPING LOGIC ====================

def execute_shipping_flow(main_window):
    # --- Phase 1: เริ่มต้น ---
    click_menu_button(main_window, S_CFG['BUTTON_S_TITLE'])

    print("[*] 2. อ่านบัตรประชาชน")
    main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()
    
    print(f"[*] 3. กรอกรหัสไปรษณีย์ผู้ส่ง")
    postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    if not scroll_until_found(postal, main_window): raise Exception("ไม่พบช่องไปรษณีย์ผู้ส่ง")
    fill_if_empty(main_window, postal, POSTAL_CODE)

    phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    if not scroll_until_found(phone, main_window): raise Exception("ไม่พบช่องเบอร์โทร")
    fill_if_empty(main_window, phone, PHONE_NUMBER)

    press_next(main_window) # ถัดไป (1)

    # --- Phase 2: เลือกเมนู ---
    print("[*] 4. เลือกเมนู W -> A -> A")
    click_menu_button(main_window, S_CFG['BUTTON_W_TITLE']) 
    click_menu_button(main_window, S_CFG['BUTTON_A_TITLE'])
    click_menu_button(main_window, S_CFG['BUTTON_A_TITLE'])

    press_next(main_window) # ถัดไป (2)

    # --- Phase 3: กรอกน้ำหนัก ---
    print(f"[*] 5. กรอกน้ำหนัก: {S_CFG['WEIGHT_VALUE']}")
    weight_input = main_window.child_window(auto_id=S_CFG['WEIGHT_EDIT_ID'], control_type="Edit")
    if not scroll_until_found(weight_input, main_window): raise Exception(f"ไม่พบช่องกรอกน้ำหนัก")
    weight_input.click_input()
    main_window.type_keys(S_CFG['WEIGHT_VALUE'])
    
    press_next(main_window) # ถัดไป (3)

    # --- Phase 4: รหัสไปรษณีย์ปลายทาง ---
    dest_id = S_CFG['POSTAL_DEST_EDIT_ID']
    print(f"[*] 6. กรอกรหัสไปรษณีย์ปลายทาง: {POSTAL_CODE}")
    postal_dest = main_window.child_window(auto_id=dest_id, control_type="Edit")
    if not scroll_until_found(postal_dest, main_window): raise Exception(f"ไม่พบช่องไปรษณีย์ปลายทาง")
    fill_if_empty(main_window, postal_dest, POSTAL_CODE)

    press_next(main_window) # ถัดไป (4)

    # --- Phase 5: ดำเนินการ (ENTER) -> คลิก A ---
    print("[*] 7. กดดำเนินการ (ENTER)")
    main_window.type_keys("{ENTER}") 
    time.sleep(WAIT_TIME)
    
    service_a_id = S_CFG['SERVICE_A_BUTTON_ID']
    print(f"[*] 7.1 คลิกปุ่ม A (ID: {service_a_id})")
    btn_a = main_window.child_window(auto_id=service_a_id)
    if not scroll_until_found(btn_a, main_window): raise Exception(f"ไม่พบปุ่ม A")
    btn_a.click_input()
    time.sleep(WAIT_TIME)

    # --- Phase 6: วงเงินประกัน ---
    print(f"[*] 8. กรอกวงเงินประกัน: {S_CFG['INSURANCE_AMOUNT']}")
    coverage_btn = main_window.child_window(auto_id=S_CFG['COVERAGE_ICON_ID'])
    if not scroll_until_found(coverage_btn, main_window): raise Exception("ไม่พบปุ่ม CoverageIcon")
    coverage_btn.click_input()
    main_window.type_keys(S_CFG['INSURANCE_AMOUNT'])

    press_next(main_window) # ถัดไป (5)
    press_next(main_window) # ถัดไป (6)

    # --- Phase 7: เมนู A อีกรอบ ---
    print("[*] 9. คลิก A")
    click_menu_button(main_window, S_CFG['BUTTON_A_TITLE'])

    press_next(main_window) # ถัดไป (7)
    press_next(main_window) # ถัดไป (8)

    # --- Phase 8: ค้นหาที่อยู่ ---
    print(f"[*] 10. ค้นหาที่อยู่: {S_CFG['ADDRESS_SEARCH_TERM']}")
    search_field = main_window.child_window(auto_id=S_CFG['SEARCH_FIELD_ID'], control_type="Edit")
    if not scroll_until_found(search_field, main_window): raise Exception("ไม่พบช่องค้นหาที่อยู่")
    search_field.click_input()
    main_window.type_keys(S_CFG['ADDRESS_SEARCH_TERM'])
    
    press_next(main_window) # ถัดไป (9)

    # =================================================================
    # แก้ไข Phase 9 และ Phase 10: เพิ่ม Wait และปรับการค้นหาช่องชื่อลูกค้า
    # =================================================================
    
    # --- Phase 9: เลือกที่อยู่ (แก้ไขใหม่ใช้ AutoID Group) ---
    print(f"[*] 11. เลือกผลลัพธ์ที่อยู่ (ID: {S_CFG['ADDRESS_RESULT_ID']})")
    
    # เปลี่ยนจากหาด้วย Title เป็น AutoID และ ControlType="Group"
    addr_group = main_window.child_window(
        auto_id=S_CFG['ADDRESS_RESULT_ID'], 
        control_type="Group"
    )
    
    # เช็คว่าเจอไหม
    if not scroll_until_found(addr_group, main_window): 
        raise Exception(f"ไม่พบผลลัพธ์ที่อยู่ (ID: {S_CFG['ADDRESS_RESULT_ID']})")
    
    addr_group.click_input() # คลิกเลือก
    
    print("[*] คลิกที่อยู่แล้ว รอหน้าจอโหลด (3 วินาที)...")
    time.sleep(3) # รอโหลดหน้าถัดไป

    # --- Phase 10: ข้อมูลลูกค้า (ชื่อ/นามสกุล/เบอร์) ---
    print("[*] 12. กรอกข้อมูลลูกค้า")
    
    # [แก้ไข] เอา control_type="Edit" ออก เพราะบางที UserControl ไม่ใช่ Edit ธรรมดา
    # และใช้ wait('visible') เพื่อรอให้มั่นใจว่าช่องมาแล้วจริงๆ
    print(f" [-] รอช่องชื่อลูกค้า (ID: {S_CFG['CUST_NAME_ID']})")
    name_input = main_window.child_window(auto_id=S_CFG['CUST_NAME_ID']) 
    
    # ลองรอสูงสุด 5 วินาที ถ้าไม่มาให้ Scroll หา
    if not name_input.exists(timeout=5):
        print("[!] ไม่พบช่องชื่อทันที ลอง Scroll หา...")
        if not scroll_until_found(name_input, main_window):
            raise Exception("ไม่พบช่องชื่อลูกค้าหลัง Scroll")
            
    name_input.click_input()
    main_window.type_keys(S_CFG['CUSTOMER_NAME'])
    time.sleep(0.5)

    # นามสกุล
    print(f" [-] กรอกนามสกุล (ID: {S_CFG['CUST_LASTNAME_ID']})")
    lastname_input = main_window.child_window(auto_id=S_CFG['CUST_LASTNAME_ID']) # เอา control_type="Edit" ออกเช่นกัน
    if not lastname_input.exists(timeout=2):
        scroll_until_found(lastname_input, main_window)
        
    lastname_input.click_input()
    main_window.type_keys(S_CFG['CUSTOMER_LASTNAME'])

    # เบอร์โทร
    print(f" [-] กรอกเบอร์โทร")
    phone_cust = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    if not scroll_until_found(phone_cust, main_window):
        # เผื่อช่องเบอร์โทรอยู่ล่าง
        force_scroll_down(main_window)
        
    phone_cust.click_input()
    main_window.type_keys(PHONE_NUMBER)

    press_next(main_window) # ถัดไป (10)
    press_next(main_window) # ถัดไป (11)
    press_next(main_window) # ถัดไป (12)

    # --- Phase 11: เสร็จสิ้น (Z) ---
    print("[*] 13. กดเสร็จสิ้น (Z)")
    try:
        main_window.child_window(title=S_CFG['BUTTON_Z_TITLE'], control_type="Text").click_input()
    except:
        print("[!] หาปุ่ม Z ไม่เจอ ลองกดคีย์บอร์ดแทน")
        main_window.type_keys("z")
    time.sleep(WAIT_TIME)

# ==================== 4. ENGINE (STOP ON ERROR) ====================

def run_service():
    step_name = "Shipping Airbubble Flow"
    app = None
    print(f"\n{'='*50}\n[*] เริ่มทำรายการ: {step_name}")

    try:
        app, main_window = connect_main_window()
        execute_shipping_flow(main_window)
        print(f"[V] SUCCESS: {step_name} สำเร็จ")

    except Exception as e:
        print(f"\n[X] FAILED: {step_name} -> {e}")
        if app:
            try:
                save_evidence_context(app, {
                    "test_name": "Shipping Automation",
                    "step_name": step_name,
                    "error_message": str(e)
                })
                print("[/] บันทึกภาพ Error เรียบร้อย")
            except: pass
        
        print("!!! หยุดการทำงาน (Stop Execution) !!!")
        sys.exit(1)

# ==================== 5. ENTRY POINT ====================

if __name__ == "__main__":
    run_service()