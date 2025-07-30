"""
# Create a summary JSON
summary = {
    "Payer ID": ins_payerID,
    "Provider": provider_last_name,
    "Member ID": ins_memberID,
    "Date of Birth": dob,
    "Patient Name": patient_name,
    "Patient Info": {
        "DOB": dob,
        "Address": "{} {}".format(patient_info.get("addressLine1", ""), patient_info.get("addressLine2", "")).strip(),
        "City": patient_info.get("city", ""),
        "State": patient_info.get("state", ""),
        "ZIP": patient_info.get("zip", ""),
        "Relationship": patient_info.get("relationship", "")
    },
    "Insurance Info": {
        "Payer Name": insurance_info.get("payerName", ""),
        "Payer ID": ins_payerID,
        "Member ID": ins_memberID,
        "Group Number": insurance_info.get("groupNumber", ""),
        "Insurance Type": ins_insuranceType,
        "Type Code": ins_insuranceTypeCode,
        "Address": "{} {}".format(insurance_info.get("addressLine1", ""), insurance_info.get("addressLine2", "")).strip(),
        "City": insurance_info.get("city", ""),
        "State": insurance_info.get("state", ""),
        "ZIP": insurance_info.get("zip", "")
    },
    "Policy Info": {
        "Eligibility Dates": eligibilityDates,
        "Policy Member ID": policy_info.get("memberId", ""),
        "Policy Status": policy_status
    },
    "Deductible Info": {
        "Remaining Amount": remaining_amount
    }
}

Features Added:
1. Allows users to manually input patient information for deductible lookup before processing CSV data.
2. Supports multiple manual requests, each generating its own Notepad file.
3. Validates user inputs and provides feedback on required formats.
4. Displays available Payer IDs as a note after manual entries.
"""
# MediLink_Deductible.py
import MediLink_API_v3
import os, sys, requests, json
from datetime import datetime

try:
    from MediLink import MediLink_ConfigLoader
except ImportError:
    import MediLink_ConfigLoader

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.append(project_dir)

try:
    from MediBot import MediBot_Preprocessor_lib
except ImportError:
    import MediBot_Preprocessor_lib

# Function to check if the date format is correct
def validate_and_format_date(date_str):
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d-%b-%Y', '%d-%m-%Y'):
        try:
            formatted_date = datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            return formatted_date
        except ValueError:
            continue
    return None

# Load configuration
config, _ = MediLink_ConfigLoader.load_configuration()

# Initialize the API client
client = MediLink_API_v3.APIClient()

# Get provider_last_name and npi from configuration
provider_last_name = config['MediLink_Config'].get('default_billing_provider_last_name', 'Unknown')
npi = config['MediLink_Config'].get('default_billing_provider_npi', 'Unknown')

# Check if the provider_last_name is still 'Unknown'
if provider_last_name == 'Unknown':
    MediLink_ConfigLoader.log("Warning: provider_last_name was not found in the configuration.", level="WARNING")

# Define the list of payer_id's to iterate over
payer_ids = ['87726', '03432', '96385', '95467', '86050', '86047', '95378', '06111', '37602']  # United Healthcare.

# Get the latest CSV
CSV_FILE_PATH = config.get('CSV_FILE_PATH', "")
csv_data = MediBot_Preprocessor_lib.load_csv_data(CSV_FILE_PATH)

# Only keep rows that contain a valid number from the payer_ids list
valid_rows = [row for row in csv_data if str(row.get('Ins1 Payer ID', '')) in payer_ids]

# Extract important columns for summary with fallback
summary_valid_rows = [
    {
        'DOB': row.get('Patient DOB', row.get('DOB', '')),  # Try 'Patient DOB' first, then 'DOB'
        'Ins1 Member ID': row.get('Primary Policy Number', row.get('Ins1 Member ID', '')),  # Try 'Primary Policy Number' first, then 'Ins1 Member ID'
        'Ins1 Payer ID': row.get('Ins1 Payer ID', '')
    }
    for row in valid_rows
]

# Print summary of valid rows
print("\n--- Summary of Valid Rows ---")
for row in summary_valid_rows:
    print("DOB: {}, Member ID: {}, Payer ID: {}".format(row['DOB'], row['Ins1 Member ID'], row['Ins1 Payer ID']))

# List of patients with DOB and MemberID from CSV data with fallback
patients = [
    (validate_and_format_date(row.get('Patient DOB', row.get('DOB', ''))),  # Try 'Patient DOB' first, then 'DOB'
     row.get('Primary Policy Number', row.get('Ins1 Member ID', '')).strip())  # Try 'Primary Policy Number' first, then 'Ins1 Member ID'
    for row in valid_rows 
    if validate_and_format_date(row.get('Patient DOB', row.get('DOB', ''))) is not None and 
       row.get('Primary Policy Number', row.get('Ins1 Member ID', '')).strip()
]

