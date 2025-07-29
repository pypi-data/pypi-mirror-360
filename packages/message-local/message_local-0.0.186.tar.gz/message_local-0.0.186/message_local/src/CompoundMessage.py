# TODO Please make sure every src file will have a test file i.e. CompoundMessage
import json
import random
from collections import defaultdict
from functools import lru_cache

from criteria_local.criteria_profile import CriteriaProfile
from database_mysql_local.generic_crud import GenericCRUD
from language_remote.lang_code import LangCode
from logger_local.MetaLogger import MetaLogger
from profile_local.profiles_local import ProfilesLocal
from queue_local.database_queue import DatabaseQueue
from user_context_remote.user_context import UserContext
from variable_local.template import ReplaceFieldsWithValues

from .MessageChannels import MessageChannel
from .MessageConstants import object_message
from .MessageTemplates import MessageTemplates
from .Recipient import Recipient

RECIPIENTS_LIMIT_PER_COMPOUND_MESSAGE = 2
JSON_VERSION = "240416"  # TODO: make it generic


class CompoundMessage(GenericCRUD, metaclass=MetaLogger, object=object_message):
    # TODO Shall we change the campaign_id to campaign_criteria_set_id?
    def __init__(self, *, campaign_id: int = None, message_template_id: int = None, original_body: str = None,
                 original_subject: str = None,
                 recipients: list[Recipient] = None, message_id: int = None, is_test_data: bool = False,
                 form_id: int = None, is_debug: bool = False,
                 # TODO save_additional_parameters_dict
                 is_require_moderator: bool = True, save_additional_parameters: dict = None):
        """Initializes the CompoundMessage instance and sets the compound message in the instance and in the database"""
        super().__init__(default_entity_name="message", default_schema_name="message", default_table_name="message_table",
                         default_view_table_name="message_view", default_column_name="message_id",
                         is_test_data=is_test_data)

        self.campaign_id = campaign_id
        self.message_template_id = message_template_id
        self.__original_body = original_body
        self.__original_subject = original_subject
        self._recipients = recipients
        self.message_ids = [message_id] if message_id else []
        self.form_id = form_id
        self.is_debug = is_debug
        self.__compound_message = {}
        self.is_require_moderator = is_require_moderator
        self.save_additional_parameters = save_additional_parameters or {}

        self.profile_local = ProfilesLocal(is_test_data=is_test_data)
        self.message_template = MessageTemplates(is_test_data=is_test_data)
        self.criteria_profile = CriteriaProfile(is_test_data=is_test_data)
        self.user_context = UserContext()
        self.queue = None

        self.set_compound_message_after_text_template()

    # TODO If it is being used only for outgoing messaeges, shall we rename the method to get_outgoing_messages_queue()
    def get_queue(self):
        # TODO Shall we change self.queue to self.outgoing_message_queue so it will be easier to search the code in the IDE
        if not self.queue:
            self.queue = DatabaseQueue(schema_name="message", table_name="message_table",
                                       view_name="message_view", queue_item_id_column_name="message_id",
                                       is_test_data=self.is_test_data)
        queue = self.queue
        return queue

    @lru_cache
    def _get_message_template_ids_with_weights_by_campaign_id(self, campaign_id: int) -> list[dict]:
        """Returns a list of possible template ids from the campaign"""
        message_template_ids_with_weights = self.select_multi_dict_by_where(
            schema_name="campaign_message_template", view_table_name="campaign_message_template_view",
            select_clause_value="message_template_id, percent",
            where="campaign_id=%s AND message_template_id IS NOT NULL", params=(campaign_id,))
        if not message_template_ids_with_weights:
            raise Exception(
                f"No message_template_id found for campaign_id={campaign_id} in campaign_message_template_view")
        return message_template_ids_with_weights

    def _get_random_weighted_message_template_id(self, campaign_id: int) -> int:
        # percent = 0.7 -> This Message Template should be sent in 70% of the cases.
        # percent = None -> equal distribution
        message_template_ids_with_weights = self._get_message_template_ids_with_weights_by_campaign_id(
            campaign_id)
        weights = [row["percent"] or 1 / len(message_template_ids_with_weights)
                   for row in message_template_ids_with_weights]
        message_templates = [row["message_template_id"]
                             for row in message_template_ids_with_weights]
        random_message_template_id = random.choices(
            message_templates, weights=weights, k=1)[0]
        self.logger.info("Choosed random message_template_id", object={
            "random_message_template_id": random_message_template_id, "campaign_id": campaign_id,
            "message_template_ids_with_weights": message_template_ids_with_weights})
        return random_message_template_id

    # TODO Why this code is commented? - Please always include a comment when commenting so it will be more efficient.
    # def get_criteria_set_ids_per_message_template_id(self, message_template_ids: list[int]) -> dict[int, list[int]]:
    #     placeholders = ", ".join(["%s"] * len(message_template_ids))
    #     query = f"""
    #     SELECT criteria_set_id, message_template_view.message_template_id AS message_template_id
    #         FROM message_template.message_template_view
    #              JOIN message_template.message_template_message_template_text_block_view AS message_template_message_template_text_block
    #                   ON message_template_message_template_text_block.message_template_id =
    #                      message_template_view.message_template_id
    #              JOIN message_template.message_template_text_block_table AS message_template_text_block
    #                   ON message_template_text_block.message_template_text_block_id =
    #                      message_template_message_template_text_block.message_template_text_block_id
    #         WHERE criteria_set_id IS NOT NULL
    #             AND message_template_view.message_template_id IN ({placeholders})
    #       """  # noqa
    #     self.cursor.execute(query, message_template_ids)
    #
    #     results = self.convert_multi_to_dict(rows=self.cursor.fetchall(),
    #                                          select_clause_value="message_template_id, criteria_set_id")
    #     criteria_set_ids_per_message_template_id = defaultdict(list)
    #     for row in results:
    #         criteria_set_ids_per_message_template_id[row["message_template_id"]].append(row["criteria_set_id"])
    #     return criteria_set_ids_per_message_template_id

    @lru_cache
    def get_recipients_by_criteria_set_ids(self, criteria_set_ids: tuple[int, ...]) -> list[Recipient]:
        query = """
            SELECT phone_profile.full_number_normalized           AS phone_number,
                   phone_profile.`profile.main_email_address`     AS email_address,
                   profile_ml.title                               AS title,
                   profile_ml.lang_code                           AS lang_code_str,
                   profile_ml.profile_id                          AS profile_id,
                   `person.first_name`								AS first_name
            FROM phone_profile.phone_profile_general_view AS phone_profile
                     JOIN profile.profile_ml_view AS profile_ml
                          ON phone_profile.profile_id = profile_ml.profile_id
        """
        all_profile_ids = []
        if criteria_set_ids:  # otherwise get all profiles
            profile_ids_per_criteria_set_id = self.criteria_profile.get_profile_ids_per_criteria_set_id(
                criteria_set_ids)
            all_profile_ids = list(set([profile_id for profile_ids in profile_ids_per_criteria_set_id.values()
                                        for profile_id in profile_ids]))
            if not all_profile_ids:
                return []
            query += f"WHERE profile_ml.profile_id IN ({', '.join(['%s'] * len(all_profile_ids))})"
        self.cursor.execute(query, all_profile_ids)
        result = self.convert_multi_to_dict(
            rows=self.cursor.fetchall(),
            select_clause_value="phone_number, email_address, title, lang_code_str, profile_id, first_name")
        profile_dicts = defaultdict(list)
        for row in result:
            profile_dicts[row["profile_id"]].append(row)

        if set(all_profile_ids) - set(profile_dicts.keys()):
            self.logger.warning("Failed to find names for the follwoing profile ids:", object={
                "missing_profile_ids": sorted(set(all_profile_ids) - set(profile_dicts.keys()))})
        recipients = []
        for profile_id, profile_dicts in profile_dicts.items():
            profile_dict = profile_dicts[0]
            title_per_lang_code_str = {
                row["lang_code_str"]: row["title"] for row in profile_dicts}
            recipients.append(Recipient(profile_id=profile_id, title_per_lang_code_str=title_per_lang_code_str,
                                        telephone_number=profile_dict["phone_number"],
                                        email_address_str=profile_dict["email_address"],
                                        first_name=profile_dict["first_name"],))
        self._recipients = recipients
        return recipients

    def set_compound_message_after_text_template(
            self, campaign_id: int = None, message_template_id: int = None, body: str = None, subject: str = None,
            recipients: list[Recipient] = None, message_id: int = None, form_id: int = None,
            is_debug: bool = False, is_require_moderator: bool = True) -> None:
        """Sets the compound message in the instance and in the database."""

        # Allow overiding instance vars
        campaign_id = campaign_id or self.campaign_id
        message_template_id = message_template_id or self.message_template_id
        body = body or self.__original_body
        subject = subject or self.__original_subject
        self._recipients = recipients or self._recipients or []
        message_id = message_id or (
            self.message_ids[0] if self.message_ids else None)
        form_id = form_id or self.form_id
        is_debug = is_debug or self.is_debug
        is_require_moderator = is_require_moderator or self.is_require_moderator

        if not self._recipients and campaign_id:
            # Get campaign recipients:
            criteria_set_ids = self.criteria_profile.get_criteria_set_ids_list_by_campaign_id(
                campaign_id=campaign_id)
            self._recipients = self.get_recipients_by_criteria_set_ids(
                criteria_set_ids)

        compound_message = {"json_version": JSON_VERSION, "data": {}}
        if message_id:
            # get compound message from the db:
            compound_message_dict = self.select_one_value_by_column_and_value(
                select_clause_value="compound_message_json", column_value=message_id)
            if compound_message_dict is None:
                raise Exception(
                    f"No compound_message_json found for message_id={message_id}")
            self.__compound_message = json.loads(compound_message_dict)
            return

        if body:
            textblocks_and_attributes = [{"default_body_template": body,
                                          "default_subject_template": subject}]

        elif form_id:  # If body is not given, get it from the database
            textblocks_and_attributes = self.message_template.get_textblocks_and_attributes_by_form_id(
                form_id)
            if not self._recipients:
                # message_template_ids = [message_template_id] or [
                #     row["message_template_id"] for row in textblocks_and_attributes]
                # criteria_set_ids_per_message_template_id = self.get_criteria_set_ids_per_message_template_id(
                #     message_template_ids)  # TODO: criteria per message template
                # criteria_set_ids = [criteria_set_id for criteria_set_ids in
                #                     criteria_set_ids_per_message_template_id.values()
                #                     for criteria_set_id in criteria_set_ids]
                self._recipients = [Recipient(profile_id=self.user_context.get_effective_profile_id(),
                                              preferred_lang_code_str=self.user_context.get_effective_profile_preferred_lang_code().value,
                                              user_id=self.user_context.get_effective_user_id(),
                                              first_name=self.user_context.get_real_name())]
        else:
            textblocks_and_attributes = None
            if campaign_id and not message_template_id:
                message_template_id = self._get_random_weighted_message_template_id(
                    campaign_id=campaign_id)
            if message_template_id:
                textblocks_and_attributes = self.message_template.get_textblocks_and_attributes_by_message_template_id(
                    message_template_id)
        if not textblocks_and_attributes:
            raise Exception(f"No text blocks found for message_template_id={message_template_id} ("
                            f"campaign_id={campaign_id}) or form_id={form_id}")
        if not self._recipients:
            raise Exception(
                f"No recipients found for campaign_id={campaign_id} or form_id={form_id}")

        grouped_textblocks_and_attributes = self._get_grouped_textblocks_and_attributes(
            textblocks_and_attributes)
        for channel in MessageChannel:
            compound_message_dict = self.create_compound_message_dict(
                grouped_textblocks_and_attributes=grouped_textblocks_and_attributes, channel=channel,
                form_id=form_id, recipients=self._recipients, is_debug=is_debug)
            if compound_message_dict:
                compound_message["data"][channel.name] = compound_message_dict

        if compound_message["data"]:
            self.message_ids = self._split_and_push_compound_message(
                compound_message, is_require_moderator)

        self.__compound_message = compound_message
        self.logger.debug(object=locals())

    def _split_and_push_compound_message(self, compound_message: dict, is_require_moderator: bool) -> list:
        all_profile_ids = sorted({
            profile["profile_id"]
            for channel_key, channel_value in compound_message["data"].items()
            for page in channel_value["Page"]
            for message_template in page["MessageTemplates"]
            for text_block in message_template["MessageTemplateTextBlocks"]
            for profile in text_block["Profiles"]})

        if len(all_profile_ids) <= RECIPIENTS_LIMIT_PER_COMPOUND_MESSAGE:  # for performance reasons
            message_ids = [self._push_compound_message(
                compound_message, is_require_moderator)]
            return message_ids

        message_ids = []
        for i in range(0, len(all_profile_ids), RECIPIENTS_LIMIT_PER_COMPOUND_MESSAGE):
            profile_ids = all_profile_ids[i:i +
                                          RECIPIENTS_LIMIT_PER_COMPOUND_MESSAGE]
            self.logger.info(f"Processing profiles: {profile_ids}")
            mini_compound_message = {
                'data': {},
                'json_version': compound_message['json_version']
            }
            for channel_key, channel_value in compound_message['data'].items():
                mini_channel_value = {
                    key: channel_value[key] for key in channel_value.keys() if key != 'Page'}
                mini_channel_value['Page'] = []
                for page in channel_value['Page']:
                    mini_page = {
                        key: page[key] for key in page.keys() if key != 'MessageTemplates'}
                    mini_page['MessageTemplates'] = []
                    for message_template in page['MessageTemplates']:
                        mini_message_template = {key: message_template[key] for key in message_template.keys()
                                                 if key != 'MessageTemplateTextBlocks'}
                        mini_message_template['MessageTemplateTextBlocks'] = []
                        for text_block in message_template['MessageTemplateTextBlocks']:
                            profile_blocks = [profile_block for profile_block in text_block['Profiles']
                                              if profile_block["profile_id"] in profile_ids]
                            if profile_blocks:
                                mini_text_block = {key: text_block[key] for key in text_block.keys() if
                                                   key != 'Profiles'}
                                mini_text_block['Profiles'] = profile_blocks
                                mini_message_template['MessageTemplateTextBlocks'].append(
                                    mini_text_block)

                        if mini_message_template['MessageTemplateTextBlocks']:
                            mini_page['MessageTemplates'].append(
                                mini_message_template)

                    if mini_page['MessageTemplates']:
                        mini_channel_value["Page"].append(mini_page)

                if mini_channel_value["Page"]:
                    mini_compound_message['data'][channel_key] = mini_channel_value

            message_id = self._push_compound_message(
                mini_compound_message, is_require_moderator)
            message_ids.append(message_id)
        return message_ids

    def _push_compound_message(self, compound_message: dict, is_require_moderator: bool) -> int:
        # TODO data_dict -> outgoing_message_dict
        # TODO Can we also add message_template_id to outgoing_message_dict
        data_dict = {
            "compound_message_json": json.dumps(compound_message),
            "compound_message_json_version": JSON_VERSION,
            "is_require_moderator": is_require_moderator}
        data_dict.update(self.save_additional_parameters)
        message_id = self.get_queue().push(data_dict)
        return message_id

    @staticmethod
    def _is_processed(*, profile_id: int, message_template_text_block_id: int, processed_text_blocks: list) -> bool:
        is_processed = any(processed_text_block["profile_id"] == profile_id and
                           processed_text_block["message_template_text_block_id"] == message_template_text_block_id
                           for processed_text_block in processed_text_blocks
                           )
        return is_processed

    # TODO recipients -> recipients_list
    # TODO recipients means people, contacts, users, or profiles? - Let's discuss
    def get_profiles_blocks(self, *, text_block: dict, recipients: list[Recipient],
                            content_per_language: dict, possible_answers_per_question_id: dict,
                            processed_text_blocks: list) -> list[dict]:
        if text_block.get("criteria_set_id"):
            potentials_recipients = self.criteria_profile.get_profile_ids_per_criteria_set_id(
                criteria_set_ids=(text_block["criteria_set_id"], )).get(text_block["criteria_set_id"], [])
        else:
            potentials_recipients = [recipient.get_profile_id()
                                     for recipient in recipients]

        profiles_blocks = []
        for recipient in recipients:
            profile_id = recipient.get_profile_id()
            if recipient.get_profile_id() not in potentials_recipients:
                continue
            if self._is_processed(profile_id=profile_id,
                                  message_template_text_block_id=text_block.get(
                                      "message_template_text_block_id"),
                                  processed_text_blocks=processed_text_blocks):
                continue
            question_id = text_block.get("question_id")
            profile_block = {
                "profile_id": profile_id,
                "preferred_language": self.profile_local.get_preferred_lang_code_by_profile_id(profile_id).value,
                "subject_per_language": {
                    lang_code_str: self._process_text_block(
                        content, recipient, lang_code_str)
                    for lang_code_str, content in content_per_language[question_id]["subject_per_language"].items()},
                "body_per_language": None if question_id else {
                    lang_code_str: self._process_text_block(
                        content, recipient, lang_code_str)
                    for lang_code_str, content in content_per_language[question_id]["body_per_language"].items()},
                "question_per_language": None if not question_id else {
                    lang_code_str: self._process_text_block(content, recipient, lang_code_str) for
                    lang_code_str, content in
                    content_per_language[question_id]["question_per_language"].items()},
                "question_id": question_id,
                "variable_id": text_block.get("variable_id"),
                # TODO: get the answer if we already have it
                "default_question_possible_answer_id": text_block.get("default_question_possible_answer_id"),
                "is_visible": text_block.get("message_template_text_block_is_visible"),
                "is_required": text_block.get("is_required") or False,
                "possible_answers": possible_answers_per_question_id[question_id]
            }
            if profile_block not in profiles_blocks and (profile_block["subject_per_language"] or
                                                         profile_block["body_per_language"] or
                                                         profile_block["question_per_language"]):
                profiles_blocks.append(profile_block)
                processed_text_blocks.append({
                    "profile_id": profile_id,
                    "message_template_text_block_id": text_block.get("message_template_text_block_id")})
        return profiles_blocks

    @staticmethod
    def _get_grouped_textblocks_and_attributes(textblocks_and_attributes: list[dict]) \
            -> dict[int, dict[int, list[dict]]]:
        # Group the fetched data by page and message_template_id
        grouped_textblocks_and_attributes = {}
        for row in textblocks_and_attributes:
            if not row:
                continue
            page_number = row.get("form_page", row.get(
                "message_template_text_block_seq", 1))
            message_template_id = row.get("message_template_id")
            if page_number not in grouped_textblocks_and_attributes:
                grouped_textblocks_and_attributes[page_number] = {}
            if message_template_id not in grouped_textblocks_and_attributes[page_number]:
                grouped_textblocks_and_attributes[page_number][message_template_id] = [
                ]
            grouped_textblocks_and_attributes[page_number][message_template_id].append(
                row)
        return grouped_textblocks_and_attributes

    def create_compound_message_dict(self, *, grouped_textblocks_and_attributes: dict, channel: MessageChannel,
                                     form_id: int = None, recipients: list[Recipient], is_debug: bool) -> dict | None:
        """Specs: https://docs.google.com/document/d/1UvdU9WrK7RwMNnLLBwdye9HbUzgMGEG8wsIMxxYrxa4/edit?usp=sharing
Returns dict with the following structure:
form_id: int or missing
form_name: str or missing [if debug=true]
Page[]
    page_number: int
    message_seq_in_page [If debug=true] - Sorted by message_seq_in_page
    MessageTemplates[]
        index_number[]  (min..max)
        index_name: str - i.e. Home/Work (default null)
        message_template_id: int
        message_template_name: str [If debug=true]
        MessageTemplateTextBlocks[]
            message_template_text_block_id: int
            If debug=true:
                message_template_text_block_seq: int - Sorted by message_template_text_block_seq
                message_template_text_block_name: str
                subject_templates{}  - similar to subject_per_language, but on question level
                body_templates{} - message_template_text_block_ml.default_subject_template [If debug=true] Based on Channel
                question_templates{}
            question_schema{}  example: {"type": "string", "title": "First Name" }
            question_uischema{}
            Profiles[] - Generated by message-local-python-package based on message_template_text_block_ml.default_subject_template in the relevant language/channel - Index is profile_id  # noqa
                profile_id: int
                # TODO Shal we call it preferred_lang_code_str?
                preferred_language: str
                subject_per_language = {"en": "..."}
                body_per_language = {"en": "..."} or null
                question_per_language = {"en": "..."} or null
                question_id: int
                variable_id: int
                default_question_possible_answer_id: int
                is_visible: bool or null
                is_required: bool
                possible_answers = [{"en": "..."}]
"""

        compound_message_dict = {"Page": []}
        if form_id:
            compound_message_dict["form_id"] = form_id

        # if is_debug:  TODO
        #     if form_id:
        #         compound_message_dict["form_name"] = textblocks_and_attributes[0]["form_name"]

        processed_text_blocks = []

        # Iterate through the fetched data and structure it into the JSON
        for page_number, message_templates in grouped_textblocks_and_attributes.items():
            page = {
                "page_number": page_number,
                "MessageTemplates": []
            }

            for message_template_id, text_blocks in message_templates.items():
                if not text_blocks:
                    continue
                message_template_data = {
                    "message_template_id": message_template_id,
                    "MessageTemplateTextBlocks": []
                }
                if form_id:
                    # TODO: is it always a range? if so, we can send only the min and max
                    message_template_data["index_number"] = list(
                        range(text_blocks[0].get("min_message_template", 0),
                              text_blocks[0].get("max_message_template", 0) + 1)),
                    # will be filled by the frontend
                    message_template_data["index_name"] = None

                if is_debug:
                    message_template_data["message_template_name"] = text_blocks[0].get(
                        "message_template_name")
                    message_template_data["message_seq_in_page"] = text_blocks[0].get(
                        "form_message_seq_in_page", 1)

                # Group possible answers by question_id
                possible_answers_per_question_id = defaultdict(list)
                for text_block in text_blocks:
                    if text_block.get("possible_answer"):
                        # TODO: multiple languages
                        lang_code_str = text_block["question_ml_lang_code"] or LangCode.ENGLISH.value
                        possible_answers_per_question_id[text_block["question_id"]].append(
                            {lang_code_str: text_block["possible_answer"]})

                # Group questions by language:
                content_per_language = defaultdict(lambda: {"body_per_language": {},
                                                            "subject_per_language": {},
                                                            "question_per_language": {}})

                body_key = (channel.name.lower(
                ) + "_body") if channel != MessageChannel.EMAIL else "email_body_html"
                if f"{body_key}_template" not in text_blocks[0]:
                    return  # no special template for this channel
                field_to_lang_field = {
                    f"{body_key}_template": ("body_per_language", "message_template_text_block_ml_lang_code"),
                    f"{channel.name}_subject_template": (
                        "subject_per_language", "message_template_text_block_ml_lang_code"),
                    "question_title": ("question_per_language", "question_ml_lang_code")}

                text_blocks_by_question_id = defaultdict(list)
                for text_block in text_blocks:
                    text_blocks_by_question_id[text_block.get(
                        "question_id")].append(text_block)

                for question_id, _text_blocks in text_blocks_by_question_id.items():
                    for text_block in text_blocks:
                        for field, (lang_field, lang_code_field) in field_to_lang_field.items():
                            lang_code_str = text_block.get(
                                lang_code_field) or LangCode.ENGLISH.value
                            # Note: question_id can be None
                            if text_block.get(field) and text_block.get("question_id") == question_id:
                                content_per_language[question_id][lang_field][lang_code_str] = text_block[field]

                # remove duplicated text_blocks
                unique_text_blocks = []
                for text_block in text_blocks:
                    columns_to_ignore = ["possible_answer"]
                    for field, (lang_field, lang_code_field) in field_to_lang_field.items():
                        columns_to_ignore.extend([field, lang_code_field])
                    unique_text_block = {
                        k: v for k, v in text_block.items() if k not in columns_to_ignore}
                    if unique_text_block not in unique_text_blocks:
                        unique_text_blocks.append(unique_text_block)

                for text_block in unique_text_blocks:
                    text_block_data = {
                        "message_template_text_block_id": text_block.get("message_template_text_block_id"),
                        "question_schema": text_block.get("question_type_schema_attributes") or text_block.get(
                            "schema_attribute"),
                        "question_uischema": text_block.get("question_type_uischema_attributes") or text_block.get(
                            "uischema_attribute"),
                        "Profiles": self.get_profiles_blocks(
                            text_block=text_block, recipients=recipients, content_per_language=content_per_language,
                            possible_answers_per_question_id=possible_answers_per_question_id,
                            processed_text_blocks=processed_text_blocks)
                    }
                    if not text_block_data["Profiles"]:
                        continue  # There's no one to send to

                    # if channel == MessageChannel.FORM_REACTJS:
                    #     text_block_data["question_schema"] = text_block["question_type_schema_attributes"] or text_block["schema_attribute"]
                    #     text_block_data["question_uischema"] = text_block["question_type_uischema_attributes"] or text_block["uischema_attribute"]

                    if is_debug:
                        text_block_data["message_template_text_block_seq"] = text_block.get(
                            "message_template_text_block_seq", 1)
                        text_block_data["message_template_text_block_name"] = text_block.get(
                            "message_template_text_block_name")
                        text_block_data["subject_templates"] = content_per_language[text_block.get("question_id")][
                            "subject_per_language"]
                        text_block_data["body_templates"] = content_per_language[text_block.get("question_id")][
                            "body_per_language"]
                        text_block_data["question_templates"] = content_per_language[text_block.get("question_id")][
                            "question_per_language"]

                    if text_block_data not in message_template_data["MessageTemplateTextBlocks"]:
                        message_template_data["MessageTemplateTextBlocks"].append(
                            text_block_data)

                if (message_template_data["MessageTemplateTextBlocks"] and
                        message_template_data not in page["MessageTemplates"]):
                    page["MessageTemplates"].append(message_template_data)

            if page["MessageTemplates"] and page not in compound_message_dict["Page"]:
                compound_message_dict["Page"].append(page)

        if not compound_message_dict["Page"]:
            return None
        return compound_message_dict

    # TODO _process_text_block -> _process_message_text_block
    def _process_text_block(self, text_block_body: str, recipient: Recipient, lang_code_str: str) -> str:
        lang_code = LangCode(lang_code_str or LangCode.ENGLISH.value)
        template = ReplaceFieldsWithValues(message=text_block_body,
                                           lang_code=lang_code,
                                           variables=recipient.get_profile_variables())
        # TODO: what to do in case the message contains to.first_name but the recipient has no first name defined in that language? We should take
        # the English otherwise the Heberew
        # TODO get_formatted_message_str()
        processed_text_block_str = template.get_formatted_message(
            # TODO recipient -> recipient_profile
            profile_id=recipient.get_profile_id(),
            kwargs={"to.first_name": recipient.get_first_name_in_lang_code(lang_code),
                    "from.first_name": self.user_context.get_real_first_name(),
                    "from.last_name": self.user_context.get_real_last_name(),
                    })
        return processed_text_block_str

    def get_compound_message_dict(self, channel: MessageChannel = None) -> dict:
        if channel is None:
            return self.__compound_message["data"]
        else:
            compound_message_dict = {
                channel.name: self.__compound_message["data"].get(channel.name, {})}
            if channel != MessageChannel.DEFAULT:
                compound_message_dict["DEFAULT"] = self.__compound_message["data"].get(
                    "DEFAULT", {})
            return compound_message_dict

    def get_compound_message_str(self, channel: MessageChannel = None) -> str:
        return json.dumps(self.get_compound_message_dict(channel=channel))

    @lru_cache
    def get_profile_blocks(self, profile_id: int, channel: MessageChannel) -> list[dict]:
        compound_message_dict = self.get_compound_message_dict(channel=channel)
        if "Page" not in compound_message_dict[channel.name]:
            channel = MessageChannel.DEFAULT

        profile_blocks = []
        for page in compound_message_dict[channel.name].get("Page", {}):
            for message_template in page.get("MessageTemplates", {}):
                for text_block in message_template.get("MessageTemplateTextBlocks", {}):
                    message_template_text_block_id = text_block.get(
                        "message_template_text_block_id", None)
                    for profile_block in text_block.get("Profiles", {}):
                        if profile_block["profile_id"] == profile_id and profile_block not in profile_blocks:
                            profile_block["message_template_text_block_id"] = message_template_text_block_id
                            profile_blocks.append(profile_block)
        return profile_blocks
