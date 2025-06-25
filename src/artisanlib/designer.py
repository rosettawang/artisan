#
# ABOUT
# Artisan Designer Dialogs

# LICENSE
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

# AUTHOR
# Marko Luther, 2023

from typing import Optional, List, Tuple, TYPE_CHECKING

from artisanlib.util import stringfromseconds, stringtoseconds
from artisanlib.dialogs import ArtisanDialog

try:
    from PyQt6.QtCore import Qt, pyqtSlot, QRegularExpression, QSettings # @UnusedImport @Reimport  @UnresolvedImport
    from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator # @UnusedImport @Reimport  @UnresolvedImport
    from PyQt6.QtWidgets import (QApplication, QLabel, # @UnusedImport @Reimport  @UnresolvedImport
        QComboBox, QHBoxLayout, QVBoxLayout, QCheckBox, QDialogButtonBox, QGridLayout, # @UnusedImport @Reimport  @UnresolvedImport
        QGroupBox, QLineEdit, QMessageBox, QLayout) # @UnusedImport @Reimport  @UnresolvedImport
except ImportError:
    from PyQt5.QtCore import Qt, pyqtSlot, QRegularExpression, QSettings # type: ignore # @UnusedImport @Reimport  @UnresolvedImport
    from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator # type: ignore # @UnusedImport @Reimport  @UnresolvedImport
    from PyQt5.QtWidgets import (QApplication, QLabel, # type: ignore # @UnusedImport @Reimport  @UnresolvedImport
        QComboBox, QHBoxLayout, QVBoxLayout, QCheckBox, QDialogButtonBox, QGridLayout, # @UnusedImport @Reimport  @UnresolvedImport
        QGroupBox, QLineEdit, QMessageBox, QLayout) # @UnusedImport @Reimport  @UnresolvedImport

if TYPE_CHECKING:
    from artisanlib.main import ApplicationWindow # noqa: F401 # pylint: disable=unused-import
    from PyQt6.QtWidgets import QWidget, QPushButton # pylint: disable=unused-import

#########################################################################
#############  DESIGNER CONFIG DIALOG ###################################
#########################################################################

class designerconfigDlg(ArtisanDialog):
    def __init__(self, parent:'QWidget', aw:'ApplicationWindow') -> None:
        super().__init__(parent, aw)
        self.setWindowTitle(QApplication.translate('Form Caption','Designer Config'))
        self.setModal(True)

        #landmarks
        charge = QLabel(QApplication.translate('Label', 'CHARGE'))
        charge.setAlignment(Qt.AlignmentFlag.AlignRight)
        charge.setStyleSheet('background-color: #f07800')
        self.dryend = QCheckBox(QApplication.translate('CheckBox','DRY END'))
        self.dryend.setStyleSheet('background-color: orange')
        self.fcs = QCheckBox(QApplication.translate('CheckBox','FC START'))
        self.fcs.setStyleSheet('background-color: orange')
        self.fce = QCheckBox(QApplication.translate('CheckBox','FC END'))
        self.fce.setStyleSheet('background-color: orange')
        self.scs = QCheckBox(QApplication.translate('CheckBox','SC START'))
        self.scs.setStyleSheet('background-color: orange')
        self.sce = QCheckBox(QApplication.translate('CheckBox','SC END'))
        self.sce.setStyleSheet('background-color: orange')
        drop = QLabel(QApplication.translate('Label', 'DROP'))
        drop.setAlignment(Qt.AlignmentFlag.AlignRight)
        drop.setStyleSheet('background-color: #f07800')
        self.loadconfigflags()
        self.dryend.clicked.connect(self.changeflags)
        self.fcs.clicked.connect(self.changeflags)
        self.fce.clicked.connect(self.changeflags)
        self.scs.clicked.connect(self.changeflags)
        self.sce.clicked.connect(self.changeflags)
        if self.aw.qmc.timeindex[0] != -1:
            start = self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
        else:
            start = 0
        markersettinglabel = QLabel(QApplication.translate('Label', 'Marker'))
        markersettinglabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timesettinglabel = QLabel(QApplication.translate('Label', 'Time'))
        timesettinglabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btsettinglabel = QLabel(QApplication.translate('Label', 'BT'))
        btsettinglabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        etsettinglabel = QLabel(QApplication.translate('Label', 'ET'))
        etsettinglabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Edit0 = QLineEdit(stringfromseconds(0))

        self.Edit0.setEnabled(False)
        self.Edit0bt = QLineEdit(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[0]]:.1f}')
        self.Edit0et = QLineEdit(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[0]]:.1f}')
        self.Edit0.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit0bt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit0et.setAlignment(Qt.AlignmentFlag.AlignRight)
        if self.aw.qmc.timeindex[1]:
            self.Edit1 = QLineEdit(stringfromseconds(self.aw.qmc.timex[self.aw.qmc.timeindex[1]] - start))
            self.Edit1bt = QLineEdit(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[1]]:.1f}')
            self.Edit1et = QLineEdit(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[1]]:.1f}')
        else:
            self.Edit1 = QLineEdit(stringfromseconds(0))
            self.Edit1bt = QLineEdit('0.0')
            self.Edit1et = QLineEdit('0.0')
        self.Edit1.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit1bt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit1et.setAlignment(Qt.AlignmentFlag.AlignRight)
        if self.aw.qmc.timeindex[2]:
            self.Edit2 = QLineEdit(stringfromseconds(self.aw.qmc.timex[self.aw.qmc.timeindex[2]] - start))
            self.Edit2bt = QLineEdit(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[2]]:.1f}')
            self.Edit2et = QLineEdit(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[2]]:.1f}')
        else:
            self.Edit2 = QLineEdit(stringfromseconds(0))
            self.Edit2bt = QLineEdit('0.0')
            self.Edit2et = QLineEdit('0.0')
        self.Edit2.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit2bt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit2et.setAlignment(Qt.AlignmentFlag.AlignRight)
        if self.aw.qmc.timeindex[3]:
            self.Edit3 = QLineEdit(stringfromseconds(self.aw.qmc.timex[self.aw.qmc.timeindex[3]] - start))
            self.Edit3bt = QLineEdit(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[3]]:.1f}')
            self.Edit3et = QLineEdit(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[3]]:.1f}')
        else:
            self.Edit3 = QLineEdit(stringfromseconds(0))
            self.Edit3bt = QLineEdit('0.0')
            self.Edit3et = QLineEdit('0.0')
        self.Edit3.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit3bt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit3et.setAlignment(Qt.AlignmentFlag.AlignRight)
        if self.aw.qmc.timeindex[4]:
            self.Edit4 = QLineEdit(stringfromseconds(self.aw.qmc.timex[self.aw.qmc.timeindex[4]] - start))
            self.Edit4bt = QLineEdit(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[4]]:.1f}')
            self.Edit4et = QLineEdit(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[4]]:.1f}')
        else:
            self.Edit4 = QLineEdit(stringfromseconds(0))
            self.Edit4bt = QLineEdit('0.0')
            self.Edit4et = QLineEdit('0.0')
        self.Edit4.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit4bt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit4et.setAlignment(Qt.AlignmentFlag.AlignRight)
        if self.aw.qmc.timeindex[5]:
            self.Edit5 = QLineEdit(stringfromseconds(self.aw.qmc.timex[self.aw.qmc.timeindex[5]] - start))
            self.Edit5bt = QLineEdit(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[5]]:.1f}')
            self.Edit5et = QLineEdit(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[5]]:.1f}')
        else:
            self.Edit5 = QLineEdit(stringfromseconds(0))
            self.Edit5bt = QLineEdit('0.0')
            self.Edit5et = QLineEdit('0.0')
        self.Edit5.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit5bt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit5et.setAlignment(Qt.AlignmentFlag.AlignRight)
        if self.aw.qmc.timeindex[6]:
            self.Edit6 = QLineEdit(stringfromseconds(self.aw.qmc.timex[self.aw.qmc.timeindex[6]] - start))
            self.Edit6bt = QLineEdit(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[6]]:.1f}')
            self.Edit6et = QLineEdit(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[6]]:.1f}')
        else:
            self.Edit6 = QLineEdit(stringfromseconds(0))
            self.Edit6bt = QLineEdit('0.0')
            self.Edit6et = QLineEdit('0.0')
        self.Edit6.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit6bt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.Edit6et.setAlignment(Qt.AlignmentFlag.AlignRight)
        maxwidth = 70
        self.Edit0.setMaximumWidth(maxwidth)
        self.Edit1.setMaximumWidth(maxwidth)
        self.Edit2.setMaximumWidth(maxwidth)
        self.Edit3.setMaximumWidth(maxwidth)
        self.Edit4.setMaximumWidth(maxwidth)
        self.Edit5.setMaximumWidth(maxwidth)
        self.Edit6.setMaximumWidth(maxwidth)
        self.Edit0bt.setMaximumWidth(maxwidth)
        self.Edit1bt.setMaximumWidth(maxwidth)
        self.Edit2bt.setMaximumWidth(maxwidth)
        self.Edit3bt.setMaximumWidth(maxwidth)
        self.Edit4bt.setMaximumWidth(maxwidth)
        self.Edit5bt.setMaximumWidth(maxwidth)
        self.Edit6bt.setMaximumWidth(maxwidth)
        self.Edit0et.setMaximumWidth(maxwidth)
        self.Edit1et.setMaximumWidth(maxwidth)
        self.Edit2et.setMaximumWidth(maxwidth)
        self.Edit3et.setMaximumWidth(maxwidth)
        self.Edit4et.setMaximumWidth(maxwidth)
        self.Edit5et.setMaximumWidth(maxwidth)
        self.Edit6et.setMaximumWidth(maxwidth)
        self.Edit1copy = self.Edit1.text()
        self.Edit2copy = self.Edit2.text()
        self.Edit3copy = self.Edit3.text()
        self.Edit4copy = self.Edit4.text()
        self.Edit5copy = self.Edit5.text()
        self.Edit6copy = self.Edit6.text()
        self.Edit0btcopy = self.Edit0bt.text()
        self.Edit1btcopy = self.Edit1bt.text()
        self.Edit2btcopy = self.Edit2bt.text()
        self.Edit3btcopy = self.Edit3bt.text()
        self.Edit4btcopy = self.Edit4bt.text()
        self.Edit5btcopy = self.Edit5bt.text()
        self.Edit6btcopy = self.Edit6bt.text()
        self.Edit0etcopy = self.Edit0et.text()
        self.Edit1etcopy = self.Edit1et.text()
        self.Edit2etcopy = self.Edit2et.text()
        self.Edit3etcopy = self.Edit3et.text()
        self.Edit4etcopy = self.Edit4et.text()
        self.Edit5etcopy = self.Edit5et.text()
        self.Edit6etcopy = self.Edit6et.text()
