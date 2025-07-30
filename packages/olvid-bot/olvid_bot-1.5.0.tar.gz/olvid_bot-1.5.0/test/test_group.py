import logging
import base64
import os

import ressources

from grpc.aio import AioRpcError

from ClientHolder import ClientHolder, ClientWrapper
from utils.tools_group import create_standard_group, create_controlled_group
from olvid import OlvidClient, datatypes, listeners


# noinspection PyProtectedMember
def get_group_seen_by_a_member(original_group: datatypes.Group, member_contact_id: int):
	group: datatypes.Group = original_group._clone()

	# exchange member and owner permissions
	contact_member: datatypes.GroupMember = [m for m in group.members if m.contact_id == member_contact_id][0]
	contact_permissions: datatypes.GroupMemberPermissions = contact_member.permissions
	contact_member.permissions = group.own_permissions
	group.own_permissions = contact_permissions

	# hide ids
	group.id = 0
	for member in group.members:
		member.contact_id = 0
	for pending_member in group.pending_members:
		pending_member.contact_id = 0
		pending_member.pending_member_id = 0

	return group


async def test_disband_group(client_holder: ClientHolder, admin_client: ClientWrapper, group_id: int):
	member_clients: list[ClientWrapper] = [c for c in client_holder.clients if c != admin_client]
	member_contacts: list[datatypes.Contact] = [await admin_client.get_contact_associated_to_another_client(c) for c in
												member_clients]

	original_group: datatypes.Group = await admin_client.group_get(group_id=group_id)

	# create notif-checker bots for group admin
	bots: list[OlvidClient] = [
		admin_client.create_notification_bot(listeners.GroupDeletedListener(handler=admin_client.get_check_content_handler(original_group, notification_type=listeners.NOTIFICATIONS.GROUP_DELETED), count=1)),
		admin_client.create_notification_bot(listeners.DiscussionLockedListener(handler=admin_client.get_check_content_handler(datatypes.Discussion(title=original_group.name), notification_type=listeners.NOTIFICATIONS.DISCUSSION_LOCKED), count=1)),
		admin_client.create_notification_bot(listeners.GroupUpdateInProgressListener(handler=lambda gid: gid, count=1)),
		admin_client.create_notification_bot(listeners.GroupUpdateFinishedListener(handler=lambda gid: gid, count=1)),
	]

	# TODO remove this, used to pass a known bug (group type is not stored so we cannot retrieve it when group have been disbanded)
	original_group.type = datatypes.Group.Type.TYPE_UNSPECIFIED

	# create notif-checker bots for members
	for i in range(len(member_clients)):
		member_client = member_clients[i]
		member_contact_id = member_contacts[i].id
		bots.extend([
			member_client.create_notification_bot(listeners.GroupDeletedListener(handler=member_client.get_check_content_handler(get_group_seen_by_a_member(original_group, member_contact_id), notification_type=listeners.NOTIFICATIONS.GROUP_DELETED), count=1)),
			member_client.create_notification_bot(listeners.DiscussionLockedListener(handler=member_client.get_check_content_handler(datatypes.Discussion(title=original_group.name), notification_type=listeners.NOTIFICATIONS.DISCUSSION_LOCKED), count=1)),
		])

	disbanded_group = await admin_client.group_disband(group_id=original_group.id)
	disbanded_group._test_assertion(original_group)

	for bot in bots:
		await bot.wait_for_listeners_end()
		await bot.stop()


async def test_try_do_delete_a_contact_in_group(client_holder: ClientHolder, admin_client: ClientWrapper):
	member_clients: list[ClientWrapper] = [c for c in client_holder.clients if c != admin_client]
	member_contacts: list[datatypes.Contact] = [await admin_client.get_contact_associated_to_another_client(c) for c in member_clients]

	for member_contact in member_contacts:
		try:
			await admin_client.contact_delete(contact_id=member_contact.id)
			assert False, "Was able to delete a contact in a group"
		except AioRpcError:
			continue


