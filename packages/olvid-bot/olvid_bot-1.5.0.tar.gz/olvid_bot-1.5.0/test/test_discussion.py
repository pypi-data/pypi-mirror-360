import copy
import logging

from ClientHolder import ClientHolder, ClientWrapper
from olvid import datatypes, listeners


async def command_tests(client_1: ClientWrapper, client_2: ClientWrapper):
	discussion_1, discussion_2 = await client_1.get_discussion_associated_to_another_client(client_2), await client_2.get_discussion_associated_to_another_client(client_1)

	await compare_list_and_get_results(client_1)

	# fake bot to avoid watchdogs trigger
	message_count = await count_messages_in_discussion(client_1, discussion_1)
	if message_count > 0:
		message_deleted_bot = client_1.create_notification_bot(listeners.MessageDeletedListener(handler=lambda m: None, count=message_count))

		# empty discussion
		await client_1.discussion_empty(discussion_id=discussion_1.id)

		# wait for messages to be deleted
		await message_deleted_bot.wait_for_listeners_end()

	# check discussion is empty
	assert (await count_messages_in_discussion(client_1, discussion_1)) == 0


async def test_notifications(client_1: ClientWrapper):
	group_name = f"GroupName-{client_1.identity.details.first_name}"
	group_name_updated = f"GroupName-{client_1.identity.details.first_name}-Updated"
	group_description = "NoDescription"

	await compare_list_and_get_results(client_1)

	#####
	# Group creation
	#####
	# create bots to check workflow
	bots = []
	ideal_group = datatypes.Group(name=group_name, description=group_description)
	ideal_discussion = datatypes.Discussion(title=group_name)
	bots.append(client_1.create_notification_bot(listeners.GroupUpdateInProgressListener(handler=lambda gid: gid, count=1)))
	bots.append(client_1.create_notification_bot(listeners.GroupNewListener(handler=client_1.get_check_content_handler(ideal_group, notification_type=listeners.NOTIFICATIONS.GROUP_NEW), count=1)))
	bots.append(client_1.create_notification_bot(listeners.DiscussionNewListener(handler=client_1.get_check_content_handler(ideal_discussion, notification_type=listeners.NOTIFICATIONS.DISCUSSION_NEW), count=1)))
	bots.append(client_1.create_notification_bot(listeners.GroupUpdateFinishedListener(handler=lambda gid: gid, count=1)))

	# create a new group and wait for creation on both sides
	await client_1.group_new_controlled_group(name=group_name, description=group_description, contact_ids=[])

	for bot in bots:
		await bot.wait_for_listeners_end()

	await compare_list_and_get_results(client_1)

	#####
	# update discussion title
	#####
	# TODO use group_new returned group when implemented
	# manually determine new group id
	group_id = 0
	async for g in client_1.group_list():
		group_id = g.id
	assert group_id != 0

	# get the original group
	prev_group: datatypes.Group = await client_1.group_get(group_id=group_id)
	new_group: datatypes.Group = copy.copy(prev_group)
	new_group.name = group_name_updated
	new_group.update_in_progress = False  # set to False to avoid comparison in notification handler

	# create bots to check workflow
	bots = []
	ideal_discussion = datatypes.Discussion(title=new_group.name, group_id=new_group.id)
	ideal_discussion.title = group_name_updated
	bots.append(client_1.create_notification_bot(listeners.GroupUpdateInProgressListener(handler=client_1.get_check_content_handler(new_group.id, notification_type=listeners.NOTIFICATIONS.GROUP_UPDATE_IN_PROGRESS), count=1)))
	bots.append(client_1.create_notification_bot(listeners.GroupNameUpdatedListener(handler=client_1.get_check_content_handler(new_group, group_name, notification_type=listeners.NOTIFICATIONS.GROUP_NEW), count=1)))
	bots.append(client_1.create_notification_bot(listeners.DiscussionTitleUpdatedListener(handler=client_1.get_check_content_handler(ideal_discussion, group_name, notification_type=listeners.NOTIFICATIONS.DISCUSSION_TITLE_UPDATED), count=1)))
	bots.append(client_1.create_notification_bot(listeners.GroupUpdateFinishedListener(handler=client_1.get_check_content_handler(new_group.id, notification_type=listeners.NOTIFICATIONS.GROUP_UPDATE_IN_PROGRESS), count=1)))

	# rename group
	await client_1.group_update(group=new_group)

	for bot in bots:
		await bot.wait_for_listeners_end()

	await compare_list_and_get_results(client_1)

	#####
	# disband group
	#####
	# TODO remove: this is to avoid a known bug: in GroupDeleted notification group.type is not properly set
	new_group.type = datatypes.Group.Type.TYPE_UNSPECIFIED
	# create bots to check workflow
	bots = [
		client_1.create_notification_bot(listeners.GroupUpdateInProgressListener(handler=client_1.get_check_content_handler(new_group.id, notification_type=listeners.NOTIFICATIONS.GROUP_UPDATE_IN_PROGRESS), count=1)),
		client_1.create_notification_bot(listeners.DiscussionLockedListener(handler=client_1.get_check_content_handler(ideal_discussion, notification_type=listeners.NOTIFICATIONS.DISCUSSION_LOCKED), count=1)),
		client_1.create_notification_bot(listeners.GroupDeletedListener(handler=client_1.get_check_content_handler(new_group, notification_type=listeners.NOTIFICATIONS.GROUP_DELETED), count=1)),
		client_1.create_notification_bot(listeners.GroupUpdateFinishedListener(handler=client_1.get_check_content_handler(new_group.id, notification_type=listeners.NOTIFICATIONS.GROUP_UPDATE_IN_PROGRESS), count=1)),
	]

	await client_1.group_disband(group_id=group_id)

	for bot in bots:
		await bot.wait_for_listeners_end()

	await compare_list_and_get_results(client_1)


async def compare_list_and_get_results(client: ClientWrapper):
	async for d_list in client.discussion_list():
		d_get: datatypes.Discussion = await client.discussion_get(discussion_id=d_list.id)
		assert d_get == d_list


async def count_messages_in_discussion(client: ClientWrapper, discussion: datatypes.Discussion):
	message_count = 0
	async for _ in client.message_list(filter=datatypes.MessageFilter(discussion_id=discussion.id)):
		message_count += 1
	return message_count


async def test_get_identifier(c1: ClientWrapper):
	async for discussion in c1.discussion_list():
		identifier_1: bytes = await c1.discussion_get_bytes_identifier(discussion_id=discussion.id)
		identifier_2: bytes = await c1.discussion_get_bytes_identifier(discussion_id=discussion.id)
		assert identifier_1, "discussion identifier is empty"
		assert identifier_1 == identifier_2, "discussion identifier are not coherent"


# noinspection PyUnusedLocal
async def test_discussion(client_holder: ClientHolder, fast_mode: bool = False):
	for c1, c2 in client_holder.get_one_client_pair_and_reverse():
		logging.info("-" * 10 + " commands " + "-" * 10)
		await command_tests(c1, c2)
		logging.info("-" * 10 + " notifications " + "-" * 10)
		await test_notifications(c1)
		await test_get_identifier(c1)
