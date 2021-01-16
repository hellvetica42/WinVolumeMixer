from pycaw.pycaw import AudioUtilities

class Mixer():

    def __init__(self):
        pass

    def getSources(self):
        sessions = AudioUtilities.GetAllSessions()
        return [s.Process.name() for s in sessions if s.Process]

    def setSourceVol(self, source, vol):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session.SimpleAudioVolume
            if session.Process and session.Process.name() == source:
                volume.SetMasterVolume(vol, None)

