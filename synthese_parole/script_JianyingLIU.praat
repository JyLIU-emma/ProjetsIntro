#pour nettoyer la fenêtre d'affichage (info)
clearinfo

######PARTIE 1: entrer la phrase et transcrire phonétiquement la phrase################################################
######créer la boite de dialogue pour entrer la phrase######
form Paramètres de la phrase
	comment Choisissez le sujet:
	optionmenu sujet: 1
		option Mon amie 
		option Ils 
		option Elles 
		option Charles 
		option Elodie 
		option Il 
		option Elle 
	optionmenu verbe: 1
		option me prête son ordinateur 
		option me prête son manuel 
		option discutent chaleureusement sur le sujet de l' immigration 
		option a reconnu son professeur 
		option a fait la vaisselle 
	optionmenu adv: 1
		option pour que je puisse faire le devoir sur le sujet de l' immigration
		option pendant la conférence
		option après le réveillon de Noël
		option (sans adv)
	comment choisissez la voix:
	choice voix: 1
		button aiguë
		button grave
	comment choisissez l'intonation:
	choice intonation: 1
		button énonciatif
		button intérrogatif
	comment Donnez le nom au fichier son (*.wav): 
	word nom phrase1.wav
endform

#concaténer la phrase entière
if adv = 4
	phrase$ = sujet$ + verbe$ - " "
else
	phrase$ = sujet$ + verbe$ + adv$
endif
pause Phrase traitée: 'phrase$'

######trouver sa forme phonetique######
#preparer la phrase, la chaine phonetique vide et la reference dico
phrase$ = phrase$ + " "
phrase_pho$ = ""
dico = Read Table from tab-separated file: "dico1.txt"

#extraire chaque mot et trouver sa forme phonetique
while phrase$ != ""
	mot$ = left$(phrase$, index(phrase$, " ")-1)
	reste$ = right$(phrase$, length(phrase$)-index(phrase$, " "))
	select 'dico'
	lignes = Extract rows where column (text): "orthographe", "is equal to", mot$
	mot_phonetique$ = Get value: 1, "phonetique"
	phrase_pho$ = phrase_pho$ + mot_phonetique$
	phrase$ = reste$
endwhile
phrase_pho$ = "_" + phrase_pho$ + "_"

#--------préparer les variables pour trouver plus tard le temps final de chaque syntagme-------
#trouver la longueur de la transcription phonétique du sujet
sujet_pho$ = ""
while sujet$ != ""
	mot$ = left$(sujet$, index(sujet$, " ")-1)
	reste$ = right$(sujet$, length(sujet$)-index(sujet$, " "))
	select 'dico'
	lignes = Extract rows where column (text): "orthographe", "is equal to", mot$
	mot_phonetique$ = Get value: 1, "phonetique"
	sujet_pho$ = sujet_pho$ + mot_phonetique$
	sujet$ = reste$
endwhile
longueur_sujet_pho = length(sujet_pho$)

#trouver la longueur de la transcription phonétique jusqu'à la fin du "verbe"
verbe_pho$ = ""
while verbe$ != ""
	mot$ = left$(verbe$, index(verbe$, " ")-1)
	reste$ = right$(verbe$, length(verbe$)-index(verbe$, " "))
	select 'dico'
	lignes = Extract rows where column (text): "orthographe", "is equal to", mot$
	mot_phonetique$ = Get value: 1, "phonetique"
	verbe_pho$ = verbe_pho$ + mot_phonetique$
	verbe$ = reste$
endwhile
longueur_verbe_pho = length(verbe_pho$)+ longueur_sujet_pho

#préparer les compteurs et les variables vides pour la concaténation des durées de diphones
i=1
c=1
temps_s = 0
temps_v = 0
#---------------------------------------------------------------------------------------------

