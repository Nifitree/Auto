from utility_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Utility Service 1 (50002) [Normal Selection + Barcode]...")

    app = None
    WAIT_TIME = 2

    try:
        if not utility_services_main(): exit()
        app, main_window = connect_main_window()

        SERVICE_TITLE = S_CFG['UTILITY_1_TITLE']         # 50002
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']   # SubTextTextBlock

        # 1. เลือกรายการ (จิ้มเลย ไม่ต้องค้นหา)
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANS_TYPE, control_type="Text").click_input()
        time.sleep(2) # รอโหลดหน้า

        # 2. พิมพ์บาร์โค้ด
        # ใช้ ID1 ตาม Config (Barcode_50002)
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID1']      
        BARCODE_VAL = S_CFG.get('TEST_BARCODE_VALUE1', "|0994000165463002017829830427897172608660700000079154") 
        
        main_window.child_window(auto_id=BARCODE_ID).type_keys(BARCODE_VAL)
        print(f"[*] Typed Barcode: {BARCODE_VAL}")
        time.sleep(1)

        # 3. กดถัดไป
        print("[*] Next")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 4. กดถัดไป
        print("[*] Next")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 5. กดเสร็จสิ้น
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"]).click_input()
        print(f"[*] Clicked {B_CFG['FINISH_BUTTON_TITLE']}")

    except Exception as e:
        target_app = app if (app is not None) else (ctx.app if 'ctx' in globals() else None)
        
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Utility Service 1",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")