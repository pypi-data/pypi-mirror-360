import string
import os
from datetime import datetime
from tqdm import tqdm

class BruteforcePassword:
    def __init__(self, first_name="",  middle_name="", last_name="", dob="", 
                 city="", fav_number="", pet_name="", target_website="", apply_leetspeak=False):
        '''
        Initialize the BruteforcePassword class with user information.
        :param first_name [string]: User's first name
        :param middle_name [string]: User's middle name
        :param last_name [string]: User's last name
        :param dob [string]: User's date of birth in DDMMYYYY format
        :param city [string]: User's city
        :param fav_number [string]: User's favorite number
        :param pet_name [string]: User's pet name
        :param target_website [string]: Target website for which passwords are being generated
        :param apply_leetspeak [bool]: Whether to apply leetspeak transformations to generated passwords
        '''

        # Validate date format if provided
        if dob:
            try:
                parsed = datetime.strptime(dob, "%d%m%Y")
                day_of_birth = parsed.strftime("%d")
                month_of_birth = parsed.strftime("%m")
                year_of_birth = parsed.strftime("%Y")
            except ValueError:
                raise ValueError(f"Invalid date format for dob: '{dob}'. Expected format is DDMMYYYY.")
            except Exception as e:
                print(e)
                raise ValueError(f"An unexpected error occurred while parsing dob: '{dob}'.")

        self.vocabulary = {
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "dob": dob,
            "day_of_birth": day_of_birth,
            "month_of_birth": month_of_birth,
            "year_of_birth": year_of_birth,
            "city": city,
            "fav_number": fav_number,
            "pet_name": pet_name,
            "target_website": target_website,
        }
        self.generate_default_template()
        self.relevant_words = list(self.vocabulary.values())
        self.apply_leetspeak = apply_leetspeak

    def add_more_info(self, key, value):
        """
        Add more information to the vocabulary.
        :param key: The key for the information (e.g., "favorite_color")
        :param value: The value for the information (e.g., "blue")
        :raises ValueError: If the key is "any_word" which is reserved.
        """
        assert key != "any_word", "Key 'any_word' is reserved and cannot be used."
        self.vocabulary[key] = value

    def add_relevant_words(self, words):
        '''
        Add more relevant words to the list of words used for password generation. Relevant words are added to the passwords.
        Example if the target may have the word "charizard" in the password, you can add it to the relevant words.
        :param words: A list of words to be added.
        '''
        self.relevant_words.extend(words)

    
    def add_template(self, template: str):
        """
            Add a custom template to the list of templates. Templates are used to generate passwords.
            Example template: {mothers_name}.123
            note: If you add a template you need to ensure that the vocabulary contains the required fields.
        :param template: A string template that can contain placeholders like {first_name}, {last_name}, etc.
        :raises ValueError: If the template is empty.
        """
        if not template:
            raise ValueError("Template cannot be empty.")
        self.templates.append(template)



    def generate_default_template(self):
        '''
            Internal function
        '''
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "common_passwords.txt")

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            self.templates = [line.strip() for line in lines if line.strip()]


    def safe_format(self, template: str) -> tuple[bool, list[str]]:
        """
        Internal function.
        Format the template into one or more variations if all fields are valid.
        Returns (False, []) if required fields are missing or empty.
        Returns (True, [variants...]) otherwise.
        """
        formatter = string.Formatter()
        fields = [field for _, field, _, _ in formatter.parse(template) if field]

        # Ensure all required fields are present and non-empty
        for field in fields:
            value = self.vocabulary.get(field)
            if not value:
                return False, []

        # Basic format using raw values
        try:
            base = template.format(**self.vocabulary)
        except KeyError:
            return False, []

        # Generate variants for the fields: lowercase and capitalized
        variant_sets = []
        for field in fields:
            value = self.vocabulary[field]
            variant_sets.append([value.lower(), value.capitalize()])

        # Generate all combinations of variants for fields
        from itertools import product

        variants = []
        for combo in product(*variant_sets):
            # Build a temp dict with these variations
            temp_info = self.vocabulary.copy()
            for i, field in enumerate(fields):
                temp_info[field] = combo[i]
            try:
                formatted = template.format(**temp_info)
                variants.append(formatted)
            except KeyError:
                continue

        return True, list(set(variants))  # remove duplicates just in case
        
    def apply_leetspeak(self, word: str) -> str:
        '''
            Internal function.
        '''
        leet_map = {
            'a': ['@', '4'],
            'b': ['8'],
            'e': ['3'],
            'i': ['1', '!'],
            'l': ['1', '|'],
            'o': ['0'],
            's': ['$', '5'],
            't': ['7'],
            'g': ['9'],
        }

        variations = set([word])

        for i, char in enumerate(word):
            if char.lower() in leet_map:
                for leet_char in leet_map[char.lower()]:
                    for variant in list(variations):
                        # Replace char at i with leet_char
                        new_variant = variant[:i] + leet_char + variant[i+1:]
                        variations.add(new_variant)

        return variations

    def transform_passwords(self, passwords: set) -> set:
        '''
            Internal function.
        '''
        transformed = set()
        for pw in passwords:
            transformed.update(self.apply_leetspeak(pw))
        return transformed

    def brute_force(self):
        """
        Generate all possible passwords based on the vocabulary and relevant words.
        """
        passwords = set()

        for template in tqdm(self.templates):
            if '{any_word}' in template:
                for word in self.relevant_words:
                    if not word:
                        continue
                    for variation in [word.lower(), word.capitalize(), word.upper()]:
                        temp_template = template.replace('{any_word}', variation)
                        ok, variants = self.safe_format(temp_template)
                        if ok:
                            passwords.update(variants)
            else:
                ok, variants = self.safe_format(template)
                if ok:
                    passwords.update(variants)
        
        if self.apply_leetspeak:
            # Apply leetspeak and return full list
            passwords |= self.transform_passwords(passwords)
        return list(passwords)
