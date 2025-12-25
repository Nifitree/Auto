from mutual_core import *

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Mutual Service 3...")
    try:
        if not mutual_main(): exit()
        app, main_window = connect_main_window()
        
        # 1. Select Item
        run_mutual_transaction(main_window, S_CFG['MUTUAL_3_TITLE'])
        
        # 2. Fill Data & Combobox
        print("[*] Filling Data & Combobox...")
        main_window.child_window(auto_id=MEMBER_ID_AUTO_ID).type_keys(MEMBER_ID_VALUE)
        time.sleep(0.5)
        
        select_combobox_item(main_window, LOAN_TYPE_COMBO_ID, LOAN_TYPE_SELECT, WAIT_TIME)
        time.sleep(WAIT_TIME)

        main_window.child_window(auto_id=ACCOUNT_NAME_AUTO_ID).type_keys(ACCOUNT_NAME_VALUE)
        main_window.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID).type_keys(AMOUNT_TO_PAY_VALUE)
        time.sleep(WAIT_TIME)

        # 3. Next -> Next -> Receive -> Pay -> Next -> Finish
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)
        
        print("[*] Receive Payment")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE).click_input()
        time.sleep(WAIT_TIME)

        # ---------------------------------------------------------
        # [STEP 7] PAYMENT SELECTION (เลือก 1 วิธี)
        # ---------------------------------------------------------
        print("[*] 7. เข้าสู่หน้าจอการชำระเงินและดำเนินการ...")
        
        # payment.pay_cash()                      # 1. เงินสด (ระบุจำนวนเอง)
        main_window.type_keys(T_CFG['PAYMENT_FAST']) # 2. เงินสด (ด่วน/เต็มจำนวน - Hotkey F)
        # payment.pay_qr()                        # 3. QR PromptPay
        # payment.pay_credit()                    # 4. บัตรเครดิต
        # payment.pay_debit()                     # 5. บัตรเดบิต
        # payment.pay_check()                     # 6. เช็คธนาคาร
        # payment.pay_alipay()                    # 7. Alipay
        # payment.pay_wechat()                    # 8. WeChat Pay
        # payment.pay_thp()                       # 9. Wallet@Post
        # payment.pay_truemoney()                 # 10. TrueMoney Wallet
        # payment.pay_qr_credit()                 # 11. QR Credit
        
        time.sleep(WAIT_TIME)
        # ---------------------------------------------------------
        
        print("[*] Next (3)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        finish_transaction(main_window)
        print("[V] Service 3 Success!")

    except Exception as e:
        print(f"[X] FAILED: {e}")