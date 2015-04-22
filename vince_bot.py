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
        self.nickname = kwargs.get('nickname', 'bob')
        self.rnd_max = kwargs.get('rnd_max', 25)
        try:
            del kwargs['only_direct']
            del kwargs['nickname']
            del kwargs['rnd_max']
        except KeyError:
            pass

        # initialize jabberbot
        super(MUCJabberBot, self).__init__(*args, **kwargs)

        # create a regex to check if a message is a direct message
        user, domain = str(self.jid).split('@')
        self.direct_message_re = re.compile('^%s(@%s)?[^\w]? ' \
                % (user, domain))

        random.seed()
        self.msg_count = 0
        self.go_mode = False
        self.random = random.randint(1, self.rnd_max)
        self.ok_str = ["c'est pas faux", "ok", "c'est pas con", "j'suis pour", "moi aussi !", "kler.", "grav'", "+1", "je bois les mots à tes lèvres tel cendrillon la sève au gland du prince charmant" ]
        self.nok_str = ["j'peux pas te laisser dire ça", "FOUTAISES !", "mais c'est n'importe quoi !!!", "tu dis que d'la merde toi !", "sans moi", "weekly...", "peux pas, j'ai poney"]
        self.insult_str = ["oh putain mais ta gueule !", "salope, salope, salope !", "ducon !", "et dans l'cul la balayette !", "t'es vraiment trop con toi !", "RTFM !"]
	self.other_str = [ "pause !", "choub:!!!!", "mais qu'est-ce qu'on fout là ?", "j'suis putain de las !", "on va au resto ?", "sérieux ?", "la loose...", "rheuuuuuuuuuuuu", "et ben on est pas rendu avec ça !"]
        self.direct_str = [ "ben chais pas", "parles-moi pas toi !", "kestuveux ?!", "vas-y lâche-moi !", "putain, j'dormais...", "pffff ! mais qu'est-ce j'en sais moi ?!" ]
        self.choub_str = ["choub: !!!!!!!", "choub: !$%#+@", "choub: bordel !" ]
        self.procedures_str = ["putain, mais on chie sur les procedures là !!!", "pffffff !!!", "ok, mais on timeout à 30 alors !!!" ]
        self.all_str = self.ok_str + self.nok_str + self.insult_str + self.other_str

    def callback_message(self, conn, mess):
        ''' Changes the behaviour of the JabberBot in order to allow
        it to answer direct messages. This is used often when it is
        connected in MUCs (multiple users chatroom). '''

        message = mess.getBody()
        if not message:
            return

        if not re.search("/%s$" % self.nickname, mess.getFrom().__str__(), re.IGNORECASE):
            # this is not a message from myself

            if re.search("^go$", message, re.IGNORECASE) and not self.go_mode:
                time.sleep(3*random.random())
                self.send_simple_reply(mess, "go")
                self.go_mode = True
                return

            self.go_mode = False

            if re.search("^choub: [!@#%]", message, re.IGNORECASE):
                # call choub !
                time.sleep(2*random.random())
                self.send_simple_reply(mess, random.choice(self.choub_str));
                return

            if re.search("^2s$", message, re.IGNORECASE):
                time.sleep(2*random.random())
                self.send_simple_reply(mess, random.choice(self.procedures_str));
                return

            if re.search("^%s:? " % self.nickname, message, re.IGNORECASE):
                # someone talks to me...
                time.sleep(3*random.random())
                self.send_simple_reply(mess, random.choice(self.direct_str));
                return

            self.msg_count += 1
            if self.msg_count >= self.random:
                self.msg_count = 0
                self.random = random.randint(1, self.rnd_max)
                time.sleep(3*random.random())
                self.send_simple_reply(mess,random.choice(self.all_str))
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

    mucbot = Example(username, password, None, False, False, False, None, '', server, port, only_direct=False, nickname=nickname, rnd_max=25)
    mucbot.muc_join_room(chatroom, nickname)
    mucbot.serve_forever()
