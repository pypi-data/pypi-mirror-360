import asyncio
import base64
import logging
import random
import string
from os import remove

import grpc.aio

from ClientHolder import ClientHolder, ClientWrapper
from olvid import datatypes
import ressources


# noinspection PyProtectedMember
async def create_identities(client_holder: ClientHolder, number_of_identities: int):
	#####
	# Create identities
	#####
	random_prefix = "".join(random.choice(string.ascii_letters) for _ in range(5))
	for i in range(number_of_identities):
		first_name = f"TestIdentity-{random_prefix}"
		last_name = str(i)
		position = "TO DEL"
		company = "Earth"
		identity = await client_holder.create_identity(first_name=first_name, last_name=last_name, position=position, company=company)
		expected_identity = datatypes.Identity(details=datatypes.IdentityDetails(first_name=first_name, last_name=last_name, position=position, company=company), display_name=f"{first_name} {last_name} ({position} @ {company})", keycloak_managed=False)
		assert identity._test_assertion(expected_identity)

	#####
	# Show created identities
	#####
	for client in client_holder.clients:
		logging.info(f"{client.identity.id}: {client.identity.details.first_name} {client.identity.details.last_name}")

	#####
	# Check admin identity get commands
	#####
	for client in client_holder.clients:
		assert client.identity == await client_holder.admin_client.admin_identity_admin_get(client.identity.id)
		assert await client.identity_get() == await client_holder.admin_client.admin_identity_admin_get(client.identity.id)


async def set_and_unset_identity_photo(client: ClientWrapper):
	# file that does not exist
	try:
		await client.identity_set_photo("this_file_does_not_exists.txt")
		raise Exception(f"Do not detected invalid file")
	except IOError:
		pass
	except Exception as e:
		print(type(e))
		raise Exception(f"Invalid exception raised: {e}")
	# check image is set (wait for DbCache to be up-to-date ...)
	await asyncio.sleep(0.1)
	assert not (await client.identity_get()).has_a_photo

	# valid filename, invalid payload
	try:
		with open("invalid_photo.png", "w") as fd:
			fd.write("This is not a photo !" * 20)
		await client.identity_set_photo("invalid_photo.png")
		raise Exception(f"Daemon accepted an invalid format image")
	except grpc.aio.AioRpcError:
		pass
	except Exception as e:
		raise Exception(f"Invalid exception raised: {e}")
	finally:
		remove("invalid_photo.png")
	# check image is set (wait for DbCache to be up-to-date ...)
	await asyncio.sleep(0.1)
	assert not (await client.identity_get()).has_a_photo

	# valid image
	with open("image.png", "wb") as fd:
		fd.write(base64.b64decode(ressources.PNG_IMAGE_AS_B64))
	await client.identity_set_photo("image.png")

	await asyncio.sleep(0.1)  # added to be sure new photo is set in database
	# download image and check it's valid
	downloaded_image: bytes = await client.identity_download_photo()
	# downloaded image len is hardcoded for this given image, after daemon re-compressed it
	assert downloaded_image and len(downloaded_image) > 0, f"downloaded identity photo is invalid ({len(downloaded_image)})"

	# check image is set (wait for db to be up-to-date ...)
	# TODO add and wait for identity_photo_updated notification
	c = 0
	while not (await client.identity_get()).has_a_photo:
		await asyncio.sleep(0.1)
		c += 1
		if c == 100:
			assert (await client.identity_get()).has_a_photo

	# unset image
	await client.identity_remove_photo()

	# delete file on disk
	remove("image.png")


async def admin_test_get_identifier(client_holder: ClientHolder):
	async for identity in client_holder.admin_client.admin_identity_list():
		identifier_1: bytes = await client_holder.admin_client.admin_identity_admin_get_bytes_identifier(identity_id=identity.id)
		identifier_2: bytes = await client_holder.admin_client.admin_identity_admin_get_bytes_identifier(identity_id=identity.id)
		assert identifier_1, "identity identifier is empty"
		assert identifier_1 == identifier_2

async def admin_test_invitation_link(client_holder: ClientHolder):
	async for identity in client_holder.admin_client.admin_identity_list():
		link: str = await client_holder.admin_client.admin_identity_admin_get_invitation_link(identity_id=identity.id)
		assert link, "empty identity invitation link"
		assert link.startswith("https://invitation.olvid.io/#"), f"Invalid identity invitation link format: {link}"
		assert len(link.removeprefix("https://invitation.olvid.io/#")) > 0, f"Invalid identity invitation link payload: {link}"

async def test_get_identifier(c1: ClientWrapper):
	identifier_1: bytes = await c1.identity_get_bytes_identifier()
	identifier_2: bytes = await c1.identity_get_bytes_identifier()
	assert identifier_1, "identity identifier is empty"
	assert identifier_1 == identifier_2

async def test_invitation_link(c1: ClientWrapper):
	link: str = await c1.identity_get_invitation_link()
	assert link, "empty contact invitation link"
	assert link.startswith("https://invitation.olvid.io/#"), "Invalid contact invitation link format"
	assert len(link.removeprefix("https://invitation.olvid.io/#")) > 0, f"Invalid identity invitation link payload: {link}"


async def test_identity(client_holder: ClientHolder, number_of_identities: int):
	await create_identities(client_holder, number_of_identities)

	# admin identity tests
	await admin_test_get_identifier(client_holder)
	await admin_test_invitation_link(client_holder)

	for client in client_holder.clients:
		await set_and_unset_identity_photo(client)
		await test_get_identifier(client)
		await test_invitation_link(client)
