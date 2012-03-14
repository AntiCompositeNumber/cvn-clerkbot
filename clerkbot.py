import sys, time
from sys import displayhook as logc
from twisted.internet import reactor, task, defer, protocol
from twisted.python import log
from twisted.words.protocols import irc
from twisted.web.client import getPage
from twisted.application import internet, service
HOST, PORT = 'chat.us.freenode.net', 6667
class CVNClerkBot(irc.IRCClient):
	nickname = 'clerkbot'
	password = '***'
	realname = 'clerkbot'
	versionName = 'clerkbot'
	versionNum = '1.0'
	versionEnv = 'python-twisted on Python 2.7'
	lineRate = .5
	def signedOn(self):
        	for channel in self.factory.channels:
			self.join(channel)
	def privmsg(self, user, channel, message):
		nick, sep, user_host = user.partition('!')
		if message.startswith('!'):
			command, sep, rest = message.lstrip('!').partition(' ')
			if command in dir(self):
				function = getattr(self, command)
				r = function(rest, nick, channel)
				if r != None: self.msg(channel, r)
				else: return
		elif message.startswith(self.nickname+':') or message.startswith(self.nickname+',') or message.startswith(self.nickname):
			if message.lower() == self.nickname.lower()+', lol' or message.lower() == self.nickname.lower()+': lol':
				self.msg(channel, 'lol')
			if channel == '#cvn-bots' or channel == '#cvn-staff':
				if message == self.nickname + ' quit':
					self.quit('Disconnecting by order of '+nick)
					reactor.callLater(3, reactor.stop)
				elif self.nickname + ' join' in message:
					parts = message.split(' ')
					if parts[2] not in self.factory.channels: self.factory.channels.append(parts[2])
					self.join(parts[2])
					logc('Joined '+parts[2])
				elif self.nickname + ' part' in message:
					parts = message.split(' ')
					if parts[2] in self.factory.channels: self.factory.channels.remove(parts[2])
					self.leave(parts[2], reason="Ordered by "+nick)
					logc('Parted '+parts[2])
	def staff(self, rest, nick, channel):
		if len(rest) > 0:
			self.msg('#cvn-staff', '%s has requested !staff assistance in %s (Details provided: %s)' % (nick, channel, rest))
		else:
			self.msg('#cvn-staff', '%s has requested !staff assistance in %s' % (nick, channel))
		return 'Thanks %s, staff have been notified of your request and should be around shortly to assist you. In case nobody answers, please ask in #countervandalism if you have not already done so.' % nick
	def globalnotice(self, rest, nick, channel):
		if channel == '#cvn-staff':
			for i in self.factory.channels:
				if i != '#cvn-staff' and i != '#cvn-bots':
					self.notice(i, '\00304[Global notice from %s]:\003 %s' % (nick, rest))
			return 'Global announcement dispatched.'
		else:
			return 'Nice try, %s, but that command can only be used via #cvn-staff ;)' % nick
	def lol(self, rest, nick, channel):
		return 'lol'
class ClerkBotFactory(protocol.ReconnectingClientFactory):
	protocol = CVNClerkBot
	channels = ['#botwar', '##clerkbot']
if __name__ == '__main__':
	reactor.connectTCP(HOST, PORT, ClerkBotFactory())
	log.startLogging(sys.stdout)
	reactor.run()