#        regextime = QRegularExpression(r'^-?[0-9]?[0-9]?[0-9]:[0-5][0-9]$')
        regextime = QRegularExpression(r'^[0-9]?[0-9]:[0-5][0-9]$')
        self.Edit0.setValidator(QRegularExpressionValidator(regextime,self))
        self.Edit1.setValidator(QRegularExpressionValidator(regextime,self))
        self.Edit2.setValidator(QRegularExpressionValidator(regextime,self))
        self.Edit3.setValidator(QRegularExpressionValidator(regextime,self))
        self.Edit4.setValidator(QRegularExpressionValidator(regextime,self))
        self.Edit5.setValidator(QRegularExpressionValidator(regextime,self))
        self.Edit6.setValidator(QRegularExpressionValidator(regextime,self))
        regextemp = QRegularExpression(r'^[0-9]?[0-9]?[0-9]?\.?[0-9]$')
        self.Edit0bt.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit1bt.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit2bt.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit3bt.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit4bt.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit5bt.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit6bt.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit0et.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit1et.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit2et.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit3et.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit4et.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit5et.setValidator(QRegularExpressionValidator(regextemp,self))
        self.Edit6et.setValidator(QRegularExpressionValidator(regextemp,self))
        curvinesslabel = QLabel(QApplication.translate('Label', 'Curviness'))
        etcurviness = QLabel(QApplication.translate('Label', 'ET'))
        btcurviness = QLabel(QApplication.translate('Label', 'BT'))
        etcurviness.setAlignment(Qt.AlignmentFlag.AlignRight)
        btcurviness.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.ETsplineComboBox = QComboBox()
        self.ETsplineComboBox.addItems(['1','2','3','4','5'])
        self.ETsplineComboBox.setCurrentIndex(self.aw.qmc.ETsplinedegree - 1)
        self.ETsplineComboBox.currentIndexChanged.connect(self.redrawcurviness)
        self.BTsplineComboBox = QComboBox()
        self.BTsplineComboBox.addItems(['1','2','3','4','5'])
        self.BTsplineComboBox.setCurrentIndex(self.aw.qmc.BTsplinedegree - 1)
        self.BTsplineComboBox.currentIndexChanged.connect(self.redrawcurviness)

        # connect the ArtisanDialog standard OK/Cancel buttons
        self.dialogbuttons.removeButton(self.dialogbuttons.button(QDialogButtonBox.StandardButton.Ok))
        self.dialogbuttons.removeButton(self.dialogbuttons.button(QDialogButtonBox.StandardButton.Cancel))

        close_button: Optional[QPushButton] = self.dialogbuttons.addButton(QDialogButtonBox.StandardButton.Close)
        apply_button: Optional[QPushButton] = self.dialogbuttons.addButton(QDialogButtonBox.StandardButton.Apply)
        defaults_button: Optional[QPushButton] = self.dialogbuttons.addButton(QDialogButtonBox.StandardButton.RestoreDefaults)
        if close_button is not None:
            self.setButtonTranslations(close_button,'Close',QApplication.translate('Button','Close'))
        if apply_button is not None:
            self.setButtonTranslations(apply_button,'Apply',QApplication.translate('Button','Apply'))
            apply_button.clicked.connect(self.settimes)
        if defaults_button is not None:
            self.setButtonTranslations(defaults_button,'Restore Defaults',QApplication.translate('Button','Restore Defaults'))
            defaults_button.clicked.connect(self.reset)
            defaults_button.setAutoDefault(False)

        self.dialogbuttons.rejected.connect(self.accept)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.dialogbuttons)
        marksLayout = QGridLayout()
        marksLayout.addWidget(markersettinglabel,0,0)
        marksLayout.addWidget(timesettinglabel,0,1)
        marksLayout.addWidget(btsettinglabel,0,2)
        marksLayout.addWidget(etsettinglabel,0,3)
        marksLayout.addWidget(charge,1,0)
        marksLayout.addWidget(self.Edit0,1,1)
        marksLayout.addWidget(self.Edit0bt,1,2)
        marksLayout.addWidget(self.Edit0et,1,3)
        marksLayout.addWidget(self.dryend,2,0)
        marksLayout.addWidget(self.Edit1,2,1)
        marksLayout.addWidget(self.Edit1bt,2,2)
        marksLayout.addWidget(self.Edit1et,2,3)
        marksLayout.addWidget(self.fcs,3,0)
        marksLayout.addWidget(self.Edit2,3,1)
        marksLayout.addWidget(self.Edit2bt,3,2)
        marksLayout.addWidget(self.Edit2et,3,3)
        marksLayout.addWidget(self.fce,4,0)
        marksLayout.addWidget(self.Edit3,4,1)
        marksLayout.addWidget(self.Edit3bt,4,2)
        marksLayout.addWidget(self.Edit3et,4,3)
        marksLayout.addWidget(self.scs,5,0)
        marksLayout.addWidget(self.Edit4,5,1)
        marksLayout.addWidget(self.Edit4bt,5,2)
        marksLayout.addWidget(self.Edit4et,5,3)
        marksLayout.addWidget(self.sce,6,0)
        marksLayout.addWidget(self.Edit5,6,1)
        marksLayout.addWidget(self.Edit5bt,6,2)
        marksLayout.addWidget(self.Edit5et,6,3)
        marksLayout.addWidget(drop,7,0)
        marksLayout.addWidget(self.Edit6,7,1)
        marksLayout.addWidget(self.Edit6bt,7,2)
        marksLayout.addWidget(self.Edit6et,7,3)
        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(marksLayout)
        curvinessLayout = QHBoxLayout()
        curvinessLayout.addWidget(curvinesslabel)
        curvinessLayout.addWidget(etcurviness)
        curvinessLayout.addWidget(self.ETsplineComboBox)
        curvinessLayout.addWidget(btcurviness)
        curvinessLayout.addWidget(self.BTsplineComboBox)
        modLayout = QVBoxLayout()
        modLayout.addLayout(curvinessLayout)
        marksGroupLayout = QGroupBox(QApplication.translate('GroupBox','Initial Settings'))
        marksGroupLayout.setLayout(settingsLayout)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(marksGroupLayout)
        mainLayout.addLayout(modLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        if close_button is not None:
            close_button.setFocus()

        settings = QSettings()
        if settings.contains('DesignerPosition'):
            self.move(settings.value('DesignerPosition'))

        mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

    @pyqtSlot(int)
    def redrawcurviness(self, _:int) -> None:
        try:
            ETcurviness = int(str(self.ETsplineComboBox.currentText()))
        except Exception:  # pylint: disable=broad-except
            ETcurviness = self.aw.qmc.ETsplinedegree
        try:
            BTcurviness = int(str(self.BTsplineComboBox.currentText()))
        except Exception:  # pylint: disable=broad-except
            BTcurviness = self.aw.qmc.BTsplinedegree
        timepoints = len(self.aw.qmc.timex)
        if (timepoints - ETcurviness) >= 1:
            self.aw.qmc.ETsplinedegree = ETcurviness
        else:
            self.aw.qmc.ETsplinedegree = len(self.aw.qmc.timex)-1
            self.ETsplineComboBox.setCurrentIndex(self.aw.qmc.ETsplinedegree-1)
            ms = QApplication.translate('Message','Not enough time points for an ET curviness of {0}. Set curviness to {1}').format(ETcurviness,self.aw.qmc.ETsplinedegree)
            QMessageBox.information(self,QApplication.translate('Message','Designer Config'),ms)
        if (timepoints - BTcurviness) >= 1:
            self.aw.qmc.BTsplinedegree = BTcurviness
        else:
            self.aw.qmc.BTsplinedegree = len(self.aw.qmc.timex)-1
            self.BTsplineComboBox.setCurrentIndex(self.aw.qmc.BTsplinedegree-1)
            ms = QApplication.translate('Message','Not enough time points for an BT curviness of {0}. Set curviness to {1}').format(BTcurviness,self.aw.qmc.BTsplinedegree)
            QMessageBox.information(self,QApplication.translate('Message','Designer Config'),ms)
        self.aw.qmc.redrawdesigner()

    @pyqtSlot(bool)
    def settimes(self, _:bool = False) -> None:
        #check input
        strings = [QApplication.translate('Message','CHARGE'),
                   QApplication.translate('Message','DRY END'),
                   QApplication.translate('Message','FC START'),
                   QApplication.translate('Message','FC END'),
                   QApplication.translate('Message','SC START'),
                   QApplication.translate('Message','SC END'),
                   QApplication.translate('Message','DROP')]
        timecheck = self.validatetime()
        if timecheck != 1000:
            st = QApplication.translate('Message','Incorrect time format. Please recheck {0} time').format(strings[timecheck])
            QMessageBox.information(self,QApplication.translate('Message','Designer Config'),st)
            return
        checkvalue = self.validatetimeorder()
        if checkvalue != 1000:
            st = QApplication.translate('Message','Times need to be in ascending order. Please recheck {0} time').format(strings[checkvalue+1])
            QMessageBox.information(self,QApplication.translate('Message','Designer Config'),st)
            return
        if self.Edit0bt.text() != self.Edit0btcopy:
            try:
                self.aw.qmc.temp2[self.aw.qmc.timeindex[0]] = float(str(self.Edit0bt.text()))
                self.Edit0btcopy = self.Edit0bt.text()
            except Exception: # pylint: disable=broad-except
                self.Edit0bt.setText(self.Edit0btcopy)
        if self.Edit0et.text() != self.Edit0etcopy:
            try:
                self.aw.qmc.temp1[self.aw.qmc.timeindex[0]] = float(str(self.Edit0et.text()))
                self.Edit0etcopy = self.Edit0et.text()
            except Exception: # pylint: disable=broad-except
                self.Edit0et.setText(self.Edit0etcopy)
        if self.dryend.isChecked():
            if self.Edit1.text() != self.Edit1copy and stringtoseconds(str(self.Edit1.text())):
                try:
                    timez = stringtoseconds(str(self.Edit1.text()))+ self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    self.aw.qmc.timex[self.aw.qmc.timeindex[1]] = timez
                    self.Edit1copy = self.Edit1.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit1.setText(self.Edit1copy)
            if self.Edit1bt.text() != self.Edit1btcopy:
                try:
                    self.aw.qmc.temp2[self.aw.qmc.timeindex[1]] = float(self.Edit1bt.text())
                    self.Edit1btcopy = self.Edit1bt.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit1bt.setText(self.Edit1btcopy)
            if self.Edit1et.text() != self.Edit1etcopy:
                try:
                    self.aw.qmc.temp1[self.aw.qmc.timeindex[1]] = float(self.Edit1et.text())
                    self.Edit1etcopy = self.Edit1et.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit1et.setText(self.Edit1etcopy)
        if self.fcs.isChecked():
            if self.Edit2.text() != self.Edit2copy and stringtoseconds(str(self.Edit2.text())):
                try:
                    timez = stringtoseconds(str(self.Edit2.text()))+ self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    self.aw.qmc.timex[self.aw.qmc.timeindex[2]] = timez
                    self.Edit2copy = self.Edit2.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit2.setText(self.Edit2copy)
            if self.Edit2bt.text() != self.Edit2btcopy:
                try:
                    self.aw.qmc.temp2[self.aw.qmc.timeindex[2]] = float(self.Edit2bt.text())
                    self.Edit2btcopy = self.Edit2bt.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit2bt.setText(self.Edit2btcopy)
            if self.Edit2et.text() != self.Edit2etcopy:
                try:
                    self.aw.qmc.temp1[self.aw.qmc.timeindex[2]] = float(self.Edit2et.text())
                    self.Edit2etcopy = self.Edit2et.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit2et.setText(self.Edit2etcopy)
        if self.fce.isChecked():
            if self.Edit3.text() != self.Edit3copy and stringtoseconds(str(self.Edit3.text())):
                try:
                    timez = stringtoseconds(str(self.Edit3.text()))+ self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    self.aw.qmc.timex[self.aw.qmc.timeindex[3]] = timez
                    self.Edit3copy = self.Edit3.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit3.setText(self.Edit3copy)
            if self.Edit3bt.text() != self.Edit3btcopy:
                try:
                    self.aw.qmc.temp2[self.aw.qmc.timeindex[3]] = float(self.Edit3bt.text())
                    self.Edit3btcopy = self.Edit3bt.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit3bt.setText(self.Edit3btcopy)
            if self.Edit3et.text() != self.Edit3etcopy:
                try:
                    self.aw.qmc.temp1[self.aw.qmc.timeindex[3]] = float(self.Edit3et.text())
                    self.Edit3etcopy = self.Edit3et.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit3et.setText(self.Edit3etcopy)
        if self.scs.isChecked():
            if self.Edit4.text() != self.Edit4copy and stringtoseconds(str(self.Edit4.text())):
                try:
                    timez = stringtoseconds(str(self.Edit4.text()))+ self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    self.aw.qmc.timex[self.aw.qmc.timeindex[4]] = timez
                    self.Edit4copy = self.Edit4.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit4.setText(self.Edit4copy)
            if self.Edit4bt.text() != self.Edit4btcopy:
                try:
                    self.aw.qmc.temp2[self.aw.qmc.timeindex[4]] = float(self.Edit4bt.text())
                    self.Edit4btcopy = self.Edit4bt.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit4bt.setText(self.Edit4btcopy)
            if self.Edit4et.text() != self.Edit4etcopy:
                try:
                    self.aw.qmc.temp1[self.aw.qmc.timeindex[4]] = float(self.Edit4et.text())
                    self.Edit4etcopy = self.Edit4et.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit4et.setText(self.Edit4etcopy)
        if self.sce.isChecked():
            if self.Edit5.text() != self.Edit5copy and stringtoseconds(str(self.Edit5.text())):
                try:
                    timez = stringtoseconds(str(self.Edit5.text()))+ self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    self.aw.qmc.timex[self.aw.qmc.timeindex[5]] = timez
                    self.Edit5copy = self.Edit5.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit5.setText(self.Edit5copy)
            if self.Edit5bt.text() != self.Edit5btcopy:
                try:
                    self.aw.qmc.temp2[self.aw.qmc.timeindex[5]] = float(self.Edit5bt.text())
                    self.Edit5btcopy = self.Edit5bt.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit5bt.setText(self.Edit5btcopy)
            if self.Edit5et.text() != self.Edit5etcopy:
                try:
                    self.aw.qmc.temp1[self.aw.qmc.timeindex[5]] = float(self.Edit5et.text())
                    self.Edit5etcopy = self.Edit5et.text()
                except Exception: # pylint: disable=broad-except
                    self.Edit5et.setText(self.Edit5etcopy)
        if self.Edit6.text() != self.Edit6copy and stringtoseconds(str(self.Edit6.text())):
            try:
                timez = stringtoseconds(str(self.Edit6.text()))+ self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                self.aw.qmc.timex[self.aw.qmc.timeindex[6]] = timez
                self.Edit6copy = self.Edit6.text()
            except Exception: # pylint: disable=broad-except
                self.Edit6.setText(self.Edit6copy)
        if self.Edit6bt.text() != self.Edit6btcopy:
            try:
                self.aw.qmc.temp2[self.aw.qmc.timeindex[6]] = float(self.Edit6bt.text())
                self.Edit6btcopy = self.Edit6bt.text()
            except Exception: # pylint: disable=broad-except
                self.Edit6bt.setText(self.Edit6btcopy)
        if self.Edit6et.text() != self.Edit6etcopy:
            try:
                self.aw.qmc.temp1[self.aw.qmc.timeindex[6]] = float(self.Edit6et.text())
                self.Edit6etcopy = self.Edit6et.text()
            except Exception: # pylint: disable=broad-except
                self.Edit6et.setText(self.Edit6etcopy)
        for i in range(1,6): #1-5
            self.aw.qmc.designertimeinit[i] = self.aw.qmc.timex[self.aw.qmc.timeindex[i]]
        self.aw.qmc.xaxistosm(redraw=False)
        self.aw.qmc.redrawdesigner(force=True)

    #supporting function for settimes()
    def validatetimeorder(self) -> int:
        time = []
        checks = self.readchecks()
        time.append(stringtoseconds(str(self.Edit0.text())))
        time.append(stringtoseconds(str(self.Edit1.text())))
        time.append(stringtoseconds(str(self.Edit2.text())))
        time.append(stringtoseconds(str(self.Edit3.text())))
        time.append(stringtoseconds(str(self.Edit4.text())))
        time.append(stringtoseconds(str(self.Edit5.text())))
        time.append(stringtoseconds(str(self.Edit6.text())))
        for i in range(len(time)-1):
            if time[i+1] <= time[i] and checks[i+1] != 0:
                return i
        return 1000

    def validatetime(self) -> int:
        strings:List[Tuple[int, str]] = []
#        strings.append(self.Edit0.text()) # CHARGE cannot be edited
        if self.dryend.isChecked():
            strings.append((1, self.Edit1.text()))
        if self.fcs.isChecked():
            strings.append((2, self.Edit2.text()))
        if self.fce.isChecked():
            strings.append((3, self.Edit3.text()))
        if self.scs.isChecked():
            strings.append((4, self.Edit4.text()))
        if self.scs.isChecked():
            strings.append((5, self.Edit5.text()))
        strings.append((6, self.Edit6.text()))
        for (i, s) in strings:
            if len(s) < 4 or len(s) > 5:
                return i
        return 1000

    #supporting function for settimes()
    def readchecks(self) -> List[int]:
        checks = [0,0,0,0,0,0,1]
        if self.dryend.isChecked():
            checks[1] = 1
        if self.fcs.isChecked():
            checks[2] = 1
        if self.fce.isChecked():
            checks[3] = 1
        if self.scs.isChecked():
            checks[4] = 1
        if self.sce.isChecked():
            checks[5] = 1
        return checks

#    def create(self) -> None:
#        self.close()
#        self.aw.qmc.convert_designer()

    @pyqtSlot()
    def accept(self) -> None:
        #save window position (only; not size!)
        settings = QSettings()
        settings.setValue('DesignerPosition',self.frameGeometry().topLeft())
        super().accept()

    #reset
    @pyqtSlot(bool)
    def reset(self, _:bool = False) -> None:
        self.dryend.setChecked(True)
        self.fcs.setChecked(True)
        self.fce.setChecked(True)
        self.scs.setChecked(True)
        self.sce.setChecked(True)
        #reset designer
        self.aw.qmc.reset_designer()
        #update editboxes
        self.Edit0.setText(stringfromseconds(0))
        self.Edit1.setText(stringfromseconds(self.aw.qmc.designertimeinit[1]))
        self.Edit2.setText(stringfromseconds(self.aw.qmc.designertimeinit[2]))
        self.Edit3.setText(stringfromseconds(self.aw.qmc.designertimeinit[3]))
        self.Edit4.setText(stringfromseconds(self.aw.qmc.designertimeinit[4]))
        self.Edit5.setText(stringfromseconds(self.aw.qmc.designertimeinit[5]))
        self.Edit6.setText(stringfromseconds(self.aw.qmc.designertimeinit[6]))
        self.Edit0bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[0]]:.1f}')
        self.Edit1bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[1]]:.1f}')
        self.Edit2bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[2]]:.1f}')
        self.Edit3bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[3]]:.1f}')
        self.Edit4bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[4]]:.1f}')
        self.Edit5bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[5]]:.1f}')
        self.Edit6bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[6]]:.1f}')
        self.Edit0et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[0]]:.1f}')
        self.Edit1et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[1]]:.1f}')
        self.Edit2et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[2]]:.1f}')
        self.Edit3et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[3]]:.1f}')
        self.Edit4et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[4]]:.1f}')
        self.Edit5et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[5]]:.1f}')
        self.Edit6et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[6]]:.1f}')
        self.aw.sendmessage(QApplication.translate('Message','Designer has been reset'))

    def loadconfigflags(self) -> None:
        self.dryend.setChecked(bool(self.aw.qmc.timeindex[1]))
        self.fcs.setChecked(bool(self.aw.qmc.timeindex[2]))
        self.fce.setChecked(bool(self.aw.qmc.timeindex[3]))
        self.scs.setChecked(bool(self.aw.qmc.timeindex[4]))
        self.sce.setChecked(bool(self.aw.qmc.timeindex[5]))

    #adds deletes landmarks
    @pyqtSlot(bool)
    def changeflags(self, _:bool = False) -> None:
        sender = self.sender()
        if sender == self.dryend:
            idi = 1
        elif sender == self.fcs:
            idi = 2
        elif sender == self.fce:
            idi = 3
        elif sender == self.scs:
            idi = 4
        elif sender == self.sce:
            idi = 5
        else:
            return
        if self.validatetimeorder() != 1000:
            if idi == 1 and self.dryend.isChecked():
                self.dryend.setChecked(False)
            elif idi == 2 and self.fcs.isChecked():
                self.fcs.setChecked(False)
            elif idi == 3 and self.fce.isChecked():
                self.fce.setChecked(False)
            elif idi == 4 and self.scs.isChecked():
                self.scs.setChecked(False)
            elif idi == 5 and self.sce.isChecked():
                self.sce.setChecked(False)
            #ERROR time from edit boxes is not in ascending order
            strings = [QApplication.translate('Message','CHARGE'),
                       QApplication.translate('Message','DRY END'),
                       QApplication.translate('Message','FC START'),
                       QApplication.translate('Message','FC END'),
                       QApplication.translate('Message','SC START'),
                       QApplication.translate('Message','SC END'),
                       QApplication.translate('Message','DROP')]
            st = QApplication.translate('Message','Times need to be in ascending order. Please recheck {0} time').format(strings[idi])
            QMessageBox.information(self,QApplication.translate('Message','Designer Config'),st)
            return
        #idi = id index
        if self.aw.qmc.timeindex[idi]:
            #ERASE mark point
            self.aw.qmc.currentx = self.aw.qmc.timex[self.aw.qmc.timeindex[idi]]
            self.aw.qmc.currenty = self.aw.qmc.temp2[self.aw.qmc.timeindex[idi]]
            self.aw.qmc.removepoint()
        else:
            #ADD mark point
            timez:Optional[float] = None
            bt:Optional[float] = None
            et:Optional[float] = None
            if idi == 1:
                try:
                    timez = stringtoseconds(self.Edit1.text()) + self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    bt = float(self.Edit1bt.text())
                    et = float(self.Edit1et.text())
                except Exception: # pylint: disable=broad-except
                    self.Edit1.setText(stringfromseconds(self.aw.qmc.designertimeinit[1]))
                    self.Edit1et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[1]]:.1f}')
                    self.Edit1bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[1]]:.1f}')
            if idi == 2:
                try:
                    timez = stringtoseconds(str(self.Edit2.text())) + self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    bt = float(str(self.Edit2bt.text()))
                    et = float(str(self.Edit2et.text()))
                except Exception: # pylint: disable=broad-except
                    self.Edit2.setText(stringfromseconds(self.aw.qmc.designertimeinit[2]))
                    self.Edit2et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[2]]:.1f}')
                    self.Edit2bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[2]]:.1f}')
            if idi == 3:
                try:
                    timez = stringtoseconds(self.Edit3.text()) + self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    bt = float(self.Edit3bt.text())
                    et = float(self.Edit3et.text())
                except Exception: # pylint: disable=broad-except
                    self.Edit3.setText(stringfromseconds(self.aw.qmc.designertimeinit[3]))
                    self.Edit3et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[3]]:.1f}')
                    self.Edit3bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[3]]:.1f}')
            if idi == 4:
                try:
                    timez = stringtoseconds(self.Edit4.text()) + self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    bt = float(self.Edit4bt.text())
                    et = float(self.Edit4et.text())
                except Exception: # pylint: disable=broad-except
                    self.Edit4.setText(stringfromseconds(self.aw.qmc.designertimeinit[4]))
                    self.Edit4et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[4]]:.1f}')
                    self.Edit4bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[4]]:.1f}')
            if idi == 5:
                try:
                    timez = stringtoseconds(self.Edit5.text()) + self.aw.qmc.timex[self.aw.qmc.timeindex[0]]
                    bt = float(self.Edit5bt.text())
                    et = float(self.Edit5et.text())
                except Exception: # pylint: disable=broad-except
                    self.Edit5.setText(stringfromseconds(self.aw.qmc.designertimeinit[5]))
                    self.Edit5et.setText(f'{self.aw.qmc.temp1[self.aw.qmc.timeindex[5]]:.1f}')
                    self.Edit5bt.setText(f'{self.aw.qmc.temp2[self.aw.qmc.timeindex[5]]:.1f}')
            if timez is not None and bt is not None and et is not None:
                self.aw.qmc.currentx = timez
                self.aw.qmc.currenty = bt
                newindex = self.aw.qmc.addpoint(manual=False)
                if newindex is not None:
                    self.aw.qmc.timeindex[idi] = newindex
                    self.aw.qmc.temp2[self.aw.qmc.timeindex[idi]] = bt
                    self.aw.qmc.temp1[self.aw.qmc.timeindex[idi]] = et
                    self.aw.qmc.xaxistosm(redraw=False)
                    self.aw.qmc.redrawdesigner()


