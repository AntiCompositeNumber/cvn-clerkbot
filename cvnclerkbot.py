# CVN-ClerkBot version 1.2.2 (2012-03-16)
#
# Helperbot for the Countervandalism Network <http://countervandalism.net>.
# For help on installing, check README.
# Based on:
# - CVNClerkBOT (by Misza13)
# - wikilogbot.py (by Krinkle)
# 
# (C) Daniel Salciccioli <sactage@sactage.com>, 2012
# (C) Krinkle <krinklemail@gmail.com>, 2010-2012
#
# Distributed under the terms of the MIT license.
import sys, time, datetime, string
import wikilog
import twisted
from twisted.internet import reactor, task, protocol
from twisted.python import log
from twisted.words.protocols import irc
from twisted.application import internet, service
import cvnclerkbotconfig as config
if config.useMySQL: # We only need this import if we're want MySQL
	from FurriesBotSQLdb import FurriesBotSQLdb as sqlclient

class CVNClerkBot(irc.IRCClient):
	currentstatus = 'All OK!'
	msgs_help = "Give right: {{Right given|NickServname|Wikiname|rightstemplate|channel|diffid=000}} | Remove right: {{Right removed|NickServname|Wikiname|rightstemplate|channel|comment=Reason here}} (see !info for useful links)"
	info_help = "Mailing list (*new*): http://bit.ly/cvnLatest / http://bit.ly/cvnMonth | Subscribe: https://lists.wikimedia.org/mailman/listinfo/cvn | Server admin Log: http://bit.ly/clogger | Rights log: http://bit.ly/rightslog | Toolserver: http://toolserver.org/~cvn/"
	statuslastmodtime = '?'
	statuslastmodauthor = '?'
	monthsnames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	versionName = 'CVN-ClerkBot'
	versionNum = '1.2.2'
	versionEnv = "Python Twisted %s; Python %s" % (twisted.version.short(), sys.version.split()[0])
	nickname = config.nickname
	password = config.password
	realname = config.realname + "; " + versionName + " " + versionNum
	lineRate = .5 # If we don't have this, we'll excess flood when we join channels/send a !globalnotice
	privs = []
	sqldb = None
	channels = []
	oplist = {"#countervandalism": [], "#cvn-bots": []}
	voicelist = {"#countervandalism": [], "#cvn-bots": []}

	def signedOn(self):
		self.msg("NickServ", "id " + config.password.partition(":")[2])
		self.msg("NickServ", "ghost %s %s" % (config.nickname, config.password.partition(":")[2])) # .partition(":")[2] is the actual password of the bot, assuming you're using account:password format
		self.msg("NickServ", "release %s %s" % (config.nickname, config.password.partition(":")[2]))
		self.setNick(config.nickname)
		for channel in config.channels:
			self.join(channel)
		if config.useMySQL: # Are we using MySQL?
			self.sqldb = sqlclient(config.schema, config.sqlpw, config.sqlname, config.sqlhost, port=config.sqlport)
##			 for mask in self.sqldb.fetch("SELECT mask FROM priv;", multi=True):
##			 	self.privs.append(mask[0])
			for channel in self.sqldb.fetch("SELECT ch_name FROM channels;", multi=True):
				self.join(channel[0])
