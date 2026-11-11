from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class TransformPanel(QFrame):
    close_requested = Signal()
    translation_changed = Signal(float, float, float)
    rotation_changed = Signal(float, float, float)
    scale_changed = Signal(float)
    camera_view_changed = Signal(str)
    projection_changed = Signal(bool)
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("transformPanel")
        self.setMinimumWidth(230)
        self.setStyleSheet("""
            QFrame#transformPanel { background: #ffffff; }
            QLabel { color: #23344d; }
            QLabel#panelTitle { font-size: 19px; font-weight: 700; }
            QLabel#moduleHeading {
                color: #65C8C0;
                font-size: 15px;
                font-weight: 700;
            }
            QLabel#mutedText { color: #B8C7D3; }
            QFrame#moduleCard {
                background: #f7f9fc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            QPushButton {
                min-height: 34px;
                padding: 0 10px;
                border: 1px solid #d5deea;
                border-radius: 7px;
                background: #ffffff;
                color: #23344d;
            }
            QPushButton:hover { background: #edf4fb; }
            QPushButton#primaryButton {
                background: #1769aa;
                border: none;
                color: #ffffff;
                font-weight: 600;
            }
            QPushButton#primaryButton:hover { background: #12588f; }
            QSlider::groove:horizontal {
                height: 6px;
                background: #dce3ed;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                margin: -5px 0;
                background: #1769aa;
                border-radius: 8px;
            }
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(
            "background: #f5f8fc; border-bottom: 1px solid #e2e8f0;"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 12, 12, 12)
        title = QLabel("Transformar cena")
        title.setObjectName("panelTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.close_requested)
        header_layout.addWidget(close_button)
        root_layout.addWidget(header)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 20)
        layout.setSpacing(14)

        layout.addWidget(self._section_heading("Translação"))
        translation_hint = QLabel(
            "Deslocamento em porcentagem do tamanho do modelo."
        )
        translation_hint.setObjectName("mutedText")
        translation_hint.setWordWrap(True)
        layout.addWidget(translation_hint)
        (
            translation_card,
            translation_sliders,
            self._translation_value_labels,
        ) = self._slider_card(
            [
                ("X", -100, 100, 0, "%"),
                ("Y", -100, 100, 0, "%"),
                ("Z", -100, 100, 0, "%"),
            ]
        )
        self.translation_sliders = translation_sliders
        for slider in translation_sliders:
            slider.valueChanged.connect(self._emit_translation)
        layout.addWidget(translation_card)

        layout.addWidget(self._section_heading("Rotação"))
        (
            rotation_card,
            rotation_sliders,
            self._rotation_value_labels,
        ) = self._slider_card(
            [
                ("X", -180, 180, 0, "°"),
                ("Y", -180, 180, 0, "°"),
                ("Z", -180, 180, 0, "°"),
            ]
        )
        self.rotation_sliders = rotation_sliders
        for slider in rotation_sliders:
            slider.valueChanged.connect(self._emit_rotation)
        layout.addWidget(rotation_card)

        layout.addWidget(self._section_heading("Escala"))
        scale_card, scale_sliders, scale_value_labels = self._slider_card(
            [("Tamaño", 10, 300, 100, "%")]
        )
        self.scale_slider = scale_sliders[0]
        self._scale_value_label = scale_value_labels[0]
        self.scale_slider.valueChanged.connect(self._emit_scale)
        layout.addWidget(scale_card)

        layout.addWidget(self._section_heading("Câmera"))
        camera_card = self._card()
        camera_layout = QVBoxLayout(camera_card)
        camera_layout.setContentsMargins(12, 10, 12, 10)
        camera_layout.setSpacing(6)
        self.camera_slider = QSlider(Qt.Orientation.Horizontal)
        self.camera_slider.setRange(0, 3)
        self.camera_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.camera_slider.setTickInterval(1)
        self.camera_slider.setToolTip("Deslize para selecionar uma vista")
        self.camera_label = QLabel("Isométrica")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        camera_layout.addWidget(self.camera_label)
        camera_layout.addWidget(self.camera_slider)
        self._camera_views = (
            ("isometric", "Isométrica"),
            ("top", "Superior"),
            ("front", "Frontal"),
            ("side", "Lateral"),
        )
        self._camera_view_names = ("isometric", "top", "front", "side")
        self.camera_slider.valueChanged.connect(self._set_camera_view)
        layout.addWidget(camera_card)

        projection_card = self._card()
        projection_layout = QVBoxLayout(projection_card)
        projection_layout.setContentsMargins(12, 10, 12, 10)
        projection_layout.setSpacing(6)
        self.projection_checkbox = QCheckBox("Projeção ortográfica")
        self.projection_checkbox.toggled.connect(self.projection_changed)
        projection_layout.addWidget(self.projection_checkbox)
        layout.addWidget(projection_card)

        self.reset_button = QPushButton("Restaurar transformações")
        self.reset_button.setObjectName("primaryButton")
        self.reset_button.clicked.connect(self.reset_requested)
        self.reset_button.clicked.connect(self.reset_transform_sliders)
        layout.addWidget(self.reset_button)
        layout.addStretch()

        scroll_area.setWidget(content)
        root_layout.addWidget(scroll_area, stretch=1)

    @staticmethod
    def _section_heading(text):
        heading = QLabel(text)
        heading.setObjectName("moduleHeading")
        return heading

    @staticmethod
    def _card():
        card = QFrame()
        card.setObjectName("moduleCard")
        return card

    def _slider_card(self, definitions):
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        sliders = []
        value_labels = []
        for label, minimum, maximum, initial, unit in definitions:
            row = QHBoxLayout()
            name = QLabel(label)
            name.setMinimumWidth(26)
            value_label = QLabel(f"{initial}{unit}")
            value_label.setMinimumWidth(48)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(minimum, maximum)
            slider.setValue(initial)
            slider.setSingleStep(1)
            slider.setPageStep(10)
            slider.valueChanged.connect(
                lambda value, target=value_label, suffix=unit:
                    target.setText(f"{value}{suffix}")
            )
            row.addWidget(name)
            row.addWidget(slider, stretch=1)
            row.addWidget(value_label)
            layout.addLayout(row)
            sliders.append(slider)
            value_labels.append(value_label)
        return card, sliders, value_labels

    def _emit_translation(self):
        self.translation_changed.emit(
            *(slider.value() / 100 for slider in self.translation_sliders)
        )

    def _emit_rotation(self):
        self.rotation_changed.emit(
            *(float(slider.value()) for slider in self.rotation_sliders)
        )

    def _emit_scale(self, value):
        self._scale_value_label.setText(f"{value}%")
        self.scale_changed.emit(value / 100)

    def _set_camera_view(self, index):
        view, label = self._camera_views[index]
        self.camera_label.setText(label)
        self.camera_view_changed.emit(view)

    def reset_controls(self):
        self.reset_transform_sliders()
        self.camera_slider.blockSignals(True)
        self.camera_slider.setValue(0)
        self.camera_slider.blockSignals(False)
        self.camera_label.setText("Isométrica")
        self.projection_checkbox.blockSignals(True)
        self.projection_checkbox.setChecked(False)
        self.projection_checkbox.blockSignals(False)

    def reset_transform_sliders(self):
        for slider in self.translation_sliders + self.rotation_sliders:
            slider.blockSignals(True)
            slider.setValue(0)
            slider.blockSignals(False)
        for value_label in self._translation_value_labels:
            value_label.setText("0%")
        for value_label in self._rotation_value_labels:
            value_label.setText("0°")
        self.scale_slider.blockSignals(True)
        self.scale_slider.setValue(100)
        self.scale_slider.blockSignals(False)
        self._scale_value_label.setText("100%")

    def set_camera_view(self, view):
        if view not in self._camera_view_names:
            raise ValueError(f"Vista de câmera não suportada: {view}")
        self.camera_slider.setValue(self._camera_view_names.index(view))
