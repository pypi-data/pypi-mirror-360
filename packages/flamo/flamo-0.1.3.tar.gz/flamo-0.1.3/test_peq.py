import torch
import numpy as np
from flamo.functional import *
import matplotlib.pyplot as plt

def get_poly_coeff(param, nfft, fs=48000, center_freq_bias=None, design='biquad', is_twostage=False):
    r"""
    Computes the polynomial coefficients for the SOS section.
    """
    n_bands = len(center_freq_bias)
    if is_twostage:
        param_eq = param[:-1, ...]
    param_eq = map_eq(param_eq, fs=fs, center_freq_bias=center_freq_bias, design=design, is_twostage=False)
    a = torch.zeros((n_bands, 3, len(delays)))
    b = torch.zeros((n_bands, 3, len(delays)))
    for n_i in range(len(delays)):
        f = param_eq[0, :, n_i] 
        R = param_eq[1, :, n_i]
        G = param_eq[2, :, n_i]
        # low shelf filter 
        a[0, :, n_i], b[0, :, n_i] = compute_biquad_coeff(
            f=f[0],
            R=R[0] if design == 'biquad' else R[0] + torch.sqrt(torch.tensor( 1 / 2)),
            G=G[0],
            type='lowshelf'
        )
        # high shelf filter 
        a[-1, :, n_i], b[-1, :, n_i] = compute_biquad_coeff(
            f=f[-1],
            R=R[-1] if design == 'biquad' else R[-1] + torch.sqrt(torch.tensor( 1 / 2)),
            G=G[-1],
            type='highshelf'
        )
        # peak filter 
        a[1:-1, :, n_i], b[1:-1, :, n_i] = compute_biquad_coeff(
            f=f[1:-1],
            R=R[1:-1],
            G=G[1:-1],
            type='peaking'
        )
    if is_twostage:
        param_ls = map_eq(param[-1, ...], fs=fs, center_freq_bias=center_freq_bias, design=design, is_twostage=is_twostage)
        a_ls = torch.zeros((3, len(delays)))
        b_ls = torch.zeros((3, len(delays)))
        for n_i in range(len(delays)):
            a_ls[:, n_i], b_ls[:, n_i] = compute_biquad_coeff(
                f=param_ls[0, n_i],
                R=param_ls[1, n_i] if design == 'biquad' else param_ls[1, :] + torch.sqrt(torch.tensor( 1 / 2)),
                G=param_ls[2, n_i],
                type='highshelf'
            )
        a = torch.cat((a, a_ls.unsqueeze(0)), dim=0)
        b = torch.cat((b, b_ls.unsqueeze(0)), dim=0)
    B = torch.fft.rfft(b, nfft, dim=1)
    A = torch.fft.rfft(a, nfft, dim=1)
    H_temp = torch.prod(B, dim=0) / (torch.prod(A, dim=0))
    H = torch.where(torch.abs(torch.prod(A, dim=0)) != 0, H_temp, torch.finfo(H_temp.dtype).eps*torch.ones_like(H_temp))
    H_type = torch.complex128 if param.dtype == torch.float64 else torch.complex64
    return H.to(H_type), B, A

def compute_biquad_coeff(f, R, G, type='peaking'):
    # f : freq, R : resonance, G : gain in dB
    b = torch.zeros(*f.shape, 3)     
    a = torch.zeros(*f.shape, 3)  

    if design == 'svf':
        G = 10 ** (G / 20)
        if type == 'peaking':
            mLP = torch.ones_like(G)
            mBP = 2 * R * torch.sqrt(G)
            mHP = torch.ones_like(G)
        elif type == 'lowshelf':
            mLP = G
            mBP = 2 * R * torch.sqrt(G)
            mHP = torch.ones_like(G)
        elif type == 'highshelf':
            mLP = torch.ones_like(G)
            mBP = 2 * R * torch.sqrt(G)
            mHP = G
        b[..., 0] = (f**2) * mLP + f * mBP + mHP
        b[..., 1] = 2*(f**2) * mLP - 2 * mHP
        b[..., 2] = (f**2) * mLP - f * mBP + mHP
        a[..., 0] = f**2 + 2*R*f + 1
        a[..., 1] = 2* (f**2) - 2
        a[..., 2] = f**2 - 2*R*f + 1  
    elif design == 'biquad':
        G = 10 ** (G / 40)
        if type == 'peaking':
            alpha = torch.sin(f) / (2 * R)
            b[..., 0] = 1 + alpha * G
            b[..., 1] = -2 * torch.cos(f)
            b[..., 2] = 1 - alpha * G
            a[..., 0] = 1 + alpha / G
            a[..., 1] = -2 * torch.cos(f)
            a[..., 2] = 1 - alpha / G
        elif type == 'lowshelf':
            alpha = torch.sin(f) * torch.sqrt((G**2 + 1) * (1/R - 1) + 2*G)
            b[..., 0] = G * ((G + 1) - (G - 1) * torch.cos(f) + alpha)
            b[..., 1] = 2 * G * ((G - 1) - (G + 1) * torch.cos(f))
            b[..., 2] = G * ((G + 1) - (G - 1) * torch.cos(f) - alpha)
            a[..., 0] = (G + 1) + (G - 1) * torch.cos(f) + alpha
            a[..., 1] = -2 * ((G - 1) + (G + 1) * torch.cos(f))
            a[..., 2] = (G + 1) + (G - 1) * torch.cos(f) - alpha
        elif type == 'highshelf':
            alpha = torch.sin(f) * torch.sqrt((G**2 + 1) * (1/R - 1) + 2*G)
            b[..., 0] = G * ((G + 1) + (G - 1) * torch.cos(f) + alpha)
            b[..., 1] = -2 * G * ((G - 1) + (G + 1) * torch.cos(f))
            b[..., 2] = G * ((G + 1) + (G - 1) * torch.cos(f) - alpha)
            a[..., 0] = (G + 1) - (G - 1) * torch.cos(f) + alpha
            a[..., 1] = 2 * ((G - 1) - (G + 1) * torch.cos(f))
            a[..., 2] = (G + 1) - (G - 1) * torch.cos(f) - alpha

    return a, b

