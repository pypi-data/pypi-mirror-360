# MediLink_837p_encoder_library.py
from datetime import datetime
import sys, os
from MediLink import MediLink_ConfigLoader

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from MediBot import MediBot_Preprocessor_lib
load_insurance_data_from_mains = MediBot_Preprocessor_lib.load_insurance_data_from_mains
from MediBot import MediBot_Crosswalk_Library
from MediLink_API_v3 import fetch_payer_name_from_api

# Converts date format from one format to another.
def convert_date_format(date_str):
    # Parse the input date string into a datetime object using the input format    
    # Determine the input date format based on the length of the input string
    input_format = "%m-%d-%Y" if len(date_str) == 10 else "%m-%d-%y"
    date_obj = datetime.strptime(date_str, input_format)
    # Format the datetime object into the desired output format and return
    return date_obj.strftime("%Y%m%d")

# Formats date and time according to the specified format.
def format_datetime(dt=None, format_type='date'):
    if dt is None:
        dt = datetime.now()
    if format_type == 'date':
        return dt.strftime('%Y%m%d')
    elif format_type == 'isa':
        return dt.strftime('%y%m%d')
    elif format_type == 'time':
        return dt.strftime('%H%M')

# Constructs the ST segment for transaction set.
def create_st_segment(transaction_set_control_number):
    return "ST*837*{:04d}*005010X222A1~".format(transaction_set_control_number)

# Constructs the BHT segment based on parsed data.
def create_bht_segment(parsed_data):
    chart_number = parsed_data.get('CHART', 'UNKNOWN')
    return "BHT*0019*00*{}*{}*{}*CH~".format(
        chart_number, format_datetime(), format_datetime(format_type='time'))
    
# Constructs the HL segment for billing provider.
def create_hl_billing_provider_segment():
    return "HL*1**20*1~"

# Constructs the NM1 segment for billing provider and includes address and Tax ID.
def create_nm1_billing_provider_segment(config, endpoint):
    endpoint_config = config['endpoints'].get(endpoint.upper(), {})
    
    # Billing provider details
    billing_provider_entity_code = endpoint_config.get('billing_provider_entity_code', '85')
    billing_provider_npi_qualifier = endpoint_config.get('billing_provider_npi_qualifier', 'XX')
    #billing_provider_lastname = endpoint_config.get('billing_provider_lastname', config.get('default_billing_provider_name', 'DEFAULT NAME'))
    #billing_provider_firstname = endpoint_config.get('billing_provider_firstname', '')
    billing_provider_lastname = config.get('billing_provider_lastname', config.get('default_billing_provider_name', 'DEFAULT NAME'))
    billing_provider_firstname = config.get('billing_provider_firstname', '')
    billing_provider_npi = endpoint_config.get('billing_provider_npi', config.get('default_billing_provider_npi', 'DEFAULT NPI'))
    
    # Determine billing_entity_type_qualifier based on the presence of billing_provider_firstname
    billing_entity_type_qualifier = '1' if billing_provider_firstname else '2' 
    
    # Construct NM1 segment for the billing provider
    nm1_segment = "NM1*{}*{}*{}*{}****{}*{}~".format(
        billing_provider_entity_code, 
        billing_entity_type_qualifier,
        billing_provider_lastname, 
        billing_provider_firstname,
        billing_provider_npi_qualifier, 
        billing_provider_npi
    )
  
    # Construct address segments
    address_segments = []
    if config.get('billing_provider_address'):
        # N3 segment for address line
        address_segments.append("N3*{}~".format(config.get('billing_provider_address', 'NO ADDRESS')))
        # N4 segment for City, State, ZIP
        address_segments.append("N4*{}*{}*{}~".format(
            config.get('billing_provider_city', 'NO CITY'), 
            config.get('billing_provider_state', 'NO STATE'), 
            config.get('billing_provider_zip', 'NO ZIP')
        ))
    
    # Assuming Tax ID is part of the same loop, otherwise move REF segment to the correct loop
    ref_segment = "REF*EI*{}~".format(config.get('billing_provider_tin', 'NO TAX ID'))
    
    # Construct PRV segment if provider taxonomy is needed, are these just for Medicaid??
    #prv_segment = ""
    #if config.get('billing_provider_taxonomy'):
    #    prv_segment = "PRV*BI*PXC*{}~".format(config.get('billing_provider_taxonomy'))
    
    # Combine all the segments in the correct order, I think the PRV goes after the address and/or after ref
    segments = [nm1_segment]
    #if prv_segment:
    #    segments.append(prv_segment)
    segments.extend(address_segments)
    segments.append(ref_segment)
    
    return segments

# Constructs the NM1 segment and accompanying details for the service facility location.
def create_service_facility_location_npi_segment(config):
    """
    Constructs segments for the service facility location, including the NM1 segment for identification
    and accompanying N3 and N4 segments for address details.
    """
    facility_npi = config.get('service_facility_npi', 'DEFAULT FACILITY NPI')
    facility_name = config.get('service_facility_name', 'DEFAULT FACILITY NAME')
    address_line_1 = config.get('service_facility_address', 'NO ADDRESS')
    city = config.get('service_facility_city', 'NO CITY')
    state = config.get('service_facility_state', 'NO STATE')
    zip_code = config.get('service_facility_zip', 'NO ZIP')

    # NM1 segment for facility identification
    nm1_segment = "NM1*77*2*{}*****XX*{}~".format(facility_name, facility_npi)
    # N3 segment for facility address
    n3_segment = "N3*{}~".format(address_line_1)
    # N4 segment for facility city, state, and ZIP
    n4_segment = "N4*{}*{}*{}~".format(city, state, zip_code)

    return [nm1_segment, n3_segment, n4_segment]

