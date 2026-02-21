import json
from Contact import Contact
import os

class ContactBook:
    """
    Class to represent a contact book that stores and manages a list of Contact objects.
    This class allows for one and only one contact for a given phone nubmer.
    """

    def __init__(self, contacts:list[Contact] =[])->None:
        """
        Initializes a new ContactBook with given a list of contacts or with an empty list.

        Args:
            contacts (list, optional): List of contacts.
        """
        self.contacts = contacts

    def add_contact(self, contact: Contact)->None:
        """
        Adds a new Contact to the contact book and sort the contacts list to keep it ordered.

        Args:
            contact (Contact): Contact to be added.
        
        Raises:
            ValueError : If phone number is already in the contact book.
        """
        #checks if the contact phone number is already in the contact book
        existing_contact = self.find_contact_by_phone_number(contact.phone_number)

        if existing_contact:
            #if phone number is found raise an error
            raise ValueError(f"Phone number {contact.phone_number} is already in the contact book.")
        
        #else it adds the contact and re-sort the contact book
        self.contacts.append(contact)
        self.sort_cotacts()

    def remove_contact(self, phone_number: str)->None:
        """
        Removes a Contact from the contact book by phone number.

        Args:
            phone_number (str): The phone number of the contact to be removed.
        """
        #checks if the contact phone number is in the contact book
        contact = self.find_contact_by_phone_number(phone_number)
        if contact:
            #if the contact is found, it is then removed
            self.contacts.remove(contact)
            
    def find_contact_by_name(self, name: str)->Contact:
        """
        Find contacts by a given name.

        Args:
            name (str): Name of the contact to find. 

        Returns:
            contact (Contact): Returns the contact if found, if many contacts match the request returns a list of contacts.
        """
        contacts_by_name = list()

        for contact in self.get_contacts():
            if contact.get_name() == name:
                contacts_by_name.append(contact)
            elif contact.get_name() > name:
                #Minimizes search checks by leveraging the fact that the contact list is sorted
                break

        if not contacts_by_name:
            return None        
        elif len(contacts_by_name) == 1:
            return contacts_by_name[0]
        else:
            return contacts_by_name
        
    def find_contact_by_surname(self, surname: str)->Contact:
        """
        Find ontacts by a given surname.

        Args:
            name (str): Name of the contact to find. 

        Returns:
            contact (Contact): Returns the contact if found, if many contacts match the request returns a list of contacts.
        """
        contacts_by_surname = list()

        for contact in self.get_contacts():
            if contact.get_surname() == surname:
                contacts_by_surname.append(contact)
        
        if not contacts_by_surname:
            return None        
        elif len(contacts_by_surname) == 1:
            return contacts_by_surname[0]
        else:
            return contacts_by_surname

        
    def find_contact_by_name_and_surname(self, name: str, surname: str)->Contact:
        """
        Find contacts by a given name and surname.

        Args:
            name (str): Name of the contact to find.
            surname (str): Surname of the contact to find.

        Returns:
            contact (Contact): Returns the contact if found, if many contacts match the request returns a list of contacts.
        """

        contacts_ = list()

        for contact in self.get_contacts():
            if contact.get_name() == name and contact.get_surname() == surname:
                contacts_.append(contact)
            elif contact.get_name() > name:
                #Minimizes search checks by leveraging the fact that the contact list is sorted
                break

        if len(contacts_) == 0:
            return None
        elif len(contacts_) == 1:
            return contacts_[0]
        else:
            return contacts_
    
    def find_contact_by_phone_number(self, phone_number: str)->Contact:
        """
        Find contacts by a given name and surname.

        Args:
            phone_number (str): Phone number of the contact to find.

        Returns:
            contact (Contact): Returns the contact if found.
        """
        for contact in self.get_contacts():
            if contact.get_phone_number() == phone_number:
                return contact
        return None


    def get_contacts(self)->list:
        """
        Returns the list of all contacts in the contact book.

        Returns:
            list: A list of Contact instances currently stored.
        """
        return self.contacts
    
    def sort_cotacts(self)->None:
        """
        Keep the contacts list sorted by name and surname.
        """
        self.contacts.sort(key=lambda c: (c.get_name(), c.get_surname()))
    
    def __str__(self)->str:
        """
        String reppresentation of the contacts book.
        """
        if not self.get_contacts():
            return "Contact book is empty."

        rendered_contacts = [str(contact) for contact in self.get_contacts()]
        return "\n\n".join(rendered_contacts)

    def __repr__(self)->str:
        """
        Return a technical representation of the ContactBook instance.
        """
        return f"ContactBook(contacts={self.contacts!r})"

    def save_to_file(self, filename="data/contacts.json")->None:
        """
        Save contacts in the contact book in a JSON file for persistency.
        """
        #Create directory if it doesn't exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        #Prepares payload
        payload = [
            {
                "name": c.get_name(),
                "surname": c.get_surname(),
                "phone_number": c.get_phone_number(),
                "notes": c.get_notes()
            }
            for c in self.get_contacts()
        ]

        #Write or overwrite file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

    def load_from_file(self, filename="data/contacts.json")->None:
        """
        Loads contacts from a JSON file into the contact book. If the file does not exist, initializes with an empty list.

        Args:
            filename (str, optional): The path to the file from which contacts will be loaded. Defaults to "data/contacts.json".
        """
        self.contacts = []
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                for c in data:
                    contact = Contact(c.get("name"), c.get("surname"), c.get("phone_number"), c.get("notes", " "))
                    try:
                        self.add_contact(contact)
                    except:
                        #if any duplicates by phone number are found only the first one is added to the contact list
                        continue
                self.sort_cotacts()
        except FileNotFoundError:
            self.contacts = []