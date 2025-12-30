from pos_core import *
import configparser
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Service 4 (51119)...")
    
    # อ่าน Config
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    S_CFG = config['PRAISANI_POS_SERVICES']
    M_CFG = config['PRAISANI_POS_MAIN']

    app = None
    try:
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # --- ส่วน Logic ที่แก้ไขใหม่ (เลียนแบบ pos_2) ---

        # 1. เลือกรายการ 51119 (ใช้รูปแบบเดียวกับ pos_2 เป๊ะๆ)
        SERVICE_TITLE = S_CFG['PRAISANI_4_TITLE']
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE'] # ค่าคือ SubTextTextBlock
        
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANS_TYPE, control_type="Text").click_input()
        time.sleep(2) # รอโหลดหน้า

        # 2. พิมพ์บาร์โค้ด
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID']
        BARCODE_VAL = S_CFG['TEST_BARCODE_VALUE']
        
        main_window.child_window(auto_id=BARCODE_ID).type_keys(BARCODE_VAL)
        print(f"[*] Typed Barcode: {BARCODE_VAL}")
        time.sleep(1)

        # 3. กดถัดไป
        print("[*] Next ")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 4. กดตกลง
        main_window.child_window(title=B_CFG["ACCEPT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        print("[*] Clicked OK")
        time.sleep(1)

        # 5. กดเสร็จสิ้น
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        print(f"[*] Clicked {FINISH_BTN}")
        
    except Exception as e:
        target_app = app if (app is not None) else ctx.app
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Mutual Service 3",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")