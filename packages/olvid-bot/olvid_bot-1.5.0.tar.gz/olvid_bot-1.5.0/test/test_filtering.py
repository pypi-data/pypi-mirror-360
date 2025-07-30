import re
import logging
from typing import Any

from olvid import datatypes, listeners, OlvidClient
from ClientHolder import ClientHolder, ClientWrapper
from utils.tools_group import create_standard_group
from utils.tools_message import send_message_wait_and_check_content, send_message_with_attachments_in_memory_and_check
from utils.tools_reaction import react_message


def compare_ordered_lists(given: list[Any], expected: list[Any]):
	assert len(given) == len(expected), f"Invalid list length: {len(given)} != {len(expected)}\ngiven:{given}\nexpected: {expected}"
	for i in range(len(given)):
		assert given[i] == expected[i], f"Invalid element in list: {given[i]} != {expected[i]}\ngiven:{given}\nexpected: {expected}"


def message_sort_key(m: datatypes.Message):
	return m.id.id if m.id.type == datatypes.MessageId.Type.TYPE_INBOUND else -1 * m.id.id

def compare_message_lists(given: list[datatypes.Message], expected: list[datatypes.Message]):
	given = sorted(given, key=message_sort_key)
	expected = sorted(expected, key=message_sort_key)
	return compare_ordered_lists(given, expected)

async def test_filtering_discussion(client_holder: ClientHolder, c1: ClientWrapper, c2: ClientWrapper):
	# create group discussion
	group_standard = await create_standard_group(client_holder=client_holder, admin_client=c1, group_name="Group Name", group_description="")
	group_controlled = await create_standard_group(client_holder=client_holder, admin_client=c1, group_name="Group Name", group_description="")

	all_discussions_1: list[datatypes.Discussion] = sorted([d async for d in c1.discussion_list()], key=lambda d: d.id)
	all_discussions_2: list[datatypes.Discussion] = sorted([d async for d in c2.discussion_list()], key=lambda d: d.id)

	# .type: unspecified
	unspecified_discussion_1: list[datatypes.Discussion] = sorted([d async for d in c1.discussion_list(filter=datatypes.DiscussionFilter(type=datatypes.DiscussionFilter.Type.TYPE_UNSPECIFIED))], key=lambda d: d.id)
	compare_ordered_lists(unspecified_discussion_1, [d for d in all_discussions_1])
	unspecified_discussion_2: list[datatypes.Discussion] = sorted([d async for d in c2.discussion_list(filter=datatypes.DiscussionFilter(type=datatypes.DiscussionFilter.Type.TYPE_UNSPECIFIED))], key=lambda d: d.id)
	compare_ordered_lists(unspecified_discussion_2, [d for d in all_discussions_2])

	# .type: oto
	oto_discussion_1: list[datatypes.Discussion] = sorted([d async for d in c1.discussion_list(filter=datatypes.DiscussionFilter(type=datatypes.DiscussionFilter.Type.TYPE_OTO))], key=lambda d: d.id)
	compare_ordered_lists(oto_discussion_1, [d for d in all_discussions_1 if d.contact_id != 0])
	oto_discussion_2: list[datatypes.Discussion] = sorted([d async for d in c2.discussion_list(filter=datatypes.DiscussionFilter(type=datatypes.DiscussionFilter.Type.TYPE_OTO))], key=lambda d: d.id)
	compare_ordered_lists(oto_discussion_2, [d for d in all_discussions_2 if d.contact_id != 0])

	# .type: group
	group_discussion_1: list[datatypes.Discussion] = sorted([d async for d in c1.discussion_list(filter=datatypes.DiscussionFilter(type=datatypes.DiscussionFilter.Type.TYPE_GROUP))], key=lambda d: d.id)
	compare_ordered_lists(group_discussion_1, [d for d in all_discussions_1 if d.group_id != 0])
	group_discussion_2: list[datatypes.Discussion] = sorted([d async for d in c2.discussion_list(filter=datatypes.DiscussionFilter(type=datatypes.DiscussionFilter.Type.TYPE_GROUP))], key=lambda d: d.id)
	compare_ordered_lists(group_discussion_2, [d for d in all_discussions_2 if d.group_id != 0])

	# identifier: contact_id
	cid_discussions_1: list[datatypes.Discussion] = sorted([d async for d in c1.discussion_list(filter=datatypes.DiscussionFilter(contact_id=oto_discussion_1[0].contact_id))], key=lambda d: d.id)
	compare_ordered_lists(cid_discussions_1, [d for d in all_discussions_1 if d.contact_id == oto_discussion_1[0].contact_id])
	cid_discussions_2: list[datatypes.Discussion] = sorted([d async for d in c2.discussion_list(filter=datatypes.DiscussionFilter(contact_id=oto_discussion_2[0].contact_id))], key=lambda d: d.id)
	compare_ordered_lists(cid_discussions_2, [d for d in all_discussions_2 if d.contact_id == oto_discussion_2[0].contact_id])

	# identifier: group_id
	if len(group_discussion_1) > 0 and len(group_discussion_2) > 0:
		group_discussions_1: list[datatypes.Discussion] = sorted([d async for d in c1.discussion_list(filter=datatypes.DiscussionFilter(group_id=group_discussion_1[0].group_id))], key=lambda d: d.id)
		compare_ordered_lists(group_discussions_1, [d for d in all_discussions_1 if d.group_id == group_discussion_1[0].group_id])
		group_discussions_2: list[datatypes.Discussion] = sorted([d async for d in c2.discussion_list(filter=datatypes.DiscussionFilter(group_id=group_discussion_2[0].group_id))], key=lambda d: d.id)
		compare_ordered_lists(group_discussions_2, [d for d in all_discussions_2 if d.group_id == group_discussion_2[0].group_id])
	else:
		logging.warning("skipped group discussion filtering tests cause there are no group discussions")

	# title search 1
	title_discussions_1: list[datatypes.Discussion] = sorted([d async for d in c1.discussion_list(filter=datatypes.DiscussionFilter(title_search="^TestIdentity"))], key=lambda d: d.id)
	compare_ordered_lists(title_discussions_1, [d for d in all_discussions_1 if d.title.startswith("TestIdentity")])
	title_discussions_2: list[datatypes.Discussion] = sorted([d async for d in c2.discussion_list(filter=datatypes.DiscussionFilter(title_search="^TestIdentity"))], key=lambda d: d.id)
	compare_ordered_lists(title_discussions_2, [d for d in all_discussions_2 if d.title.startswith("TestIdentity")])

	# clean
	await c1.group_disband(group_id=group_standard.id)
	await c1.group_disband(group_id=group_controlled.id)


