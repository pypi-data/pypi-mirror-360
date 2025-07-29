import json
import time
from datetime import datetime
from functools import lru_cache
from http import HTTPStatus
from typing import List

from api_management_local.api_limit_status import APILimitStatus
from api_management_local.api_mangement_manager import APIManagementsManager
from api_management_local.direct import Direct
from api_management_local.exception_api import (ApiTypeDisabledException,
                                                ApiTypeIsNotExistException,
                                                PassedTheHardLimitException)
from api_management_local.indirect import InDirect
from item_local.item import Item
from logger_local.MetaLogger import MetaLogger
from star_local.exception_star import NotEnoughStarsForActivityException

from .ChannelProviderConstants import (AWS_SES_EMAIL_MESSAGE_PROVIDER_ID,
                                       AWS_SNS_SMS_MESSAGE_PROVIDER_ID,
                                       INFORU_MESSAGE_PROVIDER_ID)
from .CompoundMessage import CompoundMessage
from .MessageChannels import MessageChannel
from .MessageConstants import DEFAULT_HTTP_HEADER, SMS_MESSAGE_LENGTH, object_message
from .MessageImportance import MessageImportance
from .Recipient import Recipient


# TODO recipients -> recipients_list (breaking change)
# TODO: lines not tested - 83, 101, 107, 118-122, 128-139, 151, 162, 167-172, 177-209, 213-253, 259, 265-269, 275, 280, 292, 296, 299
class MessageLocal(Item, CompoundMessage, metaclass=MetaLogger, object=object_message):
    """Message Local Class"""

    def __init__(self, *, recipients: List[Recipient] = None, api_type_id: int = None, campaign_id: int = None,
                 message_template_id: int = None,
                 original_body: str = None, original_subject: str = None,
                 importance: MessageImportance = MessageImportance.MEDIUM, message_id: int = None,
                 is_http_api: bool = None, endpoint_url: str = None, is_debug: bool = False,
                 headers: dict = DEFAULT_HTTP_HEADER, user_external_id: int = None, form_id: int = None,
                 sender_profile_id: int = None, is_test_data: bool = False,
                 is_require_moderator: bool = True) -> None:
        """message_dict contains a list of dicts, each with the following keys:
        ["sms_body_template", "email_subject_template", "email_body_html_template",
        "whatsapp_body_template", "question_id", "question_type_id", "question_title", "question_type_name"]"""
        # TODO We should add all fields from message schema in the database
        # (i.e. message_id, scheduled_sent_timestamp, message_sent_status : MessageSentStatus  ...)

        CompoundMessage.__init__(self, message_id=message_id, campaign_id=campaign_id, is_debug=is_debug,
                                 message_template_id=message_template_id, original_body=original_body, form_id=form_id,
                                 original_subject=original_subject, recipients=recipients, is_test_data=is_test_data,
                                 is_require_moderator=is_require_moderator)
        if not self._recipients:
            raise Exception(
                "recipients parameter is required (couldn't be detected automatically based on the provided data)")

        # init instance variables
        self.importance = importance
        self._is_http_api = is_http_api
        self._api_type_id = api_type_id
        self._endpoint_url = endpoint_url
        self._headers = headers
        self.__user_external_id = user_external_id
        self._campaign_id = campaign_id
        self.__sender_profile_id = sender_profile_id

        # init instances
        self.__indirect = InDirect()
        self.__direct = Direct()
        self.api_management_manager = APIManagementsManager()

        # decide how to send (channel & provider) for each recipient
        self.message_channel_per_recipient_id = {
            recipient.get_profile_id(): self.get_message_channel_by_recipient(recipient)
            for recipient in self._recipients}
        self.provider_id_per_recipient = {recipient.get_profile_id(): self.get_message_provider_id(
            message_channel=self.get_message_channel_by_recipient(recipient), recipient=recipient)
            for recipient in self._recipients}
        # self.message_template_dict_by_campaign_id = self.get_message_template_dict_by_campaign_id(campaign_id=campaign_id)

        # Old code I might need later:
        # if self._campaign_id:
        #     body = self.message_template_dict_by_campaign_id.get(
        #         self._campaign_id).get(recipient.get_preferred_language())
        #     body = self.message_template.get_message_template_textblock_and_attributes(
        #         message_template_id=body, destination_profile_id=recipient.get_profile_id())

    # TODO _data -> _dict
    def insert_message_data(self, message_data: dict) -> int:
        """
        Inserts message data into the database.
        """
        self._validate_args(message_data)
        message_id = self.insert(data_dict=message_data)
        return message_id

    def get_id(self) -> int | None:
        message_id = self.message_ids[0] if self.message_ids else None
        return message_id

    def get_message_channel_by_recipient(self, recipient: Recipient) -> MessageChannel:
        # TODO: return msg_type (sms, email, whatsapp) based on hours, provider availability, msg length, etc.
        """TODO: make sure we can access:
        1. size of message
        2. message contains html or not
        3. country of recipient
        4. time of the day
        5. preferences of the recipient
        6. attachments type and size 7. cost of sending the message"""
        if recipient.get_email_address() is not None:
            message_channel = MessageChannel.EMAIL
        else:
            for _message_channel in MessageChannel:
                if len(self.get_body_text_after_template_processing(
                        recipient=recipient, message_channel=_message_channel)) < SMS_MESSAGE_LENGTH:
                    message_channel = MessageChannel.SMS
                    return message_channel
            message_channel = MessageChannel.WHATSAPP
        return message_channel

    # TODO Let's create logger_table SQL to verify the decision taken by this method (like ...)

    def get_message_channel(self, recipient: Recipient) -> MessageChannel:
        if recipient.get_profile_id() in self.message_channel_per_recipient_id:
            message_channel = self.message_channel_per_recipient_id[recipient.get_profile_id(
            )]
        else:
            message_channel = self.get_message_channel_by_recipient(recipient)
        return message_channel

    # TODO Let's create logger_table SQL to verify the decision taken by this method (like ...)
    @staticmethod
    # TOOD get_message_channel_provider_id
    def get_message_provider_id(*, message_channel: MessageChannel, recipient: Recipient) -> int:
        """return message provider"""
        # TODO: implement the logic for the provider_id (remove +972, etc.)
        # TODO message_channel_provider_id
        # TODO Sending SMS only in Israel, the rest will be subjected to moderation
        # TODO Can we use Israel country_id instead of 972 to make it more generic and readable?
        # TODO Object Oriented wise, I would expect this logic to be in https://github.com/circles-zone/sms-message-local-python-package
        if message_channel == MessageChannel.SMS and recipient.get_phone_number_full_normalized().startswith("972"):
            provider_id = AWS_SNS_SMS_MESSAGE_PROVIDER_ID
        elif message_channel == MessageChannel.EMAIL:
            provider_id = AWS_SES_EMAIL_MESSAGE_PROVIDER_ID
        elif message_channel == MessageChannel.WHATSAPP:
            # TODO: or vonage
            # TODO Can we use WHATSAPP_SELENIUM_MESSAGE_CHANNEL_PROVIDER_ID?
            provider_id = INFORU_MESSAGE_PROVIDER_ID
        else:
            # TODO Can we include the message_id?
            raise Exception(
                "Can't determine the Message Channel Provider for message_channel=" + str(message_channel))

        return provider_id

    @lru_cache
    def get_subject_text_after_template_processing(
            self, *, recipient: Recipient, message_channel: MessageChannel = None) -> str:
        seperator = ", "
        message_channel = message_channel or self.get_message_channel(
            recipient)

        subject = ""
        for block in self.get_profile_blocks(recipient.get_profile_id(), message_channel):
            preferred_language = block["preferred_language"]

            if not block["subject_per_language"]:
                self.logger.warning(
                    f"subject_per_language not found for recipient with profile_id: {recipient.get_profile_id()}."
                )
                continue

            if preferred_language in block["subject_per_language"]:
                if block["subject_per_language"][preferred_language]:
                    subject_block = block["subject_per_language"][preferred_language]
                    if subject_block not in subject:
                        subject += subject_block + seperator
            else:
                self.logger.warning(
                    f"Subject not found for recipient with profile_id: {recipient.get_profile_id()} in language {preferred_language}."
                    f"Available languages for subject: {', '.join(block['subject_per_language'].keys())}."
                )

        return subject

    @lru_cache
    def get_body_text_after_template_processing(
            self, *, recipient: Recipient, message_channel: MessageChannel = None) -> str:
        seperator = "\n"
        message_channel = message_channel or self.get_message_channel(
            recipient)

        body = ""
        for block in self.get_profile_blocks(recipient.get_profile_id(), message_channel):
            preferred_language = block["preferred_language"]
            body_block = None
            if (block["question_per_language"] or {}).get(preferred_language):
                body_block = block["question_per_language"][preferred_language]
            elif (block["body_per_language"] or {}).get(preferred_language):
                body_block = block["body_per_language"][preferred_language]

            if body_block and body_block not in body:
                body += body_block + seperator

        return body.rstrip(seperator)

    def get_sender_profile_id(self, *, recipient: Recipient = None) -> int:
        """determine the sender for each recipient based on (location, groups, campaign.is_dialog_workflow, campaign.default_sender_profile_id ...)"""
        # TODO: implement the logic for the sender_profile_id
        return self.__sender_profile_id  # or campaign_table.default_sender_profile_id

    # api_data To know if to API calls are actually the same and do caching.
    # TODO Do we need user_external as parameter?
    def can_send(self, *, sender_profile_id: int = None, api_data: dict = None, outgoing_body: dict = None,
                 recipient: Recipient = None) -> bool:
        sender_profile_id = sender_profile_id or self.get_sender_profile_id(
            recipient=recipient)
        if self._is_http_api:
            can_send = self.__can_send_direct(
                sender_profile_id=sender_profile_id, api_data=api_data)
        else:
            can_send = self.__can_send_indirect(
                sender_profile_id=sender_profile_id, outgoing_body=outgoing_body)
        return can_send

    # api_data To know if to API calls are actually the same and do caching.
    def __can_send_direct(self, *, sender_profile_id: int, api_data: dict = None) -> bool:
        # TODO: implement sender_profile_id logic
        try:
            try_to_call_api_result = self.__direct.try_to_call_api(
                user_external_id=self.__user_external_id,
                api_type_id=self._api_type_id,
                endpoint_url=self._endpoint_url,
                outgoing_body=api_data,  # data
                outgoing_header=self._headers
            )
            http_status_code = try_to_call_api_result['http_status_code']
            if http_status_code != HTTPStatus.OK.value:
                raise Exception(try_to_call_api_result['response_body_json'])
            else:
                return True
        except PassedTheHardLimitException:
            seconds_to_sleep_after_passing_the_hard_limit = self.api_management_manager.get_seconds_to_sleep_after_passing_the_hard_limit(
                api_type_id=self._api_type_id)
            if seconds_to_sleep_after_passing_the_hard_limit > 0:
                self.logger.info(
                    f"sleeping for {seconds_to_sleep_after_passing_the_hard_limit=} seconds")
                time.sleep(seconds_to_sleep_after_passing_the_hard_limit)
            else:
                self.logger.info(
                    f"No sleeping needed: {seconds_to_sleep_after_passing_the_hard_limit=} seconds")
        except NotEnoughStarsForActivityException:
            self.logger.warning("Not Enough Stars For Activity Exception")

        except ApiTypeDisabledException:
            self.logger.error("Api Type Disabled Exception")

        except ApiTypeIsNotExistException:
            self.logger.error("Api Type Is Not Exist Exception")

        except Exception as exception:
            self.logger.exception(object=exception)
        return False

    def __can_send_indirect(self, *, sender_profile_id: int = None, outgoing_body: dict = None) -> bool:
        # TODO: implement sender_profile_id logic
        http_status_code = None
        try:
            api_check, self.__api_call_id, http_status_code, response_body_json = self.__indirect.before_call_api(
                user_external_id=self.__user_external_id, api_type_id=self._api_type_id,
                endpoint_url=self._endpoint_url,
                outgoing_header=self._headers,
                outgoing_body=outgoing_body
            )
            if response_body_json is None:
                self.__used_cache = False
                if api_check == APILimitStatus.BETWEEN_SOFT_LIMIT_AND_HARD_LIMIT:
                    self.logger.warn("You passed the soft limit")
                if api_check != APILimitStatus.GREATER_THAN_HARD_LIMIT:
                    try:
                        http_status_code = HTTPStatus.OK.value
                    except Exception as exception:
                        self.logger.exception(object=exception)
                        http_status_code = HTTPStatus.BAD_REQUEST.value
                else:
                    self.logger.info("You passed the hard limit")
                    seconds_to_sleep_after_passing_the_hard_limit = self.api_management_manager.get_seconds_to_sleep_after_passing_the_hard_limit(
                        api_type_id=self._api_type_id)
                    if seconds_to_sleep_after_passing_the_hard_limit > 0:
                        self.logger.info(
                            f"sleeping: {seconds_to_sleep_after_passing_the_hard_limit=} seconds")
                        time.sleep(
                            seconds_to_sleep_after_passing_the_hard_limit)
                        # raise PassedTheHardLimitException

                    else:
                        self.logger.info(
                            f"No sleeping needed: {seconds_to_sleep_after_passing_the_hard_limit=} seconds")
            else:
                self.__used_cache = True
                self.logger.info("result from cache")
                http_status_code = HTTPStatus.OK.value
        except ApiTypeDisabledException:
            self.logger.error("Api Type Disabled Exception")

        except ApiTypeIsNotExistException:
            self.logger.error("Api Type Is Not Exist Exception")
        self.logger.info("http_status_code: " + str(http_status_code))
        return http_status_code == HTTPStatus.OK.value

    # TOOO Do we want to send only to one channel or multi-channels of the recipients? - Please add support to campaign_criteria_set_table.number_of_channels_per_recipient  # noqa
    def send(self, *, body: str = None, compound_message_dict: dict = None,
             recipients: List[Recipient] = None, cc: List[Recipient] = None, bcc: List[Recipient] = None,
             scheduled_timestamp_start: datetime = None,
             scheduled_timestamp_end: datetime = None, **kwargs) -> list[int]:
        '''This method supports multiple alternatives to send messages
            1. body only
            2. compound_message created by CompoundMessage class

            1. with/without recipients/to
            2. with/without cc
            3. with/without bcc

            1. Without schedule
            2. With schedule_timestamp_start
            3. With schedule_timestamp_end
            4. With both start and end
        '''
        pass  # this is an abstract method, but we don't want to make this class abstract

    def after_send_attempt(self, *, sender_profile_id: int = None, outgoing_body: json = None,
                           incoming_message: json = None, http_status_code: int = None,
                           response_body: dict | dict = None, recipient: Recipient = None) -> None:
        # TODO: implement sender_profile_id logic
        sender_profile_id = sender_profile_id or self.get_sender_profile_id(
            recipient=recipient)
        if self._is_http_api:
            self.__after_direct_send()
        else:
            self.__after_indirect_send(outgoing_body=outgoing_body,
                                       incoming_message=incoming_message,
                                       http_status_code=http_status_code,
                                       response_body=response_body)

    def display(self):
        print("MessageLocal: " + str(self.__dict__))

    def __after_indirect_send(self, *, outgoing_body: json, incoming_message: json,
                              http_status_code: int, response_body: json):

        self.__indirect.after_call_api(user_external_id=self.__user_external_id,
                                       api_type_id=self._api_type_id,
                                       endpoint_url=self._endpoint_url,
                                       outgoing_header=self._headers,
                                       outgoing_body=outgoing_body,
                                       incoming_message=incoming_message,
                                       http_status_code=http_status_code,
                                       response_body=response_body,
                                       api_call_id=self.__api_call_id,
                                       used_cache=self.__used_cache)

    def __after_direct_send(self):
        pass

    def get_importance(self) -> MessageImportance:
        """get method"""
        return self.importance

    def get_recipients(self) -> List[Recipient]:
        # recipients may be modified by CompoundMessage
        return self._recipients