#		else: # I guess not D:
#			self.privs = config.masks
#			for i in config.channels:
#				self.join(i)
	def joined(self, channel):
		self.channels.append(channel)
		self.sendLine("WHO " + channel) # We have to send a WHO message to the server so we can get the current users with +o/+v
		
	def privmsg(self, user, channel, message):
		#@TODO Deferreds
		nick, sep, user_host = user.partition('!')
		if message.startswith('!'):
			command, sep, rest = message.lstrip('!').partition(' ')
			if command == 'lol':
				function = getattr(self, "lol")
				r = function(rest, nick, channel, user_host)
				if r != None:
					self.msg(channel, r)
				return
			if command in dir(self) and command != 'join' and command != 'part' and command != 'log': # Because we have functions defined for 'join', 'part', and 'log', we can't getattr(self, command) then
				function = getattr(self, command)
				try:
					r = function(rest, nick, channel, user_host)
					if r != None:
						self.msg(channel, r)
					return
				except Exception, err:
					self.msg(channel, "Error: " + str(err))
			elif command == 'join' or command == 'part' or command == 'log' or command == 'quit':
				cmds = {"join": "j", "part": "p", "log": "wlog", "quit": "exit"}
				function = getattr(self, cmds[command])
				try:
					r = function(rest, nick, channel, user_host)
					if r != None:
						self.msg(channel, r)
					return
				except Exception, err:
					self.msg(channel, "Error: " + str(err))
		elif message.startswith(self.nickname+':') or message.startswith(self.nickname+',') or message.startswith(self.nickname):
			if message.lower() == self.nickname.lower()+', lol' or message.lower() == self.nickname.lower()+': lol':
				self.msg(channel, 'lol')

	def staff(self, rest, nick, channel, user_host):
		if channel == self.nickname: # message sent directly to nickname
			self.msg(nick, "Sorry, you need to use !staff in an actual channel.")
			return
		if len(rest) > 0:
			self.msg('#cvn-staff', '%s has requested !staff assistance in %s (Details provided: %s)' % (nick, channel, rest))
		else:
			self.msg('#cvn-staff', '%s has requested !staff assistance in %s' % (nick, channel))
		if channel != '#countervandalism':
			return 'Thanks %s, staff have been notified of your request and should be around shortly to assist you. In case nobody answers, please ask in #countervandalism if you have not already done so.' % nick
		else: # Saying "Please ask in #countervandalism" makes no sense if they're already there
			return "Thanks %s, staff have been notified of your request and should be around shortly to assist you." % nick

	def globalnotice(self, rest, nick, channel, user_host):
		if channel == '#cvn-staff':
			for i in self.channels:
				if i != '#cvn-staff' and i != '#cvn-bots':
					self.notice(i, '\00304[Global notice from %s]:\003 %s' % (nick, rest))
			return 'Global notice has been sent to %s channels, %s.' % (len(self.channels), nick)
		else:
			self.notice(nick, 'Global notices may only be announced from #cvn-staff'
		return

	def lol(self, rest, nick, channel, user_host):
		return "%s [%s] has called for LOL in %s" % (nick, user_host, channel)

	def wlog(self, rest, nick, channel, user_host):
		if channel == "#cvn-staff" or (nick in self.oplist[channel] or nick in self.voicelist[channel]):
			try:
				wikilog.log(rest, nick)
				return "Logged the message ( http://bit.ly/clogger ), " + nick + "."
			except Exception, err:
				return "I failed :( [%s]" % err

	def rights(self, rest, nick, channel, user_host):
		if channel == "#cvn-staff" or (nick in self.oplist[channel] or nick in self.voicelist[channel]):
			try:
				wikilog.rights(rest, nick)
				return "Rights Log ( http://bit.ly/rightslog ), " + nick + "."
			except Exception, err:
				return "I failed :( [%s]" % err

	def j(self, rest, nick, channel, user_host):
		if channel == "#cvn-staff" or (nick in self.oplist[channel] or nick in self.voicelist[channel]):
			self.join(rest)
			if config.useMySQL:
				self.sqldb.exe("INSERT INTO channels (ch_name) VALUES('" + rest + "');")

	def left(self, channel):
		self.channels.remove(channel)
		if channel in self.oplist.keys():
			self.oplist[channel] = []
			self.voicelist[channel] = []
		if config.useMySQL:
			self.sqldb.exe("DELETE FROM channels WHERE ch_name = '%s';" % channel)

	def p(self, rest, nick, channel, user_host):
		if channel == "#cvn-staff" or (nick in self.oplist[channel] or nick in self.voicelist[channel]):
			if len(rest) > 0:
				self.part(rest, "Requested by " + nick)
			else:
				self.part(channel, "Requested by " + nick)

	def help(self, rest, nick, channel, user_host):
		return self.msgs_help

	def info(self, rest, nick, channel, user_host):
		return self.info_help

	def updatestatus(self, rest, nick, channel, user_host):
		if channel == "#cvn-staff" or (nick in self.oplist[channel] or nick in self.voicelist[channel]):
			try:
				self.currentstatus = rest
				now = datetime.datetime.utcnow()
				self.statuslastmodtime = "%02d:%02d, %d %s %d" % ( now.hour, now.minute, now.day, self.monthsnames[now.month-1], now.year )
				self.statuslastmodauthor = nick
				return "Status updated, " + nick + "."
			except Exception, err:
				return "Error updating status, " + nick + ". [%s]" % err

	def status(self, rest, nick, channel, user_host):
		return "Status: " + self.currentstatus + " (Last modified by " + self.statuslastmodauthor + " at " + self.statuslastmodtime + ")"

	def exit(self, rest, nick, channel, user_host):
		if channel == "#cvn-staff" or (nick in self.oplist[channel] or nick in self.voicelist[channel]):
			self.quit(message = "Ordered by " + nick)
			reactor.callLater(2, reactor.stop)

##	def add(self, rest, nick, channel, user_host):
##		return self.addpriv(rest, nick, channel, user_host)
##
##	def addpriv(self, rest, nick, channel, user_host):
##		if user_host.partition("@")[2] in self.privs:
##			if self.useMySQL:
##				self.sqldb.exe("INSERT INTO priv (mask) VALUES('%s');" % rest)
##			self.privs.append(rest)
##
##	def delpriv(self, rest, nick, channel, user_host):
##		if user_host.partition("@")[2] in self.privs:
##			if self.userMySQL:
##				self.sqldb.exe("DELETE FROM priv WHERE mask = '%s';" % rest)
##			self.privs.remove(rest)
##
##	def priv(self, rest, nick, channel, user_host):
##		if user_host.partition("@")[2] in self.privs:
##			return "Privlist: " + ", ".join(self.privs)

	def sqlconn(self, rest, nick, channel, user_host): # In case the SQL connection ever dies
		if channel == "#cvn-staff" or (nick in self.oplist[channel] or nick in self.voicelist[channel]):
			try:
				self.sqldb = sqlclient(config.schema, config.sqlpw, config.sqlname, config.sqlhost)
				return nick + ": Reconnected to MySQL server."
			except Exception, err:
				return "Error: " + str(err)

	def irc_MODE(self, user, params):
		# This is called upon a MODE message from the server
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
					except Exception, err:
						print err
				elif i[0] == 'v':
					try:
						self.voicelist[channel].remove(i[1])
					except Exception, err:
						print err
						
	def irc_RPL_WHOREPLY(self, prefix, params):
		# This is called upon a WHO reply from the server
		if params[1] in self.oplist.keys(): # Check to see if we care about the channel's modes
			mode = params[6].strip("H")
			if mode == "@": # The server will only show one mode  in WHO at a time - if the user is +ov, only @ will show
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
			if nick in self.oplist[channel]: self.oplist[channel].remove(nick)
			if nick in self.voicelist[channel]: self.voicelist[channel].remove(nick)
	def userQuit(self, user, message):
		for channel in self.oplist.keys(): # Checks every channel we keep an oplist for, because QUIT messages aren't per-channel
			if user in self.oplist[channel]:
				self.oplist[channel].remove(user)
			if user in self.voicelist[channel]:
				self.voicelist[channel].remove(user)
	def ctcpQuery_VERSION(self, user, channel, data):
		if self.versionName:
			nick = string.split(user,"!")[0]
			self.ctcpMakeReply(nick, [('VERSION', '%s %s; %s' %
						(self.versionName,
						self.versionNum or '',
						self.versionEnv or ''))])
class CVNClerkBotFactory(protocol.ReconnectingClientFactory):
	protocol = CVNClerkBot

if __name__ == '__main__':
	reactor.connectTCP(config.HOST, config.PORT, CVNClerkBotFactory())
	log.startLogging(sys.stdout)
	reactor.run()
