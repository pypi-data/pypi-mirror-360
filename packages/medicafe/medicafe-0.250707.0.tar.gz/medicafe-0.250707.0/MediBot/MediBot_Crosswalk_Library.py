import json, sys, os

# Set the project directory to the parent directory of the current file
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path: 
    sys.path.append(project_dir)

# Attempt to import the MediLink_ConfigLoader module, falling back to an alternative import if necessary
try: 
    import MediLink_ConfigLoader
except ImportError: 
    from MediLink import MediLink_ConfigLoader

# Attempt to import the fetch_payer_name_from_api function from MediLink_API_v3, with a fallback
try: 
    from MediLink_API_v3 import fetch_payer_name_from_api
except ImportError: 
    from MediLink import MediLink_API_v3
    fetch_payer_name_from_api = MediLink_API_v3.fetch_payer_name_from_api

# Attempt to import the MediBot_Preprocessor_lib module, with a fallback
try: 
    from MediBot import MediBot_Preprocessor_lib
except ImportError: 
    import MediBot_Preprocessor_lib

"""
# TODO This has a bunch of issues that need to be fixed. Notice, the log has repetitive calls to the API that are redundant.

PS G:\My Drive\Codes\MediCafe> & C:/Python34/python.exe "g:/My Drive/Codes/MediCafe/MediBot/MediBot_Preprocessor.py" --update-crosswalk
Updating the crosswalk...
The 'payer_id' list is empty or missing. Would you like to initialize the crosswalk? (yes/no): yes
No payer found at AVAILITY for ID 60054M. Response: {'limit': 50, 'offset': 0, 'totalCount': 0, 'payers': [], 'count': 0}
All endpoints exhausted for Payer ID 60054M.
WARNING: Invalid Payer ID 60054M (Unknown).
Enter the correct Payer ID for replacement or type 'FORCE' to continue with the unresolved Payer ID: 60054
csv_replacements updated: '60054M' -> '60054'.
No payer found at AVAILITY for ID MCRFL. Response: {'limit': 50, 'offset': 0, 'totalCount': 0, 'payers': [], 'count': 0}
All endpoints exhausted for Payer ID MCRFL.
No payer found at AVAILITY for ID BCSFL. Response: {'limit': 50, 'offset': 0, 'totalCount': 0, 'payers': [], 'count': 0}
All endpoints exhausted for Payer ID BCSFL.
Payer ID '60054M' has been successfully replaced with '60054'.
No payer found at AVAILITY for ID MCRFL. Response: {'limit': 50, 'offset': 0, 'totalCount': 0, 'payers': [], 'count': 0}
All endpoints exhausted for Payer ID MCRFL.
WARNING: Invalid Payer ID MCRFL (Unknown).
Enter the correct Payer ID for replacement or type 'FORCE' to continue with the unresolved Payer ID: force
Payer ID 'MCRFL' has been marked as 'Unknown'.
No payer found at AVAILITY for ID BCSFL. Response: {'limit': 50, 'offset': 0, 'totalCount': 0, 'payers': [], 'count': 0}
All endpoints exhausted for Payer ID BCSFL.
WARNING: Invalid Payer ID BCSFL (Unknown).
Enter the correct Payer ID for replacement or type 'FORCE' to continue with the unresolved Payer ID: 00590
csv_replacements updated: 'BCSFL' -> '00590'.
Payer ID 'BCSFL' has been successfully replaced with '00590'.
Crosswalk initialized with mappings for 5 payers.

"""


def fetch_and_store_payer_name(client, payer_id, crosswalk, config):
    """
    Fetches the payer name for a given payer ID and stores it in the crosswalk.
    
    Args:
        payer_id (str): The ID of the payer to fetch.
        crosswalk (dict): The crosswalk dictionary to store the payer name.
        config (dict): Configuration settings for logging.

    Returns:
        bool: True if the payer name was fetched and stored successfully, False otherwise.
    """
    MediLink_ConfigLoader.log("Attempting to fetch payer name for Payer ID: {}".format(payer_id), config, level="DEBUG")
    try:
        # Fetch the payer name from the API
        payer_name = fetch_payer_name_from_api(client, payer_id, config, primary_endpoint=None)
        MediLink_ConfigLoader.log("Fetched payer name: {} for Payer ID: {}".format(payer_name, payer_id), config, level="DEBUG")
        
        # Ensure the 'payer_id' key exists in the crosswalk
        if 'payer_id' not in crosswalk: 
            crosswalk['payer_id'] = {}
            MediLink_ConfigLoader.log("Initialized 'payer_id' in crosswalk.", config, level="DEBUG")
        
        # Initialize the payer ID entry if it doesn't exist
        if payer_id not in crosswalk['payer_id']:
            crosswalk['payer_id'][payer_id] = {}  # Initialize the entry
            MediLink_ConfigLoader.log("Initialized entry for Payer ID: {}".format(payer_id), config, level="DEBUG")
        
        # Store the fetched payer name in the crosswalk
        crosswalk['payer_id'][payer_id]['name'] = payer_name
        message = "Payer ID {} ({}) fetched and stored successfully.".format(payer_id, payer_name)
        MediLink_ConfigLoader.log(message, config, level="INFO")
        print(message)
        return True
    except Exception as e:
        # Log any errors encountered during the fetching process
        MediLink_ConfigLoader.log("Failed to fetch name for Payer ID {}: {}".format(payer_id, e), config, level="WARNING")
        crosswalk['payer_id'][payer_id]['name'] = "Unknown"
        return False

