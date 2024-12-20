import random
import sys
from datetime import datetime
import itertools
import time

def read_input_file(file_name):
    """
    Reads the input file and returns a dictionary of participants with their details.
    Format of the input file: email;first_name;last_name;family;category
    """
    participants = {}
    with open(file_name, 'r') as file:
        for line in file:
            email, first_name, last_name, family, category = line.strip().split(';')
            participants[email] = {
                'first_name': first_name,
                'last_name': last_name,
                'family': family,
                'category': category
            }
    return participants

def match_secret_santa_in_category(participants):
    """
    Matches participants for Secret Santa within a single category, ensuring:
    - No one is matched with someone from the same family.
    - No duplicate pairings.
    """
    emails = list(participants.keys())
    random.shuffle(emails)
    matches = {}

    for sender in emails:
        sender_details = participants[sender]
        receiver = None

        for potential_receiver in emails:
            if potential_receiver == sender:
                continue

            receiver_details = participants[potential_receiver]

            if (receiver_details['family'] != sender_details['family'] and
                potential_receiver not in matches.values()):
                receiver = potential_receiver
                break

        if receiver is None:
            return None  # Indicates matching failed

        matches[sender] = receiver

    return matches

def match_secret_santa(participants, debug_file=None):
    """
    Matches participants for Secret Santa across categories and combines results.
    """
    # Split participants by category
    category_groups = {}
    for email, details in participants.items():
        category_groups.setdefault(details['category'], {}).update({email: details})

    all_matches = {}

    for category, group in category_groups.items():
        if debug_file:
            with open(debug_file, 'a') as dbg:
                dbg.write(f"Matching for category {category}\n")

        retries = 0
        max_retries = 100
        while retries < max_retries:
            matches = match_secret_santa_in_category(group)
            if matches:
                all_matches.update(matches)
                break
            retries += 1
            if debug_file:
                with open(debug_file, 'a') as dbg:
                    dbg.write(f"Retry {retries} for category {category}\n")

        if retries == max_retries:
            if debug_file:
                with open(debug_file, 'a') as dbg:
                    dbg.write(f"Failed to generate matches for category {category} after {max_retries} attempts\n")
            return None

    return all_matches

def generate_output_file_name(input_file):
    """
    Generates a unique output file name based on the input file name and current timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    base_name = input_file.rsplit('.', 1)[0]
    return f"{base_name}-Matched-{timestamp}.txt"

def generate_debug_file_name(input_file):
    """
    Generates a debug file name based on the input file name and current timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    base_name = input_file.rsplit('.', 1)[0]
    return f"{base_name}-Debug-{timestamp}.txt"

def write_output_file(matches, participants, output_file):
    """
    Writes the matches to an output file in the format:
    <Gift Giver's first name>,<Gift Giver's last name>,<Gift Giver's email>,
    <Gift Receiver's first name>,<Gift Receiver's last name>,<Gift Receiver's email>
    """
    with open(output_file, 'w') as file:
        for sender, receiver in matches.items():
            sender_details = participants[sender]
            receiver_details = participants[receiver]
            file.write(f"{sender_details['first_name']},{sender_details['last_name']},{sender},"
                       f"{receiver_details['first_name']},{receiver_details['last_name']},{receiver}\n")

def spinner():
    """
    Displays a spinner to indicate progress.
    """
    while True:
        for char in "|/-\\":
            print(f"\rGenerating matches, please wait... {char}", end="", flush=True)
            time.sleep(0.1)

def secret_santa():
    """
    Main function to generate Secret Santa matches and write to the output file.
    """
    # Check for input file as a command-line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Please enter the input file name: ")

    participants = read_input_file(input_file)

    output_file = generate_output_file_name(input_file)
    debug_file = generate_debug_file_name(input_file)

    import threading
    spin_thread = threading.Thread(target=spinner, daemon=True)
    spin_thread.start()

    matches = match_secret_santa(participants, debug_file)

    if matches:
        print("\nGenerated Secret Santa matches successfully.")
        for sender, receiver in matches.items():
            sender_details = participants[sender]
            receiver_details = participants[receiver]
            print(f"{sender_details['first_name']} {sender_details['last_name']} ({sender}) -> "
                  f"{receiver_details['first_name']} {receiver_details['last_name']} ({receiver})")

        confirmation = input("Are these matches okay? (Y/N): ")
        if confirmation.lower() == 'y':
            write_output_file(matches, participants, output_file)
            print(f"Matches written to {output_file}.")
        else:
            print("Operation canceled by the user.")
    else:
        print("\nFailed to generate matches. Please review the input file and constraints.")

    spin_thread.join()

# Unit Test Function
if __name__ == "__main__":
    import unittest

    class TestSecretSanta(unittest.TestCase):

        def setUp(self):
            self.participants = {
                'a@example.com': {'first_name': 'Alice', 'last_name': 'A', 'family': 'F1', 'category': 'P'},
                'b@example.com': {'first_name': 'Bob', 'last_name': 'B', 'family': 'F2', 'category': 'P'},
                'c@example.com': {'first_name': 'Charlie', 'last_name': 'C', 'family': 'F3', 'category': 'C'},
                'd@example.com': {'first_name': 'David', 'last_name': 'D', 'family': 'F1', 'category': 'C'}
            }

        def test_valid_matching(self):
            matches = match_secret_santa(self.participants)
            self.assertIsNotNone(matches, "Matching failed.")
            for sender, receiver in matches.items():
                self.assertNotEqual(self.participants[sender]['family'], self.participants[receiver]['family'], "Family constraint violated.")
                self.assertEqual(self.participants[sender]['category'], self.participants[receiver]['category'], "Category constraint violated.")

        def test_no_self_matching(self):
            matches = match_secret_santa(self.participants)
            for sender, receiver in matches.items():
                self.assertNotEqual(sender, receiver, "Self-matching detected.")

        def test_debug_file_generation(self):
            debug_file = generate_debug_file_name("TestParticipants.txt")
            self.assertTrue(debug_file.startswith("TestParticipants-Debug"), "Debug file name not generated correctly.")

    unittest.main()
