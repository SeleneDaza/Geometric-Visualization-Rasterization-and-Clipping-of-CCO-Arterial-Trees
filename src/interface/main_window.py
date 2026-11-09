from pathlib import Path

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
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

        self.setWindowTitle("Laboratório de Gráficos Arteriais")
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
        self._current_dimension = None
        self._translation_actions = []

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
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_scroll_area = QScrollArea()
        sidebar_scroll_area.setWidgetResizable(True)
        sidebar_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        sidebar_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        sidebar_content = QWidget()
        sidebar_content_layout = QVBoxLayout(sidebar_content)
        sidebar_content_layout.setContentsMargins(18, 20, 18, 18)
        sidebar_content_layout.setSpacing(10)
        sidebar_scroll_area.setWidget(sidebar_content)
        sidebar_layout.addWidget(sidebar_scroll_area)

        title = QLabel("Laboratório de Gráficos Arteriais")
        title.setObjectName("appTitle")
        sidebar_content_layout.addWidget(title)
        sidebar_content_layout.addSpacing(10)

        model_title = QLabel("Selecionar modelo")
        model_title.setObjectName("sectionTitle")
        sidebar_content_layout.addWidget(model_title)

        self.file_selector = QComboBox()
        sidebar_content_layout.addWidget(self.file_selector)

        self.load_button = QPushButton("Carregar modelo")
        self.load_button.clicked.connect(self.load_selected_model)
        sidebar_content_layout.addWidget(self.load_button)

        self.browse_button = QPushButton("Adicionar arquivos")
        self.browse_button.clicked.connect(self.browse_file)
        sidebar_content_layout.addWidget(self.browse_button)

        self.directory_button = QPushButton("Adicionar pasta")
        self.directory_button.clicked.connect(self.browse_directory)
        sidebar_content_layout.addWidget(self.directory_button)

        sidebar_content_layout.addSpacing(16)
        status_title = QLabel("Status")
        status_title.setObjectName("sectionTitle")
        sidebar_content_layout.addWidget(status_title)

        self.status_label = QLabel("Preparando visualizadores...")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        sidebar_content_layout.addWidget(self.status_label)

        sidebar_content_layout.addSpacing(8)
        info_title = QLabel("Informações do modelo")
        info_title.setObjectName("sectionTitle")
        sidebar_content_layout.addWidget(info_title)

        self.info_label = QLabel("Nenhum modelo carregado.")
        self.info_label.setWordWrap(True)
        sidebar_content_layout.addWidget(self.info_label)

        color_map_title = QLabel("Mapa de cores")
        color_map_title.setObjectName("sectionTitle")
        sidebar_content_layout.addWidget(color_map_title)

        self.color_map_selector = QComboBox()
        self.color_map_selector.addItem("Viridis", "viridis")
        self.color_map_selector.addItem("HSV", "hsv")
        self.color_map_selector.addItem("RGB", "rgb")
        self.color_map_selector.currentIndexChanged.connect(
            self._update_color_map
        )
        sidebar_content_layout.addWidget(self.color_map_selector)

        antialiasing_title = QLabel("Suavização de bordas")
        antialiasing_title.setObjectName("sectionTitle")
        sidebar_content_layout.addWidget(antialiasing_title)

        self.antialiasing_checkbox = QCheckBox("Ativar antialiasing (FXAA)")
        self.antialiasing_checkbox.setChecked(True)
        self.antialiasing_checkbox.setToolTip(
            "Aplica filtragem de subpixel para suavizar as artérias nos "
            "visualizadores 2D e 3D."
        )
        self.antialiasing_checkbox.toggled.connect(self._update_antialiasing)
        sidebar_content_layout.addWidget(self.antialiasing_checkbox)
        sidebar_content_layout.addStretch()

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

    def _connect_transform_controls(self):
        panel = self.visualization_surface.transform_panel
        panel.translation_changed.connect(
            lambda x, y, z: self.viewer_3d.set_transform_parameters(
                (x, y, z),
                tuple(slider.value() for slider in panel.rotation_sliders),
                panel.scale_slider.value() / 100,
            )
        )
        panel.rotation_changed.connect(
            lambda x, y, z: self.viewer_3d.set_transform_parameters(
                tuple(
                    slider.value() / 100
                    for slider in panel.translation_sliders
                ),
                (x, y, z),
                panel.scale_slider.value() / 100,
            )
        )
        panel.scale_changed.connect(
            lambda factor: self.viewer_3d.set_transform_parameters(
                tuple(
                    slider.value() / 100
                    for slider in panel.translation_sliders
                ),
                tuple(slider.value() for slider in panel.rotation_sliders),
                factor,
            )
        )
        panel.camera_view_changed.connect(self.viewer_3d.set_camera_view)
        panel.projection_changed.connect(
            self.viewer_3d.set_parallel_projection
        )
        panel.reset_requested.connect(self.viewer_3d.reset_transform)

        translations = (
            ("Alt+Left", 0, -10),
            ("Alt+Right", 0, 10),
            ("Alt+Down", 1, -10),
            ("Alt+Up", 1, 10),
            ("Alt+PageDown", 2, -10),
            ("Alt+PageUp", 2, 10),
        )

        def translation_shortcut(axis, step):
            return lambda: self._move_translation_slider(axis, step)

        for shortcut, axis, step in translations:
            action = QAction(self)
            action.setShortcut(shortcut)
            action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
            action.triggered.connect(translation_shortcut(axis, step))
            self.addAction(action)
            self._translation_actions.append(action)

    def _move_translation_slider(self, axis, step):
        slider = self.visualization_surface.transform_panel.translation_sliders[
            axis
        ]
        slider.setValue(slider.value() + step)

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
            self._update_antialiasing(
                self.antialiasing_checkbox.isChecked()
            )
            self._connect_transform_controls()
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
        QMessageBox.critical(self, "Falha na inicialização", message)
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
            self._current_dimension = dimension
            color_map = self.color_map_selector.currentData()
            if dimension == 2:
                self.visualization_surface.viewer_container.setCurrentWidget(
                    self.viewer_2d
                )
                self.viewer_2d.show_model(model, color_map)
            else:
                self.visualization_surface.viewer_container.setCurrentWidget(
                    self.viewer_3d
                )
                self.viewer_3d.show_model(model, color_map)
                self.viewer_3d.set_camera_view("isometric")
                self.viewer_3d.set_parallel_projection(False)
            self.visualization_surface.transform_panel.reset_controls()
            for action in self._translation_actions:
                action.setEnabled(dimension == 3)
            self.visualization_surface.set_model_dimension(dimension)

            info = (
                f"Arquivo: {Path(file_path).name}\n\n"
                f"Pontos (vértices): {statistics['points']}\n"
                f"Segmentos: {statistics['segments']}\n\n"
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

    def _update_color_map(self):
        if self.loader is None or self._current_dimension is None:
            return

        model = self.loader.get_model()
        color_map = self.color_map_selector.currentData()
        if self._current_dimension == 2:
            self.viewer_2d.show_model(model, color_map)
        else:
            self.viewer_3d.set_color_map(color_map)

    def _update_antialiasing(self, enabled):
        for viewer_name in ("viewer_2d", "viewer_3d"):
            viewer = getattr(self, viewer_name, None)
            if viewer is not None:
                viewer.set_antialiasing(enabled)

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
