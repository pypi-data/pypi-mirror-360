import copy
import logging
import traceback
from typing import Callable

import grpc.aio

from olvid import OlvidClient, datatypes, listeners

from ClientHolder import ClientHolder, ClientWrapper


# noinspection DuplicatedCode
async def generic_read_once_routine(client_1: ClientWrapper, client_2: ClientWrapper, test_id: str, ephemerality: datatypes.MessageEphemerality):
	discussion_1, discussion_2 = await client_1.get_discussion_associated_to_another_client(client_2), await client_2.get_discussion_associated_to_another_client(client_1)
	contact_2 = await client_2.get_contact_associated_to_another_client(client_1)

	####
	# read once messages
	####
	bot_1_ideal_message = datatypes.Message(id=datatypes.MessageId(type=datatypes.MessageId.Type.TYPE_OUTBOUND), discussion_id=discussion_1.id, body=test_id)
	bot_2_ideal_message = datatypes.Message(id=datatypes.MessageId(type=datatypes.MessageId.Type.TYPE_INBOUND), discussion_id=discussion_2.id, body=test_id, sender_id=contact_2.id)

	bots: list[OlvidClient] = []
	optional_bots: list[OlvidClient] = []
	# check notification flow on client 1
	bots.append(client_1.create_notification_bot(listeners.MessageSentListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_SENT), count=1)))
	bots.append(client_1.create_notification_bot(listeners.MessageDeletedListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELETED), count=1)))

	optional_bots.append(client_1.create_notification_bot(listeners.MessageUploadedListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_UPLOADED), count=1)))
	optional_bots.append(client_1.create_notification_bot(listeners.MessageDeliveredListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELIVERED), count=1)))
	optional_bots.append(client_1.create_notification_bot(listeners.MessageReadListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_READ), count=1)))

	# check notification flow on client 2
	bots.append(client_2.create_notification_bot(listeners.MessageReceivedListener(handler=client_2.get_check_content_handler(bot_2_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_RECEIVED), count=1)))
	bots.append(client_2.create_notification_bot(listeners.MessageDeletedListener(handler=client_2.get_check_content_handler(bot_2_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELETED), count=1)))

	# check message deletion on both clients
	bots.append(client_1.create_notification_bot(listeners.MessageDeletedListener(handler=assert_message_deletion_handler_creator(client_1), count=1)))
	bots.append(client_2.create_notification_bot(listeners.MessageDeletedListener(handler=assert_message_deletion_handler_creator(client_2), count=1)))

	# send message
	message = await client_1.message_send(discussion_id=discussion_1.id, body=test_id, ephemerality=ephemerality)
	logging.debug(f"Sent {test_id} message: {message_id_to_str(message.id)}")

	# wait for notifications
	for bot in bots:
		await bot.wait_for_listeners_end()
	for bot in optional_bots:
		await bot.stop()


