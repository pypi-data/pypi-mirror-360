import os
from datetime import datetime
from typing import List

from email_message_aws_ses_local.ses_email import EmailMessageAwsSesLocal
from label_message_local.LabelConstants import MESSAGE_OUTBOX_LABEL_ID
from label_message_local.LabelMessage import LabelsMessageLocal
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.MetaLogger import MetaLogger
# TODO Where do we use FACEBOOK_MESSAGE_SELENIUM_PROVIDER_ID
from message_local.ChannelProviderConstants import (
    AWS_SES_EMAIL_MESSAGE_PROVIDER_ID, AWS_SNS_SMS_MESSAGE_PROVIDER_ID,
    INFORU_MESSAGE_PROVIDER_ID, VONAGE_MESSAGE_PROVIDER_ID,)
from message_local.MessageChannels import MessageChannel
from message_local.MessageImportance import MessageImportance
from message_local.MessageLocal import MessageLocal
from message_local.Recipient import Recipient
from queue_worker_local.queue_worker import QueueWorker
from sms_message_aws_sns_local.sms_message_aws_sns import SmsMessageAwsSnsLocal
from whataspp_message_inforu_local.WhatsAppMessageInforuLocal import WhatsAppMessageInforuLocal
from whatsapp_message_vonage_local.vonage_whatsapp_message_local import WhatsAppMessageVonageLocal
from facebook_message_selenium_local.facebook_message_selenium import FacebookMessageSelenium

# TODO Replace Magic Number with enum in a separate file in this repo which will be created by Sql2Code in the future
MESSAGES_API_TYPE_ID = 5
SEND_MESSAGE_SYNC_ACTION_ID = 15  # The queue use this to invoke the send_sync method
MESSAGE_LOCAL_PYTHON_COMPONENT_ID = 259
MESSAGE_LOCAL_PYTHON_COMPONENT_COMPONENT_NAME = 'messages-local-python-package'
DEVELOPER_EMAIL = 'akiva.s@circ.zone'

