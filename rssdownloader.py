#
# Script for watching an rss-feed of torrents and download
# any matches to a special folder.
#
# By Anders Bennehag, 2012
#
# Licensed under GPL
#


import sys
import optparse
import ConfigParser
import feedparser
import re
import string
import urllib

feed = ""
cachedFeed = "example.rss"
searchString = ""
minSize = 100
maxSize = 100
torrentFolder = ""

configfile = ''
dryrun = False
rememberFile = ''
lastItem = None
	

def parseFeed():
	
	d = feedparser.parse(feed)

	print "Number of items in rss-feed is "+str(len(d.entries))
	if len(d.entries)==0:
		sys.exit()
	
	lastItem = rememberLastFeed()
	rememberNewestItem( d.entries[0]['title'] )
	pattern = convertSearchStringToRegExp( searchString )
	

	for item in d.entries:
		if lastItem == item['title']:
			print "Found item from earlier feed"
			break
		
		match = re.search( pattern, item['title'].lower() )
		#print "Comparing\t"+item['title']
		if match is not None:
			print "A match has been found"
			print match.group(0)
			if isPossibleTorrent( item ):
				url = item.links[0].href
				filename = torrentFolder+"/"+url.rpartition("/")[2]
				downloadFile( url, filename )

def rememberLastFeed():
	""" Remember the newest item last time feed was read. """
	try:
		f = open(rememberFile, 'r')
	except IOError:
		return None
	return f.readline()
	
def rememberNewestItem( newestItem ):
	""" Save newest item to disk. """
	if not dryrun:
		f = open(rememberFile, 'w')
		f.write( newestItem )

def convertSearchStringToRegExp( searchString ):
	regExp = string.replace( searchString, " ", ".*?") 
	print "Converted search string to "+regExp
	return re.compile(regExp)
	
def isPossibleTorrent( item ):
	""" Examine an rss-item to see if the torrent should be downloaded. """
	
	# Check size
	torrentSize = int(item.contentlength)/1048576
	if torrentSize > minSize and torrentSize < maxSize:
		print "Match fits size-requirements"
		return True
	else:
		return False

def downloadFile( url, filename ):
	""" Download a file into folder. """
	if not dryrun:
		u = urllib.urlretrieve( url, filename )
	else:
		print "Download "+str(url)+" to "+str(filename)
	
def readConfig( filename ):
	print "Reading config "+filename
	config = ConfigParser.RawConfigParser()
	config.read( filename )
	
	global searchString,feed,minSize,maxSize,torrentFolder
	searchString = config.get("torrent","search-string")
	feed = config.get("torrent","rss")
	minSize = config.getint("torrent","min-size")
	maxSize = config.getint("torrent","max-size")
	torrentFolder = config.get("torrent","folder")
	
if __name__ == '__main__':
	
	parser = optparse.OptionParser()
	parser.add_option("-c","--config", action="store", dest="configfile", help="Use config-file FILE", metavar="FILE")
	parser.add_option("-d","--dry-run", action="store_true", dest="dryrun", help="Do a search without downloading anything")
	
	(options, args) = parser.parse_args()
	
	if len(sys.argv)<2 :
		parser.print_help()
		sys.exit()
	
	dryrun = options.dryrun
	readConfig(options.configfile)
	
	
	print "Searching for "+searchString
	print "in "+feed	
	print "Size between "+str(minSize)+" and "+str(maxSize)+"Mb"
	print ""
	
	if searchString=="" or feed=="":
		parser.print_help()
		sys.exit()
	
	rememberFile = "lastfile_"+searchString.replace(" ","_")+".txt"
	parseFeed()
