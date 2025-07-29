import json
from enum import Enum, auto

from language_remote.lang_code import LangCode
from phones_local.phones_local import PhonesLocal
from variable_local.variables_local import VariablesLocal
from user_external_local.user_externals_local import UserExternalsLocal

DEFAULT_LANG_CODE = LangCode.ENGLISH.value


# TODO Each of them has field_id value in field.field_table, shall we use it?
#   (I didn't find it there)
class ReferenceType(Enum):
    PERSON_ID = auto()
    CONTACT_ID = auto()
    USER_ID = auto()
    PROFILE_ID = auto()


class RecipientType(Enum):
    TELEPHONE_NUMBER = auto()
    EMAIL_ADDRESS = auto()

    UNKNOWN = auto()


class Recipient:
    def __init__(self, contact_id: int = None, person_id: int = None, user_id: int = None, profile_id: int = None,
                 telephone_number: str = None, email_address_str: str = None, preferred_lang_code_str: str = None,
                 first_name: str = None, title_per_lang_code_str: dict[str, str] = None) -> None:
        self.__person_id = person_id
        self.__email_address_str = email_address_str
        self.__contact_id = contact_id
        self.__user_id = user_id
        self.__profile_id = profile_id
        self.__telephone_number = telephone_number
        self.__preferred_lang_code_str = preferred_lang_code_str
        self.__first_name = first_name
        self.__title_per_lang_code_str = title_per_lang_code_str or {}
        for key, value in self.to_dict().items():
            if not key.endswith("id") and key.upper() in RecipientType.__members__:
                self._recipient_type = RecipientType[key.upper()]  # remove the first underscore

        self.__variables_local: VariablesLocal or None = None  # To improve performance, we will get it only when needed.

    def get_profile_variables(self) -> VariablesLocal:
        if self.__variables_local is not None:
            return self.__variables_local
        self.__variables_local = VariablesLocal()
        # TODO: make sure those are stored on the effective_profile_id (using global user_context or sending the user_context).
        self.__variables_local.add(self.__contact_id, "contact_id")
        self.__variables_local.add(self.__person_id, "person_id")
        self.__variables_local.add(self.__user_id, "user_id")
        self.__variables_local.add(self.__profile_id, "profile_id")
        self.__variables_local.add(self.__telephone_number, "telephone_number")
        self.__variables_local.add(self.__email_address_str, "email_address")
        return self.__variables_local

    def get_person_id(self) -> int:
        return self.__person_id

    def get_profile_id(self) -> int:
        return self.__profile_id

    def get_contact_id(self) -> int:
        return self.__contact_id

    def get_user_id(self) -> int:
        return self.__user_id

    def get_first_name(self) -> str:
        return self.__first_name

    def is_email_address(self):
        return self.__telephone_number is not None

    def is_telephone_number(self):
        return self.__telephone_number is not None

    def get_email_address(self):
        return self.__email_address_str

    def get_telephone_address(self):
        return self.__telephone_number is not None

    def get_preferred_lang_code_str(self) -> str:
        # message preferred_lang_code_str() is based on first_name, subject and body
        return self.__preferred_lang_code_str or DEFAULT_LANG_CODE

    def get_preferred_lang_code(self) -> LangCode:
        return LangCode(self.get_preferred_lang_code_str())

    # TODO Shall we move this method to people-local-python-package FirstName class?
    def get_first_name_in_lang_code(self, lang_code: LangCode = None) -> str:
        if not lang_code:
            lang_code = self.get_preferred_lang_code()
        name = self.__title_per_lang_code_str.get(lang_code.value) or self.get_first_name()
        return name

    # TODO region or country_id?
    def get_phone_number_full_normalized(self, region: str = "IL") -> str or None:
        """normalized/canonical phone, telephone number """
        if self.__telephone_number is None:
            return None
        normalized_phone_number = PhonesLocal.normalize_phone_number(
            original_number=self.__telephone_number, region=region)['full_number_normalized']
        return normalized_phone_number

    def to_dict(self):
        init_args = ("contact_id", "person_id", "user_id", "profile_id", "telephone_number",
                     "email_address_str", "preferred_lang_code_str", "first_name", "title_per_lang_code_str")
        return {k.replace("_Recipient__", ""): v for k, v in self.__dict__.items()
                if v is not None and k.replace("_Recipient__", "") in init_args}

    @staticmethod
    def from_dict(json_object: dict) -> 'Recipient':
        return Recipient(**json_object)

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        """This is used when we print a list of recipients"""
        return self.__str__()

    @staticmethod
    def recipients_from_dicts(recipients: list[dict]) -> list['Recipient'] or list or None:
        """get recipients"""
        if not recipients:
            return recipients  # None or []
        return [Recipient.from_dict(recipient) for recipient in recipients]

    @staticmethod
    def recipients_to_dicts(recipients: list['Recipient']) -> list[dict] or list or None:
        """recipients to json"""
        if not recipients:
            return recipients
        return [recipient.to_dict() for recipient in recipients]

    # TODO Shall we move it to user_external package? Shall we rename the method to get_user_external_dict_by_system_id()?
    def get_user_dict_by_system_id(self, system_id: int) -> dict:
        # Return all the usernames and ids that the recipient has in specific system_id
        where = f"system_id = {system_id}"
        if self.__user_id:
            where += f" AND user_id = {self.__user_id}"
        if self.__profile_id:
            where += f" AND profile_id = {self.__profile_id}"
        if self.__person_id:
            where += f" AND person_id = {self.__person_id}"
        if self.__telephone_number:
            where += f" AND `phone.full_number_normalized` = {self.__telephone_number}"

        # TODO create INITIAL_CONDTION and compare to it or add boolean flag
        if where == f"system_id = {system_id}":
            # There are no parameters in this recipient
            user_dict = {"username": list, "user_external_id": list, "phone.full_number_normalized": list}
        else:
            user_dict = UserExternalsLocal.get_recipient_user_dict(where=where)

        return user_dict
