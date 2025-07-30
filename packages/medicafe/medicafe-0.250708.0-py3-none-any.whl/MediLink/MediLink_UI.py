# MediLink_UI.py
from datetime import datetime
import os, sys

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.append(project_dir)

try:
    import MediLink_ConfigLoader
except ImportError:
    from MediLink import MediLink_ConfigLoader

def display_welcome():
    print("\n" + "-" * 60)
    print("          *~^~*:    Welcome to MediLink!    :*~^~*")
    print("-" * 60)

def display_menu(options):
    print("Menu Options:")
    for i, option in enumerate(options):
        print("{0}. {1}".format(i+1, option))

def get_user_choice():
    return input("Enter your choice: ").strip()

def display_exit_message():
    print("\nExiting MediLink.")

def display_invalid_choice():
    print("Invalid choice. Please select a valid option.")

def display_patient_options(detailed_patient_data):
    """
    Displays a list of patients with their current suggested endpoints, prompting for selections to adjust.
    """
    print("\nPlease select the patients to adjust by entering their numbers separated by commas\n(e.g., 1,3,5):")
    # Can disable this extra print for now because the px list would already be on-screen.
    #for i, data in enumerate(detailed_patient_data, start=1):
    #    patient_info = "{0} ({1}) - {2}".format(data['patient_name'], data['patient_id'], data['surgery_date'])
    #    endpoint = data.get('suggested_endpoint', 'N/A')
    #    print("{:<3}. {:<30} Current Endpoint: {}".format(i, patient_info, endpoint))

def get_selected_indices(patient_count):
    """
    Collects user input for selected indices to adjust endpoints.
    """
    selected_indices_input = input("> ")
    selected_indices = [int(index.strip()) - 1 for index in selected_indices_input.split(',') if index.strip().isdigit() and 0 <= int(index.strip()) - 1 < patient_count]
    return selected_indices

def display_patient_for_adjustment(patient_name, suggested_endpoint):
    """
    Displays the current endpoint for a selected patient and prompts for a change.
    """
    print("\n- {0} | Current Endpoint: {1}".format(patient_name, suggested_endpoint))

def get_endpoint_decision():
    """
    Asks the user if they want to change the endpoint.
    Ensures a valid entry of 'Y' or 'N'.
    """
    while True:
        decision = input("Change endpoint? (Y/N): ").strip().lower()
        if decision in ['y', 'n']:
            return decision
        else:
            print("Invalid input. Please enter 'Y' for Yes or 'N' for No.")

def display_endpoint_options(endpoints_config):
    """
    Displays the endpoint options to the user based on the provided mapping.

    Args:
        endpoints_config (dict): A dictionary mapping endpoint keys to their properties, 
                                 where each property includes a 'name' key for the user-friendly name.
                                 Example: {'Availity': {'name': 'Availity'}, 'OptumEDI': {'name': 'OptumEDI'}, ...}

    Returns:
        None
    """
    print("Select the new endpoint for the patient:")
    for index, (key, details) in enumerate(endpoints_config.items(), 1):
        print("{0}. {1}".format(index, details['name']))

def get_new_endpoint_choice():
    """
    Gets the user's choice for a new endpoint.
    Ensures a valid entry of endpoint numbers.
    """
    while True:
        choice = input("Select desired endpoint (e.g. 1, 2): ").strip()
        
        # Auto-correct periods and spaces
        corrected_choice = choice.replace('.', '').replace(' ', '')
        
        if all(index.isdigit() for index in corrected_choice.split(',')):
            return corrected_choice
        else:
            print("Invalid input. I understood your request as: '{}'. Please enter valid endpoint numbers separated by commas.".format(choice))
            print("Tip: Ensure there are no extra spaces or periods in your input.")

# Function to display full list of insurance options
def display_insurance_options(insurance_options=None):

    # Retrieve insurance options with codes and descriptions
    config, _ = MediLink_ConfigLoader.load_configuration()
    insurance_options = config['MediLink_Config'].get('insurance_options')
    
    print("\nInsurance Type Options:")
    for code, description in sorted(insurance_options.items()):
        print("{}: {}".format(code, description))
    print()  # Add a blank line for better readability

def display_patient_summaries(detailed_patient_data):
    """
    Displays summaries of all patients and their suggested endpoints.
    """
    print("\nSummary of patient details and suggested endpoint:")
    for index, summary in enumerate(detailed_patient_data, start=1):
        try:
            display_file_summary(index, summary)
        except KeyError as e:
            print("Summary at index {} is missing key: {}".format(index, e))
    print() # add blank line for improved readability.

def display_file_summary(index, summary):
    # Ensure surgery_date is converted to a datetime object
    surgery_date = datetime.strptime(summary['surgery_date'], "%m-%d-%y")
    
    # Add header row if it's the first index
    if index == 1:
        print("{:<3} {:5} {:<10} {:20} {:15} {:2} {:20}".format(
            "No.", "Date", "ID", "Name", "Primary Ins.", "IT", "Suggested Endpoint"
        ))
        print("-"*80)

    # Check if insurance_type is available; if not, set a default placeholder (this should already be '12' at this point)
    insurance_type = summary.get('insurance_type', '--')

    # Displays the summary of a file.
    print("{:02d}. {:5} ({:<8}) {:20} {:15} {:2} {:20}".format(
        index,
        surgery_date.strftime("%m-%d"),
        summary['patient_id'],
        summary['patient_name'][:20],
        summary['primary_insurance'][:15],
        insurance_type[:2],
        summary['suggested_endpoint'][:20])
    )

def user_select_files(file_list):
    # Sort files by creation time in descending order
    file_list = sorted(file_list, key=os.path.getctime, reverse=True)[:10]  # Limit to max 10 files
    
    print("\nSelect the Z-form files to submit from the following list:\n")

    formatted_files = []
    for i, file in enumerate(file_list):
        basename = os.path.basename(file)
        parts = basename.split('_')
        
        # Try to parse the timestamp from the filename
        if len(parts) > 2:
            try:
                timestamp_str = parts[1] + parts[2].split('.')[0]
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                formatted_date = timestamp.strftime('%m/%d %I:%M %p')  # Changed to 12HR format with AM/PM
            except ValueError:
                formatted_date = basename  # Fallback to original filename if parsing fails
        else:
            formatted_date = basename  # Fallback to original filename if no timestamp
        
        formatted_files.append((formatted_date, file))
        print("{}: {}".format(i + 1, formatted_date))
    
    selected_indices = input("\nEnter the numbers of the files to process, separated by commas\n(or press Enter to select all): ")
    if not selected_indices:
        return [file for _, file in formatted_files]
    
    selected_indices = [int(i.strip()) - 1 for i in selected_indices.split(',')]
    selected_files = [formatted_files[i][1] for i in selected_indices]
    
    return selected_files