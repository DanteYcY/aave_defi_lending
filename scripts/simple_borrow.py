from scripts.helpful_scripts import get_account
from brownie import interface, config, network
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork-dev"]:
        get_weth()
    print(erc20_address)
    lending_pool = get_lending_pool()
    # Approve sending out ERC tokens
    # approve_erc20(erc20_address, lending_pool.address, amount, account)
    # print("Depositing!")
    # tx = lending_pool.deposit(
    #     erc20_address, amount * 0.8, account.address, 0, {"from": account}
    # )
    # tx.wait(1)
    # print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow!")
    # DAI interms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_dai_to_borrow = (1 / dai_eth_price) * borrowable_eth * 0.9
    print(f"We are going to borrow {amount_dai_to_borrow} DAI!")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        2,
        0,
        account.address,
        {"from": account, "gasLimit": 50000},
    )
    borrow_tx.wait(1)
    # Here we start to repay all the debt in our account
    # We recalculate the latest debt and latest price to make sure how much debt we have to repay
    # dai_eth_price = get_asset_price(
    #     config["networks"][network.show_active()]["dai_eth_price_feed"]
    # )
    # borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    # amount_dai_to_repay = (1 / dai_eth_price) * total_debt
    # repay_all(
    #     lending_pool, dai_address, Web3.toWei(amount_dai_to_repay, "ether"), account
    # )
    # borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)


# function repay(address asset, uint256 amount, uint256 rateMode, address onBehalfOf)
def repay_all(lending_pool, asset, amount, account):
    approve_erc20(
        asset,
        lending_pool.address,
        amount * 100,
        account,
    )
    print(f"{amount} is approved!")
    repay_tx = lending_pool.repay(asset, amount, 2, account.address, {"from": account})
    repay_tx.wait(1)
    print("All debt is repaid!")


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_price = Web3.fromWei(latest_price, "ether")
    print(f"Latest DAI/ETH price is {converted_price}!")
    return float(converted_price)


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(erc20_address, spender, value, account):
    # ABI
    # Address
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, value, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account.address)
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")
    print(f"You have {totalCollateralETH} worth of ETH deposited!")
    print(f"You have {totalDebtETH} worth of ETH borrowed!")
    print(f"You can borrow {availableBorrowsETH} worth of ETH!")
    return (float(availableBorrowsETH), float(totalDebtETH))