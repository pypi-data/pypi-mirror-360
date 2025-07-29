# message-send-local-python-package

## Workflow for sending messages

class `CampaignMessageSend` uses the `MessagesLocal` classes to send messages 




## Steps for sending messages:
1. Import contacts.
2. Run criteria-local CLI with --campaign_id or --criteria_set_ids and approve the profiles in criteria_profile
Example: `cd .../criteria-local-python-package; python -m criteria_local.src.CriteriaLocal --campaign_id 1`
3. Run send-message CLI with --campaign_id and approve the compound messages in message-local
Example: `cd .../message-send-local-python-package; python -m message_send_local.src.campaign_message_send --campaign_id 1`
4. Run send_sync_from_queue from messages-local with total_missions and optionally campaign_id.
Example: `cd .../messages-local-python-package; python -m messages_local.src.MessagesLocal --total_missions 1`
5. Verify the smartlink & dialog sent.

TODO: invitations_multiplier/additional_amount