# Constructs the NM1 segment for submitter name and includes PER segment for contact information.
def create_1000A_submitter_name_segment(patient_data, config, endpoint):
    """
    Creates the 1000A submitter name segment, including the PER segment for contact information.

    Args:
        patient_data (dict): Enriched patient data containing payer information.
        config (dict): Configuration settings.
        endpoint (str): Intended Endpoint for resolving submitter information.

    Returns:
        list: A list containing the NM1 segment for the submitter name and the PER segment for contact information.
    """
    endpoint_config = config['endpoints'].get(endpoint.upper(), {})
    submitter_id_qualifier = endpoint_config.get('submitter_id_qualifier', '46')  # '46' for ETIN or 'XX' for NPI
    submitter_name = endpoint_config.get('nm_103_value', 'DEFAULT NAME')  # Default name if not in config
    
    # Extract payer_id from patient_data
    payer_id = patient_data.get('payer_id', '')
    
    # Check if payer_id is Florida Blue (00590 or BCBSF) and assign submitter_id accordingly
    if payer_id in ['00590', 'BCBSF']:
        submitter_id = endpoint_config.get('nm_109_bcbsf', 'DEFAULT BCBSF ID')
    else:
        submitter_id = endpoint_config.get('nm_109_value', 'DEFAULT ID')  # Default ID if not specified in endpoint
    
    # Submitter contact details
    contact_name = config.get('submitter_name', 'NONE')
    contact_telephone_number = config.get('submitter_tel', 'NONE')
    entity_type_qualifier = '2' # if contact_name else '1'  BUG - 1 if submitter_first_name is not empty. Reference: billing_entity_type_qualifier = '1' if billing_provider_firstname else '2' 
    
    # Construct NM1 segment for the submitter
    nm1_segment = "NM1*41*{}*{}*****{}*{}~".format(entity_type_qualifier, submitter_name, submitter_id_qualifier, submitter_id) # BUG - need to check submitter_name because this is written as fixed ****** which implies a single entry and not a first and last name. This is weird.
    
    # Construct PER segment for the submitter's contact information
    per_segment = "PER*IC*{}*TE*{}~".format(contact_name, contact_telephone_number)

    return [nm1_segment, per_segment]

# Constructs the NM1 segment for the receiver (1000B).
def create_1000B_receiver_name_segment(config, endpoint):
    # Retrieve endpoint specific configuration
    endpoint_config = config['endpoints'].get(endpoint.upper(), {})

    # Set the entity identifier code to '40' for receiver and qualifier to '46' for EDI, 
    # unless specified differently in the endpoint configuration.
    receiver_entity_code = '40'
    receiver_id_qualifier = endpoint_config.get('receiver_id_qualifier', '46')
    receiver_name = endpoint_config.get('receiver_name', 'DEFAULT RECEIVER NAME')
    receiver_edi = endpoint_config.get('receiver_edi', 'DEFAULT EDI')
    
    return "NM1*{entity_code}*2*{receiver_name}*****{id_qualifier}*{receiver_edi}~".format(
        entity_code=receiver_entity_code,
        receiver_name=receiver_name,
        id_qualifier=receiver_id_qualifier,
        receiver_edi=receiver_edi
    )

def payer_id_to_payer_name(parsed_data, config, endpoint, crosswalk, client):
    """
    Preprocesses payer information from parsed data and enriches parsed_data with the payer name and ID.

    Args:
        parsed_data (dict): Parsed data containing Z-dat information.
        config (dict): Configuration settings.
        endpoint (str): Intended Endpoint for resolving payer information.

    Returns:
        dict: Enriched parsed data with payer name and payer ID.
    """
    # Step 1: Extract insurance name from parsed data
    insurance_name = parsed_data.get('INAME', '')

    # Step 2: Map insurance name to payer ID
    payer_id = map_insurance_name_to_payer_id(insurance_name, config, client, crosswalk)

    # Step 3: Validate payer_id
    if payer_id is None:
        error_message = "Payer ID for '{}' cannot be None.".format(insurance_name)
        MediLink_ConfigLoader.log(error_message, level="WARNING")
        raise ValueError(error_message)

    # Step 4: Resolve payer name using payer ID
    payer_name = resolve_payer_name(payer_id, config, endpoint, insurance_name, parsed_data, crosswalk, client)

    # Enrich parsed_data with payer name and payer ID
    parsed_data['payer_name'] = payer_name
    parsed_data['payer_id'] = payer_id

    return parsed_data

# Then you can use the enriched parsed_data in your main function
def create_2010BB_payer_information_segment(parsed_data):
    """
    Creates the 2010BB payer information segment.

    Args:
        parsed_data (dict): Parsed data containing enriched payer information.

    Returns:
        str: The 2010BB payer information segment.
    """
    # Extract enriched payer name and payer ID
    payer_name = parsed_data.get('payer_name')
    payer_id = parsed_data.get('payer_id')

    # Validate payer_name and payer_id
    if not payer_name or not payer_id:
        error_message = "Payer name and payer ID must be provided."
        raise ValueError(error_message)

    # Build NM1 segment using provided payer name and payer ID
    return build_nm1_segment(payer_name, payer_id)

def get_user_confirmation(prompt_message):
    while True:
        response = input(prompt_message).strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please respond with 'yes' or 'no'.")

