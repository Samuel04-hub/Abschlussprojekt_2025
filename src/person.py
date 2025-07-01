
"""
import json
from PIL import Image
from datetime import date
class Person:
    def __init__(self, id : int, date_of_birth : int, firstname, lastname, picture_path, ekg_tests, gender = "Male"):
        self.id = id
        self.date_of_birth = date_of_birth
        self.firstname = firstname
        self.lastname = lastname
        self.picture_path = picture_path
        self.ekg_tests = ekg_tests
        self.hr_max = 220 - (2025-int(date_of_birth))
        self.gender = gender

    @staticmethod
    def load_person_data():
        ...A Function that knows where the person Database is and returns a Dictionary with the Persons...
        with open("data/person_db.json", "r", encoding="utf-8") as file:
            person_data = json.load(file)
        return person_data

    def set_hr(self, hr):
        self.hr_max = hr

    def calc_age(self):
        ...Berechnet das Alter der Person....
        current_year = date.today().year
        return current_year - int(self.date_of_birth)
    
    def get_full_name(self):
        return self.lastname + ", " + self.firstname

    def get_image(self):
        image = Image.open(self.picture_path)
        return image

    @staticmethod
    def get_person_list(persons):
        ...Gibt eine Liste aller Namen zurück....
        return [p.get_full_name() for p in persons]

    @staticmethod
    def find_person_data_by_name(full_name):
        persons = Person.get_person_data()
        firstname = full_name.split(", ")[1]
        lastname = full_name.split(", ")[0]
        for person in persons:
            if person.firstname == firstname and person.lastname == lastname:
                return person

    @staticmethod
    def get_person_data():
        ...
        Returns the person data loaded from the JSON file as Person-Objekte.
        ...
        person_data = Person.load_person_data()
        person_object_list = []
        for person_dict in person_data:
            person_object = Person(
                person_dict["id"],
                person_dict["date_of_birth"],
                person_dict["firstname"],
                person_dict["lastname"],
                person_dict["picture_path"],
                person_dict["ekg_tests"],
                person_dict.get("gender", "Male")
            )
            person_object_list.append(person_object)
        return person_object_list

    def get_person_object_by_full_name(self, full_name):
        persons = self.get_person_data()
        firstname = full_name.split(", ")[1]
        lastname = full_name.split(", ")[0]
        for person in persons:
            if person.firstname == firstname and person.lastname == lastname:
                return person

if __name__ == "__main__":
    print("This is a module with some functions to read the person data")
    persons = get_person_data()
    person_names = Person.get_person_list(persons)
    print(person_names)
    print(Person.find_person_data_by_name("Huber, Julian"))

   
"""

import json
from PIL import Image
from datetime import date
import os

