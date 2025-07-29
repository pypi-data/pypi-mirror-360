from message_local.MessageLocal import MessageLocal


class EmailMessage(MessageLocal):
    """EmailMessage The base class for email messages that will take care database operations.

    Keyword arguments:
    1. default_schema_name: The name of the database schema to use.
    2. default_table_name: The name of the database table to use.
    3. default_view_table_name: The name of the database view table to use.
    4. default_entity_name: The name of the entity to use.
    """

    def __init__(self, default_schema_name: str = "message",
                 default_table_name: str = "message_table",
                 default_view_table_name: str = "message_view_table",
                 default_entity_name: str = "message_entity",):

        self.default_schema_name = default_schema_name
        self.default_table_name = default_table_name
        self.default_view_table_name = default_view_table_name
        self.default_entity_name = default_entity_name

    def save_email_message(self, message_data: dict) -> int:
        """
        Add required fields for MessageLocal.insert_message_data and
        Saves the message data to message..message_table and returns the message ID.
        """

        # required_args = ("schema_name", "table_name", "view_table_name",
        #                  "select_clause_value", "data_dict")

        message_data["schema_name"] = self.default_schema_name
        message_data["table_name"] = self.default_table_name
        message_data["view_table_name"] = self.default_view_table_name
        message_data["select_clause_value"] = "message_id"

        message_id = self.insert_message_data(
            message_data=message_data,
        )

        return message_id
