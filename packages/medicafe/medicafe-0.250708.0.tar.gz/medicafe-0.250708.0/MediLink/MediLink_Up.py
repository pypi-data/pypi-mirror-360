# MediLink_Up.py
from datetime import datetime
import os, re, subprocess, traceback
from tqdm import tqdm
import MediLink_837p_encoder
from MediLink_ConfigLoader import log, load_configuration
from MediLink_DataMgmt import operate_winscp
import MediLink_API_v3

# Internet Connectivity Check
def check_internet_connection():
    """
    Checks if there is an active internet connection.
    Returns: Boolean indicating internet connectivity status.
    """
    # Check if TestMode is enabled
    config, _ = load_configuration()
    if config.get("MediLink_Config", {}).get("TestMode", True):
        # If TestMode is True, skip the connectivity check and return True as if the internet connection were fine
        return True
        
    try:
        # Run a ping command to a reliable external server (e.g., Google's DNS server)
        ping_process = subprocess.Popen(["ping", "-n", "1", "8.8.8.8"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ping_output, ping_error = ping_process.communicate()

        # Check if the ping was successful
        if "Reply from" in ping_output.decode("utf-8"):
            return True
        else:
            return False
    except Exception as e:
        print("An error occurred checking for internet connectivity:", e)
        return False

def submit_claims(detailed_patient_data_grouped_by_endpoint, config, crosswalk):
    """
    Submits claims for each endpoint, either via WinSCP or API, based on configuration settings.

    Parameters:
    - detailed_patient_data_grouped_by_endpoint: Dictionary with endpoints as keys and lists of patient data as values.
    - config: Configuration settings loaded from a JSON file.

    Returns:
    - None
    """
    # Accumulate submission results
    submission_results = {}
    
    if not detailed_patient_data_grouped_by_endpoint:
        print("No new files detected for submission.")
        return

    # Iterate through each endpoint and submit claims
    for endpoint, patients_data in tqdm(detailed_patient_data_grouped_by_endpoint.items(), desc="Progress", unit="endpoint"):
        if not patients_data:
            continue

        # Determine the submission method (e.g., "winscp" or "api")
        method = config.get('MediLink_Config', {}).get('endpoints', {}).get(endpoint, {}).get('submission_method', 'winscp')

        # Attempt submission to each endpoint
        if True: #confirm_transmission({endpoint: patients_data}): # Confirm transmission to each endpoint with detailed overview
            if check_internet_connection():
                client = MediLink_API_v3.APIClient()
                # Process files per endpoint
                converted_files = MediLink_837p_encoder.convert_files_for_submission(patients_data, config, crosswalk, client)
                if converted_files:
                    if method == 'winscp':
                        # Transmit files via WinSCP
                        try:
                            operation_type = "upload"
                            transmission_result = operate_winscp(operation_type, converted_files, config['MediLink_Config']['endpoints'][endpoint], config['MediLink_Config']['local_claims_path'], config)
                            success_dict = handle_transmission_result(transmission_result, config, operation_type, method)
                            submission_results[endpoint] = success_dict
                        except FileNotFoundError as e:
                            print("Failed to transmit files to {}. Error: Log file not found - {}".format(endpoint, str(e)))
                            submission_results[endpoint] = {"status": False, "error": "Log file not found - " + str(e)}
                        except IOError as e:
                            print("Failed to transmit files to {}. Error: Input/output error - {}".format(endpoint, str(e)))
                            submission_results[endpoint] = {"status": False, "error": "Input/output error - " + str(e)}
                        except Exception as e:
                            print("Failed to transmit files to {}. Error: {}".format(endpoint, str(e)))
                            submission_results[endpoint] = {"status": False, "error": str(e)}
                    elif method == 'api':
                        # Transmit files via API
                        try:
                            api_responses = []
                            for file_path in converted_files:
                                with open(file_path, 'r') as file:
                                    x12_request_data = file.read().replace('\n', '').replace('\r', '').strip()
                                    response = MediLink_API_v3.submit_uhc_claim(client, x12_request_data)
                                    api_responses.append((file_path, response))
                            success_dict = handle_transmission_result(api_responses, config, "api", method)
                            submission_results[endpoint] = success_dict
                        except Exception as e:
                            print("Failed to transmit files via API to {}. Error: {}".format(endpoint, str(e)))
                            submission_results[endpoint] = {"status": False, "error": str(e)}
                else:
                    print("No files were converted for transmission to {}.".format(endpoint))
            else:
                print("Error: No internet connection detected.")
                log("Error: No internet connection detected.", level="ERROR")
                try_again = input("Do you want to try again? (Y/N): ").strip().lower()
                if try_again != 'y':
                    print("Exiting transmission process. Please try again later.")
                    return  # Exiting the function if the user decides not to retry
        else:
            # This else statement is inaccessible because it is preceded by an if True condition, 
            # which is always true and effectively makes the else clause unreachable.
            # To handle this, we need to decide under what conditions the submission should be canceled. 
            # One option is to replace the if True with a condition that checks for some pre-submission criteria. 
            # For instance, if there is a confirmation step or additional checks that need to be performed before 
            # proceeding with the submission, these could be included here.
            print("Transmission canceled for endpoint {}.".format(endpoint)) 
        
        # Continue to next endpoint regardless of the previous outcomes

    # Build and display receipt
    build_and_display_receipt(submission_results, config)
    
    print("Claim submission process completed.\n")

def handle_transmission_result(transmission_result, config, operation_type, method):
    """
    Analyze the outcomes of file transmissions based on WinSCP log entries or API responses.

    Parameters:
    - transmission_result: List of paths for files that were attempted to be transmitted or API response details.
    - config: Configuration dictionary containing paths and settings.
    - operation_type: The type of operation being performed (e.g., "upload").
    - method: The transmission method used ("winscp" or "api").

    Returns:
    - Dictionary mapping each file path or API response to a tuple indicating successful transmission and any relevant messages.
    """
    success_dict = {}

    if method == "winscp":
        # Define the log filename based on the operation type
        log_filename = "winscp_{}.log".format(operation_type)
        # BUG local_claims_path is where the uploads are only. this needs to have a switch. Check where WinSCP actually logs though.
        # At some point we're going to want to make some aux function that cleans the winscp logs every once in a while (once a day?).
        log_path = os.path.join(config['MediLink_Config']['local_claims_path'], log_filename)
        
        try:
            # Read the contents of the WinSCP log file
            with open(log_path, 'r') as log_file:
                log_contents = log_file.readlines()

            if not log_contents:
                # Handle the case where the log file is empty
                log("Log file '{}' is empty.".format(log_path))
                success_dict = {file_path: (False, "Log file empty") for file_path in transmission_result}
            else:
                # Process the last few lines of the log file for transfer status
                last_lines = log_contents[-35:]
                for file_path in transmission_result:
                    success_message = "Transfer done: '{}'".format(file_path)
                    additional_success_message = "Upload of file '{}' was successful, but error occurred while setting the permissions and/or timestamp.".format(file_path)
                    success = any(success_message in line or additional_success_message in line for line in last_lines)
                    message = "Success" if success else "Transfer incomplete or error occurred"
                    success_dict[file_path] = (success, message)

        except FileNotFoundError:
            # Log file not found, handle the error
            log("Log file '{}' not found.".format(log_path))
            success_dict = {file_path: (False, "Log file not found") for file_path in transmission_result}
        except IOError as e:
            # Handle IO errors, such as issues reading the log file
            log("IO error when handling the log file '{}': {}".format(log_path, e))
            success_dict = {file_path: (False, "IO error: {}".format(e)) for file_path in transmission_result}
        except Exception as e:
            # Catch all other exceptions and log them
            log("Error processing the transmission log: {}".format(e))
            success_dict = {file_path: (False, "Error: {}".format(e)) for file_path in transmission_result}

    elif method == "api":
        # Process each API response to determine the success status
        for file_path, response in transmission_result:
            try:
                # Check if the API response indicates a successful submission
                success = response.get('message') in ["Claim validated and sent for further processing", "Acknowledgement pending"]
                # Record the API message.
                message = response.get('message', 'No message provided')
                success_dict[file_path] = (success, message)
            except Exception as e:
                # Handle API exception
                log("Error processing API response: {}".format(e))
                success_dict[file_path] = (False, str(e))

    return success_dict

def build_and_display_receipt(submission_results, config):
    """
    Builds and displays a receipt for submitted claims, including both successful and failed submissions.
    A receipt of submitted claims is typically attached to each printed facesheet for recordkeeping confirming submission.
    
    Parameters:
    - submission_results: Dictionary containing submission results with detailed information for each endpoint.
    - config: Configuration settings loaded from a JSON file.

    Returns:
    - None
    """
    # Prepare data for receipt
    receipt_data = prepare_receipt_data(submission_results)

    # Build the receipt
    receipt_content = build_receipt_content(receipt_data)

    # Print the receipt to the screen
    log("Printing receipt...")
    print(receipt_content)

    # Save the receipt to a text file
    save_receipt_to_file(receipt_content, config)

    log("Receipt has been generated and saved.")

def prepare_receipt_data(submission_results):
    """
    Prepare submission results for a receipt, including data from both successful and failed submissions.

    This function extracts patient names, dates of service, amounts billed, and insurance names from an 837p file.
    It also includes the date and time of batch claim submission, and the receiver name from the 1000B segment.
    Data is organized by receiver name and includes both successful and failed submissions.

    Parameters:
    - submission_results (dict): Contains submission results grouped by endpoint, with detailed status information.

    Returns:
    - dict: Organized data for receipt preparation, including both successful and failed submission details.
    """
    receipt_data = {}
    for endpoint, files in submission_results.items():
        log("Processing endpoint: {}".format(endpoint), level="INFO")
        for file_path, file_result in files.items():
            log("File path: {}".format(file_path), level="DEBUG")
            log("File result: {}".format(file_result), level="DEBUG")

            try:
                # Unpack the tuple to get status and message
                status, message = file_result
            except ValueError as e:
                file_result_length = len(file_result) if hasattr(file_result, '__len__') else 'Unknown'
                error_msg = 'Too many values to unpack.' if 'too many values to unpack' in str(e) else \
                            'Not enough values to unpack.' if 'not enough values to unpack' in str(e) else \
                            'Value unpacking error.'
                log("ValueError: {} for file_result: {} (Length: {})".format(error_msg, file_result, file_result_length), level="ERROR")
                continue
            except Exception as e:
                tb = traceback.format_exc()
                log("Unexpected error: {}. Traceback: {}".format(e, tb), level="ERROR")
                continue

            log("Status: {}, Message: {}".format(status, message), level="DEBUG")

            if endpoint not in receipt_data:
                receipt_data[endpoint] = {
                    "patients": [],
                    "date_of_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

            # Parse patient details and add the result status and message
            patient_data, _ = parse_837p_file(file_path)
            for patient in patient_data:
                patient['status'] = status
                patient['message'] = message

            receipt_data[endpoint]["patients"].extend(patient_data)
    
    validate_data(receipt_data)
    log("Receipt data: {}".format(receipt_data), level="DEBUG")
    
    return receipt_data

def validate_data(receipt_data):
    # Simple validation to check if data fields are correctly populated
    for endpoint, data in receipt_data.items():
        patients = data.get("patients", [])
        for index, patient in enumerate(patients, start=1):
            missing_fields = [field for field in ('name', 'service_date', 'amount_billed', 'insurance_name', 'status') if patient.get(field) in (None, '')]
            
            if missing_fields:
                # Log the missing fields without revealing PHI
                log("Receipt Data validation error for endpoint '{}', patient {}: Missing information in fields: {}".format(endpoint, index, ", ".join(missing_fields)))
    return True

def parse_837p_file(file_path):
    """
    Parse an 837p file to extract patient details and date of submission.

    This function reads the specified 837p file, extracts patient details such as name, service date, and amount billed,
    and retrieves the date of submission from the GS segment. It then organizes this information into a list of dictionaries
    containing patient data. If the GS segment is not found, it falls back to using the current date and time.

    Parameters:
    - file_path (str): The path to the 837p file to parse.

    Returns:
    - tuple: A tuple containing two elements:
        - A list of dictionaries, where each dictionary represents patient details including name, service date, and amount billed.
        - A string representing the date and time of submission in the format 'YYYY-MM-DD HH:MM:SS'.
    """
    patient_details = []
    date_of_submission = None
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            log("Parsing submitted 837p...")

            # Extract the submission date from the GS segment
            gs_match = re.search(r'GS\*HC\*[^*]*\*[^*]*\*([0-9]{8})\*([0-9]{4})', content)
            if gs_match:
                date = gs_match.group(1)
                time = gs_match.group(2)
                date_of_submission = datetime.strptime("{}{}".format(date, time), "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Fallback to the current date and time if GS segment is not found
                date_of_submission = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Split content using 'SE*{count}*{control_number}~' as delimiter
            patient_records = re.split(r'SE\*\d+\*\d{4}~', content)
            
            # Remove any empty strings from list that may have been added from split
            patient_records = [record for record in patient_records if record.strip()]
            
            for record in patient_records:
                # Extract patient name
                name_match = re.search(r'NM1\*IL\*1\*([^*]+)\*([^*]+)\*([^*]*)', record)
                # Extract service date
                service_date_match = re.search(r'DTP\*472\D*8\*([0-9]{8})', record)
                # Extract claim amount
                amount_match = re.search(r'CLM\*[^\*]*\*([0-9]+\.?[0-9]*)', record)
                # Extract insurance name (payer_name)
                insurance_name_match = re.search(r'NM1\*PR\*2\*([^*]+)\*', record)
                
                if name_match and service_date_match and amount_match:
                    # Handle optional middle name
                    middle_name = name_match.group(3).strip() if name_match.group(3) else ""
                    patient_name = "{} {} {}".format(name_match.group(2), middle_name, name_match.group(1)).strip()
                    service_date = "{}-{}-{}".format(service_date_match.group(1)[:4], service_date_match.group(1)[4:6], service_date_match.group(1)[6:])
                    amount_billed = float(amount_match.group(1))
                    insurance_name = insurance_name_match.group(1)
                    
                    patient_details.append({
                        "name": patient_name,
                        "service_date": service_date,
                        "amount_billed": amount_billed,
                        "insurance_name": insurance_name
                    })
    except Exception as e:
        print("Error reading or parsing the 837p file: {0}".format(str(e)))
    
    return patient_details, date_of_submission

def build_receipt_content(receipt_data):
    """
    Build the receipt content in a human-readable ASCII format with a tabular data presentation for patient information.

    Args:
        receipt_data (dict): Dictionary containing receipt data with patient details.

    Returns:
        str: Formatted receipt content as a string.
    """
    # Build the receipt content in a human-readable ASCII format
    receipt_lines = ["Submission Receipt", "=" * 60, ""]  # Header

    for endpoint, data in receipt_data.items():
        header = "Endpoint: {0} (Submitted: {1})".format(endpoint, data['date_of_submission'])
        receipt_lines.extend([header, "-" * len(header)])
        
        # Table headers
        table_header = "{:<20} | {:<15} | {:<15} | {:<20} | {:<10}".format("Patient", "Service Date", "Amount Billed", "Insurance", "Status")
        receipt_lines.append(table_header)
        receipt_lines.append("-" * len(table_header))
        
        # Adding patient information in a tabular format
        for patient in data["patients"]:
            # Use the message as the status if the submission failed
            status_display = "SUCCESS" if patient['status'] else patient['message']
            patient_info = "{:<20} | {:<15} | ${:<14} | {:<20} | {:<10}".format(
                patient['name'], 
                patient['service_date'], 
                patient['amount_billed'], 
                patient['insurance_name'], 
                status_display
            )
            receipt_lines.append(patient_info)
        
        receipt_lines.append("")  # Blank line for separation
    
    receipt_content = "\n".join(receipt_lines)
    return receipt_content

def save_receipt_to_file(receipt_content, config):
    """
    Saves the receipt content to a text file and opens it for the user.

    Parameters:
    - receipt_content (str): The formatted content of the receipt.
    - config: Configuration settings loaded from a JSON file.

    Returns:
    - None
    """
    try:
        file_name = "Receipt_{0}.txt".format(datetime.now().strftime('%Y%m%d_%H%M%S'))
        file_path = os.path.join(config['MediLink_Config']['local_claims_path'], file_name)
        
        with open(file_path, 'w') as file:
            file.write(receipt_content)
        
        log("Receipt saved to:", file_path)
        # Open the file automatically for the user (Windows-specific)
        if os.name == 'nt':
            os.startfile(file_path)
    except Exception as e:
        print("Failed to save or open receipt file:", e)

# Secure File Transmission
def confirm_transmission(detailed_patient_data_grouped_by_endpoint):
    """
    Displays detailed patient data ready for transmission and their endpoints, 
    asking for user confirmation before proceeding.

    :param detailed_patient_data_grouped_by_endpoint: Dictionary with endpoints as keys and 
            lists of detailed patient data as values.
    :param config: Configuration settings loaded from a JSON file.
    """ 
    # Clear terminal for clarity
    os.system('cls')
    
    print("\nReview of patient data ready for transmission:")
    for endpoint, patient_data_list in detailed_patient_data_grouped_by_endpoint.items():
        print("\nEndpoint: {0}".format(endpoint))
        for patient_data in patient_data_list:
            patient_info = "({1}) {0}".format(patient_data['patient_name'], patient_data['patient_id'])
            print("- {:<33} | {:<5}, ${:<6}, {}".format(
                patient_info, patient_data['surgery_date'][:5], patient_data['amount'], patient_data['primary_insurance']))
    
    while True:
        confirmation = input("\nProceed with transmission to all endpoints? (Y/N): ").strip().lower()
        if confirmation in ['y', 'n']:
            return confirmation == 'y'
        else:
            print("Invalid input. Please enter 'Y' for yes or 'N' for no.")

# Entry point if this script is run directly. Probably needs to be handled better.
if __name__ == "__main__":
    print("Please run MediLink directly.")