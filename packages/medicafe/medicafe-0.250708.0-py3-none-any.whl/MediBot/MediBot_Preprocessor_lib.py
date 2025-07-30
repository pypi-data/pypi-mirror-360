#MediBot_Preprocessor_lib.py
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
import os, csv, sys
import chardet  # Ensure chardet is imported

# Add the parent directory of the project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Attempt to import necessary modules, falling back if they are not found
try:
    import MediLink_ConfigLoader
    import MediLink_DataMgmt
except ImportError:
    from MediLink import MediLink_ConfigLoader, MediLink_DataMgmt

try:
    from MediBot_UI import app_control
    from MediBot_docx_decoder import parse_docx
except ImportError:
    from MediBot import MediBot_UI
    app_control = MediBot_UI.app_control
    from MediBot import MediBot_docx_decoder
    parse_docx = MediBot_docx_decoder.parse_docx

class InitializationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def initialize(config):
    global AHK_EXECUTABLE, CSV_FILE_PATH, field_mapping, page_end_markers
    
    required_keys = {
        'AHK_EXECUTABLE': "",
        'CSV_FILE_PATH': "",
        'field_mapping': {},
        'page_end_markers': []
    }
    
    for key, default in required_keys.items():
        try:
            globals()[key] = config.get(key, default) if key != 'field_mapping' else OrderedDict(config.get(key, default))
        except AttributeError:
            raise InitializationError("Error: '{}' not found in config.".format(key))

def open_csv_for_editing(csv_file_path):
    try:
        # Open the CSV file with its associated application
        os.system('start "" "{}"'.format(csv_file_path))
        print("After saving the revised CSV, please re-run MediBot.")
    except Exception as e:
        print("Failed to open CSV file:", e)
        
# Function to clean the headers
def clean_header(headers):
    """
    Cleans the header strings by removing unwanted characters and trimming whitespace.

    Parameters:
    headers (list of str): The original header strings.

    Returns:
    list of str: The cleaned header strings.
    """
    cleaned_headers = []
    
    for header in headers:
        # Strip leading and trailing whitespace
        cleaned_header = header.strip()
        # Remove unwanted characters while keeping spaces, alphanumeric characters, hyphens, and underscores
        cleaned_header = ''.join(char for char in cleaned_header if char.isalnum() or char.isspace() or char in ['-', '_'])
        cleaned_headers.append(cleaned_header)

    # Log the original and cleaned headers for debugging
    MediLink_ConfigLoader.log("Original headers: {}".format(headers), level="INFO")
    MediLink_ConfigLoader.log("Cleaned headers: {}".format(cleaned_headers), level="INFO")

    # Check if 'Surgery Date' is in the cleaned headers
    if 'Surgery Date' not in cleaned_headers:
        MediLink_ConfigLoader.log("WARNING: 'Surgery Date' header not found after cleaning.", level="WARNING")
        print("WARNING: 'Surgery Date' header not found after cleaning.")
        raise ValueError("Error: 'Surgery Date' header not found after cleaning.")

    return cleaned_headers

