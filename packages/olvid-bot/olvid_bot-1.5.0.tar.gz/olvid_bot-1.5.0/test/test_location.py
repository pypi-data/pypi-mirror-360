import logging

from ClientHolder import ClientHolder, ClientWrapper
from olvid import datatypes, listeners

test_failed: bool = False

async def location_send(c1: ClientWrapper, c2: ClientWrapper):
	discussion_1, discussion_2 = await c1.get_discussion_associated_to_another_client(c2), await c2.get_discussion_associated_to_another_client(c1)
	contact_1, contact_2 = await c1.get_contact_associated_to_another_client(c2), await c2.get_contact_associated_to_another_client(c1)

	# prepare expected payloads
	expected_body: str = "https://maps.google.com/?q=48.87174+2.32649"
	expected_location_1: datatypes.MessageLocation = datatypes.MessageLocation(type=datatypes.MessageLocation.LocationType.LOCATION_TYPE_SEND, latitude=48.87174, longitude=2.32649, precision=68, altitude=854)
	expected_message_1: datatypes.Message = datatypes.Message(discussion_id=discussion_1.id, body=expected_body, attachments_count=0, message_location=expected_location_1)
	expected_location_2: datatypes.MessageLocation = datatypes.MessageLocation(type=datatypes.MessageLocation.LocationType.LOCATION_TYPE_SEND, latitude=expected_location_1.latitude, longitude=expected_location_1.longitude, altitude=expected_location_1.altitude, precision=expected_location_1.precision)
	expected_message_2: datatypes.Message = datatypes.Message(discussion_id=discussion_2.id, body=expected_body, sender_id=contact_2.id, attachments_count=0, message_location=expected_location_2)

	# prepare notification bots
	bots = [
		c1.create_notification_bot(listeners.MessageSentListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_SENT), count=1)),
		c1.create_notification_bot(listeners.MessageLocationSentListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_SENT), count=1)),
		c1.create_notification_bot(listeners.MessageUploadedListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_UPLOADED), count=1)),
		c1.create_notification_bot(listeners.MessageDeliveredListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELIVERED), count=1)),
		c1.create_notification_bot(listeners.MessageReadListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_READ), count=1)),
		c2.create_notification_bot(listeners.MessageReceivedListener(handler=c2.get_check_content_handler(expected_message_2, notification_type=listeners.NOTIFICATIONS.MESSAGE_RECEIVED), count=1)),
		c2.create_notification_bot(listeners.MessageLocationReceivedListener(handler=c2.get_check_content_handler(expected_message_2, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_RECEIVED), count=1)),
	]

	location_message: datatypes.Message = await c1.message_send_location(discussion_id=discussion_1.id, latitude=expected_location_1.latitude, longitude=expected_location_1.longitude, altitude=expected_location_1.altitude, precision=expected_location_1.precision)
	assert location_message._test_assertion(expected_message_1), "Returned message is not as expected"

	for bot in bots:
		await bot.wait_for_listeners_end()


async def start_location_sharing(c1: ClientWrapper, c2: ClientWrapper) -> tuple[datatypes.Message, datatypes.Message]:
	discussion_1, discussion_2 = await c1.get_discussion_associated_to_another_client(c2), await c2.get_discussion_associated_to_another_client(c1)
	contact_1, contact_2 = await c1.get_contact_associated_to_another_client(c2), await c2.get_contact_associated_to_another_client(c1)

	if len([m async for m in c1.message_list(filter=datatypes.MessageFilter(location=datatypes.MessageFilter.Location.LOCATION_IS_SHARING))]) > 0:
		logging.warning("Found a running sharing location message, next warning on LOCATION_SHARING_END is normal")

	# prepare expected payloads
	expected_body: str = "https://maps.google.com/?q=48.87175+2.32650"
	expected_location_1: datatypes.MessageLocation = datatypes.MessageLocation(type=datatypes.MessageLocation.LocationType.LOCATION_TYPE_SHARING, latitude=48.87175, longitude=2.32650, precision=75, altitude=458)
	expected_message_1: datatypes.Message = datatypes.Message(discussion_id=discussion_1.id, body=expected_body, attachments_count=0, message_location=expected_location_1)
	expected_location_2: datatypes.MessageLocation = datatypes.MessageLocation(type=datatypes.MessageLocation.LocationType.LOCATION_TYPE_SHARING, latitude=expected_location_1.latitude, longitude=expected_location_1.longitude, altitude=expected_location_1.altitude, precision=expected_location_1.precision)
	expected_message_2: datatypes.Message = datatypes.Message(discussion_id=discussion_2.id, body=expected_body, sender_id=contact_2.id, attachments_count=0, message_location=expected_location_2)

	# prepare notification bots
	location_sharing_start_notif: list = []
	bots = [
		c1.create_notification_bot(listeners.MessageSentListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_SENT), count=1)),
		c1.create_notification_bot(listeners.MessageUploadedListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_UPLOADED), count=1)),
		c1.create_notification_bot(listeners.MessageDeliveredListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_DELIVERED), count=1)),
		c1.create_notification_bot(listeners.MessageReadListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_READ), count=1)),
		c1.create_notification_bot(listeners.MessageLocationSharingStartListener(handler=c1.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_SHARING_START), count=1)),

		c2.create_notification_bot(listeners.MessageReceivedListener(handler=c2.get_check_content_handler(expected_message_2, notification_type=listeners.NOTIFICATIONS.MESSAGE_RECEIVED), count=1)),
		c2.create_notification_bot(listeners.MessageLocationSharingStartListener(handler=c2.get_check_content_handler(expected_message_2, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_SHARING_START), count=1)),
		c2.create_notification_bot(listeners.MessageLocationSharingStartListener(handler=c2.get_store_notif_handler(location_sharing_start_notif, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_SHARING_START), count=1)),
	]

	sharing_location_message_1: datatypes.Message = await c1.message_start_location_sharing(discussion_id=discussion_1.id, latitude=expected_location_1.latitude, longitude=expected_location_1.longitude, altitude=expected_location_1.altitude, precision=expected_location_1.precision)
	assert sharing_location_message_1._test_assertion(expected_message_1), "Returned message is not as expected"

	for bot in bots:
		await bot.wait_for_listeners_end()

	sharing_location_message_2: datatypes.Message = location_sharing_start_notif[0]
	return sharing_location_message_1, sharing_location_message_2