# noinspection DuplicatedCode
async def generic_self_expiring_test(client_1: ClientWrapper, client_2: ClientWrapper, test_id: str, ephemerality: datatypes.MessageEphemerality):
	discussion_1, discussion_2 = await client_1.get_discussion_associated_to_another_client(client_2), await client_2.get_discussion_associated_to_another_client(client_1)
	contact_2 = await client_2.get_contact_associated_to_another_client(client_1)

	####
	# existence duration messages
	####
	bot_1_ideal_message = datatypes.Message(id=datatypes.MessageId(type=datatypes.MessageId.Type.TYPE_OUTBOUND), discussion_id=discussion_1.id, body=test_id)
	bot_2_ideal_message = datatypes.Message(id=datatypes.MessageId(type=datatypes.MessageId.Type.TYPE_INBOUND), discussion_id=discussion_2.id, body=test_id, sender_id=contact_2.id)

	bots: list[OlvidClient] = [
		# check notification flow on client 1
		client_1.create_notification_bot(listeners.MessageSentListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_SENT), count=1)),
		client_1.create_notification_bot(listeners.MessageUploadedListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_UPLOADED), count=1)),
		client_1.create_notification_bot(listeners.MessageDeliveredListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELIVERED), count=1)),
		client_1.create_notification_bot(listeners.MessageReadListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_READ), count=1)),
		client_1.create_notification_bot(listeners.MessageDeletedListener(handler=client_1.get_check_content_handler(bot_1_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELETED), count=1)),

		# check notification flow on client 2
		client_2.create_notification_bot(listeners.MessageReceivedListener(handler=client_2.get_check_content_handler(bot_2_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_RECEIVED), count=1)),
		client_2.create_notification_bot(listeners.MessageDeletedListener(handler=client_2.get_check_content_handler(bot_2_ideal_message, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELETED), count=1)),

		# check message is available on both clients, on every notification (before deletion)
		client_1.create_notification_bot(listeners.MessageSentListener(handler=assert_message_existence_handler_creator(client_1, handler_id=f"{test_id}-4.1"), count=1)),
		client_1.create_notification_bot(listeners.MessageUploadedListener(handler=assert_message_existence_handler_creator(client_1, handler_id=f"{test_id}-4.2"), count=1)),
		client_1.create_notification_bot(listeners.MessageDeliveredListener(handler=assert_message_existence_handler_creator(client_1, handler_id=f"{test_id}-4.3"), count=1)),
		client_1.create_notification_bot(listeners.MessageReadListener(handler=assert_message_existence_handler_creator(client_1, handler_id=f"{test_id}-4.3"), count=1)),
		client_2.create_notification_bot(listeners.MessageReceivedListener(handler=assert_message_existence_handler_creator(client_2, handler_id=f"{test_id}-4.4"), count=1)),

		# check message had been deleted on both client when delete notifications arrive
		client_1.create_notification_bot(listeners.MessageDeletedListener(handler=assert_message_deletion_handler_creator(client_1, handler_id=f"{test_id}-3.1"), count=1)),
		client_2.create_notification_bot(listeners.MessageDeletedListener(handler=assert_message_deletion_handler_creator(client_2, handler_id=f"{test_id}-3.2"), count=1)),

		# check message deletion after the delay
		# client_1.create_notification_bot(notifications_dictionary={Notifications.MESSAGE_DELIVERED.name: 1}, handler=assert_message_deletion_handler_creator(client_1, delay=delay_before_deletion_check + 1)),
		# client_2.create_notification_bot(notifications_dictionary={Notifications.MESSAGE_RECEIVED.name: 1}, handler=assert_message_deletion_handler_creator(client_2, delay=delay_before_deletion_check + 1)),

	]

	# send message
	message = await client_1.message_send(discussion_id=discussion_1.id, body=test_id, ephemerality=ephemerality)
	logging.debug(f"Sent {test_id} message: {message_id_to_str(message.id)}")

	# wait for notifications
	for bot in bots:
		await bot.wait_for_listeners_end()


# execute generic ephemeral tests, but it set discussion shared ephemeral settings before test (and restore it after)
# noinspection DuplicatedCode
async def generic_discussion_customization_test(client_1: ClientWrapper, client_2: ClientWrapper, test_id: str, new_settings: datatypes.DiscussionSettings, generic_routine: Callable):
	logging.debug(f"Starting test: {test_id}")

	discussion_1, discussion_2 = await client_1.get_discussion_associated_to_another_client(client_2), await client_2.get_discussion_associated_to_another_client(client_1)

	# get current settings
	prev_settings_1 = (await client_1.discussion_settings_get(discussion_1.id))
	prev_settings_2 = (await client_2.discussion_settings_get(discussion_2.id))

	# prepare new settings
	new_settings_1 = copy.deepcopy(new_settings)
	new_settings_1.discussion_id = prev_settings_1.discussion_id
	new_settings_2 = copy.deepcopy(new_settings)
	new_settings_2.discussion_id = prev_settings_2.discussion_id

	# prepare notification bots
	bot_1 = client_1.create_notification_bot(listeners.DiscussionSettingsUpdatedListener(handler=client_1.get_check_content_handler(discussion_1, new_settings_1, prev_settings_1, notification_type=listeners.NOTIFICATIONS.DISCUSSION_SETTINGS_UPDATED), count=1))
	bot_2 = client_2.create_notification_bot(listeners.DiscussionSettingsUpdatedListener(handler=client_2.get_check_content_handler(discussion_2, new_settings_2, prev_settings_2, notification_type=listeners.NOTIFICATIONS.DISCUSSION_SETTINGS_UPDATED), count=1))

	# set ephemeral settings
	await client_1.discussion_settings_set(settings=new_settings_1)

	# wait for notifications to arrive
	await bot_1.wait_for_listeners_end()
	await bot_2.wait_for_listeners_end()

	# test settings are properly used
	await generic_routine(client_1, client_2, test_id, datatypes.MessageEphemerality())

	# restore previous settings
	# prepare notification bots
	bot_1 = client_1.create_notification_bot(listeners.DiscussionSettingsUpdatedListener(handler=client_1.get_check_content_handler(discussion_1, prev_settings_1, new_settings_1, notification_type=listeners.NOTIFICATIONS.DISCUSSION_SETTINGS_UPDATED), count=1))
	bot_2 = client_2.create_notification_bot(listeners.DiscussionSettingsUpdatedListener(handler=client_2.get_check_content_handler(discussion_2, prev_settings_2, new_settings_2, notification_type=listeners.NOTIFICATIONS.DISCUSSION_SETTINGS_UPDATED), count=1))

	# set ephemeral settings
	await client_2.discussion_settings_set(settings=prev_settings_2)

	# wait for notifications to arrive
	await bot_1.wait_for_listeners_end()
	await bot_2.wait_for_listeners_end()


