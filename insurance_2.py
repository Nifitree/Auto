from insurance import *
from evidence import save_evidence_context
import time

CONFIG_FILE = "config.ini"

def read_config(filename=CONFIG_FILE):
    import configparser
    import os
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
S_CFG = CONFIG["INSURANCE_SERVICES"]

def run_insurance_2():
    """Logic สำหรับ Insurance_2 (51015) - กรอกบาร์โค้ด, ข้อมูลส่วนบุคคล, รับเงิน Fast Cash"""
    app = None
    try:
        step_name = "Insurance_2"
        service_title = S_CFG["TRANSACTION_2_TITLE"]
        
        print(f"\n{'='*50}\n[*] Starting: {step_name} ({service_title})")
        if not insurance_navigate_main(): 
            return
        
        app, main_window = connect_main_window()
        
        # เลือก Service 51015
        print(f"[*] Selecting Service: {service_title}")
        target = main_window.child_window(title=service_title, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text")
        if not scroll_until_found(target, main_window): 
            raise Exception(f"Service {service_title} not found")
        target.click_input()
        time.sleep(WAIT_TIME)
        
        # กดถัดไป 1 ครั้ง
        print("[*] Clicking Next (1)...")
        main_window.child_window(title=B_CFG["NEXT_BUTTON_TITLE"], auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # กรอกบาร์โค้ด (Barcode_51015)
        barcode_value = S_CFG["I2_BARCODE"]
        barcode_id = S_CFG["I2_BARCODE_INPUT_ID"]
        print(f"[*] Filling Barcode ({barcode_id}): {barcode_value}")
        barcode_edit = main_window.child_window(auto_id=barcode_id, control_type="Edit")
        barcode_edit.click_input()
        main_window.type_keys(barcode_value, with_spaces=True)
        time.sleep(WAIT_TIME)
        
        # กดถัดไป
        print("[*] Clicking Next (after barcode)...")
        main_window.child_window(title=B_CFG["NEXT_BUTTON_TITLE"], auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # กรอกข้อมูลส่วนบุคคล (ใช้ค่าเดียวกับ I1)
        # ชื่อ-สกุล (REFNO8)
        print("[*] Filling Name...")
        name_edit = main_window.child_window(auto_id=S_CFG["I1_NAME_AUTO_ID"], control_type="Edit")
        fill_if_empty(main_window, name_edit, S_CFG["I1_NAME"])
        
        # เลขประจำตัวประชาชน (REFNO9)
        print("[*] Filling ID Card...")
        id_card_edit = main_window.child_window(auto_id=S_CFG["I1_ID_CARD_AUTO_ID"], control_type="Edit")
        fill_if_empty(main_window, id_card_edit, S_CFG["I1_ID_CARD"])
        
        # เบอร์โทร (REFNO7)
        print("[*] Filling Phone...")
        phone_edit = main_window.child_window(auto_id=S_CFG["I1_PHONE_AUTO_ID"], control_type="Edit")
        fill_if_empty(main_window, phone_edit, S_CFG["I1_PHONE"])
        
        # เลขกรมธรรม 11 หลัก (REFNO4)
        print("[*] Filling Policy Number (11 digits)...")
        policy11_edit = main_window.child_window(auto_id=S_CFG["I1_POLICY_11_AUTO_ID"], control_type="Edit")
        fill_if_empty(main_window, policy11_edit, S_CFG["I1_POLICY_11"])
        
        # เลขที่กรมธรรม์ (AcctNo)
        print("[*] Filling Policy Account Number...")
        policy_edit = main_window.child_window(auto_id=S_CFG["I1_POLICY_AUTO_ID"], control_type="Edit")
        fill_if_empty(main_window, policy_edit, S_CFG["I1_POLICY"])
        
        # กดถัดไป 2 ครั้ง
        print("[*] Clicking Next (1/2)...")
        main_window.child_window(title=B_CFG["NEXT_BUTTON_TITLE"], auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print("[*] Clicking Next (2/2)...")
        main_window.child_window(title=B_CFG["NEXT_BUTTON_TITLE"], auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # กดรับเงิน
        print("[*] Clicking Receive Payment...")
        receive_btn = main_window.child_window(title=S_CFG["RECEIVE_PAYMENT_TITLE"], control_type="Text")
        receive_btn.click_input()
        time.sleep(WAIT_TIME)
        
        # กด Fast Cash
        print("[*] Waiting for Payment Screen (3s)...")
        time.sleep(3)
        main_window.set_focus()

        print(f"[*] Payment Action: Clicking Fast Cash...")
        fast_cash_btn = main_window.child_window(auto_id="EnableFastCash")
        
        if fast_cash_btn.exists(timeout=2):
            fast_cash_btn.click_input()
        else:
            print("[!] EnableFastCash not found, using Hotkey F")
            main_window.type_keys(T_CFG['PAYMENT_FAST'])
        
        time.sleep(WAIT_TIME)
        
        print(f"[V] SUCCESS: {step_name}")
        
    except Exception as e:
        save_evidence_context(app, {"test_name": "Insurance", "step_name": "Insurance_2", "error_message": str(e)})
        print(f"[X] FAILED: {e}")

if __name__ == "__main__":
    run_insurance_2()