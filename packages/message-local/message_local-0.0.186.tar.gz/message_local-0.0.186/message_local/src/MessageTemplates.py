from functools import lru_cache

from database_mysql_local.generic_crud_ml import GenericCRUDML
from logger_local.MetaLogger import MetaLogger

from .MessageConstants import object_message


class MessageTemplates(GenericCRUDML, metaclass=MetaLogger, object=object_message):
    def __init__(self, is_test_data: bool = False):
        super().__init__(default_entity_name="field", default_schema_name="field", default_table_name="field_table",
                         is_test_data=is_test_data)

    @lru_cache
    def get_textblocks_and_attributes_by_form_id(self, form_id: int) -> list[dict]:
        """
            form_id
            form_name
            min_message_template
            max_message_template
            form_page
            form_message_seq_in_page
            form_message_template_id
            message_template_id
            message_template_name
            message_template_text_block_seq
            message_template_text_block_id
            message_template_text_block_name
            default_subject_template
            default_body_template
            message_template_text_block_ml_lang_code
            question_id
            question_title
            question_ml_lang_code
            default_question_possible_answer_id
            schema_attribute
            uischema_attribute
            question_type_id
            question_type_name
            variable_id
            variable_name
            variable_ml_title
            field_name
            message_template_text_block_is_visible
            possible_answer
        """
        query_by_form_id = """
        SELECT * FROM form.form_general_view WHERE form_id = %s
            ORDER BY form_page, form_message_seq_in_page, message_template_text_block_seq;"""
        self.cursor.execute(query_by_form_id, (form_id,))
        columns = self.cursor.column_names()
        select_clause_value = ", ".join(x.split(".")[-1] for x in columns)
        textblocks_and_attributes = self.convert_multi_to_dict(self.cursor.fetchall(),
                                                               select_clause_value=select_clause_value)
        return textblocks_and_attributes

    @lru_cache
    def get_textblocks_and_attributes_by_message_template_id(self, message_template_id: int) -> list[dict]:
        # TODO: do we want to allow None (all ids)
        assert isinstance(message_template_id, int)
        query = """
SELECT 
       message_template_general.question_id AS question_id,
       message_template_general.question_type_id AS question_type_id,
       message_template_general.variable_id AS variable_id,
       message_template_general.question_is_required AS is_required,
       message_template_general.schema_attributes AS schema_attribute,
       message_template_general.uischema_attributes AS uischema_attribute,
       message_template_general.question_type_schema_attributes AS question_type_schema_attributes,
       message_template_general.question_type_uischema_attributes AS question_type_uischema_attributes,
       message_template_general.`question.title` AS question_title,
       message_template_general.question_ml_lang_code AS question_ml_lang_code,
       message_template_general.message_template_text_block_ml_lang_code AS message_template_text_block_ml_lang_code,
       message_template_general.message_template_text_block_name AS message_template_text_block_name,
       message_template_general.message_template_text_block_seq AS message_template_text_block_seq,
       message_template_general.question_type_name AS question_type_name,
       message_template_general.possible_answer AS possible_answer,
       message_template_general.message_template_text_block_is_visible AS message_template_text_block_is_visible,
       message_template_general.message_template_text_block_id,
       message_template_general.`message_template_text_block.criteria_set_id` AS criteria_set_id,
       message_template_general.message_template_id AS message_template_id,
       message_template_general.default_question_possible_answer_id AS default_question_possible_answer_id,
       message_template_general.sms_body_template AS sms_body_template,
       message_template_general.email_subject_template AS email_subject_template,
       message_template_general.email_body_html_template AS email_body_html_template,
       message_template_general.whatsapp_body_template AS whatsapp_body_template,
       message_template_general.default_subject_template AS default_subject_template,
       message_template_general.default_body_template AS default_body_template

FROM message_template.message_template_general_view AS message_template_general
"""  # noqa

        where = f" WHERE message_template_id = {message_template_id} "
        order_by = " ORDER BY message_template_general.message_template_text_block_seq;"
        query += where + order_by

        self.cursor.execute(query)
        columns = ("question_id, question_type_id, variable_id, is_required, schema_attribute, uischema_attribute,"
                   "question_type_schema_attributes, question_type_uischema_attributes, question_title,"
                   "question_ml_lang_code, message_template_text_block_ml_lang_code, message_template_text_block_name,"
                   "message_template_text_block_seq, question_type_name, possible_answer, message_template_text_block_is_visible,"
                   "message_template_text_block_id, criteria_set_id, message_template_id, default_question_possible_answer_id, sms_body_template,"
                   "email_subject_template, email_body_html_template, whatsapp_body_template, default_subject_template,"
                   "default_body_template")
        # for inner_row in self.cursor.fetchall():
        #     text_block_dict = self.convert_to_dict(inner_row, ", ".join(columns))
        #
        #     text_block_dict["possibleAnswers"] = self._get_possible_answers(
        #         question_id=text_block_dict["questionId"])
        #     self.logger.info(object={"text_block_dict": text_block_dict})
        #     textblocks_and_attributes.append(text_block_dict)

        textblocks_and_attributes = self.convert_multi_to_dict(
            self.cursor.fetchall(), select_clause_value=columns)
        return textblocks_and_attributes

    # def _get_possible_answers(self, question_id: int) -> list[dict]:
    #     # TODO: get cities etc and insert as a possible answer.
    #     # We don't join this with the above query, because we want to keep the possible answers separated in a list.
    #     query = """
    #         SELECT value
    #         FROM question.question_possible_answer_table
    #                  JOIN question.question_possible_answer_ml_view AS question_possible_answer_ml
    #                       ON question_possible_answer_ml.question_possible_answer_id =
    #                          question_possible_answer_table.question_possible_answer_id
    #         WHERE question_id = %s """
    #     self.cursor.execute(query, (question_id,))
    #     # We will change action in the future.
    #     return [{"answerValue": row[0], "action": None} for row in self.cursor.fetchall()]