class Person:
    def __init__(self, id: int, date_of_birth: int, firstname: str, lastname: str, picture_path: str, ekg_tests: list, gender: str = "Male", is_new: bool = False):
        self.id = id
        self.date_of_birth = date_of_birth
        self.firstname = firstname
        self.lastname = lastname
        self.picture_path = picture_path
        self.ekg_tests = ekg_tests
        self.hr_max = 220 - (2025 - int(date_of_birth))
        # Normiere das Geschlecht
        self.gender = self._normalize_gender(gender)
        self.is_new = is_new

    @staticmethod
    def _normalize_gender(gender: str) -> str:
        """Normiert das Geschlecht zu 'Male', 'Female' oder 'Other'."""
        gender = gender.strip().capitalize()
        if gender in ["Male", "Female", "Other"]:
            return gender
        elif gender.lower() == "male":
            return "Male"
        elif gender.lower() == "female":
            return "Female"
        else:
            return "Other"

    @staticmethod
    def load_person_data():
        """Lädt die Personendaten aus der JSON-Datei."""
        try:
            with open("data/person_db.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    @staticmethod
    def save_person_data(person_data):
        """Speichert die Personendaten in der JSON-Datei."""
        with open("data/person_db.json", "w", encoding="utf-8") as file:
            json.dump(person_data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def get_person_data():
        """Gibt die Personendaten als Liste von Person-Objekten zurück."""
        person_data = Person.load_person_data()
        person_object_list = []
        for person_dict in person_data:
            person_object = Person(
                person_dict["id"],
                person_dict["date_of_birth"],
                person_dict["firstname"],
                person_dict["lastname"],
                person_dict["picture_path"],
                person_dict["ekg_tests"],
                person_dict.get("gender", "Male"),
                person_dict.get("is_new", False)
            )
            person_object_list.append(person_object)
        return person_object_list

    @staticmethod
    def get_person_list(persons):
        """Gibt eine Liste aller Namen zurück."""
        return [p.get_full_name() for p in persons]

    def get_full_name(self):
        """Gibt den vollständigen Namen zurück."""
        return f"{self.lastname}, {self.firstname}"

    def calc_age(self):
        """Berechnet das Alter der Person."""
        current_year = date.today().year
        return current_year - int(self.date_of_birth)

    def get_image(self):
        """Lädt das Bild der Person."""
        try:
            return Image.open(self.picture_path)
        except FileNotFoundError:
            return None

    @staticmethod
    def find_person_data_by_name(full_name: str):
        """Findet eine Person anhand des vollständigen Namens."""
        persons = Person.get_person_data()
        firstname = full_name.split(", ")[1]
        lastname = full_name.split(", ")[0]
        for person in persons:
            if person.firstname == firstname and person.lastname == lastname:
                return person
        return None

    @staticmethod
    def add_person(id: int, date_of_birth: int, firstname: str, lastname: str, picture_path: str, gender: str = "Male"):
        """Fügt eine neue Person zur JSON-Datei hinzu."""
        person_data = Person.load_person_data()
        new_person = {
            "id": id,
            "date_of_birth": date_of_birth,
            "firstname": firstname,
            "lastname": lastname,
            "picture_path": picture_path,
            "ekg_tests": [],
            "gender": Person._normalize_gender(gender),
            "is_new": True
        }
        person_data.append(new_person)
        Person.save_person_data(person_data)

    @staticmethod
    def update_person(full_name: str, updated_data: dict):
        """Aktualisiert die Daten einer bestehenden Person."""
        person_data = Person.load_person_data()
        firstname = full_name.split(", ")[1]
        lastname = full_name.split(", ")[0]
        for person in person_data:
            if person["firstname"] == firstname and person["lastname"] == lastname:
                person.update(updated_data)
                # Normiere das Geschlecht auch bei Updates
                person["gender"] = Person._normalize_gender(person["gender"])
                break
        Person.save_person_data(person_data)

    @staticmethod
    def delete_person(full_name: str):
        """Löscht eine neu erstellte Person, wenn is_new == True."""
        person_data = Person.load_person_data()
        firstname = full_name.split(", ")[1]
        lastname = full_name.split(", ")[0]
        person_data = [p for p in person_data if not (p["firstname"] == firstname and p["lastname"] == lastname and p.get("is_new", False))]
        Person.save_person_data(person_data)

    @staticmethod
    def add_ekg_test(full_name: str, test_date: str, ekg_path: str):
        """Fügt einen neuen EKG-Test für eine Person hinzu."""
        person_data = Person.load_person_data()
        firstname = full_name.split(", ")[1]
        lastname = full_name.split(", ")[0]
        for person in person_data:
            if person["firstname"] == firstname and person["lastname"] == lastname:
                person["ekg_tests"].append({"date": test_date, "ekg_path": ekg_path})
                break
        Person.save_person_data(person_data)

if __name__ == "__main__":
    print("Dies ist ein Modul mit Funktionen zum Lesen und Verwalten von Personendaten.")
    persons = Person.get_person_data()
    person_names = Person.get_person_list(persons)
    print(person_names)
    person = Person.find_person_data_by_name("Huber, Julian")
    if person:
        print(f"Gefundene Person: {person.get_full_name()}")