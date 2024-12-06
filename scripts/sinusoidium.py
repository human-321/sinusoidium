print('sinusoidium will take a few minutes to load')
import sys
import os
import time
import subprocess

# subprocess.Popen('echo "pip install -r requirements.txt"', shell=True)

import math
import random
import PyQt5
import PyQt5.Qt
from PyQt5.Qt import *
import PyQt5.QtRemoteObjects
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets
import cell_manager
from cell_manager import cell as cellClass
from pathlib import Path
# from  Qt import AlignmentFlag
os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-codespace"
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLineEdit, QSizePolicy , QScrollArea,QGroupBox, QLabel,QLayout)
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QSize
import numpy
# import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# from sympy import *
from matplotlib.figure import Figure
from numpy import *
import webbrowser

import warnings
warnings.filterwarnings("ignore")
#if you run this file on the codespace nothing will appear but it will sill work just without visuals
#if you want to see stuff download this locally with it's dependcies and run it

#--------depdencies---------
#pyqt5
#matplotlib
#numpy
#----------------------

#to compile install pyinstaller and use the following command
# python -m PyInstaller project\scripts\sinusoidium.py

#colors

#region
#colros

class designSettingsClass():
    def __init__(self):
        self.revertToDefaultColors()
        self.revertToDefaultSizing()

    def revertToDefaultSizing(self):
        self.cellEditorScreenItemHeight = 25
        self.cellLineEditBorderSize = 1
        self.cellLineEditVSpace = 5
        self.graphScreenWidthPercent = .5
        self.mainButtonEdgeRadius = 5
        self.projectButtonsLayoutVmargin = 2
        self.topBarVmargin = 1

    def revertToDefaultColors(self):
        self.cellRandomColors = ['#ff0d05','#fca503','#f605fa','#05e1fa','#0509fa','#070800','#64b93d']

        self.mainColor = "#02404b"
        self.secondaryColor = "#bcdff7"

        self.graphScreenColor = "#fcfbfb"
        self.graphScreengGridColor = "#5c5b5b"
        self.graphScreengAxiesColor = "#050505"

        self.cellTextColor = '#4d4a4a'
        self.cellTextBackgroundColor = '#ffffff'
        self.cellTextBorderColor = "#070707"
        self.cellTextEditAreaBorderColor = self.secondaryColor
        # self.cellEditAreaBorderColor =  self.mainColor

        self.mainBarButtonColor = "#ffffff"
        self.mainButtonBorderColor = "#313131"

        # button
        self.addCellButtonBorderColor = "#424242"

designSettings = designSettingsClass()


#dependices pyqt5 numpy matplotlib

#endregion

#declare vars
#region


# print("\n\n\n\n\n")
appName = "sinusoidium"
appIconImagePath = "project/assets/images/logoAttempt3.png"
MinWindowWidth = 1000
MinWindowHeight = 500
windowWidth = MinWindowWidth
windowHeight = MinWindowHeight

helpPdfFileLink = "project/assets/pdfs/SinusoidiumHelpV2.pdf"




def clamp(minimum,maximum,val):
    return max(min(val,maximum),minimum)


#threadcontroller class
class threadController():

    def __init__(self):

        #setup logic threac
        #region
        self.worker = programEventLoopThreadClass()

        self.programEventLoopThread  = QThread()

        self.setupForeverThread(self.worker, self.programEventLoopThread)

        #endregion


        #setup gui thread
        #region
        self.guiWorker = guiUpdateLoopThreadClass()

        self.guiUpdateLoopThread  = QThread()

        self.setupForeverThread(self.guiWorker, self.guiUpdateLoopThread)

        #endregion

    def setupForeverThread(self, paramworker, paramthread): 
        paramworker.moveToThread(paramthread) #this is fine

        paramthread.started.connect(paramworker.run)
        paramthread.start()



class addCellToCellEditorSignalEmitter(QObject):
    addCellToCellEditorSignal = pyqtSignal(cellClass)

global addCellToCellEditorSignalEmitterId
addCellToCellEditorSignalEmitterId = addCellToCellEditorSignalEmitter()

class updateGraphSignalEmitter(QObject):
    updateGraphSignal = pyqtSignal()

global updateGraphSignalEmitterId
updateGraphSignalEmitterId = updateGraphSignalEmitter()


class cellWidgetManager(QObject):


    def __init__(self):
        super().__init__()
        self.myCellWidgets = []
        # self.myCellWidgetsObjects = []
        
    

    def addCellToCellEditorScreen(self,cell : cellClass):
        
        

        
        self.myCellWidgets.append(cellWidget(cell,self))


