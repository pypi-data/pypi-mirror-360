#MediBot.py
import subprocess, os, tempfile, traceback, re, sys
from collections import OrderedDict
import MediBot_dataformat_library
import MediBot_Preprocessor
from MediBot_Preprocessor_lib import initialize, AHK_EXECUTABLE, CSV_FILE_PATH, field_mapping, load_csv_data
from MediBot_UI import app_control, manage_script_pause, user_interaction

# Add parent directory of the project to the Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

from MediLink import MediLink_ConfigLoader

try:
    from MediBot_Crosswalk_Library import crosswalk_update
except ImportError:
    from MediBot import MediBot_Crosswalk_Library
    crosswalk_update = MediBot_Crosswalk_Library.crosswalk_update

try:
    from MediLink.MediLink_API_v3 import APIClient
except ImportError as e:
    raise ImportError("Failed to import APIClient from MediLink.MediLink_API_v3. "
                        "Ensure the MediLink_API_v3 module is installed and accessible.") from e
    
# After successful import
try:
    api_client = APIClient()  # Pass necessary arguments if required
except Exception as e:
    raise RuntimeError("Failed to instantiate APIClient. Ensure correct initialization parameters.") from e

def identify_field(header, field_mapping):
    for medisoft_field, patterns in field_mapping.items():
        for pattern in patterns:
            if re.search(pattern, header, re.IGNORECASE):
                return medisoft_field
    return None

    # Add this print to a function that is calling identify_field
    #print("Warning: No matching field found for CSV header '{}'".format(header))

# Function to execute an AutoHotkey script
def run_ahk_script(script_content):
    temp_script_name = None  # Initialize variable to hold the name of the temporary script file
    try:
        # Create a temporary AHK script file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ahk', encoding='utf-8') as temp_script:
            temp_script_name = temp_script.name  # Store the name of the temporary script file
            temp_script.write(script_content)  # Write the script content to the temporary file
            temp_script.flush()  # Ensure the file is written to disk
        # Attempt to run the AHK script
        subprocess.check_call([AHK_EXECUTABLE, temp_script_name])  # Execute the AHK script using the AutoHotkey executable
    except subprocess.CalledProcessError as e:
        print("AHK script failed with exit status: {}".format(e.returncode))  # Log the exit status of the failed script
        print("Output from AHK script: {}".format(e.output))  # Log the output from the failed script
    except Exception as e:
        print("An unexpected error occurred while running the AHK script: {}".format(e))  # Log any unexpected errors
        traceback.print_exc()  # Print the full traceback for debugging purposes
    finally:
        # Delete the temporary script file
        if temp_script_name:
            try:
                os.unlink(temp_script_name)  # Attempt to delete the temporary script file
            except OSError as e:
                print("Error deleting temporary script file: {}".format(e))  # Log any errors encountered while deleting the file
                # Future Improvement: Implement a cleanup mechanism to handle orphaned temporary files

# Global variable to store the last processed entry
last_processed_entry = None
# Global variable to store temporarily parsed address components
parsed_address_components = {}

def process_field(medisoft_field, csv_row, parsed_address_components, reverse_mapping, csv_data, fixed_values):
    global last_processed_entry
    
    try:
        # Attempt to retrieve the value for the current medisoft_field from parsed_address_components
        value = parsed_address_components.get(medisoft_field, '') if medisoft_field in parsed_address_components else ''
        
        # If no value is found, check if there is a fixed value available for this field
        if not value:
            if medisoft_field in fixed_values:
                value = fixed_values[medisoft_field][0]  # Use the fixed value if available
        
        # If still no value, check if the field is present in the reverse mapping
        if not value and medisoft_field in reverse_mapping:
            # Retrieve the corresponding CSV header from the reverse mapping
            csv_header = reverse_mapping[medisoft_field]
            value = csv_row.get(csv_header, '')  # Get the value from the CSV row using the header
            
            # Log the detected field and its value after assignment
            MediLink_ConfigLoader.log("Detected {}: {}".format(medisoft_field, value), level="DEBUG")

        # Format the value for the AutoHotkey script, or default to sending an Enter key if no value is found
        formatted_value = (MediBot_dataformat_library.format_data(medisoft_field, value, csv_data, reverse_mapping, parsed_address_components)
                           if value else 'Send, {Enter}')
        
        # Execute the AutoHotkey script with the formatted value
        run_ahk_script(formatted_value)

        # Update the last processed entry with the current field and its value
        last_processed_entry = (medisoft_field, value)
        return 'continue', last_processed_entry  # Indicate to continue processing
    except Exception as e:
        # Handle any exceptions that occur during processing
        return handle_error(e, medisoft_field, last_processed_entry, csv_data)

