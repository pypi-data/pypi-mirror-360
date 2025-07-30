#!/usr/bin/env python3
"""Example demonstrating browser control with Fleet Manager Client."""

import asyncio
import fleet as flt


async def main():
    fleet = flt.AsyncFleet()

    environments = await fleet.list_envs()
    print("Environments:", len(environments))

    instances = await fleet.instances(status="running")
    print("Instances:", len(instances))

    instance = await fleet.instance("16fdbc96")
    print("Instance:", instance.instance_id)
    print("Instance Environment:", instance.env_key)

    environment = await fleet.environment(instance.env_key)
    print("Environment Default Version:", environment.default_version)

    response = await instance.env.reset()
    print("Reset response:", response)

    print(await instance.env.resources())

    sqlite = instance.env.sqlite("current")
    print("SQLite:", await sqlite.describe())

    print("Query:", await sqlite.query("SELECT * FROM users"))

    sqlite = await instance.env.state("sqlite://current").describe()
    print("SQLite:", sqlite)

    browser = await instance.env.browser("cdp").describe()
    print("CDP URL:", browser.url)
    print("CDP Devtools URL:", browser.devtools_url)

    # Create a new instance
    instance = await fleet.make(flt.InstanceRequest(env_key=instance.env_key))
    print("New Instance:", instance.instance_id)

    # Delete the instance
    instance = await fleet.delete(instance.instance_id)
    print("Instance deleted:", instance.terminated_at)


if __name__ == "__main__":
    asyncio.run(main())
