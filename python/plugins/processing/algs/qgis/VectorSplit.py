# -*- coding: utf-8 -*-

"""
***************************************************************************
    VectorSplit.py
    ---------------------
    Date                 : September 2014
    Copyright            : (C) 2014 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import str

__author__ = 'Alexander Bruy'
__date__ = 'September 2014'
__copyright__ = '(C) 2014, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QIcon

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterTableField
from processing.core.outputs import OutputDirectory
from processing.tools import dataobjects, vector
from processing.tools.system import mkdir

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class VectorSplit(GeoAlgorithm):

    INPUT = 'INPUT'
    FIELD = 'FIELD'
    OUTPUT = 'OUTPUT'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'ftools', 'split_layer.png'))

    def group(self):
        return self.tr('Vector general tools')

    def name(self):
        return 'splitvectorlayer'

    def displayName(self):
        return self.tr('Split vector layer')

    def defineCharacteristics(self):
        self.addParameter(ParameterVector(self.INPUT,
                                          self.tr('Input layer')))
        self.addParameter(ParameterTableField(self.FIELD,
                                              self.tr('Unique ID field'), self.INPUT))
        self.addOutput(OutputDirectory(self.OUTPUT, self.tr('Output directory')))

    def processAlgorithm(self, feedback):
        layer = dataobjects.getLayerFromString(
            self.getParameterValue(self.INPUT))
        fieldName = self.getParameterValue(self.FIELD)
        directory = self.getOutputValue(self.OUTPUT)

        mkdir(directory)

        fieldIndex = layer.fields().lookupField(fieldName)
        uniqueValues = vector.uniqueValues(layer, fieldIndex)
        baseName = os.path.join(directory, '{0}_{1}'.format(layer.name(), fieldName))

        fields = layer.fields()
        crs = layer.crs()
        geomType = layer.wkbType()

        total = 100.0 / len(uniqueValues)

        for current, i in enumerate(uniqueValues):
            fName = u'{0}_{1}.shp'.format(baseName, str(i).strip())

            writer = vector.VectorWriter(fName, None, fields, geomType, crs)
            for f in vector.features(layer):
                if f[fieldName] == i:
                    writer.addFeature(f)
            del writer

            feedback.setProgress(int(current * total))