def handle_error(error, medisoft_field, last_processed_entry, csv_data):
    MediLink_ConfigLoader.log("Error in process_field: ", e)
    print("An error occurred while processing {0}: {1}".format(medisoft_field, error))
    # Assuming the interaction mode is 'error' in this case
    interaction_mode = 'error'
    response = user_interaction(csv_data, interaction_mode, error, reverse_mapping)
    return response, last_processed_entry

# iterating through each field defined in the field_mapping.
def iterate_fields(csv_row, field_mapping, parsed_address_components, reverse_mapping, csv_data, fixed_values):
    global last_processed_entry
    # Check for user action at the start of each field processing
    for medisoft_field in field_mapping.keys():
        action = manage_script_pause(csv_data,'',reverse_mapping) # per-field pause availability. Necessary to provide frequent opportunities for the user to pause the script.
        if action != 0:  # If action is either 'Retry' (-1) or 'Skip' (1)
            return action  # Break out and pass the action up
        
        # Process each field in the row
        _, last_processed_entry = process_field(medisoft_field, csv_row, parsed_address_components, reverse_mapping, csv_data, fixed_values)
        
    return 0 # Default action to continue

def data_entry_loop(csv_data, field_mapping, reverse_mapping, fixed_values):
    global last_processed_entry, parsed_address_components
    # last_processed_entry, parsed_address_components = None, {} // BUG should this just be this line rather than the global line above?
    error_message = ''  # Initialize error_message once
    current_row_index = 0

    while current_row_index < len(csv_data):
        row = csv_data[current_row_index]
        
        # Handle script pause at the start of each row (patient record). 
        manage_script_pause(csv_data, error_message, reverse_mapping)
        error_message = ''  # Clear error message for the next iteration
        
        if app_control.get_pause_status():
            continue  # Skip processing this row if the script is paused

        # I feel like this is overwriting what would have already been idenfitied in the mapping. 
        # This probably needs to be initialized differently.
        # parsed_address_components = {'City': '', 'State': '', 'Zip Code': ''}
        parsed_address_components = {}

        # Process each field in the row
        action = iterate_fields(row, field_mapping, parsed_address_components, reverse_mapping, csv_data, fixed_values)
        # TODO (Low) add a feature here where if you accidentally started overwriting a patient that you could go back 2 patients.
        # Need to tell the user which patient we're talking about because it won't be obvious anymore.
        if action == -1:  # Retry
            continue  # Remain on the current row. 
        elif action == 1:  # Skip
            if current_row_index == len(csv_data) - 1:  # If it's the last row
                MediLink_ConfigLoader.log("Reached the end of the patient list.")
                print("Reached the end of the patient list. Looping back to the beginning.")
                current_row_index = 0  # Reset to the first row
            else:
                current_row_index += 1 # Move to the next row
            continue
        elif action == -2:  # Go back two patients and redo
            current_row_index = max(0, current_row_index - 2)  # Go back two rows, but not below 0
            continue

        # Code to handle the end of a patient record
        # TODO One day this can just not pause...
        app_control.set_pause_status(True)  # Pause at the end of processing each patient record
        current_row_index += 1  # Move to the next row by default

def open_medisoft(shortcut_path):
    try:
        os.startfile(shortcut_path)
        print("Medisoft is being opened...\n")
    except subprocess.CalledProcessError as e:
        print("Failed to open Medisoft:", e)
        print("Please manually open Medisoft.")
    except Exception as e:
        print("An unexpected error occurred:", e)
        print("Please manually open Medisoft.")
    finally:
        print("Press 'F12' to begin data entry.")

