from datetime import datetime
from typing import List, Union

import boto3
from database_mysql_local.generic_crud import GenericCRUD
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.MetaLogger import MetaLogger
# from message_local.MessageImportance import MessageImportance
from message_local.MessageLocal import MessageLocal
from message_local.Recipient import Recipient
from python_sdk_remote.utilities import our_get_env

EMAIL_MESSAGE_AWS_SES_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 208
EMAIL_MESSAGE_AWS_SES_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = "email_message_aws_ses_local_python_package"
DEVELOPER_EMAIL = "emad.a@circ.zone"

logger_object = {
    "component_id": EMAIL_MESSAGE_AWS_SES_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    "component_name": EMAIL_MESSAGE_AWS_SES_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": DEVELOPER_EMAIL
}

EMAIL_AWS_SES_API_TYPE = 1
# TODO MESSAGE_ID_WHEN_NOT_SENT
MESSAGE_NOT_SENT = 0

# TODO Why 'False' and not False?
IS_REALLY_SEND_EMAIL = our_get_env('IS_REALLY_SEND_EMAIL', 'False')
IS_REALLY_SEND_EMAIL = IS_REALLY_SEND_EMAIL.lower() in ('true', '1')
AWS_REGION = our_get_env('AWS_DEFAULT_REGION',
                         raise_if_not_found=IS_REALLY_SEND_EMAIL)
FROM_EMAIL = our_get_env('FROM_EMAIL', raise_if_not_found=IS_REALLY_SEND_EMAIL)
AWS_SES_DEFAULT_CONFIGURATION_SET = our_get_env('AWS_SES_DEFAULT_CONFIGURATION_SET',
                                                raise_if_not_found=IS_REALLY_SEND_EMAIL)


class EmailMessageAwsSesLocal(MessageLocal, GenericCRUD, metaclass=MetaLogger, object=logger_object):
    """Assuming the usage is as follows:
    message_local = MessageLocal(...)
    message_local.__class__ = EmailMessageAwsSesLocal
    message_local.__init__()  # calling the "init" of EmailMessageAwsSesLocal
    message_local.send(...)  # calling the "send" of EmailMessageAwsSesLocal
    """

    def __init__(self, subject: str, ses_resource=None, api_type_id=EMAIL_AWS_SES_API_TYPE, from_email=FROM_EMAIL,  # noqa
                 aws_ses_configuration_set=AWS_SES_DEFAULT_CONFIGURATION_SET):
        # Don't call MessageLocal.__init__, as we already have the message_local object
        GenericCRUD.__init__(self, default_schema_name="message",
                             default_table_name="message_table")
        self.ses_resource = ses_resource or boto3.client(
            'ses', region_name=AWS_REGION)
        self.subject = subject
        self._api_type_id = api_type_id  # used by MessageLocal
        self.from_email = from_email
        self.configuration_set = aws_ses_configuration_set

    def __send_email(self, recipient_email: str, body: str) -> str:
        """Returns the message ID of the email sent and the message ID of the email saved in the database"""
        api_data = {
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': body,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': self.subject,
            },
        }

        if self.can_send(api_data=api_data, outgoing_body=api_data["Body"],
                         sender_profile_id=self.get_sender_profile_id()):
            response = self.ses_resource.send_email(
                Destination={'ToAddresses': [recipient_email]},
                Message=api_data,
                Source=FROM_EMAIL,  # Use provided or default sender email
                ConfigurationSetName=AWS_SES_DEFAULT_CONFIGURATION_SET
            )
            # Example MessageId: '0100018c9e7552b1-b8932399-7049-492d-ae47-8f60967f49f1-000000'
            email_message_id = response['MessageId']
            self.logger.info(f"Email sent to {recipient_email} with message ID: {email_message_id}, "
                             f"subject: {self.subject}, body: {body}, recipient_email: {recipient_email}",
                             object={"email_message_id": email_message_id, "to_emails": recipient_email})
            self.after_send_attempt(outgoing_body=api_data, incoming_message=response['ResponseMetadata'],
                                    http_status_code=response['ResponseMetadata']['HTTPStatusCode'],
                                    response_body=response)
        else:
            self.logger.warn(f"EmailMessageAwsSesLocal.__send_email can_send is False: "
                             f"supposed to send email to {recipient_email} with body {body}")
            # TODO Please replace Magic Numbers with const/enum
            email_message_id = '0'

        return email_message_id

    def send(self, body: str = None, compound_message_dict: dict = None, recipients: List[Recipient] = None,
             cc: List[Recipient] = None, bcc: List[Recipient] = None,
             scheduled_timestamp_start: Union[str, datetime] = None,
             scheduled_timestamp_end: Union[str, datetime] = None, **kwargs) -> list[int]:
        recipients = recipients or self.get_recipients()
        self.logger.start(object={"body": body, "recipients": recipients})
        messages_ids = []
        for recipient in recipients:
            message_body = body or self.get_body_text_after_template_processing(
                recipient=recipient)
            recipient_email = recipient.get_email_address()
            if recipient_email is not None:
                if IS_REALLY_SEND_EMAIL:
                    email_message_id = self.__send_email(
                        recipient_email, message_body)
                    # TODO: subject and body should be inside ml table
                    message_id = super().insert(data_dict={"email_message_id": email_message_id,
                                                           "body": body,
                                                           "subject": self.subject,
                                                           "to_profile_id": recipient.get_profile_id(),
                                                           "to_email": recipient_email,
                                                           })
                else:
                    self.logger.info(f"EmailMessageAwsSesLocal.send IS_REALLY_SEND_EMAIL is off: "
                                     f"supposed to send email to {recipient_email} with body {message_body}")
                    message_id = MESSAGE_NOT_SENT
            else:
                self.logger.warn(f"recipient.get_email() is None: {recipient}")
                message_id = MESSAGE_NOT_SENT
            messages_ids.append(message_id)
        return messages_ids
