# crypto_address_generator/generator.py

from bitcoinlib.keys import HDKey
from eth_account import Account
from solana.keypair import Keypair

def generate_btc_address():
    key = HDKey()
    return {
        "address": key.address(),
        "private_key": key.wif()
    }

def generate_ltc_address():
    key = HDKey(network='litecoin')
    return {
        "address": key.address(),
        "private_key": key.wif()
    }

def generate_eth_address():
    acct = Account.create()
    return {
        "address": acct.address,
        "private_key": acct.key.hex()
    }

def generate_solana_address():
    keypair = Keypair.generate()
    return {
        "address": str(keypair.public_key),
        "private_key": keypair.secret_key.hex()
    }
