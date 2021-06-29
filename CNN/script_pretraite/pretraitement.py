"""
Ce script sert à prétraiter les fichiers audios. Il est utilisé avec le script "utils.py"

Premièrement, il supprimer les silence au début et à la fin des audios.

De plus, il change le speed de fichier audio dans le train set afin d'avoir plus de données pour l'entainement.
        Après tester sur les corpus petit, on a trouvé que le changement du speed aider à améliorer la performance 
        de modéle de classification. Parce que le pitch change aussi quand le speed change.

Vitesses par rapport au fichier initial: 0.9, 0.95, 1.05, 1.10. 
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import collections
import sys
import os
import wave
import webrtcvad
import random
import pydub
import numpy as np
#from script utils.py import
from utils import read_wave_from_file, save_wav, get_feature, plot_spectrogram, write_wave, read_wave

#-----------------------------Prélever les silences dans les enregistrement-------------------------
#-----------------------------------------Avec webrtcvad--------------------------------------------
AGGRESSIVENESS = 3
class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.

    Args:
        frame_duration_ms: The desired frame duration in milliseconds.
        audio: The PCM data.
        sample_rate: The sample rate
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, vad, frames):
    """Filters out non-voiced audio frames.

    Args:
        sample_rate: The audio sample rate, in Hz.
        vad: An instance of webrtcvad.Vad.
        frames: A source of audio frames (sequence or generator).

    Returns: A generator that yields PCM audio data.
    """

    voiced_frames = []
    for idx, frame in enumerate(frames):
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if is_speech:
            voiced_frames.append(frame)

    return b''.join([f.bytes for f in voiced_frames])


def voiced_frames_expand(voiced_frames, duration=2):
    total = duration * 8000 * 2
    expanded_voiced_frames = voiced_frames
    while len(expanded_voiced_frames) < total:
        expand_num = total - len(expanded_voiced_frames)
        expanded_voiced_frames += voiced_frames[:expand_num]

    return expanded_voiced_frames


def filter(wavpath, out_dir, expand=False):
    '''
    Apply vad with wave file.

    Args:
        wavpath: The input wave file.
        expand: Expand the frames or not, default False.
    '''
    print("wavpath:", wavpath)
    try:
        audio, sample_rate = read_wave(wavpath)
    except:
        print("wrong", wavpath)
        if os.path.exists(wavpath):
            os.remove(wavpath)
        return 0
    print('sample rate:%d'%sample_rate)
    vad = webrtcvad.Vad(AGGRESSIVENESS)
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    voiced_frames = vad_collector(sample_rate, vad, frames)
    voiced_frames = voiced_frames_expand(voiced_frames, 2) if expand else voiced_frames
    wav_name = wavpath.split('/')[-1]
    save_path = out_dir + '/' + wav_name
    write_wave(save_path, voiced_frames, sample_rate)

    return 1

#---------------------------------------Pré-amphasis: speed--------------------------

def speed_numpy(samples, speed):
    """
    :param speeds: une liste [0.9, 0.95, 1.05, 1.01]
    :param samples: un tuple (wave_data, framerate)
    :max_speed: no less than 0.9
    :min_speed: no bigger that 1.1
    :return:
    """
    
    data_type = samples[0].dtype
    
    old_length = samples.shape[0]
    new_length = int(old_length / speed)
    old_indices = np.arange(old_length)  
    new_indices = np.linspace(start=0, stop=old_length, num=new_length)  #Equalize the space between numbers from 0 to old_length
    samples = np.interp(new_indices, old_indices, samples)  # one-dimensional linear 
    samples = samples.astype(data_type)
        
    return samples

def main():
    path_list = open("../list_path.txt", "r").readlines()
    speeds = [0.9, 0.95, 1.05, 1.1]
    
    for in_wav in path_list:
        """
        Supprimer les silences dans les enregistrement
        """
        in_wav = in_wav.strip()
        partie_in = in_wav.split("/")
        out_rep = "../clean_amphasis/" + partie_in[2] + "/" + partie_in[3]
        if not os.path.exists(out_rep):
            os.makedirs(out_rep)
        t = filter(in_wav, out_rep, expand=False)

        new_in_wav = out_rep + "/" + partie_in[-1]
        for speed in speeds:
            if t == 1:
                """
                Data complete
                """
                audio_data = read_wave_from_file(new_in_wav)[0]
                try:
                    audio_data = speed_numpy(audio_data, speed)
                    out_file = out_rep + "/" + str(speed) + "-" + partie_in[-1]
                    save_wav(out_file, audio_data)
                except IndexError:
                    os.remove(in_wav)
                    
            if t == 0:
                """
                Data broken
                """
                pass

if __name__ == '__main__':
    main()

