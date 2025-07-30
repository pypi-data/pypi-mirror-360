"""
Data loading and management for CBUAE policies.
"""

import json
import os
from typing import Dict, Any

def load_policy_db() -> Dict[str, Any]:
    """
    Load policy data from a JSON file or fall back to mock data.
    """
    # Try to load from different possible locations
    possible_paths = [
        "policy_db.json",
        os.path.join(os.path.dirname(__file__), "..", "policy_db.json"),
        os.path.join(os.path.dirname(__file__), "policy_db.json")
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    
    # Fall back to mock data
    print("policy_db.json not found, using mock data")
    return {
        "AML_2018": {
            "title": "Federal Decree-Law No. 20 of 2018 on Anti-Money Laundering and Combating the Financing of Terrorism",
            "text": "Financial institutions must implement enhanced customer due diligence for high-risk clients, report suspicious transactions to the Financial Intelligence Unit, and comply with FATF recommendations. This includes maintaining records for at least five years and conducting ongoing monitoring.",
            "category": "Anti-Money Laundering"
        },
        "CAPITAL_2023": {
            "title": "Capital Adequacy Regulation 2023",
            "text": "Banks must maintain a minimum Capital Adequacy Ratio of 10.5% as per Basel III standards, including a Common Equity Tier 1 (CET1) ratio of 7%. Additional capital buffers apply for systemically important banks, and stress testing is required.",
            "category": "Banking Regulation"
        },
        "PTS_2024": {
            "title": "Payment Token Services Regulation 2024",
            "text": "Governs the issuance, conversion, custody, and transfer of payment tokens. Requires robust risk management, cybersecurity measures, and compliance with anti-money laundering regulations.",
            "category": "FinTech"
        },
        "OUTSOURCING_2021": {
            "title": "Outsourcing Regulation for Banks 2021",
            "text": "Banks must obtain prior approval from CBUAE before outsourcing material activities. Requires due diligence on service providers, data protection measures, and ongoing monitoring. Applies to cloud services and hyperscaler providers.",
            "category": "Banking Regulation"
        },
        "CYBER_SECURITY_2020": {
            "title": "Cyber Security Regulation 2020", 
            "text": "Establishes cybersecurity requirements for financial institutions including incident reporting, risk management frameworks, and business continuity planning. Covers cloud computing security requirements.",
            "category": "Cybersecurity"
        }
    }