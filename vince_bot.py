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
import subprocess
import threading
import codecs

class MUCJabberBot(JabberBot):

    ''' Add features in JabberBot to allow it to handle specific
    caractheristics of multiple users chatroom (MUC). '''

    def __init__(self, *args, **kwargs):
        ''' Initialize variables. '''

        # answer only direct messages or not?
        self.only_direct = kwargs.get('only_direct', False)
        self.nickname = kwargs.get('nickname', 'bob')
        self.chatroom = kwargs.get('chatroom', None)
        self.rnd_max = kwargs.get('rnd_max', 25)
        try:
            del kwargs['only_direct']
            del kwargs['nickname']
            del kwargs['chatroom']
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
        self.started_at = time.time()
        self.t = threading.Timer(random.randint(15,60) * 60.0, self.say_smthg)
        self.t.daemon = True
        self.t.start()
        self.msg_count = 0
        self.go_mode = False
        self.yo_mode = False
        self.random = random.randint(1, self.rnd_max)
        self.ok_str = [ \
                "c'est pas faux", \
                "ok", \
                "c'est pas con", \
                "j'suis pour", \
                "moi aussi !", \
                "kler.", \
                "grav'", \
                "sérieux ?", \
                "+1" ]
        self.nok_str = [ \
                "j'peux pas te laisser dire ça", \
                "FOUTAISES !", \
                "mais c'est n'importe quoi !!!", \
                "tu dis que d'la merde toi !", \
                "sans moi", \
                "weekly...", \
                "la loose...", \
                "et ben on est pas rendu avec ça !", \
                "peux pas, j'ai poney"]
        self.insult_str = [ \
                "oh putain mais ta gueule !", \
                "salope, salope, salope !", \
                "ducon !", \
                "et dans l'cul la balayette !", \
                "t'es vraiment trop con toi !", \
                "RTFM !" ]
        self.other_str = [ \
                "pause !", \
                "mais qu'est-ce qu'on fout là ?", \
                "j'suis putain de las !", \
                "/me se fait chier", \
                "/me est las", \
                "on va au resto ?", \
                "rheuuuuuuuuuuuu", \
                "j'me fais chier grave", \
                "c'est calme ici...", \
                "...", \
                "pffffffff", \
                "quelqu'un a LA réponse ?", \
                "pfffff ! j'ai pas l'goût !" ]
        self.direct_str = [ \
                "ben chais pas", \
                "parles-moi pas toi !", \
                "kestuveux ?!", \
                "vas-y lâche-moi !", \
                "putain, j'dormais...", \
                "pffff ! mais qu'est-ce j'en sais moi ?!", \
                "honnêtement, je m'en bats les couilles.", \
                "qu'est-ce que tu veux que ça me fasse ?", \
                "t'sais quoi ? ça m'en touche une sans faire bouger l'autre !", \
                "Parle à ma main !", \
                "qui me parle ?", \
                "toi-même !", \
                "cébon! ça va, j'ai compris.", \
                "roger.", \
                "lapin cômpri", \
                "cestcuiquiditquiyest !", \
                "miroir incassable !", \
                "Wouhaa ! mais c'est génial !", \
                "Putain, c'est trop d'la balle", \
                "c'est quoi la question ?", \
                "je bois les mots à tes lèvres tel cendrillon la sève au gland du prince charmant", \
                "<Abraham Simpson>Faut que j'aille prendre mes médicaments</Abraham Simpson>", \
                "Je ne pine rien à ce que tu me baves" ]
        self.choub_str = [ \
                "choub: !!!!!!!", \
                "choub: !$%#+@", \
                "choub: bordel !" ]
        self.procedures_str = [ \
                "putain, mais on chie sur les procedures là !!!", \
                "pffffff !!!", \
                "franchement, c'est abusé !", \
                "ok, mais on timeout à 30 alors !!!", \
                "Nan, c'est maintenant ! benoît: go" ]
        self.yo_str = [ \
                "yo", \
                "salut", \
                "plop", \
                "salut salut", \
                "bonjour", \
                "bonjour bonjour", ]
        self.all_str = self.ok_str + self.nok_str + self.insult_str

    def callback_message(self, conn, mess):
        ''' Changes the behaviour of the JabberBot in order to allow
        it to answer direct messages. This is used often when it is
        connected in MUCs (multiple users chatroom). '''

        # discards the server backlog
        if (time.time() - self.started_at) < 4:
            return

        self.last_message = mess
        message = mess.getBody()
        if not message:
            return

        self.t.cancel()
        self.timer_val = random.randint(20,60) * 60.0
        self.t = threading.Timer(self.timer_val, self.say_smthg)
        self.t.daemon = True
        self.t.start()
        print time.ctime()
        print "next in %d sec" % self.timer_val

        if not re.search("/%s$" % self.nickname, mess.getFrom().__str__(), re.IGNORECASE):
            # this is not a message from myself

            if message == "go":
                if not self.go_mode:
                    time.sleep(3*random.random())
                    self.send_simple_reply(mess, "go")
                self.go_mode = True
                self.yo_mode = False
                return

            self.go_mode = False

            if message.lower() in self.yo_str:
                if not self.yo_mode:
                    time.sleep(3*random.random())
                    self.send_simple_reply(mess, random.choice(self.yo_str))
                self.yo_mode = True
                return

            self.yo_mode = False

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

    def say_smthg(self):
        # can send directly to a chatroom instead:
        # http://stackoverflow.com/questions/3528373/how-to-create-muc-and-send-messages-to-existing-muc-using-python-and-xmpp
        if self.chatroom != None:
            mucbot.muc_join_room(self.chatroom, self.nickname)
        self.send_simple_reply(self.last_message,random.choice(self.other_str))

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

    @botcmd
    def blague(self, mess, args):
        """Tells a joke in french"""
        result = subprocess.check_output("$HOME/bin/blague.sh",shell=True)
        return '%s' % (result, )

def convert_handler(err):
    end = err.end
    return (u' ', end)

def get_out():
    print "bye bye"
    quit()

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

    codecs.register_error('strict', convert_handler)

    mucbot = Example(username, password, None, False, False, False, None, '', server, port, only_direct=False, nickname=nickname, chatroom=chatroom, rnd_max=25)
    mucbot.muc_join_room(chatroom, nickname)
    mucbot.serve_forever(disconnect_callback=get_out)
