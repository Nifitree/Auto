from mutual_core import *

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Mutual Service 4...")
    app = None
    try:
        if not mutual_main(): exit()
        app, main_window = connect_main_window()
        
        run_mutual_transaction(main_window, S_CFG['MUTUAL_4_TITLE'], barcode_id=S_CFG['BARCODE2_EDIT_AUTO_ID'])
        finish_transaction(main_window)
        print("[V] Service 4 Success!")

    except Exception as e:
        # --- [Logic แคปภาพ] ---
        target_app = app if (app is not None) else ctx.app
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Mutual Service 4",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        # ----------------------
        print(f"[X] FAILED: {e}")