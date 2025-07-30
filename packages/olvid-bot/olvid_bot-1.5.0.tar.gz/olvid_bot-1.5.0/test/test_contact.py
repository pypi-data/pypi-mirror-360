import logging

from ClientHolder import ClientHolder, ClientWrapper
from olvid import OlvidClient, datatypes, listeners, errors
from utils.tools_message import send_message_wait_and_check_content
from utils.tools_identity import update_identity_details


# noinspection PyProtectedMember
async def test_check_list_and_get_content(client_holder: ClientHolder, client1: ClientWrapper, client2: ClientWrapper):
	# check number of contacts is correct
	identity_count = len(client_holder.clients)
	contacts1 = [c async for c in client1.contact_list()]
	assert len(contacts1) == identity_count - 1
	contacts2 = [c async for c in client2.contact_list()]
	assert len(contacts2) == identity_count - 1

	# check contact_lis and contact_get returns same data
	[(await client1.contact_get(contact_id=c.id))._test_assertion(c) for c in contacts1]
	[(await client1.contact_get(contact_id=c.id))._test_assertion(c) for c in contacts1]


# noinspection PyProtectedMember
async def test_down_upgrade_one_to_one_and_locked_discussions(client1: ClientWrapper, client2: ClientWrapper):
	# get other client contact on each side
	contact1: datatypes.Contact = await client1.get_contact_associated_to_another_client(client2)
	contact2: datatypes.Contact = await client2.get_contact_associated_to_another_client(client1)

	if not contact1.has_one_to_one_discussion or not contact2.has_one_to_one_discussion:
		logging.warning(f"test_contact: contacts are not one to one, upgrading channel first ({client1.identity.id} <-> {client2.identity.id})")
		await upgrade_contact_to_one_to_one(client1, client2, contact1, contact2, ideal_discussion1=datatypes.Discussion(title=contact1.display_name), ideal_discussion2=datatypes.Discussion(title=contact2.display_name))

	# get other client discussion on each side
	discussion1: datatypes.Discussion = await client1.get_discussion_associated_to_another_client(client2)
	discussion2: datatypes.Discussion = await client2.get_discussion_associated_to_another_client(client1)

	# send message in discussions to be sure it's not empty
	await send_message_wait_and_check_content(client1, client2, body="Do not let discussion empty")

	# mark as not one to one cause we will use this value to check notif content
	contact1.has_one_to_one_discussion = False
	contact2.has_one_to_one_discussion = False

	# create bot to check discussion is properly locked
	bots: list[OlvidClient] = [
		# discussion locked on each side
		client1.create_notification_bot(listeners.DiscussionLockedListener(handler=client1.get_check_content_handler(discussion1, notification_type=listeners.NOTIFICATIONS.DISCUSSION_LOCKED), count=1)),
		client2.create_notification_bot(listeners.DiscussionLockedListener(handler=client2.get_check_content_handler(discussion2, notification_type=listeners.NOTIFICATIONS.DISCUSSION_LOCKED), count=1)),
	]

	# delete contact (downgrade to not one to one discussion)
	await client1.contact_downgrade_one_to_one_discussion(contact_id=contact1.id)

	# wait for notifications
	for bot in bots:
		await bot.wait_for_listeners_end()
		await bot.stop()

	# check contacts are still here and have been downgraded
	contact1._test_assertion(await client1.contact_get(contact1.id))
	contact2._test_assertion(await client2.contact_get(contact2.id))

	# check discussion appear as locked
	assert len([ld async for ld in client1.discussion_locked_list() if ld.id == discussion1.id]) == 1, "locked discussion cannot be listed"
	assert len([ld async for ld in client2.discussion_locked_list() if ld.id == discussion2.id]) == 1, "locked discussion cannot be listed"

	# check discussion is not listed anymore
	assert len([ld async for ld in client1.discussion_list() if ld.id == discussion1.id]) == 0, "locked discussion still listed"
	assert len([ld async for ld in client2.discussion_list() if ld.id == discussion2.id]) == 0, "locked discussion still listed"

	# check discussion is not getable
	try:
		await client1.discussion_get(discussion_id=discussion1.id)
		assert False, "discussion still accessible"
	except errors.NotFoundError:
		pass
	try:
		await client2.discussion_get(discussion_id=discussion2.id)
		assert False, "discussion still accessible"
	except errors.NotFoundError:
		pass

	# actually we can do it, that's probably what we want to do
	# check we cannot list messages in a locked discussion
	# try:
	# 	messages = [m async for m in client1.message_list(datatypes.MessageFilter(discussion_id=discussion1.id))]
	# 	assert False, f"can list messages in a locked discussion: {messages}"
	# except errors.NotFoundError:
	# 	pass
	# try:
	# 	messages = [m async for m in client2.message_list(datatypes.MessageFilter(discussion_id=discussion2.id))]
	# 	assert False, f"can list messages in a locked discussion: {messages}"
	# except errors.NotFoundError:
	# 	pass

	# check we cannot send a message in a locked discussion
	try:
		await client1.message_send(discussion_id=discussion1.id, body="This message MUST NOT be sent")
		assert False, "can post in a locked discussion"
	except errors.NotFoundError:
		pass
	try:
		await client2.message_send(discussion_id=discussion2.id, body="This message MUST NOT be sent")
		assert False, "can post in a locked discussion"
	except errors.NotFoundError:
		pass

	# delete locked discussion
	await client1.discussion_locked_delete(discussion_id=discussion1.id)
	await client2.discussion_locked_delete(discussion_id=discussion2.id)

	# check discussion locked had been deleted
	assert len([ld async for ld in client1.discussion_locked_list() if ld.id == discussion1.id]) == 0, "deleted locked discussion can be listed"
	assert len([ld async for ld in client2.discussion_locked_list() if ld.id == discussion2.id]) == 0, "deleted locked discussion can be listed"

	# check discussion is not listed anymore
	assert len([ld async for ld in client1.discussion_list() if ld.id == discussion1.id]) == 0, "locked discussion still listed as normal after deletion"
	assert len([ld async for ld in client2.discussion_list() if ld.id == discussion2.id]) == 0, "locked discussion still listed as normal after deletion"

	# check discussion is not getable
	try:
		await client1.discussion_get(discussion_id=discussion1.id)
		assert False, "discussion still accessible"
	except errors.NotFoundError:
		pass
	try:
		await client2.discussion_get(discussion_id=discussion2.id)
		assert False, "discussion still accessible"
	except errors.NotFoundError:
		pass

	await upgrade_contact_to_one_to_one(client1, client2, contact1, contact2,
										ideal_discussion1=datatypes.Discussion(title=contact1.display_name),
										ideal_discussion2=datatypes.Discussion(title=contact2.display_name))

	new_contact_1: datatypes.Contact = await client1.contact_get(contact_id=contact1.id)
	# get new contact and check content
	new_contact_1._test_assertion(contact1)
	new_contact_2: datatypes.Contact = await client2.contact_get(contact_id=contact2.id)
	new_contact_2._test_assertion(contact2)


