# coding=utf-8
from __future__ import unicode_literals
import youtube_dl
import os

def downloadSong(song, path):
	options = {
		'format': 'bestaudio/best', # choice of quality
		'postprocessors': [{
					  'key': 'FFmpegExtractAudio',
						  'preferredcodec': 'mp3',
						  'preferredquality': '192',
				  },],
		'outtmpl': '%(title)s'.split("-")[0] + '.%(ext)s',        # name the file
		'noplaylist' : True,        # only download single song, not playlist  
	}
	try:
		os.chdir(path)
	except:
		return 'Path invalid'
	try:
		with youtube_dl.YoutubeDL(options) as ydl:
			info_dict = ydl.extract_info(song, download=False)
			title = info_dict.get('title', None)
			ydl.download([song])
		return title
	except:
		return 'Url invalid'
	