# Function to handle manual patient deductible lookup
def manual_deductible_lookup():
    print("\n--- Manual Patient Deductible Lookup ---")
    while True:
        member_id = input("Enter the Member ID of the subscriber (or press Enter to skip): ").strip()
        if not member_id:
            print("No Member ID entered. Skipping manual lookup.\n")
            break

        dob_input = input("Enter the Date of Birth (YYYY-MM-DD): ").strip()
        formatted_dob = validate_and_format_date(dob_input)
        if not formatted_dob:
            print("Invalid DOB format. Please enter in YYYY-MM-DD format.\n")
            continue

        # Create a temporary list for single patient
        single_patient = [(formatted_dob, member_id)]
        print("Processing manual lookup for Member ID: {}, DOB: {}".format(member_id, formatted_dob))

        # Fetch eligibility data
        for payer_id in payer_ids:
            eligibility_data = get_eligibility_info(client, payer_id, provider_last_name, formatted_dob, member_id, npi)
            if eligibility_data:
                # Generate unique output file for manual request
                output_file_name = "eligibility_report_manual_{}_{}.txt".format(member_id, formatted_dob)
                output_file_path = os.path.join(os.getenv('TEMP'), output_file_name)
                with open(output_file_path, 'w') as output_file:
                    table_header = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
                        "Patient Name", "DOB", "Insurance Type", "PayID", "Policy Status", "Remaining Amt")
                    output_file.write(table_header + "\n")
                    output_file.write("-" * len(table_header) + "\n")
                    print(table_header)
                    print("-" * len(table_header))
                    display_eligibility_info(eligibility_data, formatted_dob, member_id, output_file)
                # Open the generated file in Notepad
                os.system('notepad.exe "{}"'.format(output_file_path))
                print("Manual eligibility report generated: {}\n".format(output_file_path))
                break  # Assuming one payer ID per manual lookup
            else:
                print("No eligibility data found for Payer ID: {}".format(payer_id))
        
        # Ask if the user wants to perform another manual lookup
        continue_choice = input("\nDo you want to perform another manual lookup? (Y/N): ").strip().lower()
        if continue_choice in ['n', 'no']:
            break

    # Display available Payer IDs as a note
    print("\nNOTE: The tool can only look up the following Payer IDs:")
    print(", ".join(payer_ids))
    print("-------------------------------------------------\n")


# Function to get eligibility information
def get_eligibility_info(client, payer_id, provider_last_name, date_of_birth, member_id, npi):
    try:
        # Log the parameters being sent to the function
        MediLink_ConfigLoader.log("Calling eligibility check with parameters:", level="DEBUG")
        MediLink_ConfigLoader.log("payer_id: {}".format(payer_id), level="DEBUG")
        MediLink_ConfigLoader.log("provider_last_name: {}".format(provider_last_name), level="DEBUG")
        MediLink_ConfigLoader.log("date_of_birth: {}".format(date_of_birth), level="DEBUG")
        MediLink_ConfigLoader.log("member_id: {}".format(member_id), level="DEBUG")
        MediLink_ConfigLoader.log("npi: {}".format(npi), level="DEBUG")

        # Configuration flag to control which API to use
        # Set to False to use the new Super Connector API, True to use the legacy v3 API
        USE_LEGACY_API = False
        
        if USE_LEGACY_API:
            # Use the legacy get_eligibility_v3 function as primary
            MediLink_ConfigLoader.log("Using legacy get_eligibility_v3 API", level="INFO")
            eligibility = MediLink_API_v3.get_eligibility_v3(
                client, payer_id, provider_last_name, 'MemberIDDateOfBirth', date_of_birth, member_id, npi
            )
        else:
            # Use the new Super Connector API as primary
            MediLink_ConfigLoader.log("Using new get_eligibility_super_connector API", level="INFO")
            eligibility = MediLink_API_v3.get_eligibility_super_connector(
                client, payer_id, provider_last_name, 'MemberIDDateOfBirth', date_of_birth, member_id, npi
            )
        
        # Log the response
        MediLink_ConfigLoader.log("Eligibility response: {}".format(json.dumps(eligibility, indent=4)), level="DEBUG")
        
        return eligibility
    except requests.exceptions.HTTPError as e:
        # Log the HTTP error response
        MediLink_ConfigLoader.log("HTTPError: {}".format(e), level="ERROR")
        MediLink_ConfigLoader.log("Response content: {}".format(e.response.content), level="ERROR")
    except Exception as e:
        # Log any other exceptions
        MediLink_ConfigLoader.log("Error: {}".format(e), level="ERROR")
    return None

