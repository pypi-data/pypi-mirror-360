#MediBot_Preprocessor.py
import os, re, sys, argparse
from collections import OrderedDict # so that the field_mapping stays in order.
import MediBot_Crosswalk_Library

# Add parent directory of the project to the Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

try: 
    from MediLink import MediLink_ConfigLoader
except ImportError:
    import MediLink_ConfigLoader

try:
    import MediBot_Preprocessor_lib
except ImportError:
    from MediBot import MediBot_Preprocessor_lib

try:
    from MediLink.MediLink_API_v3 import APIClient
except ImportError as e:
    raise ImportError("Failed to import APIClient from MediLink.MediLink_API_v3. "
                        "Ensure the MediLink_API_v3 module is installed and accessible.") from e

# Load configuration
# Should this also take args? Path for ./MediLink needed to be added for this to resolve
config, crosswalk = MediLink_ConfigLoader.load_configuration()

# CSV Preprocessor built for Carol
def preprocess_csv_data(csv_data, crosswalk):
    try:
        # Add the "Ins1 Insurance ID" and "Default Diagnosis #1" columns to the CSV data.
        # This initializes the columns with empty values for each row.
        columns_to_add = ['Ins1 Insurance ID', 'Default Diagnosis #1', 'Procedure Code', 'Minutes', 'Amount']
        MediLink_ConfigLoader.log("CSV Pre-processor: Initializing empty columns to the CSV data...", level="INFO")
        MediBot_Preprocessor_lib.add_columns(csv_data, columns_to_add)
        
        # Filter out rows without a Patient ID and rows where the Primary Insurance
        # is 'AETNA', 'AETNA MEDICARE', or 'HUMANA MED HMO'.
        MediLink_ConfigLoader.log("CSV Pre-processor: Filtering out missing Patient IDs and 'AETNA', 'AETNA MEDICARE', or 'HUMANA MED HMO'...", level="INFO")
        MediBot_Preprocessor_lib.filter_rows(csv_data)
        
        # Convert 'Surgery Date' from string format to datetime objects for sorting purposes.
        MediBot_Preprocessor_lib.convert_surgery_date(csv_data)
        
        # Update the CSV data to include only unique patient records.
        # Re-sort the CSV data after deduplication to ensure the correct order.
        # Sort the patients by 'Surgery Date' and then by 'Patient Last' name alphabetically.
        # Deduplicate patient records based on Patient ID, keeping the entry with the earliest surgery date.
        MediLink_ConfigLoader.log("CSV Pre-processor: Sorting and de-duplicating patient records...", level="INFO")
        MediBot_Preprocessor_lib.sort_and_deduplicate(csv_data) 
        # TODO This eventually needs to be handled differently because now we're wanting to handle both surgery dates.
        # Instead of deleting, maybe we need to make a secondary dataset or some kind of flag or isolate here where 
        # MediBot knows to skip it when entering the patient data but is ready to put Charges for the second surgery date.
        # MediLink_Scheduler will have a dictionary persist somewhere that would tell us which patients were billed 
        # and which haven't been yet. So, if the patient 'exists' in the system, the next quetion is about claims/billing status.
        # Eventually, we really want to get out of Medisoft... 
        
        # Convert 'Surgery Date' back to string format if needed for further processing.
        # Combine 'Patient First', 'Patient Middle', and 'Patient Last' into a single 'Patient Name' field.
        # Combine 'Patient Address1' and 'Patient Address2' into a single 'Patient Street' field.
        MediLink_ConfigLoader.log("CSV Pre-processor: Constructing Patient Name and Address for Medisoft...", level="INFO")
        MediBot_Preprocessor_lib.combine_fields(csv_data)
        
        # Retrieve replacement values from the crosswalk.
        # Iterate over each key-value pair in the replacements dictionary and replace the old value
        # with the new value in the corresponding fields of each row.
        MediLink_ConfigLoader.log("CSV Pre-processor: Applying mandatory replacements per Crosswalk...", level="INFO")
        MediBot_Preprocessor_lib.apply_replacements(csv_data, crosswalk)
        
        # Update the "Ins1 Insurance ID" column based on the crosswalk and the "Ins1 Payer ID" column for each row.
        # If the Payer ID is not found in the crosswalk, create a placeholder entry in the crosswalk and mark the row for review.
        MediLink_ConfigLoader.log("CSV Pre-processor: Populating 'Ins1 Insurance ID' based on Crosswalk...", level="INFO")
        MediBot_Preprocessor_lib.update_insurance_ids(csv_data, config, crosswalk)
        
        # Enrich the "Default Diagnosis #1" column based on the parsed docx for each row.
        # This needs to handle the different patient dates correctly so we get the right diagnosis code assigned to the right patient on the right date of service.
        # Currently, we've deleted all the second date entries for patients. As long as they exist in the system, they're just deleted.
        MediLink_ConfigLoader.log("CSV Pre-processor: Populating 'Default Diagnosis #1' based on Surgery Schedule and Crosswalk...", level="INFO")
        print("Parsing Surgery Schedules...") # This step takes a while.
        MediBot_Preprocessor_lib.update_diagnosis_codes(csv_data)
        
        # Enrich the procedure code column based on the diagnosis code for each patient. 
        # MediLink_ConfigLoader.log("CSV Pre-processor: Populating 'Procedure Code' based on Crosswalk...", level="INFO")
        # MediBot_Preprocessor_lib.update_procedure_codes(csv_data, crosswalk)
        
        # Convert all text fields to uppercase
        MediLink_ConfigLoader.log("CSV Pre-processor: Converting all text fields to uppercase...", level="INFO")
        print("Converting all text fields to uppercase...")
        MediBot_Preprocessor_lib.capitalize_all_fields(csv_data)
    
    except Exception as e:
        message = "An error occurred while pre-processing CSV data. Please repair the CSV directly and try again: {}".format(e)
        MediLink_ConfigLoader.log(message, level="ERROR")
        print(message)

