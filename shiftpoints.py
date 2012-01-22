# -*- coding: utf-8 -*-

#******************************************************************************
#
# ShiftPoints
# ---------------------------------------------------------
# Moves overlapped points with same coordinates in a circle around the
# original position.
#
# Copyright (C) 2011 Alexander Bruy (alexander.bruy@gmail.com), NextGIS
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

from __init__ import mVersion

import shiftpointsdialog

import resources_rc

class ShiftPointsPlugin( object ):
  def __init__( self, iface ):
    self.iface = iface
    self.iface = iface

    try:
      self.QgisVersion = unicode( QGis.QGIS_VERSION_INT )
    except:
      self.QgisVersion = unicode( QGis.qgisVersion )[ 0 ]

    # For i18n support
    userPluginPath = QFileInfo( QgsApplication.qgisUserDbFilePath() ).path() + "/python/plugins/shiftpoints"
    systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/shiftpoints"

    overrideLocale = QSettings().value( "locale/overrideFlag", QVariant( False ) ).toBool()
    if not overrideLocale:
      localeFullName = QLocale.system().name()
    else:
      localeFullName = QSettings().value( "locale/userLocale", QVariant( "" ) ).toString()

    if QFileInfo( userPluginPath ).exists():
      translationPath = userPluginPath + "/i18n/shiftpoints_" + localeFullName + ".qm"
    else:
      translationPath = systemPluginPath + "/i18n/shiftpoints_" + localeFullName + ".qm"

    self.localePath = translationPath
    if QFileInfo( self.localePath ).exists():
      self.translator = QTranslator()
      self.translator.load( self.localePath )
      QCoreApplication.installTranslator( self.translator )

  def initGui( self ):
    if int( self.QgisVersion ) < 1:
      QMessageBox.warning( self.iface.mainWindow(), "Shift Points",
                           QCoreApplication.translate( "Shift Points", "Quantum GIS version detected: " ) + unicode( self.QgisVersion ) + ".xx\n" +
                           QCoreApplication.translate( "Shift Points", "This version of Shift Points requires at least QGIS version 1.0.0\nPlugin will not be enabled." ) )
      return None

    self.actionRun = QAction( QIcon( ":/icons/shiftpoints.png" ), "Shift points", self.iface.mainWindow() )
    self.actionRun.setStatusTip( QCoreApplication.translate( "ShiftPoints", "Moves overlapped points with same coordinates in a circle" ) )
    self.actionAbout = QAction( QIcon( ":/icons/about.png" ), "About Shift points", self.iface.mainWindow() )

    QObject.connect( self.actionRun, SIGNAL( "triggered()" ), self.run )
    QObject.connect( self.actionAbout, SIGNAL( "triggered()" ), self.about )

    if hasattr( self.iface, "addPluginToVectorMenu" ):
      self.iface.addPluginToVectorMenu( QCoreApplication.translate( "ShiftPoints", "Shift points" ), self.actionRun )
      self.iface.addPluginToVectorMenu( QCoreApplication.translate( "ShiftPoints", "Shift points" ), self.actionAbout )
      self.iface.addVectorToolBarIcon( self.actionRun )
    else:
      self.iface.addPluginToMenu( QCoreApplication.translate( "ShiftPoints", "Shift points" ), self.actionRun )
      self.iface.addPluginToMenu( QCoreApplication.translate( "ShiftPoints", "Shift points" ), self.actionAbout )
      self.iface.addToolBarIcon( self.actionRun )

  def unload( self ):
    if hasattr( self.iface, "addPluginToVectorMenu" ):
      self.iface.removePluginVectorMenu( QCoreApplication.translate( "ShiftPoints", "Shift points" ), self.actionRun )
      self.iface.removePluginVectorMenu( QCoreApplication.translate( "ShiftPoints", "Shift points" ), self.actionAbout )
      self.iface.removeVectorToolBarIcon( self.actionRun )
    else:
      self.iface.removePluginMenu( QCoreApplication.translate( "ShiftPoints", "Shift points" ), self.actionRun )
      self.iface.removePluginMenu( QCoreApplication.translate( "ShiftPoints", "Shift points" ), self.actionAbout )
      self.iface.removeToolBarIcon( self.actionRun )

  def about( self ):
    dlgAbout = QDialog()
    dlgAbout.setWindowTitle( QApplication.translate( "ShiftPoints", "About Shift Points", "Window title" ) )
    lines = QVBoxLayout( dlgAbout )
    title = QLabel( QApplication.translate( "ShiftPoints", "<b>Shift Points</b>" ) )
    title.setAlignment( Qt.AlignHCenter | Qt.AlignVCenter )
    lines.addWidget( title )
    version = QLabel( QApplication.translate( "ShiftPoints", "Version: %1" ).arg( mVersion ) )
    version.setAlignment( Qt.AlignHCenter | Qt.AlignVCenter )
    lines.addWidget( version )
    lines.addWidget( QLabel( QApplication.translate( "ShiftPoints", "Moves overlapped points with same\ncoordinates in a circle around the\noriginal position." ) ) )
    lines.addWidget( QLabel( QApplication.translate( "ShiftPoints", "<b>Developers:</b>" ) ) )
    lines.addWidget( QLabel( "  Alexander Bruy" ) )
    lines.addWidget( QLabel( QApplication.translate( "ShiftPoints", "<b>Homepage:</b>") ) )

    overrideLocale = QSettings().value( "locale/overrideFlag", QVariant( False ) ).toBool()
    if not overrideLocale:
      localeFullName = QLocale.system().name()
    else:
      localeFullName = QSettings().value( "locale/userLocale", QVariant( "" ) ).toString()

    localeShortName = localeFullName[ 0:2 ]
    if localeShortName in [ "ru", "uk" ]:
      link = QLabel( "<a href=\"http://gis-lab.info/qa/point-displacement.html\">http://gis-lab.info/qa/point-displacement.html</a>" )
    else:
      link = QLabel( "<a href=\"http://gis-lab.info/qa/point-displacement-eng.html\">http://gis-lab.info/qa/point-displacement-eng.html</a>" )

    link.setOpenExternalLinks( True )
    lines.addWidget( link )

    btnClose = QPushButton( QApplication.translate( "ShiftPoints", "Close" ) )
    lines.addWidget( btnClose )
    QObject.connect( btnClose, SIGNAL( "clicked()" ), dlgAbout, SLOT( "close()" ) )

    dlgAbout.exec_()

  def run( self ):
    dlg = shiftpointsdialog.ShiftPointsDialog( self.iface )
    dlg.exec_()
