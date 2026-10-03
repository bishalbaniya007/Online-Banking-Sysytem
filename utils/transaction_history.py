# this fucntion is used to build transaction history in history page 
# and recent transactions in dashboard

# Takes cursor, transaction(dict) and current user account_id
# mutates evey single transaction that is passed 

def build_txn_history(cursor, transaction, user_acc_id):
  # for each transaction:

  # a. Direction of money flow
  if transaction["receiver_acc_id"] == user_acc_id:
    direction = "Credit"
  else:
    direction = "Debit"

  # b. Label for users to see
  if transaction["transaction_type"] == "deposit":
    label = "Deposit"

  elif transaction["transaction_type"] == "withdraw":
    label = "Withdraw"

  elif transaction["transaction_type"] == "transfer":
    label = "Received" if direction == "Credit" else "Sent"

  # c. Counterparty
  if transaction["transaction_type"] == "transfer":
    other_acc_id = transaction["sender_acc_id"] if direction == "Credit" else transaction["receiver_acc_id"]

    # Fetching account number and username of other party
    cursor.execute("""
          SELECT a.account_num, u.username
          FROM accounts a
          INNER JOIN users u ON a.user_id = u.user_id
          WHERE a.account_id = %s""", (other_acc_id,))

    counter_party = cursor.fetchone()

  else:
    counter_party = None

  # Storing in dictionary
  transaction["direction"] = direction
  transaction["label"] = label
  transaction["counterparty"] = counter_party

  return transaction
  

    