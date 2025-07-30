import sys, pathlib
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtGui, QtCore
from dropclust.gui import gui 
from dropclust.utils import download_url_to_file

def confirm_prompt(question):
    reply = None
    while reply not in ("", "y", "n"):
        reply = input(f"{question} (y/n): ").lower()
    return (reply in ("", "y"))

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    app = QApplication(sys.argv)

    screen = app.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    pxr = screen.devicePixelRatio()
    size = screen.availableGeometry()
    clipboard = app.clipboard()

    icon_path = pathlib.Path.home().joinpath(".dropclust", "logo.png")
    
    if not icon_path.is_file():
        cp_dir = pathlib.Path.home().joinpath(".dropclust")
        cp_dir.mkdir(exist_ok=True)
        print("downloading logo")
        download_url_to_file(
            "https://gitlab.com/MeLlamoArroz/DropClustGUI/-/raw/master/logo.png",
            icon_path, progress=True)

    icon_path = str(icon_path.resolve())
    app_icon = QtGui.QIcon()
    app_icon.addFile(icon_path, QtCore.QSize(16, 16))
    app_icon.addFile(icon_path, QtCore.QSize(24, 24))
    app_icon.addFile(icon_path, QtCore.QSize(32, 32))
    app_icon.addFile(icon_path, QtCore.QSize(48, 48))
    app_icon.addFile(icon_path, QtCore.QSize(64, 64))
    app_icon.addFile(icon_path, QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)

    demo = gui.AppDemo(size, dpi, pxr, clipboard)
    demo.show()
    sys.exit(app.exec())
    
if __name__ == '__main__':
    main()

