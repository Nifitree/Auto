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

def run_insurance_5():
    """Logic สำหรับ Insurance_5 (52031) - กรอกบาร์โค้ด, ชื่อ-สกุล, รับเงิน Fast Cash"""
    app = None
    try:
        step_name = "Insurance_5"
        service_title = S_CFG["TRANSACTION_5_TITLE"]
        
        print(f"\n{'='*50}\n[*] Starting: {step_name} ({service_title})")
        if not insurance_navigate_main(): 
            return
        
        app, main_window = connect_main_window()
        
        # เลือก Service 52031
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
        
        # กรอกบาร์โค้ด (Barcode_52031)
        barcode_value = S_CFG["I5_BARCODE"]
        barcode_id = S_CFG["I5_BARCODE_INPUT_ID"]
        print(f"[*] Filling Barcode ({barcode_id}): {barcode_value}")
        barcode_edit = main_window.child_window(auto_id=barcode_id, control_type="Edit")
        barcode_edit.click_input()
        main_window.type_keys(barcode_value, with_spaces=True)
        time.sleep(WAIT_TIME)
        
        # กดถัดไป
        print("[*] Clicking Next (after barcode)...")
        main_window.child_window(title=B_CFG["NEXT_BUTTON_TITLE"], auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # กรอกชื่อ-สกุล (REFNO6)
        print("[*] Filling Name (REFNO6)...")
        name_edit = main_window.child_window(auto_id=S_CFG["I5_NAME_AUTO_ID"], control_type="Edit")
        fill_if_empty(main_window, name_edit, S_CFG["I5_NAME"])
        
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
        save_evidence_context(app, {"test_name": "Insurance", "step_name": "Insurance_5", "error_message": str(e)})
        print(f"[X] FAILED: {e}")

if __name__ == "__main__":
    run_insurance_5()