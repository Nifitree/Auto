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

def run_insurance_4():
    """Logic สำหรับ Insurance_4 (52029) - กรอกบาร์โค้ดมั่วๆ, กด popup ตกลง, เสร็จสิ้น"""
    app = None
    try:
        step_name = "Insurance_4"
        service_title = S_CFG["TRANSACTION_4_TITLE"]
        
        print(f"\n{'='*50}\n[*] Starting: {step_name} ({service_title})")
        if not insurance_navigate_main(): 
            return
        
        app, main_window = connect_main_window()
        
        # เลือก Service 52029
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
        
        # กรอกบาร์โค้ดมั่วๆ (Barcode_52029)
        barcode_value = S_CFG["I4_BARCODE"]
        barcode_id = S_CFG["I4_BARCODE_INPUT_ID"]
        print(f"[*] Filling Barcode ({barcode_id}): {barcode_value}")
        barcode_edit = main_window.child_window(auto_id=barcode_id, control_type="Edit")
        barcode_edit.click_input()
        main_window.type_keys(barcode_value, with_spaces=True)
        time.sleep(WAIT_TIME)
        
        # กดถัดไป
        print("[*] Clicking Next (after barcode)...")
        main_window.child_window(title=B_CFG["NEXT_BUTTON_TITLE"], auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # รอ popup และกดตกลง
        print("[*] Waiting for popup...")
        time.sleep(2)
        print("[*] Clicking OK on popup...")
        ok_btn = main_window.child_window(title=S_CFG["OK_BUTTON_TITLE"], control_type="Text")
        if ok_btn.exists(timeout=3):
            ok_btn.click_input()
        else:
            # ลองหาปุ่มตกลงแบบอื่น
            ok_btn = main_window.child_window(title=S_CFG["OK_BUTTON_TITLE"], control_type="Button")
            ok_btn.click_input()
        time.sleep(WAIT_TIME)
        
        # กดเสร็จสิ้น
        print("[*] Clicking Finish...")
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print(f"[V] SUCCESS: {step_name}")
        
    except Exception as e:
        save_evidence_context(app, {"test_name": "Insurance", "step_name": "Insurance_4", "error_message": str(e)})
        print(f"[X] FAILED: {e}")

if __name__ == "__main__":
    run_insurance_4()