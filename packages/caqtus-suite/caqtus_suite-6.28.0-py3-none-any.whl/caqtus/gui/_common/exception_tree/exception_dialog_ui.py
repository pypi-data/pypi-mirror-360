# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'exception_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFrame,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)


class Ui_ExceptionDialog(object):
    def setupUi(self, ExceptionDialog):
        if not ExceptionDialog.objectName():
            ExceptionDialog.setObjectName("ExceptionDialog")
        ExceptionDialog.resize(400, 300)
        self.verticalLayout = QVBoxLayout(ExceptionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.exception_label = QLabel(ExceptionDialog)
        self.exception_label.setObjectName("exception_label")

        self.verticalLayout.addWidget(self.exception_label)

        self.line = QFrame(ExceptionDialog)
        self.line.setObjectName("line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.exception_tree = QTreeWidget(ExceptionDialog)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, "1")
        self.exception_tree.setHeaderItem(__qtreewidgetitem)
        self.exception_tree.setObjectName("exception_tree")
        self.exception_tree.setHeaderHidden(True)

        self.verticalLayout.addWidget(self.exception_tree)

        self.buttonBox = QDialogButtonBox(ExceptionDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ExceptionDialog)
        self.buttonBox.accepted.connect(ExceptionDialog.accept)
        self.buttonBox.rejected.connect(ExceptionDialog.reject)

        QMetaObject.connectSlotsByName(ExceptionDialog)

    # setupUi

    def retranslateUi(self, ExceptionDialog):
        ExceptionDialog.setWindowTitle(
            QCoreApplication.translate("ExceptionDialog", "Dialog", None)
        )
        self.exception_label.setText(
            QCoreApplication.translate("ExceptionDialog", "An error occured", None)
        )

    # retranslateUi
