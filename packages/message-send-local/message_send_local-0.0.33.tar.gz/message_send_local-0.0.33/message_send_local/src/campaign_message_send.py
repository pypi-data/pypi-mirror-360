# TODO Shall we call it campaign_critetia_set_message_send.py

"""imports"""
from datetime import datetime
from typing import List

from criteria_local.criteria_local import CriteriaLocal
from database_mysql_local.generic_crud_ml import GenericCRUD
from logger_local.MetaLogger import MetaLogger
from message_local.MessageImportance import MessageImportance
from message_local.MessageTemplates import MessageTemplates
from message_local.Recipient import Recipient
from messages_local.MessagesLocal import MessagesLocal

try:
    from .constants import MESSAGE_SEND_CODE_LOGGER_OBJECT
except ImportError:  # needed for the CLI
    from constants import MESSAGE_SEND_CODE_LOGGER_OBJECT

# MINIMAL DAYS BETWEEN INITIAL CAMPAIGN MESSAGES TO THE SAME PROFILE
# TODO Do we comply with this description?
DEFAULT_MINIMAL_DAYS = 3

# TODO Can we block message-send from sending from non-prod1 environments (except is_system_data users/profiles of Circlez Team Members for debugging)?. I'm afraid someone is going to set IS_REALLY_SEND to true in play1  # noqa
# I think the rule above lets us run it in play1 (limited)