def validate_and_correct_payer_ids(client, crosswalk, config, auto_correct=False):
    """
    Validates and corrects payer IDs in the crosswalk. If a payer ID is invalid, it prompts the user for correction.
    
    Args:
        crosswalk (dict): The crosswalk dictionary containing payer IDs.
        config (dict): Configuration settings for logging.
        auto_correct (bool): If True, automatically corrects invalid payer IDs to 'Unknown'.
    """
    processed_payer_ids = set()  # Track processed payer IDs
    payer_ids = list(crosswalk.get('payer_id', {}).keys())  # Static list to prevent modification issues
    
    for payer_id in payer_ids:
        if payer_id in processed_payer_ids:
            continue  # Skip already processed payer IDs
        
        # Validate the payer ID by fetching its name
        is_valid = fetch_and_store_payer_name(client, payer_id, crosswalk, config)
        
        if not is_valid:
            if auto_correct:
                # Automatically correct invalid payer IDs to 'Unknown'
                crosswalk['payer_id'][payer_id]['name'] = "Unknown"
                MediLink_ConfigLoader.log(
                    "Auto-corrected Payer ID {} to 'Unknown'.".format(payer_id),
                    config,
                    level="WARNING"
                )
                print("Auto-corrected Payer ID '{}' to 'Unknown'.".format(payer_id))
                processed_payer_ids.add(payer_id)
                continue
            
            # Prompt the user for a corrected payer ID
            current_name = crosswalk['payer_id'].get(payer_id, {}).get('name', 'Unknown')
            corrected_payer_id = input(
                "WARNING: Invalid Payer ID {} ({}).\n"
                "Enter the correct Payer ID for replacement or type 'FORCE' to continue with the unresolved Payer ID: ".format(
                    payer_id, current_name)
            ).strip()
            
            if corrected_payer_id.lower() == 'force':
                # Assign "Unknown" and log the action
                crosswalk['payer_id'][payer_id]['name'] = "Unknown"
                MediLink_ConfigLoader.log(
                    "User forced unresolved Payer ID {} to remain as 'Unknown'.".format(payer_id),
                    config,
                    level="WARNING"
                )
                print("Payer ID '{}' has been marked as 'Unknown'.".format(payer_id))
                processed_payer_ids.add(payer_id)
                continue
            
            if corrected_payer_id:
                # Validate the corrected payer ID
                if fetch_and_store_payer_name(client, corrected_payer_id, crosswalk, config):
                    # Replace the old payer ID with the corrected one in the crosswalk
                    success = update_crosswalk_with_corrected_payer_id(client, payer_id, corrected_payer_id, config, crosswalk)
                    if success:
                        print("Payer ID '{}' has been successfully replaced with '{}'.".format(
                            payer_id, corrected_payer_id))
                        processed_payer_ids.add(corrected_payer_id)
                else:
                    # Only set to "Unknown" if the corrected payer ID is not valid
                    crosswalk['payer_id'][corrected_payer_id] = {'name': "Unknown"}
                    MediLink_ConfigLoader.log(
                        "Failed to validate corrected Payer ID {}. Set to 'Unknown'.".format(corrected_payer_id),
                        config,
                        level="ERROR"
                    )
                    print("Payer ID '{}' has been added with name 'Unknown'.".format(corrected_payer_id))
                    processed_payer_ids.add(corrected_payer_id)
            else:
                MediLink_ConfigLoader.log(
                    "No correction provided for Payer ID {}. Skipping.".format(payer_id),
                    config,
                    level="WARNING"
                )
                print("No correction provided for Payer ID '{}'. Skipping.".format(payer_id))

def initialize_crosswalk_from_mapat(client, config, crosswalk):
    """
    Initializes the crosswalk from the MAPAT data source. Loads configuration and data sources, 
    validates payer IDs, and saves the crosswalk.
    
    Returns:
        dict: The payer ID mappings from the initialized crosswalk.
    """
    # Ensure full configuration and crosswalk are loaded
    config, crosswalk = ensure_full_config_loaded(config, crosswalk)
    
    try:
        # Load data sources for patient and payer IDs
        patient_id_to_insurance_id, payer_id_to_patient_ids = MediBot_Preprocessor_lib.load_data_sources(config, crosswalk)
    except ValueError as e:
        print(e)
        sys.exit(1)
    
    # Map payer IDs to insurance IDs
    payer_id_to_details = MediBot_Preprocessor_lib.map_payer_ids_to_insurance_ids(patient_id_to_insurance_id, payer_id_to_patient_ids)
    crosswalk['payer_id'] = payer_id_to_details
    
    # Validate and correct payer IDs in the crosswalk
    validate_and_correct_payer_ids(client, crosswalk, config)
    
    # Save the crosswalk and log the result
    if save_crosswalk(client, config, crosswalk):
        message = "Crosswalk initialized with mappings for {} payers.".format(len(crosswalk.get('payer_id', {})))
        print(message)
        MediLink_ConfigLoader.log(message, config, level="INFO")
    else:
        print("Failed to save the crosswalk.")
        sys.exit(1)
    
    return crosswalk['payer_id']

