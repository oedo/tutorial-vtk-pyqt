from __future__ import print_function
import os
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PySide6 import QtWidgets, QtGui


class GlyphViewerApp(QtWidgets.QMainWindow):
    def __init__(self, data_dir):
        #Parent constructor
        super(GlyphViewerApp,self).__init__()
        self.vtk_widget = None
        self.ui = None
        self.setup(data_dir)

    def setup(self, data_dir):
        import glyph_ui
        self.ui = glyph_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.vtk_widget = QGlyphViewer(self.ui.vtk_panel, data_dir)
        self.ui.vtk_layout = QtWidgets.QHBoxLayout()
        self.ui.vtk_layout.addWidget(self.vtk_widget)
        self.ui.vtk_layout.setContentsMargins(0,0,0,0)
        self.ui.vtk_panel.setLayout(self.ui.vtk_layout)

    def initialize(self):
        self.vtk_widget.start()

class QGlyphViewer(QtWidgets.QFrame):
    def __init__(self, parent, data_dir):
        super(QGlyphViewer,self).__init__(parent)

        # Make tha actual QtWidget a child so that it can be re parented
        interactor = QVTKRenderWindowInteractor(self)
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(interactor)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # Read the data
        xyx_file = os.path.join(data_dir, "combxyz.bin")
        q_file = os.path.join(data_dir, "combq.bin")
        pl3d = vtk.vtkMultiBlockPLOT3DReader()
        pl3d.SetXYZFileName(xyx_file)
        pl3d.SetQFileName(q_file)
        pl3d.SetScalarFunctionNumber(100)
        pl3d.SetVectorFunctionNumber(202)
        pl3d.Update()

        blocks = pl3d.GetOutput()
        b0 = blocks.GetBlock(0)

        # Setup VTK environment
        renderer = vtk.vtkRenderer()
        render_window = interactor.GetRenderWindow()
        render_window.AddRenderer(renderer)

        interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        render_window.SetInteractor(interactor)
        renderer.SetBackground(0.2,0.2,0.2)

        # Draw Outline
        outline = vtk.vtkStructuredGridOutlineFilter()
        outline.SetInputData(b0)
        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        outline_actor = vtk.vtkActor()
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(1,1,1)
        renderer.AddActor(outline_actor)
        renderer.ResetCamera()

        # Draw Outline
        outline = vtk.vtkStructuredGridOutlineFilter()
        outline.SetInputData(b0)
        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        outline_actor = vtk.vtkActor()
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(1,1,1)
        renderer.AddActor(outline_actor)
        renderer.ResetCamera()

        # Threshold points
        threshold = vtk.vtkThresholdPoints()
        threshold.SetInputData(b0)
        threshold.ThresholdByUpper(0.5)

        # Draw arrows
        arrow = vtk.vtkArrowSource()
        glyphs = vtk.vtkGlyph3D()
        glyphs.SetInputData(b0)
        glyphs.SetSourceConnection(arrow.GetOutputPort())
        glyphs.SetInputConnection(threshold.GetOutputPort())

        glyphs.SetVectorModeToUseVector()
        glyphs.SetScaleModeToScaleByVector()
        glyphs.SetScaleFactor(0.005)
        glyphs.SetColorModeToColorByVector()

        # Mapper
        glyph_mapper =  vtk.vtkPolyDataMapper()
        glyph_mapper.SetInputConnection(glyphs.GetOutputPort())
        glyph_actor = vtk.vtkActor()
        glyph_actor.SetMapper(glyph_mapper)

        glyph_mapper.UseLookupTableScalarRangeOn()
        renderer.AddActor(glyph_actor)

        # Set color lookuptable
        glyphs.Update()
        s0,sf = glyphs.GetOutput().GetScalarRange()
        lut = vtk.vtkColorTransferFunction()
        lut.AddRGBPoint(s0, 1,0,0)
        lut.AddRGBPoint(sf, 0,1,0)
        glyph_mapper.SetLookupTable(lut)

        self.b0 = b0
        self.renderer = renderer
        self.interactor = interactor
        self.threshold = threshold

    def start(self):
        self.interactor.Initialize()
        self.interactor.Start()

if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))

    # # Recompile ui
    # with open("glyph_view.ui") as ui_file:
    #     with open("glyph_ui.py","w") as py_ui_file:
    #         uic.compileUi(ui_file,py_ui_file)

    app = QtWidgets.QApplication([])
    main_window = GlyphViewerApp("volume")
    main_window.show()
    main_window.initialize()
    app.exec_()
