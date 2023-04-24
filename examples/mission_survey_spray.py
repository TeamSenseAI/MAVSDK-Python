#!/usr/bin/env python3

import asyncio
from mavsdk import System
from mavsdk import mission_raw

seq = 0

start = [47.3979628, 8.545607314378373]
end = [47.397696299304066, 8.544122437805441]

async def px4_connect_drone():
    drone = System()
    print("Waiting for drone to connect...")
    await drone.connect(system_address="udp://:14540") # simulator
    # await drone.connect(system_address="serial:///dev/ttyACM0") # serial

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            return drone


async def run():
    drone = await px4_connect_drone()
    await run_drone(drone)


async def sprayerOn():
    mission_items = []

    global seq

    # Turn on sprayer
    seq = seq + 1
    mission_items.append(mission_raw.MissionItem(
         seq,  # start seq at 0
         2,  # frame https://mavlink.io/en/messages/common.html#MAV_FRAME
         205, # command https://mavlink.io/en/messages/common.html#mav_commands
         0,  # first one is current
         1,  # autocontinue
         0, 50, 0, 0, # param 1-4
         0, # local x (param 5)
         0, # local y (param 6)
         2,  # local z (param 7)
         0 # mission type
    ))

    # Delay 2 seconds
    seq = seq + 1
    mission_items.append(mission_raw.MissionItem(
         seq,  # start seq at 0
         2,  # frame https://mavlink.io/en/messages/common.html#MAV_FRAME
         93, # command https://mavlink.io/en/messages/common.html#mav_commands
         0,  # first one is current
         1,  # autocontinue
         2, 0, 0, 0, # param 1-4
         0, # local x (param 5)
         0, # local y (param 6)
         0,  # local z (param 7)
         0 # mission type
    ))

    # Turn on pump
    seq = seq + 1
    mission_items.append(mission_raw.MissionItem(
         seq,  # start seq at 0
         2,  # frame https://mavlink.io/en/messages/common.html#MAV_FRAME
         205, # command https://mavlink.io/en/messages/common.html#mav_commands
         0,  # first one is current
         1,  # autocontinue
         50, 50, 0, 0, # param 1-4
         0, # local x (param 5)
         0, # local y (param 6)
         2,  # local z (param 7)
         0 # mission type
    ))

    return mission_items

async def sprayerOff():
    mission_items = []

    global seq

    # Turn off pump
    seq = seq + 1
    mission_items.append(mission_raw.MissionItem(
         seq,  # start seq at 0
         2,  # frame https://mavlink.io/en/messages/common.html#MAV_FRAME
         205, # command https://mavlink.io/en/messages/common.html#mav_commands
         0,  # first one is current
         1,  # autocontinue
         0, 50, 0, 0, # param 1-4
         0, # local x (param 5)
         0, # local y (param 6)
         2,  # local z (param 7)
         0 # mission type
    ))

    # Delay 2 seconds
    seq = seq + 1
    mission_items.append(mission_raw.MissionItem(
         seq,  # start seq at 0
         2,  # frame https://mavlink.io/en/messages/common.html#MAV_FRAME
         93, # command https://mavlink.io/en/messages/common.html#mav_commands
         0,  # first one is current
         1,  # autocontinue
         2, 0, 0, 0, # param 1-4
         0, # local x (param 5)
         0, # local y (param 6)
         0,  # local z (param 7)
         0 # mission type
    ))

    # Turn of sprayer
    seq = seq + 1
    mission_items.append(mission_raw.MissionItem(
         seq,  # start seq at 0
         2,  # frame https://mavlink.io/en/messages/common.html#MAV_FRAME
         205, # command https://mavlink.io/en/messages/common.html#mav_commands
         0,  # first one is current
         1,  # autocontinue
         0, 0, 0, 0, # param 1-4
         0, # local x (param 5)
         0, # local y (param 6)
         2,  # local z (param 7)
         0 # mission type
    ))

    return mission_items

async def calulate_survey():
    mission_items = []
    forward = True

    global seq

    for lat in range(int(start[0] * 10**7),int(end[0] * 10**7),int(((end[0]-start[0]) * 10**7)/3)):
        if forward:
            for lon in range(int(start[1] * 10**7),int(end[1] * 10**7),int(((end[1]-start[1]) * 10**7)/3)):
                seq = seq + 1
                mission_items.append(mission_raw.MissionItem(
                     seq,  # start seq at 0
                     6,  # frame https://mavlink.io/en/messages/common.html#MAV_FRAME
                     16, # command https://mavlink.io/en/messages/common.html#mav_commands
                     0,  # first one is current
                     1,  # autocontinue
                     0, 10, 0, 1.0, # param 1-4
                     lat, # local x (param 5)
                     lon, # local y (param 6)
                     await get_altitude(),  # local z (param 7)
                     0 # mission type
                ))
        else:
            for lon in range(int(end[1] * 10**7),int(start[1] * 10**7),int(((start[1]-end[1]) * 10**7)/5)):
                seq = seq + 1
                mission_items.append(mission_raw.MissionItem(
                     seq,  # start seq at 0
                     6,  # frame https://mavlink.io/en/messages/common.html#MAV_FRAME
                     16, # command https://mavlink.io/en/messages/common.html#mav_commands
                     0,  # first one is current
                     1,  # autocontinue
                     0, 10, 0, 1.0, # param 1-4
                     lat, # local x (param 5)
                     lon, # local y (param 6)
                     await get_altitude(),  # local z (param 7)
                     0 # mission type
                ))

        forward = not forward

    return mission_items

async def get_altitude():
    return 10.0

async def run_drone(drone):

    mission_items = []

    global seq

    # First we start with a takeoff to a safe altitude
    mission_items.append(mission_raw.MissionItem(
        seq,  # start seq at 0
        6,  # frame https://mavlink.io/en/messages/common.html#MAV_FRAME
        22, # command https://mavlink.io/en/messages/common.html#mav_commands
        1,  # first one is current
        1,  # autocontinue
        0, 0, 0, 1, # param 1-4
        int(47.3977508 * 10**7), # local x (param 5)
        int(8.5456074 * 10**7), # local y (param 6)
        20.0,  # local z (param 7)
        0 # mission type
     ))

    # Go to the first point to start spraying
    seq = seq + 1
    mission_items.append(mission_raw.MissionItem(
        seq,
        6,
        16,
        0,
        1,
        0, 10, 0, 1.0,
        int(start[0] * 10**7),
        int(start[1] * 10**7),
        await get_altitude(),
        0
    ))

    # Turn on spray rig
    mission_items = (mission_items + await sprayerOn())

    # Create survey pattern
    mission_items = (mission_items + await calulate_survey())

    # Turn off spray rig
    mission_items = (mission_items + await sprayerOff())

    # Perform RTL
    seq = seq + 1
    mission_items.append(mission_raw.MissionItem(
        seq,
        2,
        20,
        0,
        1,
        0, 0, 0, float('nan'),
        0,
        0,
        0,
        0
    ))

    print("Number of items: ", len(mission_items))

    print("-- Uploading mission")
    await drone.mission_raw.upload_mission(mission_items)
    print("-- Done")


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
