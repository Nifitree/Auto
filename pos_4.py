from pos_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Service 4 (51119)...")

    app = None
    WAIT_TIME = 2

    try:
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # 1. ค้นหาและเลือกรายการ 51119
        SERVICE_TITLE = S_CFG['PRAISANI_4_TITLE']
        SEARCH_ID = S_CFG['SEARCH_EDIT_ID']
        
        print(f"[*] Searching for Service: {SERVICE_TITLE}")
        search_input = main_window.child_window(auto_id=SEARCH_ID, control_type="Edit")
        search_input.click_input()
        search_input.type_keys("^a{BACKSPACE}")
        search_input.type_keys(SERVICE_TITLE, with_spaces=True)
        search_input.type_keys("{ENTER}")
        time.sleep(1.5)
        
        print(f"[*] Clicking on: {SERVICE_TITLE}")
        target = main_window.child_window(title=SERVICE_TITLE, control_type="Text")
        if not target.exists(timeout=3):
            raise Exception(f"Service {SERVICE_TITLE} not found")
        target.click_input()
        time.sleep(WAIT_TIME)

        # 2. พิมพ์บาร์โค้ด (Barcode_51119)
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID4']
        BARCODE_VAL = S_CFG.get('P4_BARCODE', '')
        
        print(f"[*] Typing Barcode: {BARCODE_VAL}")
        main_window.child_window(auto_id=BARCODE_ID, control_type="Edit").click_input()
        time.sleep(0.3)
        main_window.child_window(auto_id=BARCODE_ID, control_type="Edit").type_keys(BARCODE_VAL, with_spaces=True)
        time.sleep(1)

        # 3. กดถัดไป
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 4. กรอกข้อมูล
        print("[*] Filling form fields...")
        
        # 4.1 AcctNo = ชื่อ-สกุล
        name_val = S_CFG.get('P4_NAME', 'นายทดสอบ ระบบ')
        name_id = S_CFG.get('P4_AUTOID_NAME', 'AcctNo')
        print(f" [-] Name ({name_id}): {name_val}")
        main_window.child_window(auto_id=name_id, control_type="Edit").click_input()
        time.sleep(0.3)
        main_window.child_window(auto_id=name_id, control_type="Edit").type_keys(name_val, with_spaces=True)
        
        # 4.2 REFNO7 = เบอร์โทรติดต่อ
        phone_val = S_CFG.get('P4_PHONE', '0987654321')
        phone_id = S_CFG.get('P4_AUTOID_PHONE', 'REFNO7')
        print(f" [-] Phone ({phone_id}): {phone_val}")
        main_window.child_window(auto_id=phone_id, control_type="Edit").click_input()
        time.sleep(0.3)
        main_window.child_window(auto_id=phone_id, control_type="Edit").type_keys(phone_val, with_spaces=True)
        
        time.sleep(WAIT_TIME)

        # 5. กดถัดไป 2 ครั้ง
        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print("[*] Next (3)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 6. กดรับเงิน + Fast Cash
        print("[*] Clicking 'Receive Money'...")
        main_window.child_window(title="รับเงิน", control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print("[*] Clicking Fast Cash (ID: EnableFastCash)...")
        main_window.child_window(auto_id="EnableFastCash").click_input()
        time.sleep(WAIT_TIME)

        # 7. กดเสร็จสิ้น
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"]).click_input()
        print(f"[V] POS Service 4 Success!")

    except Exception as e:
        target_app = app if (app is not None) else ctx.app
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "POS Service 4",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")