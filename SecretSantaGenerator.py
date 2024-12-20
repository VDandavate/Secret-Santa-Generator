#!/usr/bin/env python3
"""
Secret Santa Generator
====================

A robust implementation of a Secret Santa matching system with comprehensive validation,
retry logic, and detailed debugging capabilities.

Features:
---------
- Input validation with detailed error reporting
- Multiple matching strategies with intelligent retry logic
- Comprehensive debug logging
- Family and category-based matching constraints
- Progress indication and user-friendly output

Input File Format:
----------------
CSV file with semicolon-separated values containing:
    email;firstName;lastName;family;category

Example:
    john.doe@example.com;John;Doe;Family1;Adults
    jane.smith@example.com;Jane;Smith;Family2;Adults
    bobby.child@example.com;Bobby;Child;Family3;Kids

Usage:
------
1. Regular execution:
    python SecretSantaGenerator.py participants.csv

2. Run unit tests:
    python SecretSantaGenerator.py --test

Author: [Your Name]
Date: December 2024
Version: 2.0
"""

import random
import sys
import re
from datetime import datetime
import time
import threading
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

def readInputFile(inputFilename):
    """
    Reads the input file and returns a dictionary of participants with their details.
    Format of the input file: email;firstName;lastName;family;category
    """
    participants = {}
    with open(inputFilename, 'r') as file:
        for line in file:
            email, firstName, lastName, family, category = line.strip().split(';')
            participants[email] = {
                'firstName': firstName,
                'lastName': lastName,
                'family': family,
                'category': category
            }
    return participants

def validateEmail(email: str) -> bool:
    """
    Validates email format using regex pattern matching.

    Args:
        email (str): Email address to validate

    Returns:
        bool: True if email format is valid, False otherwise

    Example:
        >>> validateEmail("john.doe@example.com")
        True
        >>> validateEmail("invalid.email")
        False
    """
    # RFC 5322 compliant email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validateInputData(participants: Dict, debugFile: str) -> Tuple[bool, str]:
    """
    Performs comprehensive validation of input participant data.

    Validation checks include:
    - Minimum participant count
    - Email format and uniqueness
    - Required field presence
    - Category distribution
    - Family distribution within categories

    Args:
        participants (Dict): Dictionary of participant information
        debugFile (str): Path to debug log file

    Returns:
        Tuple[bool, str]: (isValid, message)
            - isValid: True if all validation passes, False otherwise
            - message: Descriptive message about validation result or error
    """
    writeDebugInfo(debugFile, "INFO", "Starting comprehensive input data validation")

    # Check minimum participant count
    if len(participants) < 2:
        writeDebugInfo(debugFile, "ERROR", "Insufficient participants (minimum 2 required)")
        return False, "Need at least 2 participants"

    # Initialize tracking containers
    seenEmails = set()
    categoryGroups = defaultdict(list)
    familyGroups = defaultdict(list)

    # Validate individual participant records
    for email, details in participants.items():
        # Email format validation
        if not validateEmail(email):
            writeDebugInfo(debugFile, "ERROR", f"Invalid email format: {email}")
            return False, f"Invalid email format: {email}"

        # Check for duplicate emails
        if email in seenEmails:
            writeDebugInfo(debugFile, "ERROR", f"Duplicate email detected: {email}")
            return False, f"Duplicate email found: {email}"
        seenEmails.add(email)

        # Validate required fields
        requiredFields = ['firstName', 'lastName', 'family', 'category']
        for field in requiredFields:
            if not details.get(field):
                writeDebugInfo(debugFile, "ERROR", f"Missing required field: {field} for {email}")
                return False, f"Missing {field} for {email}"

        # Build category and family distribution data
        categoryGroups[details['category']].append(email)
        familyGroups[details['family']].append(email)

    # Validate category distributions
    for category, members in categoryGroups.items():
        # Check minimum category size
        if len(members) < 2:
            writeDebugInfo(debugFile, "ERROR",
                f"Category {category} has insufficient participants (minimum 2 required)")
            return False, f"Category {category} has less than 2 participants"

        # Analyze family distribution within category
        categoryFamilies = defaultdict(int)
        for email in members:
            family = participants[email]['family']
            categoryFamilies[family] += 1

            # Check if any family has too many members in category
            if categoryFamilies[family] > len(members) // 2:
                writeDebugInfo(debugFile, "ERROR",
                    f"Family {family} has {categoryFamilies[family]} members in category {category} "
                    f"(maximum allowed: {len(members) // 2})")
                return False, f"Family {family} has too many members in category {category}"

    writeDebugInfo(debugFile, "SUCCESS",
        f"Input validation completed successfully for {len(participants)} participants "
        f"across {len(categoryGroups)} categories")
    return True, "Validation successful"