def assert_message_deletion_handler_creator(client: ClientWrapper, handler_id: str = ""):
	async def assert_message_deletion_handler(message: datatypes.Message):
		try:
			message_id = message.id
			try:
				await client.message_get(message_id=message_id)
				raise Exception("Message was not deleted on server")
			except grpc.aio.AioRpcError:
				pass

			async for message in client.message_list():
				assert message.id != message_id
			logging.debug(f"Message was deleted on server: {message_id_to_str(message_id)}")
		except Exception as e:
			logging.error(f"{handler_id}: exception")
			traceback.print_exc()
			raise e
	return assert_message_deletion_handler


def assert_message_existence_handler_creator(client: ClientWrapper, handler_id: str = ""):
	async def assert_message_existence_handler(message: datatypes.Message):
		try:
			message_id = message.id
			await client.message_get(message_id=message_id)

			async for message in client.message_list():
				if message.id == message_id:
					logging.debug(f"Message was found on server: {message_id_to_str(message_id)}")
					return
			raise Exception("Message not found using message_list")
		except Exception as e:
			logging.error(f"{handler_id}: exception")
			traceback.print_exc()
			raise e
	return assert_message_existence_handler


def message_id_to_str(message_id: datatypes.MessageId) -> str:
	return f"{message_id.type.name[0]}-{message_id.id}"


async def test_ephemeral_message(client_holder: ClientHolder, fast_mode: bool = False):
	for c1, c2 in client_holder.get_one_client_pair_and_reverse():
		logging.info("-" * 10 + " Read Once " + "-" * 10)
		await generic_read_once_routine(c1, c2, "read-once", datatypes.MessageEphemerality(read_once=True))

		logging.info("-" * 10 + " Visibility Duration " + "-" * 10)
		await generic_self_expiring_test(c1, c2, "visibility", datatypes.MessageEphemerality(visibility_duration=3))

		logging.info("-" * 10 + " Existence Duration " + "-" * 10)
		await generic_self_expiring_test(c1, c2, "existence", datatypes.MessageEphemerality(existence_duration=4))

		logging.info("-" * 10 + " Visibility-Existence Duration " + "-" * 10)
		await generic_self_expiring_test(c1, c2, "vi-ex", datatypes.MessageEphemerality(existence_duration=20, visibility_duration=3))

		logging.info("-" * 10 + " Existence-Visibility Duration " + "-" * 10)
		await generic_self_expiring_test(c1, c2, "ex-vi", datatypes.MessageEphemerality(existence_duration=4, visibility_duration=20))

		logging.info("-" * 10 + " ReadOnce-Existence-Visibility Duration " + "-" * 10)
		await generic_read_once_routine(c1, c2, "ro-ex-vi", datatypes.MessageEphemerality(read_once=True, existence_duration=3, visibility_duration=2))

		logging.info("-" * 10 + " DiscussionCustomization-1 " + "-" * 10)
		await generic_discussion_customization_test(c1, c2, "dc-1", datatypes.DiscussionSettings(read_once=True), generic_read_once_routine)

		if not fast_mode:
			logging.info("-" * 10 + " DiscussionCustomization-2 " + "-" * 10)
			await generic_discussion_customization_test(c1, c2, "dc-2", datatypes.DiscussionSettings(visibility_duration=3), generic_self_expiring_test)

			logging.info("-" * 10 + " DiscussionCustomization-3 " + "-" * 10)
			await generic_discussion_customization_test(c1, c2, "dc-3", datatypes.DiscussionSettings(existence_duration=4, visibility_duration=20), generic_self_expiring_test)

		if fast_mode:
			break
