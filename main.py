from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebKitWidgets import *
from PyQt5.QtPrintSupport import *

import os
import sys


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("PyBrowser")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        self.setLayout(layout)

        logo = QLabel()
        logo.setPixmap(QPixmap("img/application-browser.png"))

        layout.addWidget(title, alignment=Qt.AlignHCenter)
        layout.addWidget(logo, alignment=Qt.AlignHCenter)
        layout.addWidget(QLabel("Version 0.1 Lite"), alignment=Qt.AlignHCenter)
        layout.addWidget(QLabel("Copyright 2020 Yohan Maury"), alignment=Qt.AlignHCenter)
        layout.addWidget(self.buttonBox)


class Color(QWidget):
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("PyBrowser")
        self.setWindowIcon(QIcon("img/application-browser.png"))
        self.baseUrl = "https://www.google.com"

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)

        back_btn = QAction ( QIcon("img/arrow-back.png"), "Back", self)
        back_btn.setStatusTip("Back to the previous page")
        # back_btn.triggered.connect(self.browser.back)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back)
        navtb.addAction(back_btn)

        next_btn = QAction(QIcon("img/arrow-forward.png"), "Forward", self)
        next_btn.setStatusTip("Go to the next page")
        # next_btn.triggered.connect(self.browser.forward)
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward)
        navtb.addAction(next_btn)

        refresh_btn = QAction(QIcon("img/arrow-refresh.png"), "Refresh", self)
        refresh_btn.setStatusTip("Refresh the page")
        # refresh_btn.triggered.connect(self.browser.reload)
        refresh_btn.triggered.connect(lambda: self.tabs.currentWidget().reload)
        navtb.addAction(refresh_btn)

        home_btn = QAction(QIcon("img/home.png"), "Home", self)
        home_btn.setStatusTip("Return to the home page")
        home_btn.triggered.connect(self.redirect_to_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        screenshot_btn = QAction(QIcon("img/camera--arrow.png"), "Screenshot", self)
        screenshot_btn.setStatusTip("Take a screenshot")
        navtb.addAction(screenshot_btn)

        navtb.addSeparator()

        self.httpsicon = QLabel() # Yes, really!
        navtb.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(QIcon("img/control-stop.png"), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop)
        navtb.addAction(stop_btn)

        self.menuBar().setNativeMenuBar(False)

        file_menu = self.menuBar().addMenu("&File")

        new_tab_action = QAction( QIcon("img/ui-tab--plus.png"), "New Tab", self)
        new_tab_action.setStatusTip("Open a new tab")
        new_tab_action.triggered.connect(lambda x: self.add_new_tab)
        file_menu.addAction(new_tab_action)

        open_file_action = QAction( QIcon("img/disk--arrow.png"), "Open file...", self)
        open_file_action.setStatusTip("Open from file")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction(QIcon("img/disk--pencil.png"), "Save page as...", self)
        save_file_action.setStatusTip("Save page as...")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)

        print_action = QAction( QIcon("img/printer.png"), "Print...", self)
        print_action.setStatusTip("Print current page")
        print_action.setShortcut(QKeySequence("Ctrl+P"))
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)

        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction(QIcon("img/question-button.png"), "About PyBrowser", self)
        about_action.setStatusTip("About this browser")
        about_action.setShortcut(QKeySequence("Ctrl+H"))
        about_action.triggered.connect(self.about_page)
        help_menu.addAction(about_action)

        # tools_menu = self.menuBar().addMenu("&Tools")
        # screenshot_action = QAction(QIcon("img/camera--arrow.png"), "Take screenshot", self)
        # screenshot_action.setStatusTip("Take a screenshot")
        # screenshot_action.setShortcut(QKeySequence("Ctrl+W"))
        # screenshot_action.triggered.connect(self.take_screenshot)
        # tools_menu.addAction(screenshot_action)

        self.add_new_tab(QUrl("https://www.google.com"), "Homepage")

        self.show()

    def add_new_tab(self, qurl=None, label="Blank"):

        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().mainFrame().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())

    def close_current_tab(self, i):
        print(i)
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self,
                                                  "Open file",
                                                  "",
                                                  "Hypertext Markup Language (*.htm *.html);;",
                                                  "All files (*.*)")
        if filename:
            with open(filename, 'r') as f:
                html = f.read()
            self.tabs.currentWidget().setHtml(html)
            self.urlbar.setText(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self,
                                                                  "Save Page As",
                                                                  "",
                                                                  "Hypertext Markup Language (*.htm *.html);;",
                                                                  "All files (*.*)")
        if filename:
            html = self.tabs.currentWidget().page().mainFrame().toHtml()
            with open(filename, 'w') as f:
                f.write(html.encode('utf8'))

    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.tabs.currentWidget().print_)
        dlg.exec_()

    def about_page(self):
        dlg = AboutDialog()
        dlg.exec_()

    def redirect_to_home(self):
        self.tabs.currentWidget().setUrl(QUrl(self.baseUrl))
        # self.browser.setUrl(QUrl(self.baseUrl))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
            self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore it!
            return

        if q.scheme() == 'https':
            # Secure padlock icon
            self.httpsicon.setPixmap(QPixmap(QPixmap("img/lock-https.png")))
        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(QPixmap(QPixmap("img/lock-http.png")))
        self.urlbar.setText( q.toString() )
        self.urlbar.setCursorPosition(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("PyBrowser")
    app.setOrganizationName("PyBrowser")
    app.setOrganizationDomain("pybrowser.org")

    window = MainWindow()
    window.show()  # Affiche la fenetre !

    app.exec_()
