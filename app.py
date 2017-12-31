#!/usr/bin/env python
# -*- coding: utf-8 -*-

import irc.bot
import irc.strings
from appJar import gui
import json
from time import gmtime, strftime

'''
Loads username and token from user.json
'''
try:
    with open("user.json") as u:
        user = json.load(u)
except FileNotFoundError:
    print('user.json is missing!')
    raise
    sys.exit()

'''
Load channels to join from channels.json
'''
try:
    with open("channels.json") as u:
        channels = json.load(u)
except FileNotFoundError:
    print('channels.json is missing!')
    raise
    sys.exit()

'''
Create GUI with title, resolution and background color
'''
app = gui("Ripple IRC Client", "800x400")
app.setBg("#454545")
app.setLocation("LEFT")

'''
Sends private message and adds it to list
'''


def send_private_message(button):
    msg = str(app.getEntry(button))
    if bool(msg.strip()):
        msg2 = "[{}] {}: {}".format(strftime("%H:%M", gmtime()), user["username"], msg)
        app.addListItem(button, msg2)
        irc.connection.privmsg(button, msg)
    else:
        msg2 = "Empty messages are not allowed!"
        app.addListItem(button, msg2)


'''
Get message from irc and put it in list
'''


def send_private(nick, msg):
    app.addListItem(nick, msg)


'''
Sends message to public channel
'''


def send_message(button):
    channel = button
    btn = "Message_" + channel
    msg = app.getEntry(btn)
    if bool(msg.strip()):
        msg2 = "[{}] {}: {}".format(strftime("%H:%M", gmtime()), user["username"], msg)
        app.addListItem(channel, msg2)
        irc.connection.privmsg(channel, msg)
    else:
        msg2 = "Empty messages are not allowed!"
        app.addListItem(channel, msg2)


'''
Create GUI for private chat
'''


def create_private(nick, msg):
    app.startSubWindow(nick, title=nick, modal=False)
    app.addListBox(nick, ["Private with " + nick], 0, 1, 10, 0)
    app.addLabelEntry(nick, 2, 0)
    app.addListItem(nick, msg)
    app.addNamedButton("Send", nick, send_private_message, 2, 1)
    app.stopSubWindow()


'''
IRC connection to Ripple server
'''


class RippleBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        irc.bot.SingleServerIRCBot.__init__(self, [("irc.ripple.moe", 6667, user["token"])],
                                            user["username"], user["username"])

    '''
    On welcome creates GUI with tabs
    '''

    def on_welcome(self, c, e):
        app.startTabbedFrame("IRC")
        app.setTabbedFrameTabExpand("IRC", expand=True)
        app.setFont(12)
        app.setStretch("both")
        for channel in channels:
            app.startTab(channel)
            app.setBg("#454545")
            app.addListBox(channel, ["Welcome to " + channel], 0, 0, 3)
            app.addLabelEntry("Message_" + channel, 2, 0)
            app.addNamedButton("Send", channel, send_message, 2, 1)
            app.stopTab()
            c.join(channel)
        app.stopTabbedFrame()

    '''
    Public messages
    '''

    def on_pubmsg(self, c, e):
        cmd = e.arguments[0]
        nick = e.source.nick
        msg = "{} {}: {}".format(strftime("%H:%M", gmtime()), nick, cmd)

        app.addListItem(e.target, msg)

    '''
    Private messages
    '''

    def on_privmsg(self, c, e):
        nick = e.source.nick
        cmd = e.arguments[0]
        msg = "{} {}: {}".format(strftime("%H:%M", gmtime()), nick, cmd)
        try:
            create_private(nick, msg)
        except:
            send_private(nick, msg)

        app.showSubWindow(nick)


irc = RippleBot()

'''
Login GUI
'''


def gui_login(button):
    username = app.getEntry("Name")
    token = app.getEntry("Token")

    if username and token:

        print("User:", username, "Token:", token)

        data = {"username": username, "token": token}

        with open('user.json', 'w') as outfile:
            json.dump(data, outfile)

        app.destroySubWindow("GUILogin")

    else:
        print("Input is empty")

'''
Create GUI for login
'''
app.startSubWindow("GUILogin", title="Login", modal=True)
app.addLabelEntry("Name")
app.addLabelSecretEntry("Token")
app.setFocus("Name")
app.addButtons(["Login"], gui_login)
app.stopSubWindow()

'''
Check if username and token are not empty
'''
if not user["username"] or not user["token"]:
    app.showSubWindow("GUILogin")
    app.thread(irc.start)
else:
    app.thread(irc.start)

'''
Starts application
'''
app.go()
