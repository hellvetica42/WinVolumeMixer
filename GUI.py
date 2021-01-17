from utils import getSources, setMasterVol, setSourceVol
import PySimpleGUI as sg
from utils import *
import serial.tools.list_ports
from PySimpleGUI.PySimpleGUI import Column, VerticalSeparator
from threading import Thread
from queue import Queue
from math import floor

sources = getSources()
control =  Queue()
_kill = object()

names = ['-VOL1-',
        '-VOL2-',
        '-VOL3-',
        '-VOL4-']

layout = [[],[]]
layout[0] = [sg.Text("PORT:"), sg.Combo([], size=(15, 1), key="-PORT-"), sg.Button("Select"), sg.Button("Refresh")]
layout[1].append(sg.Column( [
    [
        sg.Text("MASTER")
    ],
    [sg.Slider(range=(0,100), orientation='v', key="-MASTER-"+"SLIDER", enable_events=True)],
    [sg.Check("Enable", default=True)],
]))
layout[1].append(sg.VSeparator())

for i in range(1,5):
    layout[1].append(sg.Column( [
        [
            sg.Text(names[i-1])
        ],
        [sg.Combo(sources, key=names[i-1], enable_events=True)],
        [sg.Slider(range=(0,100), orientation='v', key=names[i-1]+"SLIDER", enable_events=True)],
        [sg.Check("Enable", default=True)],
        [sg.Button("Clear", key=names[i-1]+"CLEAR")]
    ]))
    if i != 4:
        layout[1].append(sg.VSeparator())

window = sg.Window("WinMixer", layout)

def updateSources(s):
    for n in names:
        window[n].update(values=s)

def updatePorts():
    ports = serial.tools.list_ports.comports()
    val = []
    for port, desc, hwid in sorted(ports):
        val.append(port)
    window["-PORT-"].update(values=val)
    return val

def readSerialData(serialPort: serial.Serial, control: Queue, window: sg.Window):
    while True:
        if serialPort != None:
            if serialPort.in_waiting > 0:
                #Read and parse data from form
                string = serialPort.readline().decode('Ascii')
                vals = string.split(":")

                #Sets master volume
                v = floor(float(vals[0])*100) 
                window["-MASTER-"+"SLIDER"].update(v) 
                setMasterVol(float(vals[0]))

                #Loops through names
                for n, i in zip(names, range(len(names))):
                    v = floor(float(vals[i+1])*100) 
                    #Sets slider values to volumes
                    window[n+"SLIDER"].update(v) 

                    if values[n] != "": 
                        #Sets volume of source
                        setSourceVol(values[n], float(vals[i+1]))

        #If kill command is sent break thread
        if not control.empty():
            if control.get() == _kill:
                break

thread = None
serialPort = None
while True:
    event, values = window.read()
    #Update the selections for new sources
    updateSources(getSources())

    if event == sg.WIN_CLOSED:
        control.put(_kill)
        break

    if event in names:
        for n in names:
            #We check if the chosen source has been chosen by any OTHER combo box
            if n is not event:
                if values[n] == values[event]:
                    window[n].update(value = "")

    if 'CLEAR' in event:
        window[event.replace('CLEAR', '')].update(value="")

    if 'SLIDER' in event:
        box = event.replace('SLIDER', '')
        vol = values[event]/100

        if 'MASTER' in event:
            setMasterVol(vol)
            pass
        #Check if source is chosen
        elif values[box] != "":
            setSourceVol(values[box], vol)
    #If port has been chosen
    if 'Select' == event:
        #Check if port is chosen
        if values["-PORT-"] != "":
            if serialPort != None:
                serialPort.close()
            serialPort = serial.Serial(port = values["-PORT-"], baudrate=115200, bytesize=8)

            if thread == None:
                thread = Thread(target=readSerialData, args=(serialPort, control, window))
                thread.start()

    if 'Refresh' == event:
        updatePorts()

window.close()