from mutual_core import mutual_main, run_mutual_transaction, finish_transaction, connect_main_window, S_CFG

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Mutual Service 4...")
    try:
        if not mutual_main(): exit()
        app, main_window = connect_main_window()
        
        run_mutual_transaction(main_window, S_CFG['MUTUAL_4_TITLE'], barcode_id=S_CFG['BARCODE2_EDIT_AUTO_ID'])
        finish_transaction(main_window)
        print("[V] Service 4 Success!")
    except Exception as e:
        print(f"[X] FAILED: {e}")