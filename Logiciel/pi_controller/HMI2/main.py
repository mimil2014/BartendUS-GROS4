import sys
import time
#from calibration import Calibration_cam
#from Vision.calibration import Calibration_cam
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets as qtw
from PyQt5.QtWidgets import QDialog, QApplication, QInputDialog, QListWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from Logiciel.pi_controller.HMI2.librairieRecette import gestion_Recette,gestion_ingredient_dispo,recette
from Logiciel.pi_controller.HMI2.stateMachine import sequence
import serial.tools.list_ports


#init des variables globales
livreRecette=gestion_Recette()
livreIngredient=gestion_ingredient_dispo()
#calib = Calibration_cam()
max_Bouteille=9
sequence=sequence()


# Step 1: Create a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(object)
    enCours = pyqtSignal(bool)
    def run(self):
        """state_machine"""
        self.enCours.emit(True)
        sequence.sequence()
        for i in range(5):
            time.sleep(1)
        # sequence.sequence()
        self.enCours.emit(False)
        self.finished.emit()


class MainWindow(QDialog):
    def __init__(self):
        print("refresh")
        super(MainWindow, self).__init__()
        loadUi("pi_controller/HMI2/MainWindow_test.ui", self)
        self.recettes.clicked.connect(self.go_to_recettes)
        self.boire.clicked.connect(self.go_to_boire)
        # self.boire.clicked.connect(self.show_popup)
        self.bouteilles.clicked.connect(self.go_to_bouteilles)
        # self.consulter.clicked.connect(self.go_to_consulter_recettes)
        self.reglages.clicked.connect(self.go_to_reglages)

    def go_to_recettes(self):
        screen5 = consulter_recettes_screen5()
        widget.addWidget(screen5)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def go_to_boire(self):
        screen3 = boire_screen3()
        widget.addWidget(screen3)
        widget.setCurrentIndex(widget.currentIndex()+1)
        screen3.recettes_disponibles.setCurrentRow(-1)

    def go_to_bouteilles(self):
        screen4 = bouteilles_screen4()
        widget.addWidget(screen4)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_reglages(self):
        screen5 = reglages_screen5()
        widget.addWidget(screen5)
        widget.setCurrentIndex(widget.currentIndex() + 1)





#*****************************************************************************************************WINDOW RECETTE
class recette_screen2(QDialog):
    def __init__(self):
        super(recette_screen2, self).__init__()
        loadUi("pi_controller/HMI2/recette.ui", self)
        # mettre les recettes a jour dans la liste widget sans bouton
        self.precedent.clicked.connect(self.go_to_recettes)
        self.ajouter_alcool.clicked.connect(self.ajouter_ingredient)
        self.ajouter_recette.clicked.connect(self.ajouter_livreRecette)
        self.supprimer.clicked.connect(self.supprimer_ligne)
        self.delete_all.clicked.connect(self.supprimer_tout)
        self.liste_ingredient_recette=[]
        self.liste_quantite_recette=[]

    def go_to_recettes(self):
        screen5 = consulter_recettes_screen5()
        widget.addWidget(screen5)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def ajouter_ingredient(self):
        # travailler l'affichage de la liste widget

        alcool = self.alcool_ligne.text()
        quantite = self.quantite_ligne.text()

        if alcool == "":
            qtw.QMessageBox.information(self, 'Attention', '''Aucun alcool entrée'''+ "\n" + '''Réessayer...''')
            return
        try:
            quantite=float(quantite)
        except:
            qtw.QMessageBox.information(self, 'Erreur',
                                        '''La quantité "''' + quantite + '''" n'est pas un chiffre.''' + "\n" + '''Réessayer...''')
            return

        if quantite > 8:
            qtw.QMessageBox.information(self, 'Attention', '''La quantité d'alcool est supérieure à 8 oz'''+ "\n" + '''Réessayer...''')
            return

        self.liste_ingredient_recette.append(alcool)
        self.liste_quantite_recette.append(quantite)

        chaine_temp = alcool + ': ' + str(quantite) + 'oz'
        self.listWidget.addItem(chaine_temp)

        self.alcool_ligne.setText('')
        self.alcool_ligne.setFocus()
        self.quantite_ligne.setText('')
        self.quantite_ligne.setFocus()

    def supprimer_ligne(self):
        row=self.listWidget.currentRow()
        if(row>=0):
            self.listWidget.takeItem(row)
            self.liste_ingredient_recette.pop(row)
            self.liste_quantite_recette.pop(row)


    def supprimer_tout(self):
        self.listWidget.clear()
        self.liste_ingredient_recette.clear()
        self.liste_quantite_recette.clear()

    def ajouter_livreRecette(self):

        titre = self.titre_ligne.text()
        if titre == "":
            qtw.QMessageBox.information(self, 'Erreur entrée','''Aucun titre''' + "\n" + '''Réessayer...''')
            return

        if len(self.liste_ingredient_recette)<1:
            qtw.QMessageBox.information(self, 'Erreur entrée', '''Aucun ingrédient''' + "\n" + '''Ajoutez au moins un ingrédient...''')
            return

        livreRecette.ajouterRecette(titre,self.liste_ingredient_recette,self.liste_quantite_recette)
        livreRecette.update_recette_dispo(livreIngredient)
        self.liste_ingredient_recette.clear()
        self.liste_quantite_recette.clear()
        self.listWidget.clear()
        #clear le texte des boites
        self.alcool_ligne.setText('')
        self.alcool_ligne.setFocus()
        self.titre_ligne.setText('')
        self.titre_ligne.setFocus()
        self.quantite_ligne.setText('')
        self.quantite_ligne.setFocus()