def load_and_parse_z_data(config):
    """
    Loads and parses Z data for patient to insurance name mappings from the specified directory.
    
    Args:
        config (dict): Configuration settings for logging.
    
    Returns:
        dict: A mapping of patient IDs to insurance names.
    """
    patient_id_to_insurance_name = {}
    try:
        z_dat_path = config['MediLink_Config']['Z_DAT_PATH']
        MediLink_ConfigLoader.log("Z_DAT_PATH is set to: {}".format(z_dat_path), config, level="DEBUG")
        
        # Get the directory of the Z_DAT_PATH
        directory = os.path.dirname(z_dat_path)
        MediLink_ConfigLoader.log("Looking for .DAT files in directory: {}".format(directory), config, level="DEBUG")
        
        # List all .DAT files in the directory, case insensitive
        dat_files = [f for f in os.listdir(directory) if f.lower().endswith('.dat')]
        MediLink_ConfigLoader.log("Found {} .DAT files in the directory.".format(len(dat_files)), config, level="DEBUG")
        
        # Load processed files tracking
        processed_files_path = os.path.join(directory, 'processed_files.txt')
        if os.path.exists(processed_files_path):
            with open(processed_files_path, 'r') as f:
                processed_files = set(line.strip() for line in f)
            MediLink_ConfigLoader.log("Loaded processed files: {}.".format(processed_files), config, level="DEBUG")
        else:
            processed_files = set()
            MediLink_ConfigLoader.log("No processed files found, starting fresh.", config, level="DEBUG")

        # Filter for new .DAT files that haven't been processed yet, but always include Z.DAT and ZM.DAT
        new_dat_files = [f for f in dat_files if f not in processed_files or f.lower() in ['z.dat', 'zm.dat']]
        MediLink_ConfigLoader.log("Identified {} new .DAT files to process.".format(len(new_dat_files)), config, level="INFO")

        for dat_file in new_dat_files:
            file_path = os.path.join(directory, dat_file)
            MediLink_ConfigLoader.log("Parsing .DAT file: {}".format(file_path), config, level="DEBUG")
            # Parse each .DAT file and accumulate results
            insurance_name_mapping = MediBot_Preprocessor_lib.parse_z_dat(file_path, config['MediLink_Config'])
            if insurance_name_mapping:  # Ensure insurance_name_mapping is not empty
                patient_id_to_insurance_name.update(insurance_name_mapping)

            # Mark this file as processed
            with open(processed_files_path, 'a') as f:
                f.write(dat_file + '\n')
            MediLink_ConfigLoader.log("Marked file as processed: {}".format(dat_file), config, level="DEBUG")

        if not patient_id_to_insurance_name:  # Check if the result is empty
            raise ValueError("Parsed Z data is empty, possibly indicating an error in parsing or all files already processed.") # TODO Add differentiator here because this is dumb.
        MediLink_ConfigLoader.log("Successfully parsed Z data with {} mappings found.".format(len(patient_id_to_insurance_name)), config, level="INFO")
        return patient_id_to_insurance_name  # Ensure the function returns the mapping
    except Exception as e:
        MediLink_ConfigLoader.log("Error loading and parsing Z data: {}".format(e), config, level="ERROR")
        return {}

