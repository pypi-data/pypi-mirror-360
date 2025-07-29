from item_local.item import Item

from .MessageLocal import MessageLocal


class SmsMessageLocal(Item, MessageLocal):
    pass  # TODO implement

    def check_message(self):
        # TODO Check that there is only body without subject
        # TODO Check that there is version of plain text without HTML
        # TODO Check the length of the self.__body_after_text_template is in the right length
        pass
