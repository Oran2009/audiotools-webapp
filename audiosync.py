import librosa
import numpy as np
import os
from pydub import AudioSegment
import subprocess
import tempfile
import string
import random
import matplotlib.pyplot as plt


def sync(videofile, audiofile, method='chroma_stft', n_fft=4410, hop_size=512, sampling_rate=44100, duration_limit=120):
    # Description: Computes a chromagram
    # Input: numpy.ndarray (audio), sampling rate
    # Return: numpy.ndarray (Normalized energy for each chroma bin at each frame)
    # Uses: Librosa
    def featureExtraction(audio, sr):
        if method == 'chroma_stft':
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr, tuning=0, norm=2, hop_length=hop_size, n_fft=n_fft)
            return chroma
        else:
            return None

    # Description: Runs .bat file to combine video and audio
    # Input: Location of audio file, Location of Video File, Save Location
    # Return: None
    # Uses: ffmpeg
    def combine(audio_file, video_file, save_location):
        cmd = ['ffmpeg', '-y', '-i', video_file, '-i', audio_file, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a',
               'aac', '-b:a', '160k', save_location]
        subprocess.run(cmd)

    # Description: Runs .bat file to extract audio file from video
    # Input: Location of Video File, Save Location
    def extract(video_file, save_location):
        cmd = ['ffmpeg', '-y', '-loglevel', 'quiet', '-i', video_file, save_location]
        subprocess.run(cmd)

    # #############---------LOAD FILES---------##############

    # Load audio file
    audio_file = audiofile
    audio, _ = librosa.load(audio_file, sr=sampling_rate, mono=True, duration=duration_limit)

    # Load video file, creates .wav file of the video audio
    video_file = videofile
    handle, video_audio_file = tempfile.mkstemp(suffix='.wav')
    os.close(handle)
    extract(video_file, video_audio_file)
    video, _ = librosa.load(video_audio_file, sr=sampling_rate, mono=True, duration=duration_limit)
    os.unlink(video_audio_file)

    # #############---------SETUP SYNC---------##############

    # Chromagram
    audio_chroma = featureExtraction(audio, sampling_rate)

    # Chromagram
    video_chroma = featureExtraction(video, sampling_rate)

    # Performs RQA
    xsim = librosa.segment.cross_similarity(audio_chroma, video_chroma, mode='affinity')
    L_score, L_path = librosa.sequence.rqa(xsim, np.inf, np.inf, backtrack=True)

    audio_times = []
    video_times = []
    diff_times = []
    for v, a in L_path * hop_size / sampling_rate:
        A = float(a)
        V = float(v)
        audio_times.append(A)
        video_times.append(V)
        diff_times.append((A - V))

    # #############---------SYNC PROCESS---------##############

    # Find mean of time differences
    diff_times = np.array(diff_times)
    mean = np.average(diff_times)
    std = np.std(diff_times)
    diff_times = [d for d in diff_times if np.abs(d - mean) < (0.5 * std)]
    diff = np.average(diff_times)

    # Setting move option
    move = True if (diff > 0) else False

    # Sync using PyDub
    audio = AudioSegment.from_wav(audio_file)

    if move:
        # Trim diff seconds from beginning
        final = audio[diff * 1000:]
    else:
        # Add diff seconds of silence to beginning
        silence = AudioSegment.silent(duration=-diff * 1000)
        final = silence + audio

    # LOG results
    # append to log file; create file if not exist
    logfolder = '/home/site/wwwroot/log'
    if not os.path .exists(logfolder):
        os.makedirs(logfolder)
    logfilename = os.path.join(logfolder, 'sync.txt')
    with open(logfilename, 'a+') as logfile:
        logfile.write('Video: {} Audio: {} n_fft: {} hop_size: {} sampling_rate: {} duration_limit: {} diff: {}'.format(
            videofile, audiofile, n_fft, hop_size, sampling_rate, duration_limit, diff))

    # Export synced audio
    handle, synced_audio = tempfile.mkstemp(suffix='.wav')
    os.close(handle)
    final.export(synced_audio, format='wav')

    # #############---------COMBINE PROCESS---------##############
    base_file = '/home/site/wwwroot/combined/combined'
    rand = ''.join(random.choice(string.ascii_lowercase) for i in range(16))
    suffix = ''.join([rand, '.mp4'])
    save_file = "_".join([base_file, suffix])
    combine(synced_audio, video_file, save_file)
    os.unlink(synced_audio)
    # print('Synced and combined successfully to {}'.format(save_file))
    return save_file, diff