def crosswalk_update(client, config, crosswalk, skip_known_payers=True): # Upstream of this is only MediBot_Preprocessor.py and MediBot.py
    """
    Updates the crosswalk with insurance data and historical mappings. 
    It loads insurance data, historical payer mappings, and updates the crosswalk accordingly.
    
    Args:
        config (dict): Configuration settings for logging.
        crosswalk (dict): The crosswalk dictionary to update.
        skip_known_payers (bool): If True, skips records with 'name' not equal to 'Unknown'.
    
    Returns:
        bool: True if the crosswalk was updated successfully, False otherwise.
    """
    MediLink_ConfigLoader.log("Starting crosswalk update process...", config, level="INFO")

    # Load insurance data from MAINS
    try:
        MediLink_ConfigLoader.log("Attempting to load insurance data from MAINS...", config, level="DEBUG")
        insurance_name_to_id = MediBot_Preprocessor_lib.load_insurance_data_from_mains(config)
        MediLink_ConfigLoader.log("Loaded insurance data from MAINS with {} entries.".format(len(insurance_name_to_id)), config, level="INFO")
    except Exception as e:
        MediLink_ConfigLoader.log("Error loading insurance data from MAINS: {}".format(e), config, level="ERROR")
        return False

    # Load historical payer to patient mappings
    try:
        MediLink_ConfigLoader.log("Attempting to load historical payer to patient mappings...", config, level="DEBUG")
        patient_id_to_payer_id = MediBot_Preprocessor_lib.load_historical_payer_to_patient_mappings(config)
        MediLink_ConfigLoader.log("Loaded historical mappings with {} entries.".format(len(patient_id_to_payer_id)), config, level="INFO")
    except Exception as e:
        MediLink_ConfigLoader.log("Error loading historical mappings: {}".format(e), config, level="ERROR")
        return False

    # Parse Z data for patient to insurance name mappings
    try:
        patient_id_to_insurance_name = load_and_parse_z_data(config)
        mapping_count = len(patient_id_to_insurance_name) if patient_id_to_insurance_name is not None else 0
        MediLink_ConfigLoader.log("Parsed Z data with {} mappings found.".format(mapping_count), config, level="INFO")
    except Exception as e:
        MediLink_ConfigLoader.log("Error parsing Z data in crosswalk update: {}".format(e), config, level="ERROR")
        return False

    # Check if 'payer_id' key exists and is not empty
    MediLink_ConfigLoader.log("Checking for 'payer_id' key in crosswalk...", config, level="DEBUG")
    if 'payer_id' not in crosswalk or not crosswalk['payer_id']:
        MediLink_ConfigLoader.log("The 'payer_id' list is empty or missing.", config, level="WARNING")
        user_input = input(
            "The 'payer_id' list is empty or missing. Would you like to initialize the crosswalk? (yes/no): "
        ).strip().lower()
        if user_input in ['yes', 'y']:
            MediLink_ConfigLoader.log("User chose to initialize the crosswalk.", config, level="INFO")
            initialize_crosswalk_from_mapat(client, config, crosswalk)
            return True  # Indicate that the crosswalk was initialized
        else:
            MediLink_ConfigLoader.log("User opted not to initialize the crosswalk.", config, level="WARNING")
            return False  # Indicate that the update was not completed

    # Update the crosswalk with new payer IDs and insurance IDs
    for patient_id, payer_id in patient_id_to_payer_id.items():
        """ TODO this needs to be implemented at some point so we can skip known entities.
        # Skip known payers if the flag is set
        if skip_known_payers:
            payer_id_str = next(iter(payer_id))  # Extract the single payer_id from the set
            MediLink_ConfigLoader.log("Checking if payer_id '{}' is known...".format(payer_id_str), config, level="DEBUG")
            payer_info = crosswalk['payer_id'].get(payer_id_str, {})
            payer_name = payer_info.get('name', "Unknown")
            MediLink_ConfigLoader.log("Retrieved payer name: '{}' for payer_id '{}'.".format(payer_name, payer_id), config, level="DEBUG")
            
            if payer_name != "Unknown":
                MediLink_ConfigLoader.log("Skipping known payer_id: '{}' as it is already in the crosswalk.".format(payer_id), config, level="DEBUG")
                continue  # Skip this payer_id
            MediLink_ConfigLoader.log("Skipping known payer_id: {} as it is already in the crosswalk.".format(payer_id), config, level="DEBUG")
            continue  # Skip this payer_id
        """
   
        insurance_name = patient_id_to_insurance_name.get(patient_id)
        if insurance_name and insurance_name in insurance_name_to_id:
            insurance_id = insurance_name_to_id[insurance_name]
           
            # Log the assembly of data
            MediLink_ConfigLoader.log("Assembling data for patient_id '{}': payer_id '{}', insurance_name '{}', insurance_id '{}'.".format(
                patient_id, payer_id, insurance_name, insurance_id), config, level="INFO")
            # Ensure the 'payer_id' key exists in the crosswalk
            if 'payer_id' not in crosswalk:
                crosswalk['payer_id'] = {}
                MediLink_ConfigLoader.log("Initialized 'payer_id' in crosswalk.", config, level="DEBUG")

            # Initialize the payer ID entry if it doesn't exist
            if payer_id not in crosswalk['payer_id']:
                # Prompt the user to select an endpoint name or use the default
                endpoint_options = list(config['MediLink_Config']['endpoints'].keys())
                print("Available endpoints:")
                for idx, key in enumerate(endpoint_options):
                    print("{0}: {1}".format(idx + 1, config['MediLink_Config']['endpoints'][key]['name']))
                user_choice = input("Select an endpoint by number (or press Enter to use the default): ").strip()

                if user_choice.isdigit() and 1 <= int(user_choice) <= len(endpoint_options):
                    selected_endpoint = config['MediLink_Config']['endpoints'][endpoint_options[int(user_choice) - 1]]['name']
                else:
                    selected_endpoint = config['MediLink_Config']['endpoints'][endpoint_options[0]]['name']
                    MediLink_ConfigLoader.log("User opted for default endpoint: {}".format(selected_endpoint), config, level="INFO")

                crosswalk['payer_id'][payer_id] = {
                    'endpoint': selected_endpoint,
                    'medisoft_id': set(),  # Use set to store multiple IDs
                    'medisoft_medicare_id': set()
                }
                MediLink_ConfigLoader.log("Initialized payer ID {} in crosswalk with endpoint '{}'.".format(payer_id, selected_endpoint), config, level="DEBUG")

            # Add the insurance ID to the payer ID entry
            crosswalk['payer_id'][payer_id]['medisoft_id'].add(str(insurance_id))  # Ensure IDs are strings
            MediLink_ConfigLoader.log(
                "Added new insurance ID {} to payer ID {}.".format(insurance_id, payer_id),
                config,
                level="INFO"
            )

            # Log the update of the crosswalk
            MediLink_ConfigLoader.log("Updated crosswalk for payer_id '{}': added insurance_id '{}'.".format(payer_id, insurance_id), config, level="DEBUG")

            # Fetch and store the payer name
            MediLink_ConfigLoader.log("Fetching and storing payer name for payer_id: {}".format(payer_id), config, level="DEBUG")
            fetch_and_store_payer_name(client, payer_id, crosswalk, config)
            MediLink_ConfigLoader.log("Successfully fetched and stored payer name for payer_id: {}".format(payer_id), config, level="INFO")

    # Validate and correct payer IDs in the crosswalk
    MediLink_ConfigLoader.log("Validating and correcting payer IDs in the crosswalk.", config, level="DEBUG")
    validate_and_correct_payer_ids(client, crosswalk, config)

    # Check for any entries marked as "Unknown" and validate them
    unknown_payers = [
        payer_id for payer_id, details in crosswalk.get('payer_id', {}).items()
        if details.get('name') == "Unknown"
    ]
    MediLink_ConfigLoader.log("Found {} unknown payer(s) to validate.".format(len(unknown_payers)), config, level="INFO")
    for payer_id in unknown_payers:
        MediLink_ConfigLoader.log("Fetching and storing payer name for unknown payer_id: {}".format(payer_id), config, level="DEBUG")
        fetch_and_store_payer_name(client, payer_id, crosswalk, config)
        MediLink_ConfigLoader.log("Successfully fetched and stored payer name for unknown payer_id: {}".format(payer_id), config, level="INFO")

    # Ensure multiple medisoft_id values are preserved by converting sets to sorted lists
    for payer_id, details in crosswalk.get('payer_id', {}).items():
        if isinstance(details.get('medisoft_id'), set):
            crosswalk['payer_id'][payer_id]['medisoft_id'] = sorted(list(details['medisoft_id']))
            MediLink_ConfigLoader.log("Converted medisoft_id for payer ID {} to sorted list.".format(payer_id), config, level="DEBUG")
        if isinstance(details.get('medisoft_medicare_id'), set):
            crosswalk['payer_id'][payer_id]['medisoft_medicare_id'] = sorted(list(details['medisoft_medicare_id']))
            MediLink_ConfigLoader.log("Converted medisoft_medicare_id for payer ID {} to sorted list.".format(payer_id), config, level="DEBUG")

    MediLink_ConfigLoader.log("Crosswalk update process completed. Processed {} payer IDs.".format(len(patient_id_to_payer_id)), config, level="INFO")
    return save_crosswalk(client, config, crosswalk)

