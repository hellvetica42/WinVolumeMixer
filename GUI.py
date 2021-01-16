import PySimpleGUI as sg
from Mixer import Mixer
import serial.tools.list_ports
from PySimpleGUI.PySimpleGUI import Column, VerticalSeparator
from threading import Thread
from queue import Queue
from math import floor
m = Mixer()
sources = m.getSources()
sPORT =""
chosen = {s:False for s in sources}
_kill = object()
data = Queue()
controlQ = Queue()

names = ['-VOL1-',
        '-VOL2-',
        '-VOL3-',
        '-VOL4-',
        '-VOL5']

controlDict = {n:"" for n in names}

def comboChosen(s, event, w: sg.Window, values):
    if chosen[s]:
        for n in names:
            if values[n] == s and n is not event:
                w[n].update(value="")

    chosen[s] = True
    controlDict[event] = s

def readSerialPort(s: serial.Serial, q: Queue, control: Queue, w: sg.Window, dict):
    m = Mixer()
    while True:
        if s != None:
            if(s.in_waiting > 0):
                string = s.readline().decode('Ascii')
                vals = string.split(":")
                q.put(vals[:-1])

                for n, i in zip(names, range(len(names))):
                    v = floor(float(vals[i])*100)
                    w[n+"SLIDER"].update(v)
                    if values[n] != "":
                        m.setSourceVol(dict[n], float(vals[i]))

        if not control.empty():
            if control.get() == _kill:
                break

def updateGui(w: sg.Window, data):
    pass


layout = [[],[]]
layout[0] = [sg.Text("PORT:"), sg.Combo([], size=(7, 1), key="-PORT-"), sg.Button("Select")]
for i in range(1,6):
    layout[1].append(sg.Column( [
        [
            sg.Text(names[i-1])
        ],
        [sg.Combo(sources, key=names[i-1], enable_events=True)],
        [sg.Slider(range=(0,100), orientation='v', key=names[i-1]+"SLIDER", enable_events=True)],
        [sg.Check("Enable", default=True)],
        [sg.Button("Clear", key=names[i-1]+"CLEAR")]
    ]))
    if i != 5:
        layout[1].append(sg.VSeparator())

# Create the window
window = sg.Window("WinMixer", layout)
serialPort = None
thread = None
# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    if event == sg.WIN_CLOSED:
        controlQ.put(_kill)
        break

    if event in names:
        comboChosen(values[event], event, window, values)

    if 'CLEAR' in event:
        chosen[event.replace('CLEAR', '')] = False
        controlDict[event.replace('CLEAR', '')] = ""
        window[event.replace('CLEAR', '')].update(value="")

    if 'SLIDER' in event:
        if values[event.replace('SLIDER', '')] != "":
            vol = values[event]/100
            s = values[event.replace('SLIDER', '')]
            m.setSourceVol(s, vol)

    if 'Select' == event:
        ports = serial.tools.list_ports.comports()
        val = []
        for port, desc, hwid in sorted(ports):
            val.append(port)
        window["-PORT-"].update(values=val)

        if values["-PORT-"] != "":
            if serialPort != None:
                serialPort.close()
            serialPort = serial.Serial(port = values["-PORT-"], baudrate=115200, bytesize=8)

            if thread == None:
                thread = Thread(target=readSerialPort, args=(serialPort, data, controlQ, window, controlDict))
                thread.start()

    # if not data.empty():
    #     print(data.get())



window.close()