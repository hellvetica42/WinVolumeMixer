from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from math import floor

def getSources():
    sessions = AudioUtilities.GetAllSessions()
    return [s.Process.name() for s in sessions if s.Process]

def setSourceVol(source, vol):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session.SimpleAudioVolume
        if session.Process and session.Process.name() == source:
            volume.SetMasterVolume(vol, None)

def setMasterVol(vol):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        level = floor((1.0 - vol) * -28.0)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevel(level, None)
    except Exception as e:
        print('err')
