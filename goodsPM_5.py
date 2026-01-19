from goodsPM_core import *
import time
from evidence import save_evidence_context

def run_goodsPM_5_custom():
    step_name = "goodsPM_5 (Custom Flow)"
    app = None
    
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name}")
        # 1. รัน Flow หลัก
        if not goods_pm_main(): exit()
        app, main_window = connect_main_window()

        # 2. เลือกรายการ (Direct Click)
        SERVICE_TITLE = S_CFG['GOODSPM_5_TITLE']        # 50732
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']  # SubTextTextBlock

        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        try:
            main_window.child_window(
                title=SERVICE_TITLE, 
                auto_id=TRANS_TYPE, 
                control_type="Text"
            ).click_input()
        except Exception as e:
            print(f"[!] หาเมนูไม่เจอ ({SERVICE_TITLE}): {e}")

        time.sleep(WAIT_TIME)

        # 3. กรอกบาร์โค้ด
        barcode_val = S_CFG.get('PM5_BARCODE', '|0105531027264000222227176111009355300')
        # AutoID: Barcode_50732
        fill_field_by_id(main_window, "Barcode_50732", barcode_val, "บาร์โค้ด")

        # 4. กดถัดไป (เพื่อไปหน้ากรอกจำนวนเงิน)
        press_next_button(main_window)

        # 5. กรอกจำนวนเงิน
        # AutoID: Amount
        amt_val = S_CFG.get('PM5_AMOUNT', '100.00')
        fill_field_by_id(main_window, "Amount", amt_val, "จำนวนเงิน")

        # 6. กดถัดไป 2 ครั้ง (ยืนยัน -> รับเงิน)
        press_next_button(main_window)
        press_next_button(main_window)

        # 7. กดรับเงิน
        print("[*] Clicking 'Receive Money'...")
        main_window.child_window(title="รับเงิน", control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 8. กดปุ่ม Fast Cash
        print("[*] Clicking Fast Cash (ID: EnableFastCash)...")
        main_window.child_window(auto_id="EnableFastCash").click_input()
        time.sleep(WAIT_TIME)

        print(f"[V] SUCCESS: {step_name} Completed")

    except Exception as e:
        if app:
            save_evidence_context(app, {
                "test_name": "GoodsPM Service 5",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
        print(f"[X] FAILED: {step_name} error: {e}")

if __name__ == "__main__":
    run_goodsPM_5_custom()