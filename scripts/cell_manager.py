# from PyQt5 import *

global cellList
cellList = []

#region useful stuff
def containerHas(container,thing):
    has = False
    for i in container:
        if(i == thing):
            has = True
            break

    return has

def deSpaceString(string):
    output = ''
    for char in string:
        if(not char == ' '): output += char

    return output

def addEmptycell():

    newCell = cell("",len(cellList))
    newCell.setCellContent("")
    newCell = cellList.append(newCell)
    return newCell
    

def bootUpCellManager():
    global cellList 
    cellList = []

def updateCells():
    for item in cellList:
        item.setContentToCellWidgetContent()
        item.myCellType.updateType()


#endregion
#region buncho classes

class cell:
    def __init__(self,contents,index):
        self.cellContent = contents
        self.cellIndex = index
        self.cellRenderingData = cellRenderData()
        self.myCellLineEdit = None
        self.myCellWidget= None
        self.myCellType = cellNoType(self)

        cellList.append(self)

    #region getters setters
    def setContentToCellWidgetContent(self):
        if(self.myCellLineEdit != None):
            self.cellContent = self.myCellLineEdit.text()

    def setCellWidget(self,widget):
        self.myCellLineEdit = widget

    
    def setCellContent(self,content):
        self.cellContent = content

    def getCellContent(self):
        return self.cellContent
    
    def getCellIndex(self):
        try: self.cellIndex = cellList.index(self)
        except: pass
        return self.cellIndex
    
    def setRenderCell(self,render):
        self.cellRenderingData.renderCell = render

    def getRenderCell(self):
        return self.cellRenderingData.renderCell
    #endregion


#region cell type shit


#region the abstract parents in the hierarchy
class cellType:
    def __init__(self,cell:cell = None):
        self.typeName = 'cellTypeBase : this is an abstract cellType you should not be seeing this'
        self.shouldRender = False
        self.myCell = cell

    def updateType(self):
        
        if(self.myCell != None):
            
            newType = cellNoType(self.myCell)
            content = self.myCell.getCellContent()

            if(content != ''):
                

                if(containerHas(content,'=')):
                    try:
                        if(containerHas(content,'(')):
                            if(content.index('(') < content.index('=')):
                                newType = cellTypeExplicitFunctionDefinition(self.myCell)
                            else:
                                if(deSpaceString( content[:content.index('=')]) != 'x'):
                                    newType = cellTypeVariableDefinition(self.myCell)
                        else:
                            newType = cellTypeVariableDefinition(self.myCell)
                    except:
                        newType = cellTypeDefinition(self.myCell)

                        
                else:
                    if(containerHas(content,'x')):
                        newType = cellTypeExplicitRenderableExpression(self.myCell)
                    else:
                        newType = cellTypeComputableNonIndependentExpression(self.myCell)

            self.myCell.myCellType = newType
            del self

class cellNoType(cellType):


    def __init__(self, cell: cell  = None):
        super().__init__(cell)
        self.typeName = 'no type'

class cellTypeExpression(cellType):
    def __init__(self,cell  = None):
        super().__init__(cell)
        self.typeName = "cellTypeExpression : this is an abstract cellType you should not be seeing this"   
        
class cellTypeDefinition(cellType):
    def __init__(self,cell  = None):
        super().__init__(cell)
        self.typeName = "cellTypeDefintion : this is an abstract cellType you should not be seeing this"   

    def getDefiningName(self):
        output = ''
        for i in self.myCell.getCellContent():
            if(i == '=' or i == '('): return deSpaceString(output )
                
            output += i
        return deSpaceString(output)

    def getDefiningExpression(self):
        equalIndex = self.myCell.getCellContent().index('=')
        return deSpaceString(self.myCell.getCellContent()[equalIndex +1:])

#endregion



#region cell types you are actually going to see

class cellTypeExplicitRenderableExpression(cellTypeExpression):
    def __init__(self,cell  = None):
        super().__init__(cell)
        self.typeName = "explicit expression"   
        self.shouldRender = True

class cellTypeComputableNonIndependentExpression(cellTypeExpression):
    def __init__(self,cell  = None):
        super().__init__(cell)
        self.typeName = "computable non independent expression"   
        self.shouldRender = False

    def computeExpression(self,funcRemap):
        return float(eval(self.myCell.cellContent,funcRemap))
        

class cellTypeVariableDefinition(cellTypeDefinition):
    def __init__(self,cell  = None):
        super().__init__(cell)
        self.typeName = "variable definition"  


        
        

class cellTypeExplicitFunctionDefinition(cellTypeDefinition):
    def __init__(self,cell  = None):
        super().__init__(cell)
        self.typeName = "explicit function definition" 
        self.shouldRender = True 


#endregion


#endregion


class cellRenderData:
    def __init__(self):
        self.backToDefaultSettings()

    def backToDefaultSettings(self):
        self.renderCell = True
        self.renderColor =  '#ff0000'
        self.renderDetail = 250
        self.renderDiscontinuities = False


#endregion

#region rest of this shit

def getCellContent(cell:cell):
    return cell.cellContent

def getCellIndex(cell:cell):
    return cell.cellIndex

def addCellToBottom(contents: str):
   newCell = cell(contents,len(cellList))
   cellList.append(newCell)
   return newCell


def checkIfGraphNeedUpdating():
    needUpdating = False


    for j in cellList:
        original_content = j.getCellContent()
        j.setContentToCellWidgetContent()
        new_content = j.getCellContent()

        if not original_content == new_content: needUpdating = True

    return needUpdating


def deleteCell(cell:cell):
    try:
        updateCells()
        cellList.pop(cell.getCellIndex())
        # del cell.cellRenderingData
        # del cell

    except:
        pass
#endregion



