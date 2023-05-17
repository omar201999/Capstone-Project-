import csv
from datetime import datetime
import os
import shutil
import boto3
import re


class Contact:
    # The Contact class represents a single contact entry in the contact book.
    # It has attributes such as username, email, phone_numbers, address, and insertion_date.
    def __init__(self, username, email, phone_number, address, insertion_date):
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.insertion_date = insertion_date

    def to_csv_row(self):
        # This function converts a Contact object into a list representing a single row of CSV data.
        return [self.username, self.email, self.phone_number, self.address, self.insertion_date]


class ContactBook:
    current_date = datetime.now().strftime("%d%m%Y")

    def __init__(self, file_name):
        self.file_name = file_name

    def validate_email(self, email):
        # This function validates whether an email address is in a valid format using a regular expression pattern.
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return True
        return False

    def validate_phone_number(self, phone_number):
        # This function validates whether a phone number is in a valid Egypthin number format using a regular expression pattern.
        pattern = re.compile(r'^(\+201|01|00201)[0-2,5]{1}[0-9]{8}')
        return bool(pattern.match(phone_number))

    def create_contact(self):
        # This function allows the user to enter contact details (username, email, phone numbers, address).
        username = input("Enter username: ")
        email = input("Enter email: ")
        phone_number = input("Enter phone number : ")
        address = input("Enter address: ")
        insertion_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.validate_email(email) and self.validate_phone_number(phone_number):
            contact = Contact(username, email, phone_number,
                              address, insertion_date)
            # If the details are valid, it creates a Contact object and appends it to the contact book.
            self.append_contact(contact)
            
            print("Contact added successfully!")
        elif not self.validate_email(email):
            print("Please enter vaild email")
        elif not self.validate_phone_number(phone_number):
            print("Please enter vaild email")

    def update_contact(self):
        # This function allows the user to update a specific field (username, email, phone number, address) of a contact.
        name = input("Enter name of contact to update: ")
        field = input("Enter field to update (username/email/phone/address): ")
        new_value = input("Enter new value: ")
        rows = self.load_contacts()
        for row in rows:
            if row[0] == name:
                if field == "username":
                    row[0] = new_value
                elif field == "email":
                    if self.validate_email(new_value):
                        row[1] = new_value
                    else:
                        print("Please enter vaild email")
                elif field == "phone":
                    if self.validate_phone_number(new_value):
                        row[2] = new_value
                    else:
                        print("Please enter vaild phone")
                elif field == "address":
                    row[3] = new_value
        #It finds the contact in the contact book, updates the specified field, and saves the changes.
        self.save_contacts(rows)
        print("Contact updated successfully!")

    def delete_contact(self):
        # This function allows the user to remove a contact from the contact book.
        name = input("Enter name of contact to remove: ")
        rows = self.load_contacts()
        for row in rows:
            if row[0] == name:
                rows.remove(row)
        self.save_contacts(rows)
        print("Contact removed successfully!")

    def backup(self, backup_directory):
        # This function creates a backup of the contact book by copying the file to the specified backup directory.
        try:
            if not os.path.exists(backup_directory):
                os.makedirs(backup_directory)
            backup_file_name = self.generate_backup_file_name()
            shutil.copy(self.file_name, os.path.join(
                backup_directory, backup_file_name))
        except:
            print("Sorry,some error happend when backup ")

    def backup_to_aws(self, bucket_name, aws_access_key_id, aws_secret_access_key):
        # This function uploads the contact book file to an AWS S3 bucket for cloud backup.
        session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)
        s3 = session.resource('s3')
        bucket = s3.Bucket(bucket_name)
        #It requires the AWS bucket name, access key ID, and secret access key for authentication but i don't have aws email yet so i can't provides this data.
        backup_file_name = self.generate_backup_file_name()
        shutil.copy(self.file_name, backup_file_name)
        bucket.upload_file(backup_file_name, os.path.basename(backup_file_name))
        #It creates a backup file, uploads it to the specified S3 bucket, and removes the local backup file.
        os.remove(backup_file_name)

    def view_contacts(self):
        # This function displays all the contacts in the contact book on the console.
        try:
            if os.path.exists(self.file_name):
                with open(self.file_name, 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        print(row)
        except FileNotFoundError:
            msg = "Sorry, the file " + self.file_name + "does not exist."
            print(msg)

    def load_contacts(self):
        # This function loads the contacts from the contact book file and returns them as a list of rows.
        try:
            rows = []
            if os.path.exists(self.file_name):
                with open(self.file_name, 'r') as file:
                    reader = csv.reader(file)
                    rows = list(reader)
                    return rows

        except FileNotFoundError:
            msg = "Sorry, the file " + self.file_name + "does not exist."
            print(msg)

    def save_contacts(self, rows):
        # This function saves the contacts (rows) to the contact book file.
        try:
            if os.path.exists(self.file_name):
                with open(self.file_name, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(rows)
        except FileNotFoundError:
            msg = "Sorry, the file " + self.file_name + "does not exist."
            print(msg)

    def append_contact(self, contact):
        # This function appends a new contact to the contact book file.
        try:
            with open(self.file_name, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(contact.to_csv_row())
        except FileNotFoundError:
            msg = "Sorry, the file " + self.file_name + "does not exist."
            print(msg)

    def generate_backup_file_name(self):
        # This function generates a unique backup file name based on the current date.
        try:
            backup_file_name = f"contactbook_{self.current_date}.csv"
            return backup_file_name
        except:
            print("Sorry,some error happend when create backup file name ")


# contact_book = ContactBook(
#     f'contactbook_{datetime.now().strftime("%d%m%Y")}.csv')
# contact_book.load_contacts()
while True:
    print("\nWelcome to the Contact Book!")
    print("1. Add new contact")
    print("2. View all contacts")
    print("3. Update a contact")
    print("4. Remove a contact")
    print("5. backup your contact")
    print("6. Exit")

    choice = input("Enter your choice: ")
    contact_book = ContactBook(f'contactbook_{ContactBook.current_date}.csv')
    if choice == "1":
        contact_book.create_contact()
    elif choice == "2":
        contact_book.view_contacts()
    elif choice == "3":
        contact_book.update_contact()
    elif choice == "4":
        contact_book.delete_contact()
    elif choice == "5":
        backup_dir_name = input("Enter Backup Directory Name: ")
        contact_book.backup(backup_dir_name)
    elif choice == "6":
        print("Thank you for using the Contact Book!")
        break
    else:
        print("Invalid choice. Please try again.")
