# -*- coding: utf-8 -*-

#******************************************************************************
#
# ShiftPoints
# ---------------------------------------------------------
# Moves overlapped points with same coordinates in a circle around the
# original position.
#
# Copyright (C) 2011 Alexander Bruy (alexander.bruy@gmail.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from shiftpointsdialogbase import Ui_ShiftPointsDialog

import math

class ShiftPointsDialog( QDialog, Ui_ShiftPointsDialog ):
  def __init__( self, iface ):
    QDialog.__init__( self )
    self.setupUi( self )
    self.iface = iface

    self.outFileName = None
    self.outEncoding = None
    self.workThread = None

    self.btnOk = self.buttonBox.button( QDialogButtonBox.Ok )
    self.btnClose = self.buttonBox.button( QDialogButtonBox.Close )

    QObject.connect( self.btnSelectFile, SIGNAL( "clicked()" ), self.outFile )

    self.manageGui()

  def manageGui( self ):
    myVectors = getLayerNames( [ QGis.Point ] )
    self.cmbInputLayer.addItems( myVectors )

  def outFile( self ):
    ( self.outFileName, self.outEncoding ) = saveDialog( self )
    if self.outFileName is None or self.outEncoding is None:
      return
    self.leOutputFile.setText( self.outFileName )

  def accept( self ):
    if self.outFileName is None:
      QMessageBox.warning( self, self.tr( "No output file selected" ),
                           self.tr( "Please specify output filename." ) )
      return

    outFile = QFile( self.outFileName )
    if outFile.exists():
      if not QgsVectorFileWriter.deleteShapeFile( self.outFileName ):
        QMessageBox.warning( self, self.tr( "Delete error" ),
                             self.tr( "Can't delete file %1" ).arg( outFileName ) )
        return

    QApplication.setOverrideCursor( QCursor( Qt.WaitCursor ) )
    self.btnOk.setEnabled( False )

    vectorLayer = getVectorLayerByName( self.cmbInputLayer.currentText() )

    self.workThread = DisplacementThread( vectorLayer, self.outFileName, self.outEncoding )
    QObject.connect( self.workThread, SIGNAL( "rangeChanged( int )" ), self.setProgressRange )
    QObject.connect( self.workThread, SIGNAL( "valueProcessed()" ), self.valueProcessed )
    QObject.connect( self.workThread, SIGNAL( "processingFinished()" ), self.processingFinished )
    QObject.connect( self.workThread, SIGNAL( "processingInterrupted()" ), self.processingInterrupted )

    self.btnClose.setText( self.tr( "Cancel" ) )
    QObject.disconnect( self.buttonBox, SIGNAL( "rejected()" ), self.reject )
    QObject.connect( self.btnClose, SIGNAL( "clicked()" ), self.stopProcessing )

    self.workThread.start()

  def setProgressRange( self, maxVal ):
    self.progressBar.setRange( 0, maxVal )
    self.progressBar.setValue( 0 )

  def valueProcessed( self ):
    self.progressBar.setValue( self.progressBar.value() + 1 )

  def processingFinished( self ):
    self.stopProcessing()

    if self.chkAddToCanvas.isChecked():
      if not addShapeToCanvas( unicode( self.outFileName ) ):
        QMessageBox.warning( self, self.tr( "Point displacement" ), self.tr( "Error loading output shapefile:\n%1" ).arg( unicode( self.outFileName ) ) )

    self.restoreGui()

  def processingInterrupted( self ):
    self.restoreGui()

  def stopProcessing( self ):
    if self.workThread != None:
      self.workThread.stop()
      self.workThread = None

  def restoreGui( self ):
    self.progressBar.setValue( 0 )
    QApplication.restoreOverrideCursor()
    QObject.connect( self.buttonBox, SIGNAL( "rejected()" ), self.reject )
    self.btnClose.setText( self.tr( "Close" ) )
    self.btnOk.setEnabled( True )

# ----------------------------------------------------------------------

