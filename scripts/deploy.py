from pickle import TRUE
from brownie import FundMe, MockV3Aggregator, network, config
from scripts.helpful_scripts import (
    deploy_mocks,
    get_account,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)

# if you want to deploy this to your own ganache instence, open up ganache UI, and quickly create a ganache blockchain
# make sure the HPC server ends with 8545
# note that two contracts are made; first the pricefeed contract (mock) then the fund me contract
# note how the deployment isnt saved in the deployments folder, so add a new network to the brownie networks list
# to add a new network, run brownie networks add Ethereum ganache-local host=http://127.0.0.1:8545 chainid=1337
# when you want to close you ganache UI, go to deployments and delete the 1337 folder and go to map.json and delete the code for 1337
# to make fork, add the fork in config and run brownie networks add development mainnet-fork-dev cmd=ganache-cli host=http://127.0.0.1 fork=https://eth-mainnet.alchemyapi.io/v2/qGufmnGg2rP4Gzx5YXl73MCNvRJtIouW accounts=10 mnemonic=brownie port=8545
# note how we are using alchemy here and not infura


def deploy_fund_me():
    account = get_account()
    # now we need to pass the price feed address to FundMe because we made the priceFeed a global variable
    # so just past in the address before the "from": account
    # note that we want this to be dynamic and not always pulling in the rinkeby testnet eth/usd address, so:
    # if we are on a persistent network like rinkeby, use the associated address
    # otherwise, deploy mocks
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        price_feed_address = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]
    # now if we are on a development network, we would have to make our own price feed contract, and this would be called a mock and goes in the else: part
    # so in contracts, make a folder called test, and this is where we'll put our mock contracts
    # to deploy as a development, run just brownie run scripts/deploy.py (not like brownie run scripts/deploy.py --network rinkeby)
    # note that running brownie run scripts/deploy.py will run into an error which is caused by us trying to verify the code on etherscan with the etherscan API
    # to fix this, instead of publish_source=TRUE in the fund_me code, make the TRUE part dynamic and based off of what chain we're on (go to our config file)
    # after adding the verify=FALSE for development in the config, put this line of code in publish_source=config["networks"][network.show_active()].get("verify"),
    else:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address

    fund_me = FundMe.deploy(
        price_feed_address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    print(f"Contract deployed to {fund_me.address}")
    # put this return here so the test can pull from fund_me
    return fund_me


def main():
    deploy_fund_me()
