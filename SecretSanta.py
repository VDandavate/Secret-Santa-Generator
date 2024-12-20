import random
import sys

def read_input_file(file_name):
    participants = {}
    with open(file_name, 'r') as file:
        for line in file:
            email, family = line.strip().split(';')
            participants[email] = family
    return participants

def match_secret_santa(participants):
    emails = list(participants.keys())
    random.shuffle(emails)
    matches = {}
    for i in range(len(emails)):
        sender = emails[i]
        sender_family = participants[sender]
        receiver = None
        for j in range(len(emails)):
            potential_receiver = emails[j]
            potential_receiver_family = participants[potential_receiver]
            if (potential_receiver_family != sender_family and
                    potential_receiver not in matches.values() and
                    matches.get(potential_receiver) != sender):
                receiver = potential_receiver
                break
        if receiver is None:
            return None

        matches[sender] = receiver

    return matches

def write_output_file(matches, output_file):
    with open(output_file, 'w') as file:
        for sender, receiver in matches.items():
            file.write(f"{sender} -> {receiver}\n")

def secret_santa(input_file, output_file):
    participants = read_input_file(input_file)
    matches = None
    while True:
        print("Attempting to generate Secret Santa matches...")
        matches = match_secret_santa(participants)
        if matches:
            print("Generated Secret Santa matches:")
            for sender, receiver in matches.items():
                print(f"{sender} -> {receiver}")
            confirmation = input("Are these matches okay? (Y/N): ")
            if confirmation.lower() == 'y':
                write_output_file(matches, output_file)
                print("Secret Santa matches written to file successfully!")
                break
            elif confirmation.lower() == 'n':
                print("Restarting the matching process...")
                continue
            else:
                print("Invalid input. Please enter Y/y or N/n.")
        else:
            print("Matching failed. Restarting...")

# Example usage:
secret_santa('ChildrensEmails.txt', 'ChildrensEmails-Matched.txt')
secret_santa('ParentsEmails.txt', 'ParentsEmails-Matched.txt')
