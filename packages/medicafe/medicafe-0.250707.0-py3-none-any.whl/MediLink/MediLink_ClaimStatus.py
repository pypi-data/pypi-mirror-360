# MediLink_ClaimStatus.py
from datetime import datetime, timedelta
import os
import MediLink_API_v3

try:
    from MediLink import MediLink_ConfigLoader
except ImportError:
    import MediLink_ConfigLoader

# Load configuration
config, _ = MediLink_ConfigLoader.load_configuration()

# Calculate start_date as 60 days before today's date and end_date as today's date
end_date = datetime.today()
start_date = end_date - timedelta(days=60)
end_date_str = end_date.strftime('%m/%d/%Y')
start_date_str = start_date.strftime('%m/%d/%Y')

# Get billing provider TIN from configuration
billing_provider_tin = config['MediLink_Config'].get('billing_provider_tin')

# Define the list of payer_id's to iterate over
payer_ids = ['87726']  # Default value, getting a bad request error when trying to get all payer_ids.
# Allowed payer id's for UHC
# payer_ids = ['87726', '03432', '96385', '95467', '86050', '86047', '95378', '06111', '37602']

# Initialize the API client
client = MediLink_API_v3.APIClient()

# Function to process and display the data in a compact, tabular format
def display_claim_summary(claim_summary, payer_id, output_file):
    claims = claim_summary.get('claims', [])
    
    # Display header
    header = "Payer ID: {} | Start Date: {} | End Date: {}".format(payer_id, start_date_str, end_date_str)
    print(header)
    output_file.write(header + "\n")  # Write header to the output file
    print("=" * len(header))
    output_file.write("=" * len(header) + "\n")  # Write separator to the output file

    # Table header
    table_header = "{:<10} | {:<10} | {:<20} | {:<6} | {:<6} | {:<7} | {:<7} | {:<7} | {:<7}".format(
        "Claim #", "Status", "Patient", "Proc.", "Serv.", "Allowed", "Paid", "Pt Resp", "Charged")
    print(table_header)
    output_file.write(table_header + "\n")  # Write table header to the output file
    print("-" * len(table_header))
    output_file.write("-" * len(table_header) + "\n")  # Write separator to the output file

    # Process each claim and display it in a compact format
    claims_dict = {}
    for claim in claims:
        claim_number = claim['claimNumber']  # String: e.g., "29285698"
        claim_status = claim['claimStatus']  # String: e.g., "Finalized"
        patient_first_name = claim['memberInfo']['ptntFn']  # String: e.g., "FRANK"
        patient_last_name = claim['memberInfo']['ptntLn']  # String: e.g., "LOHR"
        processed_date = claim['claimSummary']['processedDt']  # String (Date in "MM/DD/YYYY" format): e.g., "06/10/2024"
        first_service_date = claim['claimSummary']['firstSrvcDt']  # String (Date in "MM/DD/YYYY" format): e.g., "05/13/2024"
        total_charged_amount = claim['claimSummary']['totalChargedAmt']  # String (Decimal as String): e.g., "450.00"
        total_allowed_amount = claim['claimSummary']['totalAllowdAmt']  # String (Decimal as String): e.g., "108.95"
        total_paid_amount = claim['claimSummary']['totalPaidAmt']  # String (Decimal as String): e.g., "106.78"
        total_patient_responsibility_amount = claim['claimSummary']['totalPtntRespAmt']  # String (Decimal as String): e.g., "0.00"
        
        patient_name = "{} {}".format(patient_first_name, patient_last_name)

        # Store claims in a dictionary to handle duplicate claim numbers
        if claim_number not in claims_dict:
            claims_dict[claim_number] = []
        claims_dict[claim_number].append({
            'claim_status': claim_status,
            'patient_name': patient_name,
            'processed_date': processed_date,
            'first_service_date': first_service_date,
            'total_charged_amount': total_charged_amount,
            'total_allowed_amount': total_allowed_amount,
            'total_paid_amount': total_paid_amount,
            'total_patient_responsibility_amount': total_patient_responsibility_amount,
            'claim_xwalk_data': claim['claimSummary']['clmXWalkData']
        })

    # Sort claims by first_service_date
    sorted_claims = sorted(claims_dict.items(), key=lambda x: x[1][0]['first_service_date'])

    for claim_number, claim_data_list in sorted_claims:
        # Check for repeated claim numbers and validate data
        if len(claim_data_list) > 1:
            # Validate data
            unique_claims = {tuple(claim_data.items()) for claim_data in claim_data_list}
            if len(unique_claims) == 1:
                # Data is the same, only print once
                claim_data = claim_data_list[0]
                table_row = "{:<10} | {:<10} | {:<20} | {:<6} | {:<6} | {:<7} | {:<7} | {:<7} | {:<7}".format(
                    claim_number, claim_data['claim_status'], claim_data['patient_name'][:20], 
                    claim_data['processed_date'][:5], claim_data['first_service_date'][:5],
                    claim_data['total_allowed_amount'], claim_data['total_paid_amount'], 
                    claim_data['total_patient_responsibility_amount'], claim_data['total_charged_amount']
                )
                print(table_row)
                output_file.write(table_row + "\n")  # Write each row to the output file

                if claim_data['total_paid_amount'] == '0.00':
                    for xwalk in claim_data['claim_xwalk_data']:
                        clm507Cd = xwalk['clm507Cd']  # String: e.g., "F1"
                        clm507CdDesc = xwalk['clm507CdDesc']  # String: e.g., "Finalized/Payment-The claim/line has been paid."
                        clm508Cd = xwalk['clm508Cd']  # String: e.g., "104"
                        clm508CdDesc = xwalk['clm508CdDesc']  # String: e.g., "Processed according to plan provisions..."
                        clmIcnSufxCd = xwalk['clmIcnSufxCd']  # String: e.g., "01"
                        print("  507: {} ({}) | 508: {} ({}) | ICN Suffix: {}".format(clm507Cd, clm507CdDesc, clm508Cd, clm508CdDesc, clmIcnSufxCd))
            else:
                # Data is different, print all
                for claim_data in claim_data_list:
                    table_row = "{:<10} | {:<10} | {:<20} | {:<6} | {:<6} | {:<7} | {:<7} | {:<7} | {:<7}".format(
                        claim_number, claim_data['claim_status'], claim_data['patient_name'][:20], 
                        claim_data['processed_date'][:5], claim_data['first_service_date'][:5],
                        claim_data['total_allowed_amount'], claim_data['total_paid_amount'], 
                        claim_data['total_patient_responsibility_amount'], claim_data['total_charged_amount']
                    )
                    print(table_row + " (Duplicate with different data)")
                    output_file.write(table_row + " (Duplicate with different data)\n")  # Write each row to the output file

                    if claim_data['total_paid_amount'] == '0.00':
                        for xwalk in claim_data['claim_xwalk_data']:
                            clm507Cd = xwalk['clm507Cd']  # String: e.g., "F1"
                            clm507CdDesc = xwalk['clm507CdDesc']  # String: e.g., "Finalized/Payment-The claim/line has been paid."
                            clm508Cd = xwalk['clm508Cd']  # String: e.g., "104"
                            clm508CdDesc = xwalk['clm508CdDesc']  # String: e.g., "Processed according to plan provisions..."
                            clmIcnSufxCd = xwalk['clmIcnSufxCd']  # String: e.g., "01"
                            print("  507: {} ({}) | 508: {} ({}) | ICN Suffix: {}".format(clm507Cd, clm507CdDesc, clm508Cd, clm508CdDesc, clmIcnSufxCd))
        else:
            # Only one claim, print normally
            claim_data = claim_data_list[0]
            table_row = "{:<10} | {:<10} | {:<20} | {:<6} | {:<6} | {:<7} | {:<7} | {:<7} | {:<7}".format(
                claim_number, claim_data['claim_status'], claim_data['patient_name'][:20], 
                claim_data['processed_date'][:5], claim_data['first_service_date'][:5],
                claim_data['total_allowed_amount'], claim_data['total_paid_amount'], 
                claim_data['total_patient_responsibility_amount'], claim_data['total_charged_amount']
            )
            print(table_row)
            output_file.write(table_row + "\n")  # Write each row to the output file

            if claim_data['total_paid_amount'] == '0.00':
                for xwalk in claim_data['claim_xwalk_data']:
                    clm507Cd = xwalk['clm507Cd']  # String: e.g., "F1"
                    clm507CdDesc = xwalk['clm507CdDesc']  # String: e.g., "Finalized/Payment-The claim/line has been paid."
                    clm508Cd = xwalk['clm508Cd']  # String: e.g., "104"
                    clm508CdDesc = xwalk['clm508CdDesc']  # String: e.g., "Processed according to plan provisions..."
                    clmIcnSufxCd = xwalk['clmIcnSufxCd']  # String: e.g., "01"
                    print("  507: {} ({}) | 508: {} ({}) | ICN Suffix: {}".format(clm507Cd, clm507CdDesc, clm508Cd, clm508CdDesc, clmIcnSufxCd))

# Create a temporary file to store the claim summary
output_file_path = os.path.join(os.getenv('TEMP'), 'claim_summary_report.txt')
with open(output_file_path, 'w') as output_file:
    # Loop through each payer_id and call the API, then display the claim summary
    for payer_id in payer_ids:
        claim_summary = MediLink_API_v3.get_claim_summary_by_provider(client, billing_provider_tin, start_date_str, end_date_str, payer_id=payer_id)
        display_claim_summary(claim_summary, payer_id, output_file)  # Pass output_file to the display function

# Open the generated file in Notepad
os.startfile(output_file_path)  # Use os.startfile for better handling