# -*- coding: utf-8 -*-

import re
import os
import urllib
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TCON, TRCK, APIC, USLT
import pandas as pd
import shutil
import webbrowser

def getFileName(path):
	fileList=os.listdir(path)
	return [archName for archName in fileList if '.mp3' in archName]
	
def cleanFileName(fname):
	'''Remove bad signs and words from file name'''
	fname=fname.encode('utf-8')#Big encode problem
	fname=fname[:-3]#removes.mp3
	badSign="'?.%&!|<>-/,\\+*:"+'"' 
	badWords=[' sub. ', 'subtitulado','subtitulada', 'lyrics', ' video','hd','official', 'vevo','amv', 'con letra', 'download', 'wlyrics']
	fname=''.join([i if i not in badSign else ' ' for i in fname]) #Remove bad signs
	fname=re.sub(r'\([^()]*\)', '', fname) #Remove words within parenthesess
	fname=' '.join(filter(lambda x: x.lower() not in badWords, fname.split())) #Remove bad words
	fname='+'.join(fname.split())
	return fname.strip()

def getTable(page):
	'''Returns info whitin results table MusicBrainz'''
	return [page.find('<tbody>'),page.find('</tbody>')]
		
def getPage(song,t):
	'''get the results page for a song File Name in MusicBrainz'''
	page=urllib.urlopen('https://musicbrainz.org/search?query='+song+'&type=recording&method=indexed').read()
	print 'try '+str(t)
	if page.find('Search Error - MusicBrainz')> -1 : 
		t+=1
		return getPage(song,t)
	return page[getTable(page)[0]:getTable(page)[1]] #Finds results table from musicbrainz
	
def getResults(page,initResult):
	i=0
	f=0
	rotules=['Name','Band','Album','Track','Cover','UrlAlbum','UrlSong']
	results=pd.DataFrame()
	while i <initResult:
		data=list(getData(page,f))
		f=data[-1]
		results=results.append(pd.DataFrame([data[:-1]],columns=rotules),ignore_index=True)
		i+=1
	return results.to_dict()

def cleanBasic(fname):
	return ''.join([i for i in fname if i not in '/\:*?"<>|'])
	
def getInfo(page,base,tag):
	'''get string between html tags'''
	i=page.find(tag,base)+len(tag)#si page.find=-1 khe
	if tag=='<a href="':
		f=page.find('">',i)
	elif tag=='<div id="all-tags">':
		f=page.find('</div>',i)
		page=page[i:f]
		return page,len(page)
	else:
		f=page.find(tag[:1]+'/'+tag[1:],i)
	return page[i:f],f
	
def getData(page,init):
	'''Calls getInfo and return the tags results'''
	base=page.find('<a href="/recording/',init)+len('<a href="')
	
	urlSong=page[base:page.find('"',base)]
	name,f=getInfo(page,base,'<bdi>')
	k=f
	band,f=getInfo(page,f,'<bdi>')
	if page.find('<span class="comment">',k)<f and page.find('<span class="comment">',k)>0:
		band,f=getInfo(page,f,'<bdi>')
	urlAlbum,f=getInfo(page,f,'<a href="')
	while 'isrc' in urlAlbum: 
		urlAlbum,f=getInfo(page,f,'<a href="')
	album,f=getInfo(page,f,'<bdi>')
	track,f=getInfo(page,f,'<td>')
	if getThumb(urlAlbum)[0]: 
		cover='Available'
		urlAlbum=getThumb(urlAlbum)[1]
	else: 
		cover= 'No Available'
		urlAlbum='/static/images/keep-calm-i-m-not-available.png'
	
	return name.decode('utf-8').replace('&amp;','&'), band.decode('utf-8').replace('&amp;','&'), album.decode('utf-8').replace('&amp;','&'), track.decode('utf-8').replace('&amp;','&'),cover.decode('utf-8').replace('&amp;','&'), urlAlbum,urlSong,f

