# schemas.py
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Define schemas using standard JSON Schema format
# Add descriptions to help the LLM understand the fields.

CREDIT_AGREEMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "agreement_date": {
            "description": "The execution date or effective date of the credit agreement (Format as YYYY-MM-DD if possible, otherwise as stated in the text).",
            "type": ["string", "null"]
        },
        "borrower_names": {
            "description": "List containing the full legal names of all borrowers party to the agreement.",
            "type": "array",
            "items": {
                "type": ["string", "null"],
                "description": "Full legal name of a borrower."
            }
        },
        "lender_parties": {
            "description": "List of key lender-side parties mentioned, including roles like Administrative Agent, Lenders, Issuing Banks, Swing Line Lender, etc.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {
                        "description": "The role of the party (e.g., 'Administrative Agent', 'Lender', 'Issuing Bank').",
                        "type": ["string", "null"]
                    },
                    "name": {
                        "description": "The full legal name of the party.",
                        "type": ["string", "null"]
                    }
                },
                "required": ["role", "name"]
            }
        },
        "total_commitment": {
            "description": "The total aggregate commitment amount under all credit facilities (Extract numeric value if clearly available, otherwise include currency symbol/text as string).",
            "type": ["string", "number", "null"]
        },
        "facility_details": {
            "description": "Details of specific credit facilities (e.g., Revolving Credit Facility, Term Loan A Facility) mentioned in the agreement.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "facility_name": {
                        "type": ["string", "null"],
                        "description": "Name or type of the facility."
                    },
                    "commitment_amount": {
                        "type": ["string", "number", "null"],
                        "description": "Commitment amount for this facility."
                    },
                    "maturity_date": {
                        "type": ["string", "null"],
                        "description": "Maturity date for this facility."
                    }
                }
            }
        },
        "interest_rates": {
            "description": "Interest rate information mentioned in the agreement.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "rate_type": {
                        "type": ["string", "null"],
                        "description": "Type of interest rate (e.g., 'Base Rate', 'SOFR', 'Prime Rate')."
                    },
                    "rate_value": {
                        "type": ["string", "number", "null"],
                        "description": "Interest rate value or formula."
                    },
                    "margin": {
                        "type": ["string", "number", "null"],
                        "description": "Margin or spread above the base rate."
                    }
                }
            }
        },
        "governing_law": {
            "description": "The governing law specified in the agreement.",
            "type": ["string", "null"]
        },
        "guarantors": {
            "description": "List of guarantors mentioned in the agreement.",
            "type": "array",
            "items": {
                "type": ["string", "null"],
                "description": "Name of a guarantor."
            }
        },
        "financial_covenants": {
            "description": "Financial covenants mentioned in the agreement.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "covenant_type": {
                        "type": ["string", "null"],
                        "description": "Type of financial covenant."
                    },
                    "covenant_details": {
                        "type": ["string", "null"],
                        "description": "Details of the covenant requirements."
                    }
                }
            }
        }
    },
    "required": [
        "agreement_date",
        "borrower_names",
        "lender_parties",
        "total_commitment",
        "governing_law"
    ]
}

