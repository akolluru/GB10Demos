import ollama
import pandas as pd
from typing import Dict, List, Tuple

class AMLScreener:
    def __init__(self, model_name: str = "mistral:latest"):
        self.model_name = model_name
        
    def _format_transaction(self, transaction: pd.Series) -> str:
        """Format transaction data for LLM analysis."""
        return f"""
Transaction Details:
ID: {transaction['transaction_id']}
Amount: {transaction['amount']} {transaction['currency']}
Sender: {transaction['sender_name']} ({transaction['sender_account']})
Receiver: {transaction['receiver_name']} ({transaction['receiver_account']})
Type: {transaction['transaction_type']}
Country: {transaction['country']}
Purpose: {transaction['purpose']}
        """
    
    def level1_screening(self, transaction: pd.Series) -> Tuple[float, str]:
        """Perform Level 1 screening using basic rules and LLM."""
        prompt = f"""
You are an AML screening expert. Analyze this transaction for potential money laundering risks.
Focus on basic red flags like:
1. High-value transactions
2. Transactions to high-risk countries
3. Suspicious transaction patterns

{self._format_transaction(transaction)}

Provide a risk score (0-100) and a brief explanation of any concerns.
Format your response as: SCORE: [number] | EXPLANATION: [text]
"""
        
        response = ollama.generate(model=self.model_name, prompt=prompt)
        response_text = response['response']
        
        # Parse response
        try:
            score = float(response_text.split('SCORE:')[1].split('|')[0].strip())
            explanation = response_text.split('EXPLANATION:')[1].strip()
        except:
            score = 0
            explanation = "Error in parsing LLM response"
            
        return score, explanation
    
    def level2_screening(self, transaction: pd.Series, related_transactions: List[pd.Series]) -> Dict:
        """Perform Level 2 screening with enhanced due diligence and detailed reasoning."""
        # Format related transactions
        related_tx_text = "\n".join([self._format_transaction(tx) for tx in related_transactions])
        
        prompt = f"""
You are an AML expert performing enhanced due diligence. Analyze this transaction and its related transactions
for complex money laundering patterns. Consider:
1. Transaction patterns and relationships
2. Customer behavior analysis
3. Geographic risk factors
4. Transaction purpose analysis
5. Structuring or layering indicators

Main Transaction:
{self._format_transaction(transaction)}

Related Transactions:
{related_tx_text}

Provide a detailed analysis with:
1. Risk Score (0-100)
2. Risk Level (Low/Medium/High)
3. Key Risk Factors
4. Recommended Actions
5. A detailed explanation and reasoning for your assessment, including which patterns, relationships, or red flags contributed to your decision.

Format your response as:
SCORE: [number]
RISK_LEVEL: [Low/Medium/High]
RISK_FACTORS: [list of factors]
RECOMMENDATIONS: [list of actions]
EXPLANATION: [detailed explanation and reasoning]
Please answer ONLY in the above format. Do not add any explanation or text outside this format.
"""
        
        response = ollama.generate(model=self.model_name, prompt=prompt)
        response_text = response['response']
        print("LLM raw response (L2):", response_text)  # For debugging
        
        # Parse response (robust)
        import re
        try:
            # Safely extract score
            score_match = re.search(r'SCORE:\s*([0-9.]+)', response_text)
            score = float(score_match.group(1)) if score_match else 0.0
            
            # Safely extract risk level
            risk_level_match = re.search(r'RISK_LEVEL:\s*([\w/]+)', response_text)
            risk_level = risk_level_match.group(1) if risk_level_match else "Unknown"
            
            # Safely extract risk factors
            risk_factors_match = re.search(r'RISK_FACTORS:\s*(.*?)(?:RECOMMENDATIONS:|EXPLANATION:|$)', response_text, re.DOTALL)
            risk_factors = risk_factors_match.group(1).strip() if risk_factors_match else "N/A"
            
            # Safely extract recommendations
            recommendations_match = re.search(r'RECOMMENDATIONS:\s*(.*?)(?:EXPLANATION:|$)', response_text, re.DOTALL)
            recommendations = recommendations_match.group(1).strip() if recommendations_match else "N/A"
            
            # Safely extract explanation
            explanation_match = re.search(r'EXPLANATION:\s*(.*)', response_text, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else response_text[:500]  # Use first 500 chars if no match
        except Exception as e:
            score = 0.0
            risk_level = "Unknown"
            risk_factors = f"Error in parsing LLM response: {str(e)}"
            recommendations = f"Error in parsing LLM response: {str(e)}"
            explanation = f"Error in parsing LLM response: {str(e)}"
        
        return {
            'score': score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'explanation': explanation
        }
    
    def find_related_transactions(self, transaction: pd.Series, all_transactions: pd.DataFrame) -> List[pd.Series]:
        """Find transactions related to the given transaction."""
        related = []
        
        # Find transactions with same sender or receiver
        sender_mask = all_transactions['sender_account'] == transaction['sender_account']
        receiver_mask = all_transactions['receiver_account'] == transaction['receiver_account']
        
        related_tx = all_transactions[sender_mask | receiver_mask]
        
        # Sort by timestamp and get the 5 most recent
        related_tx = related_tx.sort_values('timestamp', ascending=False)
        related = related_tx.head(5).to_dict('records')
        
        return [pd.Series(tx) for tx in related] 