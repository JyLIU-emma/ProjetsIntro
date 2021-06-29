# Ce script demande le fichier auto_generate.py et répertoire "corpus" à côté, peut importe le répertoire courant
# Il faut aussi donner le chemin vers l'exécutable Praat et le script Praat "generate_spectrograms_as_images_from_sound_files.praat" dans auto_generate.py
# nom du répertoire entrée: corpus-initial
# nom du répertoire sortie (spectrogrammes): corpus/corpus_initial_spectrograms
# pour exécuter ce script:
# python coupe2sec.py

import glob
import os
from pydub import AudioSegment
from pydub.utils import make_chunks
import shutil
import sys

from auto_generate import auto_generate_spectrogram

def cut_2_sec(file, fade=True, silence=True):
    """
    couper le son en 2 secondes, ajouter fade-in, fade-out et silence avant et après l'extrait
    entrée: un fichier
    résultat: créer des chunks dans le même répertoire, supprimer l'ancien fichier audio complet
    """
    file_name, ext = os.path.splitext(file)
    file_name = file_name.split("/")[-1]
    silence = AudioSegment.silent(duration=100)

    myaudio = AudioSegment.from_file (file, "wav") 
    chunk_length_ms = 1800 # pydub calculates in millisec
    chunks = make_chunks(myaudio, chunk_length_ms) #Make chunks of nearly two sec

    for i, chunk in enumerate(chunks):
        chunk_name = f"chunk{i}_{file_name}.wav"
        if fade:
            chunk = chunk.fade_in(5).fade_out(5)
        if silence:
            chunk = silence + chunk + silence
        chunk.export(chunk_name, format="wav")
    os.remove(file)

def create_dir_corpus(name, list_class):
    """
        créer les répertoires en respectant la structure finale
        entrée: nom du nouveau répertoire, liste des catégories
        location de sauvegarder: dans "corpus" (il faut d'abord avoir ce répertoire)

        l'exemple arborescence:
            coupe2sec.py
            corpus
                -nouveau répertoire
    """
    path = f"{sys.path[0]}/corpus"
    # tester et supprimer d'abord le test et le train existants
    if os.path.exists(f"{path}/{name}"):
        shutil.rmtree(f"{path}/{name}")
        
    for partie in ["test","train"]:
        for categorie in list_class:
            os.makedirs(f"{path}/{name}/{partie}/{categorie}")


# D:\Downloads\corpus_organise_audio\clean_amphasis
def create_cat_list(dir_name):
    """
        selon corpus existant créer la liste des catégories, renvoyer cette liste

        structure du répertoire entrée (C'est également la structure initiale du jeu de données):
        dir_name
            -langue1
                -train
                -test
            -langue2
                -train
                -test
            ...
    """
    path = f"{sys.path[0]}/{dir_name}"
    list_class = []
    for subdir in os.listdir(path):
        if "." not in subdir:
            list_class.append(subdir)
    return list_class



# clean_amphasis\L001-huhu\test\*wav
# -1 filename
# -2 test/train
# -3 className
# chemin = f"{sys.path[0]}/test-result"

def get_place_info(corpus_dir):
    """
    parcourir l'ancien répertoire, obtenir les classes et usages des fichiers selon leur chemin
    renvoyer un dico:
        "xxx.wav" : (path, usage[train/test], classe[langue...])
           clé       valeur(tuple)
    """
    fic_dico = {}
    for root, dirs, files in os.walk(corpus_dir, topdown=False):
        for fic_name in files:
            path = os.path.join(root, fic_name)
            info_place = path.split("\\")
            usage = info_place[-2]
            classe = info_place[-3]  #langue
            fic_dico[fic_name] = (path,usage,classe)
    return fic_dico

def copy_to_right_position(source, destination):
    """
        copier le répertoire global en restructurer les fichiers
    """
    fic_dico = get_place_info(source)
    lst_cat = create_cat_list(source)
    create_dir_corpus(destination, lst_cat)
    for file in fic_dico:
        path = fic_dico[file][0]
        chemin = f"{sys.path[0]}/corpus/{destination}/{fic_dico[file][1]}/{fic_dico[file][2]}"
        shutil.copy(path, chemin)

def auto_cut(dir_corpus, list_class):     #respecter la structure finale
    """
        chunker les audio, modifier directement le répertoire entrée
    """
    # test-result\train\langue2
    for partie in ["test","train"]:
        for categorie in list_class:
            path = f"{sys.path[0]}/corpus/{dir_corpus}/{partie}/{categorie}"
            os.chdir(path)
            audio_files = os.listdir()
            for file in audio_files:
                cut_2_sec(file)

def create_dir_spectrograms(dir_audio, dir_image, list_class):
    """
        créer un nouveau répertoire pour les spectrogrammes générés
    """
    create_dir_corpus(dir_image, list_class)            #   "corpus_image"
    for partie in ["test","train"]:
        for categorie in list_class:
            path_in = f"{sys.path[0]}/corpus/{dir_audio}/{partie}/{categorie}"
            path_out = f"{sys.path[0]}/corpus/{dir_image}/{partie}/{categorie}"
            auto_generate_spectrogram(path_in, path_out)


def main():
    #réorganiser le corpus
    print("réorganiser le corpus:")
    corpus_dir = "corpus-initial"   # clean_amphasis généré par Danxin, placé à côté de ce script
    des = "corpus_initial_chunk"         #nom du répertoire destiné, stockera dans "corpus(répertoire à côté de ce script)"
    copy_to_right_position(corpus_dir, des)
    list_classes = create_cat_list(corpus_dir)
    # list_classes = ["L001-huhu", "L010-filph", "L011-kmkh", "L015-azaz", "L015B-azaz"]

    # chunker, changer répertoire d'entrée
    print("CHUNK: ")
    auto_cut(des, list_classes)

    #spectrogramme
    print("SPECTROGRAM: ")
    dir_audio = des
    dir_image = "corpus_initial_spectrograms"
    create_dir_spectrograms(dir_audio, dir_image, list_classes)

if __name__=="__main__":
    main()
