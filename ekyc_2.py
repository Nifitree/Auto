from ekyc_core import run_ekyc_step, S_CFG

if __name__ == "__main__":
    if 'EKYC_2_TITLE' in S_CFG:
        run_ekyc_step("EKYC_Service_2", S_CFG['EKYC_2_TITLE'])
    else:
        print("[!] Config 'EKYC_2_TITLE' not found.")