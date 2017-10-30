import os.path
import glob

class TimeSeries():
    def __init__(self, folder=None, pattern='*'):
        if folder is not None:
            folder_path = os.path.join(folder, pattern)
            file_list = glob.glob(folder_path)
            self._timepoints = [TimePoint(f) for f in file_list]
        else:
            self._timepoints = []

    def __del__(self):
        del self._timepoints[:]

class TimePoint():
    def __init__(self, file_path=None):
        pass

    def __del__(self):
        pass