# Placeholder for any cleanup
def cleanup():
    print("\n**** Medibot Finished! ****\n")
    # THis might need to delete the staging stuff that gets set up by mostly MediLink but maybe other stuff too.
    pass 

class ExecutionState:
    def __init__(self, config_path, crosswalk_path) -> None:
        try:
            config, crosswalk = MediLink_ConfigLoader.load_configuration(config_path, crosswalk_path)
            MediLink_ConfigLoader.log("Loaded configuration: {}".format(config), level="DEBUG")
            MediLink_ConfigLoader.log("Loaded crosswalk: {}".format(crosswalk), level="DEBUG")
            self.verify_config_type(config)
            self.crosswalk = crosswalk
            self.config = config
            MediLink_ConfigLoader.log("Config loaded successfully...")

            # Instantiate APIClient
            self.api_client = APIClient()  # Pass required arguments if any

            # Simplified isinstance check
            if not isinstance(self.api_client, APIClient):
                raise TypeError("MediBot Error: api_client must be an instance of APIClient.")
            
            # Log before calling crosswalk_update
            MediLink_ConfigLoader.log("Updating crosswalk with client and config...", level="INFO")
            update_successful = crosswalk_update(self.api_client, config, crosswalk)  # Ensure crosswalk_update uses the instance. TODO We need an internet-disabled version of this.
            if update_successful:
                MediLink_ConfigLoader.log("Crosswalk update completed successfully.", level="INFO")
                print("Crosswalk update completed successfully.")
            else:
                MediLink_ConfigLoader.log("Crosswalk update failed.", level="ERROR")
                print("Crosswalk update failed.")

        except Exception as e:
            MediLink_ConfigLoader.log("MediBot: Failed to load or update configuration: {}".format(e), level="ERROR")
            print("MediBot: Failed to load or update configuration: {}".format(e))
            raise  # Re-throwing the exception or using a more sophisticated error handling mechanism might be needed
            # Handle the exception somehow (e.g., retry, halt, log)??
        
    def verify_config_type(self, config):
        MediLink_ConfigLoader.log("Verifying configuration type: {}".format(type(config)), level="DEBUG")
        if not isinstance(config, (dict, OrderedDict)):
            raise TypeError("Error: Configuration must be a dictionary or an OrderedDict. Check unpacking.")

