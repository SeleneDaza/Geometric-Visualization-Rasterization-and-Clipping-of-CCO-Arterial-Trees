
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QFrame,
    QStackedWidget
)

from core.loader import ModelLoader
from visualization.viewer_3d import Viewer3D
from visualization.viewer_2d import Viewer2D


# Raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FOLDER = PROJECT_ROOT / "data" / "3D"
DATA_2D_FOLDER = PROJECT_ROOT / "data" / "2D"


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Arterial Graphics Lab")
        self.resize(1200, 750)

        self.loader = None

        self.create_interface()
        self.load_available_files()

    def create_interface(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # -------------------------
        # Panel lateral
        # -------------------------

        sidebar = QFrame()
        sidebar.setFixedWidth(250)

        sidebar_layout = QVBoxLayout(sidebar)

        title = QLabel("Arterial Graphics Lab")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        sidebar_layout.addWidget(title)

        sidebar_layout.addWidget(QLabel("Selecionar modelo:"))

        self.file_selector = QComboBox()
        sidebar_layout.addWidget(self.file_selector)

        self.load_button = QPushButton("Carregar modelo")
        self.load_button.clicked.connect(
            self.load_selected_model
        )

        sidebar_layout.addWidget(self.load_button)

        self.browse_button = QPushButton("Procurar arquivo")
        self.browse_button.clicked.connect(
            self.browse_file
        )

        sidebar_layout.addWidget(self.browse_button)

        sidebar_layout.addSpacing(20)

        sidebar_layout.addWidget(QLabel("Informações do modelo"))

        self.info_label = QLabel(
            "Nenhum modelo foi carregado."
        )

        self.info_label.setWordWrap(True)

        sidebar_layout.addWidget(self.info_label)

        sidebar_layout.addStretch()

        # -------------------------
        # Visualizador
        # -------------------------

        self.viewer_container = QStackedWidget()
        self.viewer_2d = Viewer2D(self)
        self.viewer_3d = Viewer3D(self)
        self.viewer_container.addWidget(self.viewer_2d)
        self.viewer_container.addWidget(self.viewer_3d)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.viewer_container, stretch=1)

    def load_available_files(self):

        DATA_FOLDER.mkdir(parents=True, exist_ok=True)
        DATA_2D_FOLDER.mkdir(parents=True, exist_ok=True)

        files_2d = sorted(DATA_2D_FOLDER.glob("*.vtk"))
        files_3d = sorted(DATA_FOLDER.glob("*.vtk"))
        files = [(file, 2) for file in files_2d] + [(file, 3) for file in files_3d]

        for file, _dimension in files:
            self.file_selector.addItem(
                file.name,
                str(file)
            )

    def browse_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo VTK",
            str(PROJECT_ROOT / "data"),
            "Arquivos VTK (*.vtk)"
        )

        if file_path:

            index = self.file_selector.findData(file_path)

            if index == -1:
                self.file_selector.addItem(
                    Path(file_path).name,
                    file_path
                )
                index = self.file_selector.count() - 1

            self.file_selector.setCurrentIndex(index)

            self.load_selected_model()

    def load_selected_model(self):

        file_path = self.file_selector.currentData()

        if not file_path:
            return

        try:
            self.loader = ModelLoader(file_path)

            model = self.loader.get_model()

            statistics = self.loader.get_statistics()
            radius_range = self.loader.get_radius_range()

            dimension = self.loader.get_dimension()

            if dimension == 2:
                self.viewer_container.setCurrentWidget(self.viewer_2d)
                self.viewer_2d.show_model(model)
            else:
                self.viewer_container.setCurrentWidget(self.viewer_3d)
                self.viewer_3d.show_model(model)

            # Atualizar estatísticas
            info = (
                f"Arquivo: {Path(file_path).name}\n\n"
                f"Pontos: {statistics['points']}\n"
                f"Linhas: {statistics['lines']}\n\n"
                f"Atributos: {statistics['attributes']}"
            )

            if radius_range is not None:
                info += (
                    f"\n\nRaio mínimo: {radius_range['min']:.4f}"
                    f"\nRaio máximo: {radius_range['max']:.4f}"
                )

            self.info_label.setText(info)

        except Exception as error:

            self.info_label.setText(
                f"Erro ao carregar o modelo:\n{error}"
            )
