import json
import signal
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QApplication, QWidget

BASE_DIR = Path(__file__).parent
PETS_DIR = BASE_DIR / "pets"
DEFAULT_PET = "cat"
PIXEL = 8


def load_pet(pet_id):
    path = PETS_DIR / pet_id / "pet.json"
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    pixels = data["pixels"]
    width = len(pixels[0])
    for row in pixels:
        if len(row) != width:
            raise ValueError(f"{path}: Alle Zeilen müssen {width} Zeichen lang sein, gefunden: {row!r}")

    palette = {char: QColor(hex_code) for char, hex_code in data["palette"].items()}
    return data["name"], pixels, palette


class PetWindow(QWidget):
    def __init__(self, pet_id=DEFAULT_PET):
        super().__init__()
        self.name, self.pixels, self.palette = load_pet(pet_id)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle(self.name)

        width = len(self.pixels[0]) * PIXEL
        height = len(self.pixels) * PIXEL
        self.resize(width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        for y, row in enumerate(self.pixels):
            for x, char in enumerate(row):
                if char == ".":
                    continue
                painter.fillRect(x * PIXEL, y * PIXEL, PIXEL, PIXEL, self.palette[char])

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    pet_ids = sys.argv[1:] or [DEFAULT_PET]
    windows = []
    for index, pet_id in enumerate(pet_ids):
        window = PetWindow(pet_id)
        window.move(200 + index * 160, 200)
        window.show()
        windows.append(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()