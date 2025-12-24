import sys
import traceback
from PyQt5.QtWidgets import QApplication

try:
    from src.ui.controllers.main_controller import MainController

    def main():
        """ Start app func. """
        app = QApplication(sys.argv)
        MainController()
        sys.exit(app.exec_())

except Exception:
    with open("error.log", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    raise


if __name__ == "__main__":
    main()

