from banking_core import run_service, S_CFG

if __name__ == "__main__":
    run_service("Banking_12", S_CFG["BANKING_12_TITLE"], use_search=True)