from ekyc_core import run_ekyc_step, S_CFG

if __name__ == "__main__":
    if 'EKYC_1_TITLE' in S_CFG:
        run_ekyc_step("EKYC_Service_1", S_CFG['EKYC_1_TITLE'])
    else:
        print("[!] Config 'EKYC_1_TITLE' not found.")