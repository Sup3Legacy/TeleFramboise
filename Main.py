import hashlib
import sys
import time
import telepot
import wikipedia
import psutil
import os

TOKEN = ""
CHANNEL = 9999999999
bot = telepot.Bot(TOKEN)
admin_id = [] #listes des chat_id avec mode admin activé
admin_authorized = {}

commands = {} #Dico de correspondance commande/fonction
categories = {}
admins = {}

def commandHandler(nom, category = "Default", admin = False):
    def handlerBis(fonction):
        commands[nom] = fonction
        if category not in categories.keys():
            categories[category] = [nom]
        else:
            categories[category].append(nom)
        admins[nom] = admin
    return handlerBis

def parse(string):
    return string.split()

@commandHandler("/shutdown", category = "Admin", admin = True)
def shutdown(msg, args):
    """/shutdown : shuts down the Framboise via shell command"""
    command = "sudo shutdown now" #Changer pour pouvoir choisir l'échéance
    os.system(command)
    return

@commandHandler("/reboot", category = "Admin", admin = True)
def reboot(msg, args):
    """/reboot : reboots the Framboise via shell command"""
    command = "sudo reboot now" #Changer pour pouvoir choisir l'échéance
    os.system(command)
    return

@commandHandler("/relaunch", category = "Admin", admin = True)
def relaunch(msg, args):
    """/relaunch : relaunches the Telepot script."""
    #os.execv(__file__, sys.argv)
    return

@commandHandler("/stats", category = "Monitoring", admin = False)
def stats(msg, args):
    """/stats : shows CPU/mem stats of the Framboise."""
    cpu_util = psutil.cpu_percent()
    cpu_temp = psutil.sensors_temperatures()['cpu-thermal'][0].current
    memory = psutil.virtual_memory()
    memory_percent = round(100 * (1 - memory.available / memory.total), 1)
    res = "*Memory usage :* " + str(memory_percent) + "% \n"
    res += "*CPU usage :* " + str(cpu_util) + "% \n"
    res += "*CPU temperature :* " + str(cpu_temp) + "°C \n"
    bot.sendMessage(msg['chat']['id'], res, parse_mode = "Markdown")
    return

@commandHandler("/ping")
def ping(msg, args):
    """/ping: replies "pong"."""
    bot.sendMessage(msg['chat']['id'], "pong")
    return

@commandHandler("/chat")
def miaou(msg, args):
    """/chat : replies "miaou"."""
    bot.sendMessage(msg['chat']['id'], "Miaou")
    return

@commandHandler("/help")
def helpCommand(msg, args):
    """/help : shows all command docstrings."""
    chat_id = msg['chat']['id']
    res = ''
    for key in categories.keys():
        res += "*" + str(key) + "*\n"
        liste = categories[key]
        for nom in liste:
            res += commands[nom].__doc__ + "\n"
        res += "\n"
    bot.sendMessage(msg['chat']['id'], res, parse_mode = "Markdown")
    return

@commandHandler("/echo")
def echo(msg, args):
    """/echo message : echoes message."""
    bot.sendMessage(msg['chat']['id'], msg['text'][6:])
    return

@commandHandler("/adminmode", category = "Admin", admin = False)
def adminMode(msg, args):
    """/adminmode password : enters or leaves admin mode."""
    chat_id = msg['chat']['id']
    if len(args) == 0:
        bot.sendMessage(chat_id, "No password entered.")
        return
    password = args[0]
    if chat_id in admin_authorized.keys():
        print(password)
        print(hashlib.sha512(password.encode()).hexdigest())
        if hashlib.sha512(password.encode()).hexdigest() == admin_authorized[chat_id]:
            if chat_id in admin_id:
                admin_id.remove(chat_id)
                print("Admin " + str(chat_id) + " logged out.")
                bot.sendMessage(chat_id, "Admin mode off.")
            else:
                admin_id.append(chat_id)
                print("Admin " + str(chat_id) + " logged in.")
                bot.sendMessage(chat_id, "Admin mode on.")
        else:
            print("Wrong password entered by " + str(chat_id))
            bot.sendMessage(chat_id, "Wrong password entered.")
    else:
        print("Unknown chat_id entered by " + str(chat_id))
        bot.sendMessage(chat_id, "Wrong user. Not allowed to enter admin mode.")
    bot.deleteMessage(telepot.message_identifier(msg))
    return


@commandHandler("/wikisum")
def wikiSum(msg, args):
    """/wikisum -lang mots-clé : renvoie, si lieu, un résumé de wikipedia."""

    if args[0][0] == '-': #ie. choix de langue
        results = wikipedia.search(' '.join(args[1:]))
        try:
            wikipedia.set_lang(args[0][1:].lower())
        except:
            results = wikipedia.search(' '.join(args.lower()))
            bot.sendMessage(msg['chat']['id'], "Language " + args[0][1:] + " not found.")
    else:
        results = wikipedia.search(' '.join(args))
    if len(results) == 0:
        bot.sendMessage(msg['chat']['id'], "Pas de résultat trouvé")
    else:
        res = "*Wikipedia : " + results[0] + "*\n" + wikipedia.summary(results[0]) + "\n" + wikipedia.page(results[0]).url
        bot.sendMessage(msg['chat']['id'], res, parse_mode = "Markdown")
        print("Sent wiki summary")
    return

def handle(msg):
    chat_id = msg['chat']['id']

    if chat_id != CHANNEL:
        print("Unauthorized connection.")
        print(chat_id)
        bot.sendMessage(chat_id, "Hi! I'm a private bot, so there's no point to contact me :)")
        return #Ajouter un log des connexions frauduleuses

    command = parse(msg['text'])
    command[0].lower()

    print('Got message: %s' % command)

    print(chat_id)
    if command[0] in commands.keys():
        if (chat_id in admin_id) or (not admins[command[0]]):
            try:
                commands[command[0]](msg, command[1:])
            except:
                bot.sendMessage(chat_id, "Error in command "  + command[0])
                bot.sendMessage(chat_id, "Command docstring : " + commands[command[0]].__doc__)
        else:
            print("Admin command. Acces denied.")
            bot.sendMessage(chat_id, "This is an admin command. Acces denied.")


bot.message_loop(handle)
print('Listening.')

while 1:
    try:
        time.sleep(600)
        admin_id = []

    except KeyboardInterrupt:
        print('\n Program interrupted')
        exit()

    except:
        print('Other error or exception occured!')
