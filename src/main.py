
import sys

from PySide6.QtWidgets import QApplication
from interface.main_window import MainWindow


app = QApplication(sys.argv)

window = MainWindow()
window.show()
window.center_on_primary_screen()

sys.exit(app.exec())
