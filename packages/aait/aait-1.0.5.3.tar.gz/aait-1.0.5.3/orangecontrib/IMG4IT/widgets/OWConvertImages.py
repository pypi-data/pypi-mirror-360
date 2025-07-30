import numpy as np
import os
import zipfile
from PIL import Image
import pillow_heif
import Orange
from Orange.data import Table, Domain, StringVariable
from pathlib import Path
from Orange.widgets.widget import OWWidget, Input, Output
from AnyQt.QtWidgets import QApplication

class OWConvertImages(OWWidget):
    name = "Convert Images"
    description = "Takes one or more folders as input. In these folders, if a .zip file is found, extract the images it contains, convert them to JPG, and reduce their resolution to decrease the image file size."
    icon = "icons/resize-picture.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/resize-picture.svg"
    priority = 3000

    class Inputs:
        data = Input("Data", Orange.data.Table)

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        if self.data is None:
            return
        if "folders_path" in in_data.domain:
            self.folders_path = in_data.get_column("folders_path")
        elif "folder_path" in in_data.domain:
            self.folders_path = in_data.get_column("folder_path")
        if "file_path" in in_data.domain:
            self.path_file = in_data.get_column("file_path")
        else:
            if self.folders_path is None:
                self.error("No folder provided.")
                return
            path = Path(str(self.folders_path[0]))
            self.path_file = path.parent
        self.run()

    class Outputs:
        data = Output("Data", Orange.data.Table)

    def __init__(self):
        super().__init__()
        self.data = None
        self.folders_path = None
        self.path_file = None
        self.MAX_SIZE = (1000, 1000)
        self.run()

    def trouver_fichiers_zip(self,dossier):
        chemin_complet = None
        for racine, dossiers, fichiers in os.walk(dossier):
            for fichier in fichiers:
                if fichier.lower().endswith('.zip'):
                    chemin_complet = os.path.join(racine, fichier)
        return chemin_complet

    def run(self):
        self.error("")
        self.warning("")

        if self.data is None:
            return

        if self.folders_path is None or self.path_file is None:
            self.error("No folder provided.")
            return

        # Fonctionnel pour confideo
        # a modifier cette fonction encore la fonction de dezip à l'intérieur
        # il faudrait modifier pour enlever le début et ne laisser que la partie convertion d'image
        image_paths = []
        pillow_heif.register_heif_opener()
        # Extraction et collecte des images
        for file_path in self.folders_path:
            img = []
            path = self.trouver_fichiers_zip(file_path)
            if path == None:
                pass
            extract_path = file_path + "/" + "temp_images"
            os.makedirs(extract_path, exist_ok=True)
            ext = os.path.splitext(str(path))[1].lower()
            if ext == ".zip":
                with zipfile.ZipFile(path, "r") as zip_ref:
                    zip_ref.extractall(extract_path)
                for root, dirs, files in os.walk(extract_path):
                    for fname in files:
                        if fname.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".tif", ".heif", ".heic")):
                            img.append(os.path.join(root, fname))
            elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".heif", ".heic"]:
                image_paths.append(path)
            image_paths.append(img)

        converted_path = str(self.path_file) + "/temp_images/converted"
        os.makedirs(converted_path, exist_ok=True)
        new_image_paths = []

        for image_path in image_paths:
            for img_path in image_path:
                ext = os.path.splitext(img_path)[1].lower()
                if ext in [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".heif", ".heic"]:
                    try:
                        image = Image.open(img_path)
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        image.thumbnail(self.MAX_SIZE)
                        new_filename = os.path.splitext(os.path.basename(img_path))[0] + ".jpg"
                        new_path = os.path.join(converted_path, new_filename)
                        image.save(new_path, format="JPEG", quality=70)
                        new_image_paths.append(new_path)
                        # Supprimer l'original (facultatif)
                        # os.remove(img_path)
                    except Exception as e:
                        print(f"Erreur de conversion {img_path} : {e}")
        data_metas = [[str(self.path_file), str(new_image_paths)]]
        domain = Domain([], metas=[StringVariable("folder_path"), StringVariable("image_paths")])
        table = Table.from_numpy(domain, np.empty((len(data_metas), 0)), metas=data_metas)
        self.Outputs.data.send(table)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    my_widget = OWConvertImages()
    my_widget.show()
    if hasattr(app, "exec"):
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())
