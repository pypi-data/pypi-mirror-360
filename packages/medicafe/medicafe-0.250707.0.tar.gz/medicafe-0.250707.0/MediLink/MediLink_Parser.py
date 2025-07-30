# MediLink_Parser.py

import re

def parse_era_content(content, debug=False):
    extracted_data = []
    normalized_content = content.replace('~\n', '~')
    lines = normalized_content.split('~')

    record = {}
    check_eft, payer_address = None, None
    allowed_amount, write_off, patient_responsibility, adjustment_amount = 0, 0, 0, 0
    is_payer_section = False

    for line in lines:
        segments = line.split('*')

        if segments[0] == 'TRN' and len(segments) > 2:
            check_eft = segments[2]

        if segments[0] == 'N1':
            if segments[1] == 'PR':
                is_payer_section = True
            elif segments[1] == 'PE':
                is_payer_section = False

        if is_payer_section and segments[0] == 'N3' and len(segments) > 1:
            payer_address = segments[1]

        if segments[0] == 'CLP' and len(segments) >= 5:
            if record:
                if adjustment_amount == 0 and (write_off > 0 or patient_responsibility > 0):
                    adjustment_amount = write_off + patient_responsibility

                record.update({
                    'Payer Address': payer_address,
                    'Allowed Amount': allowed_amount,
                    'Write Off': write_off,
                    'Patient Responsibility': patient_responsibility,
                    'Adjustment Amount': adjustment_amount,
                })
                extracted_data.append(record)

                allowed_amount, write_off, patient_responsibility, adjustment_amount = 0, 0, 0, 0

            record = {
                'Check EFT': check_eft,
                'Chart Number': segments[1],
                'Payer Address': payer_address,
                'Amount Paid': segments[4],
                'Charge': segments[3],
            }

        elif segments[0] == 'CAS':
            if segments[1] == 'CO':
                write_off += float(segments[3])
            elif segments[1] == 'PR':
                patient_responsibility += float(segments[3])
            elif segments[1] == 'OA':
                adjustment_amount += float(segments[3])

        elif segments[0] == 'AMT' and segments[1] == 'B6':
            allowed_amount += float(segments[2])

        elif segments[0] == 'DTM' and (segments[1] == '232' or segments[1] == '472'):
            record['Date of Service'] = segments[2]

    if record:
        if adjustment_amount == 0 and (write_off > 0 or patient_responsibility > 0):
            adjustment_amount = write_off + patient_responsibility
        record.update({
            'Allowed Amount': allowed_amount,
            'Write Off': write_off,
            'Patient Responsibility': patient_responsibility,
            'Adjustment Amount': adjustment_amount,
        })
        extracted_data.append(record)

    if debug:
        print("Parsed ERA Content:")
        for data in extracted_data:
            print(data)

    return extracted_data

def parse_277_content(content, debug=False):
    segments = content.split('~')
    records = []
    current_record = {}
    for segment in segments:
        parts = segment.split('*')
        if parts[0] == 'HL':
            if current_record:
                records.append(current_record)
                current_record = {}
        elif parts[0] == 'NM1':
            if parts[1] == 'QC':
                current_record['Patient'] = parts[3] + ' ' + parts[4]
            elif parts[1] == '41':
                current_record['Clearing House'] = parts[3]
            elif parts[1] == 'PR':
                current_record['Payer'] = parts[3]
        elif parts[0] == 'TRN':
            current_record['Claim #'] = parts[2]
        elif parts[0] == 'STC':
            current_record['Status'] = parts[1]
            if len(parts) > 4:
                current_record['Paid'] = parts[4]
        elif parts[0] == 'DTP':
            if parts[1] == '472':
                current_record['Serv.'] = parts[3]
            elif parts[1] == '050':
                current_record['Proc.'] = parts[3]
        elif parts[0] == 'AMT':
            if parts[1] == 'YU':
                current_record['Charged'] = parts[2]

    if current_record:
        records.append(current_record)

    if debug:
        print("Parsed 277 Content:")
        for record in records:
            print(record)

    return records

def parse_277IBR_content(content, debug=False):
    return parse_277_content(content, debug)

def parse_277EBR_content(content, debug=False):
    return parse_277_content(content, debug)

def parse_dpt_content(content, debug=False):
    extracted_data = []
    lines = content.splitlines()
    record = {}
    for line in lines:
        if 'Patient Account Number:' in line:
            if record:
                extracted_data.append(record)
            record = {}
        parts = line.split(':')
        if len(parts) == 2:
            key, value = parts[0].strip(), parts[1].strip()
            record[key] = value
    if record:
        extracted_data.append(record)

    if debug:
        print("Parsed DPT Content:")
        for data in extracted_data:
            print(data)

    return extracted_data

def parse_ebt_content(content, debug=False):
    extracted_data = []  # List to hold all extracted records
    lines = content.splitlines()  # Split the content into individual lines
    record = {}  # Dictionary to hold the current record being processed

    # Regular expression pattern to match key-value pairs in the format "Key: Value"
    key_value_pattern = re.compile(r'([^:]+):\s*(.+?)(?=\s{2,}[^:]+?:|$)')

    for line in lines:
        # Check for the start of a new record based on the presence of 'Patient Name'
        if 'Patient Name:' in line and record:
            ebt_post_processor(record)  # Process the current record before adding it to the list
            extracted_data.append(record)  # Add the completed record to the list
            record = {}  # Reset the record for the next entry

        # Find all key-value pairs in the current line
        matches = key_value_pattern.findall(line)
        for key, value in matches:
            key = key.strip()  # Remove leading/trailing whitespace from the key
            value = value.strip()  # Remove leading/trailing whitespace from the value
            record[key] = value  # Add the key-value pair to the current record

    # Process and add the last record if it exists
    if record:
        ebt_post_processor(record)  # Final processing of the last record
        extracted_data.append(record)  # Add the last record to the list

    # Debug output to show parsed data if debugging is enabled
    if debug:
        print("Parsed EBT Content:")
        for data in extracted_data:
            print(data)

    return extracted_data  # Return the list of extracted records

def ebt_post_processor(record):
    # Process the 'Message Initiator' field to separate it from 'Message Type'
    if 'Message Initiator' in record and 'Message Type:' in record['Message Initiator']:
        parts = record['Message Initiator'].split('Message Type:')  # Split the string into parts
        record['Message Initiator'] = parts[0].strip()  # Clean up the 'Message Initiator'
        record['Message Type'] = parts[1].strip()  # Clean up the 'Message Type'

def parse_ibt_content(content, debug=False):
    extracted_data = []
    lines = content.splitlines()
    record = {}
    for line in lines:
        if 'Submitter Batch ID:' in line:
            if record:
                extracted_data.append(record)
            record = {}
        parts = line.split(':')
        if len(parts) == 2:
            key, value = parts[0].strip(), parts[1].strip()
            record[key] = value
    if record:
        extracted_data.append(record)

    if debug:
        print("Parsed IBT Content:")
        for data in extracted_data:
            print(data)

    return extracted_data