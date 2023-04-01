# import pyaudio
import pyaudiowpatch as pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft

CHUNK = 1024 * 4
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

IS_RUNNING = True


p = pyaudio.PyAudio()


try:
        # Get default WASAPI info
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
except OSError:
    spinner.print("Looks like WASAPI is not available on the system. Exiting...")
    spinner.stop()
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



host_info = p.get_host_api_info_by_index(0)    
device_count = host_info.get('deviceCount')
devices = []

# iterate between devices:
for i in range(0, device_count):
    device = p.get_device_info_by_host_api_device_index(0, i)
    devices.append(device['name'])

print(default_speakers)

stream = p.open(
    format=pyaudio.paInt16,
    channels=default_speakers["maxInputChannels"],
    rate=int(default_speakers['defaultSampleRate']),
    input_device_index=default_speakers["index"],
    input=True,
    frames_per_buffer=CHUNK
)

plt.ion()

fig = plt.figure()
ax = fig.add_subplot()

fig2 = plt.figure()
ax_fft = fig2.add_subplot()

# Axis labels
ax.set_ylim(-32768,32767)
ax.set_xlim(0,CHUNK)

# ax_fft.set_ylim(0, 1000)
ax_fft.set_xlim(20, RATE/2)




x = np.arange(0, 2*CHUNK , 1 )
x_fft = np.linspace(0,RATE, CHUNK)
line, = ax.plot(x, np.random.rand(CHUNK *2), '-', lw=1)
line_fft, = ax_fft.plot(x_fft, np.random.rand(CHUNK), '-', lw=1)


print(CHUNK)
print(x)
print(line)
# plt.show()

while IS_RUNNING:
    data = stream.read(CHUNK)
    data_np = np.frombuffer(data, dtype=np.int16) 
    line.set_ydata(data_np)

    y_fft = fft(data_np)
    y_data= np.abs(y_fft[0:CHUNK]) * 2 / (32767 * CHUNK)
    line_fft.set_ydata(y_data)

    print( "1 ---- X: " + str( x.size) + "   y: " +  str(data_np.size))
    print( "2 ---- X: " + str( x_fft.size) + "   y: " +  str(y_data.size))

    fig.canvas.draw()
    fig.canvas.flush_events()
    fig2.canvas.draw()
    fig2.canvas.flush_events()

   




