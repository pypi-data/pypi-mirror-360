from ClientHolder import ClientHolder, ClientWrapper

async def check_entries_count(client: ClientWrapper, expected_count: int, discussion_id: int = None):
	count = 0
	if discussion_id is not None:
		async for _ in client.discussion_storage_list(discussion_id=discussion_id):
			count += 1
	else:
		async for _ in client.storage_list():
			count += 1
	assert count == expected_count


async def check_storage_state(client: ClientWrapper, expected_global_storage: list[tuple[str, str]], discussion_id: int = None, expected_discussion_storage: list[tuple[str, str]] = None):
	for k, v in expected_global_storage:
		value = await client.storage_get(k)
		assert value == v
	await check_entries_count(client, len(expected_global_storage))

	if discussion_id is not None:
		for k, v in expected_discussion_storage:
			value = await client.discussion_storage_get(discussion_id=discussion_id, key=k)
			assert value == v
		await check_entries_count(client, len(expected_discussion_storage), discussion_id=discussion_id)


async def basic_routine_global(client: ClientWrapper):
	# Storage is empty
	await check_storage_state(client, [])

	# set some keys
	test_vectors: list[tuple[str, str]] = [("1", "NoValue"), ("ComplexeK2", "myVaLUASD"), ("123", "42321"), ("EmptyValue", "")]
	for k, v in test_vectors:
		previous_value = await client.storage_set(key=k, value=v)
		assert previous_value == ""

	# override values
	expected_previous_value = test_vectors[0][1]
	test_vectors[0] = (test_vectors[0][0], "NewValue")
	previous_value = await client.storage_set(key=test_vectors[0][0], value=test_vectors[0][1])
	assert previous_value == expected_previous_value
	await check_storage_state(client, test_vectors)

	expected_previous_value = test_vectors[0][1]
	previous_value = await client.storage_set(key=test_vectors[0][0], value=test_vectors[0][1])
	assert previous_value == expected_previous_value
	await check_storage_state(client, test_vectors)

	# check list entry point is ok
	async for element in client.storage_list():
		assert (element.key, element.value) in test_vectors

	# get invalid key
	value = await client.storage_get("UnknownKey")
	assert value == ""
	value = await client.storage_get("ThisKeyIsNotValid")
	assert value == ""

	# delete keys
	for element in test_vectors.copy():
		previous_value = await client.storage_unset(element[0])
		test_vectors.remove(element)
		assert previous_value == element[1]
		await check_storage_state(client, test_vectors)

	await check_storage_state(client, [])


async def basic_routine_discussion(client: ClientWrapper, discussion_id: int):
	# Storage is empty
	await check_storage_state(client, [], discussion_id, [])

	# set some keys
	test_vectors: list[tuple[str, str]] = [("1", "NoValue"), ("ComplexeK2", "myVaLUASD"), ("123", "42321"), ("EmptyValue", "")]
	for k, v in test_vectors:
		previous_value = await client.discussion_storage_set(discussion_id=discussion_id, key=k, value=v)
		assert previous_value == ""

	# override values
	expected_previous_value = test_vectors[0][1]
	test_vectors[0] = (test_vectors[0][0], "NewValue")
	previous_value = await client.discussion_storage_set(discussion_id=discussion_id, key=test_vectors[0][0], value=test_vectors[0][1])
	assert previous_value == expected_previous_value
	await check_storage_state(client, [], discussion_id, test_vectors)

	expected_previous_value = test_vectors[0][1]
	previous_value = await client.discussion_storage_set(discussion_id=discussion_id, key=test_vectors[0][0], value=test_vectors[0][1])
	assert previous_value == expected_previous_value
	await check_storage_state(client, [], discussion_id, test_vectors)

	# check list entry point is ok
	async for element in client.discussion_storage_list(discussion_id=discussion_id):
		assert (element.key, element.value) in test_vectors

	# get invalid key
	value = await client.discussion_storage_get(discussion_id=discussion_id, key="UnknownKey")
	assert value == ""
	value = await client.discussion_storage_get(discussion_id=discussion_id, key="ThisKeyIsNotValid")
	assert value == ""

	# delete keys
	for element in test_vectors.copy():
		previous_value = await client.discussion_storage_unset(discussion_id=discussion_id, key=element[0])
		test_vectors.remove(element)
		assert previous_value == element[1]
		await check_storage_state(client, [], discussion_id, test_vectors)

	await check_storage_state(client, [], discussion_id, [])


async def global_try_to_get_other_client_storage(client_1: ClientWrapper, client_2: ClientWrapper):
	# set elements
	await client_1.storage_set("Client1Key", "YouCantSeeMe")
	await client_2.storage_set("Client2Key", "YouCantSeeMe")

	# get invalid key
	value = await client_1.storage_get("Client2Key")
	assert value == ""

	value = await client_2.storage_get("Client1Key")
	assert value == ""

	# delete keys
	await client_1.storage_unset("Client1Key")
	await client_2.storage_unset("Client2Key")


async def clear_storage(c1: ClientWrapper, c2: ClientWrapper):
	async for element in c1.storage_list():
		await c1.storage_unset(element.key)

	async for discussion in c1.discussion_list():
		async for element in c1.discussion_storage_list(discussion_id=discussion.id):
			await c1.discussion_storage_unset(discussion_id=discussion.id, key=element.key)

	async for element in c2.storage_list():
		await c2.storage_unset(element.key)

	async for discussion in c2.discussion_list():
		async for element in c2.discussion_storage_list(discussion_id=discussion.id):
			await c2.discussion_storage_unset(discussion_id=discussion.id, key=element.key)

async def test_storage(client_holder: ClientHolder):
	for c1, c2 in client_holder.get_all_client_pairs():
		await clear_storage(c1, c2)

		await basic_routine_global(c1)
		await basic_routine_global(c2)

		discussion = await c1.get_discussion_associated_to_another_client(other_client=c2)

		await basic_routine_discussion(c1, discussion.id)

		await global_try_to_get_other_client_storage(c1, c2)

		await check_storage_state(c1, [], discussion.id, [])
		await check_storage_state(c2, [])
