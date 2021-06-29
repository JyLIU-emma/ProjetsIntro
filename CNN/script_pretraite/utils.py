import wave
import librosa
import numpy as np
import matplotlib.pyplot as plt
import contextlib

def tensor_to_img(spectrogram, x_range=None, y_range=None):
    plt.figure()  # arbitrary, looks good on my screen.
    # plt.imshow(spectrogram[0].T)
    plt.imshow(spectrogram.T)
    if x_range is not None:
        plt.xlim(0, x_range)
    if y_range is not None:
        plt.ylim(0, y_range)
    plt.show()


# Draw graphe of spectrogram
def plot_spectrogram(spec, note):
    """
    audio feature figure
    (feature_dim, time_step)
    """
    fig = plt.figure(figsize=(20, 5))
    heatmap = plt.pcolor(spec)
    fig.colorbar(mappable=heatmap)
    plt.xlabel('Time(s)')
    plt.ylabel(note)
    plt.tight_layout()
    plt.show()


def save_wav(file_name, audio_data, channels=1, sample_width=2, rate=16000):
    wf = wave.open(file_name, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(rate)
    wf.writeframes(b''.join(audio_data))
    wf.close()


def read_wave_from_file(audio_file):
    """
    return 1d array, sampling rate"""
    wav = wave.open(audio_file, 'rb')
    num_frames = wav.getnframes()
    framerate = wav.getframerate()
    str_data = wav.readframes(num_frames)
    wav.close()
    wave_data = np.frombuffer(str_data, dtype=np.short)
    return wave_data, framerate


def concat_frame(features, left_context_width, right_context_width):
    time_steps, features_dim = features.shape
    concated_features = np.zeros(
        shape=[time_steps, features_dim *
               (1 + left_context_width + right_context_width)],
        dtype=np.float32)
    # middle part is just the uttarnce
    concated_features[:, left_context_width * features_dim:
                         (left_context_width + 1) * features_dim] = features

    for i in range(left_context_width):
        # add left context
        concated_features[i + 1:time_steps,
        (left_context_width - i - 1) * features_dim:
        (left_context_width - i) * features_dim] = features[0:time_steps - i - 1, :]

    for i in range(right_context_width):
        # add right context
        concated_features[0:time_steps - i - 1,
        (right_context_width + i + 1) * features_dim:
        (right_context_width + i + 2) * features_dim] = features[i + 1:time_steps, :]

    return concated_features


def subsampling(features, subsample=3):
    interval = subsample
    temp_mat = [features[i]
                for i in range(0, features.shape[0], interval)]
    subsampled_features = np.row_stack(temp_mat)
    return subsampled_features


def get_feature(wave_data, framerate=16000, feature_dim=128):
    """
    :param wave_data: 1d array
    :param framerate:
    :param feature_dim:
    :return: specgram 
    """
    wave_data = wave_data.astype("float32")
    specgram = librosa.feature.melspectrogram(wave_data, sr=framerate, n_fft=512, hop_length=160, n_mels=feature_dim)
    specgram = np.where(specgram == 0, np.finfo(float).eps, specgram)
    specgram = np.log10(specgram)
    return specgram


def get_final_feature(samples, sample_rate=16000, feature_dim=128, left=3, right=0, subsample=3):
    feature = get_feature(samples, sample_rate, feature_dim)
    feature = concat_frame(feature, left, right)
    feature = subsampling(feature, subsample)
    return feature


def log_mel(file, sr=16000, dim=80, win_len=25, stride=10):
    samples, sr = librosa.load(file, sr=sr)
    samples = samples * 32768
    win_len = int(sr / 1000 * win_len)
    hop_len = int(sr / 1000 * stride)
    feature = librosa.feature.melspectrogram(samples, sr=sr, win_length=win_len, hop_length=hop_len, n_mels=dim)
    feature = np.where(feature == 0, np.finfo(float).eps, feature)
    feature = np.log10(feature)
    return feature


def read_wave(path):
    """
    Reads wave file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """
    Writes a .wav file.
    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)

