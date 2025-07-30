# MediCafe

MediCafe is a specialized Python package designed to automate and enhance administrative tasks in medical practices using Medisoft. It features two primary components: **MediBot** and **MediLink**, which work together to streamline patient data entry and claims submission processes. This package is particularly tailored for environments running Windows XP with Python 3.4.4.

## Features

### Automated Data Entry
MediCafe utilizes **AutoHotkey scripting** to automate the entry of patient information into Medisoft. This feature significantly reduces the time and effort required for manual data entry, minimizing human error and improving operational efficiency.

### Claims Submission Automation
The MediLink component automates the submission of 837p medical claims to various insurance providers via **APIs** and also using **WinSCP** for secure file transfers. It supports dynamic configurations for multiple endpoints, allowing for seamless integration with different payer systems with easy setup and management of custom 837p headers and trailers. This automation ensures timely and accurate claims processing, enhancing revenue cycle management for healthcare providers.

### Crosswalk Setup Tooling
MediCafe includes internal tooling to assist in setting up a **crosswalk** with referential data for payer IDs, diagnostic codes, and other essential mappings. This feature simplifies the process of aligning data formats and identifiers across different systems, ensuring consistency and accuracy in data handling.

## Installation

MediCafe can be easily installed via pip:
```bash
pip install medicafe
```

### Configuration
A custom configuration file is required for each environment and provider. This file must be set up to define paths, mappings, and other necessary parameters specific to the user's setup.

## Entry Point
The primary entry point for running MediCafe is through the **MediBot** batch file:
```bash
MediBot.bat
```

## Known Bugs
- **Endpoint Persistence**: Issues with endpoint update persistence when user adjustments are made.
- **Insurance Mode Glitches**: Certain insurance modes may not adjust data correctly, requiring manual intervention.
- **Manual Entry Requirements**: Some processes may require manual entries to handle off-nominal conditions, as indicated by comments in the codebase.

## Future Work
Future enhancements and features can be identified through TODO comments and other annotations in the codebase. These may include:
- Improvements to the crosswalk setup process.
- Additional automation features for data entry and claims processing.
- Enhancements to user interaction and error handling mechanisms.

### Developer Info:
- Name: Daniel Vidaud
- GitHub: [\[Your GitHub Profile\]](https://github.com/katanada2)
- Email: daniel@personalizedtransformations.com
- LinkedIn: [\[Your LinkedIn Profile\]](https://www.linkedin.com/in/dvidaud/)

### Contribution Guideline:
Contributions are welcome! If you'd like to contribute, please follow the steps below:
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

### Disclaimer:
MediCafe is developed as an open-source project. While we strive to provide a reliable and effective system, the developers are not responsible for any discrepancies or issues that may arise from its use. Always ensure data confidentiality and compliance with healthcare regulations.