from configparser import ConfigParser
import json, os
def getconfig(type: str, savename: str, created: str | None = "y") -> dict:
    if created == "y":
        config = ConfigParser()
        # Use the user’s home directory and create the config file path
        home_directory = os.path.expanduser("~")
        configname = os.path.join(home_directory, type + "config.ini")
        config.read(configname)
        if savename not in config:
            raise ValueError(f"Config '{savename}' not found.")
        
        
        if savename in config:
            if type == "baron":
                nick = config.get(savename, "nick")
                pwrd = config.get(savename, "pwrd")
                server = config.get(savename, "server")
                kid = config.get(savename, "kid")
                excluded_commanders = config.get(savename, "excluded_commanders")
                radius_option = config.get(savename, "radius_option")
                distance = config.getfloat(savename, "distance")  # converted to float
                vip_option = config.get(savename, "vip_option")
                max_flank = config.getint(savename, "max_flank")  # converted to int
                max_front = config.getint(savename, "max_front")  # converted to int
                unit_id = config.get(savename, "unit_id")
                flank_id = config.get(savename, "flank_id")
                flank_tool_ammount = config.getint(savename, "flank_tool_ammount")  # converted to int
                front_id_1 = config.get(savename, "front_id_1")
                front_tool_ammount1 = config.getint(savename, "front_tool_ammount1")  # converted to int
                front_id_2 = config.get(savename, "front_id_2")
                front_tool_ammount2 = config.getint(savename, "front_tool_ammount2")  # converted to int
                # Return as a dictionary
                result = {
                    "nick": nick,
                    "pwrd": pwrd,
                    "server": server,
                    "kid": kid,
                    "excluded_commanders": excluded_commanders,
                    "radius_option": radius_option,
                    "distance": distance,
                    "vip_option": vip_option,
                    "max_flank": max_flank,
                    "max_front": max_front,
                    "unit_id": unit_id,
                    "flank_id": flank_id,
                    "flank_tool_ammount": flank_tool_ammount,
                    "front_id_1": front_id_1,
                    "front_tool_ammount1": front_tool_ammount1,
                    "front_id_2": front_id_2,
                    "front_tool_ammount2": front_tool_ammount2
                }
                
                # Convert to JSON string and return
                return result  # Return a formatted JSON string
    if created == "n":
        home_directory = os.path.expanduser("~")
        configname = os.path.join(home_directory, type + "config.ini")
        config_maker_barons(savename, configname)
    else:
        print("Invalid str as the created parameter. Use 'y' or 'n' - y if you have created the config already, 'n' if no.")
        exit()
        return {}
    return {}

