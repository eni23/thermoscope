#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import copy
import array
import struct
import serial
import datetime
import collections


# QT imports
from PyQt5.QtCore import QTime, QTimer, QThread, pyqtSignal
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType



inital_sensor_resolution = 9




class TimeAxisItem(pyqtgraph.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def int2dt(ts):
        return(datetime.datetime.utcfromtimestamp(float(ts)/1e6))

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        #return [QTime().addMSecs(value).toString('mm:ss') for value in values]
        return [self.int2dt(value).strftime("%H:%M:%S") for value in values]




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

        # init serial
        self.serial = serial.Serial('/dev/ttyUSB0', 115200)
        self.ser_thread = SerialReaderThread()

        self.ser_thread.set_serial(self.serial)
        self.ser_thread.newValue.connect(self.update_temp)

        self.time_epoch = datetime.datetime(1970, 1, 1, 0, 0)

        # set inital_sensor_resolution
        for i in range(0,4):
            self.set_sens_resolution(i+1, inital_sensor_resolution)

        # init qt window
        self.win = pyqtgraph.GraphicsWindow(title="Thermoscope")
        self.win.resize(1000,600)
        self.layout = QtGui.QGridLayout()
        self.layout.setColumnStretch(1, 8)
        self.win.setLayout(self.layout)

        # init data & gui
        self.init_datastores()
        self.init_gui_tree()
        self.init_gui_plot()

        # init threads
        self.ser_thread.start()



    def now_timestamp(self):
        return( int( (
            datetime.datetime.now() - self.time_epoch).total_seconds() * 1e6
        ) )



    def init_datastores(self):
        self.curve_colors = [
            (255,0,0),
            (0,255,0),
            (0,0,255),
            (255,255,0)
        ]
        self.line_width = [ 1, 1, 1, 1 ]
        self.data = []
        for i in range(0,4):
            self.data.append([
                collections.deque(), #x
                collections.deque()  #y
            ])


    def init_gui_plot(self):
        self.plot = pyqtgraph.PlotWidget(
            title = '',
            axisItems = {
                'bottom': TimeAxisItem(orientation='bottom')
            }
        )
        self.layout.addWidget(self.param_tree, 0, 0, 1, 1)
        self.layout.addWidget(self.plot, 0, 1, 1, 8)
        self.curves = []
        for i in range(0,4):
            self.curves.append(
                self.plot.plot(
                    pen=pyqtgraph.mkPen(self.curve_colors[i], width=1),
                    name="sensor {0}".format(i),
                )
            )



    def init_gui_tree(self):
        param_tpl = {
            'name': 'Sensor',
            'type': 'group',
            'children': [
                {
                    'name': 'Show Plot',
                    'type': 'bool',
                    'value': True
                },
                {
                    'name': 'Show Dots',
                    'type': 'bool',
                    'value': False
                },
                {
                    'name': 'Resolution',
                    'type': 'list',
                    'value': inital_sensor_resolution,
                    'values': {
                        "9": 9,
                        "10": 10,
                        "11": 11,
                        "12": 12
                    }
                },
                {
                    'name': 'Line width',
                    'type': 'int',
                    'value': 1
                },
                # color item is inserted dynamically
            ]
        }
        self.params_data = []
        for i in range(0,4):
            sparam = copy.deepcopy(param_tpl)
            citem = {
                'name': 'Line color',
                'type': 'color',
                'value': self.curve_colors[i]
            }
            sparam['children'].append(citem)
            sparam['name'] = "Sensor {0}".format(i+1)
            self.params_data.append(sparam)

        self.params = Parameter.create(
            name='params',
            type='group',
            children=self.params_data
        )

        self.param_tree = ParameterTree()
        self.param_tree.setParameters(self.params, showTop=False)
        self.params.sigTreeStateChanged.connect(self.change_tree)



    def change_tree(self, params, changes):
        for param, change, data in changes:
            path = self.params.childPath(param)
            change = path[1]
            sensor_id = int(path[0].split(" ")[1])

            data_id = sensor_id - 1
            if change=="Line color":
                data_id = sensor_id - 1
                try:
                    color = data.name()[1:]
                except AttributeError:
                    color = data
                lpen = pyqtgraph.mkPen(
                    color,
                    width=self.line_width[data_id]
                )
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
                lpen = pyqtgraph.mkPen(
                    self.curve_colors[data_id],
                    width = int(data)
                )
                self.curves[data_id].setData(
                    pen = lpen
                )
                self.line_width[data_id] = int(data)

            if change == "Resolution":
                self.set_sens_resolution(sensor_id, data)



    def set_sens_resolution(self, sensor_id, value):
        msg = struct.pack(
            "=BBB",
            1,
            sensor_id,
            int(value)
        )
        self.serial.write(msg)



    def update_temp(self, sensor_id, temp):
        data_id = sensor_id-1
        ts = self.now_timestamp()
        self.data[data_id][0].append(ts)
        self.data[data_id][1].append(temp)
        self.curves[data_id].setData(
            x = list(self.data[data_id][0]),
            y = list(self.data[data_id][1])
        )



def main():
    app = ThermoscopeApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
