from pos_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Service 4 (51119)...")

    app = None
    try:
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # --- ส่วน Logic ที่แก้ไขใหม่ ---

        # 1. ค้นหาและเลือกรายการ 51119 (ใช้ช่องค้นหา)
        SERVICE_TITLE = S_CFG['PRAISANI_4_TITLE']
        SEARCH_ID = S_CFG['SEARCH_EDIT_ID']
        
        print(f"[*] Searching for Service: {SERVICE_TITLE}")
        
        # พิมพ์รหัสในช่องค้นหา
        search_input = main_window.child_window(auto_id=SEARCH_ID, control_type="Edit")
        search_input.click_input()
        search_input.type_keys("^a{BACKSPACE}")  # ล้างค่าเก่า
        search_input.type_keys(SERVICE_TITLE, with_spaces=True)
        search_input.type_keys("{ENTER}")
        time.sleep(1.5)
        
        # คลิกรายการที่ค้นหาเจอ
        print(f"[*] Clicking on: {SERVICE_TITLE}")
        target = main_window.child_window(title=SERVICE_TITLE, control_type="Text")
        if not target.exists(timeout=3):
            raise Exception(f"Service {SERVICE_TITLE} not found in search results")
        target.click_input()
        time.sleep(2) # รอโหลดหน้า

        # 2. พิมพ์บาร์โค้ด
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID4']
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
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"],).click_input()
        print(f"[*] Clicked {B_CFG['FINISH_BUTTON_TITLE']}")

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