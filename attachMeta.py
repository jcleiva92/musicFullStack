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
	return fileList
	