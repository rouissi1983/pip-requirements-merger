import sys
import os
import re
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem
from PyQt6.QtCore import Qt

class RequirementApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Chargement du fichier .ui externe
        uic.loadUi('main.ui', self)
        
        # Ensembles (Sets) pour stocker les noms de packages uniques
        self.pkgs_1 = set()
        self.pkgs_2 = set()

        # Connexions des signaux
        self.folder1_btn.clicked.connect(lambda: self.load_requirements(1))
        self.folder2_btn.clicked.connect(lambda: self.load_requirements(2))
        self.compare_btn.clicked.connect(self.compare_and_merge)
        self.export_btn.clicked.connect(self.export_merged_list) # Assurez-vous d'avoir ce bouton dans l'UI

    def clean_pkg_name(self, text):
        """Nettoie la ligne : ignore les versions, URLs et espaces."""
        if not text or text.startswith(('#', '-r', '-e')):
            return None
        # Split sur les séparateurs courants : ==, >=, <=, @ et espace
        name = re.split(r'[=<>@\s]', text)[0]
        return name.strip().lower()

    def load_requirements(self, side):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir requirements.txt", "", "Text Files (*.txt)")
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Nettoyage et filtrage des lignes vides/commentaires
            cleaned = {self.clean_pkg_name(line) for line in lines if self.clean_pkg_name(line)}
            
            if side == 1:
                self.pkgs_1 = cleaned
                self.update_list_widget(self.listView1, sorted(list(cleaned)))
                self.folder1_path.setText(os.path.basename(file_path))
            else:
                self.pkgs_2 = cleaned
                self.update_list_widget(self.listView2, sorted(list(cleaned)))
                self.folder2_path.setText(os.path.basename(file_path))
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de lecture : {e}")

    def update_list_widget(self, list_widget, items):
        list_widget.clear()
        for item in items:
            list_widget.addItem(item)

    def compare_and_merge(self):
        """Colore les différences pour visualisation."""
        if not self.pkgs_1 or not self.pkgs_2:
            QMessageBox.warning(self, "Attention", "Chargez les deux fichiers pour comparer.")
            return

        # Coloration Liste 1 (Manquants dans 2 en rouge)
        for i in range(self.listView1.count()):
            item = self.listView1.item(i)
            item.setForeground(Qt.GlobalColor.darkGreen if item.text() in self.pkgs_2 else Qt.GlobalColor.red)

        # Coloration Liste 2 (Manquants dans 1 en rouge)
        for i in range(self.listView2.count()):
            item = self.listView2.item(i)
            item.setForeground(Qt.GlobalColor.darkGreen if item.text() in self.pkgs_1 else Qt.GlobalColor.red)

    def export_merged_list(self):
        """Fusionne (Union) et exporte sans doublons."""
        merged = sorted(list(self.pkgs_1 | self.pkgs_2)) # L'opérateur | fait l'union de deux sets
        
        if not merged:
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer la liste fusionnée", "requirements_merged.txt", "Text Files (*.txt)")
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(merged))
            QMessageBox.information(self, "Succès", f"{len(merged)} packages fusionnés exportés.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RequirementApp()
    window.show()
    sys.exit(app.exec())
