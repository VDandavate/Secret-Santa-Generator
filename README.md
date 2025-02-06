# Secret Santa Generator

## Overview
The **Secret Santa Generator** is a Python-based application designed to create Secret Santa matches while adhering to specific constraints, such as category and family exclusions. It ensures a user-friendly experience with validation, debugging, and retry mechanisms.

---

## Features
- **Validation**: Ensures all participants meet the input criteria.
- **Constraints**: Matches are created within the same category, avoiding family matches.
- **Retry Mechanism**: Re-runs the matching process if constraints are not satisfied.
- **User Confirmation**: Displays matches for approval before saving to a file.
- **Debugging**: Comprehensive logs for every execution in a single debug file.
- **Directory Management**: Organizes input, debug, and output files into respective folders.
- **File Handling**: Automatically moves input files to the correct folder and generates organized output files.

---

## Prerequisites
- Python 3.7 or higher
- Operating system with support for Python execution

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Secret-Santa-Generator.git
   cd Secret-Santa-Generator
   ```
2. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage
### Running the Application
1. Place your participant file in the `input` folder.
2. Run the application:
   ```bash
   python SecretSantaGenerator.py input/Participants2024.csv
   ```

### Input File Format
The input file must be a CSV file with semicolon-separated values:
```csv
email;firstName;lastName;family;category
example1@example.com;John;Doe;Family1;Adults
example2@example.com;Jane;Smith;Family2;Kids
```

### Outputs
1. **Matches**: Saved in the `output` folder as a timestamped file.
2. **Debug Logs**: All logs are stored in `debug/allDebug.log`.

### Example
- **Input File**: `input/Participants2024.csv`
- **Output File**: `output/Participants2024-Matched-YYYYMMDDHHMMSS.txt`
- **Debug File**: `debug/allDebug.log`

---

## Code Structure
- **SecretSantaGenerator.py**: Main script for executing the application.
- **input/**: Directory for input files.
- **output/**: Directory for generated output files.
- **debug/**: Directory for debug logs.

---

## Contributions
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-branch-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature description"
   ```
4. Push the changes:
   ```bash
   git push origin feature-branch-name
   ```
5. Submit a pull request.

---

## License
This project is licensed under the MIT License. See `LICENSE` for more details.

---

## Support
If you encounter any issues, please open an issue on the GitHub repository.

Happy gifting! 🎁

