# IRC server
HOST = "irc.libera.chat"
PORT = 6667

# IRC user (used to identify with NickServ)
nickname = "cvn-clerkbot"
password = "cvn-clerkbot:*******"

# IRC initial channels to join onconnect
channels = ["#countervandalism", "#cvn-staff", "#cvn-bots"]

#
# MySQL config
#
useMySQL = False

# The below will only be used if useMySQL is True
sqlhost = ""
sqlport = 3306
# This mysql user needs the rights to use SELECT, DELETE, and INSERT statements
sqluser = ""
sqlpw = ""
# Name of the database  (must have a table named "channels")
sqldbname = ""

#
# Example:
#
# useMySQL = True
# sqlhost = "localhost"
# sqlport = 3306
# sqlname = "root"
# sqlpw = "root"
# sqldbname = "cvnclerkbot"
