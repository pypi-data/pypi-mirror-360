import csv, os, re, subprocess, time
from datetime import datetime, timedelta

# Need this for running Medibot and MediLink
try:
    import MediLink_ConfigLoader
    import MediLink_UI
except ImportError:
    from . import MediLink_ConfigLoader
    from . import MediLink_UI

# Helper function to slice and strip values with optional key suffix
def slice_data(data, slices, suffix=''):
    # Convert slices list to a tuple for slicing operation
    return {key + suffix: data[slice(*slices[key])].strip() for key in slices}

# Function to parse fixed-width Medisoft output and extract claim data
def parse_fixed_width_data(personal_info, insurance_info, service_info, service_info_2=None, service_info_3=None, config=None):
    
    # Make sure we have the right config
    if not config:  # Checks if config is None or an empty dictionary
        MediLink_ConfigLoader.log("No config passed to parse_fixed_width_data. Re-loading config...", level="WARNING")
        config, _ = MediLink_ConfigLoader.load_configuration()
    
    config = config.get('MediLink_Config', config) # Safest config call.
    
    # Load slice definitions from config within the MediLink_Config section
    personal_slices = config['fixedWidthSlices']['personal_slices']
    insurance_slices = config['fixedWidthSlices']['insurance_slices']
    service_slices = config['fixedWidthSlices']['service_slices']

    # Parse each segment
    parsed_data = {}
    parsed_data.update(slice_data(personal_info, personal_slices))
    parsed_data.update(slice_data(insurance_info, insurance_slices))
    parsed_data.update(slice_data(service_info, service_slices))
    
    if service_info_2:
        parsed_data.update(slice_data(service_info_2, service_slices, suffix='_2'))
    
    if service_info_3:
        parsed_data.update(slice_data(service_info_3, service_slices, suffix='_3'))
    
    # Replace underscores with spaces in first and last names since this is downstream of MediSoft. 
    if 'FIRST' in parsed_data:
        parsed_data['FIRST'] = parsed_data['FIRST'].replace('_', ' ')
    if 'LAST' in parsed_data:
        parsed_data['LAST'] = parsed_data['LAST'].replace('_', ' ')
    
    MediLink_ConfigLoader.log("Successfully parsed data from segments", config, level="INFO")
    
    return parsed_data

# Function to read fixed-width Medisoft output and extract claim data
def read_fixed_width_data(file_path):
    # Reads the fixed width data from the file and yields each patient's
    # personal, insurance, and service information.
    MediLink_ConfigLoader.log("Starting to read fixed width data...")
    with open(file_path, 'r') as file:
        lines_buffer = []  # Buffer to hold lines for current patient data
        
        def yield_record(buffer):
            personal_info = buffer[0]
            insurance_info = buffer[1]
            service_info = buffer[2]
            service_info_2 = buffer[3] if len(buffer) > 3 else None
            service_info_3 = buffer[4] if len(buffer) > 4 else None
            MediLink_ConfigLoader.log("Successfully read data from file: {}".format(file_path), level="INFO")
            return personal_info, insurance_info, service_info, service_info_2, service_info_3
        
        for line in file:
            stripped_line = line.strip()
            if stripped_line:
                lines_buffer.append(stripped_line)
                if 3 <= len(lines_buffer) <= 5:
                    next_line = file.readline().strip()
                    if not next_line:
                        yield yield_record(lines_buffer)
                        lines_buffer.clear()
            else:
                if len(lines_buffer) >= 3:
                    yield yield_record(lines_buffer)
                    lines_buffer.clear()
                    
        if lines_buffer:  # Yield any remaining buffer if file ends without a blank line
            yield yield_record(lines_buffer)

# TODO (Refactor) Consider consolidating with the other read_fixed_with_data 
def read_general_fixed_width_data(file_path, slices):
    # handle any fixed-width data based on provided slice definitions
    with open(file_path, 'r', encoding='utf-8') as file:
        next(file)  # Skip the header
        for line_number, line in enumerate(file, start=1):
            insurance_name = {key: line[start:end].strip() for key, (start, end) in slices.items()}
            yield insurance_name, line_number

