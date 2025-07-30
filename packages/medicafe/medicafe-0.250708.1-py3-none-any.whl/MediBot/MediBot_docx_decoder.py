#MediBot_docx_decoder.py
from datetime import datetime
from collections import OrderedDict
import os, re, sys, zipfile
from docx import Document
from lxml import etree

# Add parent directory of the project to the Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

try:
    import MediLink_ConfigLoader
except ImportError:
    from MediLink import MediLink_ConfigLoader


def parse_docx(filepath, surgery_dates):  # Accept surgery_dates as a parameter
    try:
        doc = Document(filepath)  # Open the .docx file
    except Exception as e:
        MediLink_ConfigLoader.log("Error opening document: {}".format(e), level="ERROR")  # Log error
        return {}

    patient_data = OrderedDict()  # Initialize OrderedDict to store data
    MediLink_ConfigLoader.log("Extracting Date of Service from {}".format(filepath), level="DEBUG")
    
    date_of_service = extract_date_of_service(filepath)  # Extract date of service
    MediLink_ConfigLoader.log("Date of Service recorded as: {}".format(date_of_service), level="DEBUG")

    # Convert date_of_service to match the format of surgery_dates
    date_of_service = datetime.strptime(date_of_service, '%m-%d-%Y')  # Convert to datetime object
    # Check if the date_of_service is in the passed surgery_dates
    if date_of_service not in surgery_dates:  # Direct comparison with datetime objects
        MediLink_ConfigLoader.log("Date of Service {} not found in provided surgery dates. Skipping document.".format(date_of_service), level="DEBUG")
        return {}  # Early exit if date is not found
    
    MediLink_ConfigLoader.log("Date of Service {} found in surgery dates. Proceeding with parsing of the document.".format(date_of_service), level="DEBUG")  # Log that date of service was found
    # Convert back to MM-DD-YYYY format. 
    # TODO in the future, maybe just do the treatment to surgery_dates, no need to convert back and forth..
    date_of_service = date_of_service.strftime('%m-%d-%Y')  

    for table in doc.tables:  # Iterate over tables in the document
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if len(cells) > 4 and cells[3].startswith('#'):
                try:
                    patient_id = parse_patient_id(cells[3])
                    diagnosis_code = parse_diagnosis_code(cells[4])
                    left_or_right_eye = parse_left_or_right_eye(cells[4])
                    femto_yes_or_no = parse_femto_yes_or_no(cells[4])

                    if patient_id not in patient_data:
                        patient_data[patient_id] = {}

                    if date_of_service in patient_data[patient_id]:
                        MediLink_ConfigLoader.log("Duplicate entry for patient ID {} on date {}. Skipping.".format(patient_id, date_of_service), level="WARNING")
                    else:
                        patient_data[patient_id][date_of_service] = [diagnosis_code, left_or_right_eye, femto_yes_or_no]
                except Exception as e:
                    MediLink_ConfigLoader.log("Error processing row: {}. Error: {}".format(cells, e), level="ERROR")
    
    # Validation steps
    validate_unknown_entries(patient_data)
    validate_diagnostic_code(patient_data)
    
    return patient_data


def validate_unknown_entries(patient_data):
    for patient_id, dates in list(patient_data.items()):
        for date, details in list(dates.items()):
            if 'Unknown' in details:
                warning_message = "Warning: 'Unknown' entry found. Patient ID: {}, Date: {}, Details: {}".format(patient_id, date, details)
                MediLink_ConfigLoader.log(warning_message, level="WARNING")
                del patient_data[patient_id][date]
        if not patient_data[patient_id]:  # If no dates left for the patient, remove the patient
            del patient_data[patient_id]


def validate_diagnostic_code(patient_data):
    for patient_id, dates in patient_data.items():
        for date, details in dates.items():
            diagnostic_code, eye, _ = details
            if diagnostic_code[-1].isdigit():
                if eye == 'Left' and not diagnostic_code.endswith('2'):
                    log_and_warn(patient_id, date, diagnostic_code, eye)
                elif eye == 'Right' and not diagnostic_code.endswith('1'):
                    log_and_warn(patient_id, date, diagnostic_code, eye)


