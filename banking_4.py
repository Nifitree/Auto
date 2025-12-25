from banking_core import run_service, S_CFG

if __name__ == "__main__":
    run_service("Banking_4", S_CFG["BANKING_4_TITLE"], use_main=True, double_next=True)