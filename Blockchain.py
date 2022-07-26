from functools import reduce
import hashlib as hl
from collections import OrderedDict
import json

def hash_string_256(string):
    return hl.sha256(string).hexdigest()

def hash_block(block):
    return hash_string_256(json.dumps(block, sort_keys=True).encode())

MINING_REWARD = 10
genesis_block = {"previous_hash": "", "index": 0, "transactions": [], "proof": 100}
blockchain = [genesis_block]
open_transactions = [OrderedDict([('sender', 'Garima'), ('recipient', 'Gaurav'), ('amount', 0.0)])]
owner = "Garima"
participants = {"Garima", "Gaurav","MINING"}

# To validate the proof 
def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == "00"

# To compute proof of work
def proof_of_work():
    # Generate a proof of work for the open transactions,
    # the hash of the previous block and a random number (which is guessed until it fits).
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof

# To compute the balance of the participants 
def get_balance(participant):
    tx_sender = [
        [tx["amount"] for tx in block["transactions"] if tx["sender"] == participant]
        for block in blockchain
    ]
    open_tx_sender = [
        tx["amount"] for tx in open_transactions if tx["sender"] == participant
    ]
    tx_sender.append(open_tx_sender)
    print(tx_sender)
    amount_sent = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
        tx_sender,
        0,
    )
    tx_recipient = [
        [tx["amount"] for tx in block["transactions"] if tx["recipient"] == participant]
        for block in blockchain
    ]
    amount_received = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
        tx_recipient,
        0,
    )
    return amount_received - amount_sent

# To access last block of the blockchain
def get_last_blockchain_value():
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

# To check the balance of the sender against the transaction amount
def verify_transaction(transaction):
    sender_balance = get_balance(transaction["sender"])
    return sender_balance >= transaction["amount"]

# To add the transaction and add the corresponding block to the blockchain
def add_transaction(recipient, sender=owner, amount=1.0):
    transaction = OrderedDict(
        [("sender", sender), ("recipient", recipient), ("amount", amount)]
    )
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False

# To mine the open transactions
def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = OrderedDict(
        [("sender", "MINING"), ("recipient", owner), ("amount", MINING_REWARD)]
    )
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        "previous_hash": hashed_block,
        "index": len(blockchain),
        "transactions": copied_transactions,
        "proof": proof,
    }
    blockchain.append(block)
    return True

# To input the transaction details
def get_transaction_value():
    tx_recipient = input("Enter the recipient of the transaction: ")
    tx_amount = float(input("Your transaction amount please: "))
    return tx_recipient, tx_amount

# To input the user's choice
def get_user_choice():
    user_input = input("Your choice: ")
    return user_input

# To print the blockchain
def print_blockchain_elements():
    for block in blockchain:
        print("Outputting Block")
        print(block)
    else:
        print("-" * 20)

# To verify the blockchain by comparing hash value
def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block["previous_hash"] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(
            block["transactions"][:-1], block["previous_hash"], block["proof"]
        ):
            print("Proof of work is invalid")
            return False
    return True

# To verify the pending transactions
def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True

while waiting_for_input:
    print("Please choose")
    print("1: Add a new transaction value")
    print("2: Mine a new block")
    print("3: Output the blockchain blocks")
    print("4: Output participants")
    print("5: Check transaction validity")
    print("q: Quit")
    
    user_choice = get_user_choice()
    
    if user_choice == "1":
        tx_data = get_transaction_value()
        recipient, amount = tx_data

        if add_transaction(recipient, amount=amount):
            print("Added transaction!")
        else:
            print("Transaction failed!")
        print(open_transactions)
    
    elif user_choice == "2":
        if mine_block():
            open_transactions = []
    
    elif user_choice == "3":
        print_blockchain_elements()
    
    elif user_choice == "4":
        print(participants)
    
    elif user_choice == "5":
        if verify_transactions():
            print("All transactions are valid")
        else:
            print("There are invalid transactions")
    
    elif user_choice == "q":
        waiting_for_input = False
    
    else:
        print("Input was invalid, please pick a value from the list!")
    
    if not verify_chain():
        print_blockchain_elements()
        print("Invalid blockchain!")
        break

else:
    print("User left!")


print("Done!")
