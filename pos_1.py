from pos_core import *

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Service 1 (1819)...")
    app = None
    try:
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # 1. เลือกรายการ
        SERVICE_TITLE = S_CFG['PRAISANI_1_TITLE'] 
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 2. กรอกข้อมูล (ดึงจาก S_CFG ใน [PRAISANI_POS_SERVICES])
        print("[*] Filling Data Form...")

        # เลขที่สมาชิก
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_MEMBER']).type_keys(S_CFG['P1_MEMBER_ID'])
        time.sleep(0.5)

        # ประเภทเงิน
        print(f" [-] Selecting Money Type: {S_CFG['P1_MONEY_TYPE']} (ID: {S_CFG['P1_AUTOID_MONEY_TYPE']})")
        
        # ใช้ Helper Function เลือกรายการจาก Dropdown ได้เลย
        select_combobox_item(
            main_window, 
            combo_auto_id=S_CFG['P1_AUTOID_MONEY_TYPE'],  # D_INT_01_Lookup
            item_title=S_CFG['P1_MONEY_TYPE'],            # เติมเงิน
            sleep=WAIT_TIME
        )
        time.sleep(0.5)

        # ชื่อ-สกุล
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_NAME']).type_keys(S_CFG['P1_NAME'])
        time.sleep(0.5)

        # เลขที่บัตรประชาชน
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_IDCARD']).type_keys(S_CFG['P1_ID_CARD'])
        time.sleep(0.5)

        # หมายเหตุ
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_NOTE']).type_keys(S_CFG['P1_NOTE'])
        time.sleep(0.5)

        # จำนวนเงิน
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_AMOUNT']).type_keys(S_CFG['P1_AMOUNT'])
        time.sleep(0.5)
        
        # จำนวนเงินรวม (ถ้ามี)
        amt_total = main_window.child_window(auto_id=S_CFG['P1_AUTOID_TOTAL'])
        if amt_total.exists(timeout=1):
             amt_total.type_keys(S_CFG['P1_AMOUNT'])

        time.sleep(WAIT_TIME)

        # 3. Flow ถัดไป -> รับเงิน -> จ่ายเงิน
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
                "test_name": "POS Service 1",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] Evidence Saved")
        print(f"[X] FAILED: {e}")