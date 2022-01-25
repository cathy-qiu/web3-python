from solcx import compile_standard, install_solc
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

install_solc("0.6.0")

with open("SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# compiling the .sol into
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# test values for connecting to rinkeby for development purposes
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/de5d2bc8c89b49b8a50ccf3f12fe7169")
)
chainID = 4
address = "0xe3de24AAbE2A91A4187A7E071Df10E0F30bc9B94"
privateKey = os.getenv("PRIVATE_KEY")

# create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# get latest transaction
nonce = w3.eth.getTransactionCount(address)

# to deploy contract, we need to create, sign, and send a transaction
# create transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chainID, "from": address, "nonce": nonce}
)

# sign transaction
signed_transaction = w3.eth.account.sign_transaction(
    transaction, private_key=privateKey
)

# send transaction
print("Deploying contract...")
transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
# for good practice, wait for block confirmation
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print(("Deployed!"))

# working with the contract: need contract address and ABI
simple_storage = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)


print(simple_storage.functions.retrieve().call())
print("Updating Contract...")
# making a state change to the contract on local blockchain
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chainID,
        "from": address,
        "nonce": nonce + 1,
    }
)

signed_store = w3.eth.account.sign_transaction(
    store_transaction, private_key=privateKey
)
send_store = w3.eth.send_raw_transaction(signed_store.rawTransaction)
store_receipt = w3.eth.wait_for_transaction_receipt(
    send_store
)  # updated and sent the transaction to the blockchain
print("Updated!")
print(simple_storage.functions.retrieve().call())
