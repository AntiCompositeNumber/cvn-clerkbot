# Script to log messages to a wikipage from IRC
# For help on installing, check README
#
# @version 2.0.0 (2016-02-18)
# @author Timo Tijhof <krinklemail@gmail.com>, 2010-2016
# @license Distributed under the terms of the MIT license.
import wikipedia
import datetime

# CHANGE THESE SETTINGS TO FIT YOUR OWN
site = wikipedia.getSite('en', 'samplewiki')
rightsname = u"Rights_log"


def rights(message, author):
    targetpage = wikipedia.Page(site, rightsname)
    lines = targetpage.get().split('\n')
    position = 0
    # Try extracting latest date header
    for line in lines:
        position += 1
        if line.startswith("=="):
            undef, date, undef = line.split(" ", 2)
            break

    # Um, check the date
    now = datetime.datetime.utcnow()
    logline = "* %02d:%02d %s: %s" % (now.hour, now.minute, author, message)
    logdate = "%02d-%02d-%02d" % (now.year, now.month, now.day)
    if logdate != date:
        lines.insert(0, "")
        lines.insert(0, logline)
        lines.insert(0, "== %02d-%02d-%02d ==" % (now.year, now.month, now.day))
    else:
        lines.insert(position, logline)
    targetpage.put('\n'.join(lines), "%s (%s)" % (message, author))
