import json
import os
from web3 import Web3
from pathlib import Path

# Configurações
RPC_URL = "https://ethereum-sepolia.publicnode.com" # Public RPC
CONTRACT_ADDRESS = "0x12B35aB500aca635151Db65Ba2EB51e32Ed4009b"
PRIVATE_KEY = os.getenv("SEPOLIA_PRIVATE_KEY")

ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_ohash", "type": "string"},
            {"internalType": "string", "name": "_pufId", "type": "string"}
        ],
        "name": "register",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def register():
    if not PRIVATE_KEY:
        print("❌ Erro: SEPOLIA_PRIVATE_KEY não encontrada.")
        return

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Erro: Não foi possível conectar à Sepolia.")
        return

    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

    # Carregar dados do ledger
    ledger_path = Path("/home/ubuntu/svca-lab-genesis/artifact/ledger.json")
    if not ledger_path.exists():
        print("❌ Erro: Ledger não encontrado.")
        return
    
    with open(ledger_path, "r") as f:
        ledger_data = json.load(f)
        if not ledger_data.get("records"):
            print("❌ Erro: Nenhum registro no ledger.")
            return
        record = ledger_data["records"][0]
        ohash = record["ohash"]
        puf_id = record["puf_id"]

    print(f"🚀 Registrando Ohash na Sepolia: {ohash}")
    
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Construir transação
    txn = contract.functions.register(ohash, puf_id).build_transaction({
        'chainId': 11155111,
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"✅ Transação enviada! Hash: {tx_hash.hex()}")
    print(f"🔗 Veja no Etherscan: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")

    # Salvar resultado
    with open("SEPOLIA_RESULT.json", "w") as f:
        json.dump({"tx_hash": tx_hash.hex(), "ohash": ohash, "puf_id": puf_id}, f)

if __name__ == "__main__":
    register()
