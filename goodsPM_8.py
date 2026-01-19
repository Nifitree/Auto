from goodsPM_core import *
import time
from evidence import save_evidence_context

def run_goodsPM_8_custom():
    step_name = "goodsPM_8 (Custom Flow)"
    app = None
    
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name}")
        # 1. รัน Flow หลัก
        if not goods_pm_main(): exit()
        app, main_window = connect_main_window()

        # 2. ค้นหาและเลือกรายการ (ใช้ระบบ Search ตามคำขอ)
        SERVICE_TITLE = S_CFG['GOODSPM_8_TITLE'] # 51003
        
        # เรียกใช้ฟังก์ชัน Search จาก Core
        search_and_select_service(main_window, SERVICE_TITLE)

        # 3. กรอกบาร์โค้ด
        barcode_val = S_CFG.get('PM8_BARCODE', '|01055461016270014742100871810176715158000')
        
        # AutoID: Barcode_51003 (อิงตามชื่อบริการ)
        fill_field_by_id(main_window, f"Barcode_{SERVICE_TITLE}", barcode_val, "บาร์โค้ด")

        # 4. กดถัดไป (เพื่อไปหน้ากรอกข้อมูล)
        press_next_button(main_window)

        # 5. กรอกข้อมูล (ชื่อ และ จำนวนเงิน)
        
        # 5.1 REFNO5: ชื่อ-สกุล
        name_val = S_CFG.get('PM8_NAME', 'Test Name')
        fill_field_by_id(main_window, "REFNO5", name_val, "ชื่อ-สกุล")

        # 5.2 Amount: จำนวนเงิน
        amt_val = S_CFG.get('PM8_AMOUNT', '100.00')
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
                "test_name": "GoodsPM Service 8",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
        print(f"[X] FAILED: {step_name} error: {e}")

if __name__ == "__main__":
    run_goodsPM_8_custom()