def update_crosswalk_with_corrected_payer_id(client, old_payer_id, corrected_payer_id, config=None, crosswalk=None): 
    """
    Updates the crosswalk by replacing an old payer ID with a corrected payer ID.
    
    Args:
        old_payer_id (str): The old payer ID to be replaced.
        corrected_payer_id (str): The new payer ID to replace the old one.
        config (dict, optional): Configuration settings for logging.
        crosswalk (dict, optional): The crosswalk dictionary to update.
    
    Returns:
        bool: True if the crosswalk was updated successfully, False otherwise.
    """
    # Ensure full configuration and crosswalk are loaded
    config, crosswalk = ensure_full_config_loaded(config, crosswalk)
        
    # Convert to a regular dict if crosswalk['payer_id'] is an OrderedDict
    if isinstance(crosswalk['payer_id'], dict) and hasattr(crosswalk['payer_id'], 'items'):
        crosswalk['payer_id'] = dict(crosswalk['payer_id'])
    
    MediLink_ConfigLoader.log("Checking if old Payer ID {} exists in crosswalk.".format(old_payer_id), config, level="DEBUG")
    
    MediLink_ConfigLoader.log("Attempting to replace old Payer ID {} with corrected Payer ID {}.".format(old_payer_id, corrected_payer_id), config, level="DEBUG")
        
    # Check if the old payer ID exists before attempting to replace
    if old_payer_id in crosswalk['payer_id']:
        MediLink_ConfigLoader.log("Old Payer ID {} found. Proceeding with replacement.".format(old_payer_id), config, level="DEBUG")
            
        # Store the details of the old payer ID
        old_payer_details = crosswalk['payer_id'][old_payer_id]
        MediLink_ConfigLoader.log("Storing details of old Payer ID {}: {}".format(old_payer_id, old_payer_details), config, level="DEBUG")
        
        # Replace the old payer ID with the corrected one
        crosswalk['payer_id'][corrected_payer_id] = old_payer_details
        MediLink_ConfigLoader.log("Replaced old Payer ID {} with corrected Payer ID {}.".format(old_payer_id, corrected_payer_id), config, level="INFO")
        
        # Remove the old payer ID from the crosswalk
        del crosswalk['payer_id'][old_payer_id]
        MediLink_ConfigLoader.log("Removed old Payer ID {} from crosswalk.".format(old_payer_id), config, level="DEBUG")
    
        # Fetch and store the payer name for the corrected ID
        if fetch_and_store_payer_name(client, corrected_payer_id, crosswalk, config):
            MediLink_ConfigLoader.log("Successfully fetched and stored payer name for corrected Payer ID {}.".format(corrected_payer_id), config, level="INFO")
        else:
            MediLink_ConfigLoader.log("Corrected Payer ID {} updated without a valid name.".format(corrected_payer_id), config, level="WARNING")
        
        # Update csv_replacements
        crosswalk.setdefault('csv_replacements', {})[old_payer_id] = corrected_payer_id
        MediLink_ConfigLoader.log("Updated csv_replacements: {} -> {}.".format(old_payer_id, corrected_payer_id), config, level="INFO")
        print("csv_replacements updated: '{}' -> '{}'.".format(old_payer_id, corrected_payer_id))
        
        return save_crosswalk(client, config, crosswalk)
    else:
        MediLink_ConfigLoader.log("Failed to update crosswalk: old Payer ID {} not found.".format(old_payer_id), config, level="ERROR")
        print("Failed to update crosswalk: could not find old Payer ID '{}'.".format(old_payer_id))
        return False