def resolve_payer_name(payer_id, config, primary_endpoint, insurance_name, parsed_data, crosswalk, client):
    # Check if the payer_id is in the crosswalk with a name already attached to it.
    if payer_id in crosswalk.get('payer_id', {}):
        payer_info = crosswalk['payer_id'][payer_id]
        MediLink_ConfigLoader.log("Payer ID {} found in crosswalk with name: {}".format(payer_id, payer_info['name']), level="DEBUG")
        return payer_info['name']  # Return the name from the crosswalk directly.
    
    # Step 1: Attempt to fetch payer name from API using primary endpoint
    MediLink_ConfigLoader.log("Attempting to resolve Payer ID {} via API.".format(payer_id), level="INFO")
    try:
        return fetch_payer_name_from_api(client, payer_id, config, primary_endpoint)
    except Exception as api_error:
        # Step 2: Log API resolution failure and initiate user intervention
        MediLink_ConfigLoader.log("API resolution failed for {}: {}. Initiating user intervention.".format(payer_id, str(api_error)), config, level="WARNING")
        
        # Step 3: Print warning message for user intervention
        print("\n\nWARNING: Unable to verify Payer ID '{}' for patient '{}'!".format(payer_id, parsed_data.get('CHART', 'unknown')))
        print("         Claims for '{}' may be incorrectly routed or fail without intervention.".format(insurance_name))
        print("\nACTION REQUIRED: Please verify the internet connection and the Payer ID by searching for it at the expected endpoint's website or using Google.")
        print("\nNote: If the Payer ID '{}' is incorrect for '{}', \nit may need to be manually corrected.".format(payer_id, insurance_name))
        print("If the Payer ID appears correct, you may skip the correction and force-continue with this one.")
        print("\nPlease check the Payer ID in the Crosswalk and the initial \ndata source (e.g., Carol's CSV) as needed.")
        print("If unsure, llamar a Dani for guidance on manual corrections.")
    
        # Step 4: Integrate user input logic
        user_decision = input("\nType 'FORCE' to force-continue with the Medisoft name, or press Enter to pause processing and make corrections: ").strip().lower()
        
        if user_decision == 'force':
            # Step 5: Fallback to truncated insurance name
            truncated_name = insurance_name[:10]  # Temporary fallback
            MediLink_ConfigLoader.log("Using truncated insurance name '{}' as a fallback for {}".format(truncated_name, payer_id), config, level="WARNING")
            return truncated_name
        elif not user_decision:
            # Step 6: Prompt user for corrected payer ID
            corrected_payer_id = prompt_user_for_payer_id(insurance_name)
            if corrected_payer_id:
                try:
                    resolved_name = fetch_payer_name_from_api(client, corrected_payer_id, config, primary_endpoint)
                    print("API resolved to insurance name: {}".format(resolved_name))
                    MediLink_ConfigLoader.log("API Resolved to standard insurance name: {} for corrected payer ID: {}".format(resolved_name, corrected_payer_id), config, level="INFO")
    
                    # Step 7: Ask for user confirmation using the helper
                    confirmation_prompt = "Proceed with updating the Payer ID for '{}'? (yes/no): ".format(resolved_name)
                    if get_user_confirmation(confirmation_prompt):
                        # Step 8: Load crosswalk
                        try:
                            config, crosswalk = MediLink_ConfigLoader.load_configuration()
                        except Exception as e:
                            print("Failed to load configuration and crosswalk: {}".format(e))
                            MediLink_ConfigLoader.log("Failed to load configuration and crosswalk: {}".format(e), config, level="ERROR")
                            exit(1)
                        
                        # Step 9: Update the crosswalk with the corrected Payer ID
                        if MediBot_Crosswalk_Library.update_crosswalk_with_corrected_payer_id(client, payer_id, corrected_payer_id, config, crosswalk):
                            return resolved_name
                        else:
                            print("Failed to update crosswalk with the corrected Payer ID.")
                            MediLink_ConfigLoader.log("Failed to update crosswalk with the corrected Payer ID.", config, level="ERROR")
                            exit(1)  # Consider handling failure differently.
                    else:
                        # Step 10: Handle rejection
                        print("User did not confirm the standard insurance name. Manual intervention is required.")
                        MediLink_ConfigLoader.log("User did not confirm the standard insurance name. Manual intervention is required.", config, level="CRITICAL")
                        
                        # TODO: CRITICAL ISSUE - Current rejection handling is incorrect
                        # The current implementation exits the program when a user rejects the standard insurance name,
                        # which is an overly aggressive approach. Instead, we should:
                        # 1. Prompt the user to manually enter the correct insurance name
                        # 2. Use that manually entered name to proceed with the claim processing
                        # 3. Update the crosswalk with the corrected payer name (requires a new function to be implemented)
                        # 4. Log the correction for future reference
                        #
                        # The insurance name confirmation is primarily a sanity check to verify the API recognizes the payer ID,
                        # not a critical validation for claim processing. The payer name is not used in the crosswalk or in the
                        # actual claims once they are built. The current implementation unnecessarily halts the entire process
                        # when this check fails, rather than providing a recovery path.
                        #
                        # When revisiting this code, the entire flow of interdependent functions should be reconsidered to
                        # ensure proper error handling and recovery mechanisms are in place throughout the process.
                        
                        # Placeholder for future implementation:
                        # corrected_name = input("Please enter the correct insurance name: ")
                        # MediLink_ConfigLoader.log(f"User provided corrected insurance name: {corrected_name}", config, level="INFO")
                        # print(f"Using manually entered insurance name: {corrected_name}")
                        # TODO: Implement update_crosswalk_with_corrected_payer_name(corrected_name, payer_id, config, crosswalk)
                        # return corrected_name
    
                        exit(1)  
                except Exception as e:
                    # Step 11: Handle exceptions during resolution
                    print("Failed to resolve corrected payer ID to standard insurance name: {}".format(e))
                    MediLink_ConfigLoader.log("Failed to resolve corrected payer ID to standard insurance name: {}".format(e), config, level="ERROR")
                    exit(1)  # Consider handling differently.
            else:
                # Step 12: Handle absence of corrected payer ID
                print("Exiting script. Please make the necessary corrections and retry.")
                MediLink_ConfigLoader.log("Exiting script due to absence of corrected Payer ID.", config, level="CRITICAL")
                exit(1)  # Consider handling differently.
        else:
            # Optional: Handle unexpected user input
            print("Invalid input. Manual intervention is required.")
            MediLink_ConfigLoader.log("Invalid user input during payer name resolution.", config, level="CRITICAL")
            exit(1)  # Consider handling differently.