def consolidate_csvs(source_directory, file_prefix="Consolidated", interactive=False):
    """
    Consolidate CSV files in the source directory into a single CSV file.
    
    Parameters:
        source_directory (str): The directory containing the CSV files to consolidate.
        file_prefix (str): The prefix for the consolidated file's name.
        interactive (bool): If True, prompt the user for confirmation before overwriting existing files.
    
    Returns:
        str: The filepath of the consolidated CSV file, or None if no files were consolidated.
    """
    today = datetime.now()
    consolidated_filename = "{}_{}.csv".format(file_prefix, today.strftime("%m%d%y"))
    consolidated_filepath = os.path.join(source_directory, consolidated_filename)

    consolidated_data = []
    header_saved = False
    expected_header = None

    # Check if the file already exists and log the action
    if os.path.exists(consolidated_filepath):
        MediLink_ConfigLoader.log("The file {} already exists. It will be overwritten.".format(consolidated_filename), level="INFO")
        if interactive:
            overwrite = input("The file {} already exists. Do you want to overwrite it? (y/n): ".format(consolidated_filename)).strip().lower()
            if overwrite != 'y':
                MediLink_ConfigLoader.log("User opted not to overwrite the file {}.".format(consolidated_filename), level="INFO")
                return None

    for filename in os.listdir(source_directory):
        filepath = os.path.join(source_directory, filename)
        if not filepath.endswith('.csv') or os.path.isdir(filepath) or filepath == consolidated_filepath:
            continue  # Skip non-CSV files, directories, and the target consolidated file itself

        # Check if the file was created within the last day
        modification_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        if modification_time < today - timedelta(days=1):
            continue  # Skip files not modified in the last day

        try:
            with open(filepath, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)  # Read the header
                if not header_saved:
                    expected_header = header
                    consolidated_data.append(header)
                    header_saved = True
                elif header != expected_header:
                    MediLink_ConfigLoader.log("Header mismatch in file {}. Skipping file.".format(filepath), level="WARNING")
                    continue

                consolidated_data.extend(row for row in reader)
        except StopIteration:
            MediLink_ConfigLoader.log("File {} is empty or contains only header. Skipping file.".format(filepath), level="WARNING")
            continue
        except Exception as e:
            MediLink_ConfigLoader.log("Error processing file {}: {}".format(filepath, e), level="ERROR")
            continue

        os.remove(filepath)
        MediLink_ConfigLoader.log("Deleted source file after consolidation: {}".format(filepath), level="INFO")

    if consolidated_data:
        with open(consolidated_filepath, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(consolidated_data)
        MediLink_ConfigLoader.log("Consolidated CSVs into {}".format(consolidated_filepath), level="INFO")
        return consolidated_filepath
    else:
        MediLink_ConfigLoader.log("No valid CSV files were found for consolidation.", level="INFO")
        return None

def operate_winscp(operation_type, files, endpoint_config, local_storage_path, config):
    """
    General function to operate WinSCP for uploading or downloading files.
    """
    MediLink_ConfigLoader.log("Starting operate_winscp with operation_type: {}".format(operation_type))
    
    config = ensure_config_loaded(config)
    winscp_path = get_winscp_path(config)
    
    if not os.path.isfile(winscp_path):
        MediLink_ConfigLoader.log("WinSCP.com not found at {}".format(winscp_path), level="ERROR")
        return []

    validate_endpoint_config(endpoint_config)
    winscp_log_path = setup_logging(operation_type, local_storage_path)

    # Validate the local_storage_path and replace it if necessary
    local_storage_path = validate_local_storage_path(local_storage_path, config)

    remote_directory = get_remote_directory(endpoint_config, operation_type)
    command = build_command(winscp_path, winscp_log_path, endpoint_config, remote_directory, operation_type, files, local_storage_path)

    if config.get("TestMode", True):
        MediLink_ConfigLoader.log("Test mode is enabled. Simulating operation.")
        return simulate_operation(operation_type, files, config)
    
    result = execute_winscp_command(command, operation_type, files, local_storage_path)
    MediLink_ConfigLoader.log("[Execute WinSCP Command] Result: {}".format(result), level="DEBUG")
    return result

def validate_local_storage_path(local_storage_path, config):
    """
    Validates the local storage path and replaces it with outputFilePath from config if it contains spaces.
    """
    if ' ' in local_storage_path:
        MediLink_ConfigLoader.log("Local storage path contains spaces, using outputFilePath from config.", level="WARN")
        output_file_path = config.get('outputFilePath', None)
        if not output_file_path:
            raise ValueError("outputFilePath not found in config.")
        return os.path.normpath(output_file_path)
    return os.path.normpath(local_storage_path)

def ensure_config_loaded(config):
    MediLink_ConfigLoader.log("Ensuring configuration is loaded.")
    if not config:
        MediLink_ConfigLoader.log("Warning: No config passed to ensure_config_loaded. Re-loading config...")
        config, _ = MediLink_ConfigLoader.load_configuration()
    
    # Check if config was successfully loaded
    if not config or 'MediLink_Config' not in config:
        MediLink_ConfigLoader.log("Failed to load the MediLink configuration. Config is None or missing 'MediLink_Config'.")
        raise RuntimeError("Failed to load the MediLink configuration. Config is None or missing 'MediLink_Config'.")

    # Check that 'endpoints' key exists within 'MediLink_Config'
    if 'endpoints' not in config['MediLink_Config']:
        MediLink_ConfigLoader.log("The loaded configuration is missing the 'endpoints' section.")
        raise ValueError("The loaded configuration is missing the 'endpoints' section.")

    # Additional checks can be added here to ensure all expected keys and structures are present
    if 'local_storage_path' not in config['MediLink_Config']:
        MediLink_ConfigLoader.log("The loaded configuration is missing the 'local_storage_path' setting.")
        raise ValueError("The loaded configuration is missing the 'local_storage_path' setting.")

    MediLink_ConfigLoader.log("Configuration loaded successfully.")
    return config['MediLink_Config']  # Return the relevant part of the config for simplicity

def get_winscp_path(config):
    MediLink_ConfigLoader.log("Retrieving WinSCP path from provided config.")
    
    def find_winscp_path(cfg):
        if 'winscp_path' in cfg:
            # cfg is already 'MediLink_Config'
            MediLink_ConfigLoader.log("Config provided directly as 'MediLink_Config'.")
            return cfg.get('winscp_path')
        else:
            # cfg is the full configuration, retrieve 'MediLink_Config'
            MediLink_ConfigLoader.log("Config provided as full configuration; accessing 'MediLink_Config'.")
            medi_link_config = cfg.get('MediLink_Config', {})
            return medi_link_config.get('winscp_path')

    # Attempt to find the WinSCP path using the provided config
    winscp_path = find_winscp_path(config)
    
    # If the path is not found, attempt to use default paths
    if not winscp_path:
        error_message = "WinSCP path not found in config. Attempting to use default paths."
        # print(error_message)
        MediLink_ConfigLoader.log(error_message)
        
        # Try the default paths
        default_paths = [
            os.path.join(os.getcwd(), "Installers", "WinSCP-Portable", "WinSCP.com"),
            os.path.join(os.getcwd(), "Necessary Programs", "WinSCP-Portable", "WinSCP.com")
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                found_message = "WinSCP found at {}. Using this path.".format(path)
                # print(found_message)
                MediLink_ConfigLoader.log(found_message)
                return path
        
        # If no valid path is found, attempt to reload the configuration
        reload_message = "WinSCP not found in config or default paths. Reloading the entire configuration."
        # print(reload_message)
        MediLink_ConfigLoader.log(reload_message)
        
        try:
            config, _ = MediLink_ConfigLoader.load_configuration()
            winscp_path = find_winscp_path(config)
            
            if winscp_path:
                success_message = "WinSCP path found after reloading configuration. Using this path."
                # print(success_message)
                MediLink_ConfigLoader.log(success_message)
                return winscp_path
            else:
                raise FileNotFoundError("WinSCP path not found even after reloading configuration.")
        
        except Exception as e:
            error_message = "Failed to reload configuration or find WinSCP path: {}. Exiting script.".format(e)
            print(error_message)
            MediLink_ConfigLoader.log(error_message)
            raise FileNotFoundError(error_message)
    
    return winscp_path

def validate_endpoint_config(endpoint_config):
    MediLink_ConfigLoader.log("Validating endpoint configuration.")
    if not isinstance(endpoint_config, dict):
        MediLink_ConfigLoader.log("Endpoint configuration object is invalid. Expected a dictionary, got: {}".format(type(endpoint_config)))
        raise ValueError("Endpoint configuration object is invalid. Expected a dictionary, got: {}".format(type(endpoint_config)))

def setup_logging(operation_type, local_storage_path):
    MediLink_ConfigLoader.log("Setting up logging for operation type: {}".format(operation_type))
    log_filename = "winscp_upload.log" if operation_type == "upload" else "winscp_download.log"
    return os.path.join(local_storage_path, log_filename)

def get_remote_directory(endpoint_config, operation_type):
    MediLink_ConfigLoader.log("Getting remote directory for operation type: {}".format(operation_type))
    if endpoint_config is None:
        MediLink_ConfigLoader.log("Error: Endpoint configuration is None.")
        raise ValueError("Endpoint configuration is None. Expected a dictionary with configuration details.")

    if not isinstance(endpoint_config, dict):
        MediLink_ConfigLoader.log("Error: Endpoint configuration is invalid. Expected a dictionary, got: {}".format(type(endpoint_config)))
        raise TypeError("Endpoint configuration is invalid. Expected a dictionary, got: {}".format(type(endpoint_config)))

    try:
        if operation_type == "upload":
            return endpoint_config['remote_directory_up']
        elif operation_type == "download":
            return endpoint_config['remote_directory_down']
        else:
            MediLink_ConfigLoader.log("Invalid operation type: {}. Expected 'upload' or 'download'.".format(operation_type))
            raise ValueError("Invalid operation type: {}. Expected 'upload' or 'download'.".format(operation_type))
    except KeyError as e:
        MediLink_ConfigLoader.log("Critical Error: Endpoint config is missing key: {}".format(e))
        raise RuntimeError("Configuration error: Missing required remote directory in endpoint configuration.")

def build_command(winscp_path, winscp_log_path, endpoint_config, remote_directory, operation_type, files, local_storage_path, newer_than=None, filemask=None):
    # Log the operation type
    MediLink_ConfigLoader.log("[Build Command] Building WinSCP command for operation type: {}".format(operation_type))

    session_name = endpoint_config.get('session_name', '')

    # Initial command structure with options to disable timestamp preservation and permission setting (should now be compatible with Availity, hopefully this doesn't break everything else)
    command = [
        winscp_path,
        '/log=' + winscp_log_path,
        '/loglevel=1',
        '/nopreservetime',  # Disable timestamp preservation
        '/nopermissions',   # Disable permission setting
        '/command',
        'open {}'.format(session_name),
        'cd /',
        'cd {}'.format(remote_directory)
    ]

    try:
        # Handle upload operation
        if operation_type == "upload":
            if not files:
                MediLink_ConfigLoader.log("Error: No files provided for upload operation.", level="ERROR")
                raise ValueError("No files provided for upload operation.")

            put_commands = []
            for f in files:
                # Normalize the path
                normalized_path = os.path.normpath(f)
                original_path = normalized_path  # Keep for logging

                # Remove leading slash if present
                if normalized_path.startswith('\\') or normalized_path.startswith('/'):
                    normalized_path = normalized_path.lstrip('\\/')
                    MediLink_ConfigLoader.log("Removed leading slash from path: {}".format(original_path), level="DEBUG")

                # Remove trailing slash if present
                if normalized_path.endswith('\\') or normalized_path.endswith('/'):
                    normalized_path = normalized_path.rstrip('\\/')
                    MediLink_ConfigLoader.log("Removed trailing slash from path: {}".format(original_path), level="DEBUG")

                # Determine if quotes are necessary (e.g., if path contains spaces)
                if ' ' in normalized_path:
                    put_command = 'put "{}"'.format(normalized_path)
                    MediLink_ConfigLoader.log("Constructed put command with quotes: {}".format(put_command), level="DEBUG")
                else:
                    put_command = 'put {}'.format(normalized_path)
                    MediLink_ConfigLoader.log("Constructed put command without quotes: {}".format(put_command), level="DEBUG")

                put_commands.append(put_command)
            command += put_commands

        # Handle download operation
        elif operation_type == "download":
            lcd_path = os.path.normpath(local_storage_path)
            original_lcd_path = lcd_path  # Keep for logging

            # Remove leading slash if present
            if lcd_path.startswith('\\') or lcd_path.startswith('/'):
                lcd_path = lcd_path.lstrip('\\/')
                MediLink_ConfigLoader.log("Removed leading slash from local storage path: {}".format(original_lcd_path), level="DEBUG")

            # Remove trailing slash if present
            if lcd_path.endswith('\\') or lcd_path.endswith('/'):
                lcd_path = lcd_path.rstrip('\\/')
                MediLink_ConfigLoader.log("Removed trailing slash from local storage path: {}".format(original_lcd_path), level="DEBUG")

            # Determine if quotes are necessary (e.g., if path contains spaces)
            if ' ' in lcd_path:
                lcd_command = 'lcd "{}"'.format(lcd_path)
                MediLink_ConfigLoader.log("Constructed lcd command with quotes: {}".format(lcd_command), level="DEBUG")
            else:
                lcd_command = 'lcd {}'.format(lcd_path)
                MediLink_ConfigLoader.log("Constructed lcd command without quotes: {}".format(lcd_command), level="DEBUG")

            command.append(lcd_command)

            # Handle filemask input
            if filemask:
                # TODO: Implement logic to translate filemask into WinSCP syntax
                # This should handle cases where filemask is a list, JSON, dictionary, or None.
                # Example: Convert to a string like "*.{ext1}|*.{ext2}|*.{ext3}".
                if isinstance(filemask, list):
                    filemask_str = '|'.join(['*.' + ext for ext in filemask])
                elif isinstance(filemask, dict):
                    filemask_str = '|'.join(['*.' + ext for ext in filemask.keys()])
                elif isinstance(filemask, str):
                    filemask_str = filemask  # Assume it's already in the correct format
                else:
                    filemask_str = '*'  # Default to all files if filemask is None or unsupported type
            else:
                filemask_str = '*'  # Default to all files if filemask is None

            # Use synchronize command for efficient downloading
            if newer_than:
                command.append('synchronize local -filemask="{}" -newerthan={}'.format(filemask_str, newer_than))
            else:
                command.append('synchronize local -filemask="{}"'.format(filemask_str))

        # Close and exit commands
        command += ['close', 'exit']
        MediLink_ConfigLoader.log("[Build Command] WinSCP command: {}".format(command))
        return command

    except Exception as e:
        MediLink_ConfigLoader.log("Error in build_command: {}. Reverting to original implementation.".format(e), level="ERROR")

        # Fallback to original implementation
        # Handle upload operation
        if operation_type == "upload":
            if not files:
                MediLink_ConfigLoader.log("Error: No files provided for upload operation.", level="ERROR")
                raise ValueError("No files provided for upload operation.")
            command.extend(["put {}".format(os.path.normpath(file_path)) for file_path in files])

        # Handle download operation
        else:
            command.append('get *')

        # Close and exit commands
        command.extend(['close', 'exit'])
        MediLink_ConfigLoader.log("[Build Command] Original WinSCP command: {}".format(command))
        return command

def simulate_operation(operation_type, files, config):
    MediLink_ConfigLoader.log("Test Mode is enabled! Simulating WinSCP {} operation.".format(operation_type))
    
    if operation_type == 'upload' and files:
        MediLink_ConfigLoader.log("Simulating 3 second delay for upload operation for files: {}".format(files))
        time.sleep(3)
        return [os.path.normpath(file) for file in files if os.path.exists(file)]
    elif operation_type == 'download':
        MediLink_ConfigLoader.log("Simulating 3 second delay for download operation. No files to download in test mode.")
        time.sleep(3)
        return []
    else:
        MediLink_ConfigLoader.log("Invalid operation type during simulation: {}".format(operation_type))
        return []

def execute_winscp_command(command, operation_type, files, local_storage_path):
    """
    Execute the WinSCP command for the specified operation type.
    """
    MediLink_ConfigLoader.log("Executing WinSCP command for operation type: {}".format(operation_type))
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = process.communicate()
    except Exception as e:
        MediLink_ConfigLoader.log("Error occurred while executing WinSCP command: {}".format(e), level="ERROR")
        return []  # Return an empty list instead of None

    if process.returncode == 0:
        MediLink_ConfigLoader.log("WinSCP {} operation completed successfully.".format(operation_type))

        if operation_type == 'download':
            downloaded_files = list_downloaded_files(local_storage_path) # BUG This isn't behaving correctly because the local_storage_path isn't where winscp is dumping the files
            MediLink_ConfigLoader.log("Files currently located in local_storage_path: {}".format(downloaded_files), level="DEBUG")

            if not downloaded_files:
                MediLink_ConfigLoader.log("No files were downloaded or an error occurred during the listing process.", level="WARNING")
            return downloaded_files

        elif operation_type == 'upload':
            uploaded_files = [os.path.normpath(file) for file in files if os.path.exists(file)]
            MediLink_ConfigLoader.log("Uploaded files: {}".format(uploaded_files), level="DEBUG")
            return uploaded_files
    else:
        error_message = stderr.decode('utf-8').strip()
        MediLink_ConfigLoader.log("Failed to {} files. Exit code: {}. Details: {}".format(
            operation_type, process.returncode, error_message), level="ERROR")
        return []  # Return an empty list instead of None

def list_downloaded_files(local_storage_path):

    MediLink_ConfigLoader.log("Listing downloaded files in local storage path: {}".format(local_storage_path))
    
    # Initialize an empty list to hold file paths
    downloaded_files = []

    try:
        # Walk through the directory and collect all file paths
        for root, _, files in os.walk(local_storage_path):
            for file in files:
                file_path = os.path.join(root, file)
                downloaded_files.append(file_path)
                MediLink_ConfigLoader.log("File found: {}".format(file_path), level="DEBUG")
        
        if not downloaded_files:
            MediLink_ConfigLoader.log("No files found in the directory: {}".format(local_storage_path), level="WARNING")

    except Exception as e:
        MediLink_ConfigLoader.log("Error occurred while listing files in {}: {}".format(local_storage_path, e), level="ERROR")

    # Ensure that the function always returns a list
    return downloaded_files

def detect_new_files(directory_path, file_extension='.DAT'):
    """
    Scans the specified directory for new files with a given extension and adds a timestamp if needed.
    
    :param directory_path: Path to the directory containing files to be detected.
    :param file_extension: Extension of the files to detect.
    :return: A tuple containing a list of paths to new files detected in the directory and a flag indicating if a new file was just renamed.
    """
    MediLink_ConfigLoader.log("Scanning directory: {}".format(directory_path), level="INFO")
    detected_file_paths = []
    file_flagged = False
    
    try:
        filenames = os.listdir(directory_path)
        MediLink_ConfigLoader.log("Files in directory: {}".format(filenames), level="INFO")
        
        for filename in filenames:
            MediLink_ConfigLoader.log("Checking file: {}".format(filename), level="INFO")
            if filename.endswith(file_extension):
                MediLink_ConfigLoader.log("File matches extension: {}".format(file_extension), level="INFO")
                name, ext = os.path.splitext(filename)
                MediLink_ConfigLoader.log("File name: {}, File extension: {}".format(name, ext), level="INFO")
                
                if not is_timestamped(name):
                    MediLink_ConfigLoader.log("File is not timestamped: {}".format(filename), level="INFO")
                    new_name = "{}_{}{}".format(name, datetime.now().strftime('%Y%m%d_%H%M%S'), ext)
                    os.rename(os.path.join(directory_path, filename), os.path.join(directory_path, new_name))
                    MediLink_ConfigLoader.log("Renamed file from {} to {}".format(filename, new_name), level="INFO")
                    file_flagged = True
                    filename = new_name
                else:
                    MediLink_ConfigLoader.log("File is already timestamped: {}".format(filename), level="INFO")
                
                file_path = os.path.join(directory_path, filename)
                detected_file_paths.append(file_path)
                MediLink_ConfigLoader.log("Detected file path: {}".format(file_path), level="INFO")
    
    except Exception as e:
        MediLink_ConfigLoader.log("Error occurred: {}".format(str(e)), level="INFO")
    
    MediLink_ConfigLoader.log("Detected files: {}".format(detected_file_paths), level="INFO")
    MediLink_ConfigLoader.log("File flagged status: {}".format(file_flagged), level="INFO")
    
    return detected_file_paths, file_flagged

def is_timestamped(name):
    """
    Checks if the given filename has a timestamp in the expected format.
    
    :param name: The name of the file without extension.
    :return: True if the filename includes a timestamp, False otherwise.
    """
    # Regular expression to match timestamps in the format YYYYMMDD_HHMMSS
    timestamp_pattern = re.compile(r'.*_\d{8}_\d{6}$')
    return bool(timestamp_pattern.match(name))

def organize_patient_data_by_endpoint(detailed_patient_data):
    """
    Organizes detailed patient data by their confirmed endpoints.
    This simplifies processing and conversion per endpoint basis, ensuring that claims are generated and submitted
    according to the endpoint-specific requirements.

    :param detailed_patient_data: A list of dictionaries, each containing detailed patient data including confirmed endpoint.
    :return: A dictionary with endpoints as keys and lists of detailed patient data as values for processing.
    """
    organized = {}
    for data in detailed_patient_data:
        # Retrieve confirmed endpoint from each patient's data
        endpoint = data['confirmed_endpoint'] if 'confirmed_endpoint' in data else data['suggested_endpoint']
        # Initialize a list for the endpoint if it doesn't exist
        if endpoint not in organized:
            organized[endpoint] = []
        organized[endpoint].append(data)
    return organized

def confirm_all_suggested_endpoints(detailed_patient_data):
    """
    Confirms all suggested endpoints for each patient's detailed data.
    """
    for data in detailed_patient_data:
        if 'confirmed_endpoint' not in data:
            data['confirmed_endpoint'] = data['suggested_endpoint']
    return detailed_patient_data

def bulk_edit_insurance_types(detailed_patient_data, insurance_options):
    # Allow user to edit insurance types in a table-like format with validation
    print("Edit Insurance Type (Enter the 2-character code). Enter 'LIST' to display available insurance types.")

    for data in detailed_patient_data:
        current_insurance_type = data['insurance_type']
        current_insurance_description = insurance_options.get(current_insurance_type, "Unknown")
        print("({}) {:<25} | Current Ins. Type: {} - {}".format(
            data['patient_id'], data['patient_name'], current_insurance_type, current_insurance_description))

        while True:
            new_insurance_type = input("Enter new insurance type (or press Enter to keep current): ").upper()
            if new_insurance_type == 'LIST':
                MediLink_UI.display_insurance_options(insurance_options)
            elif not new_insurance_type or new_insurance_type in insurance_options:
                if new_insurance_type:
                    data['insurance_type'] = new_insurance_type
                break
            else:
                print("Invalid insurance type. Please enter a valid 2-character code or type 'LIST' to see options.")

def review_and_confirm_changes(detailed_patient_data, insurance_options):
    # Review and confirm changes
    print("\nReview changes:")
    print("{:<20} {:<10} {:<30}".format("Patient Name", "Ins. Type", "Description"))
    print("="*65)
    for data in detailed_patient_data:
        insurance_type = data['insurance_type']
        insurance_description = insurance_options.get(insurance_type, "Unknown")
        print("{:<20} {:<10} {:<30}".format(data['patient_name'], insurance_type, insurance_description))
    confirm = input("\nConfirm changes? (y/n): ").strip().lower()
    return confirm in ['y', 'yes', '']