def update_crosswalk_with_new_payer_id(client, insurance_name, payer_id, config, crosswalk): 
    """
    Updates the crosswalk with a new payer ID for a given insurance name.
    
    Args:
        insurance_name (str): The name of the insurance to associate with the new payer ID.
        payer_id (str): The new payer ID to be added.
        config (dict): Configuration settings for logging.
    """
    # Ensure full configuration and crosswalk are loaded
    config, crosswalk = ensure_full_config_loaded(config, crosswalk)
    
    try:
        # Check if 'payer_id' is present in the crosswalk
        if 'payer_id' not in crosswalk or not crosswalk['payer_id']:
            # Reload the crosswalk if 'payer_id' is missing or empty
            _, crosswalk = MediLink_ConfigLoader.load_configuration(None, config.get('crosswalkPath', 'crosswalk.json'))
            MediLink_ConfigLoader.log("Reloaded crosswalk configuration from {}.".format(config.get('crosswalkPath', 'crosswalk.json')), config, level="DEBUG")
    except KeyError as e:  # Handle KeyError for crosswalk
        MediLink_ConfigLoader.log("KeyError while checking or reloading crosswalk: {}".format(e), config, level="ERROR")
        print("KeyError while checking or reloading crosswalk in update_crosswalk_with_new_payer_id: {}".format(e))
        return False
    except Exception as e:
        MediLink_ConfigLoader.log("Error while checking or reloading crosswalk: {}".format(e), config, level="ERROR")
        print("Error while checking or reloading crosswalk in update_crosswalk_with_new_payer_id: {}".format(e))
        return False
    
    # Load the Medisoft ID for the given insurance name
    try:
        medisoft_id = MediBot_Preprocessor_lib.load_insurance_data_from_mains(config).get(insurance_name)
    except KeyError as e:  # Handle KeyError for config
        MediLink_ConfigLoader.log("KeyError while loading Medisoft ID: {}".format(e), config, level="ERROR")
        print("KeyError while loading Medisoft ID for insurance name {}: {}".format(insurance_name, e))
        return False

    MediLink_ConfigLoader.log("Retrieved Medisoft ID for insurance name {}: {}.".format(insurance_name, medisoft_id), config, level="DEBUG")
    # print("DEBUG: Retrieved Medisoft ID for insurance name {}: {}.".format(insurance_name, medisoft_id))
    
    if medisoft_id:
        medisoft_id_str = str(medisoft_id)
        MediLink_ConfigLoader.log("Processing to update crosswalk with new payer ID: {} for insurance name: {}.".format(payer_id, insurance_name), config, level="DEBUG")
        
        # Initialize the payer ID entry if it doesn't exist
        if payer_id not in crosswalk['payer_id']:
            selected_endpoint = select_endpoint(config)  # Use the helper function to select the endpoint

            # Ensure the 'payer_id' key exists in the crosswalk
            crosswalk['payer_id'][payer_id] = {
                'endpoint': selected_endpoint,
                'medisoft_id': set(),
                'medisoft_medicare_id': []
            }
            MediLink_ConfigLoader.log("Initialized payer ID {} in crosswalk with endpoint '{}'.".format(payer_id, selected_endpoint), config, level="DEBUG")
        else:
            # Check if the existing endpoint is valid
            current_endpoint = crosswalk['payer_id'][payer_id].get('endpoint', None)
            if current_endpoint and current_endpoint not in config['MediLink_Config']['endpoints']:
                print("WARNING: The current endpoint '{}' for payer ID '{}' is not valid.".format(current_endpoint, payer_id))
                MediLink_ConfigLoader.log("Current endpoint '{}' for payer ID '{}' is not valid. Prompting for selection.".format(current_endpoint, payer_id), config, level="WARNING")
                selected_endpoint = select_endpoint(config, current_endpoint)  # Prompt user to select a valid endpoint
                crosswalk['payer_id'][payer_id]['endpoint'] = selected_endpoint  # Update the endpoint in the crosswalk
                MediLink_ConfigLoader.log("Updated payer ID {} with new endpoint '{}'.".format(payer_id, selected_endpoint), config, level="INFO")
            else:
                selected_endpoint = current_endpoint  # Use the existing valid endpoint

        # Add the insurance ID to the payer ID entry - with error handling for the .add() operation
        try:
            if not isinstance(crosswalk['payer_id'][payer_id]['medisoft_id'], set):
                # Convert to set if it's not already one
                crosswalk['payer_id'][payer_id]['medisoft_id'] = set(crosswalk['payer_id'][payer_id]['medisoft_id'])
                MediLink_ConfigLoader.log("Converted medisoft_id to set for payer ID {}.".format(payer_id), config, level="DEBUG")
            
            crosswalk['payer_id'][payer_id]['medisoft_id'].add(str(medisoft_id_str)) # Ensure IDs are strings
            MediLink_ConfigLoader.log(
                "Added new insurance ID {} to payer ID {}.".format(medisoft_id_str, payer_id),
                config,
                level="INFO"
            )
        except AttributeError as e:
            MediLink_ConfigLoader.log("AttributeError while adding medisoft_id: {}".format(e), config, level="ERROR")
            print("Error adding medisoft_id for payer ID {}: {}".format(payer_id, e))
            return False
        
        # Fetch and store the payer name for the new payer ID
        if fetch_and_store_payer_name(client, payer_id, crosswalk, config):
            MediLink_ConfigLoader.log("Successfully fetched and stored payer name for new payer ID {}.".format(payer_id), config, level="INFO")
            MediLink_ConfigLoader.log("Updated crosswalk with new payer ID {} for insurance name {}.".format(payer_id, insurance_name), config, level="INFO")
        else:
            MediLink_ConfigLoader.log("Added new payer ID {} without a valid name for insurance name {}.".format(payer_id, insurance_name), config, level="WARNING")
        
        # Save the updated crosswalk
        save_crosswalk(client, config, crosswalk)
        MediLink_ConfigLoader.log("Crosswalk saved successfully after updating payer ID {}.".format(payer_id), config, level="DEBUG")
    else:
        message = "Failed to update crosswalk: Medisoft ID not found for insurance name {}.".format(insurance_name)
        print(message)
        MediLink_ConfigLoader.log(message, config, level="ERROR")

