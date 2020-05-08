import os, sys
import platform
import subprocess
import tempfile
from PyPDF2 import PdfFileMerger
import shutil

from PyQt5.QtWidgets import QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, \
    QListView, QListWidget, QFileDialog, QAbstractItemView, QMessageBox


class FileScanner:
    def __init__(self):
        self.supported_types = [".pdf"]

    def scan_files(self, dir_path):
        # pdf file search
        files = []
        for root, dirnames, filenames in os.walk(dir_path):
            for file in filenames:
                fname, fext = os.path.splitext(file)
                if fext.lower() in self.supported_types:
                    files.append(os.path.join(root, file))
        return files


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # build gui
        # the dir chooser
        dir_line_edit = QLineEdit()
        change_dir_button = QPushButton('Change Directory')
        change_dir_button.clicked.connect(self.change_dir_button_clicked)
        dir_chooser_layout = QHBoxLayout()
        dir_chooser_layout.addWidget(dir_line_edit)
        dir_chooser_layout.addWidget(change_dir_button)

        # the file_list
        self.file_list = QListWidget()
        self.file_list.setEnabled(False)
        self.file_list.itemSelectionChanged.connect(self.file_list_item_selection_changed)
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # the file_list_action_bar
        remove_file_button = QPushButton('Remove File')
        remove_file_button.clicked.connect(self.remove_file_button_clicked)
        self.move_up_button = QPushButton('Move Up')
        self.move_up_button.clicked.connect(self.move_up_button_clicked)
        self.move_down_button = QPushButton('Move Down')
        self.move_down_button.clicked.connect(self.move_down_button_clicked)
        file_list_action_bar_layout = QHBoxLayout()
        file_list_action_bar_layout.setContentsMargins(0, 0, 0, 0);
        file_list_action_bar_layout.addWidget(remove_file_button)
        file_list_action_bar_layout.addWidget(self.move_up_button)
        file_list_action_bar_layout.addWidget(self.move_down_button)
        self.file_list_action_bar_widget = QWidget()
        self.file_list_action_bar_widget.setLayout(file_list_action_bar_layout)
        self.file_list_action_bar_widget.setEnabled(False)

        # the output_file_chooser
        self.output_file_line_edit = QLineEdit()
        output_file_change_button = QPushButton('Change Output File')
        output_file_change_button.clicked.connect(self.output_file_change_button_clicked)
        output_file_layout = QHBoxLayout()
        output_file_layout.setContentsMargins(0, 0, 0, 0)
        output_file_layout.addWidget(self.output_file_line_edit)
        output_file_layout.addWidget(output_file_change_button)
        self.output_file_widget = QWidget()
        self.output_file_widget.setLayout(output_file_layout)
        self.output_file_widget.setEnabled(False)

        # run button
        self.merge_button = QPushButton('Merge Files')
        self.merge_button.setEnabled(False)
        self.merge_button.clicked.connect(self.merge_button_clicked)

        central_widget_layout = QVBoxLayout()
        central_widget_layout.addLayout(dir_chooser_layout)
        central_widget_layout.addWidget(self.file_list)
        central_widget_layout.addWidget(self.file_list_action_bar_widget)
        central_widget_layout.addWidget(self.output_file_widget)
        central_widget_layout.addWidget(self.merge_button)
        self.setLayout(central_widget_layout)

    def file_list_item_selection_changed(self):
        list_items = self.file_list.selectedItems()
        if not list_items:
            self.file_list_action_bar_widget.setEnabled(False)
        else:
            self.file_list_action_bar_widget.setEnabled(True)
            if len(list_items) > 1:
                self.move_down_button.setEnabled(False)
                self.move_up_button.setEnabled(False)
            else:
                self.move_down_button.setEnabled(True)
                self.move_up_button.setEnabled(True)

    def change_dir_button_clicked(self):
        self.file_list.clear()
        self.file_list.setEnabled(False)
        self.output_file_widget.setEnabled(False)
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            file_scanner = FileScanner()
            files = file_scanner.scan_files(dir)
            for file in files:
                self.file_list.addItem(file)
            if len(files) > 0:
                self.file_list.setEnabled(True)
                self.output_file_widget.setEnabled(True)

    def remove_file_button_clicked(self):
        list_items = self.file_list.selectedItems()
        if not list_items:
            return
        for item in list_items:
            self.file_list.takeItem(self.file_list.row(item))

    def move_up_button_clicked(self):
        list_items = self.file_list.selectedItems()
        if not list_items:
            return
        currentRow = self.file_list.currentRow()
        if currentRow == 0:
            self.file_list.setCurrentRow(currentRow)
            self.file_list.setFocus()
            return
        currentItem = self.file_list.takeItem(currentRow)
        self.file_list.insertItem(currentRow - 1, currentItem)
        # currentItem.setSelected(True)
        self.file_list.setCurrentRow(currentRow - 1)
        self.file_list.setFocus()

    def move_down_button_clicked(self):
        list_items = self.file_list.selectedItems()
        if not list_items:
            return
        currentRow = self.file_list.currentRow()
        if currentRow + 1 == self.file_list.count():
            self.file_list.setCurrentRow(currentRow)
            self.file_list.setFocus()
            return
        currentItem = self.file_list.takeItem(currentRow)
        self.file_list.insertItem(currentRow + 1, currentItem)
        self.file_list.setCurrentRow(currentRow + 1)
        # currentItem.setSelected(True)
        self.file_list.setFocus()

    def output_file_change_button_clicked(self):
        fileName = QFileDialog.getSaveFileName(self,
                                               self.tr("Export document to PDF"),
                                               "", self.tr("PDF files (*.pdf)"))[0]
        if fileName:
            self.output_file_line_edit.setText(fileName)
            self.merge_button.setEnabled(True)
        else:
            self.merge_button.setEnabled(False)

    def merge_button_clicked(self):
        list_items = []
        for index in range(0, self.file_list.count()):
            list_items.append(self.file_list.item(index))

        # collect files in temp folder
        tmp = tempfile.mkdtemp()
        tmp_files = []
        i = 1
        for item in list_items:
            file_path = item.text()
            _, file_ext = os.path.splitext(file_path)
            file_name = str(i).zfill(12)
            tmp_file_path = os.path.join(tmp, file_name + file_ext)
            # print("creating " + tmp_file_path)
            shutil.copy2(file_path, tmp_file_path)
            tmp_files.append(tmp_file_path)
            i = i + 1

        # do the merge
        merger = PdfFileMerger()

        for file in tmp_files:
            merger.append(file)
        output_file_path = self.output_file_line_edit.text()
        merger.write(output_file_path)
        merger.close()

        # clean up
        shutil.rmtree(tmp, ignore_errors=True)

        # show the success
        reply = QMessageBox.information(self, "PdfMerge", "PDF Creation successful!", QMessageBox.Ok | QMessageBox.Open)
        if reply == QMessageBox.Open:
            self.open_file(output_file_path)

    def open_file(self, filepath):
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(filepath)
        else:  # linux variants
            subprocess.call(('xdg-open', filepath))