logger_object_message = {
    'component_id': MESSAGE_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': MESSAGE_LOCAL_PYTHON_COMPONENT_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}


class MessagesLocal(metaclass=MetaLogger, object=logger_object_message):
    # no classes type, so the worker can init it with json.
    def __init__(self, default_original_body: str = None, default_subject: str = None,
                 default_importance: int = MessageImportance.MEDIUM.value, recipients: List[dict] = None,
                 is_test_data: bool = False):
        self.recipients = recipients

        self.default_original_body = default_original_body
        self.default_subject = default_subject
        self.default_importance = default_importance
        self.is_test_data = is_test_data
        self.label_crud = LabelsMessageLocal()
        self.queue_worker = None  # This is called by the queue worker, so we can't initiate it here

    def get_queue_worker(self):
        self.queue_worker = self.queue_worker or QueueWorker(
            schema_name="message", table_name="message_table",
            view_name="message_outbox_view",
            queue_item_id_column_name="message_id",
            is_test_data=self.is_test_data)
        queue_worker = self.queue_worker
        return queue_worker

    @staticmethod
    def __send(recipient: Recipient, message_local: MessageLocal,
               importance: MessageImportance,
               campaign_id: int, message_channel_id=None) -> list[int]:
        message_recipient_channel = \
            message_local.get_message_channel(recipient)
        message_recipient_provider_id = message_local.get_message_provider_id(
            message_channel=message_recipient_channel, recipient=recipient)
        body = message_local.get_body_text_after_template_processing(
            recipient=recipient,
            message_channel=message_recipient_channel)
        if not body:
            message_ids = []
            return message_ids
        init_kwargs = {}
        send_kwargs = {"body": body, "recipients": [recipient],
                       "compound_message_dict": message_local.get_compound_message_dict(
                           channel=message_recipient_channel)}

        if message_channel_id is not None:
            message_recipient_channel = message_channel_id

        # TODO: Please change to Facebook Selenium and test it is working
        # TODO: Please change to WhatsApp Selenium and test it is working
        if (message_recipient_channel == MessageChannel.SMS and
                message_recipient_provider_id == AWS_SNS_SMS_MESSAGE_PROVIDER_ID):
            message_local.__class__ = SmsMessageAwsSnsLocal

        elif message_recipient_channel == MessageChannel.WHATSAPP:
            if message_recipient_provider_id == INFORU_MESSAGE_PROVIDER_ID:
                message_local.__class__ = WhatsAppMessageInforuLocal
            elif message_recipient_provider_id == VONAGE_MESSAGE_PROVIDER_ID:
                message_local.__class__ = WhatsAppMessageVonageLocal
            else:
                raise Exception("Don't know which WhatsAppMessageLocal class to use "
                                f"(provider_id: {message_recipient_provider_id})")
        elif (message_recipient_channel == MessageChannel.EMAIL and
              message_recipient_provider_id == AWS_SES_EMAIL_MESSAGE_PROVIDER_ID):
            # Parameters to the function we call???
            init_kwargs = {"subject": message_local.get_subject_text_after_template_processing(recipient=recipient)}
            message_local.__class__ = EmailMessageAwsSesLocal
        # TODO In this if statement we should follow the same process as the other channels and assign a value into message_local.__class__ =  # noqa: E501
        elif message_recipient_channel == MessageChannel.FACEBOOK:
            # TODO FacebookMessageSelenium doesn't work with the same format as the other send methods. Why? Seems like I need to do it like this?  # noqa: E501
            # if message_recipient_provider_id == FACEBOOK_MESSAGE_SELENIUM_PROVIDER_ID:
            message_local = FacebookMessageSelenium()
            message_ids = \
                message_local.send(recipients=[recipient], body=str(body))
            message_local.browser.quit()
            return message_ids
        else:
            # TODO We need to add to the message Recipient country, message plain text length after template,
            #  message HTML length after template, number of attachments, attachments' types and sizes.
            compound_message_dict = message_local.get_compound_message_dict()

            data_dict = {"channel_id": message_recipient_channel,
                         "provider_id": message_recipient_provider_id,
                         "recipient": recipient,
                         "compound_message_dict": compound_message_dict,
                         "compound_message_length": len(compound_message_dict),
                         "importance": importance,
                         "campaign_id": campaign_id
                         }

            error_message = "Don't know which MessageLocal class to use." \
                + " Data: " + str(data_dict)
            # data_dict will be printed anyway, as the meta logger prints the object & local variables  # noqa: E501
            raise Exception(error_message)

        message_local.__init__(**init_kwargs)
        message_ids = message_local.send(**send_kwargs)
        return message_ids

    # This method should be used by Queue Worker
    # Make sure send_sync has all the parameters in the function_parameters_json below  # noqa: E501
    def send_sync(self, *, campaign_id: int = None, message_id: int = None,
                  recipients: List[dict] = None,
                  cc_recipients: List[dict] = None,
                  bcc_recipients: List[dict] = None,
                  request_datetime: str = None,
                  # TODO What is exactly the operational meaning of start_timestamp?
                  #  There is start_timestamp, when the message can be sent?
                  start_timestamp: datetime = datetime.now(),
                  importance: int = None,
                  requested_message_type: int = None,
                  sender_profile_id: int = None, message_channel_id=None) -> None:
        """send method"""

        # TODO recipient_list = Recipient.from_dicts(recipient_list_of_dicts or self.recipients) - Three changes
        recipients = Recipient.recipients_from_dicts(recipients or self.recipients)
        importance = MessageImportance(importance or self.default_importance)
        message_local = MessageLocal(message_id=message_id,
                                     original_body=self.default_original_body,
                                     original_subject=self.default_subject,
                                     campaign_id=campaign_id,
                                     recipients=recipients,
                                     importance=importance,
                                     api_type_id=MESSAGES_API_TYPE_ID,
                                     sender_profile_id=sender_profile_id,
                                     is_test_data=self.is_test_data)

        list_return = []
        for recipient in recipients:
            list_return.append(self.__send(recipient, message_local, importance, campaign_id, message_channel_id=message_channel_id))
            # TODO: should we send to multiple recipients outside this loop?
        return list_return

    # This method will push the messages to the queue in message_outbox_table
    def send_scheduled(
            self, *, campaign_id: int = None, message_template_id: int = None,
            is_require_moderator: bool = True,
            recipients: List[Recipient] = None, 
            cc_recipients: List[Recipient] =  None,
            bcc_recipients: List[Recipient] = None,
            request_datetime: datetime = None,
            importance: MessageImportance = None,
            requested_message_type: MessageChannel = None,
            start_timestamp: datetime = datetime.now(), sender_profile_id: int = None, message_channel_id=None) -> list[int]:
        """The message will be sent any time between start_timestamp and end_timestamp
        For every bcc_recipient, a message will be pushed to the queue with the same parameters
        (message_id per bcc_recipient, or one if none provided)
        """
        importance = importance or MessageImportance(self.default_importance)
        # If no recipients are provided to MessageLocal, it will try to find them in the class
        recipients = recipients or [Recipient(**recipient) for recipient in (self.recipients or [])]
        message_ids = []
        for bcc_recipient in bcc_recipients or [None]:
            # Proccess template:
            message_local = MessageLocal(original_body=self.default_original_body,
                                         original_subject=self.default_subject,
                                         campaign_id=campaign_id,
                                         message_template_id=message_template_id,
                                         recipients=recipients,
                                         importance=importance,
                                         api_type_id=MESSAGES_API_TYPE_ID,
                                         sender_profile_id=sender_profile_id,
                                         is_require_moderator=is_require_moderator,
                                         is_test_data=self.is_test_data)
            if not message_local.message_ids:
                raise Exception("No message_ids were created")
            for message_id in message_local.message_ids:
                # Make sure send_sync accepts all these parameters.
                # As it is invoked from the queue, all parameters should be json-supported (not objects)
                function_parameters_json = {
                    "message_id": message_id,
                    "campaign_id": campaign_id,
                    "cc_recipients": Recipient.recipients_to_dicts(cc_recipients),
                    "bcc_recipients": bcc_recipient.to_dict() if bcc_recipient else None,
                    "request_datetime": str(request_datetime),
                    "importance": importance.value,
                    "requested_message_type": requested_message_type.value if requested_message_type else None,
                    "start_timestamp": str(start_timestamp),
                    "sender_profile_id": sender_profile_id
                }

                # Make sure MessagesLocal.__init__ accepts all these parameters
                class_parameters_json = {"default_original_body": self.default_original_body,
                                         "default_subject": self.default_subject,
                                         "default_importance": self.default_importance,
                                         "recipients": self.recipients,
                                         "is_test_data": self.is_test_data
                                         }

                # Edit the message entry:
                self.get_queue_worker().push({"function_parameters_json": function_parameters_json,
                                              "class_parameters_json": class_parameters_json,
                                              "message_id": message_id,
                                              "action_id": SEND_MESSAGE_SYNC_ACTION_ID})
                self.logger.info("Message pushed to the queue successfully", object={"message_id": message_id})

                try:
                    self.label_crud.add_label_message(label_id=MESSAGE_OUTBOX_LABEL_ID, message_id=message_id)
                except Exception as e:
                    self.logger.error("Failed to add label to message. continueing", object=e)
                message_ids.append(message_id)
        return message_ids

    def send_sync_from_queue(self, total_missions: int = 1, campaign_id: int = None,
                             campaing_criteria_set_id: int = None, message_channel_id=None) -> bool:
        if self.is_test_data:
            working_directory = os.path.dirname(os.path.realpath(__file__))
        else:
            working_directory = None

        custom_condition = "(is_require_moderator = 1 AND is_moderator_approved = 1) OR is_require_moderator=0"
        if campaign_id:
            custom_condition += f" AND campaign_id = {campaign_id}"
        if campaing_criteria_set_id:
            custom_condition += f" AND campaing_criteria_set_id = {campaing_criteria_set_id}"

        successed = self.get_queue_worker().execute(install_packages=not self.is_test_data,
                                                    working_directory=working_directory,
                                                    total_missions=total_missions,
                                                    custom_condition=custom_condition,
                                                    action_ids=(SEND_MESSAGE_SYNC_ACTION_ID,))
        return successed


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--total_missions", type=int, default=1)
    parser.add_argument("--campaign_id", type=int, default=None)
    parser.add_argument("--campaing_criteria_set_id", type=int, default=None)
    args = parser.parse_args()
    messages_local = MessagesLocal()
    successed = messages_local.send_sync_from_queue(total_missions=args.total_missions, campaign_id=args.campaign_id,
                                                    campaing_criteria_set_id=args.campaing_criteria_set_id)
    print(f"Successed: {successed}")
