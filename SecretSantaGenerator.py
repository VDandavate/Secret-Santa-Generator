#!/usr/bin/env python3
"""
Secret Santa Generator
---------------------
A Python script that generates Secret Santa assignments while respecting family
and category constraints. The program ensures that no one is matched with someone
from their own family and participants are only matched within their category.

Input file format:
    CSV with columns: email;first_name;last_name;family;category

Usage:
    Run program: python SecretSantaGenerator.py [input_file.csv]
    Run tests:   python SecretSantaGenerator.py --test

Author: [Your Name]
Date: December 2024
"""

import random
import sys
from datetime import datetime
import itertools
import time
import unittest

def read_input_file(file_name):
    """
    Reads and parses the input CSV file containing participant information.

    Args:
        file_name (str): Path to the input CSV file

    Returns:
        dict: Dictionary of participants with their details
            Format: {
                'email@example.com': {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'family': 'Family1',
                    'category': 'Category1'
                }
            }

    Raises:
        FileNotFoundError: If the input file doesn't exist
        ValueError: If the CSV format is invalid
    """
    participants = {}
    with open(file_name, 'r') as file:
        for line in file:
            # Split the line by semicolon and strip whitespace
            email, first_name, last_name, family, category = [
                field.strip() for field in line.strip().split(';')
            ]
            participants[email] = {
                'first_name': first_name,
                'last_name': last_name,
                'family': family,
                'category': category
            }
    return participants

def match_secret_santa_in_category(participants):
    """
    Matches participants for Secret Santa within a single category.

    Args:
        participants (dict): Dictionary of participants in the same category

    Returns:
        dict: Mapping of givers to receivers, or None if matching fails
            Format: {'giver_email': 'receiver_email'}

    Note:
        This function ensures:
        - No one is matched with themselves
        - No one is matched with someone from their own family
        - Each person gives and receives exactly one gift
    """
    emails = list(participants.keys())
    random.shuffle(emails)  # Randomize the matching order
    matches = {}

    for sender in emails:
        sender_details = participants[sender]
        receiver = None

        # Try to find a valid receiver for the current sender
        for potential_receiver in emails:
            if (potential_receiver != sender and  # No self-matching
                participants[potential_receiver]['family'] != sender_details['family'] and  # Different families
                potential_receiver not in matches.values()):  # Not already receiving
                receiver = potential_receiver
                break

        if receiver is None:
            return None  # Matching failed - no valid receiver found

        matches[sender] = receiver

    return matches

def match_secret_santa(participants, debug_file=None):
    """
    Orchestrates the Secret Santa matching across all categories.

    Args:
        participants (dict): Complete dictionary of all participants
        debug_file (str, optional): Path to write debug information

    Returns:
        dict: Complete mapping of all givers to receivers, or None if matching fails

    Note:
        This function handles the separation of participants by category
        and attempts multiple retries if initial matching attempts fail.
    """
    # Group participants by their category
    category_groups = {}
    for email, details in participants.items():
        category = details['category']
        if category not in category_groups:
            category_groups[category] = {}
        category_groups[category][email] = details

    all_matches = {}

    # Process each category separately
    for category, group in category_groups.items():
        if debug_file:
            with open(debug_file, 'a') as dbg:
                dbg.write(f"\nStarting matching for category: {category}\n")
                dbg.write(f"Number of participants: {len(group)}\n")

        retries = 0
        max_retries = 100

        # Attempt matching with multiple retries if needed
        while retries < max_retries:
            matches = match_secret_santa_in_category(group)
            if matches:
                all_matches.update(matches)
                if debug_file:
                    with open(debug_file, 'a') as dbg:
                        dbg.write(f"Successfully matched category {category} on attempt {retries + 1}\n")
                break
            retries += 1
            if debug_file:
                with open(debug_file, 'a') as dbg:
                    dbg.write(f"Retry {retries} for category {category}\n")

        if retries == max_retries:
            if debug_file:
                with open(debug_file, 'a') as dbg:
                    dbg.write(f"FAILED: Could not match category {category} after {max_retries} attempts\n")
            return None

    return all_matches

def generate_output_file_name(input_file):
    """
    Creates a unique output filename based on input filename and timestamp.

    Args:
        input_file (str): Original input filename

    Returns:
        str: Generated output filename
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    base_name = input_file.rsplit('.', 1)[0]
    return f"{base_name}-Matched-{timestamp}.txt"

def generate_debug_file_name(input_file):
    """
    Creates a debug filename based on input filename and timestamp.

    Args:
        input_file (str): Original input filename

    Returns:
        str: Generated debug filename
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    base_name = input_file.rsplit('.', 1)[0]
    return f"{base_name}-Debug-{timestamp}.txt"

