# Configuration for clerkbot


# Required

## IRC nick name, also used to identify with NickServ
nickname = "CVN-ClerkBot"
## NickServ password
password = ""
## IRC real name (appended to this is "; CVN-ClerkBot {version}")
realname = "Helper bot for the CVN"
# IRC server hostname
HOST = "irc.freenode.net"
# IRC server connecting port
PORT = 6667


# Static

## Initial list of channels to join onconnect
channels = ["#cvn-sandbox"]


# MySQL config

useMySQL = False

## The below will only be used if useMySQL is True

## MySQL server to connect to
sqlhost = ""
## Port to connect to
sqlport = 3306
## MySQL server username
## This mysql user needs the rights to use SELECT, DELETE, and INSERT statements
sqlname = ""
## Password for the above username
sqlpw = ""
## Name of the database to use
## The database must have at least one table, "channels"
schema = ""
