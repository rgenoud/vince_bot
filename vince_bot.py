#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2010 Arthur Furlan <afurlan@afurlan.org>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# On Debian systems, you can find the full text of the license in
# /usr/share/common-licenses/GPL-3


from jabberbot import JabberBot, botcmd
from datetime import datetime, timedelta
import random
import time
import re
import sys

class MUCJabberBot(JabberBot):

    ''' Add features in JabberBot to allow it to handle specific
    caractheristics of multiple users chatroom (MUC). '''

    def __init__(self, *args, **kwargs):
        ''' Initialize variables. '''

        # answer only direct messages or not?
        self.only_direct = kwargs.get('only_direct', False)
        try:
            del kwargs['only_direct']
        except KeyError:
            pass

        # initialize jabberbot
        super(MUCJabberBot, self).__init__(*args, **kwargs)

        # create a regex to check if a message is a direct message
        user, domain = str(self.jid).split('@')
        self.direct_message_re = re.compile('^%s(@%s)?[^\w]? ' \
                % (user, domain))

    def callback_message(self, conn, mess):
        ''' Changes the behaviour of the JabberBot in order to allow
        it to answer direct messages. This is used often when it is
        connected in MUCs (multiple users chatroom). '''

        message = mess.getBody()
        if not message:
            return

        bye_str = ["ciao", "tcho", "a+", "à plus dans l'bus", "bye", "salut", "à c'tantot dans l'métro"]
        adem_str = [ 'adem', "à demain dans l'train", "à demain Vince", "bonne soirée Vince" ]
        wuik_str = [ "Bon week-end Vince.", "bon wuik", "à lundi" ]
        hour=int(datetime.now().strftime('%H'))
        day=int(datetime.now().strftime('%u'))
        if hour > 15 and day < 6:
            if re.search("Vince", mess.getFrom().__str__(), re.IGNORECASE) or re.search("bebel", mess.getFrom().__str__(), re.IGNORECASE):
                time.sleep(4*random.random())
                if day < 5:
                    self.send_simple_reply(mess,random.choice(bye_str + adem_str))
                elif day == 5:
                    self.send_simple_reply(mess,random.choice(bye_str + wuik_str))
                return
    
        if self.direct_message_re.match(message):
            mess.setBody(' '.join(message.split(' ', 1)[1:]))
            return super(MUCJabberBot, self).callback_message(conn, mess)
        elif not self.only_direct:
            return super(MUCJabberBot, self).callback_message(conn, mess)


class Example(MUCJabberBot):

    @botcmd
    def date(self, mess, args):
        reply = datetime.now().strftime('%Y-%m-%d')
        self.send_simple_reply(mess, reply)

    @botcmd
    def serverinfo( self, mess, args):
        """Displays information about the server"""
        version = open('/proc/version').read().strip()
        loadavg = open('/proc/loadavg').read().strip()

        return '%s\n\n%s' % ( version, loadavg, )
    
    @botcmd
    def time( self, mess, args):
        """Displays current server time"""
        return str(datetime.now().strftime('%T'))

    @botcmd
    def rot13( self, mess, args):
        """Returns passed arguments rot13'ed"""
        return args.encode('rot13')

    @botcmd
    def whoami(self, mess, args):
        """Tells you your username"""
        return mess.getFrom().__str__()

    @botcmd
    def cpuinfo( self, mess, args):
        """Displays information about the cpu"""
        cpuinfo = open('/proc/cpuinfo').read().strip()
        return '%s' % ( cpuinfo, )
    
    @botcmd
    def uptime( self, mess, args):
        """Displays information about the cpu"""
        uptime = open('/proc/uptime', 'r')
        uptime_seconds = float(uptime.readline().split()[0])
        uptime_string = str(timedelta(seconds = uptime_seconds))

        return '%s' % ( uptime_string, )
    
if __name__ == '__main__':

    backup = 0
    """If we have arguments, switch to backup"""
    if len(sys.argv) > 1:
        backup = 1

    if backup == 1:
        username = 'bot@serverjabber.com'
        password = 'xxxxxxxxxxxxxxxx'
        nickname = 'bob'
        chatroom = 'botroom@conference.serverjabber.com'
        server = 'serverjabber.com'
        port = 5222
    else:
        username = 'bot@myserver'
        password = 'xxxxxxxxxxxxxxx'
        nickname = 'bob'
        chatroom = 'botroom@conference.myserver'
        server = '192.168.1.1'
        port = 5222

    mucbot = Example(username, password, None, False, False, False, None, '', server, port, only_direct=False)
    mucbot.muc_join_room(chatroom, nickname)
    mucbot.serve_forever()
