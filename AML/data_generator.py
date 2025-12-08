import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

def generate_transaction_data(n=1000):
    """Generate simulated transaction data with high-risk clusters."""
    random.seed(42)
    senders = [f"Sender_{i}" for i in range(1, 51)]
    receivers = [f"Receiver_{i}" for i in range(1, 51)]
    accounts = [f"ACCT{i:05d}" for i in range(1, 101)]
    countries = ["USA", "Germany", "UK", "Iran", "North Korea", "Syria", "Cuba", "Venezuela", "Paraguay", "Switzerland"]
    types = ["Wire Transfer", "Cash Deposit", "ACH", "Card Payment"]
    purposes = ["Invoice Payment", "Salary", "Gift", "Loan Repayment", "Investment", "Consulting", "Purchase", "Donation", "Beyond personal.", "Watch high fine."]

    data = []
    now = datetime.now()

    # --- Create a few high-risk clusters ---
    cluster_accounts = [f"ACCTCLUST{i:03d}" for i in range(1, 6)]
    cluster_names = [f"ClusterPerson_{i}" for i in range(1, 6)]
    for cluster in range(3):
        # Each cluster: 5-8 transactions, same accounts, high-risk countries, high values
        cluster_tx_count = random.randint(5, 8)
        sender = cluster_names[cluster]
        sender_acct = cluster_accounts[cluster]
        for i in range(cluster_tx_count):
            receiver = random.choice(cluster_names)
            receiver_acct = random.choice(cluster_accounts)
            while receiver == sender:
                receiver = random.choice(cluster_names)
            amount = random.randint(200000, 900000)
            country = random.choice(["Iran", "North Korea", "Syria", "Cuba", "Venezuela"])
            tx_type = random.choice(["Wire Transfer", "Cash Deposit"])
            purpose = random.choice(["Beyond personal.", "Watch high fine.", "Donation"])
            data.append({
                "transaction_id": f"CLUST{cluster}_{i}",
                "amount": amount,
                "currency": "USD",
                "sender_name": sender,
                "sender_account": sender_acct,
                "receiver_name": receiver,
                "receiver_account": receiver_acct,
                "transaction_type": tx_type,
                "country": country,
                "purpose": purpose,
                "timestamp": now - timedelta(days=random.randint(0, 30))
            })

    # --- Generate the rest of the transactions (less interconnected) ---
    for i in range(n - len(data)):
        sender = random.choice(senders)
        receiver = random.choice(receivers)
        sender_acct = random.choice(accounts)
        receiver_acct = random.choice(accounts)
        amount = random.randint(1000, 1000000)
        country = random.choice(countries)
        tx_type = random.choice(types)
        purpose = random.choice(purposes)
        data.append({
            "transaction_id": f"TX{i:06d}",
            "amount": amount,
            "currency": random.choice(["USD", "EUR", "CHF"]),
            "sender_name": sender,
            "sender_account": sender_acct,
            "receiver_name": receiver,
            "receiver_account": receiver_acct,
            "transaction_type": tx_type,
            "country": country,
            "purpose": purpose,
            "timestamp": now - timedelta(days=random.randint(0, 30))
        })

    df = pd.DataFrame(data)
    return df

def generate_risk_scores(df):
    """Generate risk scores for transactions."""
    risk_scores = []
    
    for _, row in df.iterrows():
        score = 0
        
        # Amount-based risk
        if row['amount'] > 500000:
            score += 3
        elif row['amount'] > 100000:
            score += 2
        elif row['amount'] > 50000:
            score += 1
            
        # Country-based risk
        high_risk_countries = ['Iran', 'North Korea', 'Syria', 'Cuba', 'Venezuela']
        if row['country'] in high_risk_countries:
            score += 3
            
        # Transaction type risk
        if row['transaction_type'] == 'Cash Deposit':
            score += 2
            
        # Normalize score to 0-100
        normalized_score = min(100, score * 20)
        risk_scores.append(normalized_score)
    
    df['risk_score'] = risk_scores
    return df

if __name__ == "__main__":
    # Generate sample data
    df = generate_transaction_data(1000)
    df = generate_risk_scores(df)
    print(df.head()) 