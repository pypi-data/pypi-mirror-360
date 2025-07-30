import sys
from PyQt5.QtWidgets import QApplication, QLineEdit, QDialog, QVBoxLayout, QGridLayout, QPushButton, QComboBox, \
    QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
import jdatetime


class JalaliCalendarDialog(QDialog):
    MONTH_NAMES = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    WEEK_DAYS = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تقویم جلالی")
        self.layout = QVBoxLayout(self)

        # انتخاب سال و ماه
        self.year_combo = QComboBox()
        current_jyear = jdatetime.date.today().year
        for year in range(current_jyear - 100, current_jyear + 10):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(current_jyear))

        self.month_combo = QComboBox()
        for i, month in enumerate(self.MONTH_NAMES, 1):
            self.month_combo.addItem(month, i)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("سال:"))
        selector_layout.addWidget(self.year_combo)
        selector_layout.addWidget(QLabel("ماه:"))
        selector_layout.addWidget(self.month_combo)
        self.layout.addLayout(selector_layout)

        # شبکه روزهای ماه
        self.days_grid = QGridLayout()
        self.layout.addLayout(self.days_grid)

        # دکمه Apply
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.accept)
        self.layout.addWidget(self.apply_button)

        # تنظیم تاریخ اولیه
        self.selected_date = jdatetime.date.today()
        self.month_combo.setCurrentIndex(self.selected_date.month - 1)
        self.update_calendar()

        # به‌روزرسانی تقویم هنگام تغییر سال یا ماه
        self.year_combo.currentTextChanged.connect(self.update_calendar)
        self.month_combo.currentIndexChanged.connect(self.update_calendar)

    def get_days_in_month(self, year, month):
        """محاسبه تعداد روزهای ماه بدون استفاده از daysinmonth"""
        try:
            jdatetime.date(year, month, 31)
            return 31
        except ValueError:
            try:
                jdatetime.date(year, month, 30)
                return 30
            except ValueError:
                return 29

    def update_calendar(self):
        """به‌روزرسانی نمایش روزهای ماه"""
        # پاک کردن شبکه قبلی
        for i in reversed(range(self.days_grid.count())):
            widget = self.days_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # افزودن سرستون‌های روزهای هفته
        for col, day_name in enumerate(self.WEEK_DAYS):
            label = QLabel(day_name)
            label.setAlignment(Qt.AlignCenter)
            # رنگ قرمز برای پنج‌شنبه و جمعه
            if day_name in ["جمعه"]:
                label.setStyleSheet("color: red;")
            self.days_grid.addWidget(label, 0, col)

        # محاسبه روزهای ماه
        year = int(self.year_combo.currentText())
        month = self.month_combo.currentIndex() + 1
        try:
            first_day = jdatetime.date(year, month, 1)
        except ValueError:
            first_day = jdatetime.date(year, month, 1)
            self.selected_date = first_day

        days_in_month = self.get_days_in_month(year, month)

        # محاسبه روز هفته برای اولین روز ماه
        gdate = first_day.togregorian()
        weekday = (gdate.weekday() + 2) % 7  # تبدیل به سیستم هفته ایرانی (شنبه = 0)

        # تاریخ امروز برای مقایسه
        today = jdatetime.date.today()

        # افزودن روزها به شبکه
        row = 1
        col = weekday
        for day in range(1, days_in_month + 1):
            btn = QPushButton(str(day))
            btn.setFixedSize(40, 40)
            # بررسی اگر روز جاری باشد
            if (day == today.day and month == today.month and year == today.year and
                    not (
                            day == self.selected_date.day and month == self.selected_date.month and year == self.selected_date.year)):
                btn.setStyleSheet("background-color: red; color: white;")
            # بررسی اگر روز انتخاب‌شده باشد
            if day == self.selected_date.day and month == self.selected_date.month and year == self.selected_date.year:
                btn.setStyleSheet("background-color: #4CAF50; color: white;")
            btn.clicked.connect(lambda _, d=day: self.select_day(d))
            self.days_grid.addWidget(btn, row, col)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def select_day(self, day):
        """انتخاب روز و به‌روزرسانی نمایش"""
        year = int(self.year_combo.currentText())
        month = self.month_combo.currentIndex() + 1
        try:
            self.selected_date = jdatetime.date(year, month, day)
        except ValueError:
            last_day = self.get_days_in_month(year, month)
            self.selected_date = jdatetime.date(year, month, last_day)
        self.update_calendar()

    def set_jalali_date(self, jdate):
        """تنظیم تاریخ جلالی"""
        self.selected_date = jdate
        self.year_combo.setCurrentText(str(jdate.year))
        self.month_combo.setCurrentIndex(jdate.month - 1)
        self.update_calendar()

    def get_jalali_date(self):
        """دریافت تاریخ جلالی انتخاب‌شده"""
        return self.selected_date


class JalaliDatePicker(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.set_jalali_date(jdatetime.date.today())
        self.mousePressEvent = self.show_calendar

    def set_jalali_date(self, jdate):
        """تنظیم تاریخ جلالی در ورودی"""
        self.setText(f"{jdate.year}/{jdate.month:02d}/{jdate.day:02d}")

    def get_jalali_date(self):
        """دریافت تاریخ جلالی از ورودی"""
        text = self.text()
        if text:
            year, month, day = map(int, text.split('/'))
            return jdatetime.date(year, month, day)
        return None

    def show_calendar(self, event):
        """نمایش فرم تقویم"""
        dialog = JalaliCalendarDialog(self)
        dialog.set_jalali_date(self.get_jalali_date())
        if dialog.exec_():
            selected_date = dialog.get_jalali_date()
            self.set_jalali_date(selected_date)
