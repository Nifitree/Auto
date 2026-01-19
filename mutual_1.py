from mutual_core import *
import time
from evidence import save_evidence_context

def run_mutual_1():
    step_name = "Mutual Fund 1 (50308)"
    app = None
    
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name}")
        # 1. รัน Flow หลัก (เข้าเมนู -> อ่านบัตร -> ถัดไป)
        if not mutual_main(): exit()
        app, main_window = connect_main_window()

        # 2. เลือกรายการ (Direct Click)
        SERVICE_TITLE = S_CFG['MUTUAL_1_TITLE']         # 50308
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']   # SubTextTextBlock

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
        barcode_val = S_CFG.get('M1_BARCODE', '|09940001673260002988710050000')
        # AutoID: Barcode_50308
        fill_field_by_id(main_window, "Barcode_50308", barcode_val, "บาร์โค้ด")

        # 4. กดถัดไป (เพื่อไปหน้ากรอกข้อมูล)
        press_next_button(main_window)

        # 5. กรอกข้อมูล 4 ช่อง
        
        # 5.1 REFNO5: ชื่อ-นามสกุล
        name_val = S_CFG.get('M1_NAME', 'Test Name')
        fill_field_by_id(main_window, "REFNO5", name_val, "ชื่อ-นามสกุล")

        # 5.2 REFNO7: รหัสสังกัด
        ref7_val = S_CFG.get('M1_REF7', '1234')
        fill_field_by_id(main_window, "REFNO7", ref7_val, "รหัสสังกัด")

        # 5.3 REFNO6: สังกัด
        ref6_val = S_CFG.get('M1_REF6', 'Test Dept')
        fill_field_by_id(main_window, "REFNO6", ref6_val, "สังกัด")

        # 5.4 Amount: จำนวนเงิน
        amt_val = S_CFG.get('M1_AMOUNT', '500.00')
        fill_field_by_id(main_window, "Amount", amt_val, "จำนวนเงิน")

        # 6. กดถัดไป 2 ครั้ง (ยืนยัน -> รับเงิน)
        press_next_button(main_window)
        press_next_button(main_window)

        # 7. กดรับเงิน + Fast Cash
        print("[*] Clicking 'Receive Money'...")
        main_window.child_window(title="รับเงิน", control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print("[*] Clicking Fast Cash (ID: EnableFastCash)...")
        main_window.child_window(auto_id="EnableFastCash").click_input()
        time.sleep(WAIT_TIME)

        print(f"[V] SUCCESS: {step_name} Completed")

    except Exception as e:
        if app:
            save_evidence_context(app, {
                "test_name": "Mutual Service 1",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
        print(f"[X] FAILED: {step_name} error: {e}")

if __name__ == "__main__":
    run_mutual_1()