def downloadThumb(urlAlbum,name,path):
	os.chdir(path)
	newName=cleanBasic(name)	
	if '.jpg' in urlAlbum:
		urllib.urlretrieve(urlAlbum,newName+'.jpg')
		return newName+'.jpg'
	else: 
		urllib.urlretrieve(urlAlbum,newName+'.png')
		return newName+'.png'
	
def getThumb(urlAlbum):
	'''search and download Thumbnail'''
	pg=urllib.urlopen('https://musicbrainz.org'+urlAlbum).read()
	if pg.find('<div class="cover-art">')!=-1:
		i=pg.find('<div class="cover-art">')+len('<div class="cover-art">')
		i=pg.find('//',i)+len('//')
		f=pg.find('"',i)
		if '.jpg' in pg[i:f]:
			return True,'https://'+pg[i:f]
		if '.png' in pg[i:f]:
			return True,'https://'+pg[i:f]
	return False,'',''
	
def getGenre(urlSong):
	'''search and get genre'''
	pg=urllib.urlopen('https://musicbrainz.org'+urlSong+'/tags').read()
	pg,f=getInfo(pg,0,'<div id="all-tags">')
	genre=''
	i=0
	while pg.find('<bdi>',i)!=-1:
		aux,i=getInfo(pg,i,'<bdi>')
		genre+=aux+'-'
	if not genre:
		genre='NG-'
	return genre[:-1]
	
def attachTags(fname,info,genre,lyrics,tCover,path):
	os.chdir(path)
	
	'''Attach Metadata to file'''
	try: 
		tags = ID3(fname,v2_version=3)
	except ID3NoHeaderError:
		print "Adding ID3 header;",
		tags = ID3()
	
	tags["TIT2"] = TIT2(encoding=3, text=info['Name'])
	tags["TALB"] = TALB(encoding=3, text=info['Album'])
	tags["TPE1"] = TPE1(encoding=3, text=info['Band'])
	tags["TCON"] = TCON(encoding=3, text=genre)
	tags["TRCK"] = TRCK(encoding=3, text=info['Track'])
	newName=cleanBasic(info['Name'])
	if lyrics:
		lyrics=lyrics.decode('utf-8')
		tags["USLT"] = USLT(encoding=3, desc=u'desc', text=lyrics)
		text_file = open(newName+".txt", "w")
		lyrics=lyrics.encode('cp1252')
		text_file.write(lyrics)

	imag=''
	if '.jpg' in tCover:
		imag='image/jpeg'
	if '.png' in tCover:
		imag='image/png'
	try:
		tags["APIC"] = APIC(encoding=3, mime=imag, type=3, desc=u'Cover',data=open(tCover,'rb').read())
	except: 
		pass
	
	tags.save(fname,v2_version=3,v1=2)
	if tCover!='': os.remove(tCover)
	newName=cleanBasic(info['Name'])+'.mp3'
	os.rename(fname,newName)
	return newName

def getLyrics(artist,song):
	artist=cleanBasic(artist)
	song=cleanBasic(song)
	if u'\xf3' in song:
		song=song.replace(u'\xf3',u'o')
	if u'\xc1' in song:
		song=song.replace(u'\xc1',u'a')
	if u'\u2019' in song:
		song=song.replace(u'\u2019',u'')
	page=urllib.urlopen('https://www.musixmatch.com/search/'+artist+' '+song).read()
	webbrowser.open('https://www.musixmatch.com/search/'+artist+' '+song)
	i=page.find('"track_share_url":"')+len('"track_share_url":"')
	f=page.find('"',i)
	try:
		page=urllib.urlopen(page[i:f]).read()
	except:
		print 'No Lyrics'
		return None
	i=page.find('"body":"')+len('"body":"')
	f=page.find('","language":"')
	lyrics=page[i:f]
	return lyrics.replace('\\n','\n')

def fDirectory(fname,path):
	
	try:
		pathD=path+r'\fixed'
		os.makedirs(pathD)
	except:
		print 'Exist'
	song=[fname,fname[:-3]+'txt']
	listFiles=os.listdir(path) 
	for arch in song:
		if arch in listFiles:
			shutil.copy(path+'\\'+arch, pathD)
			os.remove(path+'\\'+arch)