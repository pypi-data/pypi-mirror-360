"""
Module Name: compound_message_verification

This module provides a report of what errors are present in the compound message JSON files.

Main Features:
- If the name in the message isn't correct
- If the name in the sentence isn't in the correct language
- If the body text makes sense
"""

import json
import re
import pandas as pd
from database_mysql_local.generic_crud import GenericCRUD


class CompoundMessageVerification:
    """
    Class for performing compound message verification.

    Attributes:
        generic_crud (GenericCRUD): An instance of the GenericCRUD class for the
          'message' schema.
        question_crud (GenericCRUD): An instance of the GenericCRUD class for the
          'question' schema and 'question_ml_table' table.
        profile_ml_crud (GenericCRUD): An instance of the GenericCRUD class for
        the 'profile' schema and 'profile_ml_table' table.
        profile_crud (GenericCRUD): An instance of the GenericCRUD class for the
          'profile' schema and 'profile_table' table.
        user_crud (GenericCRUD): An instance of the GenericCRUD class for the
        'user' schema and 'user_table' table.
        limit (int): The limit for the number of records to retrieve.
        profile_table (None or str): The profile table name.
    """

    def __init__(self, limit=100):
        self.message_crud = GenericCRUD(
            default_entity_name="message", default_schema_name="message")
        self.question_crud = GenericCRUD(default_entity_name="question",
                                         default_schema_name="question", default_table_name="question_ml_table"
                                         )
        self.profile_ml_crud = GenericCRUD(default_entity_name="profile",
                                           default_schema_name="profile", default_table_name="profile_ml_table"
                                           )
        self.profile_crud = GenericCRUD(
            default_entity_name="profile", default_schema_name="profile")
        self.user_crud = GenericCRUD(
            default_entity_name="user", default_schema_name="user")
        self.limit = limit
        self.message_template_text_block_ml_table = GenericCRUD(default_entity_name="message_template",
                                                                default_schema_name="message_template",
                                                                default_table_name="message_template_text_block_ml_table",
                                                                )

    def set_limit(self, limit: int) -> None:
        """
        Set the limit for the number of records to retrieve.

        Args:
            limit (int): The limit for the number of records to retrieve.
        """
        self.limit = limit

    def __grab_data(self, json_string_for_test=None) -> pd.DataFrame:
        """
        Retrieve data from the database.

        Returns:
            pd.DataFrame: The retrieved data as a pandas DataFrame.
        """
        results = self.message_crud.select_multi_dict_by_where(
            select_clause_value="message_id, compound_message_json",
            where="compound_message_json is not null and compound_message_json_version = 240416",
            order_by="updated_timestamp desc",
            limit=self.limit,
        )
        results = pd.DataFrame(results)
        if json_string_for_test is None:
            return results
        return pd.DataFrame(json_string_for_test)

    def __find_profiles_plus_count_plus_template_id(
        self, json_dict: dict
    ) -> tuple[list, int, list]:
        """
        Find profiles in a JSON dictionary.
        Args:
            json_dict (dict): The JSON dictionary.

        Returns:
            list: The list of profiles found.
        """
        profiles = []
        template_ids = []
        count = 0

        def __recursive_find_profiles(data):
            nonlocal count
            if isinstance(data, dict):
                val_len = 0
                for key, value in data.items():
                    if key == "Profiles":
                        profiles.extend(value)
                        count += len(value)
                        val_len = len(value)
                    elif key == "message_template_text_block_id":
                        template_ids.extend([value] * val_len)
                    else:
                        __recursive_find_profiles(value)
            elif isinstance(data, list):
                for item in data:
                    __recursive_find_profiles(item)

        __recursive_find_profiles(json_dict)

        return profiles, count, template_ids

    def __get_channels(self, json_dict: dict) -> tuple[list, list]:
        """
        Find the key right after 'data' in a JSON dictionary.

        Args:
            json_dict (dict): The JSON dictionary.

        Returns:
            str: The key found.
        """
        channels = []
        values = []

        def __recursive_find_key(data):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == "data":
                        if isinstance(v, dict):
                            channels.extend(v.keys())
                            values.extend(v.values())
                        break
                    __recursive_find_key(v)
            elif isinstance(data, list):
                for item in data:
                    __recursive_find_key(item)

        __recursive_find_key(json_dict)

        return channels, values

    def __get_body_from_lang_and_text_block_id(
        self, lang_list: list, text_block_ids: list, body_list: list, channels: list
    ) -> list:
        """
        Get the body from language and text block ID.

        Args:
            lang (str): The language.
            text_block_id (int): The text block ID.

        Returns:
            list of body for text
        """
        string = ""
        for text_block_id, body in zip(text_block_ids, body_list):
            if body is None or body == {} or text_block_id is None:
                continue
            string += "message_template_text_block_id = " + \
                (str(text_block_id)) + " OR "
        string = string[:-4]
        body_temp = pd.DataFrame(
            self.message_template_text_block_ml_table.select_multi_dict_by_where(
                select_clause_value="message_template_text_block_id, "
                + "default_body_template,sms_body_template,"
                + " email_body_html_template, whatsapp_body_template,"
                + "lang_code",
                where=string,
                limit=self.limit,
            )
        )
        final_body = []
        for channel, body_id, lang in zip(channels, text_block_ids, lang_list):
            body_dict = {}

            if body_temp.empty:
                final_body.append(None)
                continue
            row_list = None
            if channel == "SMS":
                if body_temp.loc[body_temp["message_template_text_block_id"] == body_id].empty:
                    final_body.append(None)
                    continue
                row_list = body_temp.loc[
                    body_temp["message_template_text_block_id"] == body_id,
                    ["sms_body_template", "lang_code"],
                ].values.tolist()

            elif channel == "EMAIL":
                if body_temp.loc[
                    body_temp["message_template_text_block_id"] == body_id,
                    "email_body_html_template",
                ].empty:
                    final_body.append(None)
                    continue
                row_list = body_temp.loc[
                    body_temp["message_template_text_block_id"] == body_id,
                    ["lang_code", "email_body_html_template"],
                ].values.tolist()

            elif channel == "WHATSAPP":
                row = body_temp.loc[
                    body_temp["message_template_text_block_id"] == body_id, "whatsapp_body_template"
                ]
                if row.empty:
                    final_body.append(None)
                    continue
                row_list = body_temp.loc[
                    body_temp["message_template_text_block_id"] == body_id,
                    ["lang_code", "whatsapp_body_template"],
                ].values.tolist()
            elif channel == "DEFAULT":
                row = body_temp.loc[
                    body_temp["message_template_text_block_id"] == body_id, "default_body_template"
                ]

                if row.empty:
                    final_body.append(None)
                    continue
                row_list = body_temp.loc[
                    body_temp["message_template_text_block_id"] == body_id,
                    ["lang_code", "default_body_template"],
                ].values.tolist()
            else:
                final_body.append(None)
            for item in row_list:
                body_dict.update({item[0]: item[1]})
            final_body.append(body_dict)
        return final_body

    def __get_profile_list_and_channel_list_by_json_file(
        self, json_file: list, message_ids: list
    ) -> tuple[list, list, list]:
        """
        Get the profile list by JSON file and channels.

        Args:
            json_file (list): The list of JSON files.

        Returns:
            list: The list of profile information and channel information.
        """
        message_template_text_block_ids = []
        profile_info_list = []
        channels = []
        message_id_list = []
        ind = 0

        for json_data in json_file:
            number_of_messages = 0
            channel, channel_dicts = self.__get_channels(json.loads(json_data))

            if channel:
                index = 0
                for value in channel_dicts:
                    entry, count, template_id = self.__find_profiles_plus_count_plus_template_id(
                        value
                    )

                    if entry:
                        message_template_text_block_ids.extend(template_id)
                        profile_info_list.append(entry)
                        channels.extend([channel[index]] * count)

                        index += 1
                        number_of_messages += count

                message_id_list.extend([message_ids[ind]] * number_of_messages)
                ind += 1

        return profile_info_list, channels, message_template_text_block_ids, message_id_list

    def __get_profile_ml_names_for_hebrew(self, profile_id_list: list) -> list:

        hebrew_names = []
        string = ""
        for profile_id in profile_id_list:
            # TODO Replace in all repos 'he' with our enum/constant
            string += "(profile_id = " + (str(profile_id)) + \
                " AND lang_code = 'he')" + " OR "
        string = string[:-4]

        profile_ml_values = self.profile_ml_crud.select_multi_dict_by_where(
            select_clause_value="profile_id, title", where=string
        )
        profile_name_dict = {}
        for profile in profile_ml_values:
            profile_name_dict[profile["profile_id"]] = profile["title"]

        for pf_id in profile_id_list:

            if profile_name_dict.get(pf_id) is None:
                hebrew_names.append(None)
                continue
            name = profile_name_dict.get(pf_id)
            if len(name.split()) == 1:
                hebrew_names.append(name)
            else:
                hebrew_names.append(name.split()[0])

        return hebrew_names

    def __get_profile_table(self, profile_id_list) -> list:
        """
        Get the profile table.

        Args:
            profile_id_list: The list of profile IDs.

        Returns:
            list: The list of first names.
        """

        first_names = []
        user_ids = self.profile_crud.select_multi_tuple_by_where(
            select_clause_value="profile_id, profile.main_user_id",
            where=(
                " OR ".join(
                    ["profile_id = " + str(profile_id)
                     for profile_id in profile_id_list]
                ).replace("OR ", "", 0)
            ),
            limit=self.limit,
        )
        extended_user_id_list = set()
        has_name = []
        for profile_id in profile_id_list:
            found = False
            for user_id in user_ids:
                if profile_id == user_id[0]:
                    extended_user_id_list.add(user_id[1])
                    has_name.append(user_id[1])
                    found = True
                    break
            if not found:
                has_name.append(None)
                found = False
        extended_user_id_list = list(extended_user_id_list)
        user_first_names = self.user_crud.select_multi_tuple_by_where(
            select_clause_value="user_id, first_name",
            where=" OR ".join(
                ["user_id = " + str(user_id)
                 for user_id in extended_user_id_list]
            ).replace("OR ", "", 0),
            limit=self.limit,
        )

        for has_name_value in has_name:
            if has_name_value is not None:
                found = False
                for first_name in user_first_names:
                    if has_name_value == first_name[0]:
                        first_names.append(first_name[1])
                        found = True
                if not found:
                    first_names.append("PF_Deleted_or_Missing")
            else:
                first_names.append("PF_Deleted_or_Missing")
        return first_names

    def __get_question_by_lang_code_and_question_id(self, question_id_list: list) -> dict:
        """
        Get the question by language code and question ID.

        Args:
            lang_list (list): The list of language codes.
            question_id_list (list): The list of question IDs.

        Returns:
            str: The question.
        """
        combined_string = []
        for question_id in question_id_list:
            if question_id is None:
                continue
            # string = f"lang_code = '{lang}' AND question_id = {question_id}"
            string = f"question_id = {question_id}"
            combined_string.append(string)
        combined_string = " OR ".join(combined_string)
        combined_string = combined_string.replace("OR ", "", 0)
        question_temp = self.question_crud.select_multi_tuple_by_where(
            select_clause_value="question_id,lang_code,title",
            where=combined_string,
            limit=self.limit,
        )
        questions_not_missing = self.question_crud.select_multi_value_by_where(
            select_clause_value="question_id", where=combined_string, limit=self.limit
        )
        results = []
        for question_id in question_id_list:
            if question_id not in questions_not_missing:
                results.append("No_question_found")
            else:
                question_dict = {}
                for question in question_temp:
                    if question_id == question[0]:
                        question_dict.update({question[1]: question[2]})
                    if len(question_dict) == 2:
                        break
                results.append(question_dict)

        return results

    def __get_question_id(self, json_file: dict) -> int:
        """
        Get the question ID.

        Args:
            json_file (dict): The JSON file.

        Returns:
            int: The question ID.
        """
        return json_file.get("question_id")

    def __get_preferred_language(self, json_file: dict) -> str:
        """
        Get the preferred language.

        Args:
            json_file (dict): The JSON file.

        Returns:
            str: The preferred language.
        """
        return json_file["preferred_language"]

    def __get_body_per_language(self, json_file: dict) -> str:
        """
        Get the body per language.

        Args:
            json_file (dict): The JSON file.

        Returns:
            str: The body per language.
        """
        if json_file["body_per_language"] is None:
            return None
        return json_file["body_per_language"]

    def __get_question_per_language(self, json_file: dict) -> dict:
        """
        Get the question per language.

        Args:
            json_file (dict): The JSON file.

        Returns:
            dict: The question per language.
        """
        if json_file["question_per_language"] is None:
            return {}
        return json_file["question_per_language"]

    def __get_profile_id(self, json_file: dict) -> int:
        """
        Get the profile ID.

        Args:
            json_file (dict): The JSON file.

        Returns:
            int: The profile ID.
        """
        return json_file.get("profile_id")

    def __is_hebrew(self, string: str) -> bool:
        """
        Check if a string contains Hebrew characters.

        Args:
            string (str): The string to check.

        Returns:
            bool: True if the string contains Hebrew characters, False otherwise.
        """
        return any("\u0590" <= char <= "\u05EA" for char in string)

    def __is_english(self, string: str) -> bool:
        """
        Check if a string contains English characters.

        Args:
            string (str): The string to check.

        Returns:
            bool: True if the string contains English characters, False otherwise.
        """
        return any("\u0041" <= char <= "\u005A" or "\u0061" <= char <= "\u007A" for char in string)

    def check_for_errors(self, data=None):
        """
        Main method for the CompoundMessageVerification class.
        """
        if data is None:
            data = self.__grab_data()
        message_id_list = None
        if isinstance(data["message_id"], int):
            message_id_list = [data["message_id"]]
            data = [data["compound_message_json"]]
        else:
            message_id_list = data["message_id"].tolist()
            data = data["compound_message_json"].tolist()
        data_filtered = []
        message_id_list_filtered = []
        empty_messages = []
        for json_data, message_id in zip(data, message_id_list):
            if json_data == '{"data": {}, "json_version": "240416"}':
                empty_messages.append(
                    "EMPTY MESSAGE ERROR, MESSAGE_ID: " + str(message_id))
                continue
            data_filtered.append(json_data)
            message_id_list_filtered.append(message_id)
        profile_ids = []
        question_ids = []
        preferred_langs = []
        question_per_language = []
        body_list = []
        all_profiles, all_channels, all_message_template_text_block_ids, all_message_ids = (
            self.__get_profile_list_and_channel_list_by_json_file(
                data_filtered, message_id_list_filtered
            )
        )
        index = 0

        for profile in all_profiles:
            for profile_dict in profile:
                profile_ids.append(self.__get_profile_id(profile_dict))
                question_ids.append(self.__get_question_id(profile_dict))
                preferred_langs.append(
                    self.__get_preferred_language(profile_dict))
                question_per_language.append(
                    self.__get_question_per_language(profile_dict))
                body_list.append(self.__get_body_per_language(profile_dict))
                index += 1
        errors = []
        body_errors = []
        count = 0
        for (
            profile_id,
            question_id,

            question_per_lang,
            name,
            question_templates,  # from template
            body_per_lang,
            body_template,
            message_template_text_block_id,
            channel,
            message_id,
            hebrew_name,
        ) in zip(
            profile_ids,
            question_ids,

            question_per_language,
            self.__get_profile_table(profile_ids),
            self.__get_question_by_lang_code_and_question_id(question_ids),
            body_list,
            self.__get_body_from_lang_and_text_block_id(
                preferred_langs, all_message_template_text_block_ids, body_list, all_channels
            ),
            all_message_template_text_block_ids,
            all_channels,
            all_message_ids,
            self.__get_profile_ml_names_for_hebrew(profile_ids),
        ):

            result, error_list = self.__errors_per_lang(
                question_templates, name, question_per_lang, hebrew_name, False
            )
            if result:
                errors.append(
                    ", ".join(
                        (
                            "Question_per_lang_errors: " "Message_id: " +
                            str(message_id),
                            "Channel: " + str(channel),
                            ("Profile_id: " + str(profile_id)),
                            ("Question_id: " + str(question_id)),
                            (
                                "First name of user: "
                                + str(name)
                                + " "
                                + "Hebrew name in profile: "
                                + str(hebrew_name)
                            ),
                            *[
                                f"Question in database: {lang}: {question}"
                                for lang, question in question_templates.items()
                            ],
                            *[
                                f"Question in Json: {lang}: {question}"
                                for lang, question in question_per_lang.items()
                            ],
                            "ERRORS: " + ", ".join(error_list),
                        )
                    )
                )
            result, error_list = self.__errors_per_lang(
                body_template, name, body_per_lang, hebrew_name, True
            )
            if result:
                body_errors.append(
                    ", ".join(
                        (
                            "Body_per_lang_errors: " "Message_id: " +
                            str(message_id),
                            "Channel: " + str(channel),
                            ("Profile_id: " + str(profile_id)),
                            (
                                "First name of user: "
                                + str(name)
                                + " "
                                + "Hebrew name in profile: "
                                + str(hebrew_name)
                            ),
                            ("Question_id: " + str(question_id)),
                            (
                                "Message_template_text_block_id: "
                                + str(message_template_text_block_id)
                            ),
                            ("body in table: " + str(body_template)),
                            *[f"Body in {lang}: {body}" for lang,
                                body in body_per_lang.items()],
                            "ERRORS: " + ", ".join(error_list),
                        )
                    )
                )
            count += 1
        errors = errors + body_errors + empty_messages
        return errors

    def __swap_for_smartlink(self, template: str) -> str:
        if "${{smartlinkUrl(smartlinkType=30001)}}" in template:
            template = template.replace(
                "${{smartlinkUrl(smartlinkType=30001)}}",
                "https://faz4k77vi5.execute-api.us-east-1.amazonaws.com/play1/api/v1/smartlink/e"
                + "xecuteSmartlinkByIdentifier/8QqcT5GMDSDEaM3b3Kl0?isTestData=False",
            )
        return template

    def __error_in_check_language_of_name(
        self,
        lang: str,
        question: str,
        question_template: str,
        name: str,
        error_list: list,
        body: bool,
    ) -> list:
        """
        Check the language of the name in the question.

        Args:
            question_per_lang (dict): The question per language dictionary.
            question_template (str): The question template.

        Returns:
            list: The list of boolean values indicating the language of the name in the question.
        """

        name_from_question = self.__extract_replacement(
            question, question_template, "${{ to.first_name }}"
        )
        if not body:
            if lang == "he":
                if name is None:
                    return True, "HE: No Hebrew Version of name in database"
                elif name_from_question is None and not self.contains_name(question, name):
                    return True, "HE: No Hebrew Version of Name in question"
                elif name_from_question is not None and not self.__is_hebrew(name_from_question):
                    return True, "HE: Name is not in Hebrew in question_per_language"

                elif (
                    "HE: Question in Json doesn't match the question in the template" in error_list
                ):
                    return False, "HE: Question in Json doesn't match the question in the template"
                else:
                    return False, "HE: Name is in Hebrew"
            if lang == "en":
                if name_from_question is None and not self.contains_name(question, name):
                    return True, "EN: No English Version of name in question"
                elif name_from_question is not None and not self.__is_english(name_from_question):
                    return True, "EN: Name is not in English in question_per_language"
                elif (
                    "EN: Question in Json doesn't match the question in the template" in error_list
                ):
                    return False, "EN: Question in Json doesn't match the question in the template"
                else:
                    return False, "EN: Name is in English"
        else:
            if lang == "he":
                if name is None:
                    return True, "HE: No Hebrew Version of name in database"
                elif name_from_question is None and not self.contains_name(question, name):
                    return True, "HE: No Hebrew Version of Name in body_per_language"
                elif name_from_question is not None and not self.__is_hebrew(name_from_question):
                    return True, "HE: Name is not in Hebrew in body_per_language"
                elif (
                    "HE: body_per_lang in Json doesn't match the body in the template" in error_list
                ):
                    return False, "HE: body_per_lang in Json doesn't match the body in the template"

            if lang == "en":
                if name_from_question is None and not self.contains_name(question, name):
                    return True, "EN: No English Version of name in body_per_language"
                elif name_from_question is not None and not self.__is_english(name_from_question):
                    return True, "EN: Name is not in English in body_per_language"
                elif (
                    "EN: body_per_lang in Json doesn't match the body in the template" in error_list
                ):
                    return False, "EN: body_per_lang in Json doesn't match the body in the template"
                else:
                    return False, "EN: Name is in English"
        return False, "ERROR: CRITICAL ERROR"

    def __extract_replacement(
        self, final_question: str, template_string: str, placeholder: str
    ) -> str:
        """
        Extract the replacement from the final question.

        Args:
            final_question (str): The final question.
            template_string (str): The template string.
            placeholder (str): The placeholder.

        Returns:
            str: The extracted replacement.
        """
        # Escape the template string to treat it as a literal string in regex
        escaped_template = re.escape(template_string)

        # Find all placeholders in the template string
        placeholders = re.findall(r"\$\{\{.+?\}\}", template_string)

        # For each placeholder, replace it in the escaped template with a regex capturing group
        for ph in placeholders:
            escaped_ph = re.escape(ph)
            # Replace the placeholder with a capturing group that matches any content
            escaped_template = escaped_template.replace(escaped_ph, r"(.+?)")

        # Compile the modified template string into a regex pattern
        pattern = re.compile(r".*?" + escaped_template,
                             re.IGNORECASE | re.DOTALL)

        # Match the final question string with the compiled pattern
        match = pattern.match(final_question)

        if match:
            # If there's a match, find the group corresponding to the placeholder of interest
            # Assuming placeholders are unique, find the index of the placeholder
            placeholder_index = (
                placeholders.index(placeholder) + 1
            )  # +1 because group 0 is the entire match
            return match.group(placeholder_index)
        return None

    def __question_sentence_has_errors__without_name_swap(
        self, question_template: str, question_in_json: str
    ) -> bool:
        if "${{ to.first_name }}" not in question_template:
            return question_template != question_in_json
        return False

    def __errors_per_lang(
        self,
        question_templates: dict,
        first_name: str,
        question_per_lang: dict,
        hebrew_name: str,
        body: bool,
    ) -> tuple[bool, list]:
        if (
            question_per_lang is None
            or question_per_lang == {}
            or question_templates is None
            or question_templates == "No_question_found"
        ):
            return False, None
        result = False
        error_list = []
        for lang, question in question_templates.items():
            question_templates[lang] = self.__swap_for_smartlink(question)
        for (lang, question_from_json), (lang_template, question_template) in zip(
            question_per_lang.items(), question_templates.items()
        ):
            assert lang == lang_template
            if question_from_json is None or question_template is None:
                continue
            if first_name == "PF_Deleted_or_Missing":
                result = True
                error_list.append("User or Profile is missing or deleted")
                break
            if lang == "he":
                if self.__question_sentence_has_errors__without_name_swap(
                    question_template, question_from_json
                ):
                    result = True
                    if not body:
                        error_list.append(
                            "HE: Question in Json doesn't match the question in the template"
                        )
                    else:
                        error_list.append(
                            "HE: body_per_lang in Json doesn't match the body in the template"
                        )
                    continue
                if (
                    "${{ to.first_name }}" not in question_template
                ):  # if there is no first_name swap
                    continue
                else:
                    if first_name != "PF_Deleted_or_Missing":

                        if self.__error_in_compare_sentence_to_first_name(
                            question_template, hebrew_name, question_from_json
                        ):
                            if not self.contains_name(question_from_json, hebrew_name):
                                result = True
                                if not body:
                                    error_list.append(
                                        "HE: First name in question doesn't match"
                                        + " user name of that language"
                                    )
                                else:
                                    error_list.append(
                                        "HE: First name in body_per_lang doesn't"
                                        + " match user name of that language"
                                    )
                            else:
                                result = True
                                if not body:
                                    error_list.append(
                                        "HE: Question in Json doesn't match the"
                                        + " question in the template"
                                    )
                                else:
                                    error_list.append(
                                        "HE: body_per_lang in Json doesn't match"
                                        + " the body in the template"
                                    )
                        res, err = None, None
                        res, err = self.__error_in_check_language_of_name(
                            lang,
                            question_from_json,
                            question_template,
                            hebrew_name,
                            error_list,
                            body,
                        )
                        if res:
                            result = True
                            error_list.append(err)

            elif lang == "en":
                if self.__question_sentence_has_errors__without_name_swap(
                    question_template, question_from_json
                ):
                    result = True
                    if not body:
                        error_list.append(
                            "EN: Question in Json doesn't match the " + "question in the template"
                        )
                    else:
                        error_list.append(
                            "EN: body_per_lang in Json doesn't match " + "the body in the template"
                        )
                    continue

                if (
                    "${{ to.first_name }}" not in question_template
                ):  # if there is no first_name swap
                    continue
                else:
                    if first_name != "PF_Deleted_or_Missing":

                        if self.__error_in_compare_sentence_to_first_name(
                            question_template, first_name, question_from_json
                        ):
                            if not self.contains_name(question_from_json, first_name):
                                result = True
                                if not body:
                                    error_list.append(
                                        "EN: First name in question doesn't"
                                        + " match user name of that language"
                                    )
                                else:
                                    error_list.append(
                                        "EN: First name in body_per_lang "
                                        + "doesn't match user name of that language"
                                    )
                            else:
                                result = True
                                if not body:
                                    error_list.append(
                                        "EN: Question in Json doesn't match "
                                        + "the question in the template"
                                    )
                                else:
                                    error_list.append(
                                        "EN: body_per_lang in Json doesn't "
                                        + "match the body in the template"
                                    )

                        res, err = None, None
                        res, err = self.__error_in_check_language_of_name(
                            lang,
                            question_from_json,
                            question_template,
                            first_name,
                            error_list,
                            body,
                        )
                        if res:
                            result = True
                            error_list.append(err)

        return result, error_list

    def contains_name(self, question: str, name: str) -> bool:
        """
                Check if the question contains the name.

                Args:
                    question (str): The question.
        p
                Returns:
                    bool: True if the question contains the name, False otherwise.
        """

        # regex pattern to match the word "name" as a whole word
        pattern = rf"\b{name}\b"
        match = re.search(pattern, question)
        return bool(match)

    def __error_in_compare_sentence_to_first_name(
        self, question_template: any, name: any, question_from_json: str
    ) -> bool:
        """
        Compare the sentence to the first name.

        Args:
            sentence (any): The question template.
            name (any): The name.
            old_sentence (str): The question completed in the json.

        Returns:
            bool: True if the first name matches the question, False otherwise.
        """
        name_1 = "PF_Deleted_or_Missing"
        if name is not None:
            name_1 = name

        return question_template.replace("${{ to.first_name }}", name_1) != question_from_json

    def main(self, data=None):
        errors = self.check_for_errors(data)
        with open("compount_message_verification.log", "w", encoding="utf-8") as file:
            for err in errors:
                file.write(err + "\n" + "\n")


if __name__ == "__main__":
    comp = CompoundMessageVerification(1000)
    comp.main()
