from src.MessagesLocal import MessagesLocal

from message_local.MessageLocal import MessageLocal
from campaign_local.CampaignLocal import CampaignLocal
from criteria_local.criteria_profile import CriteriaProfile

from python_sdk_remote.mini_logger import MiniLogger as logger


def main():
    """
    Main function to run the MessagesLocal script.
    This function initializes the MessagesLocal and CriteriaProfile classes,
    retrieves recipients based on a campaign ID, and sends messages to those recipients.
    """

    logger.info("Starting MessagesLocal script...")
    messages_local = MessagesLocal(is_test_data=1)
    criteria_profile = CriteriaProfile(is_test_data=1)

    logger.info("MessagesLocal and CriteriaProfile initialized.")

    TEST_CAMPAIGN_ID = CampaignLocal().get_test_campaign_id()

    input_campaign_id = None
    # input_campaign_id = input(
    #     "Enter Campaign ID (or press Enter to use test campaign ID): ").strip()

    CAMPAIGN_ID = input_campaign_id or TEST_CAMPAIGN_ID

    logger.info(f"Using Campaign ID: {CAMPAIGN_ID}")
    # WorkFlow Stages:

    # 0. build campaign, criteria_set, criteria_profiles
    # 1. profiles preparation for a sertain campaign, filling the criteria_set_profile_table
    # 2. fill the message to the massages_table(outbox_view)/ insert to queue
    # 3. send messages to the recipients
    #   a. send message using send_scheduled
    #   b. send message using send_sync

    # 1. profiles preparation for a sertain campaign, filling the criteria_set_profile_table
    logger.info("Inserting profiles by campaign ID...")
    criteria_profile.insert_profiles_by_campaign_id(
        campaign_id=CAMPAIGN_ID,
    )
    logger.info("Profiles inserted successfully.")

    # 2. send(first saveing to the queue/database) messages
    logger.info("Sending messages...")
    message_ids = messages_local.send_scheduled(
        campaign_id=CAMPAIGN_ID,
        # is_require_moderator=False,  # set to False for testing
        # recipients=recipients,
    )

    logger.info(f"Messages sent successfully. Message IDs: {message_ids}")

    # 3. we need to approve the messages before sending them, in the database the query:
    """
        SELECT message_id, process_id, campaign_id, is_require_moderator, is_moderator_approved, created_timestamp
        FROM message.message_table
        order by created_timestamp desc limit 4;
    """
    # update the is_moderator_approved field to 1 for the latest message you sent

    messages_to_approve = messages_local.get_messages_to_approve(
        campaign_id=CAMPAIGN_ID,
        limit=10
    )

    if not messages_to_approve:
        logger.info("No messages to approve.")

    total_messages = len(messages_to_approve)
    logger.info(f"Total messages to approve: {total_messages}")

    for i, message in enumerate(messages_to_approve, start=1):
        message_id = message['message_id']
        process_id = message['process_id']
        campaign_id = message['campaign_id']
        is_require_moderator = message['is_require_moderator']
        is_moderator_approved = message['is_moderator_approved']
        created_timestamp = message['created_timestamp']

        logger.info(f"Message ID: {message_id}, Process ID: {process_id}, "
                    f"Campaign ID: {campaign_id}, "
                    f"Is Require Moderator: {is_require_moderator}, "
                    f"Is Moderator Approved: {is_moderator_approved}, "
                    f"Created Timestamp: {created_timestamp}")

        message_local = MessageLocal(
            message_id=message_id,
            campaign_id=campaign_id,
            is_test_data=1
        )

        recipient = message_local.get_recipients()[0]

        message_subject = message_local.get_subject_text_after_template_processing(
            recipient=recipient)
        message_body = message_local.get_body_text_after_template_processing(
            recipient=recipient)

        message_channel = message_local.get_message_channel(
            recipient=recipient)

        message_profile_blocks = message_local.get_profile_blocks(
            recipient.get_profile_id(), message_channel)

        logger.info(
            f"Message ID: {message_id} the #{i} from {total_messages} \n")
        logger.info(f"Recipient: {recipient}\n")
        logger.info(f"Message Profile Blocks: {message_profile_blocks}\n")
        logger.info(f"Message Channel: {message_channel}\n")
        logger.info(f"Message Subject: {message_subject}\n")
        logger.info(f"Message Body: {message_body}\n")

        input_approval = input(
            f"Do you approve message ID {message_id} for campaign ID {campaign_id}? (y/n): ").strip().lower()

        if input_approval == 'y':
            messages_local.update_is_moderator_approved(
                message_id=message_id,
                is_moderator_approved=True
            )
            logger.info(f"Message ID {message_id} approved.")
        else:
            messages_local.update_is_moderator_approved(
                message_id=message_id,
                is_moderator_approved=False
            )
            logger.info(f"Message ID {message_id} not approved.")

    # 4. send messages from the queue
    logger.info("Sending messages from the queue...")
    success = messages_local.send_sync_from_queue(
        campaign_id=CAMPAIGN_ID,
    )

    if success:
        logger.info("Messages sent successfully from the queue.")
    else:
        logger.error("Failed to send messages from the queue.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise
