from enum import Enum


# TODO Let's generate with Sql2Code
# Values are from the database message_channel_table
class MessageChannel(Enum):
    DEFAULT = 0
    EMAIL = 1
    SMS = 2
    MMS = 3
    RCS = 4
    FACEBOOK = 5
    TWITTER = 6
    LINKEDIN = 7
    SKYPE = 8
    TELEGRAM = 9
    DISCORD = 10
    WHATSAPP = 11
    WECHAT = 12
    FORM_REACTJS = 13