def log_and_warn(patient_id, date, diagnostic_code, eye):
    warning_message = (
        "Warning: Mismatch found for Patient ID: {}, Date: {}, "
        "Diagnostic Code: {}, Eye: {}".format(patient_id, date, diagnostic_code, eye)
    )
    MediLink_ConfigLoader.log(warning_message, level="WARNING")


def extract_date_of_service(docx_path, use_in_memory=True):
    extract_to = "extracted_docx_debug"
    in_memory_result = None
    directory_based_result = None

    # Log the selected approach
    if use_in_memory:
        MediLink_ConfigLoader.log("Using In-Memory extraction approach for Surgery Schedule.", level="INFO")
    else:
        MediLink_ConfigLoader.log("Using Directory-Based extraction approach for Surgery Schedule.", level="INFO")

    # Directory-Based Extraction
    if not use_in_memory:  # Only perform directory-based extraction if in-memory is not selected
        try:
            if not os.path.exists(extract_to):
                os.makedirs(extract_to)
                MediLink_ConfigLoader.log("Created extraction directory: {}".format(extract_to), level="DEBUG")
            
            with zipfile.ZipFile(docx_path, 'r') as docx:
                MediLink_ConfigLoader.log("Opened DOCX file: {}".format(docx_path), level="DEBUG")
                docx.extractall(extract_to)
                MediLink_ConfigLoader.log("Extracted DOCX to: {}".format(extract_to), level="DEBUG")
            
            file_path = find_text_in_xml(extract_to, "Surgery Schedule")
            if file_path:
                MediLink_ConfigLoader.log("Found XML file with target text: {}".format(file_path), level="DEBUG")
                directory_based_result = extract_date_from_file(file_path)
                MediLink_ConfigLoader.log("Directory-Based Extraction Result: {}".format(directory_based_result), level="DEBUG")
            else:
                MediLink_ConfigLoader.log("Target text 'Surgery Schedule' not found in any XML files.", level="WARNING")
        except zipfile.BadZipFile as e:
            MediLink_ConfigLoader.log("BadZipFile Error opening DOCX file {}: {}".format(docx_path, e), level="ERROR")
        except Exception as e:
            MediLink_ConfigLoader.log("Error opening DOCX file {}: {}".format(docx_path, e), level="ERROR")

    # In-Memory Extraction  // Single-Pass Processing is typically more efficient in terms of both time and memory compared to list creation for header isolation.
    if use_in_memory:  # Only perform in-memory extraction if selected
        try:
            with zipfile.ZipFile(docx_path, 'r') as docx:
                MediLink_ConfigLoader.log("Opened DOCX file for In-Memory extraction: {}".format(docx_path), level="DEBUG")
                for file_info in docx.infolist():
                    if file_info.filename.endswith('.xml'):
                        MediLink_ConfigLoader.log("Processing XML file in-memory: {}".format(file_info.filename), level="DEBUG")
                        with docx.open(file_info) as file:
                            try:
                                xml_content = file.read()  # Read the entire XML content
                                MediLink_ConfigLoader.log("Read XML content from {}".format(file_info.filename), level="DEBUG")
                                if "Surgery Schedule" in xml_content.decode('utf-8', errors='ignore'):
                                    MediLink_ConfigLoader.log("Found 'Surgery Schedule' in file: {}".format(file_info.filename), level="DEBUG")
                                    in_memory_result = extract_date_from_content(xml_content)
                                    MediLink_ConfigLoader.log("In-Memory Extraction Result from {}: {}".format(file_info.filename, in_memory_result), level="DEBUG")
                                    break  # Stop after finding the first relevant file
                            except Exception as e:
                                MediLink_ConfigLoader.log("Error parsing XML file {} (In-Memory): {}".format(file_info.filename, e), level="ERROR")
                
                if in_memory_result is None:
                    MediLink_ConfigLoader.log("Target text 'Surgery Schedule' not found in any XML files (In-Memory).", level="WARNING")
        except zipfile.BadZipFile as e:
            MediLink_ConfigLoader.log("BadZipFile Error opening DOCX file for In-Memory extraction {}: {}".format(docx_path, e), level="ERROR")
        except Exception as e:
            MediLink_ConfigLoader.log("Error during In-Memory extraction of DOCX file {}: {}".format(docx_path, e), level="ERROR")

    # Clean up the extracted directory if it exists
    try:
        if os.path.exists(extract_to):
            remove_directory(extract_to)
            MediLink_ConfigLoader.log("Cleaned up extracted files in: {}".format(extract_to), level="DEBUG")
    except Exception as e:
        MediLink_ConfigLoader.log("Error cleaning up extraction directory {}: {}".format(extract_to, e), level="ERROR")

    # Decide which result to return (prefer in-memory if available)
    if in_memory_result:
        return in_memory_result
    elif directory_based_result:
        return directory_based_result
    else:
        return None

