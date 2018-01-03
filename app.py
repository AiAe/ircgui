#!/usr/bin/env python
# -*- coding: utf-8 -*-

import irc.bot
import irc.strings
from appJar import gui
import json
from time import gmtime, strftime
import sys

'''
Loads username and token from user.json
'''
try:
    with open("user.json") as u:
        user = json.load(u)
except FileNotFoundError:
    print('user.json is missing!')
    sys.exit()

'''
Load channels to join from channels.json
'''
try:
    with open("channels.json") as u:
        channels = json.load(u)
except FileNotFoundError:
    print('channels.json is missing!')
    sys.exit()

'''
Create GUI with title, resolution and background color
'''
app = gui("Ripple IRC Client", "800x400")
app.setBg("#454545")
app.setLocation("LEFT")
app.setIcon("favicon.ico")

'''
Create tabs for channels and private messages
'''


def create_tab(target, msg=None):
    app.startTab(target)
    app.setBg("#454545")
    app.addListBox(target, [msg], 0, 0, 3)
    app.addLabelEntry(target, 2, 0)
    app.addNamedButton("Send", target, send_message, 2, 1)
    # app.addNamedButton("Close", "close" + target, close_message, 2, 2)
    app.stopTab()


'''
Clear user inputs
'''


def clear_entity(target):
    app.clearEntry(target)


'''
Sends private message and adds it to list
'''


def send_private_message(button):
    msg = str(app.getEntry(button))
    if bool(msg.strip()):
        msg2 = "{} {}: {}".format(strftime("%H:%M", gmtime()), user["username"], msg)
        app.addListItem(button, msg2)
        clear_entity(button)
        irc.connection.privmsg(button, msg)


'''
Get message from irc and put it in list
'''


def pull_private(nick, msg):
    app.addListItem(nick, msg)


'''
Sends message to public channel
'''


def send_message(button):
    msg = app.getEntry(button)
    if bool(msg.strip()):
        msg2 = "{} {}: {}".format(strftime("%H:%M", gmtime()), user["username"], msg)
        app.addListItem(button, msg2)
        clear_entity(button)
        irc.connection.privmsg(button, msg)


'''
Sends command to close channel/chat
'''

# def close_message(button):
#     deletetab("IRC", button.split("close")[1])


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
            create_tab(channel, "Joined " + channel)
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
            app.openTabbedFrame("IRC")
            create_tab(nick, msg)
            app.stopTabbedFrame()
        except:
            pull_private(nick, msg)


irc = RippleBot()

'''
Check if username and token are not empty
'''

if not user["username"] and not user["token"]:

    '''
    Login GUI
    '''


    def gui_login(button):
        username = app.getEntry("Name")
        token = app.getEntry("Token")

        if username and token:
            data = {"username": username, "token": token}

            with open('user.json', 'w') as outfile:
                json.dump(data, outfile)

            sys.exit()


    '''
    Create GUI for login
    '''
    app.startSubWindow("GUILogin", title="Login", modal=True)
    app.addLabelEntry("Name")
    app.addLabelSecretEntry("Token")
    app.setFocus("Name")
    app.addButtons(["Login"], gui_login)
    app.stopSubWindow()

    app.showSubWindow("GUILogin")
else:
    app.thread(irc.start)

'''
Starts application
'''
app.go()