async def test_concurrent_group_updates(client_holder: ClientHolder, admin_client: ClientWrapper, group_id: int):
	member_clients: list[ClientWrapper] = [c for c in client_holder.clients if c != admin_client]
	member_contacts: list[datatypes.Contact] = [await admin_client.get_contact_associated_to_another_client(c) for c in member_clients]

	original_group: datatypes.Group = await admin_client.group_get(group_id=group_id)

	group_updated_1: datatypes.Group = original_group._clone()
	group_updated_1.name += "-First Update"
	group_updated_1.description += "-First Update"
	group_updated_2: datatypes.Group = original_group._clone()
	group_updated_2.name = ""
	group_updated_2.description = ""

	# this handler is used to check multiple ordered notifications with different content
	def get_recursive_check_content_handler(client: ClientWrapper, listener_type: type[listeners.GenericNotificationListener], expectations: list[tuple], notification_type: listeners.NOTIFICATIONS):
		def recursive_check_content_handler(*messages):
			if not expectations:
				assert False, "Invalid expectations count"
			handler = client.get_check_content_handler(*(expectations[0]), notification_type=notification_type)
			ret = handler(*messages)

			# create next listener
			if len(expectations) > 1:
				# noinspection PyArgumentList
				client.create_notification_bot(listener_type(handler=get_recursive_check_content_handler(client, listener_type=listener_type, expectations=expectations[1:], notification_type=notification_type), count=1))

			return ret
		return recursive_check_content_handler

	# wait for task 1 and associated notif
	# create notif-checker bots for group admin
	bots: list[OlvidClient] = [
		admin_client.create_notification_bot(
			listeners.GroupNameUpdatedListener(
				handler=get_recursive_check_content_handler(admin_client, listeners.GroupNameUpdatedListener, [(group_updated_1, original_group.name), (group_updated_2, group_updated_1.name)], notification_type=listeners.NOTIFICATIONS.GROUP_NAME_UPDATED),
				count=1)),
		admin_client.create_notification_bot(
			listeners.GroupDescriptionUpdatedListener(
				handler=get_recursive_check_content_handler(admin_client, listeners.GroupDescriptionUpdatedListener, [(group_updated_1, original_group.description), (group_updated_2, group_updated_1.description)], notification_type=listeners.NOTIFICATIONS.GROUP_DESCRIPTION_UPDATED),
				count=1)),
		admin_client.create_notification_bot(
			listeners.DiscussionTitleUpdatedListener(
				handler=get_recursive_check_content_handler(admin_client, listeners.DiscussionTitleUpdatedListener, [(datatypes.Discussion(title=group_updated_1.name), original_group.name), (datatypes.Discussion(title=group_updated_2.name), group_updated_1.name)], notification_type=listeners.NOTIFICATIONS.DISCUSSION_TITLE_UPDATED),
				count=1)),
	]

	# create notif-checker bots for members: members only receive one update notifications (updates are probably too fast to give time to handle intermediary blob)
	for i in range(len(member_clients)):
		member_client = member_clients[i]
		member_contact_id = member_contacts[i].id
		bots.extend([
			member_client.create_notification_bot(
				listeners.GroupNameUpdatedListener(
					handler=member_client.get_check_content_handler(get_group_seen_by_a_member(group_updated_2, member_contact_id), original_group.name, notification_type=listeners.NOTIFICATIONS.GROUP_NAME_UPDATED),
					count=1)),
			member_client.create_notification_bot(
				listeners.GroupDescriptionUpdatedListener(
					handler=member_client.get_check_content_handler(get_group_seen_by_a_member(group_updated_2, member_contact_id), original_group.description, notification_type=listeners.NOTIFICATIONS.GROUP_DESCRIPTION_UPDATED),
					count=1)),
			member_client.create_notification_bot(
				listeners.DiscussionTitleUpdatedListener(
					handler=member_client.get_check_content_handler(datatypes.Discussion(title=group_updated_2.name), original_group.name, notification_type=listeners.NOTIFICATIONS.DISCUSSION_TITLE_UPDATED),
					count=1)),
		])

	# launch concurrent tasks
	task1 = admin_client.group_update(group=group_updated_1)
	task2 = admin_client.group_update(group=group_updated_2)

	group_update_response_1: datatypes.Group = await task1
	group_update_response_1._test_assertion(group_updated_1)

	group_update_response_2: datatypes.Group = await task2
	group_update_response_2._test_assertion(group_updated_2)

	for bot in bots:
		await bot.wait_for_listeners_end()