def find_text_in_xml(extract_dir, target_text):
    target_pattern = re.compile(re.escape(target_text), re.IGNORECASE)
    for root_dir, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.xml') and file != '[Content_Types].xml':  # Skip Content_Types.xml
                file_path = os.path.join(root_dir, file)
                try:
                    tree = etree.parse(file_path)
                    root = tree.getroot()
                    namespaces = root.nsmap
                    MediLink_ConfigLoader.log("Processing file: {}".format(file_path), level="DEBUG")
                    for elem in root.xpath('//w:t', namespaces=namespaces):
                        if elem.text and target_pattern.search(elem.text):
                            MediLink_ConfigLoader.log("Found target text '{}' in file: {}".format(target_text, file_path), level="DEBUG")
                            return file_path
                except etree.XMLSyntaxError as e:
                    MediLink_ConfigLoader.log("XMLSyntaxError parsing file {}: {}".format(file_path, e), level="ERROR")
                except Exception as e:
                    MediLink_ConfigLoader.log("Error parsing XML file {}: {}".format(file_path, e), level="ERROR")
    MediLink_ConfigLoader.log("Target text '{}' not found in any XML files within directory: {}".format(target_text, extract_dir), level="WARNING")
    return None

def extract_date_from_file(file_path):
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()
        collected_text = []
        
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}  # Hardcoded for XP handling BUG
        for elem in root.xpath('//w:t', namespaces=namespaces):
            if elem.text:
                collected_text.append(elem.text.strip())
        
        combined_text = ' '.join(collected_text)
        combined_text = reassemble_year(combined_text)  # Fix OCR splitting years
        combined_text = normalize_text(combined_text)  # Normalize abbreviations
        combined_text = re.sub(r',', '', combined_text)  # Remove commas if they exist

        # Log the combined text
        MediLink_ConfigLoader.log("Combined text from file '{}': {}".format(file_path, combined_text[:200]), level="DEBUG")
        
        day_week_pattern = r"(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)"
        month_day_pattern = r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER) \d{1,2}"
        year_pattern = r"\d{4}"

        day_of_week = re.search(day_week_pattern, combined_text, re.IGNORECASE)
        month_day = re.search(month_day_pattern, combined_text, re.IGNORECASE)
        year_match = re.search(year_pattern, combined_text, re.IGNORECASE)

        # Log the results of the regex searches
        MediLink_ConfigLoader.log("Day of week found: {}".format(day_of_week.group() if day_of_week else 'None'), level="DEBUG")
        MediLink_ConfigLoader.log("Month and day found: {}".format(month_day.group() if month_day else 'None'), level="DEBUG")
        MediLink_ConfigLoader.log("Year found: {}".format(year_match.group() if year_match else 'None'), level="DEBUG")
        
        if day_of_week and month_day and year_match:
            date_str = "{} {} {}".format(day_of_week.group(), month_day.group(), year_match.group())
            try:
                date_obj = datetime.strptime(date_str, '%A %B %d %Y')
                extracted_date = date_obj.strftime('%m-%d-%Y')
                MediLink_ConfigLoader.log("Extracted date: {}".format(extracted_date), level="DEBUG")
                return extracted_date
            except ValueError as e:
                MediLink_ConfigLoader.log("Error converting date: {}. Error: {}".format(date_str, e), level="ERROR")
        else:
            MediLink_ConfigLoader.log(
                "Date components not found or incomplete. Combined text: '{}', Day of week: {}, Month and day: {}, Year: {}".format(
                    combined_text,
                    day_of_week.group() if day_of_week else 'None',
                    month_day.group() if month_day else 'None',
                    year_match.group() if year_match else 'None'
                ), level="WARNING"
            )
    except etree.XMLSyntaxError as e:
        MediLink_ConfigLoader.log("XMLSyntaxError in extract_date_from_file '{}': {}".format(file_path, e), level="ERROR")
    except Exception as e:
        MediLink_ConfigLoader.log("Error extracting date from file '{}': {}".format(file_path, e), level="ERROR")

    return None


