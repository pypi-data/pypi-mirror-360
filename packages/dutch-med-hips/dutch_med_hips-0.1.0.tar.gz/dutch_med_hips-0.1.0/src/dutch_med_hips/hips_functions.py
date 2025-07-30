import random
import re
import string
from datetime import date, timedelta
from importlib.resources import files
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from unidecode import unidecode

from dutch_med_hips.utils import load_json, load_pickle


class HideInPlainSight:

    def __init__(self, internal_use: bool = False):
        self.config_dir = Path(files("dutch_med_hips") / "config")
        self.lookup_dir = self.config_dir / "lookup_lists"

        self.internal_use = internal_use

        self.infixes = load_json(self.lookup_dir / "infixes.json")
        self.names = load_json(self.lookup_dir / "names_lookup_lists.json")
        self.locations = load_json(self.lookup_dir / "locations_lookup_lists.json")
        self.titles = load_json(self.lookup_dir / "titles_lookup_lists.json")
        self.dates = load_json(self.lookup_dir / "dates_lookup_lists.json")
        self.netcodes = load_json(self.lookup_dir / "netcodes.json")
        self.common_names = load_json(self.lookup_dir / "common_names.json")
        self.age_distribution = load_pickle(self.lookup_dir / "age_distribution.pkl")
        self.character_distribution = load_json(
            self.lookup_dir / "dutch_character_frequency.json"
        )
        self.hospitals = pd.read_csv(self.lookup_dir / "dutch_hospitals.csv")
        self.observed_hospital_names = load_json(
            self.lookup_dir / "observed_hospital_names.json"
        )
        self.study_names = load_json(self.lookup_dir / "studies.json")
        self.weights_config = load_json(self.config_dir / "config.json")

        # Sorted lists for consistency with seed
        self.family_names_list = sorted(self.names["person_names"]["family_names"])
        self.first_names_list = sorted(self.names["person_names"]["first_names"])
        self.locations_list = sorted(self.locations["dutch_cities"])

    def get_config(self, *keys):
        cfg = self
        for k in keys:
            cfg = cfg[k]
        return cfg

    def choose_weighted(self, choices, weights):
        return random.choices(choices, weights=weights)[0]

    def choose_unweighted(self, choices):
        return random.choice(choices)

    """
    UTILITY FUNCTIONS FOR APPLYING HIDE-IN-PLAIN-SIGHT

    Function to capitalize words in a string, function to add spelling errors to a string and function to generate string of random numbers.
    """

    def capitalize_word(self, word: str) -> str:
        # Capitalize the first letter of the word and any letter after a dash or apostrophe
        return "".join(
            c.capitalize() if i == 0 or word[i - 1] in "-'" else c
            for i, c in enumerate(word)
        )

    def capitalize_words_except_infixes(self, string: str, exceptions) -> str:
        words = string.split()
        capitalized_words = []
        non_exception_words = []
        exception_words = []

        for word in words:
            if word.lower() in exceptions:
                # If the word is in the exceptions list, add it to the list of exception words
                exception_words.append(word)
            else:
                # If the word is not in the exceptions list, add it to the list of non-exception words
                non_exception_words.append(word)

        # Move the exception words to the front of the list in the order they appeared in the original string
        capitalized_words.extend(exception_words)
        # Capitalize all the non-exception words and add them to the list
        capitalized_words.extend(
            self.capitalize_word(word) for word in non_exception_words
        )

        capitalized_string = " ".join(capitalized_words)
        return capitalized_string

    def abbreviate_name(self, name, surname_letters=3, infix_list=None):
        parts = name.split()
        abbreviation = ""

        for i, part in enumerate(parts):
            if part.lower() in infix_list:
                abbreviation += part[0].lower()
            else:
                # Only apply letter limit to the last part (main surname)
                if i == len(parts) - 1:
                    abbreviation += part[:surname_letters].capitalize()
                else:
                    abbreviation += part  # Optional: handle unexpected structure

        return abbreviation

    def add_spelling_error(self, string: str) -> str:
        error_type = random.choice(["insertion", "deletion", "substitution"])
        input_list = list(string)
        keymap = load_json(self.lookup_dir / "keyboard_neighbors.json")

        if error_type == "substitution":
            # Choose a random index to introduce a spelling error
            error_index = random.randint(0, len(input_list) - 1)

            # Get the character at the chosen index
            original_char = input_list[error_index]

            # Check if the character has a replacement in the keyboard mapping
            if original_char in keymap:
                # Choose a random replacement character from the mapping
                replacement_char = random.choice(keymap[original_char])

                # Replace the original character with the replacement
                input_list[error_index] = replacement_char

            # Convert the modified list back to a string
            modified_string = "".join(input_list)

        elif error_type == "insertion":
            # Choose a random index to introduce a spelling error
            error_index = random.randint(0, len(input_list) - 1)

            # Get the character at the chosen index
            original_char = input_list[error_index]

            # Check if the character has a replacement in the keyboard mapping
            if original_char in keymap:
                # Choose a random replacement character from the mapping
                replacement_char = random.choice(keymap[original_char])

                # Insert the replacement character at the chosen index
                input_list.insert(error_index, replacement_char)

            # Convert the modified list back to a string
            modified_string = "".join(input_list)

        elif error_type == "deletion":
            # Choose a random index to introduce a spelling error
            error_index = random.randint(0, len(input_list) - 1)

            # Delete the character at the chosen index
            del input_list[error_index]

            # Convert the modified list back to a string
            modified_string = "".join(input_list)

        return modified_string

    def generate_random_number_sequence(self, length) -> str:
        return str(random.randint(0, (10**length) - 1)).zfill(length)

    """
    FUNCTIONS FOR APPLYING HIDE-IN-PLAIN-SIGHT

    If tag --use-hips flag is used, the HIPS principle is applied to the report. This means that all tags in the report are replaced by realistic surrogates.
    Additionally, a disclaimer is added to the end of the report.
    """

    def hips_person_names(self, match) -> str:
        config = self.weights_config["person_names"]

        # Generate random configurations from config
        name_config = random.choices(
            config["name_config"]["choices"], weights=config["name_config"]["weights"]
        )[0]
        rare_first_name = random.choices(
            config["rare_first_name"]["choices"],
            weights=config["rare_first_name"]["weights"],
        )[0]
        rare_last_name = random.choices(
            config["rare_last_name"]["choices"],
            weights=config["rare_last_name"]["weights"],
        )[0]
        spelling_error = random.choices(
            config["spelling_error"]["choices"],
            weights=config["spelling_error"]["weights"],
        )[0]
        capitalization = random.choices(
            config["capitalization"]["choices"],
            weights=config["capitalization"]["weights"],
        )[0]
        full_first_name = random.choices(
            config["full_first_name"]["choices"],
            weights=config["full_first_name"]["weights"],
        )[0]
        first_name_first = random.choices(
            config["first_name_first"]["choices"],
            weights=config["first_name_first"]["weights"],
        )[0]
        amount_of_initials = random.choices(
            config["amount_of_initials"]["choices"],
            weights=config["amount_of_initials"]["weights"],
        )[0]
        double_family_name = random.choices(
            config["double_family_name"]["choices"],
            weights=config["double_family_name"]["weights"],
        )[0]
        double_family_name_separator = random.choices(
            config["double_family_name_separator"]["choices"],
            weights=config["double_family_name_separator"]["weights"],
        )[0]
        add_title = random.choices(
            config["add_title"]["choices"], weights=config["add_title"]["weights"]
        )[0]

        # Pick names
        family_name = (
            random.choice(self.family_names_list)
            if rare_last_name
            else random.choice(self.common_names["family_names"])
        )
        if double_family_name:
            family_name += double_family_name_separator + random.choice(
                self.common_names["family_names"]
            )
        first_name = (
            random.choice(self.first_names_list)
            if rare_first_name
            else random.choice(self.common_names["first_names"])
        )

        # Add optional spelling errors
        if spelling_error:
            if random.choice(["first_name", "family_name"]) == "first_name":
                first_name = self.add_spelling_error(first_name)
            else:
                family_name = self.add_spelling_error(family_name)

        # Capitalize
        if capitalization:
            family_name = self.capitalize_words_except_infixes(
                family_name, self.infixes["infixes"]
            )
            first_name = self.capitalize_words_except_infixes(
                first_name, self.infixes["infixes"]
            )

        # Construct name
        if name_config == "family_name":
            new_name = family_name
        elif name_config == "first_name":
            new_name = first_name
        else:
            new_name = family_name
            if full_first_name:
                new_name = first_name + " " + new_name
            else:
                initials = [
                    (
                        random.choice(
                            string.ascii_uppercase
                            if capitalization
                            else string.ascii_lowercase
                        )
                        + "."
                    )
                    for _ in range(amount_of_initials)
                ]
                initials_str = " ".join(initials)
                if first_name_first:
                    new_name = f"{initials_str} {new_name}"
                else:
                    new_name = f"{new_name}, {initials_str}"

        # Add title (if enabled — currently not used but code is there)
        if add_title == "before":
            listkey = random.choice(list(self.titles["before"].keys()))
            listkey2 = random.choice(list(self.titles["before"][listkey].keys()))
            new_name = (
                random.choice(self.titles["before"][listkey][listkey2]) + " " + new_name
            )
        elif add_title == "after":
            listkey = random.choice(list(self.titles["after"].keys()))
            listkey2 = random.choice(list(self.titles["after"][listkey].keys()))
            new_name = (
                new_name
                + random.choice([" ", ", "])
                + random.choice(self.titles["after"][listkey][listkey2])
            )

        return unidecode(new_name).strip()

    def hips_dates(self, match) -> str:
        config = self.weights_config["dates"]

        # Generate random date
        start_date = date(
            config["start_date"]["year"],
            config["start_date"]["month"],
            config["start_date"]["day"],
        )
        if config["end_date"]["use_today"]:
            end_date = date.today()
        else:
            end_date = date(
                config["end_date"]["year"],
                config["end_date"]["month"],
                config["end_date"]["day"],
            )
        total_days = (end_date - start_date).days
        random_days = random.randint(0, total_days)
        random_date = start_date + timedelta(days=random_days)

        # Pull random config options
        named_month = random.choices(
            config["named_month"]["choices"],
            weights=config["named_month"]["weights"],
        )[0]
        add_year = random.choices(
            config["add_year"]["choices"], weights=config["add_year"]["weights"]
        )[0]
        formatting = random.choices(
            config["formatting"]["choices"], weights=config["formatting"]["weights"]
        )[0]

        # Handle named month format
        if named_month:
            listkey = random.choice(list(self.dates["months"].keys()))
            month = random.choice(self.dates["months"][listkey])
            spelling_error = random.choices(
                config["month_spelling_error"]["choices"],
                weights=config["month_spelling_error"]["weights"],
            )[0]
            if spelling_error:
                month = self.add_spelling_error(month)

            new_date = random_date.strftime("%d ") + month
            if add_year:
                new_date += random_date.strftime(" %Y")
        else:
            if add_year:
                new_date = random_date.strftime(f"%d{formatting}%m{formatting}%Y")
            else:
                new_date = random_date.strftime(f"%d{formatting}%m")

        return new_date

    def hips_time(self, match) -> str:
        config = self.weights_config["time"]

        # Generate random time components
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)

        # Config-driven choices
        only_hour = random.choices(
            config["only_hour"]["choices"], weights=config["only_hour"]["weights"]
        )[0]
        time_separator = random.choices(
            config["time_separator"]["choices"],
            weights=config["time_separator"]["weights"],
        )[0]

        # Format the time
        new_time = str(random_hour).zfill(2)
        if not only_hour:
            new_time += time_separator + str(random_minute).zfill(2)
        else:
            new_time += " uur"

        return new_time

    def hips_phone_numbers(self, match) -> str:
        config = self.weights_config["phone_number"]

        # Draw configuration options from config
        phone_format = random.choices(
            config["phone_format"]["choices"],
            weights=config["phone_format"]["weights"],
        )[0]
        separator = random.choices(
            config["separator"]["choices"], weights=config["separator"]["weights"]
        )[0]
        add_prefix = random.choices(
            config["add_prefix"]["choices"], weights=config["add_prefix"]["weights"]
        )[0]

        # Format phone number based on type
        if phone_format == "internal":
            new_phone = self.generate_random_number_sequence(5)

        elif phone_format == "sein":
            new_phone = (
                "sein " if add_prefix else ""
            ) + self.generate_random_number_sequence(4)

        elif phone_format == "mobile":
            new_phone = "06" + separator + self.generate_random_number_sequence(8)

        elif phone_format == "landline":
            netcode = random.choice(self.netcodes["netcodes"])
            fill_length = 10 - len(netcode)
            new_phone = (
                netcode + separator + self.generate_random_number_sequence(fill_length)
            )

        else:
            # Fallback just in case of unexpected value
            new_phone = self.generate_random_number_sequence(10)

        return new_phone

    def hips_patient_id(self, match) -> str:
        new_pnumber = self.generate_random_number_sequence(7)
        return new_pnumber

    def hips_z_number(self, match) -> str:
        new_znumber = "Z" + self.generate_random_number_sequence(6)
        return new_znumber

    def hips_locations(self, match) -> str:
        city_name = random.choice(self.locations_list)
        new_city = " ".join(word.capitalize() for word in city_name.split())
        return new_city

    def hips_rapport_id(self, match) -> str:
        config = self.weights_config["rapport_id"]

        # Determine base tag type
        tag_type = None
        match_tag = match.group().upper()
        if re.match("<RAPPORT[-_]ID.T[-_]NUMMER>", match_tag):
            tag_type = "T"
        elif re.match("<RAPPORT[-_]ID.R[-_]NUMMER>", match_tag):
            tag_type = "R"
        elif re.match("<RAPPORT[-_]ID.C[-_]NUMMER>", match_tag):
            tag_type = "C"
        elif re.match("<RAPPORT[-_]ID.DPA[-_]NUMMER>", match_tag):
            tag_type = "DPA"
        elif re.match("<RAPPORT[-_]ID.RPA[-_]NUMMER>", match_tag):
            tag_type = "RPA"

        # Choose prefix based on tag type override or general distribution
        if tag_type and tag_type in config["type_overrides"]:
            override = config["type_overrides"][tag_type]
            types = list(override.keys())
            weights = list(override.values())
        else:
            types = list(config["type_probabilities"].keys())
            weights = list(config["type_probabilities"].values())

        number_type = random.choices(types, weights=weights)[0]

        # Optionally extend the prefix
        extension = random.choices(
            config["extensions"]["choices"], weights=config["extensions"]["weights"]
        )[0]
        if extension:
            number_type += extension

        # Generate spacing and numeric part
        space = random.choices(
            config["space"]["choices"], weights=config["space"]["weights"]
        )[0]
        separator = " " if space else ""

        number_length = random.randint(
            config["number_length_range"]["min"], config["number_length_range"]["max"]
        )

        number = (
            self.generate_random_number_sequence(2)
            + "-"
            + self.generate_random_number_sequence(number_length)
        )

        return f"{number_type}{separator}{number}"

    def hips_phi_number(self, match) -> str:
        length = random.randint(6, 9)
        new_phinumber = self.generate_random_number_sequence(length)
        return new_phinumber

    def hips_age(self, match) -> str:
        # Generate age based on the age distribution fitted to the data of Radboudumc
        reconstructed_gmm = GaussianMixture(
            n_components=len(self.age_distribution["weights"])
        )
        reconstructed_gmm.means_ = self.age_distribution["means"]
        reconstructed_gmm.covariances_ = self.age_distribution["covariances"]
        reconstructed_gmm.weights_ = self.age_distribution["weights"]

        age = int(reconstructed_gmm.sample(1)[0][0])
        return str(age)

    def hips_person_name_abbreviation(self, match) -> str:
        config = self.weights_config["person_name_abbreviation"]
        based_on_name = random.random() < config["abbreviation_based_on_name"]

        if based_on_name:
            config = config["based_on_name"]
            # Pick names
            family_name = random.choice(self.common_names["family_names"])
            first_name = random.choice(self.common_names["first_names"])

            capitalize = random.random() < config["capitalize"]
            capitalize_all = random.random() < config["capitalize_all"]
            add_space = random.random() < config["add_space"]
            number_of_first_name_letters = random.choices(
                config["number_of_first_name_letters"]["choices"],
                weights=config["number_of_first_name_letters"]["weights"],
            )[0]

            number_of_family_name_letters = random.choices(
                config["number_of_family_name_letters"]["choices"],
                weights=config["number_of_family_name_letters"]["weights"],
            )[0]

            # Enforce the rule: if first name has 0 letters, family name can't have 1
            if number_of_first_name_letters == 0 and number_of_family_name_letters == 1:
                # Re-roll until it's not 1
                valid_family_choices = [
                    val
                    for val in config["number_of_family_name_letters"]["choices"]
                    if val != 1
                ]
                valid_weights = [
                    w
                    for v, w in zip(
                        config["number_of_family_name_letters"]["choices"],
                        config["number_of_family_name_letters"]["weights"],
                    )
                    if v != 1
                ]
                number_of_family_name_letters = random.choices(
                    valid_family_choices, weights=valid_weights
                )[0]

            if capitalize:
                family_name = self.capitalize_words_except_infixes(
                    family_name, self.infixes["infixes"]
                )
                first_name = self.capitalize_words_except_infixes(
                    first_name, self.infixes["infixes"]
                )

            name_abbreviation = "".join(
                [
                    first_name[i]
                    for i in range(min(number_of_first_name_letters, len(first_name)))
                ]
            )

            if add_space:
                name_abbreviation += " "

            name_abbreviation += self.abbreviate_name(
                family_name,
                surname_letters=number_of_family_name_letters,
                infix_list=self.infixes["infixes"],
            )

            if capitalize_all:
                name_abbreviation = name_abbreviation.upper()
            return name_abbreviation.strip()

        else:
            config = config["random"]
            # Choose length of abbreviation
            length = np.random.choice(
                config["length_distribution"]["choices"],
                p=config["length_distribution"]["weights"],
            )

            # Prepare abbreviation
            name_abbreviation = ""
            abbreviated_infixes = sorted(
                list(
                    set(
                        [
                            infix[0].strip(
                                " .,'\"-"
                            )  # remove unwanted leading characters
                            for infix in self.infixes["infixes"]
                            if infix
                            and infix[0].strip(
                                " .,'\"-"
                            )  # ensure non-empty after stripping
                        ]
                    )
                )
            )

            for i in range(length):
                # Choose letter case
                uppercase_prob = (
                    config["uppercase_first"] if i == 0 else config["uppercase_rest"]
                )
                uppercase = np.random.rand() < uppercase_prob

                # Pick a character based on distribution
                character = np.random.choice(
                    list(self.character_distribution.keys()),
                    p=list(self.character_distribution.values()),
                )
                name_abbreviation += (
                    character.upper() if uppercase else character.lower()
                )

                # Occasionally add a space
                if np.random.rand() < config["add_space"]:
                    name_abbreviation += " "

                # Occasionally add an abbreviated infix
                if np.random.rand() < config["add_infix"]:
                    name_abbreviation += np.random.choice(abbreviated_infixes)

            return name_abbreviation.strip()

    def hips_hospital(self, match) -> str:
        config = self.weights_config["hospital"]

        # Probabilistic controls
        use_observed = random.random() < config["use_observed"]
        make_uppercase = random.random() < config["make_uppercase"]
        make_lowercase = random.random() < config["make_lowercase"]
        add_typing_error = random.random() < config["add_typing_error"]
        add_hospital_word = random.random() < config["add_hospital_word"]
        add_word_at_end = random.random() < config["add_word_at_end"]
        make_word_title = random.random() < config["hospital_word_title"]

        if use_observed:
            hospital_name = np.random.choice(self.observed_hospital_names)
        else:
            hospital = self.hospitals.sample(1).iloc[0]
            full_names = hospital["Ziekenhuis"].split(",")
            abbreviations = (
                hospital["Afkorting"].split(",")
                if isinstance(hospital["Afkorting"], str)
                else []
            )
            places = hospital["Plaats"].split(",") + hospital["Provincie"].split(",")
            name = np.random.choice(full_names + abbreviations)
            place = np.random.choice(places)
            pattern = np.random.choice(config["patterns"])
            hospital_name = pattern.format(name=name, place=place)

            if add_hospital_word:
                word = random.choices(
                    config["hospital_word_choices"]["choices"],
                    weights=config["hospital_word_choices"]["weights"],
                )[0]
                if make_word_title:
                    word = word.title()
                sep = np.random.choice(["", " "], p=[0.1, 0.9])
                if add_word_at_end:
                    hospital_name = hospital_name + sep + word
                else:
                    hospital_name = word + sep + hospital_name

        # Adjust case
        if make_uppercase:
            hospital_name = hospital_name.upper()
        elif make_lowercase:
            hospital_name = hospital_name.lower()

        # Add optional typo
        if add_typing_error:
            hospital_name = self.add_spelling_error(hospital_name)

        return hospital_name

    def hips_accreditation_number(self, match) -> str:
        # Generate a random accreditation number
        new_accreditation_number = "M" + self.generate_random_number_sequence(3)
        return new_accreditation_number

    def hips_study_name(self, match) -> str:
        config = self.weights_config["study_name"]

        # Choose study name (randomly handle aliases)
        study_pool = self.study_names["study_pool"]
        base_name = random.choice(study_pool)
        study_name = (
            random.choice(base_name)
            if isinstance(base_name, (list, tuple))
            else base_name
        )

        # Choose postfix and infix
        postfix = random.choices(
            config["postfix"]["choices"], weights=config["postfix"]["weights"]
        )[0]
        infix = (
            random.choices(
                config["infix"]["choices"], weights=config["infix"]["weights"]
            )[0]
            if postfix
            else ""
        )

        # Compose base study name
        study_name = study_name + infix + postfix if postfix else study_name

        # Decide whether to add UZR number
        add_number_prob = (
            config["add_number"]["if_postfix_is_studiecode"]
            if postfix == "studiecode"
            else config["add_number"]["default"]
        )
        if random.random() < add_number_prob:
            study_name += " UZR" + self.generate_random_number_sequence(4)

        # Add random noise
        if random.random() < config["add_typing_error"]:
            study_name = self.add_spelling_error(study_name)

        if random.random() < config["all_uppercase"]:
            study_name = study_name.upper()
        elif random.random() < config["all_lowercase"]:
            study_name = study_name.lower()

        if random.random() < config["remove_spaces"]:
            study_name = study_name.replace(" ", "")

        return study_name

    @property
    def hips_disclaimer(self) -> str:
        if self.internal_use:
            return "##############################\nDISCLAIMER: \nTHIS REPORT HAS BEEN ANONYMIZED BY REPLACING PATIENT HEALTH INFORMATION WITH RANDOM SURROGATES EXCEPT FOR DATES AND TIMES.\nANY RESEMBLANCE TO REAL PERSONS, LIVING OR DEAD, IS PURELY COINCIDENTAL.\nTHIS VERSION IS FOR INTERNAL USE ONLY.\n##############################\n\n"
        else:
            return "##############################\nDISCLAIMER: \nTHIS REPORT HAS BEEN ANONYMIZED BY REPLACING PATIENT HEALTH INFORMATION WITH RANDOM SURROGATES.\nANY RESEMBLANCE TO REAL PERSONS, LIVING OR DEAD, IS PURELY COINCIDENTAL.\n##############################\n\n"

    def add_hips_disclaimer(self, report: str) -> str:
        return self.hips_disclaimer + report

    def apply_hips(
        self, report: str, seed: int = 42, ner_labels: list[tuple[int, int, str]] = None
    ):
        # Setting seed
        np.random.seed(seed)
        random.seed(seed)

        for pattern, surrogate_function in [
            ("<PERSOON>", self.hips_person_names),
            ("<DATUM>", self.hips_dates),
            ("<TIJD>", self.hips_time),
            ("<TELEFOONNUMMER>", self.hips_phone_numbers),
            ("<PATIENTNUMMER>", self.hips_patient_id),
            ("<ZNUMMER>", self.hips_z_number),
            ("<PLAATS>", self.hips_locations),
            ("<RAPPORT[_-]ID>", self.hips_rapport_id),
            ("<RAPPORT[_-]ID\.(T|R|C|DPA|RPA)[_-]NUMMER>", self.hips_rapport_id),
            ("<PHINUMMER>", self.hips_phi_number),
            ("<LEEFTIJD>", self.hips_age),
            ("<PERSOONAFKORTING>", self.hips_person_name_abbreviation),
            ("<ZIEKENHUIS>", self.hips_hospital),
            ("<ACCREDATIE_NUMMER>", self.hips_accreditation_number),
            ("<STUDIE[_-]NAAM>", self.hips_study_name),
        ]:
            pattern_matches = list(re.finditer(pattern, report, flags=re.IGNORECASE))
            pattern_matches_sorted = sorted(
                pattern_matches, key=lambda x: x.start(), reverse=True
            )
            for pattern_match in pattern_matches_sorted:
                surrogate = surrogate_function(pattern_match)
                report = (
                    report[: pattern_match.start()]
                    + surrogate
                    + report[pattern_match.end() :]
                )
                if ner_labels is not None:
                    shift = len(surrogate) - len(pattern_match.group())
                    ner_labels = [
                        (
                            start + (shift if start > pattern_match.start() else 0),
                            end + (shift if end > pattern_match.start() else 0),
                            label,
                        )
                        for (start, end, label) in ner_labels
                    ]

        # Add disclaimer that the report has been pseudonymized
        report = self.add_hips_disclaimer(report)
        if ner_labels is not None:
            # Shift labels to the right after adding the disclaimer
            ner_labels = [
                (
                    start + len(self.hips_disclaimer),
                    end + len(self.hips_disclaimer),
                    label,
                )
                for start, end, label in ner_labels
            ]

        if ner_labels is not None:
            return report, ner_labels
        else:
            return report