async def test_filtering_messages(c1: ClientWrapper, c2: ClientWrapper):
	contact_1, contact_2 = await c1.get_contact_associated_to_another_client(c2), await c2.get_contact_associated_to_another_client(c1)

	# create messages
	await send_message_wait_and_check_content(c1, c2, "Hello there")
	await send_message_wait_and_check_content(c1, c2, "my body is 1")
	message_to_react_to_1_1, message_to_react_to_1_2 = await send_message_wait_and_check_content(c1, c2, "Please react to me")
	message_to_react_to_2_1, message_to_react_to_2_2 = await send_message_wait_and_check_content(c1, c2, "I want reactions too")
	message_to_reply_to_1, message_to_reply_to_2 = await send_message_wait_and_check_content(c1, c2, "MY body is 2")
	await send_message_wait_and_check_content(c1, c2, "This message embed a reply", replied_message_ids=(message_to_reply_to_1.id, message_to_reply_to_2.id))
	await send_message_with_attachments_in_memory_and_check(c1, c2, body="", filenames=["file.txt", "image.jpg"], file_contents=[b"a", b"d"])
	await send_message_with_attachments_in_memory_and_check(c1, c2, body="Film and image", filenames=["film.mp4", "image.jpg"], file_contents=[b"a", b"d"])

	# send reactions
	# add bot for reactions
	bots: list[OlvidClient] = [
		c1.create_notification_bot(listeners.MessageReactionAddedListener(handler=lambda m, r: m, count=2)),
		c2.create_notification_bot(listeners.MessageReactionAddedListener(handler=lambda m, r: m, count=2)),
		c1.create_notification_bot(listeners.MessageReactionAddedListener(handler=lambda m, r: m, count=1, filter=datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reacted_by_me=True, reaction="🌍")]))),
		c2.create_notification_bot(listeners.MessageReactionAddedListener(handler=lambda m, r: m, count=1, filter=datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reacted_by_contact_id=contact_2.id, reaction="🌍")]))),
		c1.create_notification_bot(listeners.MessageReactionAddedListener(handler=lambda m, r: m, count=1, filter=datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reacted_by_contact_id=contact_1.id, reaction="🪦")]))),
		c2.create_notification_bot(listeners.MessageReactionAddedListener(handler=lambda m, r: m, count=1, filter=datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reacted_by_me=True, reaction="🪦")]))),
	]
	await react_message(c1, c2, message_to_react_to_1_1.id, message_to_react_to_1_2.id, "🌍" )
	await react_message(c2, c1, message_to_react_to_2_2.id, message_to_react_to_2_1.id, "🪦" )

	for bot in bots:
		await bot.wait_for_listeners_end()

	####
	# start tests
	####
	all_messages_1: list[datatypes.Message] = sorted([m async for m in c1.message_list()], key=message_sort_key)
	all_messages_2: list[datatypes.Message] = sorted([m async for m in c2.message_list()], key=message_sort_key)

	# no filter
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter()
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1])

	# body search
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(body_search="body")
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if re.findall(r"body", m.body)])
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(body_search="nothing you can find in a body")
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if re.findall(r"nothing you can find in a body", m.body)])
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(body_search="^my")
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if re.findall(r"^my", m.body)])
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(body_search="")
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if re.findall(r"", m.body)])

	# location
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(location=datatypes.MessageFilter.Location.LOCATION_HAVE)
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if m.message_location])
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(location=datatypes.MessageFilter.Location.LOCATION_HAVE_NOT)
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if not m.message_location])

	# reply
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(do_not_reply_to_a_message=True)
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if not m.replied_message_id])
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(reply_to_a_message=True)
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if m.replied_message_id])
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(replied_message_id=message_to_reply_to_1.id)
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if m.replied_message_id == message_to_reply_to_1.id])
	message_filter: datatypes.MessageFilter = datatypes.MessageFilter(replied_message_id=message_to_react_to_1_1.id)
	compare_message_lists([m async for m in c1.message_list(filter=message_filter)], [m for m in all_messages_1 if m.replied_message_id == message_to_react_to_1_1.id])

	# reactions
	# noinspection PyShadowingBuiltins
	async def test_reaction(client: ClientWrapper, other_client_contact_id: int, all_messages: list[datatypes.Message]):
		# reaction
		filter: datatypes.MessageFilter = datatypes.MessageFilter(has_reaction=datatypes.MessageFilter.Reaction.REACTION_HAS)
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions]) > 0])
		filter: datatypes.MessageFilter = datatypes.MessageFilter(has_reaction=datatypes.MessageFilter.Reaction.REACTION_HAS_NOT)
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions]) == 0])

		# reaction filters
		filter: datatypes.MessageFilter = datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reaction="🌍")])
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions if r.reaction == "🌍"]) > 0])
		filter: datatypes.MessageFilter = datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reaction="🌍", reacted_by_me=True)])
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions if r.reaction == "🌍" and r.contact_id == 0]) > 0])
		filter: datatypes.MessageFilter = datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reaction="🪦")])
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions if r.reaction == "🪦"]) > 0])
		filter: datatypes.MessageFilter = datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reaction="🪦", reacted_by_contact_id=other_client_contact_id)])
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions if r.reaction == "🪦" and r.contact_id == other_client_contact_id]) > 0])
		filter: datatypes.MessageFilter = datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reaction="💣")])
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions if r.reaction == "💣"]) > 0])
		filter: datatypes.MessageFilter = datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reaction="💣", reacted_by_me=True)])
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions if r.reaction == "💣" and r.contact_id == 0]) > 0])
		filter: datatypes.MessageFilter = datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reaction="💣", reacted_by_contact_id=other_client_contact_id)])
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions if r.reaction == "💣" and r.contact_id == other_client_contact_id]) > 0])
		filter: datatypes.MessageFilter = datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reacted_by_me=True)])
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions if r.contact_id == 0]) > 0])
		filter: datatypes.MessageFilter = datatypes.MessageFilter(reactions_filter=[datatypes.ReactionFilter(reacted_by_contact_id=other_client_contact_id)])
		compare_message_lists([m async for m in client.message_list(filter=filter)], [m for m in all_messages if len([r for r in m.reactions if r.contact_id == other_client_contact_id]) > 0])

	await test_reaction(c1, contact_1.id, all_messages_1)
	await test_reaction(c2, contact_2.id, all_messages_2)


async def test_filtering(client_holder: ClientHolder, fast_mode=False):
	for c1, c2 in client_holder.get_one_client_pair_and_reverse():
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: discussion filtering")
		await test_filtering_discussion(client_holder, c1, c2)
		logging.info(f"{c1.identity.id} <-> {c2.identity.id}: message filtering")
		await test_filtering_messages(c1, c2)
