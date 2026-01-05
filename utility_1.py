from pos_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Utility 1 (50002) [Search Mode]...")

    app = None
    WAIT_TIME = 2  # กำหนดค่าเวลาหน่วง

    try:
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # ดึงตัวแปรที่ต้องใช้
        SERVICE_TITLE = S_CFG['UTILITY_1_TITLE']       
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']  
        SEARCH_ID = S_CFG['SEARCH_EDIT_ID']             

        # 1. ค้นหาและเลือกรายการ
        print(f"[*] Searching for Service: {SERVICE_TITLE}")
        
        # 1.1 พิมพ์รหัสลงในช่องค้นหาก่อน
        main_window.child_window(auto_id=SEARCH_ID).type_keys(SERVICE_TITLE)
        time.sleep(2) # รอให้รายการกรองขึ้นมา

        # 1.2 คลิกเลือกรายการ
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANS_TYPE, control_type="Text").click_input()
        time.sleep(2) # รอโหลดหน้า

        # 2. พิมพ์บาร์โค้ด
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID1']
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
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"]).click_input()
        print(f"[*] Clicked {B_CFG['FINISH_BUTTON_TITLE']}")

    except Exception as e:
        target_app = app if (app is not None) else ctx.app
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Utility 1", # เปลี่ยนชื่อเทสให้ตรง
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")