from flask import Flask, render_template, request, flash, redirect, send_file, session
from werkzeug.utils import secure_filename
import os
import uuid
from audiosync import sync

VIDEO_UPLOAD_FOLDER = '/home/site/wwwroot/video'
AUDIO_UPLOAD_FOLDER = '/home/site/wwwroot/audio'
COMBINED_UPLOAD_FOLDER = '/home/site/wwwroot/combined'
VIDEO_EXTENSIONS = {'mp4'}
AUDIO_EXTENSIONS = {'wav'}

app = Flask(__name__)
app.config.update(SECRET_KEY='# REPLACE WITH SECRET KEY')
app.config['VIDEO_UPLOAD_FOLDER'] = VIDEO_UPLOAD_FOLDER
app.config['AUDIO_UPLOAD_FOLDER'] = AUDIO_UPLOAD_FOLDER
app.config['COMBINED_UPLOAD_FOLDER'] = COMBINED_UPLOAD_FOLDER


def allowed_video_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in VIDEO_EXTENSIONS


def allowed_audio_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in AUDIO_EXTENSIONS


@app.route('/')
def index():
    if 'videoFile' in session:
        os.remove(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], session['videoFile']))
    if 'audioFile' in session:
        os.remove(os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], session['audioFile']))
    if 'saveFile' in session:
        os.remove(session['saveFile'])
    [session.pop(key) for key in list(session.keys()) if key != '_flashes']
    return render_template('index.html')


@app.route('/video_upload', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        if 'videoFile' in session:
            return redirect(request.url_root)
        # DEBUG
        foldername = app.config['VIDEO_UPLOAD_FOLDER']
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        debugfile = os.path.join(foldername, 'log.txt')
        # DEBUG
        with open(debugfile, 'w') as logfile:
            flash('Uploading...', 'Status')
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part', 'Error')
                logfile.write('Error: No file part\n')
                return redirect(request.url_root)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if not file or file.filename == '':
                flash('No selected video file', 'Error')
                logfile.write('Error: No selected video file\n')
                return redirect(request.url_root)
            if allowed_video_file(file.filename):
                filename, file_extension = os.path.splitext(file.filename)
                session['videoFile'] = secure_filename(filename + uuid.uuid4().hex + file_extension)
                session.modified = True
                savefilename = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], session['videoFile'])
                logfile.write('Save filename = {}\n'.format(savefilename))
                file.save(savefilename)
                if os.path.exists(savefilename):
                    logfile.write('Save successful.\n')
                else:
                    logfile.write('Save failed.\n')
                flash('Done uploading video file!', 'Status')
    return render_template('index.html')


@app.route('/audio_upload', methods=['GET', 'POST'])
def upload_audio():
    if request.method == 'POST':
        if 'audioFile' in session:
            return redirect(request.url_root)
        # DEBUG
        foldername = app.config['AUDIO_UPLOAD_FOLDER']
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        debugfile = os.path.join(foldername, 'log.txt')
        # DEBUG
        with open(debugfile, 'w') as logfile:
            flash('Uploading...', 'Status')
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part', 'Error')
                logfile.write('Error: No file part\n')
                return redirect(request.url_root)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if not file or file.filename == '':
                flash('No selected audio file', 'Error')
                logfile.write('Error: No selected video file\n')
                return redirect(request.url_root)
            if allowed_audio_file(file.filename):
                filename, file_extension = os.path.splitext(file.filename)
                session['audioFile'] = secure_filename(filename + uuid.uuid4().hex + file_extension)
                session.modified = True
                savefilename = os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], session['audioFile'])
                logfile.write('Save filename = {}\n'.format(savefilename))
                file.save(savefilename)
                if os.path.exists(savefilename):
                    logfile.write('Save successful.\n')
                else:
                    logfile.write('Save failed.\n')
                flash('Done uploading audio file!', 'Status')
    return render_template('index.html')


@app.route('/process', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        flash('Processing...', 'Status')
        # display error msgs
        if 'videoFile' not in session and 'audioFile' not in session:
            flash('No selected video file or audio file', 'Error')
            return redirect(request.url_root)
        elif 'videoFile' in session and 'audioFile' not in session:
            flash('No selected audio file', 'Error')
            return redirect(request.url_root)
        elif 'videoFile' not in session and 'audioFile' in session:
            flash('No selected video file', 'Error')
            return redirect(request.url_root)

        fft = request.form['fft']
        hopLength = request.form['hopLength']
        samplingRate = request.form['samplingRate']
        duration = request.form['duration']

        # python function call to sync
        video = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], session['videoFile'])
        audio = os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], session['audioFile'])
        files, _ = sync(videofile=video, audiofile=audio, n_fft=fft, hop_size=hopLength, sampling_rate=samplingRate, duration_limit=duration)
        session['saveFile'] = files
        flash('Processing finished!', 'Status')
        os.remove(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], session['videoFile']))
        os.remove(os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], session['audioFile']))
        session.pop('videoFile', None)
        session.pop('audioFile', None)
    return render_template('index.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    # download
    if 'saveFile' not in session:
        flash('Nothing to download!', 'Error')
        return redirect(request.url_root)
    path = session['saveFile']
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    # debug
    if False:
        app.run()
    # live
    else:
        app.run(host="0.0.0.0", port=80)