def handle_missing_payer_id(insurance_name, config, crosswalk, client):
    # Reset config pull to make sure its not using the MediLink config key subset
    config, crosswalk = MediLink_ConfigLoader.load_configuration()
    
    # Step 1: Inform about the missing Payer ID
    print("Missing Payer ID for insurance name: {}".format(insurance_name))
    MediLink_ConfigLoader.log("Missing Payer ID for insurance name: {}".format(insurance_name), config, level="WARNING")
    
    # Step 2: Prompt the user for manual payer ID input
    payer_id = prompt_user_for_payer_id(insurance_name)
    
    if not payer_id:
        # Step 3: Handle absence of payer ID input
        message = "Unable to resolve missing Payer ID. Manual intervention is required."
        MediLink_ConfigLoader.log(message, config, level="CRITICAL")
        print(message)
        return None
    
    # Step 4: Resolve the payer ID to a standard insurance name via API
    try:
        # primary_endpoint=None should kick to the default in the API function.
        standard_insurance_name = resolve_payer_name(payer_id, config, primary_endpoint=None, insurance_name=insurance_name, parsed_data={}, crosswalk=crosswalk, client=client)
        message = "Resolved to standard insurance name: {} for payer ID: {}".format(standard_insurance_name, payer_id)
        print(message)
        MediLink_ConfigLoader.log(message, config, level="INFO")
    except Exception as e:
        # Step 5: Handle exceptions during resolution
        message = "Failed to resolve payer ID to standard insurance name: {}".format(e)
        print(message)
        MediLink_ConfigLoader.log(message, config, level="ERROR")
        return None
    
    # Step 6: Ask for user confirmation
    confirmation_prompt = "Is the standard insurance name '{}' correct? (yes/no): ".format(standard_insurance_name)
    if get_user_confirmation(confirmation_prompt):
        # Step 7: Update the crosswalk with the new payer ID and insurance name mapping
        try:
            MediLink_ConfigLoader.log("Updating crosswalk with payer ID: {} for insurance name: {}".format(payer_id, insurance_name), config, level="DEBUG")
            MediBot_Crosswalk_Library.update_crosswalk_with_new_payer_id(client, insurance_name, payer_id, config, crosswalk)
            return payer_id  # Return the payer_id after successful update
        except Exception as e:
            # Enhanced error message to include exception type and context
            error_message = "Failed to update crosswalk with new Payer ID: {}. Exception type: {}. Context: {}".format(
                e, type(e).__name__, str(e)
            )
            print(error_message)
            MediLink_ConfigLoader.log(error_message, config, level="ERROR")
            return None
    else:
        # Step 8: Handle rejection
        print("User did not confirm the standard insurance name. Manual intervention is required.")
        MediLink_ConfigLoader.log("User did not confirm the standard insurance name. Manual intervention is required.", config, level="CRITICAL")
        return None

def prompt_user_for_payer_id(insurance_name):
    """
    Prompts the user to input the payer ID manually and ensures that a valid alphanumeric ID is provided.
    """
    while True:
        print("Manual intervention required: No payer ID found for insurance name '{}'.".format(insurance_name))
        payer_id = input("Please enter the payer ID manually: ").strip()
        
        if payer_id.isalnum():
            return payer_id
        else:
            print("Error: Payer ID must be alphanumeric. Please try again.")

def build_nm1_segment(payer_name, payer_id):
    # Step 1: Build NM1 segment using payer name and ID
    return "NM1*PR*2*{}*****PI*{}~".format(payer_name, payer_id)

def map_insurance_name_to_payer_id(insurance_name, config, client, crosswalk):
    """
    Maps insurance name to payer ID using the crosswalk configuration.

    Args:
        insurance_name (str): Name of the insurance.
        config (dict): Configuration settings.

    Returns:
        str: The payer ID corresponding to the insurance name.
    """
    try:        
        # Load crosswalk configuration only if 'payer_id' is not initialized
        if 'payer_id' not in crosswalk:
            _, crosswalk = MediLink_ConfigLoader.load_configuration(None, config.get('crosswalkPath', 'crosswalk.json'))
            
            # Ensure crosswalk is initialized and 'payer_id' key is available
            if 'payer_id' not in crosswalk:
                raise ValueError("Crosswalk 'payer_id' not found. Please run MediBot_Preprocessor.py with the --update-crosswalk argument.")

        # Load insurance data from MAINS to get insurance ID
        insurance_to_id = load_insurance_data_from_mains(config)
        
        # Get medisoft ID corresponding to the insurance name
        medisoft_id = insurance_to_id.get(insurance_name)
        if medisoft_id is None:
            error_message = "No Medisoft ID found for insurance name: {}. Consider checking MAINS directly.".format(insurance_name)
            MediLink_ConfigLoader.log(error_message, config, level="ERROR")
            # Asking for payer ID here is not the right approach.
            raise ValueError(error_message)
        
        # Convert medisoft_id to string to match the JSON data type
        medisoft_id_str = str(medisoft_id)
        
        # Get payer ID corresponding to the medisoft ID
        payer_id = None
        for payer, payer_info in crosswalk['payer_id'].items():
            if medisoft_id_str in payer_info['medisoft_id']:
                payer_id = payer
                break

        # Handle the case where no payer ID is found
        if payer_id is None:
            error_message = "No payer ID found for Medisoft ID: {}.".format(medisoft_id)
            MediLink_ConfigLoader.log(error_message, config, level="ERROR")
            print(error_message)
            payer_id = handle_missing_payer_id(insurance_name, config, crosswalk, client)

        if payer_id is None:
            raise ValueError("Payer ID cannot be None after all checks.")

        return payer_id

    except ValueError as e:
        if "JSON" in str(e) and "decode" in str(e):
            error_message = "Error decoding the crosswalk JSON file in map_insurance_name_to_payer_id"
            MediLink_ConfigLoader.log(error_message, config, level="CRITICAL")
            raise ValueError(error_message)
        else:
            error_message = "Unexpected error in map_insurance_name_to_payer_id: {}".format(e)
            MediLink_ConfigLoader.log(error_message, config, level="ERROR")
            raise e

