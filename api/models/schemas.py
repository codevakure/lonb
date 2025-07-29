# schemas.py
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Define schemas using standard JSON Schema format
# Add descriptions to help the LLM understand the fields.

CREDIT_AGREEMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "agreement_execution_date": {
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
                    "facility_type": {
                        "description": "Type of the facility (e.g., 'Revolving Credit Facility', 'Term Loan A Facility').",
                        "type": ["string", "null"]
                    },
                    "commitment_amount": {
                        "description": "The commitment amount specific to this facility (Extract numeric value if clearly available, otherwise include currency symbol/text as string).",
                        "type": ["string", "number", "null"]
                    },
                    "maturity_date": {
                        "description": "The maturity date specific to this facility (Format as YYYY-MM-DD if possible, otherwise as stated).",
                        "type": ["string", "null"]
                    }
                },
                "required": ["facility_type"]
            }
        },
        "interest_rate_details": {
            "description": "Specifics about applicable interest rates, margins, base rates, and floors.",
            "type": "object",
            "properties": {
                "base_rate_options": {
                    "description": "List of available base rates mentioned (e.g., 'Adjusted Term SOFR', 'Alternate Base Rate', 'LIBOR').",
                    "type": "array",
                    "items": {"type": "string"}
                },
                "applicable_margins": {
                    "description": "Summary of margins added to base rates. Mention if they vary by rate type or leverage level.",
                    "type": ["string", "null"]
                },
                "rate_floor": {
                    "description": "Any specified minimum interest rate or floor (e.g., 'SOFR floor of 0.50%') (Extract numeric value if clearly available, otherwise include text as string).",
                     "type": ["string", "number", "null"]
                },
                "default_rate": {
                     "description": "Description of the interest rate applicable during an event of default (e.g., 'Base Rate plus 2.00%').",
                     "type": ["string", "null"]
                }
            }
        },
        "key_fees": {
            "description": "Details on significant fees mentioned, such as commitment fees, letter of credit fees, or administrative agent fees.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fee_type": {
                        "description": "Type of fee (e.g., 'Commitment Fee', 'LC Participation Fee', 'Upfront Fee').",
                        "type": ["string", "null"]
                    },
                    "fee_rate_or_amount": {
                        "description": "The rate (e.g., '0.25% per annum') or fixed amount of the fee.",
                        "type": ["string", "null"]
                    },
                    "payment_frequency": {
                        "description": "How often the fee is payable (e.g., 'quarterly in arrears', 'annually', 'upon closing').",
                        "type": ["string", "null"]
                    }
                },
                "required": ["fee_type", "fee_rate_or_amount"]
            }
        },
        "maturity_date_final": {
            "description": "The final maturity date for the overall agreement or the longest-dated facility (Format as YYYY-MM-DD if possible, otherwise as stated).",
            "type": ["string", "null"]
        },
        "governing_law": {
            "description": "The jurisdiction whose laws govern the agreement (e.g., 'State of New York', 'laws of England and Wales').",
            "type": ["string", "null"]
        },
        "definition_business_day": {
            "description": "The specific definition of 'Business Day' as provided in the definitions section of the agreement.",
            "type": ["string", "null"]
        }
    },
    "required": [
        "agreement_execution_date",
        "borrower_names",
        "lender_parties",
        "total_commitment",
        "maturity_date_final",
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
        "borrower_names": {
            "description": "List of borrower names listed in the agreement.",
            "type": "array",
            "items": {"type": ["string", "null"]}
        },
        "governing_law": {
            "description": "The jurisdiction whose laws govern the loan agreement (e.g., 'State of New York', 'laws of England and Wales').",
            "type": ["string", "null"]
        },
        "is_revolving_facility": {
            "description": "Indicates if this is a revolving facility.",
            "type": ["boolean", "null"]
        }
    },
    "required": [
        "maturity_date",
        "total_loan_facility_amount",
        "borrower_names",
        "governing_law"
    ]
}
LOAN_BOOKING_SHEET_SCHEMA = {
    "type": "object",
    "properties": {
        "maturity_date": {
            "description": "The maturity date of the loan (Format as YYYY-MM-DD if possible, otherwise as stated).",
            "type": ["string", "null"],
            "examples": [
                "Search for: 'Maturity Date', 'Stated Maturity', 'Final Payment Date', maturity date, final payment date, expiration date, termination date, end date, due date, loan term end, facility expiration, maturity, expires on, term ends, final maturity. Check cover page, key terms section, and facility description. Look for specific dates in MM/DD/YYYY, DD/MM/YYYY, or written formats like 'December 31, 2025'. Also check for terms like '5 years from effective date', 'December 2025', or specific calendar dates. Search summary pages, term sheets, and commitment schedules."
            ]
        },
        "total_loan_facility_amount": {
            "description": "The total loan facility amount.",
            "type": ["string", "number", "null"],
            "examples": [
                "Search for: 'Total Commitment', 'Aggregate Commitment', 'Maximum Loan Amount', total facility amount, aggregate facility size, total loan amount, facility limit, credit limit, total available credit, maximum facility amount, principal amount, facility size. Often found on cover page or in facility description. Look for dollar amounts with words like 'million', 'billion', currency symbols '$', amounts with commas. Check summary sections, commitment schedules, facility descriptions, and any tables showing loan amounts."
            ]
        },
        "withheld_amount": {
            "description": "Amount withheld from the loan facility.",
            "type": ["string", "number", "null"],
            "examples": [
                "Search for: 'withholding', 'retention', 'reserve' in disbursement or tax sections, withheld amount, holdback amount, reserve amount, retained funds, escrow amount, set aside amount, blocked funds, restricted amount, holdback reserve. Check disbursement conditions and tax withholding clauses."
            ]
        },
        "used_amount": {
            "description": "Amount of the loan facility that has been used.",
            "type": ["string", "number", "null"],
            "examples": [
                "Search for: 'Outstanding Principal', 'Drawn Amount', 'Utilized Commitment', used amount, outstanding balance, utilized amount, disbursed amount, advanced amount, funded amount, borrowed amount. Check current status sections and borrowing base calculations."
            ]
        },
        "remaining_available_amount": {
            "description": "Remaining available amount in the loan facility.",
            "type": ["string", "number", "null"],
            "examples": [
                "Search for: 'Available Commitment', 'Undrawn Amount', remaining available, unused portion, available balance, unutilized amount, remaining capacity, available credit, unfunded amount, remaining commitment. Often calculated as total minus used amounts."
            ]
        },
        "global_syndicated_amount": {
            "description": "Global syndicated amount for this facility.",
            "type": ["string", "number", "null"],
            "examples": [
                "Search for: 'Syndicated Facility', 'Aggregate Lender Commitments', global syndicated amount, syndicated portion, syndication amount, syndicate commitment, global allocation, total syndicated, consortium amount, syndicate share, multi-lender amount. Check syndication section and lender commitment schedules."
            ]
        },
        "maximum_takedown_amount": {
            "description": "Maximum takedown amount allowed.",
            "type": ["string", "number", "null"],
            "examples": [
                "Search for: 'Maximum Draw', 'Cap on Advances', maximum takedown, max takedown amount, maximum advance, largest single draw, maximum borrowing, max single advance, takedown limit, draw limit. Often in borrowing procedures or facility terms."
            ]
        },
        "prepayment_penalty": {
            "description": "Indicates if there is a prepayment penalty for this loan.",
            "type": ["boolean", "null"],
            "examples": [
                "Search for: 'Prepayment' or 'Breakage Fee' clauses, prepayment penalty, early payment penalty, prepayment fee, early repayment charge, breakage costs, make-whole premium, call protection, prepayment premium, early termination fee. Check prepayment sections and fee schedules."
            ]
        },
        "associated_fees": {
            "description": "List of fees associated with this facility.",
            "type": "array",
            "examples": [
                "Search in: 'Fees', 'Costs', or 'Expenses' sections, associated fees, facility fees, loan fees, commitment fees, arrangement fees, administrative fees, origination fees, upfront fees, ongoing fees, periodic fees, service charges. Scan fee schedules and cost sections comprehensively."
            ],
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
            "type": ["string", "null"],
            "examples": [
                "Search for: 'Base Rate', 'Reference Rate', 'Benchmark Rate', base balance type, calculation basis, fee calculation base, balance calculation method, fee basis, calculation methodology, fee computation base. Check interest rate and fee calculation sections."
            ]
        },
        "effective_date": {
            "description": "Effective date of the loan or fee (Format as YYYY-MM-DD if possible, otherwise as stated).",
            "type": ["string", "null"],
            "examples": [
                "Usually on the cover page or in the preamble. Search for: effective date, commencement date, start date, inception date, activation date, origination date, beginning date, facility start date, agreement date, execution date. Check document header, signature page, and opening paragraphs."
            ]
        },
        "expiration_date": {
            "description": "Expiration date of the loan or fee (Format as YYYY-MM-DD if possible, otherwise as stated).",
            "type": ["string", "null"],
            "examples": [
                "Often the same as 'Maturity Date'. Search for: expiration date, termination date, end date, maturity date, cessation date, conclusion date, facility end date, final date, expiry date. May be identical to maturity date in many cases."
            ]
        },
        "expiration_schedule": {
            "description": "Expiration schedule or timing.",
            "type": ["string", "null"],
            "examples": [
                "Found in 'Extension Options' or 'Renewal Terms'. Search for: expiration schedule, termination schedule, maturity schedule, expiry timing, end schedule, cessation timeline, facility termination plan, extension provisions, renewal clauses."
            ]
        },
        "fee_accrual_start_date": {
            "description": "Date when the fee starts accruing.",
            "type": ["string", "null"],
            "examples": [
                "Typically begins on the 'Effective Date'. Search for: fee accrual start date, accrual commencement, fee start date, accrual begins, fee effective date, accrual inception, charge begins, fee calculation starts. Often coincides with loan effective date."
            ]
        },
        "fee_calculation_method": {
            "description": "Method used to calculate the fee.",
            "type": ["string", "null"],
            "examples": ["What method is used to calculate the fee? Look for 'Fee Calculation' or 'Interest Computation'. Search for: fee calculation method, calculation methodology, computation method, fee formula, calculation basis, fee determination method, pricing methodology. Check detailed fee calculation sections."]
        },
        "accrual_rate": {
            "description": "Accrual rate for this facility.",
            "type": ["string", "number", "null"],
            "examples": ["What is the accrual rate for this facility? Refer to 'Applicable Margin' or 'Interest Rate'. Look for: accrual rate, interest rate, fee rate, annual rate, percentage rate, rate per annum, pricing rate, charge rate, applicable rate, margin, spread. Check pricing grids and rate schedules."]
        },
        "accrual_basis": {
            "description": "Accrual basis used (e.g., 30/360).",
            "type": ["string", "null"],
            "examples": ["What accrual basis is used? Found in 'Interest Calculation' (e.g., 360/365-day year). Look for: accrual basis, day count convention, calculation basis, day count method, accrual convention, interest basis, day count basis (30/360, actual/360, actual/365, etc.). Check interest calculation methodology sections."]
        },
        "percentage_applied": {
            "description": "Percentage applied and to what amount.",
            "type": ["string", "null"],
            "examples": ["What percentage is applied and to what amount? Often in 'Borrowing Base' or 'Advance Rate' formulas. Look for: percentage applied, rate applied, applicable percentage, fee percentage, charge percentage, rate calculation, percentage basis, advance rate, borrowing base percentage. Check availability calculations and advance formulas."]
        },
        "low_high_indicator": {
            "description": "Low/high indicator meaning for this fee.",
            "type": ["string", "null"],
            "examples": ["What does the low/high indicator mean for this fee? Look for tiered fee or utilization thresholds. Search for: low/high indicator, tier indicator, threshold indicator, balance tier, rate tier, fee tier, pricing tier, balance range indicator, utilization tiers, commitment level tiers."]
        },
        "pse_low_balance_threshold": {
            "description": "Low balance threshold defined by the Payment Settlement Entity.",
            "type": ["string", "number", "null"],
            "examples": ["What is the low balance threshold defined by the Payment Settlement Entity? Found in 'Utilization Fee' or 'Commitment Fee' tiers. Look for: PSE low balance threshold, payment settlement entity low threshold, minimum balance threshold, low balance limit, minimum balance requirement, PSE minimum threshold, utilization fee tiers."]
        },
        "pse_high_balance_threshold": {
            "description": "High balance threshold defined by the Payment Settlement Entity.",
            "type": ["string", "number", "null"],
            "examples": ["What is the high balance threshold defined by the Payment Settlement Entity? Found in 'Utilization Fee' or 'Commitment Fee' tiers. Look for: PSE high balance threshold, payment settlement entity high threshold, maximum balance threshold, high balance limit, maximum balance requirement, PSE maximum threshold, utilization fee tiers."]
        },
        "facility_low_balance_threshold": {
            "description": "Low balance threshold for this facility.",
            "type": ["string", "number", "null"],
            "examples": ["What is the low balance threshold for this facility? Found in 'Borrowing Base' or 'Availability' clauses. Look for: facility low balance threshold, minimum facility balance, low balance limit, minimum threshold, facility minimum balance, low tier threshold, borrowing base minimum, availability threshold."]
        },
        "facility_high_balance_threshold": {
            "description": "High balance threshold for this facility.",
            "type": ["string", "number", "null"],
            "examples": ["What is the high balance threshold for this facility? Found in 'Borrowing Base' or 'Availability' clauses. Look for: facility high balance threshold, maximum facility balance, high balance limit, maximum threshold, facility maximum balance, high tier threshold, borrowing base maximum, availability ceiling."]
        },
        "next_due_date": {
            "description": "Next due date or accrue-to date.",
            "type": ["string", "null"],
            "examples": ["What is the next due date or accrue-to date? Refer to 'Interest Payment Dates' or 'Scheduled Payment Dates'. Look for: next due date, next payment date, accrue-to date, next billing date, upcoming due date, next maturity date, payment due date, next accrual date, scheduled payment dates, interest payment calendar."]
        },
        "business_day_adjustment_rule": {
            "description": "Business day adjustment rule for the next due or accrue date.",
            "type": ["string", "null"],
            "examples": ["What is the business day adjustment rule for the next due or accrue date? Found in 'Business Day Convention' clauses. Look for: business day adjustment, business day convention, holiday adjustment, weekend adjustment, modified following, following business day, preceding business day, business day rules."]
        },
        "due_date_end_of_month": {
            "description": "Indicates if the due date is set to the end of the month.",
            "type": ["boolean", "null"],
            "examples": ["Is the due date set to the end of the month? Look for 'end-of-month convention'. Search for: end of month, month end, EOM, due at month end, month-end payment, end-of-month adjustment, monthly cycle end, end-of-month rule, EOM convention."]
        },
        "calendar_used": {
            "description": "Calendar used for payment or accrual scheduling.",
            "type": ["string", "null"],
            "examples": ["What calendar is used for payment or accrual scheduling? Refer to 'Day Count Basis' or 'Interest Calculation Method'. Look for: calendar used, holiday calendar, business calendar, payment calendar, accrual calendar, financial calendar, banking calendar, settlement calendar, NYC calendar, London calendar."]
        },
        "pse_lead_days": {
            "description": "Number of lead days defined by the Payment Settlement Entity.",
            "type": ["integer", "null"],
            "examples": ["How many lead days are defined by the Payment Settlement Entity? Found in 'Notice Periods' for borrowings or billing. Look for: PSE lead days, payment settlement entity lead time, advance notice days, lead time, notice period, PSE advance days, settlement lead days, borrowing notice period."]
        },
        "pse_billing_frequency": {
            "description": "Billing frequency defined by the Payment Settlement Entity.",
            "type": ["string", "null"],
            "examples": ["What is the billing frequency defined by the Payment Settlement Entity? Look for 'Billing Frequency' or 'Fee Payment Schedule'. Search for: PSE billing frequency, payment settlement entity billing cycle, billing period, billing schedule, payment frequency, PSE billing cycle, settlement frequency, fee payment schedule."]
        },
        "pse_collection_instructions": {
            "description": "Collection instructions from the Payment Settlement Entity.",
            "type": ["string", "null"],
            "examples": ["What are the collection instructions from the Payment Settlement Entity? Found in 'Payment Instructions'. Look for: PSE collection instructions, payment settlement entity collection, collection procedures, payment instructions, collection method, PSE payment method, payment processing instructions, fund collection procedures."]
        },
        "pse_bill_format": {
            "description": "Bill format defined by the Payment Settlement Entity.",
            "type": ["string", "null"],
            "examples": ["What is the bill format defined by the Payment Settlement Entity? May be described in 'Invoicing' or 'Statement Requirements'. Look for: PSE bill format, payment settlement entity bill format, billing format, invoice format, statement format, PSE billing template, invoicing requirements, statement specifications."]
        },
        "pse_mailing_instructions": {
            "description": "Mailing instructions defined by the Payment Settlement Entity.",
            "type": ["string", "null"],
            "examples": ["What are the mailing instructions defined by the Payment Settlement Entity? Refer to 'Notices' or 'Communications' sections. Look for: PSE mailing instructions, payment settlement entity mailing, delivery instructions, postal instructions, mailing address, PSE delivery method, notice delivery, communication procedures."]
        },
        "billing_lead_days": {
            "description": "Number of lead days defined for billing.",
            "type": ["integer", "null"],
            "examples": ["How many lead days are defined for billing? Look for 'Notice Period' or 'Billing Timeline'. Search for: billing lead days, billing lead time, advance billing days, billing notice period, billing advance notice, bill preparation time, billing timeline, advance notice requirements."]
        },
        "billing_frequency": {
            "description": "Billing frequency.",
            "type": ["string", "null"],
            "examples": ["What is the billing frequency? Typically stated as 'quarterly', 'monthly', etc. Look for: billing frequency, billing cycle, billing period, billing schedule, invoice frequency, statement frequency, payment cycle (monthly, quarterly, annually, etc.), fee billing schedule."]
        },
        "bill_handling": {
            "description": "How the bill is handled.",
            "type": ["string", "null"],
            "examples": ["How is the bill handled? Found in 'Billing Procedures'. Look for: bill handling, billing process, invoice processing, bill management, billing procedure, statement handling, billing workflow, invoice management, billing administration."]
        },
        "bill_format": {
            "description": "Bill format.",
            "type": ["string", "null"],
            "examples": ["What is the bill format? Refer to 'Invoice Format'. Look for: bill format, invoice format, statement format, billing template, bill layout, invoice template, statement design, billing format specifications, invoice structure."]
        },
        "mailing_instructions": {
            "description": "Mailing instructions.",
            "type": ["string", "null"],
            "examples": ["What are the mailing instructions? Found in 'Notice Provisions'. Look for: mailing instructions, delivery instructions, postal instructions, shipping instructions, mail delivery, correspondence instructions, notice delivery methods, communication delivery."]
        },
        "billing_address": {
            "description": "Billing address.",
            "type": ["string", "null"],
            "examples": ["What is the billing address? Usually listed in a 'Notices' schedule. Look for: billing address, invoice address, statement address, payment address, correspondence address, mailing address, billing location, notice address, payment delivery address."]
        },
        "borrower_names": {
            "description": "List of borrower names listed in the agreement.",
            "type": "array",
            "examples": ["Who are the borrower names listed in the agreement? Found on the cover page or preamble. Look for: borrower names, borrower entities, obligors, debtors, loan parties, credit parties, borrowing entities, company names, corporate borrowers, individual borrowers. Check signature pages and party listings. Search for company names, individual names, legal entity names, 'LLC', 'Inc.', 'Corp.', 'Partnership', entity types. Look in preamble sections that start with 'This agreement is between...', party identification sections, signature blocks, and anywhere legal names are listed."],
            "items": {"type": ["string", "null"]}
        },
        "investor": {
            "description": "Investor for this facility.",
            "type": ["string", "null"],
            "examples": ["Who is the investor for this facility? Refer to 'Schedule of Investors' or 'Subscription Agreements'. Look for: investor, investment entity, funding party, capital provider, investor name, investment fund, financial investor, equity investor, debt investor, institutional investor."]
        },
        "lender_type": {
            "description": "Type of lender (e.g., 'Bank', 'Credit Union').",
            "type": ["string", "null"],
            "examples": ["What type of lender is involved in this agreement? Found in 'Lender Definitions' or 'Commitment Schedule'. Look for: lender type, lender classification, financial institution type, creditor type, lending entity type (bank, credit union, finance company, institutional lender, etc.), lender category."]
        },
        "sub_lender_type": {
            "description": "Sub-category of the lender type if applicable.",
            "type": ["string", "null"],
            "examples": ["What is the sub-category of the lender type? May be detailed in 'Assignment and Assumption'. Look for: sub-lender type, lender sub-classification, specific lender category, detailed lender type, lender specialization, lender subcategory, specific institution type."]
        },
        "agent": {
            "description": "Agent for the loan (if any).",
            "type": ["string", "null"],
            "examples": ["Who is the agent for the loan? Clearly stated on the cover page and in 'Agency' section. Look for: agent, administrative agent, collateral agent, loan agent, facility agent, lead agent, managing agent, acting agent. Check cover page and agency provisions."]
        },
        "syndicate_agent": {
            "description": "Syndicate agent for the loan (if any).",
            "type": ["string", "null"],
            "examples": ["Who is the syndicate agent for the loan? If applicable, found in 'Syndication' section. Look for: syndicate agent, syndication agent, lead arranger, book runner, mandated lead arranger, MLA, joint lead arranger, co-agent, lead manager, bookrunner."]
        },
        "participation": {
            "description": "Details of any participations in the loan.",
            "type": "array",
            "examples": ["What are the participation details? Refer to 'Participation' or 'Lender Shares'. Look for participation agreements, lender shares, participant details, participation amounts, lender allocations."],
            "items": {
                "type": "object",
                "properties": {
                    "participant_name": {
                        "description": "Name of the participant.",
                        "type": ["string", "null"]
                    },
                    "participation_amount": {
                        "description": "Amount of the loan participated.",
                        "type": ["string", "number", "null"]
                    }
                }
            }
        },
        "collateral_details": {
            "description": "Details of collateral securing the loan, if any.",
            "type": "array",
            "examples": ["What are the collateral details? Found in 'Security Agreement' or 'Collateral Description'. Look for collateral descriptions, security interests, pledged assets, guarantees, security documents."],
            "items": {
                "type": "object",
                "properties": {
                    "collateral_type": {
                        "description": "Type of collateral (e.g., 'Property', 'Equipment').",
                        "type": ["string", "null"]
                    },
                    "collateral_value": {
                        "description": "Value of the collateral.",
                        "type": ["string", "number", "null"]
                    },
                    "security_agreement": {
                        "description": "Security agreement details if applicable.",
                        "type": ["string", "null"]
                    }
                }
            }
        },
        "financial_covenants": {
            "description": "Details of financial covenants applicable to the loan.",
            "type": "array",
            "examples": ["What are the financial covenant details? Look for a 'Financial Covenants' section. Search for leverage ratios, debt service coverage, minimum EBITDA, financial performance requirements."],
            "items": {
                "type": "object",
                "properties": {
                    "covenant_type": {
                        "description": "Type of financial covenant (e.g., 'Leverage Ratio', 'Interest Coverage').",
                        "type": ["string", "null"]
                    },
                    "covenant_value": {
                        "description": "Value or description of the covenant.",
                        "type": ["string", "null"]
                    },
                    "testing_frequency": {
                        "description": "Frequency of testing the covenant (e.g., 'quarterly', 'annually').",
                        "type": ["string", "null"]
                    }
                }
            }
        },
        "negative_covenants": {
            "description": "Details of negative covenants applicable to the loan.",
            "type": "array",
            "examples": ["What are the negative covenant details? Found in 'Negative Covenants' or 'Restrictions'. Look for restrictions on debt, liens, asset sales, mergers, dividends."],
            "items": {
                "type": "object",
                "properties": {
                    "covenant_description": {
                        "description": "Description of the negative covenant.",
                        "type": ["string", "null"]
                    },
                    "applicable_to": {
                        "description": "What the covenant is applicable to (e.g., 'all borrowers', 'specific assets').",
                        "type": ["string", "null"]
                    }
                }
            }
        },
        "reporting_requirements": {
            "description": "Details of any reporting requirements for the borrower.",
            "type": "array",
            "examples": ["What are the reporting requirements? Refer to 'Information and Reporting' or 'Covenants'. Look for financial statement requirements, compliance certificates, periodic reports."],
            "items": {
                "type": "object",
                "properties": {
                    "report_type": {
                        "description": "Type of report required (e.g., 'financial statements', 'compliance certificate').",
                        "type": ["string", "null"]
                    },
                    "reporting_frequency": {
                        "description": "Frequency of reporting (e.g., 'monthly', 'quarterly').",
                        "type": ["string", "null"]
                    },
                    "recipient": {
                        "description": "Who the report is to be sent to (e.g., 'lender', 'agent').",
                        "type": ["string", "null"]
                    }
                }
            }
        },
        "events_of_default": {
            "description": "Details of events of default and remedies.",
            "type": "array",
            "examples": ["What are the events of default? Detailed in 'Events of Default' section. Look for payment defaults, covenant breaches, bankruptcy events, material adverse changes."],
            "items": {
                "type": "object",
                "properties": {
                    "event_description": {
                        "description": "Description of the event of default.",
                        "type": ["string", "null"]
                    },
                    "remedy": {
                        "description": "Remedy or action to be taken in case of default.",
                        "type": ["string", "null"]
                    }
                }
            }
        },
        "amendment_provisions": {
            "description": "Provisions regarding amendments to the loan agreement.",
            "type": "array",
            "examples": ["What are the amendment provisions? Found in 'Amendments and Waivers'. Look for amendment procedures, required consents, voting thresholds."],
            "items": {
                "type": "object",
                "properties": {
                    "amendment_type": {
                        "description": "Type of amendment (e.g., 'financial', 'non-financial').",
                        "type": ["string", "null"]
                    },
                    "amendment_description": {
                        "description": "Description of the amendment.",
                        "type": ["string", "null"]
                    },
                    "effective_date": {
                        "description": "Effective date of the amendment.",
                        "type": ["string", "null"]
                    }
                }
            }
        },
        "assignment_provisions": {
            "description": "Provisions regarding assignment of the loan.",
            "type": "array",
            "examples": ["What are the assignment provisions? Refer to 'Assignments' or 'Transfers'. Look for assignment procedures, consent requirements, minimum assignment amounts."],
            "items": {
                "type": "object",
                "properties": {
                    "assignee": {
                        "description": "Entity to whom the loan can be assigned.",
                        "type": ["string", "null"]
                    },
                    "assignment_conditions": {
                        "description": "Conditions under which assignment is allowed.",
                        "type": ["string", "null"]
                    }
                }
            }
        },
        "governing_law": {
            "description": "The jurisdiction whose laws govern the loan agreement (e.g., 'State of New York', 'laws of England and Wales').",
            "type": ["string", "null"],
            "examples": ["What jurisdiction's laws govern this loan agreement? Typically in 'Governing Law' section. Look for: governing law, applicable law, jurisdiction, governing jurisdiction, legal jurisdiction, law governing, choice of law, governing state, governing country. Usually found near the end of the agreement."]
        },
        "definition_business_day": {
            "description": "The specific definition of 'Business Day' as provided in the definitions section of the agreement.",
            "type": ["string", "null"],
            "examples": ["What is the definition of 'Business Day'? Defined in the 'Definitions' section. Look for: business day definition, business day meaning, definition of business day, business day specification, working day definition. Check definitions section thoroughly."]
        },
        "is_revolving_facility": {
            "description": "Indicates if this is a revolving facility.",
            "type": ["boolean", "null"],
            "examples": ["Is this a revolving facility? Confirmed in the title or 'Facility Description'. Look for: revolving facility, revolving credit, revolving line, revolver, credit line, revolving commitment, line of credit, working capital facility, revolving loan. Check facility type descriptions and title page."]
        }
    },
    "required": [
        # List fields that are essential and should ideally always be present (LLM should use null if not found)
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