LOAN_BOOKING_SHEET_SCHEMA = {
    "type": "object",
    "properties": {
        "maturity_date": {
            "description": "The maturity date of the loan (Format as YYYY-MM-DD if possible, otherwise as stated).",
            "type": ["string", "null"]
        },
        "total_loan_facility_amount": {
            "description": "The total loan facility amount.",
            "type": ["string", "number", "null"]
        },
        "withheld_amount": {
            "description": "Amount withheld from the loan facility.",
            "type": ["string", "number", "null"]
        },
        "used_amount": {
            "description": "Amount of the loan facility that has been used.",
            "type": ["string", "number", "null"]
        },
        "remaining_available_amount": {
            "description": "Remaining available amount in the loan facility.",
            "type": ["string", "number", "null"]
        },
        "global_syndicated_amount": {
            "description": "Global syndicated amount for this facility.",
            "type": ["string", "number", "null"]
        },
        "maximum_takedown_amount": {
            "description": "Maximum takedown amount allowed.",
            "type": ["string", "number", "null"]
        },
        "prepayment_penalty": {
            "description": "Indicates if there is a prepayment penalty for this loan.",
            "type": ["boolean", "null"]
        },
        "associated_fees": {
            "description": "List of fees associated with this facility.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fee_type": {"type": ["string", "null"], "description": "Type of fee."},
                    "fee_amount": {"type": ["string", "number", "null"], "description": "Amount or rate of the fee."}
                }
            }
        },
        "base_balance_type": {
            "description": "Base balance type used to calculate fees.",
            "type": ["string", "null"]
        },
        "effective_date": {
            "description": "Effective date of the loan or fee (Format as YYYY-MM-DD if possible, otherwise as stated).",
            "type": ["string", "null"]
        },
        "expiration_date": {
            "description": "Expiration date of the loan or fee (Format as YYYY-MM-DD if possible, otherwise as stated).",
            "type": ["string", "null"]
        },
        "expiration_schedule": {
            "description": "Expiration schedule or timing.",
            "type": ["string", "null"]
        },
        "fee_accrual_start_date": {
            "description": "Date when the fee starts accruing.",
            "type": ["string", "null"]
        },
        "fee_calculation_method": {
            "description": "Method used to calculate the fee.",
            "type": ["string", "null"]
        },
        "accrual_rate": {
            "description": "Accrual rate for this facility.",
            "type": ["string", "number", "null"]
        },
        "accrual_basis": {
            "description": "Accrual basis used (e.g., 30/360).",
            "type": ["string", "null"]
        },
        "percentage_applied": {
            "description": "Percentage applied and to what amount.",
            "type": ["string", "null"]
        },
        "low_high_indicator": {
            "description": "Low/high indicator meaning for this fee.",
            "type": ["string", "null"]
        },
        "pse_low_balance_threshold": {
            "description": "Low balance threshold defined by the Payment Settlement Entity.",
            "type": ["string", "number", "null"]
        },
        "pse_high_balance_threshold": {
            "description": "High balance threshold defined by the Payment Settlement Entity.",
            "type": ["string", "number", "null"]
        },
        "facility_low_balance_threshold": {
            "description": "Low balance threshold for this facility.",
            "type": ["string", "number", "null"]
        },
        "facility_high_balance_threshold": {
            "description": "High balance threshold for this facility.",
            "type": ["string", "number", "null"]
        },
        "next_due_date": {
            "description": "Next due date or accrue-to date.",
            "type": ["string", "null"]
        },
        "business_day_adjustment_rule": {
            "description": "Business day adjustment rule for the next due or accrue date.",
            "type": ["string", "null"]
        },
        "due_date_end_of_month": {
            "description": "Indicates if the due date is set to the end of the month.",
            "type": ["boolean", "null"]
        },
        "calendar_used": {
            "description": "Calendar used for payment or accrual scheduling.",
            "type": ["string", "null"]
        },
        "pse_lead_days": {
            "description": "Number of lead days defined by the Payment Settlement Entity.",
            "type": ["integer", "null"]
        },
        "pse_billing_frequency": {
            "description": "Billing frequency defined by the Payment Settlement Entity.",
            "type": ["string", "null"]
        },
        "pse_collection_instructions": {
            "description": "Collection instructions from the Payment Settlement Entity.",
            "type": ["string", "null"]
        },
        "pse_bill_format": {
            "description": "Bill format defined by the Payment Settlement Entity.",
            "type": ["string", "null"]
        },
        "pse_mailing_instructions": {
            "description": "Mailing instructions defined by the Payment Settlement Entity.",
            "type": ["string", "null"]
        },
        "billing_lead_days": {
            "description": "Number of lead days defined for billing.",
            "type": ["integer", "null"]
        },
        "billing_frequency": {
            "description": "Billing frequency.",
            "type": ["string", "null"]
        },
        "bill_handling": {
            "description": "How the bill is handled.",
            "type": ["string", "null"]
        },
        "borrower_names": {
            "description": "List containing the full legal names of all borrowers.",
            "type": "array",
            "items": {
                "type": ["string", "null"],
                "description": "Full legal name of a borrower."
            }
        },
        "lender_type": {
            "description": "Type of lender (e.g., 'Bank', 'Credit Union', 'Private Lender').",
            "type": ["string", "null"]
        },
        "governing_law": {
            "description": "The governing law for this loan facility.",
            "type": ["string", "null"]
        }
    },
    "required": [
        "maturity_date",
        "total_loan_facility_amount",
        "borrower_names",
        "lender_type",
        "governing_law"
    ]
}

# Dictionary mapping schema names (used in the application) to schema definitions
DOCUMENT_SCHEMAS = {
    "credit_agreement": CREDIT_AGREEMENT_SCHEMA,
    "loan_booking_sheet": LOAN_BOOKING_SHEET_SCHEMA,  
}

def get_schema(schema_name: str) -> Optional[Dict]:
    """
    Retrieves a predefined schema definition by its name.

    Args:
        schema_name: The key corresponding to the desired schema in DOCUMENT_SCHEMAS.

    Returns:
        The schema dictionary if found, otherwise None.
    """
    schema = DOCUMENT_SCHEMAS.get(schema_name)
    if schema:
        logger.debug(f"Retrieved schema definition for '{schema_name}'.")
    else:
        logger.error(f"Schema definition not found for name: '{schema_name}'. Available schemas: {list(DOCUMENT_SCHEMAS.keys())}")
    return schema