async def update_location_sharing(c1: ClientWrapper, c2: ClientWrapper, sharing_location_message_1: datatypes.Message, sharing_location_message_2: datatypes.Message, new_location: datatypes.MessageLocation) -> tuple[datatypes.Message, datatypes.Message]:
	# prepare expected payloads
	expected_previous_location_1: datatypes.MessageLocation = sharing_location_message_1.message_location._clone()
	expected_previous_location_2: datatypes.MessageLocation = sharing_location_message_2.message_location._clone()
	assert expected_previous_location_1._test_assertion(expected_previous_location_2), f"Previous location are not the same on both side: {expected_previous_location_1} != {expected_previous_location_2}"
	expected_body: str = f"https://maps.google.com/?q={new_location.latitude:.5f}+{new_location.longitude:.5f}"
	expected_message_1: datatypes.Message = sharing_location_message_1._clone()
	expected_message_2: datatypes.Message = sharing_location_message_2._clone()
	expected_message_1.body = expected_body
	expected_message_1.message_location = new_location._clone()
	expected_message_2.body = expected_body
	expected_message_2.message_location = new_location._clone()

	# prepare notification bots
	location_sharing_update_notif = []
	bots = [
		c1.create_notification_bot(listeners.MessageLocationSharingUpdateListener(handler=c2.get_check_content_handler(expected_message_1, expected_previous_location_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_SHARING_UPDATE), count=1)),
		c2.create_notification_bot(listeners.MessageLocationSharingUpdateListener(handler=c2.get_check_content_handler(expected_message_2, expected_previous_location_2, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_SHARING_UPDATE), count=1)),
		c2.create_notification_bot(listeners.MessageLocationSharingUpdateListener(handler=c2.get_store_notif_handler(location_sharing_update_notif, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_SHARING_UPDATE), count=1)),
	]

	updated_message: datatypes.Message = await c1.message_update_location_sharing(message_id=sharing_location_message_1.id, latitude=new_location.latitude, longitude=new_location.longitude, altitude=new_location.altitude, precision=new_location.precision)
	assert updated_message._test_assertion(expected_message_1), "Returned message is not as expected"

	for bot in bots:
		await bot.wait_for_listeners_end()

	return updated_message, location_sharing_update_notif[0]


async def end_location_sharing(c1: ClientWrapper, c2: ClientWrapper, sharing_location_message_1: datatypes.Message, sharing_location_message_2: datatypes.Message):
	# prepare expected payloads
	expected_message_1: datatypes.Message = sharing_location_message_1._clone()
	expected_message_1.message_location.type = datatypes.MessageLocation.LocationType.LOCATION_TYPE_SHARING_FINISHED
	expected_message_2: datatypes.Message = sharing_location_message_2._clone()
	expected_message_2.message_location.type = datatypes.MessageLocation.LocationType.LOCATION_TYPE_SHARING_FINISHED

	# prepare notification bots
	location_sharing_update_notif = []
	bots = [
		c1.create_notification_bot(listeners.MessageLocationSharingEndListener(handler=c2.get_check_content_handler(expected_message_1, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_SHARING_END), count=1)),
		c2.create_notification_bot(listeners.MessageLocationSharingEndListener(handler=c2.get_check_content_handler(expected_message_2, notification_type=listeners.NOTIFICATIONS.MESSAGE_LOCATION_SHARING_END), count=1)),
	]

	returned_message: datatypes.Message = await c1.message_end_location_sharing(message_id=sharing_location_message_1.id)
	assert returned_message._test_assertion(expected_message_1), "Returned message is not as expected"

	for bot in bots:
		await bot.wait_for_listeners_end()

# noinspection PyUnusedLocal
async def test_location(client_holder: ClientHolder, fast_mode=False):
	for c1, c2 in client_holder.get_one_client_pair_and_reverse():
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: send location")
		await location_send(c1, c2)
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: start location sharing")
		m1, m2 = await start_location_sharing(c1, c2)
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: update location sharing")
		m1, m2 = await update_location_sharing(c1, c2, m1, m2, new_location=datatypes.MessageLocation(latitude=13.1313, longitude=12.1212, precision=4, altitude=15))
		m1, m2 = await update_location_sharing(c1, c2, m1, m2, new_location=datatypes.MessageLocation(latitude=15.1515, longitude=16.1616, precision=89, altitude=789))
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: end location sharing")
		await end_location_sharing(c1, c2, m1, m2)

		if test_failed:
			raise Exception("Test was marked as failed")