def create_nm1_payto_address_segments(config):
    """
    Constructs the NM1 segment for the Pay-To Address, N3 for street address, and N4 for city, state, and ZIP.
    This is used if the Pay-To Address is different from the Billing Provider Address.
    """
    payto_provider_name = config.get('payto_provider_name', 'DEFAULT PAY-TO NAME')
    payto_address = config.get('payto_address', 'DEFAULT PAY-TO ADDRESS')
    payto_city = config.get('payto_city', 'DEFAULT PAY-TO CITY')
    payto_state = config.get('payto_state', 'DEFAULT PAY-TO STATE')
    payto_zip = config.get('payto_zip', 'DEFAULT PAY-TO ZIP')

    nm1_segment = "NM1*87*2*{}~".format(payto_provider_name)  # '87' indicates Pay-To Provider
    n3_segment = "N3*{}~".format(payto_address)
    n4_segment = "N4*{}*{}*{}~".format(payto_city, payto_state, payto_zip)

    return [nm1_segment, n3_segment, n4_segment]

def create_payer_address_segments(config):
    """
    Constructs the N3 and N4 segments for the payer's address.
    
    """
    payer_address_line_1 = config.get('payer_address_line_1', '')
    payer_city = config.get('payer_city', '')
    payer_state = config.get('payer_state', '')
    payer_zip = config.get('payer_zip', '')

    n3_segment = "N3*{}~".format(payer_address_line_1)
    n4_segment = "N4*{}*{}*{}~".format(payer_city, payer_state, payer_zip)

    return [n3_segment, n4_segment]

# Constructs the PRV segment for billing provider.
def create_billing_prv_segment(config, endpoint):
    if endpoint.lower() == 'optumedi':
        return "PRV*BI*PXC*{}~".format(config['billing_provider_taxonomy'])
    return ""

# Constructs the HL segment for subscriber [hierarchical level (HL*2)]
def create_hl_subscriber_segment():
    return ["HL*2*1*22*0~"]

# (2000B Loop) Constructs the SBR segment for subscriber based on parsed data and configuration.
def create_sbr_segment(config, parsed_data, endpoint):
    # Determine the payer responsibility sequence number code based on the payer type
    # If the payer is Medicare, use 'P' (Primary)
    # If the payer is not Medicare and is primary insurance, use 'P' (Primary)
    # If the payer is secondary insurance after Medicare, use 'S' (Secondary)
    # Assume everything is Primary for now.
    responsibility_code = 'P'

    # Insurance Type Code
    insurance_type_code = insurance_type_selection(parsed_data)

    # Construct the SBR segment using the determined codes
    sbr_segment = "SBR*{responsibility_code}*18*******{insurance_type_code}~".format(
        responsibility_code=responsibility_code,
        insurance_type_code=insurance_type_code
    )
    return sbr_segment

def insurance_type_selection(parsed_data):
    """
    Quick Fix: This funtion selects the insurance type for a patient based on predefined codes.
    
    TODO (HIGH SBR09) Finish making this function. 
    This should  eventually integrate into a menu upstream. This menu flow probably needs to be alongside the suggested endpoint flow.
    For now let's make a menu here and then figure out the automated/API method to getting this per patient as there are no
    useful historical patterns other than to say that the default should be PPO (12), then CI, then FI as most common options, 
    followed by the rest. 
    
    Present a user-selectable menu of insurance types based on predefined codes.
    User needs to input the desired 2 character code for that patient or default to PPO.
    
    Currently implements a simple text-based selection menu to choose
    an insurance type for a patient. The default selection is '12' for PPO, but the user
    can input other codes as per the options listed. This initial implementation uses
    simple input/output functions for selection and can be replaced in the future by a 
    more dynamic interface or API-driven selection method.

    Future Enhancements:
    - Automate selection via an API that fetches patient data directly and auto-assigns the insurance type.
    - Error handling to manage incorrect inputs and retry mechanisms.
    
    Parameters:
    - parsed_data (dict): Contains patient's last name under key 'LAST'.
    
    Returns:
    - str: The insurance type code selected by the user.
    
    """
    MediLink_ConfigLoader.log("insurance_type_selection(parsed_data): {}".format(parsed_data), level="DEBUG")
    
    # Check if insurance type is already assigned and is valid
    insurance_type_code = parsed_data.get('insurance_type')
    if insurance_type_code and len(insurance_type_code) == 2 and insurance_type_code.isalnum():
        MediLink_ConfigLoader.log("Insurance type already assigned: {}".format(insurance_type_code), level="DEBUG")
        return insurance_type_code
    elif insurance_type_code:
        MediLink_ConfigLoader.log("Invalid insurance type: {}".format(insurance_type_code), level="WARNING")
    
    print("\nInsurance Type Validation Error: Select the insurance type for patient {}: ".format(parsed_data['LAST']))

    # Retrieve insurance options with codes and descriptions
    config, _ = MediLink_ConfigLoader.load_configuration()
    insurance_options = config['MediLink_Config'].get('insurance_options')

    def prompt_display_insurance_options():
        # Prompt to display full list
        display_full_list = input("Do you want to see the full list of insurance options? (yes/no): ").strip().lower()

        # Display full list if user confirms
        if display_full_list in ['yes', 'y']:
            MediLink_UI.display_insurance_options(insurance_options)

    # Horrible menu
    prompt_display_insurance_options()
    
    # Default selection
    insurance_type_code = '12'

    # User input for insurance type
    user_input = input("Enter the 2-character code for the insurance type (or press Enter to default to '12' for PPO): ").strip().upper()

    # Validate input and set the insurance type code
    if user_input in insurance_options:
        insurance_type_code = user_input
    else:
        print("Skipped or Input not recognized. Defaulting to Preferred Provider Organization (PPO)\n")

    return insurance_type_code