def save_crosswalk(client, config, crosswalk):
    """
    Saves the crosswalk to a JSON file. Ensures that all necessary keys are present and logs the outcome.
    
    Args:
        config (dict): Configuration settings for logging.
        crosswalk (dict): The crosswalk dictionary to save.
    
    Returns:
        bool: True if the crosswalk was saved successfully, False otherwise.
    """
    try:
        # Determine the path to save the crosswalk
        crosswalk_path = config['MediLink_Config']['crosswalkPath']
        MediLink_ConfigLoader.log("Determined crosswalk path: {}.".format(crosswalk_path), config, level="DEBUG")
    except KeyError:
        crosswalk_path = config.get('crosswalkPath', 'crosswalk.json')
        MediLink_ConfigLoader.log("Using default crosswalk path: {}.".format(crosswalk_path), config, level="DEBUG")
    
    # Validate endpoints for each payer ID in the crosswalk
    for payer_id, details in crosswalk.get('payer_id', {}).items():
        current_endpoint = details.get('endpoint', None)
        if current_endpoint and current_endpoint not in config['MediLink_Config']['endpoints']:
            print("WARNING: The current endpoint '{}' for payer ID '{}' is not valid.".format(current_endpoint, payer_id))
            MediLink_ConfigLoader.log("Current endpoint '{}' for payer ID '{}' is not valid. Prompting for selection.".format(current_endpoint, payer_id), config, level="WARNING")
            selected_endpoint = select_endpoint(config, current_endpoint)  # Prompt user to select a valid endpoint
            crosswalk['payer_id'][payer_id]['endpoint'] = selected_endpoint  # Update the endpoint in the crosswalk
            MediLink_ConfigLoader.log("Updated payer ID {} with new endpoint '{}'.".format(payer_id, selected_endpoint), config, level="INFO")
    
    try:
        # Initialize the 'payer_id' key if it doesn't exist
        if 'payer_id' not in crosswalk: 
            print("save_crosswalk is initializing 'payer_id' key...")
            crosswalk['payer_id'] = {}
            MediLink_ConfigLoader.log("Initialized 'payer_id' key in crosswalk.", config, level="INFO")
        
        # Ensure all payer IDs have a name and initialize medisoft_id and medisoft_medicare_id as empty lists if they do not exist
        for payer_id in crosswalk['payer_id']:
            if 'name' not in crosswalk['payer_id'][payer_id]: 
                fetch_and_store_payer_name(client, payer_id, crosswalk, config)
                MediLink_ConfigLoader.log("Fetched and stored payer name for payer ID: {}.".format(payer_id), config, level="DEBUG")
            
            # Check for the endpoint key
            if 'endpoint' not in crosswalk['payer_id'][payer_id]:
                crosswalk['payer_id'][payer_id]['endpoint'] = select_endpoint(config)  # Use the helper function to set the endpoint
                MediLink_ConfigLoader.log("Initialized 'endpoint' for payer ID {}.".format(payer_id), config, level="DEBUG")

            # Initialize medisoft_id and medisoft_medicare_id as empty lists if they do not exist
            crosswalk['payer_id'][payer_id].setdefault('medisoft_id', [])
            crosswalk['payer_id'][payer_id].setdefault('medisoft_medicare_id', []) # does this work in 3.4.4?
            MediLink_ConfigLoader.log("Ensured 'medisoft_id' and 'medisoft_medicare_id' for payer ID {} are initialized.".format(payer_id), config, level="DEBUG")
        
        # Convert sets to sorted lists for JSON serialization
        for payer_id, details in crosswalk.get('payer_id', {}).items():
            if isinstance(details.get('medisoft_id'), set): 
                crosswalk['payer_id'][payer_id]['medisoft_id'] = sorted(list(details['medisoft_id']))
                MediLink_ConfigLoader.log("Converted medisoft_id for payer ID {} to sorted list.".format(payer_id), config, level="DEBUG")
            if isinstance(details.get('medisoft_medicare_id'), set): 
                crosswalk['payer_id'][payer_id]['medisoft_medicare_id'] = sorted(list(details['medisoft_medicare_id']))
                MediLink_ConfigLoader.log("Converted medisoft_medicare_id for payer ID {} to sorted list.".format(payer_id), config, level="DEBUG")
        
        # Write the crosswalk to the specified file
        with open(crosswalk_path, 'w') as file:
            json.dump(crosswalk, file, indent=4)
        
        MediLink_ConfigLoader.log(
            "Crosswalk saved successfully to {}.".format(crosswalk_path),
            config,
            level="INFO"
        )
        print("Crosswalk saved successfully to {}.".format(crosswalk_path))
        return True
    except KeyError as e:
        print("Key Error: A required key is missing in the crosswalk data - {}.".format(e))
        MediLink_ConfigLoader.log("Key Error while saving crosswalk: {}.".format(e), config, level="ERROR")
        return False
    except TypeError as e:
        print("Type Error: There was a type issue with the data being saved in the crosswalk - {}.".format(e))
        MediLink_ConfigLoader.log("Type Error while saving crosswalk: {}.".format(e), config, level="ERROR")
        return False
    except IOError as e:
        print("I/O Error: An error occurred while writing to the crosswalk file - {}.".format(e))
        MediLink_ConfigLoader.log("I/O Error while saving crosswalk: {}.".format(e), config, level="ERROR")
        return False
    except Exception as e:
        print("Unexpected crosswalk error: {}.".format(e))
        MediLink_ConfigLoader.log("Unexpected error while saving crosswalk: {}.".format(e), config, level="ERROR")
        return False

