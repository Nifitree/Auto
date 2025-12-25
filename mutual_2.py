from mutual_core import *

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Mutual Service 2 (4 Fields)...")
    app = None
    try:
        if not mutual_main(): exit()
        app, main_window = connect_main_window()
        
        # 1. เลือกรายการ
        run_mutual_transaction(main_window, S_CFG['MUTUAL_2_TITLE'])
        
        # 2. กรอกข้อมูล 4 ช่อง
        print("[*] Filling 4 fields...")
        main_window.child_window(auto_id=MEMBER_ID_AUTO_ID).type_keys(MEMBER_ID_VALUE)
        main_window.child_window(auto_id=ACCOUNT_NUM_AUTO_ID).type_keys(ACCOUNT_NUM_VALUE)
        main_window.child_window(auto_id=ACCOUNT_NAME_AUTO_ID).type_keys(ACCOUNT_NAME_VALUE)
        main_window.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID).type_keys(AMOUNT_TO_PAY_VALUE)
        time.sleep(WAIT_TIME)

        # 3. Flow
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)
        
        print("[*] Receive Payment")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE).click_input()
        
        # [STEP 7] PAYMENT SECTION
        print("[*] Waiting for Payment Screen (3s)...")
        time.sleep(3)
        main_window.set_focus()
        
        print(f"[*] Payment Action: Clicking Fast Cash (ID: EnableFastCash)...")
        
        # --- 1. Fast Cash (Default) ---
        fast_cash_btn = main_window.child_window(auto_id="EnableFastCash")
        if fast_cash_btn.exists(timeout=2):
            fast_cash_btn.click_input()
        else:
            print("[!] EnableFastCash not found, using Hotkey F")
            main_window.type_keys(T_CFG['PAYMENT_FAST'])
        
        # --- 2. Other Methods (Commented Out) ---
        # payment.pay_cash()                      # เงินสด (ระบุจำนวน)
        # payment.pay_qr()                        # QR PromptPay
        # payment.pay_credit()                    # บัตรเครดิต
        # payment.pay_debit()                     # บัตรเดบิต
        # payment.pay_check()                     # เช็คธนาคาร
        # payment.pay_alipay()                    # Alipay
        # payment.pay_wechat()                    # WeChat Pay
        # payment.pay_thp()                       # Wallet@Post
        # payment.pay_truemoney()                 # TrueMoney
        # payment.pay_qr_credit()                 # QR Credit
        
        time.sleep(WAIT_TIME)
        # =========================================================

        # 4. จบงาน
        print("[*] Next (3)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        finish_transaction(main_window)
        print("[V] Service 2 Success!")

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