# Constructs the NM1 segment for subscriber based on parsed data and configuration.
def create_nm1_subscriber_segment(config, parsed_data, endpoint):
    if endpoint.lower() == 'optumedi':
        entity_identifier_code = config['endpoints']['OPTUMEDI'].get('subscriber_entity_code', 'IL')
    else:
        entity_identifier_code = 'IL'  # Default value if endpoint is not 'optumedi'

    return "NM1*{entity_identifier_code}*1*{last_name}*{first_name}*{middle_name}***MI*{policy_number}~".format(
        entity_identifier_code=entity_identifier_code,
        last_name=parsed_data['LAST'].replace('_', ' '), # Replace underscores with spaces in the name.
        first_name=parsed_data['FIRST'].replace('_', ' '),
        middle_name=parsed_data['MIDDLE'],
        policy_number=parsed_data['IPOLICY']
    )

# Constructs the N3 and N4 segments for subscriber address based on parsed data.
def create_subscriber_address_segments(parsed_data):
    return [
        "N3*{}~".format(parsed_data['ISTREET']),
        "N4*{}*{}*{}~".format(
            parsed_data['ICITY'],  
            parsed_data['ISTATE'],  
            parsed_data['IZIP'][:5]
        )
    ]

# Constructs the DMG segment for subscriber based on parsed data.
def create_dmg_segment(parsed_data):
    return "DMG*D8*{}*{}~".format(
        convert_date_format(parsed_data['BDAY']),  
        parsed_data['SEX'] # ensure it returns a string instead of a list if it only returns one segment
    )

def create_nm1_rendering_provider_segment(config, is_rendering_provider_different=False):
    """
    # BUG This is getting placed incorrectly. Has this been fixed??
    
    Constructs the NM1 segment for the rendering provider in the 2310B loop using configuration data.
    
    Parameters:
    - config: Configuration dictionary including rendering provider details.
    - is_rendering_provider_different: Boolean indicating if rendering provider differs from billing provider.
    
    Returns:
    - List containing the NM1 segment for the rendering provider if required, otherwise an empty list.
    """
    if is_rendering_provider_different:
        segments = []
        rp_npi = config.get('rendering_provider_npi', '')
        rp_last_name = config.get('rendering_provider_last_name', '')
        rp_first_name = config.get('rendering_provider_first_name', '')

        # NM1 Segment for Rendering Provider
        segments.append("NM1*82*1*{0}*{1}**XX*{2}~".format(
            rp_last_name, 
            rp_first_name, 
            rp_npi
        ))
        
        # PRV Segment for Rendering Provider Taxonomy
        if config.get('rendering_provider_taxonomy'):
            segments.append("PRV*PE*PXC*{}~".format(config['billing_provider_taxonomy']))
        
        return segments
    else:
        return []

def format_claim_number(chart_number, date_of_service):
    # Remove any non-alphanumeric characters from chart number and date
    chart_number_alphanumeric = ''.join(filter(str.isalnum, chart_number))
    date_of_service_alphanumeric = ''.join(filter(str.isalnum, date_of_service))
    
    # Combine the alphanumeric components without spaces
    formatted_claim_number = chart_number_alphanumeric + date_of_service_alphanumeric
    
    return formatted_claim_number