######traiter la liaison de voyelle nasale######
# pour compter le nombre de caractères de cette chaîne
longeur_phrase = length(phrase_pho$)
for x from 1 to longeur_phrase-1
	diphone$ = mid$ (phrase_pho$,x,2)
	if diphone$ = "Ca"
		phrase_pho$ = replace$(phrase_pho$,diphone$,"Cna",0)
		#renouveler les variables préparés
		longueur_sujet_pho = longueur_sujet_pho+1
		longueur_verbe_pho = longueur_verbe_pho+1
	elsif diphone$ = "CO"
		phrase_pho$ = replace$(phrase_pho$,diphone$,"CnO",0)
		longueur_verbe_pho = longueur_verbe_pho+1
	endif
endfor
pause 'phrase_pho$'
printline 'phrase_pho$'
# pour compter le nouveau nombre de caractères de cette chaîne
longeur_phrase = length(phrase_pho$)


######PARTIE 2: Text-to-speech##################################################################################
######Ouvrir les fichiers sources et créer des variables qui vont identifier les fichiers ouverts######
fic_textgrid = Read from file: "phoneme_complet.TextGrid"
fic_son = Read from file: "loga_complet.wav"

select 'fic_son'
#pour obtenir le point où tous les intersections déscentes qui se croisent la ligne 0
intersections = To PointProcess (zeroes): 1, "no", "yes"

printline "Les fichiers utilisés sont : " 'fic_textgrid' et 'fic_son'

#créer un fichier de son vide qui peut être rempli plus tard
son_combine = Create Sound from formula: "sineWithNoise", 1, 0, 0.01, 44100, "0"

#compter le nombre de case noté dans le fichier text_grid
select 'fic_textgrid'
nbr_inter = Get number of intervals: 1 


######Chercher les diphones demandés et les combinés ensemble######
#définir les diphones cherchés
for x from 1 to longeur_phrase-1
	diphone$ = mid$ (phrase_pho$,x,2)
	phoneme1$ = left$ (diphone$,1)
	phoneme2$ = right$ (diphone$,1)
	
	#----extraire ces diphones du fichier son en utilisant les étiquettes du fichier text_grid-----------
	#trouver l'étiquette de chaque intervalle
	for y from 1 to nbr_inter-1
		select 'fic_textgrid'
		etiquette1$ = Get label of interval: 1, y
		etiquette2$ = Get label of interval: 1, y+1
		
		#localiser le diphone
		if etiquette1$ = phoneme1$ and etiquette2$ = phoneme2$
			#chercher le début et la fin de ce diphone
			temps1 = Get start time of interval: 1, y
			temps2 = Get start time of interval: 1, y+1
			temps3 = Get end time of interval: 1, y+1
			temps_debut = (temps1+temps2)/2
			temps_fin = (temps2+temps3)/2
			#pause le 'diphone$' commence à 'temps_debut' et finit à 'temps_fin'
			printline 'diphone$' de 'temps_debut' à 'temps_fin'
			
			select 'intersections'
			index_intersections1 = Get nearest index: 'temps_debut'
			temps_debut = Get time from index: 'index_intersections1'

			index_intersections2 = Get nearest index: 'temps_fin'
			temps_fin = Get time from index: 'index_intersections2'
#------concaténer la durée de chaque diphone jusqu'à la fin du sujet et du "verbe", servant plus tard à la modification prosodique--
			duree = temps_fin - temps_debut
			if i <= longueur_sujet_pho
				temps_s = temps_s + duree
				i=i+1
			endif
			if c <= longueur_verbe_pho
				temps_v = temps_v + duree
				c=c+1
			endif
#--------------------------------------------------------------------------------------------------------
			#extraire le diphone du fichier son
			select 'fic_son'
			son_diphone = Extract part: temps_debut, temps_fin, "rectangular", 1, "no"
			#ajouter/concaténer ce diphone extrait dans le fichier son vide
			select 'son_combine'
			plus 'son_diphone'
			son_combine = Concatenate
		endif
	endfor
endfor
######nettoyer la fenêtre Object######
select all
minus 'son_combine'
Remove


######PARTIE 3: Modification prosodique##################################################################################
######changer l'intonation######
#préparer les fichiers
select 'son_combine'
son_modifiable = To Manipulation: 0.01, 75, 600
pitch_tier = Extract pitch tier

