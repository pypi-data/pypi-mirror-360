PyJalaliDatePicker
A Jalali (Persian) date picker widget for PyQt5 applications.
Installation
pip install pyjalalidatepicker

Usage
from pyjalalidatepicker import JalaliDatePicker
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout
import sys

app = QApplication(sys.argv)
window = QDialog()
layout = QVBoxLayout(window)

date_picker = JalaliDatePicker()
layout.addWidget(date_picker)

window.setLayout(layout)
window.show()
sys.exit(app.exec_())

Features

Displays a Jalali calendar with Persian month and weekday names.
Highlights the current day in red and selected day in green.
Red-colored labels for Thursday and Friday.
Easy integration with PyQt5 applications.

Requirements

Python 3.6+
PyQt5>=5.15.0
jdatetime>=4.2.0

License
MIT License