class pointDlg(ArtisanDialog):
    def __init__(self, parent:'QWidget', aw:'ApplicationWindow', values:Optional[List[float]] = None) -> None:
        super().__init__(parent, aw)
        if values is None:
            values = [0,0]
        else:
            self.values = values
        self.setWindowTitle(QApplication.translate('Form Caption','Add Point'))
        self.tempEdit = QLineEdit(str(int(round(self.values[1]))))
        self.tempEdit.setValidator(QIntValidator(0, 999, self.tempEdit))
        self.tempEdit.setFocus()
        self.tempEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        templabel = QLabel(QApplication.translate('Label', 'temp'))
        regextime = QRegularExpression(r'^-?[0-9]?[0-9]?[0-9]:[0-5][0-9]$')
        self.timeEdit = QLineEdit(stringfromseconds(self.values[0],leadingzero=False))
        self.timeEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.timeEdit.setValidator(QRegularExpressionValidator(regextime,self))
        timelabel = QLabel(QApplication.translate('Label', 'time'))

        # connect the ArtisanDialog standard OK/Cancel buttons
        self.dialogbuttons.accepted.connect(self.return_values)
        self.dialogbuttons.rejected.connect(self.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.dialogbuttons)
        grid = QGridLayout()
        grid.addWidget(timelabel,0,0)
        grid.addWidget(self.timeEdit,0,1)
        grid.addWidget(templabel,1,0)
        grid.addWidget(self.tempEdit,1,1)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(grid)
        mainLayout.addStretch()
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        ok_button: Optional[QPushButton] = self.dialogbuttons.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button is not None:
            ok_button.setFocus()

    @pyqtSlot()
    def return_values(self) -> None:
        self.values[0] = stringtoseconds(str(self.timeEdit.text()))
        self.values[1] = float(self.tempEdit.text())
        self.accept()


