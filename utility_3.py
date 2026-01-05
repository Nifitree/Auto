from utility_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Utility Service 3 (50777) [Normal Selection + Barcode]...")

    app = None
    WAIT_TIME = 2

    try:
        # 1. รัน Main Flow
        if not utility_services_main(): exit()
        app, main_window = connect_main_window()

        # --- ส่วน Logic ---

        SERVICE_TITLE = S_CFG['UTILITY_3_TITLE']         # 50777
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']   

        # 1. เลือกรายการ
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANS_TYPE, control_type="Text").click_input()
        time.sleep(2) 

        # 2. พิมพ์บาร์โค้ด
        # ใช้ ID3 ตาม Config
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID3']      # Barcode_50777
        BARCODE_VAL = S_CFG.get('TEST_BARCODE_VALUE', "9999999999") 
        
        main_window.child_window(auto_id=BARCODE_ID).type_keys(BARCODE_VAL)
        print(f"[*] Typed Barcode: {BARCODE_VAL}")
        time.sleep(1)

        # 3. กดถัดไป
        print("[*] Next")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 4. กดตกลง
        print("[*] Clicked OK")
        accept_title = B_CFG.get("ACCEPT_TITLE", "ตกลง")
        main_window.child_window(title=accept_title, auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(1)

        # 5. กดเสร็จสิ้น
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"]).click_input()
        print(f"[*] Clicked {B_CFG['FINISH_BUTTON_TITLE']}")

    except Exception as e:
        target_app = app if (app is not None) else (ctx.app if 'ctx' in globals() else None)
        
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Utility Service 3",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")