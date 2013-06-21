from __main__ import vtk, qt, ctk, slicer
import SimpleITK as sitk
import sitkUtils as su

#
# ForceIsotropic
#

class ForceIsotropic:
  def __init__(self, parent):
    parent.title = "Force Isotropic"
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Athena Lyons ",
                           "Hans Johnson"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Adjusts the slice thickness of the input volume and makes it isotropic.
    """
    parent.acknowledgementText = """
    This file was originally developed by Hans Johnson
 and Athena Lyons at the Slice Summer Project week 2013""" # replace with organization, grant and thanks.
    self.parent = parent

#
# qAdjustThicknessWidget
#

class ForceIsotropicWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Collapsible button
    self.adjustCollapsibleButton = ctk.ctkCollapsibleButton()
    self.adjustCollapsibleButton.text = "Adjust Slice Thickness"
    self.layout.addWidget(self.adjustCollapsibleButton)
    
    # Layout within the adjust Slice Thickness inputs collapsible button
    self.adjustFormLayout = qt.QFormLayout(self.adjustCollapsibleButton)

    #
    # the volume and spacing selectors
    #
    self.inputFrame = qt.QFrame(self.adjustCollapsibleButton)
    self.inputFrame.setLayout(qt.QHBoxLayout())
    self.adjustFormLayout.addWidget(self.inputFrame)
    self.inputSelector = qt.QLabel("Input Volume: ", self.inputFrame)
    self.inputFrame.layout().addWidget(self.inputSelector)
    self.inputSelector = slicer.qMRMLNodeComboBox(self.inputFrame)
    self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputFrame.layout().addWidget(self.inputSelector)
    
    self.SpacingFrame = qt.QFrame(self.adjustCollapsibleButton)
    self.SpacingFrame.setLayout(qt.QHBoxLayout())
    self.adjustFormLayout.addWidget(self.SpacingFrame)
    self.SpinBox = qt.QLabel("New  Slice Thickness: ", self.SpacingFrame)
    self.SpacingFrame.layout().addWidget(self.SpinBox)
    self.SpinBox = ctk.ctkSpinBox()
    self.SpinBox.decimals = 5
    self.SpacingFrame.layout().addWidget(self.SpinBox)
    
    self.outputFrame = qt.QFrame(self.adjustCollapsibleButton)
    self.outputFrame.setLayout(qt.QHBoxLayout())
    self.adjustFormLayout.addWidget(self.outputFrame)
    self.outputSelector = qt.QLabel("Output Volume: ", self.outputFrame)
    self.outputFrame.layout().addWidget(self.outputSelector)
    self.outputSelector = slicer.qMRMLNodeComboBox(self.outputFrame)
    self.outputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputFrame.layout().addWidget(self.outputSelector)
    
    #Radio button
    self.registrationTypeBox = qt.QGroupBox("Interpolation Type")
    self.registrationTypeBox.setLayout(qt.QFormLayout())
    self.registrationTypeButtons = {}
    self.registrationTypes = ("Linear", "Lanczos")
    for registrationType in self.registrationTypes:
      self.registrationTypeButtons[registrationType] = qt.QRadioButton()
      self.registrationTypeButtons[registrationType].text = registrationType
      self.registrationTypeButtons[registrationType].setToolTip("Pick the type of registration")
      self.registrationTypeBox.layout().addWidget(self.registrationTypeButtons[registrationType])
    self.adjustFormLayout.addWidget(self.registrationTypeBox)
    self.registrationTypeButtons["Linear"].setChecked(True)
    
    # Apply button
    adjustButton = qt.QPushButton("Adjust Slice Thickness")
    adjustButton.toolTip = "Adjusts the thickness of MRI slices in an image"
    self.adjustFormLayout.addWidget(adjustButton)
    adjustButton.connect('clicked(bool)', self.onApply)
    

    # Add vertical spacer
    self.layout.addStretch(1)

    # Set local var as instance attribute
    self.adjustButton = adjustButton

  def onApply(self):
    input = self.inputSelector.currentNode()
    inputVolume = su.PullFromSlicer(input.GetName())
    output = self.outputSelector.currentNode()
    if not (input and output):
      qt.QMessageBox.critical(
          slicer.util.mainWindow(),
          'adjust', 'Input and output volumes to be adjusted')
      return
    if (self.SpinBox.value == 0):
      qt.QMessageBox.critical(
          slicer.util.mainWindow(),
          'spacing', 'spacing can not be zero')
      return
    if(self.registrationTypeButtons["Linear"].isChecked()):
      a = sitk.sitkLinear
    else:
      #a = sitk.sitkLinear
      a = sitk.sitkLanczosWindowedSinc
    # run the filter
    Spacing = self.SpinBox.value
    preSpacing = inputVolume.GetSpacing()
    preOrigin  = inputVolume.GetOrigin()
    preDirection = inputVolume.GetDirection()
    preSize = inputVolume.GetSize()

    dimScale=[0,0,0]
    newSize = [0,0,0]
    for dim in range(0,3):
      dimScale[dim] = preSpacing[dim] / Spacing
      newSize[dim] =  int ( preSize[dim] * dimScale[dim]) + 1
      newSize[dim] =  newSize[dim] + ( newSize[dim] % 2 )
    
    outputVolume = sitk.Resample(inputVolume, newSize, sitk.Transform(), a, preOrigin, [Spacing]*3, preDirection, 0 )
    su.PushToSlicer(outputVolume, output.GetName(), 0, True)
    self.outputSelector.setCurrentNodeID(output.GetID())