#***********************************************************************************************WINDOW BOIRE
class boire_screen3(QDialog):
    def __init__(self):
        super(boire_screen3, self).__init__()
        loadUi("pi_controller/HMI2/Boire.ui", self)
        #mise a jour recette_dispo
        livreRecette.update_recette_dispo(livreIngredient)

        if(len(livreRecette.list_recette_dispo_string())>0):
            self.recettes_disponibles.addItems(livreRecette.list_recette_dispo_string())
        else:
            self.recettes_disponibles.addItem("Aucune Recette Compatible")


        self.recettes_disponibles.itemClicked.connect(self.voir_liste_ingredient)
        self.precedent.clicked.connect(self.go_to_MainWindowDialog)
        self.commander.clicked.connect(self.go_to_commander_screen6)
        print(self.recettes_disponibles.currentRow())
        print(self.recettes_disponibles.currentRow())
        # mettre les recettes a jour dans la liste widget sans bouton


    def go_to_MainWindowDialog(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        print(self.recettes_disponibles.currentRow())

    def voir_liste_ingredient(self):
        # afficher la liste d'ingrédients avec l'indice de la liste des recettes disponibles
        row = self.recettes_disponibles.currentRow()
        print(self.recettes_disponibles.currentRow())
        if row>=0 and len(livreRecette.list_recette_dispo_string())>0:
            self.ingredients.clear()
            self.ingredients.addItem(livreRecette.list_recette_dispo[row].afficherIngredient())

    def go_to_commander_screen6(self):
        # print(self.recettes_disponibles.currentRow())
        # print(self.recettes_disponibles.currentItem().text())
        row = self.recettes_disponibles.currentRow()
        print(self.recettes_disponibles.currentRow())
        if row >= 0 and len(livreRecette.list_recette_dispo_string()) > 0:
            recette_commander = livreRecette.list_recette_dispo[row]
            screen6=commander_screen6(recette_commander)
            widget.addWidget(screen6)
            widget.setCurrentIndex(widget.currentIndex()+1)
        else:
            qtw.QMessageBox.information(self, 'Erreur', '''Aucune recette selectionnée''' + "\n" + '''Sélectionnez ou ajouter une recette puis réessayez...''')
            return

    # def radioBouton(self):
    #     self.type_boire = 0
    #     if self.radioVerre.isChecked() == True:
    #         self.type_boire = 1
    #     if self.radioShot.isChecked() == True:
    #         self.type_boire = 2

#***************************************************************************************Consulter recette
class consulter_recettes_screen5(QDialog):
    def __init__(self):
        super(consulter_recettes_screen5, self).__init__()
        loadUi("pi_controller/HMI2/consulter_recette.ui", self)
        self.recettes_repertoire.clicked.connect(self.voir_liste_ingredient)
        self.ajouter_recette.clicked.connect(self.ajouter_recette_repertoire)
        self.supprimer.clicked.connect(self.supprimer_recette)
        self.precedent.clicked.connect(self.go_to_MainWindowDialog)
        livreRecette.lireRecette()

        if (len(livreRecette.list_recette_string()) > 0):
            self.recettes_repertoire.addItems(livreRecette.list_recette_string())
        else:
            self.recettes_repertoire.addItem("Aucune Recette")


    def voir_liste_ingredient(self):
        # afficher la liste d'ingrédients avec l'indice de la liste des recettes disponibles
        row = self.recettes_repertoire.currentRow()
        print(self.recettes_repertoire.currentRow())
        if row >= 0 and len(livreRecette.list_recette_string()) > 0:
            self.ingredients.clear()
            self.ingredients.addItem(livreRecette.getRecette(row).afficherIngredient())
            print(livreRecette.getRecette(row).getlistAlcool())

    def go_to_MainWindowDialog(self):
        mainwindow = MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def supprimer_recette(self):
        print('supprimer une recette')

    def ajouter_recette_repertoire(self):
        screen2 = recette_screen2()
        widget.addWidget(screen2)
        widget.setCurrentIndex(widget.currentIndex() + 1)


    def supprimer_recette(self):
        # avec currenrow qui donne l'indice appeler supprimerIngredient
        #faire un update donc call update_liste
        row=self.recettes_repertoire.currentRow()
        if row>=0:
            self.recettes_repertoire.takeItem(row)
            livreRecette.supprimerRecette(row)
            self.update_liste()

    def update_liste(self):
        # clear la liste liste_bouteilles
        # addItems
        self.ingredients.clear()
        self.recettes_repertoire.clear()
        self.recettes_repertoire.addItems(livreRecette.list_recette_string())
        livreRecette.update_recette_dispo(livreIngredient)
        return



#***********************************************************************************************WINDOW BOUTEILLE
class bouteilles_screen4(QDialog):
    def __init__(self):
        super(bouteilles_screen4, self).__init__()
        loadUi("pi_controller/HMI2/bouteilles.ui", self)

        # Initialisation des listes ici afin d'afficher des le debut ## additems(getlistingredients.text())
        self.quantite_ingredient=0
        self.precedent.clicked.connect(self.go_to_MainWindowDialog)
        self.ajouter.clicked.connect(self.ajouter_ingredient)
        self.supprimer.clicked.connect(self.supprimer_ligne)

        # self.label.setScaledContents(True)
        # self.label.setPixmap(QPixmap("icône-ou-logo-de-la-meilleure-qualité-d-alcool-dans-ligne-style-102955105.jpeg"))

        self.niveau_alcool.valueChanged.connect(self.slidervertical)
        self.update_liste()

    def slidervertical(self, value):
        self.quantite_ingredient = float("{:.2f}".format(value*750/99))

    def go_to_MainWindowDialog(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def ajouter_ingredient(self):

        ingredient = self.ingredient_ligne.text()
        position_ingredient = self.position_ingredient_ligne.text()

        if position_ingredient.isdigit()  :
            position_ingredient = int(position_ingredient)
        else:
            qtw.QMessageBox.information(self, 'Erreur position', '''La position"'''+position_ingredient+'''" est invalide.''')
            return

        if position_ingredient > max_Bouteille:
            qtw.QMessageBox.information(self, 'Erreur position', '''La position est trop élevé\n'''+'''Les positions valides sont de 0 à '''+str(max_Bouteille))
            return
        if self.quantite_ingredient==0  :
            qtw.QMessageBox.information(self, 'Erreur quantité','''Vous ne pouvez pas ajouter une bouteille vide''')
            return
        else:
            pass

        if livreIngredient.isIngredientDoublon(ingredient):
            qtw.QMessageBox.information(self, 'Erreur Doublon','''L'ingrédient : "''' + ingredient.lower() + '''" est déjà présent dans la liste''')
            return

        if livreIngredient.isPositionDoublon(position_ingredient):
            qtw.QMessageBox.information(self, 'Erreur Doublon', '''La  position : "''' + str(position_ingredient) + '''" est déjà occuper par une bouteille''')
            return

        livreIngredient.ajouterIngredient(ingredient,self.quantite_ingredient,position_ingredient)

        self.ingredient_ligne.setText('')
        self.ingredient_ligne.setFocus()
        self.position_ingredient_ligne.setText('')
        self.position_ingredient_ligne.setFocus()
        self.update_liste()

    def supprimer_ligne(self):
        row=self.liste_bouteilles.currentRow()
        if row>=0:
            self.liste_bouteilles.takeItem(row)
            livreIngredient.supprimerIngredient(row)
            self.update_liste()

    def update_liste(self):
        self.liste_bouteilles.clear()
        self.liste_bouteilles.addItems(livreIngredient.get_list_ingredient_string())
        return


#**********************************************************************************************************Commander
class commander_screen6(QDialog):
    def __init__(self, recette):
        super(commander_screen6, self).__init__()

        loadUi("pi_controller/HMI2/commander.ui", self)

        self.annuler.clicked.connect(self.go_to_Boire)
        self.terminer.clicked.connect(self.go_to_MainWindowDialog)
        self.terminer.clicked.connect(self.commander_verre)
        self.incrementer.clicked.connect(self.incrementer_compteur_verre)
        self.decrementer.clicked.connect(self.decrementer_compteur_verre)
        self.incrementer.clicked.connect(self.afficher_compteur)
        self.decrementer.clicked.connect(self.afficher_compteur)
        self.recette = recette
        self.nb_verre = 0
        # self.nombre_verre.setText('''Nombre de verre : "''' + str(self.nb_verre) + '''"''')
        self.nombre_verre.setText('''\t''' + str(self.nb_verre) + ' verre(s)')


    def go_to_Boire(self):
        windowBoire=boire_screen3()
        widget.addWidget(windowBoire)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def go_to_MainWindowDialog(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def incrementer_compteur_verre(self):
        if self.nb_verre < 8:
            self.nb_verre = self.nb_verre + 1
        else:
            qtw.QMessageBox.critical(self, 'Fail', '''Le nombre de verre ne peut pas avoir une valeur plus grande que 8.''')

    def decrementer_compteur_verre(self):
        if self.nb_verre > 0:
            self.nb_verre = self.nb_verre - 1
        else:
            qtw.QMessageBox.critical(self, 'Fail', '''Le nombre de verre ne peut pas avoir une valeur négative''')

    def afficher_compteur(self):
        str_nb_verre = str(self.nb_verre)
        self.nombre_verre.setText('''\t''' + str(self.nb_verre) + ' verre(s)')


    def commander_verre(self):
        self.startThreadSequence()
        # self.startThread()
        # print("pompe activer : ",sequence.pompe(recette_commander,livreIngredient))

        # verif_seuil = Calibration_cam()
        # if not verif_seuil.calib_vision_seuil():
        #     qtw.QMessageBox.critical(self, 'Fail', '''La caméra doit être calibrée.''')
        #     reglages_screen5.calibration(self)
        #     return

        # row = self.recettes_disponibles.currentRow()
        # recette_commander=livreRecette.list_recette_dispo[row]

        # self.thread.finished.connect(
        #     lambda: self.commander.setEnabled(False)
        # )
    def startThreadSequence(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.enCours.connect(self.afficherState)
        # self.worker.progress.connect(self.afficherTest)
        # Step 6: Start the thread
        self.thread.start()

    def afficherState(self,state):
        self.state=state
        print(state)

    def go_to_MainWindowDialog(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def supprimer_recette(self):
        pass

    def voir_liste_ingredient(self):
        # afficher la liste d'ingrédients avec l'indice de la liste des recettes disponibles
        row = self.recettes_repertoire.currentRow()
        print(self.recettes_repertoire.currentRow())
        if row>=0 and len(livreRecette.list_recette_string())>0:
            self.ingredients.clear()
            self.ingredients.addItem(livreRecette.list_recette[row].afficherIngredient())

#*******************************************************************************************************Reglage
class reglages_screen5(QDialog):
    def __init__(self):
        super(reglages_screen5, self).__init__()

        loadUi("pi_controller/HMI2/Reglage_v3.ui", self)

        self.precedent.clicked.connect(self.go_to_MainWindowDialog)
        self.home_all.clicked.connect(self.HOME_ALL)
        self.bouton_electro.clicked.connect(self.radioBouton_electro)
        self.bouton_servo.clicked.connect(self.radioBouton_servo)

        self.bouton_calibration.clicked.connect(self.calibration)
        self.move_to.clicked.connect(self.go_to_position)
        #self.connexion.connect(self.connected_button)

        self.radio_ouverture_servo.setChecked(True)
        self.radio_ouverture_electro.setChecked(True)

        #self.serialPort = []

    def go_to_MainWindowDialog(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def HOME_ALL(self):
        sequence.homing(False)

    def calibration(self):
        calib.calib_vision_init()


    def go_to_position(self):

        position_x=self.position_x.text()
        position_y=self.position_y.text()
        position_z=self.position_z.text()
        try:
            if position_x != "":
                position_y = float(position_y)
        except:
            qtw.QMessageBox.information(self, 'Erreur','''Entrée en Y incompatible''')
            return
        try:
            if position_y != "":
                position_x = float(position_x)
        except:
            qtw.QMessageBox.information(self, 'Erreur','''Entrée en X incompatible''')
            return
        try:
            if position_z != "":
                position_z = float(position_z)
        except:
            qtw.QMessageBox.information(self, 'Erreur','''Entrée en Z incompatible''')

        if position_x != "" and position_y!="" and position_z!="":
            sequence.moveTo((position_x), (position_y), False)
            sequence.moveUpDown((position_z) * 1000,False)

        elif position_x == "" and position_y=="" and position_z!="":
            sequence.moveUpDown((position_z) * 1000,False)

        elif position_x != "" and position_y!="" and position_z=="":
            sequence.moveTo((position_x),(position_y) , False)

        return

    def radioBouton_servo(self):
        self.type_servo = 0
        if self.radio_ouverture_servo.isChecked() == True:
            self.type_servo = 0
            sequence.servo(150,False)
        if self.radio_fermeture_servo.isChecked() == True:
            self.type_servo = 1
            sequence.servo(5, False)

    def radioBouton_electro(self):
        self.type_electro = 0
        if self.radio_ouverture_electro.isChecked() == True:
            self.type_electro = 0

        if self.radio_fermeture_electro.isChecked() == True:
            self.type_electro = 1
        sequence.electro(self.type_electro,False)

    def commande_purge_pompes(self):
        None

    def read_serial_port(self):
        try:
            ports = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(ports):
                self.serialPort.append(port)
            print(self.serialPort)
        except():
            print("Error while checking opened serial port")

    def connected_button(self):
        # le nom de la boite pour les ports est 'comboBox'
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.progress.connect(self.afficherTest)
        # Step 6: Start the thread
        self.thread.start()



app = QApplication(sys.argv)
widget=qtw.QStackedWidget()


mainwindow=MainWindow()
widget.addWidget(mainwindow)
widget.setFixedHeight(720)
widget.setFixedWidth(1280)
widget.show()
# widget.showFullScreen()

try:
    sys.exit(app.exec_())

except:
    print("Exiting")

