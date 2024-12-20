import random
import sys
from datetime import datetime

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

def match_secret_santa(participants):
    """
    Matches participants for Secret Santa, ensuring:
    - No one is matched with someone from the same family.
    - Matches occur within the same category.
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
                receiver_details['category'] == sender_details['category'] and
                potential_receiver not in matches.values()):
                receiver = potential_receiver
                break

        if receiver is None:
            return None  # Indicates matching failed

        matches[sender] = receiver

    return matches

def generate_output_file_name(input_file):
    """
    Generates a unique output file name based on the input file name and current timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    base_name = input_file.rsplit('.', 1)[0]
    return f"{base_name}-Matched-{timestamp}.txt"

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

    while True:
        print("Attempting to generate Secret Santa matches...")
        matches = match_secret_santa(participants)

        if matches:
            print("Generated Secret Santa matches successfully.")
            for sender, receiver in matches.items():
                sender_details = participants[sender]
                receiver_details = participants[receiver]
                print(f"{sender_details['first_name']} {sender_details['last_name']} ({sender}) -> "
                      f"{receiver_details['first_name']} {receiver_details['last_name']} ({receiver})")

            confirmation = input("Are these matches okay? (Y/N): ")
            if confirmation.lower() == 'y':
                output_file = generate_output_file_name(input_file)
                write_output_file(matches, participants, output_file)
                print(f"Matches written to {output_file}.")
                break
            elif confirmation.lower() == 'n':
                print("Restarting the matching process...")
                continue
            else:
                print("Invalid input. Please enter Y/y or N/n.")
        else:
            print("Matching failed. Retrying...")

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

    secret_santa()
