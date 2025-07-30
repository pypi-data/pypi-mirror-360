import logging

from ClientHolder import ClientHolder, ClientWrapper
from utils.tools_message import send_message_wait_and_check_content
from utils.tools_reaction import react_message


# noinspection PyProtectedMember,DuplicatedCode
async def first_routine(client_1: ClientWrapper, client_2: ClientWrapper):
	# send a message to react to
	sent_message, received_message = await send_message_wait_and_check_content(client_1, client_2, "Message to react to")
	contact_2 = await client_2.get_contact_associated_to_another_client(other_client=client_1)

	####
	# Add reaction
	####
	reaction_1, reaction_2 = await react_message(client_1, client_2, sent_message.id, received_message.id, "A")
	assert reaction_1.reaction == reaction_2.reaction == "A"
	assert reaction_1.contact_id == 0
	assert reaction_2.contact_id == contact_2.id

	reaction_1, reaction_2 = await react_message(client_1, client_2, sent_message.id, received_message.id, "B")
	assert reaction_1.reaction == reaction_2.reaction == "B"
	assert reaction_1.contact_id == 0
	assert reaction_2.contact_id == contact_2.id
	reaction_1, reaction_2 = await react_message(client_1, client_2, sent_message.id, received_message.id, "C")
	assert reaction_1.reaction == reaction_2.reaction == "C"
	assert reaction_1.contact_id == 0
	assert reaction_2.contact_id == contact_2.id

	await react_message(client_1, client_2, sent_message.id, received_message.id, "")


# noinspection PyUnusedLocal
async def test_reaction(client_holder: ClientHolder, fast_mode):
	for c1, c2 in client_holder.get_one_client_pair_and_reverse():
		logging.info(f"Reaction routine: {c1.identity.id} <-> {c2.identity.id}")
		await first_routine(c1, c2)
