from mutual_core import *

def run_mutual_2():
    step_name = "Mutual Fund 2 (50308)"
    app = None
    
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name}")
        if not mutual_main(): exit()
        app, main_window = connect_main_window()
        
        # 1. เลือกรายการ
        run_mutual_transaction(main_window, S_CFG['MUTUAL_2_TITLE'])
        
        # 2. กรอกข้อมูล 4 ช่อง (AcctNo, REFNO4, REFNO5, Amount)
        print("[*] Filling 4 fields...")
        # AcctNo = เลขที่สมาชิก
        main_window.child_window(auto_id="AcctNo").click_input()
        time.sleep(0.3)
        main_window.child_window(auto_id="AcctNo").type_keys(MEMBER_ID_VALUE, with_spaces=True)
        
        # REFNO4 = เลขที่บัญชี
        main_window.child_window(auto_id="REFNO4").click_input()
        time.sleep(0.3)
        main_window.child_window(auto_id="REFNO4").type_keys(ACCOUNT_NUM_VALUE, with_spaces=True)
        
        # REFNO5 = ชื่อเจ้าของบัญชี
        main_window.child_window(auto_id="REFNO5").click_input()
        time.sleep(0.3)
        main_window.child_window(auto_id="REFNO5").type_keys(ACCOUNT_NAME_VALUE, with_spaces=True)
        
        # Amount = จำนวนเงิน
        main_window.child_window(auto_id="Amount").click_input()
        time.sleep(0.3)
        main_window.child_window(auto_id="Amount").type_keys(AMOUNT_TO_PAY_VALUE, with_spaces=True)
        time.sleep(WAIT_TIME)

        # 3. กดถัดไป 2 ครั้ง
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)
        
        # 4. กดรับเงิน + Fast Cash
        print("[*] Clicking 'Receive Money'...")
        main_window.child_window(title="รับเงิน", control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print("[*] Clicking Fast Cash (ID: EnableFastCash)...")
        main_window.child_window(auto_id="EnableFastCash").click_input()
        time.sleep(WAIT_TIME)

        print(f"[V] SUCCESS: {step_name} Completed")

    except Exception as e:
        target_app = app if (app is not None) else ctx.app
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Mutual Service 2",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")
        print(f"[X] FAILED: {e}")