# Helper functions to extract data from different API response formats

def extract_legacy_patient_info(policy):
    """Extract patient information from legacy API response format"""
    patient_info = policy.get("patientInfo", [{}])[0]
    return {
        'lastName': patient_info.get("lastName", ""),
        'firstName': patient_info.get("firstName", ""),
        'middleName': patient_info.get("middleName", "")
    }

def extract_super_connector_patient_info(eligibility_data):
    """Extract patient information from Super Connector API response format"""
    if not eligibility_data or 'data' not in eligibility_data:
        return {'lastName': '', 'firstName': '', 'middleName': ''}
    
    # Navigate to the first eligibility record
    eligibility_list = eligibility_data.get('data', {}).get('checkEligibility', {}).get('eligibility', [])
    if not eligibility_list:
        return {'lastName': '', 'firstName': '', 'middleName': ''}
    
    first_eligibility = eligibility_list[0]
    member_info = first_eligibility.get('eligibilityInfo', {}).get('member', {})
    
    return {
        'lastName': member_info.get("lastName", ""),
        'firstName': member_info.get("firstName", ""),
        'middleName': member_info.get("middleName", "")
    }

def extract_legacy_remaining_amount(policy):
    """Extract remaining amount from legacy API response format"""
    deductible_info = policy.get("deductibleInfo", {})
    if 'individual' in deductible_info:
        return deductible_info['individual']['inNetwork'].get("remainingAmount", "")
    elif 'family' in deductible_info:
        return deductible_info['family']['inNetwork'].get("remainingAmount", "")
    else:
        return ""

def extract_super_connector_remaining_amount(eligibility_data):
    """Extract remaining amount from Super Connector API response format"""
    if not eligibility_data or 'data' not in eligibility_data:
        return ""
    
    # Navigate to the first eligibility record
    eligibility_list = eligibility_data.get('data', {}).get('checkEligibility', {}).get('eligibility', [])
    if not eligibility_list:
        return ""
    
    first_eligibility = eligibility_list[0]
    service_levels = first_eligibility.get('serviceLevels', [])
    
    # Look for deductible information in service levels
    for service_level in service_levels:
        individual_services = service_level.get('individual', [])
        for individual in individual_services:
            services = individual.get('services', [])
            for service in services:
                # Look for deductible-related information
                if service.get('service') == 'deductible' or 'deductible' in service.get('text', '').lower():
                    return service.get('remainingAmount', "")
    
    # If no specific deductible found, try to get from plan levels
    plan_levels = first_eligibility.get('eligibilityInfo', {}).get('planLevels', [])
    for plan_level in plan_levels:
        if plan_level.get('level') == 'deductibleInfo/outOfPocket/coPayMax':
            individual_levels = plan_level.get('individual', [])
            if individual_levels:
                return individual_levels[0].get('remainingAmount', "")
    
    return ""

def extract_legacy_insurance_info(policy):
    """Extract insurance information from legacy API response format"""
    insurance_info = policy.get("insuranceInfo", {})
    return {
        'insuranceType': insurance_info.get("insuranceType", ""),
        'insuranceTypeCode': insurance_info.get("insuranceTypeCode", ""),
        'memberId': insurance_info.get("memberId", ""),
        'payerId': insurance_info.get("payerId", "")
    }

def extract_super_connector_insurance_info(eligibility_data):
    """Extract insurance information from Super Connector API response format"""
    if not eligibility_data or 'data' not in eligibility_data:
        return {'insuranceType': '', 'insuranceTypeCode': '', 'memberId': '', 'payerId': ''}
    
    # Navigate to the first eligibility record
    eligibility_list = eligibility_data.get('data', {}).get('checkEligibility', {}).get('eligibility', [])
    if not eligibility_list:
        return {'insuranceType': '', 'insuranceTypeCode': '', 'memberId': '', 'payerId': ''}
    
    first_eligibility = eligibility_list[0]
    insurance_info = first_eligibility.get('eligibilityInfo', {}).get('insuranceInfo', {})
    
    # Get coverage type from coverageTypes array
    coverage_types = insurance_info.get('coverageTypes', [])
    insurance_type = ""
    if coverage_types:
        insurance_type = coverage_types[0].get('description', '')
    
    return {
        'insuranceType': insurance_type,
        'insuranceTypeCode': insurance_info.get("productCode", ""),
        'memberId': insurance_info.get("policyNumber", ""),
        'payerId': insurance_info.get("payerId", "")
    }

def extract_legacy_policy_status(policy):
    """Extract policy status from legacy API response format"""
    policy_info = policy.get("policyInfo", {})
    return policy_info.get("policyStatus", "")

