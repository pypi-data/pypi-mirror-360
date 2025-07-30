import logging

from ClientHolder import ClientHolder, ClientWrapper

async def test_tool(client_holder: ClientHolder, fast_mode=False):
	logging.info(f"tools: ping")
	for c in client_holder.clients:
		await c.ping()
