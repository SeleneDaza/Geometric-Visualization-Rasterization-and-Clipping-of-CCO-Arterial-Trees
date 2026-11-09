from pathlib import Path

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from interface.visualization_surface import VisualizationSurface


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FOLDER = PROJECT_ROOT / "data" / "3D"
DATA_2D_FOLDER = PROJECT_ROOT / "data" / "2D"


class _StartupLoadingScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget#startupLoading {
                background: #f5f8fc;
            }
            QLabel {
                color: #23344d;
                font-size: 15px;
                font-weight: 600;
            }
        """)
        self.setObjectName("startupLoading")

        loading_layout = QVBoxLayout(self)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.setContentsMargins(40, 40, 40, 40)

        self.loading_label = QLabel("Carregando aplicação...")
        self.loading_label.setWordWrap(True)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.loading_indicator = QProgressBar()
        self.loading_indicator.setRange(0, 0)
        self.loading_indicator.setFixedWidth(220)
        self.loading_indicator.setTextVisible(False)

        loading_layout.addWidget(
            self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter
        )
        loading_layout.addWidget(self.loading_indicator)

    def show_error(self, message):
        self.loading_label.setText(message)
        self.loading_indicator.hide()


class _ApplicationInitializer(QThread):
    ready = Signal(object, object, object, object)
    failed = Signal(str)

    def run(self):
        try:
            from core.loader import ModelLoader
            from visualization.viewer_2d import Viewer2D
            from visualization.viewer_3d import Viewer3D

            DATA_FOLDER.mkdir(parents=True, exist_ok=True)
            DATA_2D_FOLDER.mkdir(parents=True, exist_ok=True)
            files = sorted(DATA_2D_FOLDER.glob("*.vtk"))
            files.extend(sorted(DATA_FOLDER.glob("*.vtk")))

            self.ready.emit(ModelLoader, Viewer2D, Viewer3D, files)
        except Exception as error:
            self.failed.emit(str(error))


class _ModelLoadWorker(QThread):
    model_loaded = Signal(int, str, object, object, object, object, int)
    model_failed = Signal(int, str, str)

    def __init__(self, request_id, file_path, loader_class, parent=None):
        super().__init__(parent)
        self.request_id = request_id
        self.file_path = file_path
        self.loader_class = loader_class

    def run(self):
        try:
            loader = self.loader_class(self.file_path)
            model = loader.get_model()
            statistics = loader.get_statistics()
            radius_range = loader.get_radius_range()
            dimension = loader.get_dimension()
            self.model_loaded.emit(
                self.request_id,
                self.file_path,
                loader,
                model,
                statistics,
                radius_range,
                dimension,
            )
        except Exception as error:
            self.model_failed.emit(
                self.request_id, self.file_path, str(error)
            )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Arterial Graphics Lab")
        self.resize(1200, 750)
        self.setStyleSheet("""
            QMainWindow { background: #f5f8fc; }
            QFrame#sidebar {
                background: #ffffff;
                border-right: 1px solid #e2e8f0;
            }
            QLabel { color: #23344d; }
            QLabel#appTitle { font-size: 19px; font-weight: 700; }
            QLabel#sectionTitle { font-size: 14px; font-weight: 650; }
            QLabel#statusLabel { color: #52647a; }
            QPushButton {
                min-height: 36px;
                padding: 0 10px;
                border: 1px solid #d5deea;
                border-radius: 7px;
                background: #ffffff;
                color: #23344d;
            }
            QPushButton:hover { background: #edf4fb; }
            QComboBox {
                min-height: 34px;
                border: 1px solid #d5deea;
                border-radius: 7px;
                padding: 0 8px;
                background: #ffffff;
            }
        """)

        self.loader = None
        self._loader_class = None
        self._active_load_id = 0
        self._model_workers = []

        self._create_interface()
        self._initialize_application()

    def _create_interface(self):
        self._root_stack = QStackedWidget()
        self.setCentralWidget(self._root_stack)

        self._loading_screen = _StartupLoadingScreen()
        self._root_stack.addWidget(self._loading_screen)

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(180)
        sidebar.setMaximumWidth(420)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 20, 18, 18)
        sidebar_layout.setSpacing(10)

        title = QLabel("Arterial Graphics Lab")
        title.setObjectName("appTitle")
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(10)

        model_title = QLabel("Selecionar modelo")
        model_title.setObjectName("sectionTitle")
        sidebar_layout.addWidget(model_title)

        self.file_selector = QComboBox()
        sidebar_layout.addWidget(self.file_selector)

        self.load_button = QPushButton("Carregar modelo")
        self.load_button.clicked.connect(self.load_selected_model)
        sidebar_layout.addWidget(self.load_button)

        self.browse_button = QPushButton("Adicionar arquivos")
        self.browse_button.clicked.connect(self.browse_file)
        sidebar_layout.addWidget(self.browse_button)

        self.directory_button = QPushButton("Adicionar pasta")
        self.directory_button.clicked.connect(self.browse_directory)
        sidebar_layout.addWidget(self.directory_button)

        sidebar_layout.addSpacing(16)
        status_title = QLabel("Status")
        status_title.setObjectName("sectionTitle")
        sidebar_layout.addWidget(status_title)

        self.status_label = QLabel("Preparando visualizadores...")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        sidebar_layout.addWidget(self.status_label)

        sidebar_layout.addSpacing(8)
        info_title = QLabel("Informações do modelo")
        info_title.setObjectName("sectionTitle")
        sidebar_layout.addWidget(info_title)

        self.info_label = QLabel("Nenhum modelo carregado.")
        self.info_label.setWordWrap(True)
        sidebar_layout.addWidget(self.info_label)
        sidebar_layout.addStretch()

        self.visualization_surface = VisualizationSurface()
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(6)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.addWidget(sidebar)
        self.main_splitter.addWidget(self.visualization_surface)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([260, 940])
        main_layout.addWidget(self.main_splitter)
        self._main_interface = central_widget
        self._root_stack.addWidget(self._main_interface)
        self._root_stack.setCurrentWidget(self._loading_screen)

    def _initialize_application(self):
        self._initialization_worker = _ApplicationInitializer(self)
        self._initialization_worker.ready.connect(self._finish_initialization)
        self._initialization_worker.failed.connect(self._initialization_failed)
        self._initialization_worker.start()

    def _finish_initialization(
        self, loader_class, viewer_2d_class, viewer_3d_class, files
    ):
        try:
            self._loader_class = loader_class
            self.add_files_to_selector(files)
            self.viewer_2d = viewer_2d_class(self)
            self.viewer_3d = viewer_3d_class(self)
            self.visualization_surface.set_viewers(
                self.viewer_2d, self.viewer_3d
            )
            self.visualization_surface.hide_loading()
            self.status_label.setText("Aplicação pronta para uso.")
            self._root_stack.setCurrentWidget(self._main_interface)
        except Exception as error:
            self._initialization_failed(str(error))

    def _initialization_failed(self, error):
        message = f"Não foi possível iniciar a aplicação.\n\nDetalhes: {error}"
        self._loading_screen.show_error(message)
        if self._initialization_worker.isRunning():
            self._initialization_worker.wait()
        QMessageBox.critical(self, "Falha ao iniciar", message)
        self.close()

    def center_on_primary_screen(self):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return

        available_geometry = screen.availableGeometry()
        frame_geometry = self.frameGeometry()
        frame_width = frame_geometry.width()
        frame_height = frame_geometry.height()

        if (
            frame_width > available_geometry.width()
            or frame_height > available_geometry.height()
        ):
            frame_margins_width = max(0, frame_width - self.width())
            frame_margins_height = max(0, frame_height - self.height())
            self.resize(
                max(1, available_geometry.width() - frame_margins_width),
                max(1, available_geometry.height() - frame_margins_height),
            )
            frame_geometry = self.frameGeometry()

        x = available_geometry.left() + (
            available_geometry.width() - frame_geometry.width()
        ) // 2
        y = available_geometry.top() + (
            available_geometry.height() - frame_geometry.height()
        ) // 2
        self.move(x, y)

    def browse_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar arquivos VTK",
            str(PROJECT_ROOT / "data"),
            "Arquivos VTK (*.vtk)",
        )
        if not file_paths:
            return

        added_files = self.add_files_to_selector(file_paths)
        self.status_label.setText(
            f"{len(added_files)} arquivo(s) adicionado(s) à lista."
            if added_files
            else "Os arquivos selecionados já estão na lista."
        )
        file_path = str(Path(file_paths[-1]).resolve())
        index = self.file_selector.findData(file_path)
        if index != -1:
            self.file_selector.setCurrentIndex(index)
            self.load_selected_model()

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar pasta com arquivos VTK",
            str(PROJECT_ROOT / "data"),
        )
        if not directory:
            return

        files = sorted(
            Path(directory).glob("*.vtk"),
            key=lambda path: path.name.casefold(),
        )
        if not files:
            self.status_label.setText(
                "A pasta selecionada não contém arquivos .vtk."
            )
            return

        added_files = self.add_files_to_selector(files)
        self.status_label.setText(
            f"{len(added_files)} arquivo(s) adicionado(s) à lista."
            if added_files
            else "Os arquivos desta pasta já estão na lista."
        )

    def add_files_to_selector(self, file_paths):
        existing_paths = {
            str(Path(self.file_selector.itemData(index)).resolve()).casefold()
            for index in range(self.file_selector.count())
        }
        added_files = []
        for file_path in file_paths:
            path = Path(file_path).resolve()
            path_key = str(path).casefold()
            if path.suffix.casefold() != ".vtk" or path_key in existing_paths:
                continue
            self.file_selector.addItem(path.name, str(path))
            existing_paths.add(path_key)
            added_files.append(str(path))
        return added_files

    def load_selected_model(self):
        file_path = self.file_selector.currentData()
        if not file_path:
            self.status_label.setText("Selecione um modelo para carregar.")
            return
        if self._loader_class is None:
            self.status_label.setText(
                "Os visualizadores ainda estão sendo preparados."
            )
            return

        self._active_load_id += 1
        worker = _ModelLoadWorker(
            self._active_load_id,
            file_path,
            self._loader_class,
        )
        worker.model_loaded.connect(self._model_loaded)
        worker.model_failed.connect(self._model_load_failed)
        worker.finished.connect(
            lambda worker=worker: self._remove_model_worker(worker)
        )
        self._model_workers.append(worker)
        self.visualization_surface.show_loading("Carregando modelo...")
        self.status_label.setText("Carregando modelo...")
        worker.start()

    def _model_loaded(
        self,
        request_id,
        file_path,
        loader,
        model,
        statistics,
        radius_range,
        dimension,
    ):
        if request_id != self._active_load_id:
            return
        try:
            self.loader = loader
            if dimension == 2:
                self.visualization_surface.viewer_container.setCurrentWidget(
                    self.viewer_2d
                )
                self.viewer_2d.show_model(model)
            else:
                self.visualization_surface.viewer_container.setCurrentWidget(
                    self.viewer_3d
                )
                self.viewer_3d.show_model(model)
            self.visualization_surface.set_model_dimension(dimension)

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
            self.status_label.setText("Modelo carregado com sucesso.")
        except Exception as error:
            self.status_label.setText(f"Erro ao exibir o modelo:\n{error}")
            self.info_label.setText(
                f"Erro ao carregar o modelo:\n{error}"
            )
        finally:
            self.visualization_surface.hide_loading()

    def _model_load_failed(self, request_id, file_path, error):
        if request_id != self._active_load_id:
            return
        self.visualization_surface.hide_loading()
        message = f"Erro ao carregar o modelo:\n{error}"
        self.status_label.setText(message)
        self.info_label.setText(f"Arquivo: {Path(file_path).name}\n\n{message}")

    def _remove_model_worker(self, worker):
        if worker in self._model_workers:
            self._model_workers.remove(worker)
        worker.deleteLater()