def check_existing_patients(selected_patient_ids, MAPAT_MED_PATH):
    existing_patients = []
    patients_to_process = list(selected_patient_ids)  # Clone the selected patient IDs list

    try:
        with open(MAPAT_MED_PATH, 'r') as file:
            next(file)  # Skip header row
            for line in file:
                if line.startswith("0"): # 1 is a flag for a deleted record so it would need to be re-entered.
                    patient_id = line[194:202].strip()  # Extract Patient ID (Columns 195-202)
                    patient_name = line[9:39].strip()  # Extract Patient Name (Columns 10-39)
                    
                    if patient_id in selected_patient_ids:
                        existing_patients.append((patient_id, patient_name))
                        # Remove all occurrences of this patient_id from patients_to_process as a filter rather than .remove because 
                        # then it only makes one pass and removes the first instance.
    except FileNotFoundError:
        # Handle the case where MAPAT_MED_PATH is not found
        print("MAPAT.med was not found at location indicated in config file.")
        print("Skipping existing patient check and continuing...")
        
    # Filter out all instances of existing patient IDs
    patients_to_process = [id for id in patients_to_process if id not in [patient[0] for patient in existing_patients]]
    
    return existing_patients, patients_to_process

def intake_scan(csv_headers, field_mapping):
    identified_fields = OrderedDict()
    missing_fields_warnings = []
    required_fields = config["required_fields"]
    
    MediLink_ConfigLoader.log("Intake Scan - Field Mapping: {}".format(field_mapping), level="DEBUG")
    MediLink_ConfigLoader.log("Intake Scan - CSV Headers: {}".format(csv_headers), level="DEBUG")
    
    # Iterate over the Medisoft fields defined in field_mapping
    for medisoft_field in field_mapping.keys():
        for pattern in field_mapping[medisoft_field]:
            matched_headers = [header for header in csv_headers if re.search(pattern, header, re.IGNORECASE)]
            if matched_headers:
                # Assuming the first matched header is the desired one
                identified_fields[matched_headers[0]] = medisoft_field
                # MediLink_ConfigLoader.log("Found Header: {}".format(identified_fields[matched_headers[0]]))
                break
        else:
            # Check if the missing field is a required field before appending the warning
            if medisoft_field in required_fields:
                missing_fields_warnings.append("WARNING: No matching CSV header found for Medisoft field '{0}'".format(medisoft_field))
   
    # CSV Integrity Checks
    # Check for blank or partially blank CSV
    if len(csv_headers) == 0 or all(header == "" for header in csv_headers):
        missing_fields_warnings.append("WARNING: The CSV appears to be blank or contains only headers without data.")

    # Display the identified fields and missing fields warnings
    #MediLink_ConfigLoader.log("The following Medisoft fields have been identified in the CSV:")
    #for header, medisoft_field in identified_fields.items():
    #    MediLink_ConfigLoader.log("{} (CSV header: {})".format(medisoft_field, header))

    # This section interprets the information from identified_fields and decides if there are significant issues.
    # e.g. If the 'Street' value:key is 'Address', then any warnings about City, State, Zip can be ignored.
    for header, field in identified_fields.items():
        # Insurance Policy Numbers should be all alphanumeric with no other characters. 
        if 'Insurance Policy Number' in field:
            policy_number = identified_fields.get(header)
            MediLink_ConfigLoader.log("Checking Insurance Policy Number '{}' for alphanumeric characters.".format(policy_number), level="DEBUG")
            if not bool(re.match("^[a-zA-Z0-9]*$", policy_number)):
                missing_fields_warnings.append("WARNING: Insurance Policy Number '{}' contains invalid characters.".format(policy_number))
                MediLink_ConfigLoader.log("Insurance Policy Number '{}' contains invalid characters.".format(policy_number), level="WARNING")
        # Additional checks can be added as needed for other fields
    
    if missing_fields_warnings:
        MediLink_ConfigLoader.log("\nSome required fields could not be matched:", level="INFO")
        for warning in missing_fields_warnings:
            MediLink_ConfigLoader.log(warning, level="WARNING")

    return identified_fields

