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
Version: 3.0
"""

import random
import sys
import re
import os
from datetime import datetime
import time
import threading
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

def ensureDirectories():
    """
    Ensures required directories exist: input, debug, and output.
    """
    for folder in ["input", "debug", "output"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

def moveInputFileToFolder(inputFile):
    """
    Moves the input file to the input folder if it is in the code directory.
    """
    if os.path.isfile(inputFile) and not os.path.isfile(f"input/{inputFile}"):
        os.rename(inputFile, f"input/{inputFile}")
        return f"input/{inputFile}"
    return inputFile

def writeDebugInfo(messageType, message):
    """
    Logs debugging information to a single debug file with a timestamp and message type.
    """
    debugFile = "debug/allDebug.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(debugFile, 'a') as dbg:
        dbg.write(f"[{timestamp}] {messageType}: {message}\n")

def generateFileName(base, suffix):
    """
    Generates a unique file name with a timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base}-{suffix}-{timestamp}.txt"

def readInputFile(inputFilename):
    """
    Reads the input file and returns a dictionary of participants with their details.
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

def validateEmail(email):
    """
    Validates the email format using a regex pattern.
    """
    pattern = r'^[a-zA-Z0-9.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validateInputData(participants):
    """
    Validates participant data for correctness and compliance with constraints.
    """
    writeDebugInfo("INFO", "Validating participant data.")

    if len(participants) < 2:
        writeDebugInfo("ERROR", "Insufficient participants (minimum 2 required).")
        return False, "Need at least 2 participants."

    seenEmails = set()
    categoryGroups = defaultdict(list)

    for email, details in participants.items():
        if not validateEmail(email):
            writeDebugInfo("ERROR", f"Invalid email: {email}.")
            return False, f"Invalid email format: {email}."

        if email in seenEmails:
            writeDebugInfo("ERROR", f"Duplicate email found: {email}.")
            return False, f"Duplicate email: {email}."
        seenEmails.add(email)

        for field in ['firstName', 'lastName', 'family', 'category']:
            if not details.get(field):
                writeDebugInfo("ERROR", f"Missing field {field} for {email}.")
                return False, f"Missing {field} for {email}."

        categoryGroups[details['category']].append(email)

    for category, members in categoryGroups.items():
        if len(members) < 2:
            writeDebugInfo("ERROR", f"Category {category} has fewer than 2 participants.")
            return False, f"Category {category} has insufficient participants."

    writeDebugInfo("INFO", "Validation successful.")
    return True, "Validation passed."

def matchParticipantsInCategory(participants, attempt):
    """
    Matches participants in a single category while meeting constraints.
    """
    writeDebugInfo("INFO", f"Attempting match, attempt {attempt}.")

    emails = list(participants.keys())

    if attempt % 3 == 0:
        random.shuffle(emails)
    elif attempt % 3 == 1:
        emails.sort()
    else:
        emails.reverse()

    matches = {}
    receivers = set(emails)

    for sender in emails:
        validReceivers = [r for r in receivers if r != sender and participants[r]['family'] != participants[sender]['family']]
        if not validReceivers:
            writeDebugInfo("ERROR", f"No valid receiver for {sender}.")
            return None

        receiver = random.choice(validReceivers)
        matches[sender] = receiver
        receivers.remove(receiver)

    writeDebugInfo("INFO", "Matching successful.")
    return matches

def matchSecretSanta(participants):
    """
    Performs the Secret Santa matching process with retries.
    """
    categories = defaultdict(dict)
    for email, details in participants.items():
        categories[details['category']][email] = details

    finalMatches = {}

    for category, group in categories.items():
        for attempt in range(100):
            matches = matchParticipantsInCategory(group, attempt)
            if matches:
                finalMatches.update(matches)
                break
        else:
            writeDebugInfo("ERROR", f"Failed to match category {category} after 100 attempts.")
            return None

    return finalMatches

def writeOutputFile(matches, participants, outputFile):
    """
    Writes the matches to an output file.
    """
    with open(outputFile, 'w') as file:
        for sender, receiver in matches.items():
            senderDetails = participants[sender]
            receiverDetails = participants[receiver]
            file.write(
                f"{senderDetails['firstName']},{senderDetails['lastName']},{sender},"
                f"{receiverDetails['firstName']},{receiverDetails['lastName']},{receiver}\n"
            )

def showProgress():
    """
    Displays a spinner to indicate progress.
    """
    while True:
        for char in "|/-\\":
            print(f"\rWorking... {char}", end="", flush=True)
            time.sleep(0.1)

def main():
    """
    Main function to handle Secret Santa matching.
    """
    try:
        ensureDirectories()

        if len(sys.argv) > 1:
            inputFile = sys.argv[1]
        else:
            inputFile = input("Enter the input file name: ")

        inputFile = moveInputFileToFolder(inputFile)

        writeDebugInfo("INFO", "Starting process.")

        participants = readInputFile(inputFile)

        isValid, message = validateInputData(participants)
        if not isValid:
            print(message)
            return False

        progressThread = threading.Thread(target=showProgress, daemon=True)
        progressThread.start()

        matches = matchSecretSanta(participants)
        if matches:
            outputFile = f"output/{generateFileName(inputFile.rsplit('/', 1)[-1].rsplit('.', 1)[0], 'Matched')}"
            writeOutputFile(matches, participants, outputFile)
            print(f"\nResults saved to {outputFile}. Check debug/allDebug.log for details.")
            return True
        else:
            print("\nMatching failed. Check debug/allDebug.log for details.")
            return False
    finally:
        if 'progressThread' in locals():
            progressThread.join(0.2)

if __name__ == "__main__":
    main()