# Constructs the CLM and related segments based on parsed data and configuration.
def create_clm_and_related_segments(parsed_data, config, crosswalk): 
    """
    Insert the claim information (2300 loop), 
    ensuring that details such as claim ID, total charge amount,and service date are included.
    
    The HI segment for Health Care Diagnosis Codes should accurately reflect the diagnosis related to the service line.
    
    Service Line Information (2400 Loop):
    Verify that the service line number (LX), professional service (SV1), and service date (DTP) segments contain
    accurate information and are formatted according to the claim's details.
    """
    
    segments = []
    
    # Format the claim number
    chart_number = parsed_data.get('CHART', '')
    date_of_service = parsed_data.get('DATE', '')
    formatted_claim_number = format_claim_number(chart_number, date_of_service)
        
    # CLM - Claim Information
    segments.append("CLM*{}*{}***{}:B:1*Y*A*Y*Y~".format(
        formatted_claim_number,
        parsed_data['AMOUNT'],
        parsed_data['TOS']))
    
    # HI - Health Care Diagnosis Code
    # Hardcoding "ABK" for ICD-10 codes as they are the only ones used now.
    medisoft_code = ''.join(filter(str.isalnum, parsed_data['DIAG']))
    diagnosis_code = next((key for key, value in crosswalk.get('diagnosis_to_medisoft', {}).items() if value == medisoft_code), None) 
    
    if diagnosis_code is None:
        error_message = "Diagnosis code is empty for chart number: {}. Please verify. Medisoft code is {}".format(chart_number, medisoft_code)
        MediLink_ConfigLoader.log(error_message, config, level="CRITICAL")
        print(error_message)
        diagnosis_code = input("Enter the complete diagnosis code: ")
        # Update the crosswalk dictionary with the new pairing of diagnosis_code and medisoft_code.
        crosswalk['diagnosis_to_medisoft'][diagnosis_code] = medisoft_code
        MediLink_ConfigLoader.log("Updated crosswalk with new diagnosis code: {}, for Medisoft code {}".format(diagnosis_code, medisoft_code), config, level="INFO")
        # TODO This needs to actually save the .json though which right now I'd like to route through the dedicated function for updating the crosswalk. 
        # TODO This should have been a validation exercise upstream and not a last minute check like this.

    cleaned_diagnosis_code = ''.join(char for char in diagnosis_code if char.isalnum())
    segments.append("HI*ABK:{}~".format(cleaned_diagnosis_code))
    
    # (2310C Loop) Service Facility Location NPI and Address Information
    segments.extend(create_service_facility_location_npi_segment(config))
    
    # For future reference, SBR - (Loop 2320: OI, NM1 (2330A), N3, N4, NM1 (2330B)) - Other Subscriber Information goes here.
    
    # LX - Service Line Number
    segments.append("LX*1~")
    
    # SV1 - Professional Service
    segments.append("SV1*HC:{}:{}*{}*MJ*{}***1~".format(
        parsed_data['CODEA'],
        parsed_data['POS'],
        parsed_data['AMOUNT'],
        parsed_data['MINTUES']))
    
    # DTP - Date
    segments.append("DTP*472*D8*{}~".format(convert_date_format(parsed_data['DATE'])))
    
    # Is there REF - Line Item Control Number missing here? Private insurance doesn't need it, but Medicare does?
    # segments.append("REF*6R*1~") # REF01, Reference Identification Qualifier; REF02, Line Item Control Number.
    # 6R - Provider Control Number (Number assigned by information provider company for tracking and billing purposes)
    # 1 - Reference information as defined for a particular Transaction Set or as specified by the Reference Identification Qualifier
    
    return segments

def get_endpoint_config(config, endpoint):
    """
    Retrieves the configuration for a specified endpoint.

    Args:
        config (dict): Configuration settings loaded from a JSON file.
        endpoint (str): The endpoint for which the configuration is requested.

    Returns:
        dict: The configuration for the specified endpoint, or raises an error if not found.
    """
    endpoint_config = config['endpoints'].get(endpoint.upper(), None)
    
    if endpoint_config is None:
        error_message = "Endpoint configuration for '{}' not found.".format(endpoint)
        MediLink_ConfigLoader.log(error_message, config, level="ERROR")
        raise ValueError(error_message)  # Raise an error for invalid endpoint

    return endpoint_config

def create_interchange_elements(config, endpoint, transaction_set_control_number):
    """
    Create interchange headers and trailers for an 837P document.

    Parameters:
    - config: Configuration settings loaded from a JSON file.
    - endpoint: The endpoint for which the data is being processed.
    - transaction_set_control_number: The starting transaction set control number.

    Returns:
    - Tuple containing (ISA header, GS header, GE trailer, IEA trailer).
    """
    endpoint_config = get_endpoint_config(config, endpoint)
    
    # Get the current system time and format it as 'HHMMSS' in 24-hour clock.
    current_time = datetime.now().strftime('%H%M%S')
    isa13 = '000' + current_time  # Format ISA13 with '000HHMMSS'.

    # Check if isa13 could not be generated from the current time
    if len(isa13) != 9:
        # If isa13 cannot be generated from the current time, use the configured value.
        isa13 = endpoint_config.get('isa_13_value', '000000001')
    
    # Create interchange header and trailer using provided library functions.
    isa_header, gs_header = create_interchange_header(config, endpoint, isa13)
    ge_trailer, iea_trailer = create_interchange_trailer(config, transaction_set_control_number, isa13)
    
    return isa_header, gs_header, ge_trailer, iea_trailer

# Generates the ISA and GS segments for the interchange header based on configuration and endpoint.
def create_interchange_header(config, endpoint, isa13):
    """
    Generate ISA and GS segments for the interchange header, ensuring endpoint-specific requirements are met.
    Includes support for Availity, Optum, and PNT_DATA endpoints, with streamlined configuration and default handling.

    Parameters:
    - config: Configuration dictionary with settings and identifiers.
    - endpoint: String indicating the target endpoint ('Availity', 'Optum', 'PNT_DATA').
    - isa13: The ISA13 field value representing the current system time.

    Returns:
    - Tuple containing the ISA and GS segment strings.
    """
    endpoint_config = config['endpoints'].get(endpoint.upper(), {})
    
    # Set defaults for ISA segment values
    isa02 = isa04 = "          "  # Default value for ISA02 and ISA04
    isa05 = isa07 = 'ZZ'  # Default qualifier
    isa15 = 'P'  # 'T' for Test, 'P' for Production
    
    # Conditional values from config
    isa_sender_id = endpoint_config.get('isa_06_value', config.get('submitterId', '')).rstrip()
    isa07_value = endpoint_config.get('isa_07_value', isa07)
    isa_receiver_id = endpoint_config.get('isa_08_value', config.get('receiverId', '')).rstrip()
    gs_sender_code = endpoint_config.get('gs_02_value', config.get('submitterEdi', ''))
    gs_receiver_code = endpoint_config.get('gs_03_value', config.get('receiverEdi', ''))
    isa15_value = endpoint_config.get('isa_15_value', isa15)

    # ISA Segment
    isa_segment = "ISA*00*{}*00*{}*{}*{}*{}*{}*{}*{}*^*00501*{}*0*{}*:~".format(
        isa02, isa04, isa05, isa_sender_id.ljust(15), isa07_value, isa_receiver_id.ljust(15),
        format_datetime(format_type='isa'), format_datetime(format_type='time'), isa13, isa15_value
    )

    # GS Segment
    # GS04 YYYYMMDD
    # GS06 Group Control Number, Field Length 1/9, must match GE02
    # BUG probably move up a function.
    gs06 = '1' # Placeholder for now?
    
    gs_segment = "GS*HC*{}*{}*{}*{}*{}*X*005010X222A1~".format(
        gs_sender_code, gs_receiver_code, format_datetime(), format_datetime(format_type='time'), gs06
    )

    MediLink_ConfigLoader.log("Created interchange header for endpoint: {}".format(endpoint), config, level="INFO")
    
    return isa_segment, gs_segment