# Function to load and process CSV data
def load_csv_data(csv_file_path):
    try:
        # Check if the file exists
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError("***Error: CSV file '{}' not found.".format(csv_file_path))
        
        # Detect the file encoding
        with open(csv_file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']
            print("Detected encoding: {} (Confidence: {:.2f})".format(encoding, confidence))

        # Read the CSV file with the detected encoding
        with open(csv_file_path, 'r', encoding=encoding) as csvfile:
            reader = csv.DictReader(csvfile)
            # Clean the headers
            cleaned_headers = clean_header(reader.fieldnames)

            # Create a mapping of cleaned headers to original headers
            header_mapping = {cleaned_headers[i]: reader.fieldnames[i] for i in range(len(cleaned_headers))}

            # Process the remaining rows
            csv_data = []
            for row in reader:
                cleaned_row = {cleaned_headers[i]: row[header_mapping[cleaned_headers[i]]] for i in range(len(cleaned_headers))}
                csv_data.append(cleaned_row)

            return csv_data  # Return a list of dictionaries
    except FileNotFoundError as e:
        print(e)  # Print the informative error message
        print("Hint: Check if CSV file is located in the expected directory or specify a different path in config file.")
        print("Please correct the issue and re-run MediBot.")
        sys.exit(1)  # Halt the script
    except IOError as e:
        print("Error reading CSV file: {}. Please check the file path and permissions.".format(e))
        sys.exit(1)  # Halt the script in case of other IO errors

# CSV Pre-processor Helper functions
def add_columns(csv_data, column_headers):
    """
    Adds one or multiple columns to the CSV data.
    
    Parameters:
    csv_data (list of dict): The CSV data where each row is represented as a dictionary.
    column_headers (list of str or str): A list of column headers to be added to each row, or a single column header.
    
    Returns:
    None: The function modifies the csv_data in place.
    """
    if isinstance(column_headers, str):
        column_headers = [column_headers]
    elif not isinstance(column_headers, list):
        raise ValueError("column_headers should be a list or a string")

    for row in csv_data:
        for header in column_headers:
            row[header] = ''  # Initialize the column with empty values

# Extracting the list to a variable for future refactoring:
def filter_rows(csv_data):
    # TODO: This should be handled in the crosswalk.
    excluded_insurance = {'AETNA', 'AETNA MEDICARE', 'HUMANA MED HMO'}
    csv_data[:] = [row for row in csv_data if row.get('Patient ID') and row.get('Primary Insurance') not in excluded_insurance]

def convert_surgery_date(csv_data):
    for row in csv_data:
        surgery_date_str = row.get('Surgery Date', '')
        if not surgery_date_str:
            MediLink_ConfigLoader.log("Warning: Surgery Date not found for row: {}".format(row), level="WARNING")
            # BUG This needs a cleaning step for the Surgery Date string in case we're receiving damaged data.
            row['Surgery Date'] = datetime.min  # Assign a minimum datetime value if empty
            print("Surgery Date not found for row: {}".format(row))
        else:
            try:
                row['Surgery Date'] = datetime.strptime(surgery_date_str, '%m/%d/%Y')
            except ValueError as e:
                MediLink_ConfigLoader.log("Error parsing Surgery Date '{}': {} for row: {}".format(surgery_date_str, e, row), level="ERROR")
                row['Surgery Date'] = datetime.min  # Assign a minimum datetime value if parsing fails

def sort_and_deduplicate(csv_data):
    # Create a dictionary to hold unique patients based on Patient ID
    unique_patients = {}
    
    # Iterate through the CSV data and populate the unique_patients dictionary
    for row in csv_data:
        patient_id = row.get('Patient ID')
        if patient_id not in unique_patients:
            unique_patients[patient_id] = row
        else:
            # If the patient ID already exists, compare surgery dates
            existing_row = unique_patients[patient_id]
            if row['Surgery Date'] < existing_row['Surgery Date']:
                unique_patients[patient_id] = row

    # Convert the unique_patients dictionary back to a list and sort it
    csv_data[:] = sorted(unique_patients.values(), key=lambda x: (x['Surgery Date'], x.get('Patient Last', '').strip())) # TODO Does this need to be sorted twice? once before and once after?
    
    # TODO: Consider adding an option in the config to sort based on Surgery Schedules when available.
    # If no schedule is available, the current sorting strategy will be used.

def combine_fields(csv_data):
    for row in csv_data:
        # Safely handle the 'Surgery Date' conversion
        surgery_date = row.get('Surgery Date')
        row['Surgery Date'] = surgery_date.strftime('%m/%d/%Y') if surgery_date else ''
        
        first_name = '_'.join(part.strip() for part in row.get('Patient First', '').split()) # Join the first name parts with underscores after cleaning.
        middle_name = row.get('Patient Middle', '').strip()
        middle_name = middle_name[0] if len(middle_name) > 1 else ''  # Take only the first character or empty
        last_name = '_'.join(part.strip() for part in row.get('Patient Last', '').split()) # Join the last name parts with underscores after cleaning.
        row['Patient Name'] = ', '.join(filter(None, [last_name, first_name])) + (' ' + middle_name if middle_name else '')  # Comma between last and first, space before middle
        
        address1 = row.get('Patient Address1', '').strip()
        address2 = row.get('Patient Address2', '').strip()
        row['Patient Street'] = ' '.join(filter(None, [address1, address2]))  # Join non-empty addresses

def apply_replacements(csv_data, crosswalk):
    replacements = crosswalk.get('csv_replacements', {})
    for row in csv_data:
        for old_value, new_value in replacements.items():
            for key in ['Patient SSN', 'Primary Insurance', 'Ins1 Payer ID']:
                if row.get(key) == old_value:
                    row[key] = new_value
                    break  # Exit the loop once a replacement is made

import difflib
from collections import defaultdict

def find_best_medisoft_id(insurance_name, medisoft_ids, medisoft_to_mains_names):
    """
    Finds the best matching Medisoft ID for a given insurance name using fuzzy matching.

    Parameters:
    - insurance_name (str): The insurance name from the CSV row.
    - medisoft_ids (list): List of Medisoft IDs associated with the Payer ID.
    - medisoft_to_mains_names (dict): Mapping from Medisoft ID to list of MAINS names.

    Returns:
    - int or None: The best matching Medisoft ID or None if no match is found.
    """
    best_match_ratio = 0
    best_medisoft_id = None

    for medisoft_id in medisoft_ids:
        mains_names = medisoft_to_mains_names.get(medisoft_id, [])
        for mains_name in mains_names:
            # Preprocess names by extracting non-numeric characters and converting to uppercase
            processed_mains = ''.join(filter(lambda x: not x.isdigit(), mains_name)).upper()
            processed_insurance = ''.join(filter(lambda x: not x.isdigit(), insurance_name)).upper()

            # Log the processed names before computing the match ratio
            MediLink_ConfigLoader.log("Processing Medisoft ID '{}': Comparing processed insurance '{}' with processed mains '{}'.".format(medisoft_id, processed_insurance, processed_mains), level="DEBUG")

            # Compute the similarity ratio
            match_ratio = difflib.SequenceMatcher(None, processed_insurance, processed_mains).ratio()

            # Log the match ratio
            MediLink_ConfigLoader.log("Match ratio for Medisoft ID '{}': {:.2f}".format(medisoft_id, match_ratio), level="DEBUG")

            if match_ratio > best_match_ratio:
                best_match_ratio = match_ratio
                best_medisoft_id = medisoft_id
                # Log the current best match
                MediLink_ConfigLoader.log("New best match found: Medisoft ID '{}' with match ratio {:.2f}".format(best_medisoft_id, best_match_ratio), level="DEBUG")

    # Log the final best match ratio and ID
    MediLink_ConfigLoader.log("Final best match ratio: {:.2f} for Medisoft ID '{}'".format(best_match_ratio, best_medisoft_id), level="DEBUG")

    # No threshold applied, return the best match found
    return best_medisoft_id

def NEW_update_insurance_ids(csv_data, config, crosswalk):
    """
    Updates the 'Ins1 Insurance ID' field in each row of csv_data based on the crosswalk and MAINS data.

    Parameters:
    - csv_data (list of dict): The CSV data where each row is represented as a dictionary.
    - config (dict): Configuration object containing necessary paths and parameters.
    - crosswalk (dict): Crosswalk data containing mappings between Payer IDs and Medisoft IDs.

    Returns:
    - None: The function modifies the csv_data in place.
    """
    processed_payer_ids = set()  # Track processed Payer IDs
    MediLink_ConfigLoader.log("Starting update of insurance IDs.", level="INFO")

    # Load MAINS data to get mapping from Medisoft ID to MAINS names
    insurance_to_id = load_insurance_data_from_mains(config)  # Assuming it returns a dict mapping insurance names to IDs
    MediLink_ConfigLoader.log("Loaded MAINS data for insurance to ID mapping.", level="DEBUG")
    
    # Invert the mapping to get Medisoft ID to MAINS names
    medisoft_to_mains_names = defaultdict(list)
    for insurance_name, medisoft_id in insurance_to_id.items():
        medisoft_to_mains_names[medisoft_id].append(insurance_name)

    for row in csv_data:
        ins1_payer_id = row.get('Ins1 Payer ID', '').strip()
        MediLink_ConfigLoader.log("Processing row with Ins1 Payer ID: '{}'.".format(ins1_payer_id), level="DEBUG")
        
        if ins1_payer_id:
            # Mark this Payer ID as processed
            if ins1_payer_id not in processed_payer_ids:
                processed_payer_ids.add(ins1_payer_id)  # Add to set
                MediLink_ConfigLoader.log("Marked Payer ID '{}' as processed.".format(ins1_payer_id), level="DEBUG")
                
                # Retrieve Medisoft IDs for the current Payer ID
                medisoft_ids = crosswalk.get('payer_id', {}).get(ins1_payer_id, {}).get('medisoft_id', [])
                MediLink_ConfigLoader.log("Retrieved Medisoft IDs for Payer ID '{}': {}".format(ins1_payer_id, medisoft_ids), level="DEBUG")

        if not medisoft_ids:
            MediLink_ConfigLoader.log("No Medisoft IDs available for Payer ID '{}', creating placeholder entry.".format(ins1_payer_id), level="WARNING")
            # Create a placeholder entry in the crosswalk
            if 'payer_id' not in crosswalk:
                crosswalk['payer_id'] = {}
            crosswalk['payer_id'][ins1_payer_id] = {
                'medisoft_id': [],  # Placeholder for future Medisoft IDs
                'medisoft_medicare_id': [],  # Placeholder for future Medicare IDs
                'endpoint': None  # Placeholder for future endpoint
            }
            continue  # Skip further processing for this Payer ID

        # If only one Medisoft ID is associated, assign it directly
        if len(medisoft_ids) == 1:
            try:
                medisoft_id = int(medisoft_ids[0])
                row['Ins1 Insurance ID'] = medisoft_id
                MediLink_ConfigLoader.log("Assigned Medisoft ID '{}' to row number {} with Payer ID '{}'.".format(medisoft_id, csv_data.index(row) + 1, ins1_payer_id), level="DEBUG")
            except ValueError as e:
                MediLink_ConfigLoader.log("Error converting Medisoft ID '{}' to integer for Payer ID '{}': {}".format(medisoft_ids[0], ins1_payer_id, e), level="ERROR")
                row['Ins1 Insurance ID'] = None
            continue  # Move to the next row

        # If multiple Medisoft IDs are associated, perform fuzzy matching
        insurance_name = row.get('Primary Insurance', '').strip()
        if not insurance_name:
            MediLink_ConfigLoader.log("Row with Payer ID '{}' missing 'Primary Insurance', skipping assignment.".format(ins1_payer_id), level="WARNING")
            continue  # Skip if insurance name is missing

        best_medisoft_id = find_best_medisoft_id(insurance_name, medisoft_ids, medisoft_to_mains_names)

        if best_medisoft_id:
            row['Ins1 Insurance ID'] = best_medisoft_id
            MediLink_ConfigLoader.log("Assigned Medisoft ID '{}' to row with Payer ID '{}' based on fuzzy match.".format(best_medisoft_id, ins1_payer_id), level="INFO")
        else:
            # Default to the first Medisoft ID if no good match is found
            try:
                default_medisoft_id = int(medisoft_ids[0])
                row['Ins1 Insurance ID'] = default_medisoft_id
                MediLink_ConfigLoader.log("No suitable match found. Defaulted to Medisoft ID '{}' for Payer ID '{}'.".format(default_medisoft_id, ins1_payer_id), level="INFO")
            except ValueError as e:
                MediLink_ConfigLoader.log("Error converting default Medisoft ID '{}' to integer for Payer ID '{}': {}".format(medisoft_ids[0], ins1_payer_id, e), level="ERROR")
                row['Ins1 Insurance ID'] = None

def update_insurance_ids(csv_data, config, crosswalk):
    MediLink_ConfigLoader.log("Starting update_insurance_ids function.", level="DEBUG")
    
    # Create a dictionary to hold Medisoft IDs for each payer ID in the crosswalk
    payer_id_to_medisoft = {}
    MediLink_ConfigLoader.log("Initialized payer_id_to_medisoft dictionary.", level="DEBUG")
    
    # Populate the dictionary with data from the crosswalk
    for payer_id, details in crosswalk.get('payer_id', {}).items():
        medisoft_ids = details.get('medisoft_id', [])
        # Filter out empty strings and take the first valid ID
        medisoft_ids = [id for id in medisoft_ids if id]
        payer_id_to_medisoft[payer_id] = int(medisoft_ids[0]) if medisoft_ids else None
        MediLink_ConfigLoader.log("Processed Payer ID '{}': Medisoft IDs found: {}".format(payer_id, medisoft_ids), level="DEBUG")

    # Process the csv_data
    for row in csv_data:
        ins1_payer_id = row.get('Ins1 Payer ID', '').strip()
        MediLink_ConfigLoader.log("Processing row #{} with Ins1 Payer ID '{}'.".format(csv_data.index(row) + 1, ins1_payer_id), level="DEBUG")
        
        if ins1_payer_id not in payer_id_to_medisoft:
            # Add placeholder entry for new payer ID
            payer_id_to_medisoft[ins1_payer_id] = None  # No Medisoft ID available
            crosswalk.setdefault('payer_id', {})[ins1_payer_id] = {
                'medisoft_id': [],  # Placeholder for future Medisoft IDs
                'medisoft_medicare_id': [],  # Placeholder for future Medicare IDs
                'endpoint': None  # Placeholder for future endpoint
            }
            MediLink_ConfigLoader.log("Added placeholder entry for new Payer ID '{}'.".format(ins1_payer_id), level="INFO")
        
        # Assign the Medisoft ID to the row
        row['Ins1 Insurance ID'] = payer_id_to_medisoft[ins1_payer_id]
        MediLink_ConfigLoader.log("Assigned Medisoft ID '{}' to row with Ins1 Payer ID '{}'.".format(row['Ins1 Insurance ID'], ins1_payer_id), level="DEBUG")

def update_procedure_codes(csv_data, crosswalk): 
    
    # Get Medisoft shorthand dictionary from crosswalk and reverse it
    diagnosis_to_medisoft = crosswalk.get('diagnosis_to_medisoft', {}) # BUG We need to be careful here in case we decide we need to change the crosswalk data specifically with regard to the T8/H usage.
    medisoft_to_diagnosis = {v: k for k, v in diagnosis_to_medisoft.items()}

    # Get procedure code to diagnosis dictionary from crosswalk and reverse it for easier lookup
    diagnosis_to_procedure = {
        diagnosis_code: procedure_code
        for procedure_code, diagnosis_codes in crosswalk.get('procedure_to_diagnosis', {}).items()
        for diagnosis_code in diagnosis_codes
    }

    # Initialize counter for updated rows
    updated_count = 0

    # Update the "Procedure Code" column in the CSV data
    for row_num, row in enumerate(csv_data, start=1):
        try:
            medisoft_code = row.get('Default Diagnosis #1', '').strip()
            diagnosis_code = medisoft_to_diagnosis.get(medisoft_code)
            if diagnosis_code:
                procedure_code = diagnosis_to_procedure.get(diagnosis_code)
                if procedure_code:
                    row['Procedure Code'] = procedure_code
                    updated_count += 1
                else:
                    row['Procedure Code'] = "Unknown"  # Or handle as appropriate
            else:
                row['Procedure Code'] = "Unknown"  # Or handle as appropriate
        except Exception as e:
            MediLink_ConfigLoader.log("In update_procedure_codes, Error processing row {}: {}".format(row_num, e), level="ERROR")

    # Log total count of updated rows
    MediLink_ConfigLoader.log("Total {} 'Procedure Code' rows updated.".format(updated_count), level="INFO")

    return True

def update_diagnosis_codes(csv_data):
    try:
        # Load configuration and crosswalk
        config, crosswalk = MediLink_ConfigLoader.load_configuration()
        
        # Extract the local storage path from the configuration
        local_storage_path = config['MediLink_Config']['local_storage_path']
        
        # Initialize a dictionary to hold diagnosis codes from all DOCX files
        all_patient_data = {}

        # Convert surgery dates in CSV data
        convert_surgery_date(csv_data)
        
        # Extract all valid surgery dates from csv_data
        surgery_dates = [row['Surgery Date'] for row in csv_data if row['Surgery Date'] != datetime.min]
        
        if not surgery_dates:
            raise ValueError("No valid surgery dates found in csv_data.")
        
        # Determine the minimum and maximum surgery dates
        min_surgery_date = min(surgery_dates)
        max_surgery_date = max(surgery_dates)
        
        # Apply a ±8-day margin to the surgery dates... Increased from 5 days.
        margin = timedelta(days=8)
        threshold_start = min_surgery_date - margin
        threshold_end = max_surgery_date + margin
        
        # TODO (Low) This is a bad idea. We need a better way to handle this because it leaves 
        # us with a situation where if we take 'too long' to download the DOCX files, it will presume that the DOCX files are out of range because 
        # the modfied date is a bad proxy for the date of the surgery which would be contained inside the DOCX file. The processing overhead for extracting the
        # date of the surgery from the DOCX file is non-trivial and computationally expensive so we need a smarter way to handle this.

        MediLink_ConfigLoader.log("BAD IDEA: Processing DOCX files modified between {} and {}.".format(threshold_start, threshold_end), level="INFO")

        # Gather all relevant DOCX files in the specified directory
        docx_files = [
            os.path.join(local_storage_path, filename)
            for filename in os.listdir(local_storage_path)
            if filename.endswith(".docx")
        ]

        # Filter files based on modification time
        valid_files = [
            filepath for filepath in docx_files
            if threshold_start <= datetime.fromtimestamp(os.path.getmtime(filepath)) <= threshold_end
        ]

        # Process valid DOCX files
        for filepath in valid_files:
            MediLink_ConfigLoader.log("Processing DOCX file: {}".format(filepath), level="INFO")
            try:
                patient_data = parse_docx(filepath, surgery_dates)  # Pass surgery_dates to parse_docx
                for patient_id, service_dates in patient_data.items():
                    if patient_id not in all_patient_data:
                        all_patient_data[patient_id] = {}
                    for date_of_service, diagnosis_data in service_dates.items():
                        all_patient_data[patient_id][date_of_service] = diagnosis_data
            except Exception as e:
                MediLink_ConfigLoader.log("Error parsing DOCX file {}: {}".format(filepath, e), level="ERROR")

        # Log if no valid files were found
        if not valid_files:
            MediLink_ConfigLoader.log("No valid DOCX files found within the modification time threshold.", level="INFO")
        
        # Debug logging for all_patient_data
        MediLink_ConfigLoader.log("All patient data collected from DOCX files: {}".format(all_patient_data), level="DEBUG")
        
        # Extract patient IDs from csv_data for efficient matching
        patient_ids_in_csv = {row.get('Patient ID', '').strip() for row in csv_data}

        # Check if any patient data was collected
        if not all_patient_data or not patient_ids_in_csv.intersection(all_patient_data.keys()):
            MediLink_ConfigLoader.log("No patient data collected or no matching Patient IDs found. Skipping further processing.", level="INFO")
            return  # Exit the function early if no data is available

        # Get Medisoft shorthand dictionary from crosswalk.
        diagnosis_to_medisoft = crosswalk.get('diagnosis_to_medisoft', {})
        
        # Initialize counter for updated rows
        updated_count = 0

        # Update the "Default Diagnosis #1" column in the CSV data
        for row_num, row in enumerate(csv_data, start=1):
            patient_id = row.get('Patient ID', '').strip()
            if patient_id not in patient_ids_in_csv:
                continue  # Skip rows that do not match any patient ID

            MediLink_ConfigLoader.log("Processing row number {}.".format(row_num), level="DEBUG")
            surgery_date = row.get('Surgery Date', '')

            # Convert surgery_date to string format for lookup
            if surgery_date != datetime.min:
                surgery_date_str = surgery_date.strftime("%m-%d-%Y")
            else:
                surgery_date_str = ''

            MediLink_ConfigLoader.log("Patient ID: {}, Surgery Date: {}".format(patient_id, surgery_date_str), level="DEBUG")

            if patient_id in all_patient_data:
                if surgery_date_str in all_patient_data[patient_id]:
                    diagnosis_code, left_or_right_eye, femto_yes_or_no = all_patient_data[patient_id][surgery_date_str]
                    MediLink_ConfigLoader.log("Found diagnosis data for Patient ID: {}, Surgery Date: {}".format(patient_id, surgery_date_str), level="DEBUG")
                    
                    # Convert diagnosis code to Medisoft shorthand format.
                    medisoft_shorthand = diagnosis_to_medisoft.get(diagnosis_code, None)
                    if medisoft_shorthand is None and diagnosis_code:
                        defaulted_code = diagnosis_code.lstrip('H').lstrip('T8').replace('.', '')[-5:]
                        medisoft_shorthand = defaulted_code
                    MediLink_ConfigLoader.log("Converted diagnosis code to Medisoft shorthand: {}".format(medisoft_shorthand), level="DEBUG")
                    
                    row['Default Diagnosis #1'] = medisoft_shorthand
                    updated_count += 1
                    MediLink_ConfigLoader.log("Updated row number {} with new diagnosis code.".format(row_num), level="INFO")
                else:
                    MediLink_ConfigLoader.log("No matching surgery date found for Patient ID: {} in row {}.".format(patient_id, row_num), level="INFO")
            else:
                MediLink_ConfigLoader.log("Patient ID: {} not found in DOCX data for row {}.".format(patient_id, row_num), level="INFO")

        # Log total count of updated rows
        MediLink_ConfigLoader.log("Total {} 'Default Diagnosis #1' rows updated.".format(updated_count), level="INFO")

    except Exception as e:
        message = "An error occurred while updating diagnosis codes. Please check the DOCX files and configuration: {}".format(e)
        MediLink_ConfigLoader.log(message, level="ERROR")
        print(message)

def load_data_sources(config, crosswalk):
    """Loads historical mappings from MAPAT and Carol's CSVs."""
    patient_id_to_insurance_id = load_insurance_data_from_mapat(config, crosswalk)
    if not patient_id_to_insurance_id:
        raise ValueError("Failed to load historical Patient ID to Insurance ID mappings from MAPAT.")

    payer_id_to_patient_ids = load_historical_payer_to_patient_mappings(config)
    if not payer_id_to_patient_ids:
        raise ValueError("Failed to load historical Carol's CSVs.")

    return patient_id_to_insurance_id, payer_id_to_patient_ids

def map_payer_ids_to_insurance_ids(patient_id_to_insurance_id, payer_id_to_patient_ids):
    """Maps Payer IDs to Insurance IDs based on the historical mappings."""
    payer_id_to_details = {}
    for payer_id, patient_ids in payer_id_to_patient_ids.items():
        medisoft_ids = set()
        for patient_id in patient_ids:
            if patient_id in patient_id_to_insurance_id:
                medisoft_id = patient_id_to_insurance_id[patient_id]
                medisoft_ids.add(medisoft_id)
                MediLink_ConfigLoader.log("Added Medisoft ID {} for Patient ID {} and Payer ID {}".format(medisoft_id, patient_id, payer_id))
            else:
                MediLink_ConfigLoader.log("No matching Insurance ID found for Patient ID {}".format(patient_id))
        if medisoft_ids:
            payer_id_to_details[payer_id] = {
                "endpoint": "OPTUMEDI",  # TODO Default, to be refined via API poll. There are 2 of these defaults!
                "medisoft_id": list(medisoft_ids),
                "medisoft_medicare_id": []  # Placeholder for future implementation
            }
    return payer_id_to_details

def load_insurance_data_from_mains(config):
    """
    Loads insurance data from MAINS and creates a mapping from insurance names to their respective IDs.
    This mapping is critical for the crosswalk update process to correctly associate payer IDs with insurance IDs.

    Args:
        config (dict): Configuration object containing necessary paths and parameters.

    Returns:
        dict: A dictionary mapping insurance names to insurance IDs.
    """
    # Reset config pull to make sure its not using the MediLink config key subset
    config, crosswalk = MediLink_ConfigLoader.load_configuration()
    
    # Retrieve MAINS path and slicing information from the configuration   
    # TODO (Low) For secondary insurance, this needs to be pulling from the correct MAINS (there are 2)
    # TODO (Low) Performance: There probably needs to be a dictionary proxy for MAINS that gets updated.
    # Meh, this just has to be part of the new architecture plan where we make Medisoft a downstream 
    # recipient from the db.
    # TODO (High) The Medisoft Medicare flag needs to be brought in here.
    mains_path = config['MAINS_MED_PATH']
    mains_slices = crosswalk['mains_mapping']['slices']
    
    # Initialize the dictionary to hold the insurance to insurance ID mappings
    insurance_to_id = {}
    
    # Read data from MAINS using a provided function to handle fixed-width data
    for record, line_number in MediLink_DataMgmt.read_general_fixed_width_data(mains_path, mains_slices):
        insurance_name = record['MAINSNAME']
        # Assuming line_number gives the correct insurance ID without needing adjustment
        insurance_to_id[insurance_name] = line_number
    
    return insurance_to_id

def load_insurance_data_from_mapat(config, crosswalk):
    """
    Loads insurance data from MAPAT and creates a mapping from patient ID to insurance ID.
    
    Args:
        config (dict): Configuration object containing necessary paths and parameters.
        crosswalk ... ADD HERE.

    Returns:
        dict: A dictionary mapping patient IDs to insurance IDs.
    """
    # Retrieve MAPAT path and slicing information from the configuration
    mapat_path = app_control.get_mapat_med_path()
    mapat_slices = crosswalk['mapat_mapping']['slices']
    
    # Initialize the dictionary to hold the patient ID to insurance ID mappings
    patient_id_to_insurance_id = {}
    
    # Read data from MAPAT using a provided function to handle fixed-width data
    for record, _ in MediLink_DataMgmt.read_general_fixed_width_data(mapat_path, mapat_slices):
        patient_id = record['MAPATPXID']
        insurance_id = record['MAPATINID']
        patient_id_to_insurance_id[patient_id] = insurance_id
        
    return patient_id_to_insurance_id

def parse_z_dat(z_dat_path, config): # Why is this in MediBot and not MediLink?
    """
    Parses the Z.dat file to map Patient IDs to Insurance Names using the provided fixed-width file format.

    Args:
        z_dat_path (str): Path to the Z.dat file.
        config (dict): Configuration object containing slicing information and other parameters.

    Returns:
        dict: A dictionary mapping Patient IDs to Insurance Names.
    """
    patient_id_to_insurance_name = {}

    try:
        # Reading blocks of fixed-width data (up to 5 lines per record)
        for personal_info, insurance_info, service_info, service_info_2, service_info_3 in MediLink_DataMgmt.read_fixed_width_data(z_dat_path):
            # Parsing the data using slice definitions from the config
            parsed_data = MediLink_DataMgmt.parse_fixed_width_data(personal_info, insurance_info, service_info, service_info_2, service_info_3, config.get('MediLink_Config', config))

            # Extract Patient ID and Insurance Name from parsed data
            patient_id = parsed_data.get('PATID')
            insurance_name = parsed_data.get('INAME')

            if patient_id and insurance_name:
                patient_id_to_insurance_name[patient_id] = insurance_name
                MediLink_ConfigLoader.log("Mapped Patient ID {} to Insurance Name {}".format(patient_id, insurance_name), config, level="INFO")

    except FileNotFoundError:
        MediLink_ConfigLoader.log("File not found: {}".format(z_dat_path), config, level="INFO")
    except Exception as e:
        MediLink_ConfigLoader.log("Failed to parse Z.dat: {}".format(str(e)), config, level="INFO")

    return patient_id_to_insurance_name

def load_historical_payer_to_patient_mappings(config):
    """
    Loads historical mappings from multiple Carol's CSV files in a specified directory,
    mapping Payer IDs to sets of Patient IDs.

    Args:
        config (dict): Configuration object containing the directory path for Carol's CSV files
                       and other necessary parameters.

    Returns:
        dict: A dictionary where each key is a Payer ID and the value is a set of Patient IDs.
    """
    directory_path = os.path.dirname(config['CSV_FILE_PATH'])
    payer_to_patient_ids = defaultdict(set)

    try:
        # Check if the directory exists
        if not os.path.isdir(directory_path):
            raise FileNotFoundError("Directory '{}' not found.".format(directory_path))

        # Loop through each file in the directory containing Carol's historical CSVs
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if filename.endswith('.csv'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        patient_count = 0  # Counter for Patient IDs found in this CSV
                        for row in reader:
                            if 'Patient ID' not in row or 'Ins1 Payer ID' not in row:
                                continue  # Skip this row if either key is missing
                            if not row.get('Patient ID').strip() or not row.get('Ins1 Payer ID').strip():
                                continue  # Skip this row if either value is missing or empty
                            
                            payer_id = row['Ins1 Payer ID'].strip()
                            patient_id = row['Patient ID'].strip()
                            payer_to_patient_ids[payer_id].add(patient_id)
                            patient_count += 1  # Increment the counter for each valid mapping
                        
                        # Log the accumulated count for this CSV file
                        if patient_count > 0:
                            MediLink_ConfigLoader.log("CSV file '{}' has {} Patient IDs with Payer IDs.".format(filename, patient_count), level="DEBUG")
                        else:
                            MediLink_ConfigLoader.log("CSV file '{}' is empty or does not have valid Patient ID or Payer ID mappings.".format(filename), level="DEBUG")
                except Exception as e:
                    print("Error processing file {}: {}".format(filename, e))
                    MediLink_ConfigLoader.log("Error processing file '{}': {}".format(filename, e), level="ERROR")
    except FileNotFoundError as e:
        print("Error: {}".format(e))

    if not payer_to_patient_ids:
        print("No historical mappings were generated.")
    
    return dict(payer_to_patient_ids)

def capitalize_all_fields(csv_data):
    """
    Converts all text fields in the CSV data to uppercase.
    
    Parameters:
    csv_data (list of dict): The CSV data where each row is represented as a dictionary.
    
    Returns:
    None: The function modifies the csv_data in place.
    """
    for row in csv_data:
        for key, value in row.items():
            if isinstance(value, str):
                row[key] = value.upper()
            elif isinstance(value, datetime):
                # Keep datetime objects as they are
                pass
            elif value is not None:
                # Convert any other non-None values to string and then uppercase
                row[key] = str(value).upper()