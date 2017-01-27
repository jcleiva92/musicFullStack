# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from getSong import downloadSong
from attachMeta import fDirectory, getFileName, cleanFileName, getPage, getResults, getGenre, getThumb, downloadThumb, attachTags, getLyrics

GResult=dict()
GPath=''
GArchName=''
@app.route('/')	
@app.route('/index/',methods=['GET','POST'])
def gSong():
	global GArchName
	if request.method=='POST':
		songs=request.form['songUrl']
		path=request.form['path']
		songs=songs.split(',')
		for song in songs:
			title=downloadSong(song,path) #'C:\Users\Camilo\Documents\py\Proyectos\MusicFullStack\songs'
			if title=='Path invalid':
				flash("Ha ingresado un directorio de descarga no valido")
				return render_template('index.html')
			if title=='Url invalid':
				flash("Ha ingresado una url de cancion no valida")
				return render_template('index.html')
			flash("Cancion descargada: " +title + " en la direccion: "+path)
		return redirect(url_for('fixSongs',path=path,val=0))
	else:
		return render_template('index.html')

@app.route('/index/fixSongs/', methods=['GET','POST'])
@app.route('/index/fixSongs/<string:path>/', methods=['GET','POST'])
@app.route('/index/fixSongs/<string:path>/<int:val>/', methods=['GET','POST'])
def fixSongs(path=None,val=None):
	'''val=2 elegir resultado, val=1 pedir path, val=0 cancion descargada'''
	print val, request.method
	if path is None:
		path='Sin path'
	if val is None:
		val=1
	nResults=6
	if request.method=='POST':
		if path =='Sin path': path=request.form['path']
		fnames=getFileName(path)
		for fname in fnames:
			searchFor=cleanFileName(fname)
			pageTableBase=getPage(searchFor,0)
			results=getResults(pageTableBase,nResults)
			global GResult
			global GPath
			global GArchName
			GResult=results
			GPath=path
			GArchName=fname
			flash("Cancion "+fname+" para arreglar en la direccion "+path)
			return render_template('fixSongs.html',path=path, val=2, results=results)
		#if val>=1: return render_template('fixSongs.html',path=path, val=2, results=results)
		#return redirect(url_for('fixSongs',path=path, val=val))
	else:
		return render_template('fixSongs.html',path=path, val=val)

@app.route('/index/resultados/<int:pos>')
def resultadosFinal(pos):
	global GResult
	global GPath
	global GArchName
	info=dict()
	genre=getGenre(GResult['UrlSong'][pos])
	if GResult['Cover'][pos]!='No Available': 
		tCover=downloadThumb(GResult['UrlAlbum'][pos],GResult['Name'][pos],GPath)
	else:
		tCover=''
	for key in GResult.keys():
		info[key]=GResult[key][pos]
	lyrics=getLyrics(info['Band'],info['Name'])
	newName=attachTags(GArchName,info,genre,lyrics,tCover,GPath)
	fDirectory(newName,GPath)
	return render_template('resultados.html',pos=pos,newName=newName)


'''
#downloadSong('iAHCsyOb3Rc','C:\Users\Camilo\Documents\py\Proyectos\MusicFullStack\songs')
'''
if __name__=='__main__':
	app.secret_key='super_secret_key'
	app.debug=True
	app.run(host='0.0.0.0', port =5000)
