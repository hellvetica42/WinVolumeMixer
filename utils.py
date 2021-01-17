from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from masterVolume import *
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
    ev = IAudioEndpointVolume.get_default()
    ev.SetMasterVolumeLevelScalar(vol)