#########################################################################
#############  STANDALONE DESIGNER CLASSES ############################
#########################################################################

import json
import ast
import numpy as np
from scipy.interpolate import UnivariateSpline

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from typing import Dict, Any

# Additional imports for standalone designer
try:
    from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
        QHBoxLayout, QGridLayout, QGroupBox, QLineEdit, QComboBox, 
        QCheckBox, QPushButton, QMessageBox, QFileDialog, QSpinBox, QTextEdit)
    from PyQt6.QtGui import QShortcut, QKeySequence
except ImportError:
    from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
        QHBoxLayout, QGridLayout, QGroupBox, QLineEdit, QComboBox,
        QCheckBox, QPushButton, QMessageBox, QFileDialog, QSpinBox, QTextEdit)
    from PyQt5.QtWidgets import QShortcut
    from PyQt5.QtGui import QKeySequence


class DesignerData:
    """Data model for standalone roast profile design"""
    
    def __init__(self):
        # Initialize with factory defaults
        factory_defaults = {
            'CHARGE': {'time': 0, 'BT': 80.0, 'ET': 70.0, 'enabled': True},
            'DRY_END': {'time': 240, 'BT': 150.0, 'ET': 110.0, 'enabled': True},  # 4:00
            'FC_START': {'time': 420, 'BT': 190.0, 'ET': 140.0, 'enabled': True},  # 7:00
            'FC_END': {'time': 480, 'BT': 205.0, 'ET': 155.0, 'enabled': True},   # 8:00
            'SC_START': {'time': 540, 'BT': 220.0, 'ET': 170.0, 'enabled': False}, # 9:00
            'SC_END': {'time': 600, 'BT': 235.0, 'ET': 180.0, 'enabled': False},  # 10:00
            'DROP': {'time': 660, 'BT': 210.0, 'ET': 165.0, 'enabled': True}      # 11:00
        }
        
        # Load saved defaults or use factory defaults
        self.landmarks = self.load_defaults(factory_defaults)
        
        self.curviness = {'ET': 3, 'BT': 3}
        # Generate default name with timestamp
        import datetime
        now = datetime.datetime.now()
        self.profile_name = f"Profile_{now.strftime('%y-%m-%d_%H%M')}"
        
        # Events and alarms
        self.events = []
        self.alarms = []
    
    def load_defaults(self, factory_defaults: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Load saved defaults from settings or return factory defaults"""
        try:
            settings = QSettings()
            settings.beginGroup("DesignerDefaults")
            
            # Check if we have any saved defaults
            if not settings.childKeys():
                settings.endGroup()
                return factory_defaults.copy()
            
            # Load saved defaults
            landmarks = {}
            for name, factory_data in factory_defaults.items():
                landmarks[name] = {
                    'time': settings.value(f"{name}_time", factory_data['time'], type=int),
                    'BT': settings.value(f"{name}_BT", factory_data['BT'], type=float),
                    'ET': settings.value(f"{name}_ET", factory_data['ET'], type=float),
                    'enabled': settings.value(f"{name}_enabled", factory_data['enabled'], type=bool)
                }
            
            settings.endGroup()
            return landmarks
            
        except Exception:
            # If anything fails, return factory defaults
            return factory_defaults.copy()
        
    def get_enabled_landmarks(self) -> Dict[str, Dict[str, Any]]:
        """Return only enabled landmarks"""
        return {name: data for name, data in self.landmarks.items() 
                if data['enabled'] or name in ['CHARGE', 'DROP']}
    
    def generate_curves(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate time, BT, and ET curves from landmarks"""
        enabled = self.get_enabled_landmarks()
        
        times = [data['time'] for data in enabled.values()]
        bt_temps = [data['BT'] for data in enabled.values()]
        et_temps = [data['ET'] for data in enabled.values()]
        
        # Sort by time
        sorted_data = sorted(zip(times, bt_temps, et_temps))
        times, bt_temps, et_temps = zip(*sorted_data)
        
        # Create smooth curves using splines
        time_array = np.array(times)
        bt_array = np.array(bt_temps)
        et_array = np.array(et_temps)
        
        # Generate dense time points for smooth curves (ensure sufficient resolution)
        num_points = max(200, int((time_array[-1] - time_array[0]) / 5))  # At least one point per 5 seconds
        time_dense = np.linspace(time_array[0], time_array[-1], num_points)
        
        # Create splines with specified curviness (suppress warnings for smooth curves)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bt_spline = UnivariateSpline(time_array, bt_array, k=min(self.curviness['BT'], len(time_array)-1), s=0)
            et_spline = UnivariateSpline(time_array, et_array, k=min(self.curviness['ET'], len(time_array)-1), s=0)
        
        bt_curve = bt_spline(time_dense)
        et_curve = et_spline(time_dense)
        
        return time_dense, bt_curve, et_curve
    
    def save_to_file(self, filename: str) -> None:
        """Save profile to JSON file"""
        data = {
            'profile_name': self.profile_name,
            'landmarks': self.landmarks,
            'curviness': self.curviness,
            'events': self.events,
            'alarms': self.alarms
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_background_alog(self, filename: str) -> None:
        """Export profile as background roast profile (.alog) - reformatted for background use"""
        try:
            # Generate our temperature curve data
            time_curve, bt_curve, et_curve = self.generate_curves()
            
            # Validate we have data
            if len(time_curve) == 0 or len(bt_curve) == 0 or len(et_curve) == 0:
                raise Exception("No temperature curve data to export. Please design a profile first.")
            
            # Create detailed time and temperature arrays similar to working profile resolution
            num_points = 1800  # Similar to working profile
            detailed_time = np.linspace(time_curve[0], time_curve[-1], num_points)
            
            # Interpolate to get detailed temperature curves
            from scipy.interpolate import interp1d
            bt_interp = interp1d(time_curve, bt_curve, kind='cubic', fill_value='extrapolate')
            et_interp = interp1d(time_curve, et_curve, kind='cubic', fill_value='extrapolate')
            
            detailed_bt = bt_interp(detailed_time)
            detailed_et = et_interp(detailed_time)
            
            # Create clean background profile structure (based on working profile structure but without metadata conflicts)
            alog_data = {
                'recording_version': '3.1.5',
                'recording_revision': '',
                'recording_build': '0',
                'version': '3.1.5',
                'revision': 'designer+',
                'build': '0',
                'artisan_os': 'macOS',
                'artisan_os_version': '15.1', 
                'artisan_os_arch': 'arm64',
                'mode': 'F',
                'viewerMode': False,
                'timeindex': [-1, 0, 0, 0, 0, 0, 0, 0],
                'flavors': [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
                'flavors_total_correction': 0,
                'flavorlabels': ['Acidity', 'Aftertaste', 'Clean Cup', 'Head', 'Fragrance', 'Sweetness', 'Aroma', 'Balance', 'Body'],
                'flavorstartangle': 90,
                'flavoraspect': 1.0,
                'title': f'{self.profile_name}_background',
                'locale': 'en',
                'beans': 'Generated by Profile Designer',
                'weight': [0.0, 0, 'g'],
                'defects_weight': 0,
                'volume': [0, 0, 'gal'],
                'density': [0, 'g', 1, 'l'],
                'density_roasted': [0, 'g', 1, 'l'],
                'roastertype': 'Background Profile',
                'roastersize': 0.0,
                'roasterheating': 0,
                'machinesetup': '',
                'operator': 'Profile Designer',
                'organization': '',
                'drumspeed': '',
                'heavyFC': False,
                'lowFC': False,
                'lightCut': False,
                'darkCut': False,
                'drops': False,
                'oily': False,
                'uneven': False,
                'tipping': False,
                'scorching': False,
                'divots': False,
                'whole_color': 0,
                'ground_color': 0,
                'color_system': '',
                'volumeCalcWeightIn': '',
                'volumeCalcWeightOut': '',
                'roastdate': 'Designer Background',
                'roastisodate': '2025-06-25',
                'roasttime': '00:00:00',
                'roastepoch': 0,
                'roasttzoffset': 0,
                'roastbatchnr': 0,
                'roastbatchprefix': '',
                'roastbatchpos': 1,
                'roastUUID': '',
                'beansize_min': '0',
                'beansize_max': '0',
                'roastingnotes': 'Generated background profile from Artisan Profile Designer',
                'cuppingnotes': '',
                'timex': detailed_time.tolist(),
                'temp1': detailed_et.tolist(),  # ET (Environmental Temperature)
                'temp2': detailed_bt.tolist(),  # BT (Bean Temperature)
                'phases': [300, 170, 202, 450],
                'zmax': 50,
                'zmin': 0,
                'ymax': float(max(max(detailed_bt), max(detailed_et)) + 20),
                'ymin': float(min(min(detailed_bt), min(detailed_et)) - 20), 
                'xmin': float(detailed_time[0] - 10),
                'xmax': float(detailed_time[-1] + 10),
                'ambientTemp': 20.0,
                'ambient_humidity': 50.0,
                'ambient_pressure': 1013.25,
                'moisture_greens': 0.0,
                'greens_temp': 0.0,
                'moisture_roasted': 0.0,
                'extradevices': [],
                'extraname1': [],
                'extraname2': [],
                'extratimex': [],
                'extratemp1': [],
                'extratemp2': [],
                'extramathexpression1': [],
                'extramathexpression2': [],
                'extradevicecolor1': [],
                'extradevicecolor2': [],
                'extraLCDvisibility1': [False] * 10,
                'extraLCDvisibility2': [False] * 10,
                'extraCurveVisibility1': [True] * 10,
                'extraCurveVisibility2': [True] * 10,
                'extraDelta1': [False] * 10,
                'extraDelta2': [False] * 10,
                'extraFill1': [0] * 10,
                'extraFill2': [0] * 10,
                'extramarkersizes1': [],
                'extramarkersizes2': [],
                'extramarkers1': [],
                'extramarkers2': [],
                'extralinewidths1': [],
                'extralinewidths2': [],
                'extralinestyles1': [],
                'extralinestyles2': [],
                'extradrawstyles1': [],
                'extradrawstyles2': [],
                'externalprogram': '',
                'externaloutprogram': '',
                'extraNoneTempHint1': [],
                'extraNoneTempHint2': [],
                'alarmsetlabel': '',
                'alarmflag': [0, 0],
                'alarmguard': [-1, -1],
                'alarmnegguard': [-1, -1],
                'alarmtime': [-1, 1],
                'alarmoffset': [0, 0],
                'alarmcond': [1, 1],
                'alarmsource': [1, 1],
                'alarmtemperature': [200.0, 230.0],
                'alarmaction': [3, 3],
                'alarmbeep': [0, 0],
                'alarmstrings': ['', ''],
                'backgroundpath': '',  # IMPORTANT: Empty background path
                'svLabel': '',
                'svValues': [0] * 8,
                'svRamps': [0] * 8,
                'svSoaks': [0] * 8,
                'svActions': [-1] * 8,
                'svBeeps': [False] * 8,
                'svDescriptions': [''] * 8,
                'pidKp': 0.0,
                'pidKi': 0.0,
                'pidKd': 0.0,
                'pidSource': 1,
                'svLookahead': 8,
                'devices': ['NONE'],
                'elevation': 0,
                'computed': {
                    'total_ts': 0,
                    'total_ts_ET': 0,
                    'total_ts_BT': 0,
                    'AUC': 0,
                    'AUCbegin': 'TP',
                    'AUCbase': 212,
                    'AUCfromeventflag': 0,
                    'dry_phase_AUC': 0,
                    'mid_phase_AUC': 0,
                    'finish_phase_AUC': 0,
                    'volumein': 0,
                    'volumeout': 0,
                    'weightin': 0.0,
                    'weightout': 0,
                    'roast_defects_weight': 0,
                    'bbp_total_time': -1.0,
                    'bbp_bottom_temp': -1.0,
                    'bbp_begin_to_bottom_time': -1.0,
                    'bbp_bottom_to_charge_time': -1.0,
                    'bbp_begin_to_bottom_ror': -1.0,
                    'bbp_bottom_to_charge_ror': -1.0
                },
                'anno_positions': [],
                'flag_positions': [],
                'loadlabels': ['', '', '', ''],
                'loadratings': [0.0, 0.0, 0.0, 0.0],
                'ratingunits': [0, 0, 0, 0],
                'sourcetypes': [0, 0, 0, 0],
                'load_etypes': [0, 0, 0, 0],
                'presssure_percents': [False, False, False, False],
                'loadevent_zeropcts': [0, 0, 0, 0],
                'loadevent_hundpcts': [100, 100, 100, 100],
                'meterlabels': ['', ''],
                'meterunits': [3, 3],
                'meterfuels': [2, 2],
                'metersources': [0, 0],
                'meterreads': [[0.0] * 9, [0.0] * 9],
                'co2kg_per_btu': [6.288e-05, 5.291e-05, 0.0002964],
                'biogas_co2_reduction': 0.7562,
                'preheatDuration': 0,
                'preheatenergies': [0.0, 0.0, 0.0, 0.0],
                'betweenbatchDuration': 0,
                'betweenbatchenergies': [0.0, 0.0, 0.0, 0.0],
                'coolingDuration': 0,
                'coolingenergies': [0.0, 0.0, 0.0, 0.0],
                'betweenbatch_after_preheat': True,
                'electricEnergyMix': 0,
                'gasMix': 0,
                'bbp_begin': 'Start',
                'bbp_time_added_from_prev': 0.0,
                'bbp_endroast_epoch_msec': 0,
                'bbp_endevents': [],
                'bbp_dropevents': [],
                'bbp_dropbt': 0.0,
                'bbp_dropet': 0.0,
                'bbp_drop_to_end': 0.0,
                'default_etypes': [True, True, True, True, True],
                'default_etypes_set': [0, 0, 0, 0, 0],
                'etypes': ['Air', 'Drum', 'Damper', 'Burner', '--'],
                'specialevents': [],
                'specialeventstype': [],
                'specialeventsvalue': [],
                'specialeventsStrings': []
            }
            
            # Set landmark time indices for background format using detailed time array
            enabled_landmarks = self.get_enabled_landmarks()
            landmark_order = ['CHARGE', 'DRY_END', 'FC_START', 'FC_END', 'SC_START', 'SC_END', 'DROP']
            
            for i, landmark_name in enumerate(landmark_order):
                if landmark_name in enabled_landmarks and i < len(alog_data["timeindex"]):
                    landmark_time = enabled_landmarks[landmark_name]['time']
                    # Find closest time index in detailed time array
                    time_idx = np.argmin(np.abs(detailed_time - landmark_time))
                    alog_data["timeindex"][i] = int(time_idx)
                    
            # Add events as special events
            for event in self.events:
                time_idx = np.argmin(np.abs(detailed_time - event['time']))
                alog_data["specialevents"].append(int(time_idx))
                alog_data["specialeventstype"].append(4)  # Note event type
                alog_data["specialeventsvalue"].append(0)
                desc = event['description'] if event['description'] else event['type']
                alog_data["specialeventsStrings"].append(f"{event['type']}: {desc}")
            
            # Write background alog file (Python dict format, not JSON)
            with open(filename, 'w') as f:
                f.write(str(alog_data))
                
        except Exception as e:
            raise Exception(f"Failed to export background profile: {e}")
    
    def load_from_file(self, filename: str) -> None:
        """Load profile from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
            self.profile_name = data.get('profile_name', 'Loaded Profile')
            self.landmarks = data.get('landmarks', self.landmarks)
            self.curviness = data.get('curviness', self.curviness)
            self.events = data.get('events', [])
            self.alarms = data.get('alarms', [])


def stringfromseconds_standalone(seconds: float) -> str:
    """Convert seconds to MM:SS format"""
    if seconds < 0:
        return "0:00"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def stringtoseconds_standalone(time_str: str) -> float:
    """Convert MM:SS format to seconds"""
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            return float(parts[0]) * 60 + float(parts[1])
        else:
            return float(time_str)
    except:
        return 0.0


class ProfileCanvas(FigureCanvas):
    """Matplotlib canvas for displaying roast profile"""
    
    def __init__(self, data: DesignerData):
        self.fig = Figure(figsize=(10, 6))
        super().__init__(self.fig)
        self.data = data
        self.ax = self.fig.add_subplot(111)
        self.setup_plot()
        
        # Interactive state
        self.dragging = False
        self.drag_landmark = None
        self.drag_type = None  # 'BT' or 'ET'
        self.landmark_artists = {}
        
        # Connect mouse events
        self.mpl_connect('button_press_event', self.on_press)
        self.mpl_connect('button_release_event', self.on_release)
        self.mpl_connect('motion_notify_event', self.on_motion)
        
    def setup_plot(self):
        """Initialize plot appearance"""
        self.ax.set_xlabel('Time (mm:ss)')
        self.ax.set_ylabel('Temperature (°C)')
        # No title needed
        self.ax.grid(True, alpha=0.3)
        
        # Format x-axis to show mm:ss
        self.format_time_axis()
        
    def update_plot(self):
        """Update the plot with current data"""
        self.ax.clear()
        self.setup_plot()
        self.landmark_artists.clear()
        
        try:
            time_curve, bt_curve, et_curve = self.data.generate_curves()
            
            # Plot curves
            self.ax.plot(time_curve, bt_curve, 'r-', linewidth=2, label='BT (Bean Temperature)')
            self.ax.plot(time_curve, et_curve, 'b-', linewidth=2, label='ET (Environmental Temperature)')
            
            # Plot landmark points
            enabled = self.data.get_enabled_landmarks()
            for name, landmark in enabled.items():
                color = '#f07800' if name in ['CHARGE', 'DROP'] else 'orange'
                
                # Plot BT point (circle)
                bt_point = self.ax.plot(landmark['time'], landmark['BT'], 'o', 
                                       color=color, markersize=10, picker=True, 
                                       markeredgecolor='black', markeredgewidth=1)[0]
                
                # Plot ET point (square)
                et_point = self.ax.plot(landmark['time'], landmark['ET'], 's', 
                                       color=color, markersize=10, picker=True,
                                       markeredgecolor='black', markeredgewidth=1)[0]
                
                # Store references for interaction
                self.landmark_artists[bt_point] = {'landmark': name, 'type': 'BT'}
                self.landmark_artists[et_point] = {'landmark': name, 'type': 'ET'}
                
                # Add labels
                self.ax.annotate(f'{name}\nBT', (landmark['time'], landmark['BT']), 
                               xytext=(5, 5), textcoords='offset points', fontsize=8)
                self.ax.annotate(f'{name}\nET', (landmark['time'], landmark['ET']), 
                               xytext=(5, -15), textcoords='offset points', fontsize=8)
            
            # Plot events
            self.plot_events(time_curve, bt_curve, et_curve)
            
            # Plot alarms
            self.plot_alarms(time_curve, bt_curve, et_curve)
            
            self.ax.legend()
            self.ax.set_xlim(0, max(time_curve) * 1.1)
            
            # Set reasonable temperature range
            temp_min = min(min(bt_curve), min(et_curve)) - 20
            temp_max = max(max(bt_curve), max(et_curve)) + 20
            self.ax.set_ylim(temp_min, temp_max)
            
            # Format axes after plotting
            self.format_time_axis()
            self.format_temperature_axis()
            
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error generating plot: {e}", 
                        transform=self.ax.transAxes, ha='center', va='center')
        
        self.draw()
        
    def format_time_axis(self):
        """Format x-axis to show time in mm:ss format"""
        import matplotlib.ticker as ticker
        
        def time_formatter(x, pos):
            """Convert seconds to mm:ss format"""
            if x < 0:
                return "0:00"
            minutes = int(x // 60)
            seconds = int(x % 60)
            return f"{minutes}:{seconds:02d}"
        
        # Set custom formatter for x-axis
        self.ax.xaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
        
        # Set reasonable tick intervals based on time range
        max_time = max([data['time'] for data in self.data.landmarks.values()])
        
        if max_time <= 300:  # 5 minutes or less
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(60))   # Every 1 minute
            self.ax.xaxis.set_minor_locator(ticker.MultipleLocator(30))   # Every 30 seconds
        elif max_time <= 900:  # 15 minutes or less
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(120))  # Every 2 minutes
            self.ax.xaxis.set_minor_locator(ticker.MultipleLocator(60))   # Every 1 minute
        elif max_time <= 1800:  # 30 minutes or less
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(300))  # Every 5 minutes
            self.ax.xaxis.set_minor_locator(ticker.MultipleLocator(120))  # Every 2 minutes
        else:  # More than 30 minutes
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(600))  # Every 10 minutes
            self.ax.xaxis.set_minor_locator(ticker.MultipleLocator(300))  # Every 5 minutes
            
    def format_temperature_axis(self):
        """Format y-axis for temperature with reasonable intervals"""
        import matplotlib.ticker as ticker
        
        # Get temperature range
        y_min, y_max = self.ax.get_ylim()
        temp_range = y_max - y_min
        
        if temp_range <= 100:  # Small range
            self.ax.yaxis.set_major_locator(ticker.MultipleLocator(10))  # Every 10°C
            self.ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))   # Every 5°C
        elif temp_range <= 200:  # Medium range
            self.ax.yaxis.set_major_locator(ticker.MultipleLocator(20))  # Every 20°C
            self.ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))  # Every 10°C
        else:  # Large range
            self.ax.yaxis.set_major_locator(ticker.MultipleLocator(50))  # Every 50°C
            self.ax.yaxis.set_minor_locator(ticker.MultipleLocator(25))  # Every 25°C
            
    def plot_events(self, time_curve, bt_curve, et_curve):
        """Plot events as vertical lines on the chart"""
        y_min, y_max = self.ax.get_ylim()
        
        for event in self.data.events:
            # Draw vertical line for event
            self.ax.axvline(x=event['time'], color='green', linestyle='--', alpha=0.7, linewidth=1)
            
            # Add event label
            desc = event['description'] if event['description'] else event['type']
            self.ax.annotate(f"E: {desc}", 
                           (event['time'], y_max * 0.9), 
                           xytext=(5, 0), textcoords='offset points', 
                           fontsize=7, color='green', rotation=90,
                           ha='left', va='top')
                           
    def plot_alarms(self, time_curve, bt_curve, et_curve):
        """Plot alarms as horizontal lines and markers"""
        for alarm in self.data.alarms:
            # Interpolate temperature curve at alarm time
            import numpy as np
            if alarm['time'] <= max(time_curve):
                # Find approximate temperature at alarm time
                idx = np.searchsorted(time_curve, alarm['time'])
                if idx < len(time_curve):
                    if alarm['temp_type'] == 'BT':
                        actual_temp = bt_curve[idx] if idx < len(bt_curve) else bt_curve[-1]
                        color = 'red'
                    else:  # ET
                        actual_temp = et_curve[idx] if idx < len(et_curve) else et_curve[-1]
                        color = 'blue'
                    
                    # Draw alarm marker
                    self.ax.plot(alarm['time'], alarm['temperature'], 
                               marker='X', color=color, markersize=10, 
                               markeredgecolor='black', markeredgewidth=1)
                    
                    # Add alarm label
                    self.ax.annotate(f"A: {alarm['temp_type']} {alarm['temperature']}°C", 
                                   (alarm['time'], alarm['temperature']), 
                                   xytext=(5, 10), textcoords='offset points', 
                                   fontsize=7, color=color,
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
    def on_press(self, event):
        """Handle mouse press events"""
        if event.inaxes != self.ax:
            return
            
        # Check if we clicked on a landmark point
        for artist, info in self.landmark_artists.items():
            if artist.contains(event)[0]:
                self.dragging = True
                self.drag_landmark = info['landmark']
                self.drag_type = info['type']
                break
                
    def on_release(self, event):
        """Handle mouse release events"""
        if self.dragging:
            self.dragging = False
            self.drag_landmark = None
            self.drag_type = None
            # Notify parent window to update UI
            if hasattr(self, 'parent_window'):
                self.parent_window.refresh_ui()
                
    def on_motion(self, event):
        """Handle mouse motion events"""
        if not self.dragging or event.inaxes != self.ax:
            return
            
        if self.drag_landmark and self.drag_type:
            # Update landmark position
            landmark = self.data.landmarks[self.drag_landmark]
            
            # Don't allow dragging CHARGE time
            if self.drag_landmark != 'CHARGE':
                landmark['time'] = max(0, event.xdata)
            
            if self.drag_type == 'BT':
                landmark['BT'] = max(0, event.ydata)
            elif self.drag_type == 'ET':
                landmark['ET'] = max(0, event.ydata)
                
            # Update plot in real time
            self.update_plot()


class StandaloneDesignerWindow(QMainWindow):
    """Standalone roast profile designer window"""
    
    def __init__(self):
        super().__init__()
        self.data = DesignerData()
        self.landmark_widgets = {}
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Artisan Roast Profile Designer")
        self.setMinimumSize(1200, 800)
        
        # Add keyboard shortcuts
        try:
            from PyQt6.QtGui import QShortcut, QKeySequence
            from PyQt6.QtCore import Qt
        except ImportError:
            try:
                from PyQt5.QtWidgets import QShortcut
                from PyQt5.QtGui import QKeySequence
                from PyQt5.QtCore import Qt
            except ImportError:
                # Fallback for older PyQt versions
                from PyQt5.QtGui import QShortcut, QKeySequence
                from PyQt5.QtCore import Qt
            
        # Cmd+S (or Ctrl+S) to save draft
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.save_draft_profile)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        controls_panel = self.create_controls_panel()
        main_layout.addWidget(controls_panel, 1)
        
        # Right panel for plot
        self.canvas = ProfileCanvas(self.data)
        self.canvas.parent_window = self  # Allow canvas to update UI
        main_layout.addWidget(self.canvas, 2)
        
        # Update initial plot
        self.canvas.update_plot()
        
    def create_controls_panel(self) -> QWidget:
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Profile name
        name_group = QGroupBox("Profile")
        name_layout = QHBoxLayout(name_group)
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit(self.data.profile_name)
        self.name_edit.textChanged.connect(self.update_profile_name)
        name_layout.addWidget(self.name_edit)
        layout.addWidget(name_group)
        
        # Landmarks group
        landmarks_group = self.create_landmarks_group()
        layout.addWidget(landmarks_group)
        
        # Curviness group
        curviness_group = self.create_curviness_group()
        layout.addWidget(curviness_group)
        
        # Events group
        events_group = self.create_events_group()
        layout.addWidget(events_group)
        
        # Alarms group
        alarms_group = self.create_alarms_group()
        layout.addWidget(alarms_group)
        
        # Buttons
        button_layout = self.create_buttons()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        return panel
        
    def create_landmarks_group(self) -> QGroupBox:
        """Create landmarks configuration group"""
        group = QGroupBox("Landmarks")
        layout = QGridLayout(group)
        layout.setVerticalSpacing(8)  # Add vertical spacing
        layout.setHorizontalSpacing(5)  # Add horizontal spacing
        
        # Headers
        header_landmark = QLabel("Landmark")
        header_landmark.setStyleSheet("font-weight: bold;")
        header_time = QLabel("Time")
        header_time.setStyleSheet("font-weight: bold;")
        header_bt = QLabel("BT (°C)")
        header_bt.setStyleSheet("font-weight: bold;")
        header_et = QLabel("ET (°C)")
        header_et.setStyleSheet("font-weight: bold;")
        
        layout.addWidget(header_landmark, 0, 0)
        layout.addWidget(header_time, 0, 1)
        layout.addWidget(header_bt, 0, 2)
        layout.addWidget(header_et, 0, 3)
        
        row = 1
        for name, data in self.data.landmarks.items():
            # Create container for landmark name (editable or fixed)
            landmark_container = QWidget()
            landmark_layout = QHBoxLayout(landmark_container)
            landmark_layout.setContentsMargins(0, 0, 0, 0)
            
            if name in ['CHARGE', 'DROP']:
                # Fixed names for CHARGE and DROP
                label = QLabel(name)
                label.setStyleSheet('background-color: #f07800; padding: 4px; font-weight: bold; border-radius: 3px;')
                label.setMinimumHeight(25)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                landmark_layout.addWidget(label)
            else:
                # Editable names for other landmarks
                checkbox = QCheckBox()
                checkbox.setChecked(data['enabled'])
                checkbox.setMinimumHeight(25)
                checkbox.toggled.connect(lambda checked, n=name: self.toggle_landmark(n, checked))
                landmark_layout.addWidget(checkbox)
                
                name_edit = QLineEdit(name)
                name_edit.setStyleSheet('background-color: orange; padding: 2px; font-weight: bold; border-radius: 3px;')
                name_edit.setMinimumHeight(25)
                name_edit.returnPressed.connect(lambda n=name: self.apply_landmark_changes())
                landmark_layout.addWidget(name_edit)
                
                # Store reference to name editor
                if not hasattr(self, 'landmark_name_widgets'):
                    self.landmark_name_widgets = {}
                self.landmark_name_widgets[name] = name_edit
            
            layout.addWidget(landmark_container, row, 0)
            
            # Time input
            time_edit = QLineEdit(stringfromseconds_standalone(data['time']))
            time_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r'^[0-9]?[0-9]:[0-5][0-9]$')))
            # Connect to Enter key press instead of textChanged for on-demand updates
            time_edit.returnPressed.connect(lambda n=name: self.apply_landmark_changes())
            time_edit.setMinimumHeight(25)  # Set minimum height
            if name == 'CHARGE':
                time_edit.setEnabled(False)
            layout.addWidget(time_edit, row, 1)
            
            # BT input
            bt_edit = QLineEdit(f"{data['BT']:.1f}")
            bt_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r'^[0-9]?[0-9]?[0-9]\.?[0-9]?$')))
            # Connect to Enter key press instead of textChanged for on-demand updates
            bt_edit.returnPressed.connect(lambda n=name: self.apply_landmark_changes())
            bt_edit.setMinimumHeight(25)  # Set minimum height
            layout.addWidget(bt_edit, row, 2)
            
            # ET input
            et_edit = QLineEdit(f"{data['ET']:.1f}")
            et_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r'^[0-9]?[0-9]?[0-9]\.?[0-9]?$')))
            # Connect to Enter key press instead of textChanged for on-demand updates
            et_edit.returnPressed.connect(lambda n=name: self.apply_landmark_changes())
            et_edit.setMinimumHeight(25)  # Set minimum height
            layout.addWidget(et_edit, row, 3)
            
            # Store references
            self.landmark_widgets[name] = {
                'time': time_edit,
                'bt': bt_edit,
                'et': et_edit
            }
            
            row += 1
        
        # Add buttons side by side
        # Save as Default button (left)
        save_default_btn = QPushButton("Save as Default")
        save_default_btn.clicked.connect(self.save_as_default)
        save_default_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 5px; }")
        layout.addWidget(save_default_btn, row, 0, 1, 2)  # Span 2 columns (left half)
        
        # Apply button (right)
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self.apply_landmark_changes)
        apply_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 5px; }")
        layout.addWidget(apply_btn, row, 2, 1, 2)  # Span 2 columns (right half)
            
        return group
        
    def create_curviness_group(self) -> QGroupBox:
        """Create curviness control group"""
        group = QGroupBox("Curve Smoothness")
        layout = QHBoxLayout(group)
        
        layout.addWidget(QLabel("ET:"))
        self.et_curviness = QComboBox()
        self.et_curviness.addItems(['1', '2', '3', '4', '5'])
        self.et_curviness.setCurrentIndex(self.data.curviness['ET'] - 1)
        self.et_curviness.currentIndexChanged.connect(self.update_et_curviness)
        layout.addWidget(self.et_curviness)
        
        layout.addWidget(QLabel("BT:"))
        self.bt_curviness = QComboBox()
        self.bt_curviness.addItems(['1', '2', '3', '4', '5'])
        self.bt_curviness.setCurrentIndex(self.data.curviness['BT'] - 1)
        self.bt_curviness.currentIndexChanged.connect(self.update_bt_curviness)
        layout.addWidget(self.bt_curviness)
        
        return group
        
    def create_events_group(self) -> QGroupBox:
        """Create events configuration group"""
        group = QGroupBox("Events")
        layout = QVBoxLayout(group)
        
        # Events list container
        self.events_container = QWidget()
        self.events_layout = QVBoxLayout(self.events_container)
        self.events_layout.setContentsMargins(0, 0, 0, 0)
        self.events_layout.setSpacing(2)
        layout.addWidget(self.events_container)
        
        # Add event controls
        add_event_layout = QHBoxLayout()
        
        # Event time
        add_event_layout.addWidget(QLabel("Time:"))
        self.event_time = QLineEdit("5:00")
        self.event_time.setValidator(QRegularExpressionValidator(QRegularExpression(r'^[0-9]?[0-9]:[0-5][0-9]$')))
        self.event_time.setMaximumWidth(60)
        add_event_layout.addWidget(self.event_time)
        
        # Event type
        add_event_layout.addWidget(QLabel("Type:"))
        self.event_type = QComboBox()
        self.event_type.addItems(['Heat Up', 'Turn Point', 'Gas Adjust', 'Air Flow', 'Drum Speed', 'Custom'])
        add_event_layout.addWidget(self.event_type)
        
        # Event description
        add_event_layout.addWidget(QLabel("Note:"))
        self.event_description = QLineEdit()
        self.event_description.setPlaceholderText("Optional description...")
        add_event_layout.addWidget(self.event_description)
        
        # Add button
        add_event_btn = QPushButton("Add")
        add_event_btn.clicked.connect(self.add_event)
        add_event_layout.addWidget(add_event_btn)
        
        layout.addLayout(add_event_layout)
        
        return group
        
    def create_alarms_group(self) -> QGroupBox:
        """Create alarms configuration group"""
        group = QGroupBox("Temperature Alarms")
        layout = QVBoxLayout(group)
        
        # Alarms list container
        self.alarms_container = QWidget()
        self.alarms_layout = QVBoxLayout(self.alarms_container)
        self.alarms_layout.setContentsMargins(0, 0, 0, 0)
        self.alarms_layout.setSpacing(2)
        layout.addWidget(self.alarms_container)
        
        # Add alarm controls
        add_alarm_layout = QHBoxLayout()
        
        # Alarm time
        add_alarm_layout.addWidget(QLabel("Time:"))
        self.alarm_time = QLineEdit("6:00")
        self.alarm_time.setValidator(QRegularExpressionValidator(QRegularExpression(r'^[0-9]?[0-9]:[0-5][0-9]$')))
        self.alarm_time.setMaximumWidth(60)
        add_alarm_layout.addWidget(self.alarm_time)
        
        # Temperature type
        add_alarm_layout.addWidget(QLabel("Temp:"))
        self.alarm_temp_type = QComboBox()
        self.alarm_temp_type.addItems(['BT', 'ET'])
        add_alarm_layout.addWidget(self.alarm_temp_type)
        
        # Temperature value
        self.alarm_temp = QSpinBox()
        self.alarm_temp.setRange(0, 300)
        self.alarm_temp.setValue(180)
        self.alarm_temp.setSuffix("°C")
        add_alarm_layout.addWidget(self.alarm_temp)
        
        # Alarm action
        add_alarm_layout.addWidget(QLabel("Action:"))
        self.alarm_action = QComboBox()
        self.alarm_action.addItems(['Beep', 'Message', 'Stop', 'Custom'])
        add_alarm_layout.addWidget(self.alarm_action)
        
        # Add button
        add_alarm_btn = QPushButton("Add")
        add_alarm_btn.clicked.connect(self.add_alarm)
        add_alarm_layout.addWidget(add_alarm_btn)
        
        layout.addLayout(add_alarm_layout)
        
        return group
        
    def create_buttons(self) -> QHBoxLayout:
        """Create action buttons"""
        layout = QHBoxLayout()
        
        # Save button (changes text based on state)
        self.save_btn = QPushButton("Save Draft")
        self.save_btn.clicked.connect(self.save_draft_profile)
        self.save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        layout.addWidget(self.save_btn)
        
        # Export Profile button - exports design as background roast profile
        self.export_btn = QPushButton("Export Profile")
        self.export_btn.clicked.connect(self.export_background_profile)
        self.export_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
        layout.addWidget(self.export_btn)
        
        # Load Draft button
        load_draft_btn = QPushButton("Load Draft")
        load_draft_btn.clicked.connect(self.load_draft)
        layout.addWidget(load_draft_btn)
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_profile)
        layout.addWidget(reset_btn)
        
        return layout
    
    # Event handlers
    def update_profile_name(self, name: str):
        """Update profile name"""
        self.data.profile_name = name
        
    def toggle_landmark(self, name: str, enabled: bool):
        """Toggle landmark enabled state"""
        self.data.landmarks[name]['enabled'] = enabled
        self.canvas.update_plot()
        
    def apply_landmark_changes(self):
        """Apply all landmark changes from input fields and update plot"""
        try:
            # Handle landmark name changes first
            if hasattr(self, 'landmark_name_widgets'):
                landmarks_to_rename = []
                for old_name, name_widget in self.landmark_name_widgets.items():
                    new_name = name_widget.text().strip()
                    if new_name and new_name != old_name and old_name not in ['CHARGE', 'DROP']:
                        landmarks_to_rename.append((old_name, new_name))
                
                # Apply renames
                for old_name, new_name in landmarks_to_rename:
                    if new_name not in self.data.landmarks:  # Avoid conflicts
                        self.data.landmarks[new_name] = self.data.landmarks.pop(old_name)
                        # Update widget references
                        if old_name in self.landmark_widgets:
                            self.landmark_widgets[new_name] = self.landmark_widgets.pop(old_name)
            
            # Read all values from input fields and update data
            for name, widgets in self.landmark_widgets.items():
                # Update time
                time_str = widgets['time'].text()
                try:
                    time_seconds = stringtoseconds_standalone(time_str)
                    self.data.landmarks[name]['time'] = time_seconds
                except:
                    pass
                
                # Update BT
                bt_str = widgets['bt'].text()
                try:
                    bt_temp = float(bt_str)
                    self.data.landmarks[name]['BT'] = bt_temp
                except:
                    pass
                
                # Update ET
                et_str = widgets['et'].text()
                try:
                    et_temp = float(et_str)
                    self.data.landmarks[name]['ET'] = et_temp
                except:
                    pass
            
            # If names changed, refresh the entire UI to update references
            if hasattr(self, 'landmark_name_widgets') and landmarks_to_rename:
                self.refresh_ui()
            else:
                # Just update plot if no renames
                self.canvas.update_plot()
        except Exception as e:
            print(f"Error applying landmark changes: {e}")
    
    def save_as_default(self):
        """Save current landmark values as default for future sessions"""
        try:
            # Apply any pending changes first
            self.apply_landmark_changes()
            
            # Save defaults to settings
            settings = QSettings()
            settings.beginGroup("DesignerDefaults")
            
            for name, landmark_data in self.data.landmarks.items():
                settings.setValue(f"{name}_time", landmark_data['time'])
                settings.setValue(f"{name}_BT", landmark_data['BT'])
                settings.setValue(f"{name}_ET", landmark_data['ET'])
                settings.setValue(f"{name}_enabled", landmark_data['enabled'])
            
            settings.endGroup()
            
            QMessageBox.information(self, "Defaults Saved", 
                "Current landmark values have been saved as defaults.\n\n"
                "These values will be used when opening the designer in future sessions.")
                
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Failed to save defaults: {e}")
    
    def update_et_curviness(self, index: int):
        """Update ET curve smoothness"""
        self.data.curviness['ET'] = index + 1
        self.canvas.update_plot()
        
    def update_bt_curviness(self, index: int):
        """Update BT curve smoothness"""
        self.data.curviness['BT'] = index + 1
        self.canvas.update_plot()
        
    def add_event(self):
        """Add a new event"""
        time_str = self.event_time.text()
        event_type = self.event_type.currentText()
        description = self.event_description.text()
        
        try:
            time_seconds = stringtoseconds_standalone(time_str)
            event = {
                'time': time_seconds,
                'type': event_type,
                'description': description
            }
            self.data.events.append(event)
            self.refresh_events_list()
            self.canvas.update_plot()
            
            # Clear inputs
            self.event_description.clear()
            
        except Exception as e:
            QMessageBox.warning(self, "Invalid Event", f"Could not add event: {e}")
            
    def remove_event(self, index: int):
        """Remove event at specific index"""
        if 0 <= index < len(self.data.events):
            del self.data.events[index]
            self.refresh_events_list()
            self.canvas.update_plot()
            
    def add_alarm(self):
        """Add a new alarm"""
        time_str = self.alarm_time.text()
        temp_type = self.alarm_temp_type.currentText()
        temp_value = self.alarm_temp.value()
        action = self.alarm_action.currentText()
        
        try:
            time_seconds = stringtoseconds_standalone(time_str)
            alarm = {
                'time': time_seconds,
                'temp_type': temp_type,
                'temperature': temp_value,
                'action': action
            }
            self.data.alarms.append(alarm)
            self.refresh_alarms_list()
            self.canvas.update_plot()
            
        except Exception as e:
            QMessageBox.warning(self, "Invalid Alarm", f"Could not add alarm: {e}")
            
    def remove_alarm(self, index: int):
        """Remove alarm at specific index"""
        if 0 <= index < len(self.data.alarms):
            del self.data.alarms[index]
            self.refresh_alarms_list()
            self.canvas.update_plot()
            
    def refresh_events_list(self):
        """Refresh the events list display with trash icons"""
        # Clear existing items
        for i in reversed(range(self.events_layout.count())):
            child = self.events_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Add each event with trash icon
        for i, event in enumerate(self.data.events):
            time_str = stringfromseconds_standalone(event['time'])
            desc = event['description'] if event['description'] else event['type']
            item_text = f"{time_str} - {event['type']}: {desc}"
            
            # Create horizontal layout for event item
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(2, 2, 2, 2)
            
            # Event text label
            label = QLabel(item_text)
            label.setStyleSheet("padding: 2px;")
            item_layout.addWidget(label)
            
            # Trash button
            trash_btn = QPushButton("🗑")
            trash_btn.setMaximumSize(20, 20)
            trash_btn.setStyleSheet("QPushButton { background-color: #e0e0e0; color: #666; border: none; border-radius: 3px; font-size: 12px; } QPushButton:hover { background-color: #d0d0d0; }")
            trash_btn.clicked.connect(lambda checked, idx=i: self.remove_event(idx))
            trash_btn.setToolTip("Delete this event")
            item_layout.addWidget(trash_btn)
            
            self.events_layout.addWidget(item_widget)
            
    def refresh_alarms_list(self):
        """Refresh the alarms list display with trash icons"""
        # Clear existing items
        for i in reversed(range(self.alarms_layout.count())):
            child = self.alarms_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Add each alarm with trash icon
        for i, alarm in enumerate(self.data.alarms):
            time_str = stringfromseconds_standalone(alarm['time'])
            item_text = f"{time_str} - {alarm['temp_type']} {alarm['temperature']}°C ({alarm['action']})"
            
            # Create horizontal layout for alarm item
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(2, 2, 2, 2)
            
            # Alarm text label
            label = QLabel(item_text)
            label.setStyleSheet("padding: 2px;")
            item_layout.addWidget(label)
            
            # Trash button
            trash_btn = QPushButton("🗑")
            trash_btn.setMaximumSize(20, 20)
            trash_btn.setStyleSheet("QPushButton { background-color: #e0e0e0; color: #666; border: none; border-radius: 3px; font-size: 12px; } QPushButton:hover { background-color: #d0d0d0; }")
            trash_btn.clicked.connect(lambda checked, idx=i: self.remove_alarm(idx))
            trash_btn.setToolTip("Delete this alarm")
            item_layout.addWidget(trash_btn)
            
            self.alarms_layout.addWidget(item_widget)
        
    def save_draft_profile(self):
        """Save current points/landmarks as draft file (adsg format)"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Draft", f"{self.data.profile_name}.adsg", 
            "Artisan Designer files (*.adsg);;All files (*.*)"
        )
        if filename:
            # Automatically add .adsg extension if not present
            if not filename.lower().endswith('.adsg'):
                filename += '.adsg'
                
            try:
                self.data.save_to_file(filename)
                QMessageBox.information(self, "Draft Saved", 
                    f"Design draft saved to {filename}\n\n"
                    "This contains your points and can be loaded later for editing.")
            except Exception as e:
                QMessageBox.critical(self, "Save Failed", f"Failed to save draft: {e}")
                
    def export_background_profile(self):
        """Export design as background roast profile (.alog)"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Background Profile", f"{self.data.profile_name}_background.alog", 
            "Artisan Log files (*.alog);;All files (*.*)"
        )
        if filename:
            # Automatically add .alog extension if not present
            if not filename.lower().endswith('.alog'):
                filename += '.alog'
                
            try:
                # Generate curve from current landmarks/points and reformat as background profile
                self.data.export_background_alog(filename)
                
                # Ask user if they want to open main Artisan with this background
                reply = QMessageBox.question(self, "Profile Exported", 
                    f"Background roast profile exported to {filename}\n\n"
                    "Would you like to open the main Artisan application\n"
                    "with this profile loaded as background?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes)
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.open_artisan_with_background(filename)
                    
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export background profile: {e}")
    
    def open_artisan_with_background(self, background_file: str):
        """Open main Artisan application with the exported background profile"""
        try:
            import subprocess
            import sys
            import os
            
            # Get the path to the main Artisan script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(current_dir)  # Go up from src/artisanlib to src
            main_script = os.path.join(src_dir, 'artisan.py')
                
            if os.path.exists(main_script):
                # Check if Artisan is already running by looking for the process
                import psutil
                artisan_running = False
                
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        if proc.info['cmdline'] and any('artisan.py' in str(cmd) for cmd in proc.info['cmdline']):
                            artisan_running = True
                            break
                except:
                    pass
                
                if artisan_running:
                    # Artisan is already running - try to communicate the background file
                    # For now, just show a message (would need IPC for full implementation)
                    QMessageBox.information(self, "Load Background", 
                        f"Main Artisan is already running.\n\n"
                        f"To load your background profile:\n"
                        f"1. Go to Config → Background in the running Artisan window\n"
                        f"2. Load: {os.path.basename(background_file)}\n\n"
                        f"File location: {background_file}")
                else:
                    # Artisan not running - launch it
                    try:
                        # Try with background argument
                        cmd = [sys.executable, main_script, background_file]
                        subprocess.Popen(cmd, cwd=os.path.dirname(main_script))
                    except:
                        # Fallback to normal launch
                        cmd = [sys.executable, main_script]
                        subprocess.Popen(cmd, cwd=os.path.dirname(main_script))
                    
                    # Close the designer window to show main Artisan
                    self.close()
            else:
                # Fallback: just show instructions
                QMessageBox.information(self, "Launch Instructions", 
                    f"To use this background profile:\n\n"
                    f"1. Open the main Artisan application\n"
                    f"2. Go to Config → Background\n"
                    f"3. Load the file: {background_file}\n"
                    f"4. Start your roasting session")
                    
        except Exception as e:
            QMessageBox.warning(self, "Launch Failed", 
                f"Could not automatically launch Artisan.\n\n"
                f"To use this background profile:\n"
                f"1. Open the main Artisan application manually\n"
                f"2. Go to Config → Background\n"
                f"3. Load the file: {background_file}\n\n"
                f"Error: {e}")
            
    def load_draft(self):
        """Load draft points from .adsg file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Draft", "", 
            "Artisan Designer files (*.adsg);;JSON files (*.json);;All files (*.*)"
        )
        if filename:
            try:
                self.data.load_from_file(filename)
                
                self.refresh_ui()
                self.canvas.update_plot()
                QMessageBox.information(self, "Draft Loaded", 
                    f"Design draft loaded from {filename}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Load Failed", f"Failed to load draft: {e}")
                
    def reset_profile(self):
        """Reset profile to defaults"""
        reply = QMessageBox.question(self, "Reset Profile", 
            "Are you sure you want to reset the profile to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data = DesignerData()
            self.refresh_ui()
            self.canvas.data = self.data
            self.canvas.update_plot()
            
    def refresh_ui(self):
        """Refresh UI elements with current data"""
        self.name_edit.setText(self.data.profile_name)
        
        for name, widgets in self.landmark_widgets.items():
            data = self.data.landmarks[name]
            widgets['time'].setText(stringfromseconds_standalone(data['time']))
            widgets['bt'].setText(f"{data['BT']:.1f}")
            widgets['et'].setText(f"{data['ET']:.1f}")
            
        self.et_curviness.setCurrentIndex(self.data.curviness['ET'] - 1)
        self.bt_curviness.setCurrentIndex(self.data.curviness['BT'] - 1)
        
        # Refresh events and alarms lists
        self.refresh_events_list()
        self.refresh_alarms_list()
        
    def load_settings(self):
        """Load window settings"""
        settings = QSettings('Artisan', 'StandaloneDesigner')
        if settings.contains('geometry'):
            self.restoreGeometry(settings.value('geometry'))
            
    def save_settings(self):
        """Save window settings"""
        settings = QSettings('Artisan', 'StandaloneDesigner')
        settings.setValue('geometry', self.saveGeometry())
        
    def closeEvent(self, event):
        """Handle window close event"""
        self.save_settings()
        event.accept()


def main_standalone():
    """Main function to run the standalone designer"""
    import sys
    
    app = QApplication(sys.argv)
    app.setApplicationName("Artisan Profile Designer")
    app.setOrganizationName("Artisan")
    
    window = StandaloneDesignerWindow()
    window.show()
    
    sys.exit(app.exec())