# noinspection DuplicatedCode
async def test_update_member_permissions(client_holder: ClientHolder, admin_client: ClientWrapper, group_id: int):
	member_clients: list[ClientWrapper] = [c for c in client_holder.clients if c != admin_client]
	member_contacts: list[datatypes.Contact] = [await admin_client.get_contact_associated_to_another_client(c) for c in
												member_clients]

	original_group: datatypes.Group = await admin_client.group_get(group_id=group_id)

	if not original_group.own_permissions.admin:
		return

	# choose a member, save it's permissions and update it
	group: datatypes.Group = original_group._clone()
	member_contact_id: int = member_contacts[0].id
	member_index: int = [i for i in range(len(group.members)) if group.members[i].contact_id == member_contact_id][0]
	original_member_permissions: datatypes.GroupMemberPermissions = group.members[member_index].permissions._clone()
	new_member_permissions: datatypes.GroupMemberPermissions = datatypes.GroupMemberPermissions()
	group.members[member_index].permissions = new_member_permissions

	# prepare notification handlers
	bots: list[OlvidClient] = [
		admin_client.create_notification_bot(
			listeners.GroupMemberPermissionsUpdatedListener(
				handler=admin_client.get_check_content_handler(group, group.members[member_index], original_member_permissions, notification_type=listeners.NOTIFICATIONS.GROUP_MEMBER_PERMISSIONS_UPDATED),
				count=1)),
	]

	# update member permissions
	response_group = await admin_client.group_update(group=group)
	response_group._test_assertion(group)

	# wait for notifications
	for bot in bots:
		await bot.wait_for_listeners_end()

	####
	# restore original permissions
	####
	group.members[member_index].permissions = original_member_permissions
	bots: list[OlvidClient] = [
		admin_client.create_notification_bot(
			listeners.GroupMemberPermissionsUpdatedListener(
				handler=admin_client.get_check_content_handler(group, group.members[member_index], new_member_permissions, notification_type=listeners.NOTIFICATIONS.GROUP_MEMBER_PERMISSIONS_UPDATED),
				count=1)),
	]

	# update member permissions
	response_group = await admin_client.group_update(group=group)
	response_group._test_assertion(group)

	# wait for notifications
	for bot in bots:
		await bot.wait_for_listeners_end()


