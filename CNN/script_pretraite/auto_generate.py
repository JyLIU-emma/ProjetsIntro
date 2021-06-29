import subprocess



def auto_generate_spectrogram(dir_input, dir_output):
    # sndFilesFolder = "D:\\Downloads\\corpus\\L2-train-100"
    sndFilesFolder = dir_input
    sndFilesExtension = ".wav"
    sndFilesRegex = "*.wav"
    soundFilesMaxDuration_seconds = "0"
    # generatedImagesFolder = "D:\\Downloads\\corpus\\L2-train-100-image"
    generatedImagesFolder = dir_output
    spectrogramWindowLength_seconds = "0.005"
    spectrogramMaxFrequency_Hz = "8000"
    spectrogramTimeStep_seconds = "0.002"
    spectrogramFrequencyStep_Hz = "20"
    spectrogramWindowShape = "Gaussian"
    plottedSpectrogramMinFrequency_Hz = "0"
    plottedSpectrogramMax_dBbyHz_ratio = "100"
    plottedSpectrogramAutoScaling = "1"
    plottedSpectrogramDynamicRange_dB = "50"
    plottedSpectrogramPreemphasis_dBbyOctave = "6"
    dynamicCompression = "0"
    imageWidthInches = "5"
    imageHeightInches = "3"

    subprocess.call(["D:\\Downloads\\Praat\\Praat.exe", "--run", "D:\\Downloads\\test_generate_spectrograms.praat", \
        sndFilesFolder, sndFilesExtension, sndFilesRegex, soundFilesMaxDuration_seconds, generatedImagesFolder, spectrogramWindowLength_seconds,\
            spectrogramMaxFrequency_Hz, spectrogramTimeStep_seconds, spectrogramFrequencyStep_Hz, spectrogramWindowShape, plottedSpectrogramMinFrequency_Hz,\
                plottedSpectrogramMax_dBbyHz_ratio, plottedSpectrogramAutoScaling, plottedSpectrogramDynamicRange_dB, plottedSpectrogramPreemphasis_dBbyOctave,\
                    dynamicCompression, imageWidthInches, imageHeightInches])

# dir_in = "D:\Downloads\corpus\L2-train-100"
# dir_out = "D:\Downloads\corpus\L2-train-100-image"
# auto_generate_spectrogram(dir_in, dir_out)



