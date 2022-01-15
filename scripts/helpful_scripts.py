"""
It's a good habit to list all frequent used functions independenly in a py
so that we can call and use them everytime we need
"""
from brownie import (
    network,
    config,
    accounts,
)

# This part is used to preset frequent used variables
LOCAL_BLOCKCHAIN_ENVIRONMENT = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
DECIMALS = 8
STARTING_PRICE = 200000000000

# This function is used to get account information
def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    # if the current ran network is a local development network or a fork network, return the address directly
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    # if it's on mainnet or a testnet, get the information from environment variables
    else:
        return accounts.add(config["wallets"]["from_key"])


