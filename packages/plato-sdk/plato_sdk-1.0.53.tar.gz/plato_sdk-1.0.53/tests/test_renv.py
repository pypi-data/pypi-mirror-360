import os

from plato.models.env import PlatoEnvironment
from plato import Plato, PlatoTask
import asyncio
import json


async def main():
    client = Plato()

    env1 = await client.make_environment("espocrm", interface_type=None)
    print(f"env1: {env1.id} with id() {id(env1)}")
    await env1.wait_for_ready(timeout=300)
    print("env1 ready")
    env2 = await PlatoEnvironment.from_id(client, env1.id)
    print(f"env2: {env2.id} with id() {id(env2)}")
    await env2.reset()
    print("env2 reset")

    await asyncio.sleep(300)

    await env1.close()
    await env2.close()


if __name__ == "__main__":
    asyncio.run(main())
