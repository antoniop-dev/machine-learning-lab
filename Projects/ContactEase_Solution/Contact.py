import utilities

class Contact:
    """
    Class to represents a contact with a name, surname, phone number, and optional notes.
    """
    def __init__(self, name: str, surname:str , phone_number:str, notes:str ="")->None:
        """
        Initialize a new Contact instance with normalized name and surname.

        Args:
            name (str): The contact's first name.
            surname (str): The contact's surname.
            phone_number (str): The contact's phone number.
            notes (str, optional): Additional notes about the contact. Defaults to an empty string.
        """
        self.name = utilities.normalize_name(name)
        self.surname = utilities.normalize_surname(surname)
        self.phone_number = phone_number
        self.notes = notes

    def get_name(self)->str:
        """
        Return the contact's first name.

        Returns:
            str: First name of the contact.
        """
        return self.name
    
    def get_surname(self)->str:
        """Return the contact's surname name.

        Returns:
            str: Surname of the contact.
        """
        return self.surname
    
    def get_phone_number(self)->str:
        """Return the contact's phone number.

        Returns:
            str: Phone number of the contact.
        """
        return self.phone_number
    
    def get_notes(self)->str:
        """
        Return the notes associated with the contact.

        Returns:
            str: The notes if present, otherwise an empty string.
        """
        if self.notes:
            return self.notes
        else:
            return " "
        
    def __str__(self)->str:
        """
        Return a string representation of the Contact.
        """
        notes_str = self.get_notes()
        return f"Name: {self.name}\nSurname: {self.surname}\nPhone: {self.phone_number}\nNotes: {notes_str}"
    

    def __repr__(self)->str:
        """
        Return a technical string representation of the Contact instance.
        """
        return (f"Contact(name={self.name!r}, surname={self.surname!r}, phone_number={self.phone_number!r}, notes={self.notes!r})")
        
    def change_name(self, new_name: str)->None:
        """
        Update the contact's first name to a new name.

        Args:
            new_name (str): The new first name.
        """
        self.name = utilities.normalize_name(new_name)
    
    def change_surname(self, new_surname: str)->None:
        """
        Update the contact's surname to a new surname.

        Args:
            new_surname (str): The new surname.
        """
        self.surname = utilities.normalize_surname(new_surname)
    
    def change_phone_number(self, new_phone_number: str)->None:
        """
        Update the contact's phone number.

        Args:
            new_phone_number (str): The new phone number.
        """
        self.phone_number = new_phone_number

    def change_notes(self, new_notes: str)->None:
        """
        Update the contact's notes.
        """
        self.notes = new_notes