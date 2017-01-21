from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app=Flask(__name__)

from getSong import downloadSong
from attachMeta import getFileName

@app.route('/')	
@app.route('/index/',methods=['GET','POST'])
def gSong():
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
	if path is None:
		path='Sin path'
	if val is None:
		val=1
	#nResults=5
	if request.method=='POST':
		#results=getFileName(path,nResults)
		print path
		if path =='Sin path': path=request.form['path']
		flash("Canciones arregladas en la direccion "+path)
		if val==1: return redirect(url_for('fixSongs',path=path, val=2))
		return redirect(url_for('fixSongs',path=path, val=val))
	else:
		return render_template('fixSongs.html',path=path, val=val)


'''
path=''
@app.route('/index/', methods=['GET','POST'])
def gSong():
	if request.method=='POST':
		songs=request.form['songName']
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
			flash("Song downloaded: " +title + " in path: "+path)
		return redirect(url_for('fixSongs'))
	else:
		return render_template('index.html')
		
@app.route('/index/fixSongs', methods=['GET','POST'])
def fixSongs():
	path='C:\Users\Camilo\Documents\py\Proyectos\MusicFullStack\songs'	
	nResults=5
	if request.method=='POST':
		results=getFileName(path,nResults)
		flash("Songs fixed")
		return redirect(url_for('fixSongs'))
	else:
		return render_template('fixSongs.html')
		
#downloadSong('iAHCsyOb3Rc','C:\Users\Camilo\Documents\py\Proyectos\MusicFullStack\songs')
'''
if __name__=='__main__':
	app.secret_key='super_secret_key'
	app.debug=True
	app.run(host='0.0.0.0', port =5000)