def extract_date_from_content(xml_content):
    try:
        # Parse the XML content into an ElementTree
        tree = etree.fromstring(xml_content)
        root = tree  # root is already the root element in this case
        collected_text = []

        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        MediLink_ConfigLoader.log("Using namespaces: {}".format(namespaces), level="DEBUG")

        # Extract text from all <w:t> elements
        for elem in root.xpath('//w:t', namespaces=namespaces):
            if elem.text:
                collected_text.append(elem.text.strip())

        # Log the collected text snippets
        MediLink_ConfigLoader.log("Collected text snippets: {}".format(collected_text), level="DEBUG")

        combined_text = ' '.join(collected_text)
        combined_text = reassemble_year(combined_text)  # Fix OCR splitting years
        combined_text = normalize_text(combined_text)    # Normalize abbreviations
        combined_text = re.sub(r',', '', combined_text)   # Remove commas if they exist

        # Log the combined text
        MediLink_ConfigLoader.log("Combined text: {}".format(combined_text[:200]), level="DEBUG")  # Log first 200 characters

        day_week_pattern = r"(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)"
        month_day_pattern = r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER) \d{1,2}"
        year_pattern = r"\d{4}"

        day_of_week = re.search(day_week_pattern, combined_text, re.IGNORECASE)
        month_day = re.search(month_day_pattern, combined_text, re.IGNORECASE)
        year_match = re.search(year_pattern, combined_text, re.IGNORECASE)

        MediLink_ConfigLoader.log("Day of week found: {}".format(day_of_week.group() if day_of_week else 'None'), level="DEBUG")
        MediLink_ConfigLoader.log("Month and day found: {}".format(month_day.group() if month_day else 'None'), level="DEBUG")
        MediLink_ConfigLoader.log("Year found: {}".format(year_match.group() if year_match else 'None'), level="DEBUG")

        if day_of_week and month_day and year_match:
            date_str = "{} {} {}".format(day_of_week.group(), month_day.group(), year_match.group())
            try:
                date_obj = datetime.strptime(date_str, '%A %B %d %Y')
                extracted_date = date_obj.strftime('%m-%d-%Y')
                MediLink_ConfigLoader.log("Extracted date: {}".format(extracted_date), level="DEBUG")
                return extracted_date
            except ValueError as e:
                MediLink_ConfigLoader.log("Error converting date: {}. Error: {}".format(date_str, e), level="ERROR")
        else:
            MediLink_ConfigLoader.log(
                "Date components not found or incomplete. Combined text: '{}', Day of week: {}, Month and day: {}, Year: {}".format(
                    combined_text,
                    day_of_week.group() if day_of_week else 'None',
                    month_day.group() if month_day else 'None',
                    year_match.group() if year_match else 'None'
                ), level="WARNING"
            )
    except etree.XMLSyntaxError as e:
        MediLink_ConfigLoader.log("XMLSyntaxError in extract_date_from_content: {}".format(e), level="ERROR")
    except Exception as e:
        MediLink_ConfigLoader.log("Error extracting date from content: {}".format(e), level="ERROR")

    return None