def map_eq(param, fs=48000, center_freq_bias=None, design='biquad', is_twostage=False):
    r"""
    Mapping function for the raw parameters to the SVF filter coefficients.
    """
    if design == 'biquad' and not is_twostage:
        # frequency mapping
        bias = center_freq_bias / fs * 2 * torch.pi - 1/2

        f = torch.sigmoid(param[:, 0, ...]) + bias.unsqueeze(-1)
        # Q factor mapping 
        R = torch.zeros_like(param[:, 1, ...])
        R[0, :] = 0.1 + torch.sigmoid(R[0, :]) * 0.9
        R[-1, :] = 0.1 + torch.sigmoid(R[-1, :]) * 0.9
        R[1:-1, :] = 0.1 + torch.sigmoid(R[1:-1, :] ) * 3
        # Gain mapping
        clip_min = torch.tensor(-1e-3)
        clip_max = torch.tensor(-10)
        G =  clip_min + torch.sigmoid(param[:, 2, ...]) * clip_max
    elif design == 'svf' and not is_twostage:
        # frequency mapping
        bias = torch.log(2 * center_freq_bias / fs / (1 - 2 * center_freq_bias / fs))
        f = torch.tan(torch.pi * torch.sigmoid(param[:, 0, ...] + bias.unsqueeze(-1) ) * 0.5) 
        # Q factor mapping
        R =  torch.log(1+torch.exp(param[:, 1, ...]))  / torch.log(torch.tensor(2)) 
        # G 
        G = 10**(-torch.log(1+torch.exp(param[:, 2, ...])) / torch.log(torch.tensor(2))) - 10
    elif (design == 'svf' or design == 'biquad') and is_twostage:
        # frequency mapping
        bias = 300 / fs * 2 * torch.pi - 1/2
        f = torch.sigmoid(param[0, :]) + bias
        # Q factor mapping 
        R = torch.zeros_like(param[1, :])
        R[:] = 0.1 + torch.sigmoid(R) * 0.9
        # Gain mapping
        clip_min = torch.tensor(-1e-3)
        clip_max = torch.tensor(-20)
        G = clip_min + torch.sigmoid(param[2, :]) * clip_max

    param = torch.cat(
        (
            f.unsqueeze(0),
            R.unsqueeze(0),
            G.unsqueeze(0),
        ),
        dim=0,
    )
    return param 


delays = torch.tensor([1, 1559, 1039, 1193, 1783, 2243, 2411]) 
fs = 48000
nfft = fs*4
n_bands = 10
f_min = 20
f_max = 20000
design = "biquad"

k = torch.arange(1, n_bands + 1)
center_freq_bias = f_min * (f_max / f_min) ** ((k - 1) / (n_bands - 1))

## TEST THE PEQ filter 

# f = torch.zeros_like(center_freq_bias).unsqueeze(-1).repeat(1, len(delays)) # The bias is already at the center frequency
# R = (torch.ones_like(center_freq_bias) * 0.7071).unsqueeze(-1).repeat(1, len(delays))  # Resonance
# RT_target = torch.tensor([1.5, 2.0, 1.5, 1.0, 0.8, 0.5, 0.3, 0.2, 0.1, 0.05])  # Example RT values
# G = (-60 / fs / RT_target).unsqueeze(-1) * delays.unsqueeze(0)  # Gain in dB, scaled by delays
is_twostage = True

f = torch.zeros(n_bands + 1 if is_twostage else n_bands, len(delays))
R = torch.randn(n_bands + 1 if is_twostage else n_bands, len(delays))
G = torch.randn(n_bands + 1 if is_twostage else n_bands, len(delays))  # Gain in dB

param = torch.stack((f, R, G), dim=1)  # Shape: (n_bands, 3, len(delays))



H, B, A = get_poly_coeff(param, nfft, fs=fs, center_freq_bias=center_freq_bias, design=design, is_twostage=is_twostage)
frequencies = torch.fft.rfftfreq(nfft, 1 / fs)
plt.figure(figsize=(12, 6))
plt.plot(frequencies, 20 * torch.log10(torch.abs(H)), label='Magnitude Response')
plt.title("Magnitude Response of PEQ Filter")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")

plt.xscale('log')
plt.xlim([f_min, f_max])
plt.grid(which='both', axis='both')
plt.legend()
plt.show()


i_delay = 3
plt.figure(figsize=(12, 6))
for i in range(len(center_freq_bias)):
    plt.plot(frequencies, 20 * torch.log10(torch.abs(B[i, :, i_delay] / A[i, :, i_delay])), label=f'Band {i+1}')
    plt.axvline(x=center_freq_bias[i], color='gray', linestyle='--', label=f'Center Frequency {center_freq_bias[i]:.0f} Hz')
plt.plot(frequencies, 20 * torch.log10(torch.abs(H[:, i_delay])), '--', label='Magnitude Response')
plt.plot(center_freq_bias, G[:-1, i_delay], 'ro', label='Target Gain (dB)')
plt.title(f"Magnitude Response of PEQ Filter (Delay {delays[i_delay]})")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.xscale('log')
plt.xlim([f_min, f_max])
plt.grid(which='both', axis='both')
plt.legend()
