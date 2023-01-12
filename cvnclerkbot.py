# cvn-clerkbot
#
# Helperbot for the Countervandalism Network <http://countervandalism.net>.
# For help on installing, check README.md.
#
# @version 3.0.0 (2023-01-10)
# @author Daniel Salciccioli <sactage@sactage.com>, 2012
# @author Timo Tijhof <krinklemail@gmail.com>, 2010-2016
# @license Distributed under the terms of the MIT license.
import sys
import string
import twisted
import threading

from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.words.protocols import irc
import cvnclerkbotconfig as config

if config.useMySQL:  # We only need these imports if we want MySQL
    from FurriesBotSQLdb import FurriesBotSQLdb as sqlclient
    from MySQLdb import MySQLError


class CVNClerkBot(irc.IRCClient):
    gnoticeuser, gnoticemessage = "", ""
    versionName = 'cvn-clerkbot'
    versionNum = '3.0.0'
    versionEnv = "Python Twisted %s Python %s" % (twisted.version.short(), sys.version.split()[0])
    nickname = config.nickname
    password = config.password
    # 'realname' is used by the parent class!
    realname = versionName + " " + versionNum + " - " + versionEnv
    # 'lineRate' is used by the parent class!
    # If we don't have this, we'll excess flood when we join channels/send a !globalnotice
    lineRate = 0.8
    privs = []
    sqldb = None
    channels = []
    # these keys are the channels in which operator commands can be given to clerkbot by users with voice or op
    oplist = {"#countervandalism": [], "#cvn-bots": []}
    voicelist = {"#countervandalism": [], "#cvn-bots": []}

    def signedOn(self):
        if twisted.version.major >= 12:
            self.heartbeatInterval = 30
        self.msg("NickServ", "id " + config.password.partition(":")[2])
        # .partition(":")[2] is the actual password of the bot, assuming you're using account:password format
        self.msg("NickServ", "ghost %s %s" % (config.nickname, config.password.partition(":")[2]))
        self.msg("NickServ", "release %s %s" % (config.nickname, config.password.partition(":")[2]))
        self.setNick(config.nickname)
        for channel in config.channels:
            self.join(channel)
        if config.useMySQL:
            self.sqldb = sqlclient(config.sqldbname, config.sqlpw, config.sqluser, config.sqlhost, port=config.sqlport)
            for channel in self.sqldb.fetch("SELECT ch_name FROM channels", multi=True):
                self.join(channel[0])

    def joined(self, channel):
        self.channels.append(channel)
        # We have to send a WHO message to the server so we can get the current users with +o/+v
        self.sendLine("WHO " + channel)

    def gNotice(self):
        for c in self.channels:
            if c != "#cvn-staff" and c != "#cvn-bots":
                self.notice(c, '\00304[Global notice from %s]:\003 %s' % (self.gnoticeuser, self.gnoticemessage))
        self.msg(
            "#cvn-staff", 'Global notice has been sent to %s channels, %s.' % (len(self.channels) - 2, self.gnoticeuser)
        )

    def privmsg(self, user, channel, message):
        # TODO: Deferreds
        nick, sep, user_host = user.partition('!')
        if message.startswith('!'):
            command, sep, rest = message.lstrip('!').partition(' ')
            if hasattr(self, "command_" + command):
                function = getattr(self, "command_" + command)
                try:
                    r = function(rest, nick, channel, user_host)
                    if r is not None:
                        self.msg(channel, r)
                    return
                except MySQLError as err:
                    self.msg(channel, "MySQL Error: " + str(err))
                except Exception as err:
                    self.msg(channel, str(err.__class__.__name__) + ": " + str(err))
        elif (
            message.startswith(self.nickname + ':')
            or message.startswith(self.nickname + ',')
            or message.startswith(self.nickname)
        ):
            if message.lower() == self.nickname.lower() + ', lol' or message.lower() == self.nickname.lower() + ': lol':
                self.msg(channel, 'lol')

    def command_staff(self, rest, nick, channel, user_host):
        # message sent directly to nickname
        if channel == self.nickname:
            self.msg(nick, "Sorry, you need to use !staff in an actual channel.")
            return
        if len(rest) > 0:
            self.msg(
                '#cvn-staff',
                '%s [%s] has requested !staff assistance in %s (Details provided: %s)'
                % (nick, user_host, channel, rest),
            )
        else:
            self.msg('#cvn-staff', '%s [%s] has requested !staff assistance in %s' % (nick, user_host, channel))
        if channel != '#countervandalism':
            return (
                'Thanks %s, staff have been notified of your request and should be around shortly to assist you. In case nobody answers, please ask in #countervandalism if you have not already done so.'
                % nick
            )
        else:
            return (
                "Thanks %s, staff have been notified of your request and should be around shortly to assist you." % nick
            )

    def command_globalnotice(self, rest, nick, channel, user_host):
        if channel == '#cvn-staff':
            self.gnoticeuser, self.gnoticemessage = nick, rest
            thr = threading.Thread(target=self.gNotice, group=None)
            thr.start()
            return nick + ": Dispatching global notice"
        else:
            self.notice(nick, 'Global notices may only be announced from #cvn-staff')
            return

    def command_lol(self, rest, nick, channel, user_host):
        return "%s [%s] has called for LOL in %s" % (nick, user_host, channel)

    def command_join(self, rest, nick, channel, user_host):
        if channel == "#cvn-staff" or (
            channel in self.oplist.keys() and (nick in self.oplist[channel] or nick in self.voicelist[channel])
        ):
            self.join(rest)
            if config.useMySQL:
                self.sqldb.exe("INSERT INTO channels (ch_name) VALUES('" + rest + "')")

    def command_left(self, channel):
        self.channels.remove(channel)
        if channel in self.oplist.keys():
            self.oplist[channel] = []
            self.voicelist[channel] = []
        if config.useMySQL:
            self.sqldb.exe("DELETE FROM channels WHERE ch_name = '%s'" % channel)

    def command_part(self, rest, nick, channel, user_host):
        if channel == "#cvn-staff" or (
            channel in self.oplist.keys() and (nick in self.oplist[channel] or nick in self.voicelist[channel])
        ):
            # "!part <channel>" or plain "!part" to part the current channel
            channel_name = rest if len(rest) > 0 else channel
            self.part(channel_name, "Requested by " + nick)
            self.channels.remove(channel_name)
            if channel_name in self.oplist.keys():
                self.oplist[channel_name] = []
                self.voicelist[channel_name] = []
            if config.useMySQL:
                self.sqldb.exe("DELETE FROM channels WHERE ch_name = '%s'" % channel_name)

    def command_help(self, rest, nick, channel, user_host):
        return "Ask for help via !staff"

    def command_exit(self, rest, nick, channel, user_host):
        if channel == "#cvn-staff" or (
            channel in self.oplist.keys() and (nick in self.oplist[channel] or nick in self.voicelist[channel])
        ):
            self.quit(message="Ordered by " + nick)
            reactor.callLater(2, reactor.stop)

    def command_quit(self, rest, nick, channel, user_host):
        self.command_exit(rest, nick, channel, user_host)

    # In case the SQL connection ever dies
    def command_sqlconn(self, rest, nick, channel, user_host):
        if channel == "#cvn-staff" or (
            channel in self.oplist.keys() and (nick in self.oplist[channel] or nick in self.voicelist[channel])
        ):
            try:
                self.sqldb = sqlclient(config.sqldbname, config.sqlpw, config.sqluser, config.sqlhost)
                return nick + ": Reconnected to MySQL server."
            except Exception as err:
                return "Error: " + str(err)

    def irc_MODE(self, user, params):
        # This is called upon a MODE message from the server
        if not params[0] in self.oplist.keys():
            # Not a channel we care about
            return
        channel, modes, args = params[0], params[1], params[2:]
        if modes[0] not in '-+':
            modes = '+' + modes
        paramModes = self.getChannelModeParams()
        added, removed = self.parseModes(modes, args, paramModes)
        if added:
            for i in added:
                if i[0] == 'o':
                    self.oplist[channel].append(i[1])
                elif i[0] == 'v':
                    self.voicelist[channel].append(i[1])
        if removed:
            for i in removed:
                if i[0] == 'o':
                    try:
                        self.oplist[channel].remove(i[1])
                    except Exception as err:
                        print(err)
                elif i[0] == 'v':
                    try:
                        self.voicelist[channel].remove(i[1])
                    except Exception as err:
                        print(err)

    def irc_RPL_WHOREPLY(self, prefix, params):
        # This is called upon a WHO reply from the server
        # Check to see if we care about the channel's modes
        if params[1] in self.oplist.keys():
            mode = params[6].strip("H")
            if mode == "@":
                # The server will only show one mode in WHO at a time,
                # if the user is +ov, only @ will show
                self.oplist[params[1]].append(params[5])
            elif mode == "+":
                self.voicelist[params[1]].append(params[5])

    def parseModes(self, modes, params, paramModes=('', '')):
        changes = ([], [])
        direction = None
        count = -1
        for ch in modes:
            if ch in '+-':
                direction = '+-'.index(ch)
                count = 0
            else:
                param = None
                if ch in paramModes[direction]:
                    param = params.pop(0)
                changes[direction].append((ch, param))
                count += 1
        return changes

    def userLeft(self, user, channel):
        if channel in self.oplist.keys():
            nick = user.partition("!")
            if nick in self.oplist[channel]:
                self.oplist[channel].remove(nick)
            if nick in self.voicelist[channel]:
                self.voicelist[channel].remove(nick)

    def userQuit(self, user, message):
        # Checks every channel we keep an oplist for, because QUIT messages aren't per-channel
        for channel in self.oplist.keys():
            if user in self.oplist[channel]:
                self.oplist[channel].remove(user)
            if user in self.voicelist[channel]:
                self.voicelist[channel].remove(user)

    def ctcpQuery_VERSION(self, user, channel, data):
        if self.versionName:
            nick = string.split(user, "!")[0]
            self.ctcpMakeReply(
                nick, [('VERSION', '%s %s %s' % (self.versionName, self.versionNum or '', self.versionEnv or ''))]
            )


class CVNClerkBotFactory(protocol.ReconnectingClientFactory):
    protocol = CVNClerkBot


if __name__ == '__main__':
    reactor.connectTCP(config.HOST, config.PORT, CVNClerkBotFactory())
    log.startLogging(sys.stdout)
    reactor.run()