def remove_directory(path):
    if os.path.exists(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                    MediLink_ConfigLoader.log("Removed file: {}".format(os.path.join(root, name)), level="DEBUG")
                except Exception as e:
                    MediLink_ConfigLoader.log("Error removing file {}: {}".format(os.path.join(root, name), e), level="ERROR")
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                    MediLink_ConfigLoader.log("Removed directory: {}".format(os.path.join(root, name)), level="DEBUG")
                except Exception as e:
                    MediLink_ConfigLoader.log("Error removing directory {}: {}".format(os.path.join(root, name), e), level="ERROR")
        try:
            os.rmdir(path)
            MediLink_ConfigLoader.log("Removed extraction root directory: {}".format(path), level="DEBUG")
        except Exception as e:
            MediLink_ConfigLoader.log("Error removing root directory {}: {}".format(path, e), level="ERROR")


def normalize_text(text):
    month_map = {
        'JAN': 'JANUARY', 'FEB': 'FEBRUARY', 'MAR': 'MARCH', 'APR': 'APRIL', 
        'MAY': 'MAY', 'JUN': 'JUNE', 'JUL': 'JULY', 'AUG': 'AUGUST', 
        'SEP': 'SEPTEMBER', 'OCT': 'OCTOBER', 'NOV': 'NOVEMBER', 'DEC': 'DECEMBER'
    }
    day_map = {
        'MON': 'MONDAY', 'TUE': 'TUESDAY', 'WED': 'WEDNESDAY', 'THU': 'THURSDAY', 
        'FRI': 'FRIDAY', 'SAT': 'SATURDAY', 'SUN': 'SUNDAY'
    }
    
    for abbr, full in month_map.items():
        text = re.sub(r'\b' + abbr + r'\b', full, text, flags=re.IGNORECASE)
    for abbr, full in day_map.items():
        text = re.sub(r'\b' + abbr + r'\b', full, text, flags=re.IGNORECASE)
    
    return text


def reassemble_year(text):
    # First, handle the most common case where a 4-digit year is split as (3,1), (1,3), or (2,2)
    text = re.sub(r'(\d{3}) (\d{1})', r'\1\2', text)
    text = re.sub(r'(\d{1}) (\d{3})', r'\1\2', text)
    text = re.sub(r'(\d{2}) (\d{2})', r'\1\2', text)
    
    # Handle the less common cases where the year might be split as (1,1,2) or (2,1,1) or (1,2,1)
    parts = re.findall(r'\b(\d{1,2})\b', text)
    if len(parts) >= 4:
        for i in range(len(parts) - 3):
            candidate = ''.join(parts[i:i + 4])
            if len(candidate) == 4 and candidate.isdigit():
                combined_year = candidate
                pattern = r'\b' + r'\s+'.join(parts[i:i + 4]) + r'\b'
                text = re.sub(pattern, combined_year, text)
                break
    
    return text


def parse_patient_id(text):
    try:
        return text.split()[0].lstrip('#')  # Extract patient ID number (removing the '#')
    except Exception as e:
        MediLink_ConfigLoader.log("Error parsing patient ID: {}. Error: {}".format(text, e), level="ERROR")
        return None


def parse_diagnosis_code(text):
    try:
        # Regular expression to find all ICD-10 codes starting with 'H' and containing a period
        pattern = re.compile(r'H\d{2}\.\d+')
        matches = pattern.findall(text)
        
        if matches:
            return matches[0]  # Return the first match
        else:
            # Fallback to original method if no match is found
            if '(' in text and ')' in text:  # Extract the diagnosis code before the '/'
                full_code = text[text.index('(')+1:text.index(')')]
                return full_code.split('/')[0]
            return text.split('/')[0]
    
    except Exception as e:
        MediLink_ConfigLoader.log("Error parsing diagnosis code: {}. Error: {}".format(text, e), level="ERROR")
        return "Unknown"


def parse_left_or_right_eye(text):
    try:
        if 'LEFT EYE' in text.upper():
            return 'Left'
        elif 'RIGHT EYE' in text.upper():
            return 'Right'
        else:
            return 'Unknown'
    except Exception as e:
        MediLink_ConfigLoader.log("Error parsing left or right eye: {}. Error: {}".format(text, e), level="ERROR")
        return 'Unknown'


def parse_femto_yes_or_no(text):
    try:
        if 'FEMTO' in text.upper():
            return True
        else:
            return False
    except Exception as e:
        MediLink_ConfigLoader.log("Error parsing femto yes or no: {}. Error: {}".format(text, e), level="ERROR")
        return False


def rotate_docx_files(directory):
    # List all files in the directory
    files = os.listdir(directory)

    # Filter files that contain "DR" and "SS" in the filename
    filtered_files = [file for file in files if "DR" in file and "SS" in file]

    # Iterate through filtered files
    for filename in filtered_files:
        filepath = os.path.join(directory, filename)
        # Parse each document and print the resulting dictionary
        patient_data_dict = parse_docx(filepath)
        print("Data from file '{}':".format(filename))
        import pprint
        pprint.pprint(patient_data_dict)
        print()


def main():
    # Call the function with the directory containing your .docx files
    directory = "C:\\Users\\danie\\Downloads\\"
    rotate_docx_files(directory)


if __name__ == "__main__":
    main()