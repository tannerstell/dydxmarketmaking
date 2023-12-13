import multiprocessing
import os
import time
import json
import pprint
from typing import Optional

path = "C:\\enter\\path\\here\\"

def execute(task):

    os.chdir(path)

    if task != "":
        os.system(task)

if __name__ == "__main__":
    tasks = ['py -c "import ws; ws.main()']

    def which_file():
        print([json_files for json_files in os.listdir() if ".json" in json_files])
        settings_file_name = input("Which settings file do you want to change?: ")
        return settings_file_name

    def file_setting():

        def add_symbol(settings):
            symbol = input("What symbol would you like to add?: ")
            try:
                if symbol in settings["symbols"][0].keys():
                    return print("Symbol already exists.")
            except IndexError:
                pass

            params = {"{}".format(symbol): {"l_num_orders": "", "s_num_orders": "", "l_order_pct": "", "s_order_pct": "",
                                   "l_spacing_sd": "", "s_spacing_sd": "", "inc": "", "l_multiplier": "",
                                   "s_multiplier": "", "max_leverage": "", "tp_pct": ""}
             }
            settings["symbols"][0].update(params)
            for i in range(1, 12):
                settings = f(i, symbol, settings)
            return settings

        def new_json():
            settings_file_name = str(input("What do you want to name the file? (blah.json): "))
            with open("settings.json", 'r') as r:
                credentials = json.load(r)["credentials"]
            json_values = {"default_parameters": {"l_num_orders": "1", "s_num_orders": "5", "l_order_pct": "4", "s_order_pct": "0.02", "l_spacing_sd": "1", "s_spacing_sd": "1.5", "inc": "0.02", "l_multiplier": "2", "s_multiplier": "3", "max_leverage": "4", "tp_pct": "0.016"},
             "credentials": "{}".format(credentials),
             "symbols": [{}],
             "default": "0"}
            settings = add_symbol(json_values)
            return settings, settings_file_name

        def select_bot():
            print([json_files for json_files in os.listdir() if ".json" in json_files])
            settings_file_name = str(input("Which bot do you want to run?: "))
            with open(settings_file_name, 'r') as settings:
                settings = json.load(settings)
            return settings_file_name, settings
        def set_default(settings_file_name):
            for file in os.listdir():
                if ".json" in file:
                    with open(file, 'r') as r:
                        r = json.load(r)
                    if file == settings_file_name:
                        r["default"] = True
                    else:
                        r["default"] = False
                    save(file, r)
            with open(settings_file_name, 'r') as r:
                settings = json.load(r)
                return settings
        print("""
        1 - Add new symbol
        2 - Change parameters for symbol
        3 - Select json file to be default setting
        4 - Create json settings file
        5 - Select bot to run
                """)
        setting = int(input("What would you like to do?: "))

        if setting == 1 or setting == 2 or setting == 3:
            settings_file_name = which_file()
            with open(settings_file_name, 'r') as r:
                settings = json.load(r)
        match setting:
            case 1: settings = add_symbol(settings)
            case 2: settings = symbol_settings(settings)
            case 3: settings = set_default(settings_file_name)
            case 4: settings, settings_file_name = new_json()
            case 5: settings_file_name, settings = select_bot()
        if setting!=5:
            save(settings_file_name, settings)
            print("settings saved")
            other_settings = input("Would you like to select other settings (y,n)?: ").upper()
            if other_settings == "Y":
                file_setting()
        return settings

    def symbol_settings(settings):
        symbols = settings["symbols"][0]
        print("Current symbols: {}".format(list(symbols.keys())))
        symbol = input("Which symbol would you like to change parameters?: ")
        pprint.pprint(
        """Current settings:
        {}""".format(settings["symbols"][0][symbol]))
        print("""
        1 - long number of orders
        2 - short number of orders
        3 - long order % of equity
        4 - short order % of equity
        5 - long order spaces in std dev
        6 - short order spaces in std dev
        7 - increment % to increase order size further from mean (midline)
        8 - long std dev
        9 - short std dev
        10 - max leverage
        11 - take profit %
        """)
        done = ""
        while done != "y":
            settings = f(input("Which setting would you like to update?: "), symbol, settings)
            done = input("Are you done with this symbol? (y,n): ")
        others = input("Would you like to change parameters on other symbols? (y,n): ")
        if others == "y":
            symbol_settings(settings)
        return settings

    def save(settings_file_name, settings):
        with open("{}".format(settings_file_name), "w") as file:
            json.dump(settings, file)
    def f(x, symbol, settings):
        sym_setting = settings["symbols"][0][symbol]
        x = int(x)
        key = list(sym_setting.keys())[x-1]
        def g(x):
            match x:
                # case 0: return [s+'-USD' for s in input("Which symbols? ie (BTC, SOL, ETH): ").split(', ')],
                case 1: return input("How many long orders?: "),
                case 2: return input("How many short orders?: "),
                case 3: return input("What % of equity for each long order? ie (0.02 for 2%): "),
                case 4: return input("What % of equity for each short order? ie (0.02 for 2%): "),
                case 5: return input("Space between long orders in std dev: "),
                case 6: return input("Space between short orders in std dev: "),
                case 7: return input("Order size increment (1.3 for 30% order increase for each space between order): "),
                case 8: return input("Long order standard deviation (distance from midline): "),
                case 9: return input("Short order standard deviation (distance from midline): "),
                case 10: return input("Max Leverage: (Max leverage for position)"),
                case 11: return input("Take profit % (0.01 for 1%): ")
        settings["symbols"][0][symbol][key] = g(x)[0]
        return settings

    default = input("Run default? (y, n): ").upper()
    if default == "Y":
        for file in os.listdir():
            if ".json" in file:
                with open(file, 'r') as r:
                    settings = json.load(r)
                if settings["default"] == True:
                    symbols = settings["symbols"][0]
                    break
        else:
            print("There is no default json file set.")
            print([json_files for json_files in os.listdir() if ".json" in json_files])
            default_file = input("Please select a default json file: ")
            with open(default_file, 'r') as r:
                settings = json.load(r)
                settings["default"] = True
            with open(default_file, 'w') as w:
                json.dump(settings, w)
            symbols = settings["symbols"][0]

    elif default == "N":
        settings = file_setting()
        symbols = settings["symbols"][0]

    for symbol in symbols:
        symbol_params = symbols[symbol]
        tp_pct = float(symbol_params["tp_pct"])
        max_leverage = float(symbol_params["max_leverage"])
        l_num_orders = int(symbol_params["l_num_orders"])
        s_num_orders = int(symbol_params["s_num_orders"])
        l_order_pct = float(symbol_params["l_order_pct"])
        s_order_pct = float(symbol_params["s_order_pct"])
        l_spacing_sd = float(symbol_params["l_spacing_sd"])
        s_spacing_sd = float(symbol_params["s_spacing_sd"])
        inc = float(symbol_params["inc"])
        l_multiplier = float(symbol_params["l_multiplier"])
        s_multiplier = float(symbol_params["s_multiplier"])
        task = """py -c "import trading_algorithm; trading_algorithm.algorithm('{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}).execution()""".format(symbol, max_leverage, l_num_orders, s_num_orders, l_order_pct, s_order_pct, l_spacing_sd, s_spacing_sd, inc, l_multiplier, s_multiplier, tp_pct)
        tasks.append(task)

    for task in tasks:
        p = multiprocessing.Process(target=execute, args=(task, ))
        p.start()
        if tasks.index(task)>0:
            time.sleep(34) # 300/len(symbols))
        else:
            time.sleep(5)
