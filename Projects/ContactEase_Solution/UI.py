from Contact import Contact
from ContactBook import ContactBook
from utilities import validate_name, validate_phone_number
from time import sleep
import os

class UI:
    def __init__(self):
        self.book = ContactBook()
        self.book.load_from_file()

    def run(self):
        #Loop to keep the UI running until the user choose to close the app
        while True:
            #Clears shell
            self.clear_terminal()
            #Print Main Menu header
            self.print_header()
            #Print Menu
            print("1. Add contact.")
            print("2. Show contacts.")
            print("3. Search contact.")
            print("4. Edit contact.")
            print("5. Delete contact.")
            print("6. Save and exit.")
            #Wait for user's input
            choice = input("\n\nChoose an option: ")

            #Calls for different methods according to user's choice
            if choice == "1":
                self.add_contact()
            elif choice == "2":
                self.show_contacts()
            elif choice == "3":
                self.search_contact()
            elif choice == "4":
                self.edit_contact()
            elif choice == "5":
                self.delete_contact()
            elif choice == "6":
                self.book.save_to_file()
                print("Contacts saved.\nExiting", end="")
                for i in range(3):
                    print(".",end="", flush=True)
                    sleep(1)
                break
            else:
                print("Invalid option.")
                sleep(2)

    def add_contact(self):
        #Clears shell
        self.clear_terminal()
        #Print section's header
        self.print_header("Add  Contact")
        print("Please insert data for new contact.")
        while True:
            name = input("Name: ")
            #Checks if a name was insert
            if not validate_name(name):
                print("Name field can't be empty.")
            else:
                break
        surname = input("Surname: ")
        while True:
            phone = input("Phone Number: ")
            #Checks if phone number has the right length
            if not validate_phone_number(phone):
                print("Invalid input. Phone Number must be a 10 digit number.")
            else:
                break
        notes = input("Notes (optional): ")
        try:
            self.book.add_contact(Contact(name, surname, phone, notes))
            print("✅ Contact succefully added.")
            sleep(2)
        except ValueError as e:
            print(f"❌ Error: {e}")
            command = input("Would you like to update existing contact with the new data? [yes/NO]: ")
            if command.lower() in ["yes", "y"]:
                self.edit_contact(name, surname, phone, notes)
            else:
                return

    def show_contacts(self):
        while True:
            self.clear_terminal()
            self.print_header("Contact List")
            if not self.book.get_contacts():
                print("Empty Contact Book.")
            else:
                for c in self.book.contacts:
                    print(c,flush=True)
                    print("\n\n")
                    sleep(0.5)
            exit = input("Insert any key to go back to Main Menu.\n")
            if exit:
                break

    def search_contact(self):
        while True:
            self.clear_terminal()
            self.print_header("Search Contact")
            print("1. Search by name.")
            print("2. Search by surname.")
            print("3. Search by full name.")
            print("4. Search by phone number.")
            print("5. Back to Main Menu.")

            choice = input("\n\nChoose an option: ")
            if choice == "1":
                while True:
                    name = input("Insert name for the research: ")
                    if not validate_name(name):
                        print("Invalid input, please insert a name.")
                    else:
                        break
                results = self.book.find_contact_by_name(name)
                break
            elif choice == "2":
                while True:
                    surname = input("Insert surname for the research: ")
                    if not surname:
                        print("Invalid input, please insert a surname.")
                    else:
                        break
                results = self.book.find_contact_by_surname(surname)
                break
            elif choice == "3":
                while True:
                    name = input("Insert name for the research: ")
                    surname = input("Insert surname for the research: ")
                    if not surname:
                        print("Invalid input, please insert a surname.")
                    elif not validate_name(name):
                        print("Invalid input, please insert a name.")
                    else:
                        break
                results = self.book.find_contact_by_name_and_surname(name, surname)
                break
            elif choice == "4":
                while True:
                    phone_number = input("Insert phone number for the research: ")
                    if not validate_phone_number(phone_number):
                        print("Invalid input, please insert a valid phone number.")
                    else:
                        break
                results = self.book.find_contact_by_phone_number(phone_number)
                break
            elif choice == "5":
                return
            else:
                print("Invalid input.")
                sleep(2)
            
        while True:
            if not results:
                print("❌ No contact found.")
            elif isinstance(results, list):
                print("\nContacts found:\n")
                for c in results:
                    print(c, flush=True)
                    sleep(0.5)
                    print()
            else:
                print("\nContact found:\n")
                print(results)
            exit = input("\n\nInsert any key to go back to main menu.\n")
            if exit:
                return

    def edit_contact(self, new_name="", new_surname="", phone="", new_notes=""):
        if not any([new_name, new_surname, phone, new_notes]):
            #If no parameters is passed open section for editing
            self.clear_terminal()
            self.print_header("Edit Contact")
            phone = input("Insert contact's phone number to edit: ")
            contact = self.book.find_contact_by_phone_number(phone)
            if not contact:
                print("❌ No contact found.")
                sleep(2)
                return
            print("\nPlease insert new data.\nLeave empty (press Enter) if you do not want to edit the field.")
            new_name = input(f"Insert new name (current: {contact.get_name()}): ") or contact.get_name()
            new_surname = input(f"Insert new surname (current: {contact.get_surname()}): ") or contact.get_surname()
            new_phone = input(f"Insert new phone number: (current {contact.get_phone_number()}): ") or contact.get_phone_number()
            new_notes = input(f"Insert new notes (current: {contact.get_notes()}): ") or contact.get_notes()
        else:
            #If any parameters are passed proceed with edit
            contact = self.book.find_contact_by_phone_number(phone)
            new_name = new_name or contact.get_name()
            new_surname = new_surname or contact.get_surname()
            new_phone = phone or contact.get_phone_number()
            new_notes = new_notes or contact.get_notes()

        #Edit contact
        contact.change_name(new_name)
        contact.change_surname(new_surname)
        contact.change_phone_number(new_phone)
        contact.change_notes(new_notes)
        self.book.sort_cotacts()
        print("✅ Contact succefully updated.")
        sleep(2)

    def delete_contact(self):
        self.clear_terminal()
        self.print_header("Delete Contact")
        phone = input("Insert phone number to delete. ")
        if not self.book.find_contact_by_phone_number(phone):
            print("No contact found.")
        else:
            self.book.remove_contact(phone)
            print("✅ Contact succeffully deleted.")
        sleep(2)
    
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, header_title="ContactEase Menu"):
        for i in range((80-(len(header_title)+2))//2):
            print("-", end="")
        print(f" {header_title} ", end="")
        for i in range((80-(len(header_title)+2))//2):
            print("-", end="")
        print()