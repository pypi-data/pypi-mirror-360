import os
import logging
import urllib.parse
from pathlib import Path

from AnyQt.QtCore import QThread, pyqtSignal
from AnyQt.QtWidgets import QApplication, QLabel, QPushButton, QProgressBar, QListWidget

import Orange.data
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.data import Domain, StringVariable, Table

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode
# ... (imports identiques)

_log = logging.getLogger(__name__)
IMAGE_RESOLUTION_SCALE = 2.0

class MarkdownConversionThread(QThread):
    result_signal = pyqtSignal(list)
    progress_signal = pyqtSignal(str, int)

    def __init__(self, input_dir, output_dir, parent=None):
        super().__init__(parent)
        self.input_dir = input_dir
        self.output_dir = output_dir
        print(f"[INIT THREAD] Input: {self.input_dir}, Output: {self.output_dir}")

    def run(self):
        print("[THREAD] Début du traitement des fichiers...")
        results = []
        files = list(self.input_dir.glob("*.pdf")) + \
                list(self.input_dir.glob("*.docx")) + \
                list(self.input_dir.glob("*.pptx"))

        print(f"[THREAD] {len(files)} fichiers détectés à traiter.")
        total_files = len(files)
        processed = 0

        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True

        doc_converter_pdf = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

        for idx, file_path in enumerate(files):
            try:
                print(f"[THREAD] Traitement de : {file_path}")
                output_subdir = self.output_dir / file_path.parent.relative_to(file_path.parents[1])
                print(f"[THREAD] Output Subdir: {output_subdir}")
                output_subdir.mkdir(parents=True, exist_ok=True)

                doc_filename = file_path.stem + "_md-with-image-refs.md"
                output_file_path = output_subdir / doc_filename

                if output_file_path.exists():
                    print(f"🔁 [THREAD] Fichier déjà traité, ignoré : {doc_filename}")
                    results.append((doc_filename, output_file_path.read_text(encoding='utf-8')))
                    processed += 1
                    self.progress_signal.emit(doc_filename, int(processed / total_files * 100))
                    continue

                print(f"[THREAD] Conversion du fichier : {file_path}")
                if file_path.suffix.lower() == ".pdf":
                    conv_res = doc_converter_pdf.convert(file_path)
                else:
                    conv_res = DocumentConverter().convert(file_path)

                print(f"[THREAD] Sauvegarde du markdown dans : {output_file_path}")
                conv_res.document.save_as_markdown(output_file_path, image_mode=ImageRefMode.REFERENCED)

                with open(output_file_path, 'r', encoding='utf-8') as f:
                    content = urllib.parse.unquote(f.read())

                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                results.append((doc_filename, content))
                processed += 1
                self.progress_signal.emit(doc_filename, int(processed / total_files * 100))

            except Exception as e:
                print(f"❌ [ERREUR] lors du traitement de {file_path}: {e}")
                import traceback
                traceback.print_exc()
                continue

        print("[THREAD] Tous les fichiers ont été traités.")
        self.result_signal.emit(results)


class FileProcessorApp(widget.OWWidget):
    name = "Markdownizer"
    description = "Convert PDFs, DOCX, TXT, CSV, PPTX to Markdown and store in an output folder"
    icon = "icons/md.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/md.png"
    priority = 1001
    category = "Advanced Artificial Intelligence Tools"
    want_control_area = False

    class Inputs:
        data = Input("Input Directory", Orange.data.Table)

    class Outputs:
        data = Output("Markdown Data Table", Orange.data.Table)
    class Inputs:
        data = Input("Data", Table)

    @Inputs.data
    def set_data(self, data):
        self.data = data
        if self.data is not None:
            print("[INPUT] Données reçues.")
            path_index = None
            for i, meta_var in enumerate(self.data.domain.metas):
                print(f"[INPUT] Meta trouvée : {meta_var.name}")
                if meta_var.name.lower() == 'input_dir':
                    path_index = i
                    break

            if path_index is not None:
                self.input_path = self.data.metas[0][path_index]
                print(f"[INPUT] Chemin d'entrée extrait : {self.input_path}")
                self.startProcessing()
            else:
                print("❗ Aucun champ 'input_dir' trouvé dans les métadonnées. Colonnes disponibles :",
                      [m.name for m in self.data.domain.metas])
        else:
            print("❗ Aucune donnée reçue en entrée.")

    def __init__(self):
        super().__init__()
        print("[INIT] Initialisation du widget Markdownizer...")
        self.initUI()
        self.data = None
        self.input_path = None

    def initUI(self):
        print("[UI] Construction de l'interface utilisateur.")
        self.setGeometry(200, 200, 600, 400)
        self.mainArea.layout().setSpacing(10)
        self.status_label = QLabel("Sélectionnez un dossier contenant des fichiers.")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.start_button = QPushButton("Démarrer le traitement")
        self.start_button.clicked.connect(self.startProcessing)

        self.file_list = QListWidget()

        self.mainArea.layout().addWidget(self.status_label)
        self.mainArea.layout().addWidget(self.progress_bar)
        self.mainArea.layout().addWidget(self.start_button)
        self.mainArea.layout().addWidget(self.file_list)

    def startProcessing(self):
        print("[PROCESS] Lancement du traitement...")
        if not self.input_path:
            print("❗ Aucun chemin d'entrée valide trouvé.")
            return

        input_dir = Path(self.input_path)
        if not input_dir.exists():
            print(f"❗ Dossier d'entrée introuvable : {input_dir}")
            return

        self.output_dir = input_dir.parent / (input_dir.name + "_md")
        print(f"[PROCESS] Répertoire de sortie : {self.output_dir}")

        self.progress_bar.setValue(0)
        self.start_button.setEnabled(False)
        self.status_label.setText("Traitement en cours...")

        self.thread = MarkdownConversionThread(input_dir, self.output_dir)
        self.thread.result_signal.connect(self.handle_results)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.start()
        self.progressBarInit()

    def update_progress(self, filename, progress):
        print(f"[PROGRESS] {filename} => {progress}%")
        self.file_list.addItem(f"✅ {filename}")
        self.progress_bar.setValue(progress)

    def handle_results(self, results):
        print(f"[RESULTS] Nombre total de résultats : {len(results)}")
        self.processingComplete(results)
        self.progressBarFinished()

    def processingComplete(self, results):
        print("[COMPLETE] Fin du traitement.")
        self.status_label.setText("Traitement terminé.")
        self.start_button.setEnabled(True)
        self.send_output(results)

    def send_output(self, results):
        print("[OUTPUT] Envoi des résultats à la sortie.")
        domain = Domain([], metas=[
            StringVariable('input_dir'),
            StringVariable('output_dir'),
            StringVariable('name'),
            StringVariable('content')
        ])
        metas = [[
            str(self.input_path),
            str(self.output_dir),
            name,
            content
        ] for name, content in results] if results else [["", "", "", ""]]

        table = Table(domain, [[] for _ in metas])
        for i, meta in enumerate(metas):
            table.metas[i] = meta
        print("[OUTPUT] Données prêtes à être envoyées.")
        self.Outputs.data.send(table)

if __name__ == "__main__":
    import sys
    print("[MAIN] Lancement de l'application Qt...")
    app = QApplication(sys.argv)
    window = FileProcessorApp()
    window.show()
    if hasattr(app, "exec"):
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())