class cellWidget(QObject):

    def __init__(self,cell:cellClass,trueParent:cellWidgetManager):
        self.trueParent = trueParent
        super().__init__()
        self.lineEditStyle = 'color: {0};background-color:{3}; border: {2}px solid {1};'.format(designSettings.cellTextColor,designSettings.cellTextBorderColor,
                                                                                                designSettings.cellLineEditBorderSize,designSettings.cellTextBackgroundColor)
        self.cellEditHolder = QHBoxLayout()
        self.settingsShow = False

        self.myCell = cell
        

        # delete button

        #region
        self.cellWidgetDeleteButton = QPushButton()
        #  𝕏  ✗
        self.cellWidgetDeleteButton.setText("✗")
        self.cellWidgetDeleteButton.setFont(QFont('Times',15))
        self.cellWidgetDeleteButton.setFixedHeight(designSettings.cellEditorScreenItemHeight)
        self.cellWidgetDeleteButton.setStyleSheet("border:1px solid {0};color:{1};background-color:{2};".format(designSettings.cellTextBorderColor,designSettings.cellTextColor,
                                                                                                                designSettings.cellTextBackgroundColor))

        self.cellWidgetDeleteButton.clicked.connect(self.deleteMyself)

        

        #endregion



        #cell settings panel
        #region
        self.cellSettingsButton = QPushButton()
        # S  ⋮
        self.cellSettingsButton.setText('{0}⋮{0}'.format(''))
        self.cellSettingsButton.setFont(QFont('Times',25))
        self.cellSettingsButton.setFixedHeight(designSettings.cellEditorScreenItemHeight)
        self.cellSettingsButton.setStyleSheet("border:1px solid {0};color:{1};background-color:{2};".format(designSettings.cellTextBorderColor,designSettings.cellTextColor,
                                                                                                            designSettings.cellTextBackgroundColor))


        self.cellSettingsButton.clicked.connect(self.cellSettingsClicked)


        self.cellSettingsEditPanel = cellSettingsEditPanel(self)
        #endregion

        #main
        #region
        self.mainPanelQVLayout = QVBoxLayout()

        # line edit
        #region
        self.cellWidgetLineEdit = QLineEdit()
        self.cellWidgetLineEdit.textChanged.connect(self.myCellUpdated)
        self.cellWidgetLineEdit.setText(cell_manager.getCellContent(cell))
        self.cellWidgetLineEdit.setFixedHeight(designSettings.cellEditorScreenItemHeight)
        self.cellWidgetLineEdit.setStyleSheet(self.lineEditStyle)

        cell.setCellWidget(self.cellWidgetLineEdit)

        self.mainPanelQVLayout.addWidget(self.cellWidgetLineEdit)
        #endregion

        #under panel
        #region
        self.cellInfoPanel = QLabel()
        self.cellInfoPanel.setText('nerd')
        self.cellInfoPanel.setHidden(True)
        self.cellInfoPanelStyleSheet = """border: 2px solid {0};color:{1};background-color:{2};""".format(designSettings.cellTextBorderColor,designSettings.cellTextColor,
                                                                                                          designSettings.cellTextBackgroundColor)
        self.cellInfoPanel.setStyleSheet(self.cellInfoPanelStyleSheet)

        self.mainPanelQVLayout.addWidget(self.cellInfoPanel)
        #endregion

        self.mainPanelQVLayout.setContentsMargins(0,0,0,designSettings.cellLineEditVSpace)
        self.mainPanelQVLayout.setSpacing(0)

        #endregion


        #hack solution
        self.deleteList = [self.cellWidgetLineEdit,self.cellWidgetDeleteButton,self.cellEditHolder,self.cellSettingsEditPanel,
                            self.cellSettingsButton,self.cellInfoPanel,self.mainPanelQVLayout,self]

        #layout shit
        #region
        self.cellEditHolder.addWidget(self.cellWidgetDeleteButton, alignment=PyQt5.QtCore.Qt.AlignmentFlag.AlignTop)
        self.cellEditHolder.addWidget(self.cellSettingsButton, alignment=PyQt5.QtCore.Qt.AlignmentFlag.AlignTop)
        self.cellEditHolder.addLayout(self.mainPanelQVLayout)

        self.cellEditHolder.setContentsMargins(0,0,0,0)
        self.cellEditHolder.setSpacing(0)

        self.myCell.myCellWidget = self
        #endregion
        cellEditorScreen.addLayout(self.cellEditHolder)

    def myCellUpdated(self):
        graphScreen.updateGraph()
        
        self.updateCellValPanel()

    def updateCellValPanel(self):
        remap = graphScreen.inputRemap | graphScreen.definitionsAndDefiners
        self.cellInfoPanel.setHidden(True)
        if(isinstance(self.myCell.myCellType,cell_manager.cellTypeVariableDefinition)):

            if(len(self.myCell.myCellType.getDefiningExpression()) > 0 and self.myCell.myCellType.getDefiningName() != 'x'):
                self.cellInfoPanel.setHidden(False)
                newText = ''
                try:
                    definer = self.myCell.myCellType.getDefiningExpression()
                    newText = str(float(eval(definer,remap)))
                except:pass
                self.cellInfoPanel.setText(newText)
        else:
            if(isinstance(self.myCell.myCellType,cell_manager.cellTypeComputableNonIndependentExpression)):
                valid = False
                try:
                    self.myCell.myCellType.computeExpression(remap)
                    valid = True
                except: pass
                if(valid):
                    self.cellInfoPanel.setHidden(False)
                    newText = '' 
                    try:
                        newText = str(self.myCell.myCellType.computeExpression(remap))
                    except:pass 

                    self.cellInfoPanel.setText(newText)
            else:self.cellInfoPanel.setHidden(True)  
              

    def cellSettingsClicked(self):
        self.settingsShow = not self.settingsShow
        if(self.settingsShow): self.cellSettingsEditPanel.open()
        else: self.cellSettingsEditPanel.close()
    
    def deleteMyself(self):
        
        


        try:cellEditorScreen.removeItem(cellEditorScreen.indexOf(self.cellEditHolder))
        except: pass

        for thing in self.deleteList:  thing.deleteLater()
        
        cell_manager.deleteCell(self.myCell)
        cellWidgetManagerId.myCellWidgets.pop(cellWidgetManagerId.myCellWidgets.index(self))
        

        updateGraphSignalEmitterId.updateGraphSignal.emit()
        # self.deleteLater()