# Generates the GE and IEA segments for the interchange trailer based on the number of transactions and functional groups.
def create_interchange_trailer(config, num_transactions, isa13, num_functional_groups=1):
    """
    Generate GE and IEA segments for the interchange trailer.
    
    Parameters:
    - config: Configuration dictionary with settings and identifiers.
    - num_transactions: The number of transactions within the functional group.
    - isa13: The ISA13 field value representing the current system time.
    - num_functional_groups: The number of functional groups within the interchange. Default is 1.
    
    Returns:
    - Tuple containing the GE and IEA segment strings.
    """
    
    # GE Segment: Functional Group Trailer
    # Indicates the end of a functional group and provides the count of the number of transactions within it.
    
    # GE02 Group Control Number, Field Length 1/9, must match GS06 (Header)
    # TODO This gs/ge matching should probably move up a function like isa13. 
    ge02 = '1' #Placeholder for now?
    ge_segment = "GE*{}*{}~".format(num_transactions, ge02)
    
    # IEA Segment: Interchange Control Trailer (Note: IEA02 needs to equal ISA13)
    iea_segment = "IEA*{}*{}~".format(num_functional_groups, isa13)
    
    MediLink_ConfigLoader.log("Created interchange trailer", config, level="INFO")
    
    return ge_segment, iea_segment

# Generates segment counts for the formatted 837P transaction and updates SE segment.
def generate_segment_counts(compiled_segments, transaction_set_control_number):
    # Count the number of segments, not including the placeholder SE segment
    segment_count = compiled_segments.count('~')   # + 1 Including SE segment itself, but seems to be giving errors.
    
    # Ensure transaction set control number is correctly formatted as a string
    formatted_control_number = str(transaction_set_control_number).zfill(4)  # Pad to ensure minimum 4 characters

    # Construct the SE segment with the actual segment count and the formatted transaction set control_number
    se_segment = "SE*{0}*{1}~".format(segment_count, formatted_control_number)

    # Assuming the placeholder SE segment was the last segment added before compiling
    # This time, we directly replace the placeholder with the correct SE segment
    formatted_837p = compiled_segments.rsplit('SE**', 1)[0] + se_segment
    
    return formatted_837p

def handle_validation_errors(transaction_set_control_number, validation_errors, config):
    for error in validation_errors:
        MediLink_ConfigLoader.log("Validation error for transaction set {}: {}".format(transaction_set_control_number, error), config, level="WARNING")
    
    print("Validation errors encountered for transaction set {}. Errors: {}".format(transaction_set_control_number, validation_errors))
    user_input = input("Skip this patient and continue without incrementing transaction set number? (yes/no): ")
    if user_input.lower() == 'yes':
        print("Skipping patient...")
        MediLink_ConfigLoader.log("Skipped processing of transaction set {} due to user decision.".format(transaction_set_control_number), config, level="INFO")
        return True  # Skip the current patient
    else:
        print("Processing halted due to validation errors.")
        MediLink_ConfigLoader.log("HALT: Processing halted at transaction set {} due to unresolved validation errors.".format(transaction_set_control_number), config, level="ERROR")
        sys.exit()  # Optionally halt further processing
        
def winscp_validate_output_directory(output_directory):
    """
    Validates the output directory path to ensure it has no spaces.
    If spaces are found, prompts the user to input a new path.
    If the directory doesn't exist, creates it.
    """
    while ' ' in output_directory:
        print("\nWARNING: The output directory path contains spaces, which can cause issues with upload operations.")
        print("    Current proposed path: {}".format(output_directory))
        new_path = input("Please enter a new path for the output directory: ")
        output_directory = new_path.strip()  # Remove leading/trailing spaces
    
    # Check if the directory exists, if not, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print("INFO: Created output directory: {}".format(output_directory))
    
    return output_directory

def get_output_directory(config):
    # Retrieve desired default output file path from config 
    output_directory = config.get('outputFilePath', '').strip()
    # BUG (Low SFTP) Add WinSCP validation because of the mishandling of spaces in paths. (This shouldn't need to exist.)
    if not output_directory:
        print("Output file path is not specified in the configuration.")
        output_directory = input("Please enter a valid output directory path: ").strip()
    
    # Validate the directory path (checks for spaces and existence)
    output_directory = winscp_validate_output_directory(output_directory)
    
    if not os.path.isdir(output_directory):
        print("Output directory does not exist or is not accessible. Please check the configuration.")
        return None
    
    return output_directory