import logging

from olvid import OlvidClient, datatypes, listeners, errors

from ClientHolder import ClientHolder, ClientWrapper

from utils.tools_message import send_message_wait_and_check_content

test_failed = False


async def count_identity_messages(client: OlvidClient) -> int:
	count = 0
	async for _ in client.message_list():
		count += 1
	return count


# send a message, then a message replying to the first message, and finally update the last message body
# every message is sent twice, one by identity
async def send_reply_and_edit_messages(client_1: ClientWrapper, client_2: ClientWrapper):
	# get message count for a final check
	initial_message_count_1 = await count_identity_messages(client_1)
	initial_message_count_2 = await count_identity_messages(client_2)
	sent_message_count = 0

	# get discussions and contacts
	discussion_1, discussion_2 = await client_1.get_discussion_associated_to_another_client(client_2), await client_2.get_discussion_associated_to_another_client(client_1)
	contact_1, contact_2 = await client_1.get_contact_associated_to_another_client(client_2), await client_2.get_contact_associated_to_another_client(client_1)

	# send normal message
	sent_message_count += 1
	original_message_1, original_message_2 = await send_message_wait_and_check_content(client_1, client_2, "A")
	# original_message_2, _ = await send_message_wait_and_check_content(client_2, client_1, "B")
	logging.info("Message send finished")

	# send reply message
	sent_message_count += 1
	reply_message_1, _ = await send_message_wait_and_check_content(client_1, client_2, f"reply {client_1.identity.id}", replied_message_ids=(original_message_1.id, original_message_2.id))
	# reply_message_2, _ = await send_message_wait_and_check_content(client_2, client_1, f"reply {client_2.identity.id}", replied_message_ids=(original_message_2.id, original_message_1.id))
	logging.info("Message reply finished")

	# update message body
	ideal_updated_message_1 = datatypes.Message(discussion_id=discussion_1.id, sender_id=0, body=f"Updated body from {client_1.identity.id}", replied_message_id=original_message_1.id, edited_body=True)
	ideal_updated_message_2 = datatypes.Message(discussion_id=discussion_2.id, sender_id=contact_2.id, body=f"Updated body from {client_1.identity.id}", replied_message_id=original_message_2.id, edited_body=True)
	bots = [
		client_1.create_notification_bot(listeners.MessageBodyUpdatedListener(handler=client_1.get_check_content_handler(ideal_updated_message_1, reply_message_1.body, notification_type=listeners.NOTIFICATIONS.MESSAGE_BODY_UPDATED), count=1)),
		client_2.create_notification_bot(listeners.MessageBodyUpdatedListener(handler=client_2.get_check_content_handler(ideal_updated_message_2, reply_message_1.body, notification_type=listeners.NOTIFICATIONS.MESSAGE_BODY_UPDATED), count=1)),
	]

	# update previous message
	await client_1.message_update_body(message_id=reply_message_1.id, updated_body=f"Updated body from {client_1.identity.id}")

	# wait for notif to arrive
	for bot in bots:
		await bot.wait_for_listeners_end()

	logging.info("Message body update finished")

	# check message count
	assert await count_identity_messages(client_1) == initial_message_count_1 + sent_message_count
	assert await count_identity_messages(client_2) == initial_message_count_2 + sent_message_count


async def delete_messages(client_1: ClientWrapper, client_2: ClientWrapper):
	# get discussions and contacts
	discussion_1, discussion_2 = await client_1.get_discussion_associated_to_another_client(
		client_2), await client_2.get_discussion_associated_to_another_client(client_1)

	#####
	# delete a message locally
	#####
	# retrieve a message to delete
	message_1 = None
	async for message in client_1.message_list():
		message_1 = message
	assert message_1

	bot = client_1.create_notification_bot(listeners.MessageDeletedListener(handler=client_1.get_check_content_handler(message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELETED), count=1))
	await client_1.message_delete(message_id=message_1.id)
	await bot.wait_for_listeners_end()

	#####
	# delete a message remotely
	#####
	message_1 = None
	async for message in client_1.message_list(filter=datatypes.MessageFilter(discussion_id=discussion_1.id)):
		message_1 = message
	message_2 = None
	async for message in client_2.message_list(filter=datatypes.MessageFilter(discussion_id=discussion_2.id)):
		if message.body == message_1.body:
			message_2 = message
	assert message_1, message_2

	bot_1 = client_1.create_notification_bot(listeners.MessageDeletedListener(handler=client_1.get_check_content_handler(message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELETED), count=1))
	bot_2 = client_2.create_notification_bot(listeners.MessageDeletedListener(handler=client_2.get_check_content_handler(message_2, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELETED), count=1))

	await client_1.message_delete(message_id=message_1.id, delete_everywhere=True)

	await bot_1.wait_for_listeners_end()
	await bot_2.wait_for_listeners_end()

	try:
		message = await client_1.message_get(message_1.id)
		raise Exception(f"Found a deleted message: {message}")
	except errors.AioRpcError:
		pass
	except Exception:
		raise Exception("Invalid exception raised")

	try:
		message = await client_2.message_get(message_2.id)
		raise Exception(f"Found a deleted message: {message}")
	except errors.AioRpcError:
		pass
	except Exception:
		raise Exception("Invalid exception raised")


# noinspection PyUnusedLocal
async def test_message(client_holder: ClientHolder, fast_mode=False):
	for c1, c2 in client_holder.get_one_client_pair_and_reverse():
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: send and reply messages")
		await send_reply_and_edit_messages(c1, c2)
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: delete messages")
		await delete_messages(c1, c2)
		if test_failed:
			raise Exception("Test was marked as failed")