class cellSettingsEditPanel(QWidget):

    def __init__(self,cellWidgetInstance : cellWidget):
        super().__init__()
        self.sizeMin = [350,300]
        self.setFixedSize(QSize( self.sizeMin[0] , self.sizeMin[1] )   )
        self.widgetOwner = cellWidgetInstance

        self.settingsMainLayout = QVBoxLayout()
        self.settingsMainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        #no touchy
        #region
        # bullshit that is needed to get settings to scroll that doesn't even work 
        #region
        self.settingsGroupBox = QGroupBox()
        self.settingsScroll = QScrollArea()

        self.settingsGroupBox.setLayout(self.settingsMainLayout)
        self.settingsScroll.setWidget(self.settingsGroupBox)
        self.settingsScroll.setWidgetResizable(True)
        self.settingsScroll.setAlignment(Qt.AlignmentFlag.AlignRight)
        # self.settingsMainLayout.sizeHint
        #endregion
        


        # some other bullshit that is needed in order to actually have the settings to scroll for whatever reason
        #region
        policy = QSizePolicy.Policy.Expanding
        # self.settingsGroupBox.setSizePolicy(policy,policy)
        self.settingsScroll.setSizePolicy(policy,policy)
        # self.setSizePolicy(policy,policy)
        # self.
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(self.settingsScroll)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)
        #endregion
        
        #endregion


        self.addHeader('main settings',5)

        #render anything at all check box
        #region


        self.settingsGraphCellLabel = QLabel()
        self.settingsGraphCellLabel.setText('graph this cell')

        self.settingsGraphCellCheckBox = PyQt5.QtWidgets.QCheckBox()

        self.settingsGraphCellCheckBox.setChecked(self.widgetOwner.myCell.cellRenderingData.renderCell)
        self.settingsGraphCellCheckBox.clicked.connect(self.settingsGraphCellCheckBoxCLicked)

        self.settingsGraphCellLayout = self.addPairToMainLayout(self.settingsGraphCellLabel,self.settingsGraphCellCheckBox,15)


        #endregion

        #color enter
        #region


        self.settingsCellRenderColorLabel = QLabel()
        self.settingsCellRenderColorLabel.setText('cell render color')

        self.settingsCellRenderColorTextEdit = QLineEdit()

        self.settingsCellRenderColorTextEdit.setText(self.widgetOwner.myCell.cellRenderingData.renderColor)
        self.settingsCellRenderColorTextEdit.textEdited.connect(self.settingsCellRenderColorTextEditUpdate)

        self.settingsCellRenderColorLayout = self.addPairToMainLayout(self.settingsCellRenderColorLabel,self.settingsCellRenderColorTextEdit,15)

        #endregion

        self.addHeader('settings for nerds',5)


        #detail enter
        #region

        self.settingsCellRenderDetailLabel = QLabel()

        self.settingsCellRenderDetailLineEdit = QLineEdit()

        self.settingsCellRenderDetailLabel.setText("cell render detail / point count")
        self.settingsCellRenderDetailLineEdit.setText(str(self.widgetOwner.myCell.cellRenderingData.renderDetail))

        self.settingsCellRenderDetailLineEdit.textEdited.connect(self.settingsCellRenderDetailTextEditUpdate)

        self.settingsCellRenderDetailLayout = self.addPairToMainLayout(self.settingsCellRenderDetailLabel,self.settingsCellRenderDetailLineEdit,15)

        #rendre discontinuitys
        #endregion

        
        #graph discounititys
        #region 
        self.settingsGraphDiscontinuitiesLabel = QLabel()
        self.settingsGraphDiscontinuitiesLabel.setText('graph discontinuities')

        self.settingsGraphDiscontinuitiesCheckBox = PyQt5.QtWidgets.QCheckBox()

        self.settingsGraphDiscontinuitiesCheckBox.setChecked(self.widgetOwner.myCell.cellRenderingData.renderDiscontinuities)
        self.settingsGraphDiscontinuitiesCheckBox.clicked.connect(self.settingsGraphDiscontinuitiesCheckBoxCLicked)

        self.settingsGraphDiscontinuitiesLayout = self.addPairToMainLayout(self.settingsGraphDiscontinuitiesLabel,self.settingsGraphDiscontinuitiesCheckBox,15)
        
        

        #endregion

        #default settings button
        #region
        self.settingsCellRenderDefaultSettingsButton = QPushButton()
        self.settingsCellRenderDefaultSettingsButton.setText('revert back to default settings')
        self.settingsCellRenderDefaultSettingsButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed))
        self.settingsCellRenderDefaultSettingsButton.clicked.connect(self.settingsCellRenderBackToDefault)
        self.settingsCellRenderDefaultSettingslayoutDontMessWith = QHBoxLayout()
        
        self.settingsCellRenderDefaultSettingslayoutDontMessWith.addWidget(self.settingsCellRenderDefaultSettingsButton)

        self.settingsCellRenderDefaultSettingslayoutDontMessWith.setContentsMargins(0,10,0,10)
        self.settingsMainLayout.addLayout(self.settingsCellRenderDefaultSettingslayoutDontMessWith)
        


        #endregion

    #region QoL
    def addPairToMainLayout(self,thing1,thing2,innerMargin:int):
        layout = QHBoxLayout()
        layout.addWidget(thing1,stretch=1,alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(thing2,stretch=100,alignment=Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(innerMargin)
        layout.setContentsMargins(0,0,0,0)
        self.settingsMainLayout.addLayout(layout)
        return layout

    def updateGraph(self): #It takes too damn long to type something i use constantly
        updateGraphSignalEmitterId.updateGraphSignal.emit()

    def addHeader(self,title,margin):
        header = QLabel()
        header.setText(title)
        header.setContentsMargins(0,margin,0,margin)
        self.settingsMainLayout.addWidget(header,alignment=Qt.AlignmentFlag.AlignHCenter  )
    #endregion

    #region slots that connect to the ui elements
    def settingsCellRenderBackToDefault(self):
        self.widgetOwner.myCell.cellRenderingData.backToDefaultSettings()
        #region set all the fucking ui elements to default and update them
        self.settingsGraphCellCheckBox.setChecked(self.widgetOwner.myCell.cellRenderingData.renderCell) #render anything at all
        self.settingsCellRenderColorTextEdit.setText(self.widgetOwner.myCell.cellRenderingData.renderColor) #render color
        self.settingsCellRenderDetailLineEdit.setText(str(self.widgetOwner.myCell.cellRenderingData.renderDetail)) #nerd shit 1 detial
        self.settingsGraphDiscontinuitiesCheckBox.setChecked(self.widgetOwner.myCell.cellRenderingData.renderDiscontinuities) #nerd shit 2 render discoudfskldsf however you spell it
        #endregion

        self.updateGraph()

    def settingsCellRenderColorTextEditUpdate(self):
        self.widgetOwner.myCell.cellRenderingData.renderColor = self.settingsCellRenderColorTextEdit.text()
        self.updateGraph()

    def settingsCellRenderDetailTextEditUpdate(self):
        try:
            self.widgetOwner.myCell.cellRenderingData.renderDetail = int(self.settingsCellRenderDetailLineEdit.text())
            self.updateGraph()
        except:
            pass

    def settingsGraphCellCheckBoxCLicked(self):
        self.widgetOwner.myCell.setRenderCell(self.settingsGraphCellCheckBox.isChecked())
        self.updateGraph()

    def settingsGraphDiscontinuitiesCheckBoxCLicked(self):
        self.widgetOwner.myCell.cellRenderingData.renderDiscontinuities =  (self.settingsGraphDiscontinuitiesCheckBox.isChecked())
        self.updateGraph()
    #endregion

    #region opening and closing the damn window

    def open(self):
        try: self.setWindowTitle('cell ' + str(self.widgetOwner.myCell.getCellIndex() + 1) + " settings editor")
        except: pass
        self.show()

    def close(self):
        self.hide()

    def closeEvent(self,event):

        self.widgetOwner.settingsShow = False
        event.accept()

    #endregion



#endregion


#useful stuff
#region

def makeCellToLineEdit(cell):

    newLineEdit = QLineEdit()
    newLineEdit.setText(cell_manager.getCellContent(cell))
    return newLineEdit

def clearLayout(layout):
    for i in reversed(range(layout.count())):
        layout.removeItem(layout.itemAt(i))

def despaceString(content):
    output = ''
    for i in content:
        if(i != ' '): output += i

    return output

#endregion




#ui
class graphCanvas(FigureCanvas):
    def __init__(self,parent=None):
        self.xRange = 20
        self.yRange = 13
        self.PixToX = .01
        self.PixToY = .02
        self.graphCamCenter = [0,0]
        self.changeTolerance = 1
        self.limitStep = .01
        self.definitionsAndDefiners = {}
        
        self.inputRemap = {
            #region constants
            'pi': pi,
            'tau':2*pi,
            'e':e,
            #endregion

            #region general funcs
            'ln': log,
            'log':log10,
            'logBase': lambda x,b: log(x)/log(b),
            'exp':exp,
            'abs':abs,
            "gamma":math.gamma,
            "ceil":math.ceil,
            "floor":math.floor,
            "nCr":lambda n,r:math.gamma(n+1)/(math.gamma(n-r+1)*math.gamma(r+1)),
            "nPr":lambda n,r:math.gamma(n+1)/(math.gamma(n-r+1)),
            "root":lambda x,r:x**(1/r),
            "sqrt": lambda x:x**.5,
            # "sum":lambda expression,min,max:1

            #endregion

            #region trig
            'sin': sin,
            'cos':cos,
            'tan':tan,
            'cot': lambda x :1/tan(x),
            'arccot': lambda x :pi/2 -arctan(x),
            'csc': lambda x :1/sin(x),
            'arccsc': lambda x :arcsin(1/x),
            'sec': lambda x :1/cos(x),
            'arcsec': lambda x :arccos(1/x),
            'arctan':arctan,
            'arccos':arccos,
            'arcsin':arcsin,
            #endregion
            
            #region nuh uh funcs
            'print':None,
            'dir':None,
            'del':None,
            #endregion
        }
        

        self.Dpi = 100
        self.fig = Figure(figsize=(5,4),dpi=self.Dpi)
        self.ax = self.fig.add_subplot()

        self.preSize = self.fig.get_size_inches()

        super().__init__(self.fig)
        self.setParent(parent)

        self.reset_axies()

    def reset_axies(self):
        self.ax.cla()
        self.fig.set_facecolor(designSettings.graphScreenColor)
        self.ax.set_facecolor(designSettings.graphScreenColor)
        self.ax.set_xlim(-self.xRange/2  + self.graphCamCenter[0],self.xRange/2  + self.graphCamCenter[0])
        self.ax.set_ylim(-self.yRange/2 + self.graphCamCenter[1],self.yRange/2 + self.graphCamCenter[1])
        self.ax.grid(color=designSettings.graphScreengGridColor)
        self.ax.axhline(y=0,color = designSettings.graphScreengAxiesColor)
        self.ax.axvline(x=0,color = designSettings.graphScreengAxiesColor)
        
    def funcValFromString(self,funcString,x):
        
        return eval(funcString,{'x':x},self.inputRemap | self.definitionsAndDefiners)

    #region define shit procedually
    def defineCellVariable(self,cell:cellClass):
        currentType = cell.myCellType
        currentName = (currentType.getDefiningName())
        currentDefiner = (currentType.getDefiningExpression())

        
        if(currentName not in self.inputRemap or currentName != 'x' ):
            try: 
                #eval(funcString,{'x':x},self.inputRemap | self.definitionsAndDefiners)
                self.definitionsAndDefiners.update({currentName : float(eval(currentDefiner,self.inputRemap | self.definitionsAndDefiners))})
                runString = 'global ' + currentName + ';'  #say var is global 
                runString += currentType.getName + ' = ' + currentDefiner #set var
                exec(runString,self.inputRemap | self.definitionsAndDefiners)
            except: pass

            cell.myCellWidget.updateCellValPanel()

    def defineCellExplicitFunc(self,cell:cellClass):
        #TODO fix this shit
        currentType = cell.myCellType
        currentName = currentType.getDefiningName()
        currentDefiner = currentType.getDefiningExpression()


        # try: 
            #eval(funcString,{'x':x},self.inputRemap | self.definitionsAndDefiners)
        funcDefineString = f"""
def {currentName}(x): 
    return {currentDefiner}
        """
        
        if(currentName not in self.inputRemap):
            try:
                scope = {}
                scope |= self.inputRemap | self.definitionsAndDefiners
                exec(funcDefineString,scope,scope)
                actualFunc = scope[currentName]

                self.definitionsAndDefiners.update({currentName : actualFunc})

                return actualFunc
            except:pass
    #endregion

    #region draw stuff
    def drawPlot(self,func,renderSettings: cell_manager.cellRenderData):
        
        # collection = cell_grapher.getListOfTrueVerticesForExplict(func,int(self.ax.get_xbound()[0]),int(self.ax.get_xbound()[1]))
        try:
            detail = renderSettings.renderDetail
            original_input_vals = numpy.linspace(-self.xRange/2 + self.graphCamCenter[0],self.xRange/2 + self.graphCamCenter[0],detail)
            step = self.xRange/detail

            input_vals = []
            output_vals = []

            current_output_list = []
            current_input_list = []



            for i in original_input_vals:


                isValid = False
                #basic incontinuity
                try:
                    val = self.funcValFromString(func,i)
                    isValid = True
                except:
                    isValid = False

                #semi discontinouty test aka asymptotes
                if(not renderSettings.renderDiscontinuities):
                    
                    #actual discounity test
                    try:
                        leftSide = (self.funcValFromString(func,i-self.limitStep))
                        rightSide = (self.funcValFromString(func,i+self.limitStep ))
                        bullShitLimit = (leftSide+rightSide)/2
                        if numpy.abs(bullShitLimit-val) > self.changeTolerance:
                            isValid = False
                    except:
                        isValid = False

                    
                    #if off screen then not draw
                    try:
                        
                        if( math.sqrt((val-self.graphCamCenter[1])**2) > self.yRange): isValid = False
                    except:
                        isValid = False
                    
                
                if not isValid: #make a new draw batch
                    
                    output_vals.append(current_output_list)
                    input_vals.append(current_input_list)
                    current_output_list = []
                    current_input_list = []
                else: #add to current batch
                    
                    current_output_list.append(val)
                    current_input_list.append(i)

            output_vals.append(current_output_list)
            input_vals.append(current_input_list)

            for j in range(len(output_vals)):
                self.ax.plot(input_vals[j],output_vals[j],renderSettings.renderColor)
            



        except:
            pass
            # print('fucka you')

    def drawFuncLiterally(self,func,renderSettings: cell_manager.cellRenderData):
        try:
            detail = renderSettings.renderDetail
            original_input_vals = numpy.linspace(-self.xRange/2 + self.graphCamCenter[0],self.xRange/2 + self.graphCamCenter[0],detail)
            step = self.xRange/detail

            input_vals = []
            output_vals = []

            current_output_list = []
            current_input_list = []



            for i in original_input_vals:


                isValid = False
                #basic incontinuity
                try:
                    val = func(i)
                    isValid = True
                except:
                    isValid = False

                #semi discontinouty test aka asymptotes
                if(not renderSettings.renderDiscontinuities):
                    
                    #actual discounity test
                    try:
                        leftSide = (func(i-self.limitStep))
                        rightSide = (func(i+self.limitStep ))
                        bullShitLimit = (leftSide+rightSide)/2
                        if numpy.abs(bullShitLimit-val) > self.changeTolerance:
                            isValid = False
                    except:
                        isValid = False

                    
                    #if off screen then not draw
                    try:
                        
                        if( math.sqrt((val-self.graphCamCenter[1])**2) > self.yRange): isValid = False
                    except:
                        isValid = False
                    
                
                if not isValid: #make a new draw batch
                    
                    output_vals.append(current_output_list)
                    input_vals.append(current_input_list)
                    current_output_list = []
                    current_input_list = []
                else: #add to current batch
                    
                    current_output_list.append(val)
                    current_input_list.append(i)

            output_vals.append(current_output_list)
            input_vals.append(current_input_list)

            for j in range(len(output_vals)):
                self.ax.plot(input_vals[j],output_vals[j],renderSettings.renderColor)
        except:
            pass

    def drawCell(self,cell):
        func = cell.getCellContent()
        self.drawPlot(func,cell.cellRenderingData)
    #endregion

    def updateGraph(self):
        cell_manager.updateCells()

        for i in self.definitionsAndDefiners:
            try: exec('del ' + i)
            except: pass
        
        self.definitionsAndDefiners.clear()

        self.redrawAllCells()

    def redrawAllCells(self):
        self.reset_axies()

        for i in cellWidgetManagerId.myCellWidgets:
            i = i.myCell
            currentType = i.myCellType
            if(isinstance(currentType,cell_manager.cellTypeExplicitRenderableExpression)):
                if(i.getCellContent() != '' and i.getRenderCell()):
                    self.drawCell(i)
            if(isinstance(currentType,cell_manager.cellTypeVariableDefinition)):
                self.defineCellVariable(i)
            if(isinstance(currentType,cell_manager.cellTypeExplicitFunctionDefinition)):
                self.drawFuncLiterally(self.defineCellExplicitFunc(i),i.cellRenderingData)
            if(isinstance(currentType,cell_manager.cellTypeComputableNonIndependentExpression)):
                i.myCellWidget.updateCellValPanel()
                # print(str(i.getCellIndex())+ " " + str(i.myCellWidget.text()))
        
        self.fig.canvas.draw()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        newSize = self.fig.get_size_inches()

        yChange = (newSize[1] - self.preSize[1])*self.Dpi*self.PixToY
        xChange = ((newSize[0] - self.preSize[0])*self.Dpi*self.PixToX)/designSettings.graphScreenWidthPercent
        
        self.xRange += xChange
        self.yRange += yChange

        self.reset_axies()
        graphScreen.redrawAllCells()

        self.preSize = newSize



class projectSettingsWindowClass(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("project settings")
        self.sizeMin = [400,300]
        self.setFixedSize(QSize( self.sizeMin[0] , self.sizeMin[1] )   )

        self.settingsMainLayout = QVBoxLayout()
        self.settingsMainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)


        
        #no touchy
        #region

        # bullshit that is needed to get settings to scroll that doesn't even work 
        #region
        self.settingsGroupBox = QGroupBox()
        self.settingsScroll = QScrollArea()

        self.settingsGroupBox.setLayout(self.settingsMainLayout)
        self.settingsScroll.setWidget(self.settingsGroupBox)
        self.settingsScroll.setWidgetResizable(True)
        self.settingsScroll.setAlignment(Qt.AlignmentFlag.AlignRight)
        # self.settingsMainLayout.sizeHint
        #endregion
        


        # some other bullshit that is needed in order to actually have the settings to scroll for whatever reason
        #region
        policy = QSizePolicy.Policy.Expanding
        # self.settingsGroupBox.setSizePolicy(policy,policy)
        self.settingsScroll.setSizePolicy(policy,policy)
        # self.setSizePolicy(policy,policy)
        # self.
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(self.settingsScroll)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)
        #endregion
        
        #endregion


        #graph cam center
        #region
        self.graphCamCenterXLayout = QHBoxLayout()
        self.graphCamCenterXLabel = QLabel()
        self.graphCamCenterXEnter = QLineEdit()
        self.graphCamCenterXLabel.setText("graph camera x pos ")

        self.graphCamCenterXLayout.addWidget(self.graphCamCenterXLabel,alignment=Qt.AlignmentFlag.AlignLeft)
        self.graphCamCenterXLayout.addWidget(self.graphCamCenterXEnter,alignment=Qt.AlignmentFlag.AlignLeft)
        self.graphCamCenterXLayout.setSpacing(3)

        self.graphCamCenterXEnter.setText(str(graphScreen.graphCamCenter[0]))

        self.graphCamCenterYLayout = QHBoxLayout()
        self.graphCamCenterYLabel = QLabel()
        self.graphCamCenterYEnter = QLineEdit()
        self.graphCamCenterYLabel.setText("graph camera y pos ")

        self.graphCamCenterYLayout.addWidget(self.graphCamCenterYLabel,alignment=Qt.AlignmentFlag.AlignRight)
        self.graphCamCenterYLayout.addWidget(self.graphCamCenterYEnter,alignment=Qt.AlignmentFlag.AlignRight)
        self.graphCamCenterYLayout.setSpacing(3)

        self.graphCamCenterYEnter.setText(str(graphScreen.graphCamCenter[1]))

        self.graphCamCenterXEnter.textEdited.connect(self.updateGraphCamCenter)
        self.graphCamCenterYEnter.textEdited.connect(self.updateGraphCamCenter)

        self.addPairToMainLayout(self.graphCamCenterXLayout,self.graphCamCenterYLayout,35)
        
        #endregion
        
    def updateGraph(self): #It takes too damn long to type something i use constantly
        updateGraphSignalEmitterId.updateGraphSignal.emit()

    def addHeader(self,title,margin):
        header = QLabel()
        header.setText(title)
        header.setContentsMargins(0,margin,0,margin)
        self.settingsMainLayout.addWidget(header,alignment=Qt.AlignmentFlag.AlignHCenter  )
    
    def updateGraphCamCenter(self):
        try:
            graphScreen.graphCamCenter[0] = float(self.graphCamCenterXEnter.text())
            graphScreen.graphCamCenter[1] = float(self.graphCamCenterYEnter.text())
            self.updateGraph()
        except:pass

    def addPairToMainLayout(self,thing1,thing2,innerMargin:int):
        layout = QHBoxLayout()
        if(isinstance(thing1,QLayout)):
            layout.addLayout(thing1)
            layout.addLayout(thing2)
        else:
            layout.addWidget(thing1,stretch=1,alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(thing2,stretch=1,alignment=Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(innerMargin)
        layout.setContentsMargins(0,0,0,0)
        self.settingsMainLayout.addLayout(layout)
        return layout
    
    def closeEvent(self,event):
        mainWindow.projectSettingsWindowActive = False
        event.accept()

    def showEvent(self,event):
        self.graphCamCenterXEnter.setText(str(graphScreen.graphCamCenter[0]))
        self.graphCamCenterYEnter.setText(str(graphScreen.graphCamCenter[1]))
        event.accept()



class MainWindowClass(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(MinWindowWidth )
        self.setMinimumHeight(MinWindowHeight)
        self.setStyleSheet("background-color: " + designSettings.mainColor + ";")

        self.setWindowTitle(appName)
        self.setGeometry(0,0,windowWidth,windowHeight) # the first 2 argurements are the pos of the top left corner of the window
        self.setWindowIcon(QIcon(appIconImagePath))




        self.initUI()

    def initUI(self):

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        #region setup
        global topBar
        global graphScreen
        global cellEditorScreen
        
        topBar = QHBoxLayout(self)
        graphScreen = graphCanvas(self)
        

        self.cellEditorScreenWrapper = QGroupBox()
        cellEditorScreen = QVBoxLayout()
        self.cellEditorScroll = QScrollArea()

        self.cellEditorScreenWrapper.setLayout(cellEditorScreen)
        self.topBarHeight = int(windowHeight/15)

        self.cellEditorScreenWrapper.setStyleSheet('border: 1px solid {0};border-left: 0px solid {0}'.format(designSettings.cellTextEditAreaBorderColor))

        self.cellEditorScroll.setWidgetResizable(True)
        self.cellEditorScroll.setWidget(self.cellEditorScreenWrapper)
        cellEditorScreen.setAlignment(Qt.AlignmentFlag.AlignTop)

        # self.cellEditorScreenWrapper.setStyleSheet("margin: 5px solid {0}".format(designSettings.cellEditAreaBorderColor))
        
        
        self.addEmptyCellComplete()

        #region button stuff

        #region button to add more cells
        
        self.addCellButton = QPushButton()
        self.addCellButton.setFixedHeight(self.topBarHeight)
        self.addCellButton.setText('Add Cell')
        tempStyleSheet = """background-color: {0};
        border: 2px solid {1};
        padding-right: 15px ;
        padding-left: 15px  ;
        border-radius: {2};""".format(designSettings.mainBarButtonColor,designSettings.mainButtonBorderColor,designSettings.mainButtonEdgeRadius)
        self.addCellButton.setStyleSheet(tempStyleSheet)
        #endregion

        #region project settings button
        self.projectSettingsButton = QPushButton()
        self.projectSettingsButton.setFixedHeight(self.topBarHeight)
        self.projectSettingsButton.setText('project settings')
        tempStyleSheet2 = """background-color:{0};
        border: 2px solid {1};
        padding-right: 15px ;
        padding-left: 15px  ;
        border-radius: {2}""".format(designSettings.mainBarButtonColor,designSettings.mainButtonBorderColor,designSettings.mainButtonEdgeRadius)
        self.projectSettingsButton.setStyleSheet(tempStyleSheet2)
        #endregion

        #region help settings button
        self.helpButton = QPushButton()
        self.helpButton .setFixedHeight(self.topBarHeight)
        self.helpButton .setText('HELP')
        tempStyleSheet3 = """background-color:{0};
        border: 2px solid {1};
        padding-right: 15px ;
        padding-left: 15px  ;
        border-radius: {2};""".format(designSettings.mainBarButtonColor,designSettings.mainButtonBorderColor,designSettings.mainButtonEdgeRadius)
        self.helpButton .setStyleSheet(tempStyleSheet3)
        #endregion

        #region project settings window
        self.projectSettingsWindow = projectSettingsWindowClass()
        self.projectSettingsWindowActive = False
        self.projectSettingsWindow.setHidden(True)
        #endregion



        self.addCellButton.clicked.connect(self.addEmptyCellComplete)
        self.projectSettingsButton.clicked.connect(self.clickedProjectSettingsButton)
        self.helpButton.clicked.connect(self.clickedHelpButton)

        # topBar.addWidget(self.projectSettingsButton, alignment=PyQt5.QtCore.Qt.AlignmentFlag.AlignLeft)
        # topBar.addWidget(self.helpButton, alignment=PyQt5.QtCore.Qt.AlignmentFlag.AlignLeft)
        self.projectButtonsLayout = QHBoxLayout()
        self.projectButtonsLayout.addWidget(self.projectSettingsButton, alignment=PyQt5.QtCore.Qt.AlignmentFlag.AlignRight)
        self.projectButtonsLayout.addWidget(self.helpButton, alignment=PyQt5.QtCore.Qt.AlignmentFlag.AlignRight)



        topBar.addWidget(self.addCellButton, alignment=PyQt5.QtCore.Qt.AlignmentFlag.AlignRight)
        topBar.setSpacing(0)
        topBar.setContentsMargins(0,designSettings.topBarVmargin,0,designSettings.topBarVmargin)
        # topBar.setAlignment(PyQt5.QtCore.Qt.AlignmentFlag.AlignCenter)  

        self.projectButtonsLayout.setStretch(0,20)
        self.projectButtonsLayout.setStretch(1,1)
        self.projectButtonsLayout.setSpacing(0)
        self.projectButtonsLayout.setContentsMargins(0,designSettings.projectButtonsLayoutVmargin,0,designSettings.projectButtonsLayoutVmargin)

        #endregion

        # self.cellEditorEntiretyLayout = QVBoxLayout()
        # self.cellEditorEntiretyLayout.addLayout(topBar)
        # self.cellEditorEntiretyLayout.addWidget(self.cellEditorScroll)



        #endregion

        
        #region finsih up


        self.editingLayout = QHBoxLayout()
        self.mainLayout = QVBoxLayout()

        policy = QSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.cellEditorScroll.setSizePolicy(policy)
        

        self.graphScreenEntiretyWrapper = QVBoxLayout()
        self.graphScreenEntiretyWrapper.addWidget(graphScreen)
        self.graphScreenEntiretyWrapper.addLayout(self.projectButtonsLayout)
        self.graphScreenEntiretyWrapper.setSpacing(0)
        self.graphScreenEntiretyWrapper.setContentsMargins(0,0,0,0)

        self.editingLayout.addLayout(self.graphScreenEntiretyWrapper)
        self.editingLayout.addWidget(self.cellEditorScroll)
        
        #make the sizing not stupid
        self.editingLayout.setSpacing(0)
        self.editingLayout.setContentsMargins(0,0,0,0)
        
        #Qt.AlignmentFlag.AlignTop
        self.mainLayout.addLayout(topBar,0)
        self.mainLayout.addLayout(self.editingLayout,1)

        self.editingLayout.setStretch(0, int(designSettings.graphScreenWidthPercent*100))
        self.editingLayout.setStretch(1, int((1-designSettings.graphScreenWidthPercent)*100))

        #make the sizing not stupid 2 electric boogaloo
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mainLayout.setSpacing(0)
        #endregion

        self.centralWidget.setLayout(self.mainLayout)

    def clickedProjectSettingsButton(self):
        if(self.projectSettingsWindowActive):
            self.projectSettingsWindow.hide()
        else:
            self.projectSettingsWindow.show()

        self.projectSettingsWindowActive = not self.projectSettingsWindowActive

    def clickedHelpButton(self):
        webbrowser.open_new(helpPdfFileLink)

    def addEmptyCellComplete(self):
        temp2 = cellClass('',0)
        temp2.getCellIndex() # funny enough this updates the index
        temp2.cellRenderingData.renderColor = designSettings.cellRandomColors[random.randint(0,len(designSettings.cellRandomColors) - 1)]
        cellWidgetManagerId.addCellToCellEditorScreen(temp2)

    def closeEvent(self, a0):
        app.closeAllWindows()
        app.quit()
        a0.accept()

#main logic loop 
#region


class programEventLoopThreadClass(QObject):



    def run(self):
        cell_manager.bootUpCellManager()
        
        programEventLoop(self)   

def programEventLoop(orignator):
    pass
    # global seconds
    # seconds = 0
    # while(True):
    #     time.sleep(.01)
    #     seconds = time.time() - start
    #     # cell_manager.updateCells()






#endregion   
   
# update UI loop 
#region


class guiUpdateLoopThreadClass(QObject):
    def __init__(self):
        super().__init__()
        self.addCellToCellEditorCommuncator = addCellToCellEditorSignalEmitter()
        self.updateGraphCommuncator = updateGraphSignalEmitterId

    def emitSignalToAddCellToCellEditor(self,cell):
        self.addCellToCellEditorCommuncator.addCellToCellEditorSignal.emit(cell)

    def emitSignalUpdateGraph(self):
        self.updateGraphCommuncator.updateGraphSignal.emit()


    def run(self):
        
        self.guiUpdateEventLoop()


    def guiUpdateEventLoop(self): # i may be the orignator but ... he is the duplicator -coachwilkes 2024
        pass
        # while(True): 
        #     time.sleep(.1)
        #     # if(cell_manager.checkIfGraphNeedUpdating()): self.emitSignalUpdateGraph()

        

    
#endregion   
   


def startProgram():
    global app
    global mainWindow
    global cellWidgetManagerId
    cellWidgetManagerId = cellWidgetManager()
    app = None
    mainWindow = None

    addCellToCellEditorSignalEmitterId.addCellToCellEditorSignal.connect(cellWidgetManagerId.addCellToCellEditorScreen)

    # global threadManager
    # threadManager = threadController()

    app = QApplication(sys.argv)
    
    mainWindow = MainWindowClass()
    
    updateGraphSignalEmitterId.updateGraphSignal.connect(graphScreen.updateGraph)
    updateGraphSignalEmitterId.updateGraphSignal.emit()



    mainWindow.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__": #no idea how this works it just does
    startProgram()


