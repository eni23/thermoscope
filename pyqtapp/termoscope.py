from PyQt5.QtCore import QTime, QTimer, QThread, pyqtSignal

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

import struct
import serial
import datetime
import sys
from collections import deque
from pprint import pprint
import array
import copy



inital_sensor_resolution = 9


UNIX_EPOCH_naive = datetime.datetime(1970, 1, 1, 0, 0) #offset-naive datetime
UNIX_EPOCH = UNIX_EPOCH_naive
TS_MULT_us = 1e6

def now_timestamp(ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    return(int((datetime.datetime.now() - epoch).total_seconds()*ts_mult))

def int2dt(ts, ts_mult=TS_MULT_us):
    return(datetime.datetime.utcfromtimestamp(float(ts)/ts_mult))



class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        #return [QTime().addMSecs(value).toString('mm:ss') for value in values]
        return [int2dt(value).strftime("%H:%M:%S") for value in values]


param_tpl = {
    'name': 'Sensor', 'type': 'group', 'children': [
        {'name': 'Show Plot', 'type': 'bool', 'value': True },
        {'name': 'Show Dots', 'type': 'bool', 'value': False },
        {'name': 'Resolution', 'type': 'list', 'values': {
            "9": 9,
            "10": 10,
            "11": 11,
            "12": 12
            }, 'value': inital_sensor_resolution },
        {'name': 'Line width', 'type': 'int', 'value': 1 },
        # insert color line dynamically
    ]}


def colortupletohex(color_tuple):
    a = array.array('B',color_tuple )
    return a.tobytes().hex()


class SerialReaderThread(QThread):
    newValue = pyqtSignal(int, float)

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def set_serial(self, ser):
        self.serial = ser

    def run(self):
        while True:
            data_raw = self.serial.read(3)
            sensor_id, temp_raw = struct.unpack("=BH", data_raw)
            temp = temp_raw / 100
            self.newValue.emit(sensor_id, temp)


class ThermoscopeApp(QtGui.QApplication):


    def __init__(self, *args, **kwargs):
        super(ThermoscopeApp, self).__init__(*args, **kwargs)

        self.init_serial()
        self.ser_thread = SerialReaderThread()
        self.ser_thread.set_serial(self.serial)
        self.ser_thread.newValue.connect(self.update_temp)

        self.win = pg.GraphicsWindow(title="Thermoscope")
        self.win.resize(1000,600)

        # set inital_sensor_resolution
        for i in range(0,4):
            self.set_sens_resolution(i+1, inital_sensor_resolution)

        self.data = []
        self.curve_colors = [
            (255,0,0),
            (0,255,0),
            (0,0,255),
            (255,255,0)
        ]
        self.line_width = [ 1, 1, 1, 1 ]

        for i in range(0,4):
            self.data.append([
                deque(), #x
                deque()  #y
            ])


        # param tree
        self.params_data = []
        for i in range(0,4):
            sparam = copy.deepcopy(param_tpl)
            citem = {'name': 'Line color', 'type': 'color', 'value': colortupletohex(self.curve_colors[i]) }
            sparam['children'].append(citem)
            sparam['name'] = "Sensor {0}".format(i+1)
            self.params_data.append(sparam)

        self.params = Parameter.create(name='params', type='group', children=self.params_data)
        self.param_tree = ParameterTree()
        self.param_tree.setParameters(self.params, showTop=False)
        self.layout = QtGui.QGridLayout()
        self.layout.setColumnStretch(1, 8)

        self.win.setLayout(self.layout)

        self.params.sigTreeStateChanged.connect(self.change_tree)

        self.plot = pg.PlotWidget(
            title='',
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )

        self.layout.addWidget(self.param_tree, 0, 0, 1, 1)
        self.layout.addWidget(self.plot, 0, 1, 1, 8)

        #self.plot.setYRange(0, 150)
        self.curves = []
        for i in range(0,4):
            self.curves.append(
                self.plot.plot(
                    pen=pg.mkPen(self.curve_colors[i], width=1),
                    name="sensor {0}".format(i),
                )
            )

        self.ser_thread.start()


    def change_tree(self, params, changes):
        for param, change, data in changes:
            path = self.params.childPath(param)
            change = path[1]
            sensor_id = int(path[0].split(" ")[1])
            #print('  sensor: %s'% sensor_id)
            #print('  change: %s' % change)
            #print('  data:      %s'% str(data))
            #print('  ----------')

            data_id = sensor_id - 1
            if change=="Line color":
                data_id = sensor_id - 1
                try:
                    color = data.name()[1:]
                except AttributeError:
                    color = data
                lpen = pg.mkPen(color, width=self.line_width[data_id] )
                self.curves[data_id].setData(
                    pen = lpen
                )
                self.curve_colors[data_id] = color

            if change=="Show Plot":
                if data:
                    self.curves[data_id].show()
                else:
                    self.curves[data_id].hide()

            if change=="Show Dots":
                if data:
                    self.curves[data_id].setData(
                        symbolBrush=(0,0,0),
                        symbolPen=(255,255,255),
                        symbolSize=3
                    )
                else:
                    self.curves[data_id].setData(
                        symbolSize=0
                    )

            if change == "Line width":
                lpen = pg.mkPen(self.curve_colors[data_id], width=int(data))
                self.curves[data_id].setData(
                    pen = lpen
                )
                self.line_width[data_id] = int(data)

            if change == "Resolution":
                self.set_sens_resolution(sensor_id, data)


    def set_sens_resolution(self, sensor_id, value):
        msg = struct.pack("=BBB", 1, sensor_id, int(value) )
        self.serial.write(msg)


    def init_serial(self):
        self.serial = serial.Serial('/dev/ttyUSB0', 115200)


    def update_temp(self, sensor_id, temp):
        data_id = sensor_id-1
        ts = now_timestamp()
        self.data[data_id][0].append(ts)
        self.data[data_id][1].append(temp)
        self.curves[data_id].setData(
            x=list(self.data[data_id][0]),
            y=list(self.data[data_id][1])
        )


def main():
    app = ThermoscopeApp(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
