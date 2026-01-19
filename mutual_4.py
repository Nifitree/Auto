from mutual_core import *

def run_mutual_4():
    step_name = "Mutual Fund 4 (51130)"
    app = None
    
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name}")
        if not mutual_main(): exit()
        app, main_window = connect_main_window()
        
        # 1. เลือกรายการ (MUTUAL_4_TITLE = 51130)
        print(f"[*] Selecting: {S_CFG['MUTUAL_4_TITLE']}")
        target = main_window.child_window(title=S_CFG['MUTUAL_4_TITLE'], auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text")
        if not scroll_until_found(target, main_window):
            raise Exception(f"Item {S_CFG['MUTUAL_4_TITLE']} not found")
        target.click_input()
        time.sleep(WAIT_TIME)
        
        # 2. กรอก Barcode (Barcode_51130)
        barcode_value = S_CFG.get('M4_BARCODE', '')
        print(f"[*] Typing Barcode: {barcode_value}")
        barcode_ctrl = main_window.child_window(auto_id=S_CFG['BARCODE2_EDIT_AUTO_ID'], control_type="Edit")
        barcode_ctrl.wait('visible', timeout=WAIT_TIME).click_input()
        main_window.type_keys(barcode_value)
        time.sleep(0.5)
        
        # 3. กดถัดไป
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)
        
        # 4. กรอก REFNO7 (ชื่อผู้ฝาก)
        depositor_name = S_CFG.get('M4_DEPOSITOR_NAME', 'นายทดสอบ ระบบ')
        depositor_id = S_CFG.get('M4_DEPOSITOR_AUTO_ID', 'REFNO7')
        print(f"[*] Filling Depositor Name ({depositor_id}): {depositor_name}")
        main_window.child_window(auto_id=depositor_id).click_input()
        time.sleep(0.3)
        main_window.child_window(auto_id=depositor_id).type_keys(depositor_name, with_spaces=True)
        time.sleep(WAIT_TIME)
        
        # 5. กดถัดไป
        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)
        
        # 6. กดตกลง (Popup)
        print("[*] Clicking OK on popup...")
        ok_btn = main_window.child_window(title=S_CFG.get('OK_BUTTON_TITLE', 'ตกลง'), control_type="Text")
        if ok_btn.exists(timeout=3):
            ok_btn.click_input()
            time.sleep(WAIT_TIME)
        
        # 7. กดเสร็จสิ้น
        finish_transaction(main_window)
        print(f"[V] SUCCESS: {step_name} Completed")

    except Exception as e:
        target_app = app if (app is not None) else ctx.app
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Mutual Service 4",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")
        print(f"[X] FAILED: {e}")

if __name__ == "__main__":
    run_mutual_4()