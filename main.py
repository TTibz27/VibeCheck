# import pyaudio
import pyaudiowpatch as pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QMovie
import sys

#Chunk is the frames per buffer of the audio stream
CHUNK = 1024 * 4
SHOW_GRAPHS = True #todo- does not work if set to false??? WHY THOUGH PYTHON
IS_RUNNING = True
TARGET_FREQ =20000

CURRENT_ANIM_FRAME = -1
TOTAL_FRAMES = 36
TRIGGER_MOVIE_THRESHOLD =  0.04 # Amplitude of FFT that will
p = pyaudio.PyAudio()



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(580, 500)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # create label
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 580, 500))
        self.label.setMinimumSize(QtCore.QSize(580, 500))
        self.label.setMaximumSize(QtCore.QSize(580, 500))
        self.label.setObjectName("label")

        # add label to main window
        MainWindow.setCentralWidget(self.centralwidget)

        # set qmovie as label
        self.movie = QMovie("deal.gif")
        
    def startVideo(self):
         self.label.setMovie(self.movie)
         self.movie.start()
        #  CURRENT_ANIM_FRAME = 1
         return self.movie
    
    def stopVideo(self):
         self.movie.stop()
         self.label.clear()
        #  CURRENT_ANIM_FRAME = -1
         return self.movie

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(window)
window.show()


# --------  Grabbing Loopback Audio Device  ----------------------
try:
        # Get default WASAPI info
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
except OSError:
    print("Looks like WASAPI is not available on the system. Exiting...")
    exit()


default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

if not default_speakers["isLoopbackDevice"]:
    for loopback in p.get_loopback_device_info_generator():
        if default_speakers["name"] in loopback["name"]:
            default_speakers = loopback
            break
    else:
        print("Default loopback output device not found.\nRun this to check available devices.\nExiting...\n")
        exit()


# ----------------   initializing graphs ------------------
if SHOW_GRAPHS:
    plt.ion()

    fig = plt.figure()
    ax = fig.add_subplot()

    fig2 = plt.figure()
    ax_fft = fig2.add_subplot()

    # Axis labels
    ax.set_ylim(-32768,32767)
    ax.set_xlim(0,CHUNK)

    # ax_fft.set_ylim(0, 1000)
    ax_fft.set_xlim(20, int(default_speakers['defaultSampleRate']) /2)

    x = np.arange(0, 2*CHUNK , 1 )
    x_fft = np.linspace(0, int(default_speakers['defaultSampleRate']), CHUNK)
    line, = ax.plot(x, np.random.rand(CHUNK *2), '-', lw=1)
    line_fft, = ax_fft.plot(x_fft, np.random.rand(CHUNK), '-', lw=1)



# -----------  Opening Audio stream   ---------------------
stream = p.open(
    format=pyaudio.paInt16,
    channels=default_speakers["maxInputChannels"],
    rate=int(default_speakers['defaultSampleRate']),
    input_device_index=default_speakers["index"],
    input=True,
    frames_per_buffer=CHUNK
)

#testing  for fft bin size
fft_width_hz = default_speakers['defaultSampleRate'] / CHUNK
target_freq_index = round( TARGET_FREQ / fft_width_hz) -1 # -1 for zero indexing

print("Target freq index")
print(target_freq_index)

while IS_RUNNING:
    #grab new Data
    try:
        data_bytes = stream.read(CHUNK)
    except:
        print("No audio detected right now.")
    data_np = np.frombuffer(data_bytes, dtype=np.int16) 

    y_fft = fft(data_np)
    y_data= np.abs(y_fft[0:CHUNK]) * 2 / (32767 * CHUNK) 
    # check the FFT data, index 1706 is where 20khz is.
    if y_data[target_freq_index] > 0.04:
        print("DEAL WITH IT")
        movie_ref =  ui.startVideo()
        CURRENT_ANIM_FRAME =1
    print("")
    
    #draw graphs
    if SHOW_GRAPHS:
        line.set_ydata(data_np)
        line_fft.set_ydata(y_data)
        fig.canvas.draw()
        fig.canvas.flush_events()
        fig2.canvas.draw()
        fig2.canvas.flush_events()

    print(CURRENT_ANIM_FRAME)
    if CURRENT_ANIM_FRAME > 0:
        try:
            CURRENT_ANIM_FRAME = movie_ref.currentFrameNumber()
     
        except:
            print("No Movie Ref found")
    
    if CURRENT_ANIM_FRAME >= TOTAL_FRAMES:
         ui.stopVideo()
         CURRENT_ANIM_FRAME = -1
         print("resetting")



    # if keyboard.read_key() == "q":
    #     IS_RUNNING = False
   

