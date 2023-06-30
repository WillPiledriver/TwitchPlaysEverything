from TwitchPlays import *
from dotenv import load_dotenv
import os
from pywitch import PyWitchHeat
import threading
import pydirectinput
from global_hotkeys import *
import numpy as np
from sklearn.cluster import DBSCAN

# Set the LOKY_MAX_CPU_COUNT environment variable
os.environ['LOKY_MAX_CPU_COUNT'] = '4'



click_cooldown = 0
channel = "thepiledriver"
heat_map = True
command_chance = 1.0
command_cooldown = 0


load_dotenv()
user_dict = dict()
x_coordinates = np.array([])
y_coordinates = np.array([])

def callback(data):
    global x_coordinates, y_coordinates, user_dict
    size_x, size_y = pydirectinput.size()
    if data["user_id"] in user_dict:
        if user_dict[data["user_id"]]["time"] + click_cooldown > data["event_time"]:
            return
    
    x, y = int(data["x"] * size_x), int(data["y"] * size_y)
    user_dict[data["user_id"]] = {
        "time": data["event_time"],
        "coords": (x, y)
    }

    print(x, y)
    # x_coordinates = np.append(x_coordinates, x)
    # y_coordinates = np.append(y_coordinates, y)
    # pydirectinput.mouseDown(x, y, button="left")
    # pydirectinput.mouseUp(x, y, button="left")

def mouse_loop():
    global x_coordinates, y_coordinates, user_dict
    while True:
        if len(user_dict) == 0:
            print("nothing clicked")
            time.sleep(5)
            continue
        
        x_coordinates = np.array([data["coords"][0] for user, data in user_dict.items()])
        y_coordinates = np.array([data["coords"][1] for user, data in user_dict.items()])

        coordinates = np.column_stack((x_coordinates, y_coordinates))

        # Define the DBSCAN parameters
        eps = 150  # Distance threshold for clustering
        min_samples = 1  # Minimum number of points in a cluster

        # Perform DBSCAN clustering
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(coordinates)

        # Find the cluster with the most points
        unique_labels, counts = np.unique(labels, return_counts=True)
        most_populated_cluster_label = unique_labels[np.argmax(counts)]

        # Get the center coordinates of the most populated cluster
        most_populated_cluster = coordinates[labels == most_populated_cluster_label]
        center = np.mean(most_populated_cluster, axis=0)

        x, y = [round(center[0]), round(center[1])]
        print("Center coordinates:", x, y)
        pydirectinput.mouseDown(x, y, button="left")
        time.sleep(0.15)
        pydirectinput.mouseUp(x, y, button="left")
        user_dict = dict()
        time.sleep(5)

if heat_map:
    heat = PyWitchHeat(channel, os.getenv("ACCESS_TOKEN"), callback)
bot = Bot(os.getenv("TWITCH_TOKEN"), "!", [channel])
bot.keys = {
            "w": [("w", 1000)],
            "d": [("d", 1000)],
            "a": [("a", 1000)],
            "s": [("s", 1000)],
            "jump": [("space", 100)],
            "hover": [("space", 1000)],
            "kick": [("f", 100)],
            "e": [("e", 100)],
            "1": {("1", 100)},
            "2": {("2", 100)},
            "3": {("3", 100)},
            "4": {("4", 100)},
            "5": {("5", 100)},
            "6": {("6", 100)},
            "7": {("7", 100)},
            "8": {("8", 100)},
        }
'''bot.mouse = {
            "left": [((-10, 0), 0)],
            "right": [((10, 0), 0)],
            "up": [((0, -10), 0)],
            "down": [((0, 10), 0)],
            "lc": [((0, 0), 1)], # left click
            "rc": [((0, 0), 2)], # right click
            "mm": [((0, 0), 3)], # middle mouse button
            "lu": [((-100, 0), 1), ((0,-100), 2)], # left up, mouse 1 and 2
}'''
bot.chance = command_chance
bot.cooldown = command_cooldown
# bot.cmd["!help"] = help_cmd

@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    cmds = [f"!{cmd}" for cmd in list(bot.commands.keys())] + list(bot.cmds.keys()) + list(bot.keys.keys()) + list(bot.mouse.keys())
    response = f"@{ctx.author.name}: {', '.join(cmds)}."
    await ctx.reply(response)

async def kill_script():
    # I dont like this solution
    '''    heat.stop()
    await bot.close()'''
    os._exit(0)

def on_hotkey_press():
    asyncio.run(kill_script())

async def main():
    bindings = [{
        "hotkey": "control + down",
        "on_press_callback": on_hotkey_press,
        "on_release_callback": None,
        "actuate_on_partial_release": False
    }]
    thread1 = threading.Thread(target=bot.run)
    # thread3 = threading.Thread(target=run_forever)
    thread1.start()
    if heat_map:
        thread2 = threading.Thread(target=heat.start)
        thread2.start()
        thread3 = threading.Thread(target=mouse_loop)
        thread3.start()
    loop = asyncio.get_event_loop()
    register_hotkeys(bindings)
    start_checking_hotkeys()
    # thread3.start()
    thread1.join()
    if heat_map:
        thread2.join()
        thread3.join()
    # thread3.join()
    loop.stop()
    

if __name__ == "__main__":
    asyncio.run(main())