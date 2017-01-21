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
	print 'Try '+str(t)
	if page.find('Search Error - MusicBrainz')> -1 : 
		t+=1
		print page
		return getPage(song,t)
	return page[getTable(page)[0]:getTable(page)[1]] #Finds results table from musicbrainz
	
