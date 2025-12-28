# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GUIehadqY.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QPlainTextEdit, QPushButton, QRadioButton, QScrollArea,
    QSizePolicy, QSpacerItem, QStatusBar, QTabWidget,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1689, 998)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.Computer))
        MainWindow.setWindowIcon(icon)
        self.actionhelp = QAction(MainWindow)
        self.actionhelp.setObjectName(u"actionhelp")
        self.actionupdate = QAction(MainWindow)
        self.actionupdate.setObjectName(u"actionupdate")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_8 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.frame_5 = QFrame(self.centralwidget)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setAcceptDrops(True)
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.groupBox = QGroupBox(self.frame_5)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setAcceptDrops(True)
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tabWidget = QTabWidget(self.groupBox)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setAcceptDrops(True)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_4 = QHBoxLayout(self.tab)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.scrollArea_2 = QScrollArea(self.tab)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 656, 307))
        self.horizontalLayout_3 = QHBoxLayout(self.scrollAreaWidgetContents_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.listWidget_files = QListWidget(self.scrollAreaWidgetContents_2)
        self.listWidget_files.setObjectName(u"listWidget_files")
        self.listWidget_files.setAcceptDrops(True)

        self.horizontalLayout_3.addWidget(self.listWidget_files)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.horizontalLayout_4.addWidget(self.scrollArea_2)

        self.frame_2 = QFrame(self.tab)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.pushButton_import = QPushButton(self.frame_2)
        self.pushButton_import.setObjectName(u"pushButton_import")

        self.verticalLayout_2.addWidget(self.pushButton_import)

        self.pushButton_remove = QPushButton(self.frame_2)
        self.pushButton_remove.setObjectName(u"pushButton_remove")

        self.verticalLayout_2.addWidget(self.pushButton_remove)

        self.verticalSpacer_2 = QSpacerItem(20, 222, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout_4.addWidget(self.frame_2)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.horizontalLayout = QHBoxLayout(self.tab_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout_4.addWidget(self.tabWidget)

        self.horizontalSpacer = QSpacerItem(415, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.verticalLayout_4.addItem(self.horizontalSpacer)

        self.frame_6 = QFrame(self.groupBox)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.plainTextEdit_query = QPlainTextEdit(self.frame_6)
        self.plainTextEdit_query.setObjectName(u"plainTextEdit_query")

        self.horizontalLayout_6.addWidget(self.plainTextEdit_query)

        self.scrollArea_3 = QScrollArea(self.frame_6)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 382, 330))
        self.horizontalLayout_9 = QHBoxLayout(self.scrollAreaWidgetContents_3)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.groupBox_3 = QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout_10 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.textBrowser_log = QTextBrowser(self.groupBox_3)
        self.textBrowser_log.setObjectName(u"textBrowser_log")

        self.horizontalLayout_10.addWidget(self.textBrowser_log)


        self.horizontalLayout_9.addWidget(self.groupBox_3)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)

        self.horizontalLayout_6.addWidget(self.scrollArea_3)


        self.verticalLayout_4.addWidget(self.frame_6)

        self.pushButton_analyse = QPushButton(self.groupBox)
        self.pushButton_analyse.setObjectName(u"pushButton_analyse")

        self.verticalLayout_4.addWidget(self.pushButton_analyse)

        self.groupBox_4 = QGroupBox(self.groupBox)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout = QGridLayout(self.groupBox_4)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_test_api = QPushButton(self.groupBox_4)
        self.pushButton_test_api.setObjectName(u"pushButton_test_api")

        self.gridLayout.addWidget(self.pushButton_test_api, 2, 3, 1, 1)

        self.label_2 = QLabel(self.groupBox_4)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox_4)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lineEdit_key = QLineEdit(self.groupBox_4)
        self.lineEdit_key.setObjectName(u"lineEdit_key")

        self.gridLayout.addWidget(self.lineEdit_key, 2, 2, 1, 1)

        self.label_3 = QLabel(self.groupBox_4)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        self.lineEdit_baseurl = QLineEdit(self.groupBox_4)
        self.lineEdit_baseurl.setObjectName(u"lineEdit_baseurl")

        self.gridLayout.addWidget(self.lineEdit_baseurl, 2, 0, 1, 1)

        self.lineEdit_model = QLineEdit(self.groupBox_4)
        self.lineEdit_model.setObjectName(u"lineEdit_model")

        self.gridLayout.addWidget(self.lineEdit_model, 2, 1, 1, 1)

        self.pushButton_save_api = QPushButton(self.groupBox_4)
        self.pushButton_save_api.setObjectName(u"pushButton_save_api")

        self.gridLayout.addWidget(self.pushButton_save_api, 2, 4, 1, 1)


        self.verticalLayout_4.addWidget(self.groupBox_4)


        self.horizontalLayout_7.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.frame_5)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.plainTextEdit_code = QPlainTextEdit(self.groupBox_2)
        self.plainTextEdit_code.setObjectName(u"plainTextEdit_code")

        self.verticalLayout_5.addWidget(self.plainTextEdit_code)

        self.frame_4 = QFrame(self.groupBox_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalSpacer_2 = QSpacerItem(656, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_2)

        self.pushButton_run_code = QPushButton(self.frame_4)
        self.pushButton_run_code.setObjectName(u"pushButton_run_code")

        self.horizontalLayout_11.addWidget(self.pushButton_run_code)


        self.verticalLayout_5.addWidget(self.frame_4)

        self.radioButton_edit_code = QRadioButton(self.groupBox_2)
        self.radioButton_edit_code.setObjectName(u"radioButton_edit_code")
        self.radioButton_edit_code.setChecked(False)

        self.verticalLayout_5.addWidget(self.radioButton_edit_code)

        self.frame_edit_code = QFrame(self.groupBox_2)
        self.frame_edit_code.setObjectName(u"frame_edit_code")
        self.frame_edit_code.setEnabled(True)
        self.frame_edit_code.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_edit_code.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_edit_code)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.plainTextEdit_edit_query = QPlainTextEdit(self.frame_edit_code)
        self.plainTextEdit_edit_query.setObjectName(u"plainTextEdit_edit_query")

        self.verticalLayout_3.addWidget(self.plainTextEdit_edit_query)

        self.frame_3 = QFrame(self.frame_edit_code)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.pushButton_send_edit_query = QPushButton(self.frame_3)
        self.pushButton_send_edit_query.setObjectName(u"pushButton_send_edit_query")

        self.horizontalLayout_5.addWidget(self.pushButton_send_edit_query)


        self.verticalLayout_3.addWidget(self.frame_3)


        self.verticalLayout_5.addWidget(self.frame_edit_code)


        self.horizontalLayout_7.addWidget(self.groupBox_2)


        self.horizontalLayout_8.addWidget(self.frame_5)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1689, 33))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.actionhelp)
        self.menu.addAction(self.actionupdate)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"DumbDrawPhD", None))
        self.actionhelp.setText(QCoreApplication.translate("MainWindow", u"help", None))
        self.actionupdate.setText(QCoreApplication.translate("MainWindow", u"update", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u6570\u636e\u8f93\u5165", None))
        self.pushButton_import.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u5165\u6587\u4ef6", None))
        self.pushButton_remove.setText(QCoreApplication.translate("MainWindow", u"\u79fb\u9664\u9009\u4e2d\u6587\u4ef6", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"\u4f20\u5165\u6570\u636e\u6587\u4ef6", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), "")
        self.plainTextEdit_query.setPlainText(QCoreApplication.translate("MainWindow", u"1. \u7b80\u8981\u63cf\u8ff0\u4f60\u4f20\u5165\u7684\u6587\u4ef6\u5206\u522b\u662f\u4ec0\u4e48\uff0c\u82e5\u662f\u8868\u683c\uff0c\u52a1\u5fc5\u63cf\u8ff0\u6e05\u695a\u884c\u540d\u4e0e\u5217\u540d\uff0c\u4ee5\u53ca\u6570\u636e\u9700\u8981\u5173\u6ce8\u54ea\u4e9b\u884c\u5217\u3002\n"
"\n"
"\n"
"2. \u63cf\u8ff0\u4f60\u7684\u7ed8\u56fe\u9700\u6c42\uff0c\u4f8b\u5982\u505aT\u68c0\u9a8c\uff0c\u753b\u51fa\u5206\u5e03\u56fe\uff0c\u7b49\u9ad8\u7ebf\u56fe\uff0c\u6563\u70b9\u56fe\uff0c\u70ed\u56fe\u7b49\u3002\u4ee5\u53ca\u56fe\u7247\u5927\u5c0f\uff0cdpi\uff0c\u4fdd\u5b58\u4f4d\u7f6e", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Log", None))
        self.pushButton_analyse.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u5206\u6790", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"AI API\u4fe1\u606f", None))
        self.pushButton_test_api.setText(QCoreApplication.translate("MainWindow", u"\u6d4b\u8bd5", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"model", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Base url", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"API-Key", None))
        self.pushButton_save_api.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u4ee3\u7801\u9884\u89c8", None))
        self.pushButton_run_code.setText(QCoreApplication.translate("MainWindow", u"\u76f4\u63a5\u8fd0\u884c\u6b64\u5904\u4ee3\u7801", None))
        self.radioButton_edit_code.setText(QCoreApplication.translate("MainWindow", u"\u4fee\u6539\u4ee3\u7801", None))
        self.plainTextEdit_edit_query.setPlainText(QCoreApplication.translate("MainWindow", u"\u63cf\u8ff0\u4f60\u8981\u4fee\u6539\u7684\u8981\u6c42", None))
        self.pushButton_send_edit_query.setText(QCoreApplication.translate("MainWindow", u"\u4fee\u6539\u4ee3\u7801", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e\u672c\u8f6f\u4ef6", None))
    # retranslateUi