def write_output_file(matches, participants, output_file):
    """
    Writes the Secret Santa matches to an output file.

    Args:
        matches (dict): Mapping of givers to receivers
        participants (dict): Complete participant information
        output_file (str): Path to write the output file

    Output Format:
        CSV with columns: giver_first_name,giver_last_name,giver_email,
                         receiver_first_name,receiver_last_name,receiver_email
    """
    with open(output_file, 'w') as file:
        for sender, receiver in matches.items():
            sender_details = participants[sender]
            receiver_details = participants[receiver]
            file.write(
                f"{sender_details['first_name']},{sender_details['last_name']},{sender},"
                f"{receiver_details['first_name']},{receiver_details['last_name']},{receiver}\n"
            )

def spinner():
    """
    Displays an animated spinner to indicate processing activity.

    Note:
        This function runs in an infinite loop and should be run in a separate thread.
    """
    while True:
        for char in "|/-\\":
            print(f"\rGenerating matches, please wait... {char}", end="", flush=True)
            time.sleep(0.1)

def secret_santa():
    """
    Main function that coordinates the Secret Santa generation process.

    This function:
    1. Gets input file from command line or user input
    2. Reads participant data
    3. Generates matches
    4. Shows results for confirmation
    5. Writes output file if confirmed
    """
    # Get input file path
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Please enter the input file name: ")

    try:
        participants = read_input_file(input_file)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return

    output_file = generate_output_file_name(input_file)
    debug_file = generate_debug_file_name(input_file)

    # Start progress spinner in separate thread
    import threading
    spin_thread = threading.Thread(target=spinner, daemon=True)
    spin_thread.start()

    # Generate matches
    matches = match_secret_santa(participants, debug_file)

    if matches:
        print("\nGenerated Secret Santa matches successfully:")
        for sender, receiver in matches.items():
            sender_details = participants[sender]
            receiver_details = participants[receiver]
            print(
                f"{sender_details['first_name']} {sender_details['last_name']} ({sender}) -> "
                f"{receiver_details['first_name']} {receiver_details['last_name']} ({receiver})"
            )

        # Get user confirmation
        confirmation = input("\nAre these matches okay? (Y/N): ")
        if confirmation.lower() == 'y':
            write_output_file(matches, participants, output_file)
            print(f"\nMatches written to {output_file}")
        else:
            print("\nOperation canceled by user.")
    else:
        print("\nFailed to generate valid matches. Please review the input file and constraints.")
        print(f"Check {debug_file} for detailed information about the matching process.")

    # Clean up spinner thread
    spin_thread.join(timeout=0.2)

class TestSecretSanta(unittest.TestCase):
    """
    Unit tests for the Secret Santa Generator.

    These tests verify:
    - Valid matching within constraints
    - No self-matching
    - Proper file name generation
    """

    def setUp(self):
        """
        Sets up test data before each test method.
        """
        self.participants = {
            'a@example.com': {'first_name': 'Alice', 'last_name': 'A', 'family': 'F1', 'category': 'P'},
            'b@example.com': {'first_name': 'Bob', 'last_name': 'B', 'family': 'F2', 'category': 'P'},
            'c@example.com': {'first_name': 'Charlie', 'last_name': 'C', 'family': 'F3', 'category': 'C'},
            'd@example.com': {'first_name': 'David', 'last_name': 'D', 'family': 'F1', 'category': 'C'}
        }

    def test_valid_matching(self):
        """Tests that matching respects family and category constraints."""
        matches = match_secret_santa(self.participants)
        self.assertIsNotNone(matches, "Matching failed.")
        for sender, receiver in matches.items():
            self.assertNotEqual(
                self.participants[sender]['family'],
                self.participants[receiver]['family'],
                "Family constraint violated."
            )
            self.assertEqual(
                self.participants[sender]['category'],
                self.participants[receiver]['category'],
                "Category constraint violated."
            )

    def test_no_self_matching(self):
        """Tests that no participant is matched with themselves."""
        matches = match_secret_santa(self.participants)
        for sender, receiver in matches.items():
            self.assertNotEqual(sender, receiver, "Self-matching detected.")

    def test_debug_file_generation(self):
        """Tests proper debug file name generation."""
        debug_file = generate_debug_file_name("TestParticipants.txt")
        self.assertTrue(
            debug_file.startswith("TestParticipants-Debug"),
            "Debug file name not generated correctly."
        )

if __name__ == "__main__":
    # Check if running tests is explicitly requested
    if len(sys.argv) > 1 and sys.argv[1].lower() == '--test':
        unittest.main(argv=['dummy'])
    else:
        # Run the main Secret Santa generator
        secret_santa()
        