async def test_set_download_unset_photo(client_holder: ClientHolder, admin_client: ClientWrapper, group_id: int):
	admin_group: datatypes.Group = await admin_client.group_get(group_id=group_id)

	# create notification bots to set photo
	bots: list[OlvidClient] = []
	for client in client_holder.clients:
		group: datatypes.Group = [g async for g in client.group_list(filter=datatypes.GroupFilter(name_search=admin_group.name, description_search=admin_group.description))][-1]
		group_with_photo: datatypes.Group = group._clone()
		group_with_photo.has_a_photo = True
		# we ignore this deprecated field in checks
		group_with_photo.update_in_progress = False
		bots.append(client.create_notification_bot(
			listener=listeners.GroupPhotoUpdatedListener(handler=client.get_check_content_handler(group_with_photo), count=1)
		))

	# set group photo
	with open("image.png", "wb") as fd:
		fd.write(base64.b64decode(ressources.PNG_IMAGE_AS_B64))
	await admin_client.group_set_photo(group_id=group_id, file_path="image.png")
	os.remove("image.png")

	for bot in bots:
		await bot.wait_for_listeners_end()
		await bot.stop()

	# download photo and check validity
	downloaded_photo: bytes = await admin_client.group_download_photo(group_id=admin_group.id)
	for client in client_holder.clients:
		if client == admin_client:
			continue
		group: datatypes.Group = [g async for g in client.group_list(filter=datatypes.GroupFilter(name_search=admin_group.name, description_search=admin_group.description))][-1]
		other_downloaded_photo: bytes = await client.group_download_photo(group_id=group.id)
		assert len(downloaded_photo) != ressources.PNG_IMAGE_LENGTH_AFTER_DOWNLOAD_DOWNLOADER_SIDE, f"invalid uploader photo size ({len(downloaded_photo)})"
		assert len(other_downloaded_photo) != ressources.PNG_IMAGE_LENGTH_AFTER_DOWNLOAD_UPLOADER_SIDE, f"invalid downloader photo size {len(other_downloaded_photo)}"

	# create notification bots to unset photo
	bots: list[OlvidClient] = []
	for client in client_holder.clients:
		group: datatypes.Group = [g async for g in client.group_list(filter=datatypes.GroupFilter(name_search=admin_group.name, description_search=admin_group.description))][-1]
		group_without_photo: datatypes.Group = group._clone()
		group_without_photo.has_a_photo = False
		# we ignore this deprecated field in checks
		group_without_photo.update_in_progress = False
		bots.append(client.create_notification_bot(
			listener=listeners.GroupPhotoUpdatedListener(handler=client.get_check_content_handler(group_without_photo), count=1)
		))

	# unset photo
	await admin_client.group_unset_photo(group_id=admin_group.id)

	for bot in bots:
		await bot.wait_for_listeners_end()
		await bot.stop()

	# download photo and check validity
	downloaded_photo: bytes = await admin_client.group_download_photo(group_id=admin_group.id)
	for client in client_holder.clients:
		if client == admin_client:
			continue
		group: datatypes.Group = [g async for g in client.group_list(filter=datatypes.GroupFilter(name_search=admin_group.name, description_search=admin_group.description))][-1]
		other_downloaded_photo: bytes = await client.group_download_photo(group_id=group.id)
		assert len(downloaded_photo) != ressources.PNG_IMAGE_LENGTH_AFTER_DOWNLOAD_DOWNLOADER_SIDE, f"invalid uploader photo size ({len(downloaded_photo)})"
		assert len(other_downloaded_photo) != ressources.PNG_IMAGE_LENGTH_AFTER_DOWNLOAD_UPLOADER_SIDE, f"invalid downloader photo size {len(other_downloaded_photo)}"


async def test_get_identifier(c1: ClientWrapper, group_1: datatypes.Group, client_holder: ClientHolder):
	for c2 in client_holder.clients[1:]:
		group_2: datatypes.Group = [g async for g in c2.group_list(filter=datatypes.GroupFilter(name_search=group_1.name, description_search=group_1.description))][-1]
		identifier_1 = await c1.group_get_bytes_identifier(group_id=group_1.id)
		identifier_2 = await c2.group_get_bytes_identifier(group_id=group_2.id)
		assert identifier_1, "group identifier is empty"
		assert identifier_2, "group identifier is empty"
		assert identifier_1 == identifier_2, "group identifier are not coherent"


async def test_group(client_holder: ClientHolder):
	client = client_holder.clients[0]
	logging.info(f"{client.identity.id}: create normal group")
	group = await create_standard_group(client_holder, client, f"{client.identity.id}-NormalGroupName", group_description=f"{client.identity.id} normal group description")

	await test_get_identifier(client, group, client_holder)

	logging.info(f"{client.identity.id}: delete contact in a group")
	await test_try_do_delete_a_contact_in_group(client_holder, client)
	logging.info(f"{client.identity.id}: concurrent group updates")
	await test_concurrent_group_updates(client_holder, client, group.id)
	logging.info(f"{client.identity.id}: permission updates")
	await test_update_member_permissions(client_holder, client, group.id)
	logging.info(f"{client.identity.id}: set/unset photo")
	await test_set_download_unset_photo(client_holder, client, group.id)

	logging.info(f"{client.identity.id}: disband normal group")
	await test_disband_group(client_holder, client, group.id)

	logging.info(f"{client.identity.id}: create empty name group")
	group = await create_standard_group(client_holder, client, "", "")
	assert group.name == "", "Empty group name is not empty"
	logging.info(f"{client.identity.id}: disband empty name group")
	await test_disband_group(client_holder, client, group.id)

	logging.info(f"{client.identity.id}: create controlled group")
	group = await create_controlled_group(client_holder, client, f"{client.identity.id}-Controlled", group_description="")
	logging.info(f"{client.identity.id}: disband controlled group")
	await test_disband_group(client_holder, client, group.id)


