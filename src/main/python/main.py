import qdarkstyle
from PyQt5.QtWidgets import QMainWindow
from fbs_runtime.application_context.PyQt5 import ApplicationContext

import sys
import api

if __name__ == '__main__':
    # 1. Instantiate ApplicationContext
    app_context = ApplicationContext()

    # qmainwindow
    version = app_context.build_settings['version']
    app_name = app_context.build_settings['app_name']
    window_title = app_name + " v" + version
    window = QMainWindow()
    window.setWindowTitle(window_title)
    window.setCentralWidget(api.CentralWidget())
    window.resize(800, 600)
    # window.showMaximized()
    window.show()

    # run
    # app_context.app.setStyleSheet(qdarkstyle.load_stylesheet())
    exit_code = app_context.app.exec_()  # 2. Invoke app_context.app.exec_()
    sys.exit(exit_code)
