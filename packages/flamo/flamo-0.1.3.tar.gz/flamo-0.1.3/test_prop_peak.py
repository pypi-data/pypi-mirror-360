import torch
import numpy as np
from flamo.functional import *
import matplotlib.pyplot as plt


delays = torch.tensor([1, 1559, 1039, 1193, 1783, 2243, 2411]) 
fc = 7000
fs = 48000
rt_DC = 2.0
rt_Ny = 0.2
nfft = 2**15
omega_c = np.pi * fc / fs
gain_DC = torch.tensor([-60/fs/rt_DC])*delays #, 2.0]) #, 2.0, 0.8])  # Example gains
gain_Ny = torch.tensor([-60/fs/rt_Ny])*delays 

t = torch.tan(torch.tensor(omega_c))
k = 10 ** (gain_DC / 20) / 10 ** (gain_Ny / 20)

a = torch.zeros((2, *k.shape))
b = torch.zeros_like(a)


b[0] = t * torch.sqrt(k) + 1
b[1] = t * torch.sqrt(k) - 1
a[0] = t / torch.sqrt(k) + 1
a[1] = t / torch.sqrt(k) - 1

b = b * 10 ** (gain_Ny / 20)

B = torch.fft.rfft(b, nfft, dim=0)
A = torch.fft.rfft(a, nfft, dim=0)

H = torch.abs( B / A )

# Plot the magnitude response
frequencies = torch.fft.rfftfreq(nfft, 1 / fs)
plt.plot(frequencies, 20 * torch.log10(torch.abs(H[:, :])))

plt.title("Magnitude Response of prop_peak")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.grid()
plt.show()

rt = -3 / fs / torch.log10(torch.abs(H) ** ( 1 / delays.unsqueeze(0))) 
plt.figure()
plt.plot(frequencies, rt[:, 1:])
plt.plot(frequencies, rt[:, 0], '--')


plt.title("Magnitude Response of prop_peak")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.grid()
plt.show()