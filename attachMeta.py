# coding=utf-8

import re
import os
import urllib
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TCON, TRCK, APIC, USLT
import pandas as pd

def getFileName(path,nResults):
	fileList=os.listdir(path)
	return [archName for archName in fileList if '.mp3' in archName]
	
def cleanFileName(fname):
	'''Remove bad signs and words from file name'''
	fname=fname.decode('cp1252').encode('utf-8')#Big encode problem
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
	if getThumb(urlAlbum,name)[0]: 
		cover='Available'
		urlAlbum=getThumb(urlAlbum,name)[2]
	else: 
		cover= 'No Available'
		urlAlbum='No Available'
	album=album.replace('&amp;','&')
	return name, band, album, track,cover, urlAlbum,urlSong,f

def getThumb(urlAlbum,name):
	'''search and download Thumbnail'''
	pg=urllib.urlopen('https://musicbrainz.org'+urlAlbum).read()
	newName=cleanBasic(name).decode('utf-8')
	if pg.find('<div class="cover-art">')!=-1:
		i=pg.find('<div class="cover-art">')+len('<div class="cover-art">')
		i=pg.find('//',i)+len('//')
		f=pg.find('"',i)
		if '.jpg' in pg[i:f]:
			return True,'.jpg','https://'+pg[i:f],newName+'.jpg'
		if '.png' in pg[i:f]:
			return True,'.png','https://'+pg[i:f],newName+'.png'
	return False,'',''