def config_maker_barons(savename, filename: str):
    config = ConfigParser()
    unit_options = {
        "1": ("Distance Samurai", '35'),
        "2": ("Distance Veteran Demon", '10'),
        "3": ("Distance Mead lvl 10", '216'),
        "4": ("Distance Mead lvl 2", '207'),
        "5": ("Distance Mead lvl 1", '206'),
        "6": ("Distance Mead lvl 0", '205'),
        "7": ("Meelee   Mead lvl 10", '215'),
        "8": ("Meelee   Mead lvl 3", '198'),
        "9": ("Meelee   Mead lvl 2", '197'),
        "10": ("Meelee   Mead lvl 1", '196'),
        "11": ("Meelee   Mead lvl 0", '195')
    }

    flank_tool_options = {
        "1": ("20%  towers", '649'),
        "2": ("5%   ladders", '614'),
        "3": ("15%  steel walls (anti distance)", '651'),
        "4": ("5%   wooden walls (anti distance)", '651'),
        "5": ("--   None", '-1')
    }

    front_tool_options_1 = {
        "1": ("20%  towers", '649'),
        "2": ("5%   ladders", '614'),
        "3": ("15%  steel walls (anti distance)", '651'),
        "4": ("5%   wooden walls (anti distance)", '651'),
        "5": ("--   None", '-1')
    }

    front_tool_options_2 = {
        "1": ("20%  ram", '648'),
        "2": ("5%   ram", '611'),
        "3": ("--   None", '-1')
    }

    config.read(filename)
    print(f'Saves: {config.sections()}')
    save_name = savename
    while True:
        if not save_name:
            print("...")
            exit()
        elif config.has_section(save_name):
            if_overwrite = input("Save with this name already exists. Do you want to overwrite it?\n(y/n): ")
            if if_overwrite == 'y': 
                config.remove_section(save_name)
            else:
                print("Exitting.")
                exit()
        else:
            break
    config.add_section(save_name)

    def input_int_list(prompt):
        while True:
            raw = input(prompt).strip()
            if raw:
                try:
                    values = [int(item.strip()) for item in raw.split(",") if item.strip()]
                    return ",".join(str(val) for val in values)
                except ValueError:
                    print("Please enter valid comma separated integers (e.g. 2,29,30,31).")
            else:
                print("Input cannot be empty.")

    def input_int(prompt):
        while True:
            raw = input(prompt).strip()
            if raw:
                try:
                    return str(int(raw))
                except ValueError:
                    print("Please enter a valid integer.")
            else:
                print("Input cannot be empty.")

    nick = input("Enter your nickname: ")
    config.set(save_name, "nick", nick)
    passwd = input("Enter your password (stored local): ")
    config.set(save_name, "pwrd", passwd)
    server = input("Enter your server (e.g. PL1): ")
    config.set(save_name, "server", server)
    kid = input("Kingdom Green = g, Kingdom Fire = f, Kingdom Sand = s, Kingdom Cold = c\nKingdom -> <-\b\b\b")
    config.set(save_name, "kid", kid)

    excluded_commanders = input_int_list("Enter excluded commanders (comma separated integers, e.g. 2,3,17. -1 if none): ")
    config.set(save_name, "excluded_commanders", excluded_commanders)
    
    radius_option = "c"
    config.set(save_name, "radius_option", radius_option)

    distance = input_int("Distance for attacks (not preicse): ")
    config.set(save_name, "distance", distance)

    vip_option = input("Do you want the bot to use VIP commanders? (if no, it will send all commanders, wait until they come back and do it until the end.)\n(y/n) -> <-\b\b\b")
    if vip_option in ["y", "n"]:
        config.set(save_name, "vip_option", vip_option)
    else:
        print("Not an answer. y for yes, n for no.")
        exit()

    print("The script will use 4 waves. Always. Each wave will have the same setup.")
    max_flank = input_int("Enter ammount of units on a flank (0 if none)  : ")
    config.set(save_name, "max_flank", max_flank)

    max_front = input_int("Enter ammount of units on the front (0 if none): ")
    config.set(save_name, "max_front", max_front)

    print("\nPick units to send in the attack\n")
    for key, value in unit_options.items():
        print(f"{key}   - {value[0]}\n")
    unit_choice = (input("Selection: "))
    print(f'Selected option "{unit_options[unit_choice][0]}"')
    config.set(save_name, "unit_id", str(unit_options[unit_choice][1]))

    print("\nPick wich tool do you want to use on the flanks\n")
    for key, value in flank_tool_options.items():
        print(f"{key}   - {value[0]}\n")
    flank_choice = input("Selection: ")
    print(f'Selected option "{flank_tool_options[flank_choice][0]}"')
    config.set(save_name, "flank_id", str(flank_tool_options[flank_choice][1]))

    if flank_tool_options[flank_choice][0] != "--   None":
        flank_tool_ammount = input_int("Enter ammount of those tools per flank: ")
        config.set(save_name, "flank_tool_ammount", flank_tool_ammount)
    else:
        config.set(save_name, "flank_tool_ammount", "0")

    print("\nPick the first tool you want to use on the front\n")
    for key, value in front_tool_options_1.items():
        print(f"{key}   - {value[0]}\n")
    front_choice1 = input("Selection: ")
    print(f'Selected option "{front_tool_options_1[front_choice1][0]}"')
    config.set(save_name, "front_id_1", str(front_tool_options_1[front_choice1][1]))

    if front_tool_options_1[front_choice1][0] != "--   None":
        front_tool_ammount1 = input_int("Enter ammount of those tools per front: ")
        config.set(save_name, "front_tool_ammount1", front_tool_ammount1)
    else:
        config.set(save_name, "front_tool_ammount1", "0")

    print("\nPick the second tool you want to use on the front\n")
    for key, value in front_tool_options_2.items():
        print(f"{key}   - {value[0]}\n")
    front_choice2 = input("Selection: ")
    print(f'Selected option "{front_tool_options_2[front_choice2][0]}"')
    config.set(save_name, "front_id_2", str(front_tool_options_2[front_choice2][1]))

    if front_tool_options_2[front_choice2][0] != "--   None":
        front_tool_ammount2 = input_int("Enter ammount of those tools per front: ")
        config.set(save_name, "front_tool_ammount2", front_tool_ammount2)
    else:
        config.set(save_name, "front_tool_ammount2", "0")

    with open(filename, "w") as f:
        config.write(f)
    
    print(f"\nConfiguration saved.")
    exit()
