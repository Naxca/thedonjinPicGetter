#-*- coding: utf-8 -*-
#python 2.x code
#http://thedoujin.com/

import urllib, urllib2
import re, requests
import os, time
import platform

# pretending you are a web browser
headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

def CheckFile(chaptername):
	cnt = 0
	if os.path.exists(chaptername):
		print 'Dir exist!'
		path = os.getcwd()
		path = path + '/' + chaptername
		L = os.listdir(path)
		for i in L:
			print i
			tmp = i [ :3 ]
			if tmp == 'Pic':
				cnt = cnt + 1
		print 'Pics num you got already:'
		print cnt
	return cnt

def GetChapName(url):
	r = requests.get(url)
	data = r.text
	namelist = re.findall(r"(?<=<title>TheDoujin - Read ).+?(?=/)",data)
	if namelist == []:
		return url[-5:]
	else:
		return namelist[0]

def SavePic(url,headers,name):
	req = urllib2.Request(url ,headers = headers)
	# time.sleep(0.1)
	data = urllib2.urlopen(req, timeout=10).read()
	f = open(name,'wb')
	f.write(data)
	f.close()

def GetPicLink(pagelinklist):
	urllist=[]
	for pagelink in pagelinklist:
		urllist.append( GetPicLinkSingle(pagelink) )
	return urllist

def GetPicLinkSingle(pagelink):
	req = urllib2.Request(pagelink ,headers = headers)
	# time.sleep(0.1)
	up = urllib2.urlopen(req, timeout=5).read()
	key1 = '<img src="http'
	key2 = 'id="image"'
	pa = up.find(key1)
	pt = up.find(key2,pa)
	# for test use
	print up[pa+10:pt-2]
	return up[pa+10:pt-2]

def CreatLog(chaptername):
	f = open('log.txt','w')
	f.write('OK')

def IsMultiPage(url):
	r = requests.get(url)
	data = r.text
	# return re.findall(r"(?<=<title>TheDoujin - Read ).+?(?=/)",data)
	itemlist = re.findall(r'(/index.php/categories/[0-9]{5}\?Pages_page=[0-9])', data)
	if itemlist == []:
		print "Single Page"
	else:
		print "Multi Pages"

	return itemlist

def WindowsFix(string):
	pattern = re.compile(r'[\?/\<>*|:]+')
	p = pattern.findall(string)
	if p:
		return pattern.sub(r'_',string)
	else:
		return string

def GetPicMain(pageurl):

	'''First distinguish OS'''
	ostype = platform.platform()
	print ostype

	if ostype.find('Windows') != -1:
		osflag = 'windows'
		print 'System: Windows'
	else:
		osflag = 'Unknown'

	chaptername = GetChapName(pageurl)
	if osflag == 'windows':
		chaptername = chaptername.strip()
		chaptername = WindowsFix(chaptername)
	print 'Chapter Name: ' + chaptername

	itemlist = IsMultiPage(pageurl)
	relist = []
	rerelist = []
	if itemlist != []:
		for item in itemlist:
			if item in relist:
				pass
			else:
				relist.append(item)

		for url in relist:
			rerelist.append('http://thedoujin.com'+url)
		print 'Page link to get:'

		rerelist.insert(0,pageurl)
		for url in rerelist:
			print url
	else:
		rerelist.append(pageurl)

	'''Create Dir'''
	if os.path.exists(chaptername):
		print 'Dir Exist!'
	else:
		os.mkdir(chaptername)
		print 'Create Dir: ' + chaptername

	'''Get pic links in rerelist'''
	pagelinklist = []
	for url in rerelist:
		r = requests.get(url)
		data = r.text
		# searching for links
		link_list = re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,data)
		for url in link_list:
			# make sure utl is link to a picture page
			if ( url.find('page=') >= 0 ) and ( url.find('s=list') == -1 ) and ( url.find('categories') == -1 ):
			    # print url
			    pagelinklist.append('http://thedoujin.com'+url)

	print 'Page Link List:'
	for url in pagelinklist:
		print url

	piclinklist = []
	linkfile = open(chaptername + r'/' + 'PicLink.log','w')
	print 'Start get pic link...'
	piclinklist = GetPicLink( pagelinklist ) # Get all pic links

	totalPicCnt = 0
	for link in piclinklist:
		print link
		totalPicCnt = totalPicCnt + 1
		linkfile.write(link)
		linkfile.write('\n')
	tempstr = 'Total Pic Count: %d' %totalPicCnt
	linkfile.write(tempstr)

	linkfile.close()

	startcnt = 1
	cnt = 1
	print 'Start download'
	
	# while cnt <= totalPicCnt:
	# 	try:
	for url in piclinklist:
		print url
		name = 'Pic%03d' %cnt
		if osflag == 'windows':
			name = chaptername + '\\' + name + url[-4:]
		else:
			name = chaptername + r'/' + name + url[-4:]
		print 'Saving in path: ' + name
		if cnt >= startcnt:
			SavePic(url,headers,name)
		else:
			print 'Pic exist~'
		cnt = cnt + 1
		# except:
		# 	print 'Error when downloading, try again...'

	print '%d pics downloaded' %(cnt-1)


if __name__ == '__main__':

	startpageurl = 'http://thedoujin.com/index.php/categories/16208'
	# 11319 and 11320 11321 include '?' 11695 11705-11708
	# 11710     return re.findall(r"(?<=<title>TheDoujin - Read ).+?(?=/)",data)[0]
	# IndexError: list index out of range
	# can not get title?
	# 12151 dir error 12192
	# 12309?

	'''Caution! Danger! May be Infinite Loop!'''
	for x in xrange(13001,14000):
		pageurl = 'http://thedoujin.com/index.php/categories/%05d' %x
		print pageurl
		while True:
			try:
				GetPicMain(pageurl)
				break
			except Exception, e:
				print str(e)
				print 'Try again...'
			else:
				pass
			finally:
				pass
		