# Main script execution wrapped in try-except for error handling
if __name__ == "__main__":
    e_state = None
    try:
        print("Please wait...")
        # Default paths for configuration and crosswalk files
        default_config_path = os.path.join(os.path.dirname(__file__), '..', 'json', 'config.json')
        default_crosswalk_path = os.path.join(os.path.dirname(__file__), '..', 'json', 'crosswalk.json')

        # Determine paths based on command-line arguments or use defaults
        config_path = sys.argv[1] if len(sys.argv) > 1 else default_config_path
        crosswalk_path = sys.argv[2] if len(sys.argv) > 2 else default_crosswalk_path
        
        e_state = ExecutionState(config_path, crosswalk_path)
        
        print("Loading CSV Data...")
        MediLink_ConfigLoader.log("Loading CSV Data...", level="INFO")
        csv_data = load_csv_data(CSV_FILE_PATH)
        
        # Pre-process CSV data to add combined fields & crosswalk values
        print("Pre-Processing CSV...")
        MediLink_ConfigLoader.log("Pre-processing CSV Data...", level="INFO")
        MediBot_Preprocessor.preprocess_csv_data(csv_data, e_state.crosswalk)  
        headers = csv_data[0].keys()  # Ensure all headers are in place
        
        print("Performing Intake Scan...")
        MediLink_ConfigLoader.log("Performing Intake Scan...", level="INFO")
        identified_fields = MediBot_Preprocessor.intake_scan(headers, field_mapping)
        
        # Reverse the identified_fields mapping for lookup
        reverse_mapping = {v: k for k, v in identified_fields.items()}
        
        # CSV Patient Triage
        interaction_mode = 'triage'  # Start in triage mode
        error_message = ""  # This will be filled if an error has occurred
        
        print("Load Complete...")
        MediLink_ConfigLoader.log("Load Complete event triggered. Clearing console. Displaying Menu...", level="INFO")
        _ = os.system('cls')
        
        proceed, selected_patient_ids, selected_indices, fixed_values = user_interaction(csv_data, interaction_mode, error_message, reverse_mapping)

        if proceed:
            # Filter csv_data for selected patients from Triage mode
            csv_data = [row for index, row in enumerate(csv_data) if index in selected_indices]
            
            # Check if MAPAT_MED_PATH is missing or invalid
            if not app_control.get_mapat_med_path() or not os.path.exists(app_control.get_mapat_med_path()):
                print("Warning: MAPAT.MED PATH is missing or invalid. Please check the path configuration.")

            # Perform the existing patients check
            existing_patients, patients_to_process = MediBot_Preprocessor.check_existing_patients(selected_patient_ids, app_control.get_mapat_med_path())
            
            if existing_patients:
                print("\nNOTE: The following patient(s) already EXIST in the system and \n      will be excluded from processing:")
                
                # Collect surgery dates and patient info for existing patients
                patient_info = []
                for patient_id, patient_name in existing_patients:
                    try:
                        surgery_date = next((row.get('Surgery Date') for row in csv_data if row.get(reverse_mapping['Patient ID #2']) == patient_id), None)
                        if surgery_date is None:
                            raise ValueError("Surgery Date not found for patient ID: {}".format(patient_id))
                        patient_info.append((surgery_date, patient_name, patient_id))
                    except Exception as e:
                        MediLink_ConfigLoader.log("Warning: Error retrieving Surgery Date for patient ID '{}': {}".format(patient_id, e), level="WARNING")
                        patient_info.append(('Unknown Date', patient_name, patient_id))  # Append with 'Unknown Date' if there's an error

                # Sort by surgery date first and then by patient name
                patient_info.sort(key=lambda x: (x[0], x[1]))

                # Print the sorted patient info
                for index, (surgery_date, patient_name, patient_id) in enumerate(patient_info):
                    print("{:03d}: {} (ID: {}) {}".format(index + 1, surgery_date.strftime('%m-%d'), patient_id, patient_name))

                # Update csv_data to exclude existing patients
                # TODO: Update this logic to handle patients that exist but need new charges added.
                csv_data = [row for row in csv_data if row[reverse_mapping['Patient ID #2']] in patients_to_process]
            else:
                print("\nSelected patient(s) are NEW patients and will be processed.")

            # Check if there are patients left to process
            if len(patients_to_process) == 0:
                proceed = input("\nAll patients have been processed. Continue anyway?: ").lower().strip() in ['yes', 'y']
            else:
                proceed = input("\nDo you want to proceed with the {} remaining patient(s)? (yes/no): ".format(len(patients_to_process))).lower().strip() in ['yes', 'y']

            # TODO: Here is where we need to add the step where we move to MediBot_Charges. 
            # The return is an enriched dataset to be picked up by MediBot which means we need to return: 
            # csv_data, field_mapping, reverse_mapping, and fixed_values.

            if proceed:
                print("\nRemember, when in Medisoft:")
                print("  Press 'F8'  to create a New Patient.")
                print("  Press 'F12' to begin data entry.")
                print("  Press 'F11' at any time to Pause.")
                input("\n*** Press [Enter] when ready to begin! ***\n")
                MediLink_ConfigLoader.log("Opening Medisoft...")
                open_medisoft(app_control.get_medisoft_shortcut())
                app_control.set_pause_status(True)
                _ = manage_script_pause(csv_data, error_message, reverse_mapping)
                data_entry_loop(csv_data, field_mapping, reverse_mapping, fixed_values)
                cleanup()                
            else:
                print("Data entry canceled by user. Exiting MediBot.")
    except Exception as e:
        if e_state:
            interaction_mode = 'error'  # Switch to error mode
            error_message = str(e)  # Capture the error message
        print("An error occurred while running MediBot: {}".format(e))
        # Handle the error by calling user interaction with the error information
        if 'identified_fields' in locals():
            _ = user_interaction(csv_data, interaction_mode, error_message, reverse_mapping)
        else:
            print("Please ensure CSV headers match expected field names in config file, then re-run Medibot.")