def dump_tree(window):
    print("\n========== UI TREE ==========")
    try:
        window.print_control_identifiers()
    except Exception as e:
        print("[X] Dump tree failed:", e)
    print("================================\n")