# noinspection PyProtectedMember
async def upgrade_contact_to_one_to_one(client1: ClientWrapper, client2: ClientWrapper, contact1: datatypes.Contact, contact2: datatypes.Contact, ideal_discussion1: datatypes.Discussion, ideal_discussion2: datatypes.Discussion):
	# prepare notification bots for one to one upgrade process
	# noinspection PyProtectedMember
	async def accept_invitation_handler(invitation: datatypes.Invitation):
		await invitation._client.invitation_accept(invitation.id)
	bots = [
		# client1: invitation sent, invitation deleted, contact new, discussion new
		client1.create_notification_bot(listeners.InvitationSentListener(handler=client1.get_check_content_handler(datatypes.Invitation(status=datatypes.Invitation.Status.STATUS_ONE_TO_ONE_INVITATION_WAIT_IT_TO_ACCEPT, display_name=contact1.display_name, sas=""), notification_type=listeners.NOTIFICATIONS.INVITATION_SENT), count=1)),
		client1.create_notification_bot(listeners.InvitationDeletedListener(handler=client1.get_check_content_handler(datatypes.Invitation(status=datatypes.Invitation.Status.STATUS_ONE_TO_ONE_INVITATION_WAIT_IT_TO_ACCEPT, display_name=contact1.display_name, sas=""), notification_type=listeners.NOTIFICATIONS.INVITATION_DELETED), count=1)),
		client1.create_notification_bot(listeners.DiscussionNewListener(handler=client1.get_check_content_handler(ideal_discussion1, notification_type=listeners.NOTIFICATIONS.DISCUSSION_NEW), count=1)),

		# client2: invitation received (check content and accept it), invitation deleted, contact new, discussion new
		client2.create_notification_bot(listeners.InvitationReceivedListener(handler=client2.get_check_content_handler(datatypes.Invitation(status=datatypes.Invitation.Status.STATUS_ONE_TO_ONE_INVITATION_WAIT_YOU_TO_ACCEPT, display_name=contact2.display_name, sas=""), notification_type=listeners.NOTIFICATIONS.INVITATION_SENT), count=1)),
		client2.create_notification_bot(listeners.InvitationReceivedListener(handler=accept_invitation_handler, count=1)),
		client2.create_notification_bot(listeners.InvitationDeletedListener(handler=client2.get_check_content_handler(datatypes.Invitation(status=datatypes.Invitation.Status.STATUS_ONE_TO_ONE_INVITATION_WAIT_YOU_TO_ACCEPT, display_name=contact2.display_name, sas=""), notification_type=listeners.NOTIFICATIONS.INVITATION_DELETED), count=1)),
		client2.create_notification_bot(listeners.DiscussionNewListener(handler=client2.get_check_content_handler(ideal_discussion2, notification_type=listeners.NOTIFICATIONS.DISCUSSION_NEW), count=1)),
	]

	await client1.contact_invite_to_one_to_one_discussion(contact_id=contact1.id)

	for bot in bots:
		await bot.wait_for_listeners_end()
		await bot.stop()

	# wait for channel to be established
	await client1.wait_for_channel_creation()
	await client2.wait_for_channel_creation()
	logging.debug(f"channel created {client1.identity.id} <-> {client2.identity.id}")

	# get new contact and check content
	ideal_contact1 = contact1._clone()
	ideal_contact1.has_one_to_one_discussion = True
	ideal_contact2 = contact2._clone()
	ideal_contact2.has_one_to_one_discussion = True
	new_contact_1: datatypes.Contact = await client1.contact_get(contact_id=contact1.id)
	new_contact_1._test_assertion(ideal_contact1)
	new_contact_2: datatypes.Contact = await client2.contact_get(contact_id=contact2.id)
	new_contact_2._test_assertion(ideal_contact2)


