form generate_spectrograms_as_images_from_sound_files
	# sentence sndFilesFolder /Users/nicolasaudibert/Google Drive/cours_Paris3/reseaux_neurones_TAL/donnees/NCCFr_an/extrait_wav
	sentence sndFilesFolder D:\Downloads\corpus\L2-train-100
	word sndFilesExtension .wav
	word sndFilesRegex *.wav
	comment Set sound file max duration to 0 to autodetect
	real soundFilesMaxDuration_seconds 0
	sentence generatedImagesFolder D:\Downloads\corpus\L2-train-100-image-inPraat
	# Spectrogram settings, see http://www.fon.hum.uva.nl/praat/manual/Sound__To_Spectrogram___.html for details
	real spectrogramWindowLength_seconds 0.005
	natural spectrogramMaxFrequency_Hz 8000
	real spectrogramTimeStep_seconds 0.002
	natural spectrogramFrequencyStep_Hz 20
	sentence spectrogramWindowShape Gaussian
	# Plotting options, see http://www.fon.hum.uva.nl/praat/manual/Intro_3_2__Configuring_the_spectrogram.html for options specific to spectrograms
	integer plottedSpectrogramMinFrequency_Hz 0
	natural plottedSpectrogramMax_dBbyHz_ratio 100
	boolean plottedSpectrogramAutoScaling 1
	natural plottedSpectrogramDynamicRange_dB 50
	natural plottedSpectrogramPreemphasis_dBbyOctave 6
	real dynamicCompression 0
	# Image size settings
	real imageWidthInches 5
	real imageHeightInches 3
endform

# Create target folder if needed
createDirectory: generatedImagesFolder$

# Get the list of sound files to be processed
sndFilesSearchPath$ = sndFilesFolder$ + "/" + sndFilesRegex$
fileslist = Create Strings as file list: "fileslist", sndFilesSearchPath$
nFiles = Get number of strings

# If soundFilesMaxDuration_seconds is 0 (or a negative value), first pass on each sound file to get the max duration
if soundFilesMaxDuration_seconds<=0
	soundFilesMaxDuration_seconds = 0
	for iFile from 1 to nFiles
		# Read the sound file
		selectObject: fileslist
		currentSndFile$ = Get string: iFile
		currentSnd = Read from file: sndFilesFolder$ + "/" + currentSndFile$
		# Get its duration
		currentSndDuration = Get total duration
		if currentSndDuration > soundFilesMaxDuration_seconds
			soundFilesMaxDuration_seconds = currentSndDuration
		endif
		# Remove it from the objects list
		removeObject: currentSnd
	endfor
endif

# Convert autoscaling option to string
if plottedSpectrogramAutoScaling=1
	plottedSpectrogramAutoScalingString$ = "yes"
else
	plottedSpectrogramAutoScalingString$ = "no"
endif

# Clean the Praat picture window from any preexisting picture
Erase all
# Generate a spectrogram image for each input sound file
for iFile from 1 to nFiles
	# Read the sound file
	selectObject: fileslist
	currentSndFile$ = Get string: iFile
	currentSndFileBasename$ = currentSndFile$ - sndFilesExtension$
	currentSnd = Read from file: sndFilesFolder$ + "/" + currentSndFile$
	# Get its duration
	currentSndDuration = Get total duration
	# Get the spectrogram
	currentSpectro = To Spectrogram: spectrogramWindowLength_seconds, spectrogramMaxFrequency_Hz, spectrogramTimeStep_seconds, spectrogramFrequencyStep_Hz, spectrogramWindowShape$
	# Account for duration differences across sound files by adding silence at the end
	zero_padding_factor = imageWidthInches / (soundFilesMaxDuration_seconds/currentSndDuration) 	
	# Plot the spectrogram in the Praat picture window, adapting the viweport width to add final silence when needed
	Select outer viewport: 0, zero_padding_factor, 0, imageHeightInches
	selectObject: currentSpectro
	Paint: 0, 0, plottedSpectrogramMinFrequency_Hz, spectrogramMaxFrequency_Hz, plottedSpectrogramMax_dBbyHz_ratio, plottedSpectrogramAutoScalingString$, plottedSpectrogramDynamicRange_dB, plottedSpectrogramPreemphasis_dBbyOctave, dynamicCompression, "no"
	# Get back to the default "full" viewport abd save the result as a PNG image
	Select outer viewport: 0, imageWidthInches, 0, imageHeightInches
	Save as 300-dpi PNG file: generatedImagesFolder$ + "/" + currentSndFileBasename$ + ".png"
	# Clean the Praat picture window and remove temporary objects
	Erase all
	removeObject: currentSnd, currentSpectro
endfor

# Clean-up: remove the list of sound files
removeObject: fileslist

writeInfoLine: "Generated ", nFiles, " spectrogram images in folder ", generatedImagesFolder$
appendInfoLine: "Max duration of sound files: ", soundFilesMaxDuration_seconds, " seconds"