def main():
    parser = argparse.ArgumentParser(description='Run MediLink Data Management Tasks')
    parser.add_argument('--update-crosswalk', action='store_true',
                        help='Run the crosswalk update independently')
    parser.add_argument('--init-crosswalk', action='store_true',
                        help='Initialize the crosswalk using historical data from MAPAT and Carols CSV')
    parser.add_argument('--load-csv', action='store_true',
                        help='Load and process CSV data')
    parser.add_argument('--preprocess-csv', action='store_true',
                        help='Preprocess CSV data based on specific rules')
    parser.add_argument('--open-csv', action='store_true',
                        help='Open CSV for manual editing')

    args = parser.parse_args()

    config, crosswalk = MediLink_ConfigLoader.load_configuration()
    
    client = APIClient()
    
    # If no arguments provided, print usage instructions
    if not any(vars(args).values()):
        parser.print_help()
        return

    if args.update_crosswalk:
        print("Updating the crosswalk...")
        MediBot_Crosswalk_Library.crosswalk_update(client, config, crosswalk)

    if args.init_crosswalk:
        MediBot_Crosswalk_Library.initialize_crosswalk_from_mapat(client, config, crosswalk)

    if args.load_csv:
        print("Loading CSV data...")
        csv_data = MediBot_Preprocessor_lib.load_csv_data(config['CSV_FILE_PATH'])
        print("Loaded {} records from the CSV.".format(len(csv_data)))

    if args.preprocess_csv:
        if 'csv_data' in locals():
            print("Preprocessing CSV data...")
            preprocess_csv_data(csv_data, crosswalk)
        else:
            print("Error: CSV data needs to be loaded before preprocessing. Use --load-csv.")
    
    if args.open_csv:
        print("Opening CSV for editing...")
        MediBot_Preprocessor_lib.open_csv_for_editing(config['CSV_FILE_PATH'])

if __name__ == '__main__':
    main()