#trouver le début et la fin de pitch
temps_debut = Get time from index: 1
longueur_son = Get end time
dernier_point = Get nearest index from time: longueur_son
temps_fin = Get time from index: dernier_point

#supprimer les points inutiles
Remove points between: temps_debut, temps_fin

#faire le changement de l'intonation selon le choix au début
if intonation = 2
	#pour phrase de 2 syntames
	if adv = 4
	#ajouter les points importants
	Add point: temps_debut, 240
	Add point: temps_s, 280
	Add point: temps_s+0.2, 240
	Add point: temps_fin, 440
	#faire le ton montant de dernier syntagme
	Modify interval (tone levels): temps_s+0.2, temps_fin, 200, 440, 5, "0.01 0.5 0.95 1.0", "fractions", "1.4 1.5 2.5 5.0"
	
	#pour phrase de 3 syntames
	else
	Add point: temps_debut, 240
	Add point: temps_s, 280
	Add point: temps_s+0.2, 240
	Add point: temps_v, 280
	Add point: temps_v+0.2, 240
	Add point: temps_fin, 440
	Modify interval (tone levels): temps_v+0.2, temps_fin, 200, 440, 5, "0.01 0.5 0.95 1.0", "fractions", "1.4 1.5 2.5 5.0"
	endif

	#combler automatiquement les points selon l'algorithme
	Interpolate quadratically: 4, "Hz"
	#obtenir le son avec l'intonation modifiée
	select 'son_modifiable'
	plus 'pitch_tier'
	Replace pitch tier
	select 'son_modifiable'
	son_into = Get resynthesis (overlap-add)

elsif intonation = 1
	if adv = 4
	Add point: temps_debut, 230
	Add point: temps_s, 270
	Add point: temps_s+0.2, 230
	Add point: temps_fin, 80
	#faire le ton descendant
	Modify interval (tone levels): temps_s+0.2, temps_fin, 80, 440, 5, "0.01 0.6 0.94 1.0", "fractions", "3.1 3.6 3.0 2.1"

	else
	Add point: temps_debut, 230
	Add point: temps_s, 270
	Add point: temps_s+0.2, 230
	Add point: temps_v, 270
	Add point: temps_v+0.2, 230
	Add point: temps_fin, 80
	Modify interval (tone levels): temps_v+0.2, temps_fin, 80, 440, 5, "0.01 0.6 0.94 1.0", "fractions", "3.1 3.6 3.0 2.1"
	endif

	Interpolate quadratically: 4, "Hz"

	select 'son_modifiable'
	plus 'pitch_tier'
	Replace pitch tier
	select 'son_modifiable'
	son_into = Get resynthesis (overlap-add)
endif

######Changer la durée(le faire plus vite)######
select 'son_into'
son_modifiable = To Manipulation: 0.01, 75, 600
duration_tier = Extract duration tier
Remove points between: 0, 40
temps_final = Get end time
Add point: temps_final*0.9, 0.65
#la parole est moins vite à la fin de chaque phrase, donc j'ajoute ici un 2e point
Add point: temps_final, 1.2

#obtenir le son avec vitesse changée
select 'son_modifiable'
plus 'duration_tier'
Replace duration tier
select 'son_modifiable'
son_vite = Get resynthesis (overlap-add)
son_resultat = son_vite

######Changer la voix (aiguë/grave, facultatif selon le choix)######
if voix = 2
	select 'son_vite'
	son_modifiable = To Manipulation: 0.01, 75, 600
	pitch_tier = Extract pitch tier

	#baisser le pitch
	Shift frequencies: 0, 1000, -30, "Hertz"
	Multiply frequencies: 0, 1000, 0.7

	#obtenir le son avec la voix plus grave
	select 'son_modifiable'
	plus 'pitch_tier'
	Replace pitch tier
	select 'son_modifiable'
	son_grave = Get resynthesis (overlap-add)
	son_resultat = son_grave
endif

######Sauvegarder le son final######
select 'son_resultat'
Save as WAV file: "phrase_synthétisée\'nom$'"