class ShiftPointsThread( QThread ):
  def __init__( self, inVector, outputFileName, outputEncoding ):
    QThread.__init__( self, QThread.currentThread() )

    self.vector = inVector
    self.outputFileName = outputFileName
    self.outputEncoding = outputEncoding

    self.mutex = QMutex()
    self.stopMe = 0
    self.displ = 0.00015

  def run( self ):
    self.mutex.lock()
    self.stopMe = 0
    self.mutex.unlock()

    interrupted = False

    vProvider = self.vector.dataProvider()
    shapeFields = vProvider.fields()
    crs = vProvider.crs()
    wkbType = self.vector.wkbType()
    if not crs.isValid():
      crs = None
    shapeFileWriter = QgsVectorFileWriter( self.outputFileName, self.outputEncoding, shapeFields, wkbType, crs )

    featureCount = self.vector.featureCount()
    self.emit( SIGNAL( "rangeChanged( int )" ), featureCount )
    processed = []
    displacement = []

    allAttrs = vProvider.attributeIndexes()
    vProvider.select( allAttrs )
    vProvider.rewind()

    testFeat = QgsFeature()
    inFeat = QgsFeature()

    d = dict()
    while vProvider.nextFeature( inFeat ):
      geom = QgsGeometry( inFeat.geometry() )
      wkt = str( geom.exportToWkt() )
      if wkt not in d:
        lst = [ inFeat.id() ]
        d[ wkt ] = lst
      else:
        lst = d[ wkt ]
        j = [ inFeat.id() ]
        j.extend( lst )
        print j
        d[ wkt ] = j

      self.mutex.lock()
      s = self.stopMe
      self.mutex.unlock()
      if s == 1:
        interrupted = True
        break

      self.emit( SIGNAL( "valueProcessed()" ) )

    self.emit( SIGNAL( "rangeChanged( int )" ), len( d ) )

    for k, v in d.iteritems():
      featNum = len( v )
      if featNum == 1:
        f = QgsFeature()
        self.vector.featureAtId( v[ 0 ], f )
        shapeFileWriter.addFeature( f )
        processed.append( v[ 0 ] )
      else:
        radius = self.displ
        fullPerimeter = 2 * math.pi
        angleStep = fullPerimeter / featNum
        if featNum == 2:
          currentAngle = math.pi / 2
        else:
          currentAngle = 0
        f = QgsFeature()
        for i in v:
          sinusCurrentAngle = math.sin( currentAngle )
          cosinusCurrentAngle = math.cos( currentAngle )
          dx = radius * sinusCurrentAngle
          dy = radius * cosinusCurrentAngle
          self.vector.featureAtId( i, f )
          geom = QgsGeometry( f.geometry() ).asPoint()
          attrs = f.attributeMap()
          p = QgsPoint( geom.x() + dx, geom.y() + dy )
          ft = QgsFeature()
          g = QgsGeometry()
          ft.setGeometry( g.fromPoint( p ) )
          ft.setAttributeMap( attrs )
          shapeFileWriter.addFeature( ft )
          currentAngle += angleStep
          processed.append( i )

      self.mutex.lock()
      s = self.stopMe
      self.mutex.unlock()
      if s == 1:
        interrupted = True
        break

      self.emit( SIGNAL( "valueProcessed()" ) )

    if not interrupted:
      self.emit( SIGNAL( "processingFinished()" ) )
    else:
      self.emit( SIGNAL( "processingInterrupted()" ) )

  def stop( self ):
    self.mutex.lock()
    self.stopMe = 1
    self.mutex.unlock()

    QThread.wait( self )

# ----------------------------------------------------------------------

def addShapeToCanvas( shapefile_path ):
  file_info = QFileInfo( shapefile_path )
  if file_info.exists():
    layer_name = file_info.completeBaseName()
  else:
    return False
  vlayer_new = QgsVectorLayer( shapefile_path, layer_name, "ogr" )
  if vlayer_new.isValid():
    QgsMapLayerRegistry.instance().addMapLayer( vlayer_new )
    return True
  else:
    return False

def saveDialog( parent ):
  settings = QSettings()
  dirName = settings.value( "/UI/lastShapefileDir" ).toString()
  filtering = QString( "Shapefiles (*.shp)" )
  encode = settings.value( "/UI/encoding" ).toString()
  title = QCoreApplication.translate( "ShiftPointsDialog", "Save output shapefile" )
  fileDialog = QgsEncodingFileDialog( parent, title, dirName, filtering, encode )
  fileDialog.setDefaultSuffix( QString( "shp" ) )
  fileDialog.setFileMode( QFileDialog.AnyFile )
  fileDialog.setAcceptMode( QFileDialog.AcceptSave )
  fileDialog.setConfirmOverwrite( True )
  if not fileDialog.exec_() == QDialog.Accepted:
    return None, None
  files = fileDialog.selectedFiles()
  settings.setValue("/UI/lastShapefileDir", QVariant( QFileInfo( unicode( files.first() ) ).absolutePath() ) )
  return ( unicode( files.first() ), unicode( fileDialog.encoding() ) )

def getLayerNames( vTypes ):
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    layerlist = []
    if vTypes == "all":
        for name, layer in layermap.iteritems():
            layerlist.append( unicode( layer.name() ) )
    else:
        for name, layer in layermap.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.geometryType() in vTypes:
                    layerlist.append( unicode( layer.name() ) )
            elif layer.type() == QgsMapLayer.RasterLayer:
                if "Raster" in vTypes:
                    layerlist.append( unicode( layer.name() ) )
    return layerlist

def getVectorLayerByName( myName ):
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layermap.iteritems():
        if layer.type() == QgsMapLayer.VectorLayer and layer.name() == myName:
            if layer.isValid():
                return layer
            else:
                return None