# TODO Are we using GenericCRUD? If no, can we delete it from this file.
# TODO Change GenericCRUD to SmartStorage
class CampaignMessageSend(
    GenericCRUD, metaclass=MetaLogger,
        object=MESSAGE_SEND_CODE_LOGGER_OBJECT):
    """Message send platform class"""

    def __init__(self, is_test_data: bool = False) -> None:
        super().__init__(default_schema_name="message")
        self.message_template = MessageTemplates(is_test_data=is_test_data)
        self.messages_local = MessagesLocal(is_test_data=is_test_data)
        self.criteria_local = CriteriaLocal(is_test_data=is_test_data)

    # TODO I think we should change campaign_id to campaign_criteria_set_id
    # TODO Shall we move this method to RecipientsLocal?
    # TODO Shall we add parameter of minimal_duration_between_messages_to_same_recipient?  # noqa: E501
    # TODO Shall we add parameter of minimal_duration_between_messages_to_same_recipient_in_specific_campaign?  # noqa: E501
    def __get_potential_recipient_list_by_campaign_id_limit(
            self, campaign_id: int,
            recipient_limit: int = 100) -> List[Recipient]:
        """return list of person id """

        recipient_limit_left = recipient_limit

        # Find all the criterion which relevant to this campaign_id
        # TODO Should this be in the campaign/criteria repo? - Campaign repo
        # TODO Rename this to query_for_relevant_criteria_set_for_campaign
        # TODO The bellow version supports only one criterion per criteria_set
        query_for_relevant_criteria_for_campaign = """
            SELECT min_age, max_age,
                gender_list_id, group_list_id, profile_list_id,
                minimal_days_between_messages_to_the_same_recipient, criteria_id
            FROM campaign.campaign_view AS campaign
                JOIN campaign_criteria_set.campaign_criteria_set_view AS campaign_criteria_set
                   ON campaign_criteria_set.campaign_id=campaign.campaign_id
                JOIN criteria.criteria_set_view AS criteria_set
                   ON criteria_set.criteria_set_id = campaign_criteria_set.criteria_set_id
                JOIN people.people_criteria_ext_general_view AS people_criteria_ext
                   ON people_criteria_ext.`criteria.criteria_id` = criteria_set.criteria_id
            WHERE campaign.campaign_id = %s
        """

        self.cursor.execute(
            query_for_relevant_criteria_for_campaign, (campaign_id,))
        results = []
        for criteria_for_campaign in self.cursor.fetchall():
            # TODO Can we do something more scalable such as CampaignCriteriaLocal campaign_criteria( campaign_criteria_for_campaign)
            # TODO minimal_days -> minimal_days_between_messages_to_the_same_recipient
            min_age, max_age, gender_list_id, group_list_id, profile_list_id, minimal_days, criteria_id = criteria_for_campaign
            minimal_days = minimal_days or DEFAULT_MINIMAL_DAYS
            # profile_id didn't receive messages from this campaign for campaign.minimal_days
            # TODO We should add profile_list_id and support it in get_where_by_criteria_dict()
            criteria_dict = {"min_age": min_age, "max_age": max_age,
                             "gender_list_id": gender_list_id,
                             "group_list_id": group_list_id,
                             "profile_list_id": profile_list_id,
                             "minimal_days": minimal_days,
                             "criteria_id": criteria_id}

            self.logger.info(object=criteria_dict)
            where = self.criteria_local.get_where_by_criteria_dict(
                criteria_dict)

            # We check that the user didn't receive messages from this campaign in the last minimal_days  # noqa: E501
            where += (""" AND user.profile_id NOT IN (
                       SELECT user.profile_id FROM message.message_outbox_view
                           WHERE campaign_id = %s AND updated_timestamp >= NOW() - INTERVAL %s DAY
                       )"""
                      )
            print("where=", where)

            # Possible columns: person_id, person_is_approved, person_main_email_address, user.main_email_address,
            # username, user_id, user_is_approved, user_is_test_data, profile_preferred_lang_code, profile_gender_id,
            # user.first_name, user_last_name, user_created_timestamp, profile_id, brand_id, user_active_location_id,
            # user_active_location_country_name, subscription_id, subscription_title, user_stars, profile_stars,
            # person_birthday_date, profile_phone_full_number_normalized, role_name, group_profile_id, group_id,
            # profile_id, relationship_type_id, is_sure, group_profile_type_id, supplier_category_id,
            # consumer_category_id, participant_category_id, months, start_date_day, start_date_month, start_date_year,
            # start_circa, end_date_day, end_date_month, end_date_year, end_circa, identifier, is_test_data, rank,
            # text_block_id, is_recommended, is_request_by_the_user, is_approved_by_group_admin

            # We should not use user schema as we want to send to all person (not only to users)  # noqa: E501
            # Fields needed to create Recipient
            query_for_potentials_recipients = f"""
                    SELECT DISTINCT `user.first_name`, user_id, person_id,
                        `user.main_email_address`, user.profile_id,
                        `profile.phone.full_number_normalized`,
                        `profile.preferred_lang_code`
                    FROM user.user_general_view AS user
                        JOIN group_profile.group_profile_table AS group_profile
                            ON group_profile.profile_id = user.profile_id
                    WHERE {where} LIMIT {recipient_limit_left}
                """
            self.logger.info(
                object={"query_for_potentials_receipients": query_for_potentials_recipients,  # noqa: E501
                        "campaign_id": campaign_id,
                        "minimal_days": minimal_days})

            self.cursor.execute(query_for_potentials_recipients,
                                (campaign_id, minimal_days))

            received_results = self.cursor.fetchall()
            for (first_name, user_id, person_id, user_main_email_address,
                 profile_id, profile_phone_full_number_normalized,
                 profile_preferred_lang_code) in received_results:
                recipient = Recipient(
                    user_id=user_id, person_id=person_id,
                    email_address_str=user_main_email_address,
                    profile_id=profile_id,
                    telephone_number=profile_phone_full_number_normalized,
                    preferred_lang_code_str=profile_preferred_lang_code,
                    first_name=first_name)
                results.append(recipient)
                self.logger.info(object={"recipient": recipient})

            recipient_limit_left -= len(received_results)

        return results

    # TODO Shall we change invitations -> messages
    # TODO Shall we add _by_campaign_id() suffix
    def __get_number_of_invitations_sent_in_the_last_24_hours(
            self,
            campaign_id: int) -> int:
        """return number of invitations"""
        self.logger.start(
            f"get number of invitations sent in the last 24_hours for campaign id={campaign_id}")  # noqa: E501
        query = """
            SELECT COUNT(*) FROM message.message_outbox_view
            WHERE campaign_id = %s
               AND return_code = 0   -- success
               AND updated_timestamp >= NOW() - INTERVAL 24 HOUR  -- updated in the last 24 hours
               LIMIT 1
            """

        self.cursor.execute(query, (campaign_id,))
        number_of_invitations_sent_in_the_last_24_hours = \
            self.cursor.fetchone()[0]  # can be 0

        return number_of_invitations_sent_in_the_last_24_hours

    def __get_number_of_invitations_to_send_by_campaign_id_multiplier(
            self, campaign_id: int, additional_invitations_multiplier: float = 1.01,
            additional_invitations_amount: int = 1) -> int:
        """get a number to send after multiplier"""

        invitations_sent_in_the_last_24_hours = \
            self.__get_number_of_invitations_sent_in_the_last_24_hours(
                campaign_id)
        number_of_invitations_to_send = int(
            invitations_sent_in_the_last_24_hours *
            additional_invitations_multiplier +
            additional_invitations_amount)
        return number_of_invitations_to_send

    # Using message_campaign_ext_table
    # TODO Shall we add to the method name also what it returns? List of message_ids
    # TODO Shall we also add criteria_set_id parameter? - Who to send campaign
    def send_message_by_campaign_id(
            self, *, campaign_id: int,
            additional_invitations_multiplier: float = 1.01,
            additional_invitations_amount: int = 1,
            request_datetime: datetime = None,
            requested_message_type: int = None,
            importance: MessageImportance = None) -> list[int]:

        # TODO:
        # recipient_limit = self.__get_number_of_invitations_to_send_by_campaign_id_multiplier(
        #     campaign_id=campaign_id,
        #     additional_invitations_multiplier=additional_invitations_multiplier,
        #     additional_invitations_amount=additional_invitations_amount)
        # ! potential recipients not the actual recipients
        # recipient_list = self.__get_potential_recipient_list_by_campaign_id_limit(
        #     campaign_id, recipient_limit)
        # recipient_list = self.criteria_local
        # if not recipient_list:
        #     return []
        # self.logger.info(object={"recipient_list": recipient_list})
        message_ids = self.messages_local.send_scheduled(
            # TODO Please make sure we have send_scheduled() with recipients_list  # noqa: E501
            # recipients=recipients_list,
            request_datetime=request_datetime,
            importance=importance,
            campaign_id=campaign_id,
            # TODO: message_template_id=message_template_id, ?
            requested_message_type=requested_message_type
        )

        return message_ids

    # TODO In which cases shall we use send_to_all_campaigns?
    def send_to_all_campaigns(self, additional_invitations_multiplier: float = 1.01,
                              additional_invitations_amount: int = 1) -> None:
        """send to all campaigns"""
        # TODO crud
        # TODO Shall we change campain_view with campaign_criteria_set_view?
        self.cursor.execute(
            "SELECT campaign_id FROM campaign.campaign_view WHERE NOW() >= start_timestamp "
            "AND (end_timestamp IS NULL OR NOW() <= end_timestamp)")
        campaign_ids_list_of_tuples = self.cursor.fetchall()
        self.logger.info(object={
            "campaign_ids_list_of_tuples": campaign_ids_list_of_tuples})
        for campaign_id_tuple in campaign_ids_list_of_tuples:
            self.send_message_by_campaign_id(
                campaign_id=campaign_id_tuple[0],
                additional_invitations_multiplier=additional_invitations_multiplier,
                additional_invitations_amount=additional_invitations_amount)


if __name__ == '__main__':
    # CLI
    import argparse
    parser = argparse.ArgumentParser(description='Campaign Message Send')
    # TODO either --campaign_id or --campaign_criteria_set_id
    parser.add_argument('--campaign_id', type=int, help='campaign_id')
    parser.add_argument('--additional_invitations_multiplier', type=float,
                        help='additional_invitations_multiplier')
    parser.add_argument('--additional_invitations_amount', type=int,
                        help='additional_invitations_amount')
    args = parser.parse_args()
    campaign_message_send = CampaignMessageSend()
    message_ids = campaign_message_send.send_message_by_campaign_id(
        campaign_id=args.campaign_id,
        additional_invitations_multiplier=args.additional_invitations_multiplier,
        additional_invitations_amount=args.additional_invitations_amount
    )
    print("message_ids:", message_ids)
