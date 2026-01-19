from pos_core import *

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Service 3 (50902)...")
    app = None
    try:
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # 1. เลือกรายการ (50902)
        SERVICE_TITLE = S_CFG['PRAISANI_3_TITLE']
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        
        main_window.child_window(title=SERVICE_TITLE, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 2. กรอกข้อมูล (ตาม AutoID ที่ระบุ)
        print("[*] Filling Data Form...")

        # 2.1 ชื่อ-สกุล (AutoID: AcctNo)
        print(f" [-] Name (AcctNo): {S_CFG['P3_NAME']}")
        main_window.child_window(auto_id=S_CFG['P3_AUTOID_NAME']).type_keys(S_CFG['P3_NAME'])
        time.sleep(0.5)

        # 2.2 เลขใบอนุญาต (AutoID: REFNO4)
        print(f" [-] License No (REFNO4): {S_CFG['P3_LICENSE']}")
        main_window.child_window(auto_id=S_CFG['P3_AUTOID_LICENSE']).type_keys(S_CFG['P3_LICENSE'])
        time.sleep(0.5)

        # 2.3 จำนวนเงินฝากส่ง (AutoID: Amount)
        print(f" [-] Amount (Amount): {S_CFG['P3_AMOUNT']}")
        main_window.child_window(auto_id=S_CFG['P3_AUTOID_AMOUNT']).type_keys(S_CFG['P3_AMOUNT'])
        time.sleep(WAIT_TIME)

        # 3. Flow: ถัดไป -> ถัดไป -> รับเงิน
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print(f"[*] Receive Payment ({RECEIVE_PAYMENT_TITLE})")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE, control_type="Text").click_input()
        
        # 4. Payment (Fast Cash)
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

    except Exception as e:
        target_app = app if (app is not None) else ctx.app
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "POS Service 3",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] Evidence Saved")
        print(f"[X] FAILED: {e}")