def extract_super_connector_policy_status(eligibility_data):
    """Extract policy status from Super Connector API response format"""
    if not eligibility_data or 'data' not in eligibility_data:
        return ""
    
    # Navigate to the first eligibility record
    eligibility_list = eligibility_data.get('data', {}).get('checkEligibility', {}).get('eligibility', [])
    if not eligibility_list:
        return ""
    
    first_eligibility = eligibility_list[0]
    insurance_info = first_eligibility.get('eligibilityInfo', {}).get('insuranceInfo', {})
    
    return insurance_info.get("policyStatus", "")

def is_legacy_response_format(data):
    """Determine if the response is in legacy format (has memberPolicies)"""
    return data is not None and "memberPolicies" in data

def is_super_connector_response_format(data):
    """Determine if the response is in Super Connector format (has data.checkEligibility)"""
    return data is not None and "data" in data and "checkEligibility" in data.get("data", {})

# Function to extract required fields and display in a tabular format
def display_eligibility_info(data, dob, member_id, output_file):
    if data is None:
        return

    # Determine which API response format we're dealing with
    if is_legacy_response_format(data):
        # Handle legacy API response format
        for policy in data.get("memberPolicies", []):
            # Skip non-medical policies
            if policy.get("policyInfo", {}).get("coverageType", "") != "Medical":
                continue

            patient_info = extract_legacy_patient_info(policy)
            remaining_amount = extract_legacy_remaining_amount(policy)
            insurance_info = extract_legacy_insurance_info(policy)
            policy_status = extract_legacy_policy_status(policy)

            patient_name = "{} {} {}".format(
                patient_info['firstName'], 
                patient_info['middleName'], 
                patient_info['lastName']
            ).strip()[:20]

            # Display patient information in a table row format
            table_row = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
                patient_name, dob, insurance_info['insuranceType'], 
                insurance_info['payerId'], policy_status, remaining_amount)
            output_file.write(table_row + "\n")
            print(table_row)  # Print to console for progressive display

    elif is_super_connector_response_format(data):
        # Handle Super Connector API response format
        patient_info = extract_super_connector_patient_info(data)
        remaining_amount = extract_super_connector_remaining_amount(data)
        insurance_info = extract_super_connector_insurance_info(data)
        policy_status = extract_super_connector_policy_status(data)

        patient_name = "{} {} {}".format(
            patient_info['firstName'], 
            patient_info['middleName'], 
            patient_info['lastName']
        ).strip()[:20]

        # Display patient information in a table row format
        table_row = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
            patient_name, dob, insurance_info['insuranceType'], 
            insurance_info['payerId'], policy_status, remaining_amount)
        output_file.write(table_row + "\n")
        print(table_row)  # Print to console for progressive display

    else:
        # Unknown response format - log for debugging
        MediLink_ConfigLoader.log("Unknown response format in display_eligibility_info", level="WARNING")
        MediLink_ConfigLoader.log("Response structure: {}".format(json.dumps(data, indent=2)), level="DEBUG")

# Main Execution Flow
if __name__ == "__main__":
    # Step 1: Handle Manual Deductible Lookups
    manual_deductible_lookup()

    # Step 2: Proceed with Existing CSV Processing
    print("--- Starting Batch Eligibility Processing ---")
    output_file_path = os.path.join(os.getenv('TEMP'), 'eligibility_report.txt')
    with open(output_file_path, 'w') as output_file:
        table_header = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
            "Patient Name", "DOB", "Insurance Type", "PayID", "Policy Status", "Remaining Amt")
        output_file.write(table_header + "\n")
        output_file.write("-" * len(table_header) + "\n")
        print(table_header)
        print("-" * len(table_header))

        # Set to keep track of processed patients
        processed_patients = set()

        # Loop through each payer_id and patient to call the API, then display the eligibility information
        errors = []
        for payer_id in payer_ids:
            for dob, member_id in patients:
                # Skip if this patient has already been processed
                if (dob, member_id) in processed_patients:
                    continue
                try:
                    eligibility_data = get_eligibility_info(client, payer_id, provider_last_name, dob, member_id, npi)
                    if eligibility_data is not None:
                        display_eligibility_info(eligibility_data, dob, member_id, output_file)  # Display as we get the result
                        processed_patients.add((dob, member_id))  # Mark this patient as processed
                except Exception as e:
                    errors.append((dob, member_id, str(e)))

        # Display errors if any
        if errors:
            error_msg = "\nErrors encountered during API calls:\n"
            output_file.write(error_msg)
            print(error_msg)
            for error in errors:
                error_details = "DOB: {}, Member ID: {}, Error: {}\n".format(error[0], error[1], error[2])
                output_file.write(error_details)
                print(error_details)

    # Open the generated file in Notepad
    os.system('notepad.exe "{}"'.format(output_file_path))