async def test_update_details(c1: ClientWrapper, c2: ClientWrapper, client_holder: ClientHolder):
	# prepare new details for client2
	prev_details: datatypes.IdentityDetails = c1.identity.details
	new_details: datatypes.IdentityDetails = datatypes.IdentityDetails(first_name=prev_details.first_name + "-UPDATED", last_name=prev_details.last_name + "-UPDATED", position=prev_details.position + "-UPDATED", company=prev_details.company + "-UPDATED")

	discussion_2: datatypes.Discussion = await c2.get_discussion_associated_to_another_client(c1)
	contact_2: datatypes.Contact = await c2.get_contact_associated_to_another_client(c1)

	try:
		await update_identity_details(c1, client_holder, new_details)
		assert (await c2.discussion_get(discussion_id=discussion_2.id)).title == f"{new_details.first_name} {new_details.last_name} ({new_details.position} @ {new_details.company})"
		assert (await c2.contact_get(contact_id=contact_2.id)).display_name == f"{new_details.first_name} {new_details.last_name} ({new_details.position} @ {new_details.company})"

		await update_identity_details(c1, client_holder, prev_details)
		assert (await c2.discussion_get(discussion_id=discussion_2.id)).title == f"{prev_details.first_name} {prev_details.last_name} ({prev_details.position} @ {prev_details.company})"
		assert (await c2.contact_get(contact_id=contact_2.id)).display_name == f"{prev_details.first_name} {prev_details.last_name} ({prev_details.position} @ {prev_details.company})"

	# if something goes wrong try to restore previous details before exiting
	except Exception:
		await c1.identity_update_details(prev_details)
		raise


async def test_get_identifier(c1: ClientWrapper, c2: ClientWrapper):
	contact_1, contact_2 = await c1.get_contact_associated_to_another_client(c2), await c2.get_contact_associated_to_another_client(c1)
	identifier_1: bytes = await c1.identity_get_bytes_identifier()
	identifier_contact_1: bytes = await c1.contact_get_bytes_identifier(contact_id=contact_1.id)
	identifier_2: bytes = await c2.identity_get_bytes_identifier()
	identifier_contact_2: bytes = await c2.contact_get_bytes_identifier(contact_id=contact_2.id)
	assert identifier_1 and identifier_contact_1 and identifier_2 and identifier_contact_2, "contact identifier is empty"
	assert identifier_1 == identifier_contact_2, "contact identifier 1 are not coherent"
	assert identifier_2 == identifier_contact_1, "contact identifier 2 are not coherent"


async def test_invitation_link(c1: ClientWrapper, c2: ClientWrapper):
	contact_1, contact_2 = await c1.get_contact_associated_to_another_client(c2), await c2.get_contact_associated_to_another_client(c1)
	invitation_link_1: str = await c1.identity_get_invitation_link()
	invitation_link_contact_1: str = await c1.contact_get_invitation_link(contact_id=contact_1.id)
	invitation_link_2: str = await c2.identity_get_invitation_link()
	invitation_link_contact_2: str = await c2.contact_get_invitation_link(contact_id=contact_2.id)
	assert invitation_link_1 and invitation_link_contact_1 and invitation_link_2 and invitation_link_contact_2, "contact invitation_link is empty"
	assert invitation_link_1 == invitation_link_contact_2, "contact invitation_link 1 are not coherent"
	assert invitation_link_2 == invitation_link_contact_1, "contact invitation_link 2 are not coherent"


async def test_contact(client_holder: ClientHolder):
	c1, c2 = client_holder.get_one_client_pair()
	logging.info(f"{c1.identity.id} <-> {c2.identity.id}: prepare tests")
	await test_check_list_and_get_content(client_holder, c1, c2)
	logging.info(f"{c1.identity.id} <-> {c2.identity.id}: downgrade one to one")
	await test_down_upgrade_one_to_one_and_locked_discussions(c1, c2)
	logging.info(f"{c1.identity.id} <-> {c2.identity.id}: update contact details")
	await test_update_details(c1, c2, client_holder)

	for c1, c2 in client_holder.get_one_client_pair_and_reverse():
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: identifier")
		await test_get_identifier(c1, c2)
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: invitation link")
		await test_invitation_link(c1, c2)