def writeDebugInfo(debugFile: str, messageType: str, message: str) -> None:
    """
    Writes formatted debug information to the specified file.

    Args:
        debugFile (str): Path to debug log file
        messageType (str): Type of message (INFO, WARNING, ERROR, SUCCESS)
        message (str): Debug message content

    Format:
        [TIMESTAMP] TYPE: Message

    Example:
        [2024-12-20 14:30:45] INFO: Starting matching process
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(debugFile, 'a') as dbg:
        dbg.write(f"[{timestamp}] {messageType}: {message}\n")

def matchSecretSantaInCategory(
    participants: Dict,
    debugFile: str,
    attempt: int
) -> Optional[Dict[str, str]]:
    """
    Attempts to match Secret Santa participants within a single category.
    Uses different matching strategies based on the attempt number.

    Matching Constraints:
    - No self-matching
    - No matching within the same family
    - Each person must give and receive exactly one gift

    Args:
        participants (Dict): Dictionary of participants in the category
        debugFile (str): Path to debug log file
        attempt (int): Current attempt number (affects matching strategy)

    Returns:
        Optional[Dict[str, str]]: Dictionary of sender->receiver matches,
                                 or None if matching fails

    Matching Strategies:
    - Attempt % 3 == 0: Complete random shuffle
    - Attempt % 3 == 1: Ordered approach with rotating start point
    - Attempt % 3 == 2: Reverse order approach
    """
    writeDebugInfo(debugFile, "INFO",
        f"Starting matching attempt {attempt} for {len(participants)} participants")

    # Get list of participant emails
    emails = list(participants.keys())

    # Apply matching strategy based on attempt number
    if attempt % 3 == 0:
        # Strategy 1: Complete random shuffle
        random.shuffle(emails)
        writeDebugInfo(debugFile, "INFO", "Using random shuffle strategy")
    elif attempt % 3 == 1:
        # Strategy 2: Ordered approach with rotating start point
        emails.sort()
        startPoint = attempt // 3 % len(emails)
        emails = emails[startPoint:] + emails[:startPoint]
        writeDebugInfo(debugFile, "INFO",
            f"Using ordered approach with start point {startPoint}")
    else:
        # Strategy 3: Reverse order approach
        emails.reverse()
        writeDebugInfo(debugFile, "INFO", "Using reverse order strategy")

    matches = {}
    remainingReceivers = emails.copy()

    # Attempt to find matches for each sender
    for sender in emails:
        senderDetails = participants[sender]

        # Find valid receivers (different person, different family)
        validReceivers = [
            r for r in remainingReceivers
            if r != sender  # No self-matching
            and participants[r]['family'] != senderDetails['family']  # Different family
        ]

        # Check if we have valid receivers
        if not validReceivers:
            writeDebugInfo(debugFile, "ERROR",
                f"No valid receiver found for {sender} "
                f"(Family: {senderDetails['family']}, "
                f"Remaining receivers: {len(remainingReceivers)})")
            return None

        # Select receiver randomly from valid options
        receiver = random.choice(validReceivers)
        matches[sender] = receiver
        remainingReceivers.remove(receiver)

        writeDebugInfo(debugFile, "INFO",
            f"Matched {sender} ({senderDetails['family']}) -> "
            f"{receiver} ({participants[receiver]['family']})")

    writeDebugInfo(debugFile, "SUCCESS",
        f"Successfully matched all {len(participants)} participants")
    return matches

def generateOutputFileName(inputFile: str) -> str:
    """
    Generates a unique output filename based on input filename and timestamp.

    Args:
        inputFile (str): Original input filename

    Returns:
        str: Generated output filename in format:
             {original_name}-Matched-{YYYYMMDDHHMMSS}.txt
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    baseName = inputFile.rsplit('.', 1)[0]
    return f"{baseName}-Matched-{timestamp}.txt"

def generateDebugFileName(inputFile):
    """
    Generates a unique debug filename based on input filename and timestamp.

    Args:
        inputFile (str): Original input filename

    Returns:
        str: Generated output filename in format:
             {original_name}-Debug-{YYYYMMDDHHMMSS}.txt
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    baseName = inputFile.rsplit('.', 1)[0]
    return f"{baseName}-Debug-{timestamp}.txt"

def main() -> bool:
    """
    Main execution function coordinating the Secret Santa generation process.

    Process Flow:
    1. Get and validate input file
    2. Set up debug logging
    3. Read and parse participant data
    4. Generate matches with retry logic
    5. Output results and write files

    Returns:
        bool: True if process completes successfully, False otherwise
    """
    try:
        # Get input file path
        if len(sys.argv) > 1 and sys.argv[1].lower() != '--test':
            inputFile = sys.argv[1]
        else:
            inputFile = input("Please enter the input file name: ")

        # Initialize debug logging
        debugFile = generateDebugFileName(inputFile)
        writeDebugInfo(debugFile, "INFO",
            f"Starting Secret Santa generation process for {inputFile}")

        # Read and parse input file
        try:
            participants = readInputFile(inputFile)
            writeDebugInfo(debugFile, "INFO",
                f"Successfully loaded {len(participants)} participants")
        except Exception as e:
            writeDebugInfo(debugFile, "ERROR", f"Failed to read input file: {str(e)}")
            print(f"Error reading input file: {str(e)}")
            return False

        # Show progress indicator
        spinThread = threading.Thread(target=showSpinner, daemon=True)
        spinThread.start()

        # Generate matches
        matches = matchSecretSanta(participants, debugFile)

        if matches:
            # Success path
            print("\nSecret Santa matching completed successfully!")

            # Display matches
            for sender, receiver in matches.items():
                senderDetails = participants[sender]
                receiverDetails = participants[receiver]
                print(
                    f"{senderDetails['firstName']} {senderDetails['lastName']} -> "
                    f"{receiverDetails['firstName']} {receiverDetails['lastName']}"
                )

            # Write output files
            outputFile = generateOutputFileName(inputFile)
            writeOutputFile(matches, participants, outputFile)
            print(f"\nOutput files generated:")
            print(f"- Matches: {outputFile}")
            print(f"- Debug log: {debugFile}")
            return True
        else:
            # Failure path
            print("\nFailed to generate valid Secret Santa matches")
            print(f"Please check {debugFile} for detailed error information")
            return False

    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        return False
    finally:
        # Clean up progress indicator
        if 'spinThread' in locals():
            spinThread.join(timeout=0.2)

if __name__ == "__main__":
    # Entry point - handle both regular execution and testing
    if len(sys.argv) > 1 and sys.argv[1].lower() == '--test':
        import unittest
        unittest.main(argv=['dummy'])
    else:
        success = main()
        sys.exit(0 if success else 1)