def select_endpoint(config, current_endpoint=None):
    # BUG Check upstream for the config. One of these is not being passed correctly so we're having to do this check here.
    """
    Prompts the user to select an endpoint from the available options or returns the default endpoint.
    Validates the current endpoint against the available options.

    Args:
        config (dict): Configuration settings for logging. Can be either the full config or config['MediLink_Config'].
        current_endpoint (str, optional): The current endpoint to validate.

    Returns:
        str: The selected endpoint key.

    Raises:
        ValueError: If the config does not contain valid endpoint information.
    """
    # Determine the effective MediLink_Config
    if 'MediLink_Config' in config:
        medi_link_config = config['MediLink_Config']
        MediLink_ConfigLoader.log("Using 'MediLink_Config' from the provided configuration.", config, level="DEBUG")
    else:
        medi_link_config = config
        MediLink_ConfigLoader.log("Using the provided configuration directly as 'MediLink_Config'.", config, level="DEBUG")

    # Attempt to retrieve endpoint options
    try:
        endpoint_options = list(medi_link_config['endpoints'].keys())
        MediLink_ConfigLoader.log("Successfully retrieved endpoint options.", config, level="DEBUG")
    except KeyError:
        MediLink_ConfigLoader.log("Failed to retrieve endpoint options due to KeyError.", config, level="ERROR")
        raise ValueError("Invalid configuration: 'endpoints' not found in config.")
        

    # Ensure there are available endpoints
    if not endpoint_options:
        MediLink_ConfigLoader.log("No endpoints available in the configuration.", config, level="ERROR")
        raise ValueError("No endpoints available in the configuration.")
    else:
        MediLink_ConfigLoader.log("Available endpoints found in the configuration.", config, level="DEBUG")

    print("Available endpoints:")
    for idx, key in enumerate(endpoint_options):
        # Safely retrieve the endpoint name
        endpoint_name = medi_link_config['endpoints'].get(key, {}).get('name', key)
        print("{0}: {1}".format(idx + 1, endpoint_name))

    # Validate the current endpoint if provided
    if current_endpoint and current_endpoint not in endpoint_options:
        print("WARNING: The current endpoint '{}' is not valid.".format(current_endpoint))
        MediLink_ConfigLoader.log("Current endpoint '{}' is not valid. Prompting for selection.".format(current_endpoint), config, level="WARNING")

    user_choice = input("Select an endpoint by number (or press Enter to use the default): ").strip()

    if user_choice.isdigit() and 1 <= int(user_choice) <= len(endpoint_options):
        selected_endpoint = endpoint_options[int(user_choice) - 1]  # Use the key instead of the name
    else:
        selected_endpoint = endpoint_options[0]  # Default to the first key
        MediLink_ConfigLoader.log("User opted for default endpoint: " + selected_endpoint, config, level="INFO")

    return selected_endpoint

def ensure_full_config_loaded(config=None, crosswalk=None):
    """
    Ensures that the full base configuration and crosswalk are loaded.
    If the base config is not valid or the crosswalk is None, reloads them.

    Args:
        config (dict, optional): The current configuration.
        crosswalk (dict, optional): The current crosswalk.

    Returns:
        tuple: The loaded base configuration and crosswalk.
    """
    MediLink_ConfigLoader.log("Ensuring full configuration and crosswalk are loaded.", level="DEBUG")

    # Reload configuration if necessary
    if config is None or 'MediLink_Config' not in config:
        MediLink_ConfigLoader.log("Base config is missing or invalid. Reloading configuration.", level="WARNING")
        config, crosswalk = MediLink_ConfigLoader.load_configuration()
        MediLink_ConfigLoader.log("Base configuration and crosswalk reloaded.", level="INFO")
    else:
        MediLink_ConfigLoader.log("Base config was correctly passed.", level="DEBUG")

    # Reload crosswalk if necessary
    if crosswalk is None:
        MediLink_ConfigLoader.log("Crosswalk is None. Reloading crosswalk.", level="WARNING")
        _, crosswalk = MediLink_ConfigLoader.load_configuration()  # Reloading to get the crosswalk
        MediLink_ConfigLoader.log("Crosswalk reloaded.", level="INFO")

    return config, crosswalk