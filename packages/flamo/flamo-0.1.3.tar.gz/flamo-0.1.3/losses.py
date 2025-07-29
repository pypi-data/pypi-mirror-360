import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List
from flamo.auxiliary.filterbank import FilterBank
from nnAudio import features
import pyfar as pf


class mse_loss(nn.Module):
    """Mean Squared Error Loss"""

    def __init__(self, nfft: int, energy_norm: bool = False, name: str = "MSE"):
        super(mse_loss, self).__init__()
        self.name = name
        self.nfft = nfft
        self.energy_norm = energy_norm
        self.transform = lambda x: torch.fft.rfft(x, n=self.nfft, dim=1)
        self.mse = nn.MSELoss(reduction="mean")

    def forward(self, x, y):
        X = self.transform(x)
        Y = self.transform(y)
        if self.energy_norm:
            X = X / torch.norm(X, p=2)
            Y = Y / torch.norm(Y, p=2)
        return self.mse(X, Y)


## -------------------- MULTI SCALE SPECTRAL LOSSES
class mel_mss_loss(nn.Module):
    r"""
    Multi-Scale Spectral Loss in the Mel scale.
    This loss function computes the difference between predicted and true audio signals
    in the Mel spectrogram domain across multiple FFT sizes.
    The number of Mel bins is determined by the current FFT size divided by 8.
    It is possible to apply a mask based on Signal-to-Noise Ratio (SNR) to the loss computation (this is particularly useful for training models on noisy data).
    The mask is calculated from the target (true) signal and is applied to both target and prediction before loss computation.
    The noise will be calculated as the mean of the energy of the last 0.01s unless its value is being passed as an argument.

    The loss is computed as the p norm of the difference between the predicted and true Mel spectrograms.
    The spectrogram is computed using nnAudio's MelSpectrogram class.

    Attributes:
        - **nfft** (list): A list of FFT sizes to compute the multi-scale spectrograms.
        - **overlap** (float): The overlap ratio for the STFT computation. Default is 0.75.
        - **sample_rate** (int): The sampling rate of the audio signals. Default is 48000.
        - **energy_norm** (bool): Whether to normalize the energy of the input signals. Default is False.
        - **device** (str): The device to run the computations on (e.g., "cpu" or "cuda"). Default is "cpu".
        - **name** (str): A name for the loss function. Default is "MelMSS".
        - **nfft** (list): A list of FFT sizes to compute the multi-scale spectrograms.
        - **overlap** (float): The overlap ratio for the STFT computation. Default is 0.75.
        - **apply_mask** (bool): Whether to apply a mask based on SNR. Default is False.
        - **threshold** (float): The SNR threshold for masking. Default is 5.
        - **p** (str): The order of the norm to be used. Default is "fro" (Frobenius norm).
        - **log_term** (bool): Whether to include the log term in the loss computation. Default is False.
        - **alpha** (float): A scaling factor for the log term in the loss computation. Default is 1.0.
        - **noise_energy** (float): The energy of the noise to be used for masking. Default is None.
    """

    def __init__(
        self,
        nfft: List[int] = [128, 256, 512, 1024, 2048, 4096],
        overlap: float = 0.75,
        sample_rate: int = 48000,
        energy_norm: bool = False,
        device="cpu",
        name: str = "MelMSS",
        apply_mask: bool = False,
        threshold: float = 5,
        p: str = "fro", 
        log_term: bool = False,
        alpha: float = 1.0,
        noise_energy = None,
    ):
        super().__init__()
        self.nfft = nfft
        self.overlap = overlap
        self.sample_rate = sample_rate
        self.energy_norm = energy_norm
        self.name = name
        self.device = device
        self.apply_mask = apply_mask
        self.threshold = threshold
        self.p = p 
        self.log_term = log_term
        self.alpha = alpha
        self.noise_energy = noise_energy

    def forward(self, y_pred, y_true):
        # assert that y_pred and y_true have the same shape = (n_batch, n_samples, n_channels)
        if len(y_pred.shape) == 1:
            y_pred = y_pred.unsqueeze(0).unsqueeze(-1)
            y_true = y_true.unsqueeze(0).unsqueeze(-1)
        assert (y_pred.shape == y_true.shape) & (
            len(y_true.shape) == 3
        ), "y_pred and y_true must have the same shape (n_batch, n_samples, n_channels)"

        n_channels = y_pred.shape[-1]
        batch_size = y_pred.shape[0]

        if self.energy_norm:
            y_pred = y_pred / torch.norm(y_pred, p=2)
            y_true = y_true / torch.norm(y_true, p=2)

        # reshape it to (num_audio, len_audio) as indicated by nnAudio
        y_pred = torch.reshape(y_pred, (-1, y_pred.shape[1]))
        y_true = torch.reshape(y_true, (-1, y_true.shape[1]))

        loss = 0  # initialize loss
        for i, nfft in enumerate(self.nfft):
            # initialize stft function with new nfft
            hop_length = int(nfft * (1 - self.overlap))
            mel_stft = features.mel.MelSpectrogram(
                n_fft=nfft,
                hop_length=hop_length,
                window="hann",
                sr=self.sample_rate,
                fmin=0,
                fmax=self.sample_rate // 2,
                n_mels=nfft // 8,
                verbose=False,
            )
            mel_stft = mel_stft.to(self.device)

            h, w = tuple(mel_stft(y_pred).shape[-2:])
            Y_pred_lin = torch.reshape(mel_stft(y_pred), (batch_size, h, w, n_channels))
            Y_true_lin = torch.reshape(mel_stft(y_true), (batch_size, h, w, n_channels))

            mask = torch.ones_like(Y_true_lin)
            if self.apply_mask:
                if not self.noise_energy:
                    # compute the noise energy as the mean of the last 0.01s
                    self.noise_energy = torch.mean(
                        torch.pow(
                            Y_true_lin[
                                :, :, -int(0.01 * self.sample_rate / hop_length), :
                            ],
                            2,
                        )
                    )
                SNR = 10 * torch.log10(
                    torch.max(Y_true_lin**2, self.noise_energy * 1.01)
                    - self.noise_energy
                ) - 10 * torch.log10(self.noise_energy)
                mask[SNR < self.threshold] = 0
                N = torch.sum(mask)
            else:
                N = torch.numel(Y_true_lin)

            # update match loss
            loss += torch.norm((Y_true_lin - Y_pred_lin) * mask, p=self.p) / N
            if self.log_term:
                Y_pred_log = torch.reshape(torch.log(mel_stft(y_pred)), (batch_size, h, w, n_channels))
                Y_true_log = torch.reshape(torch.log(mel_stft(y_true)), (batch_size, h, w, n_channels))
                loss += self.alpha * torch.norm((Y_true_log - Y_pred_log) * mask, p=self.p) / N
                

class mss_loss(nn.Module):
    r"""
    Multi-Scale Spectral Loss in the linear scale.
    This loss function computes the difference between predicted and true audio signals
    in the linear spectrogram domain across multiple FFT sizes.
    It is possible to apply a mask based on Signal-to-Noise Ratio (SNR) to the loss computation (this is particularly useful for training models on noisy data).
    The mask is calculated from the target (true) signal and is applied to both target and prediction before loss computation.
    The noise will be calculated as the mean of the energy of the last 0.01s unless its value is being passed as an argument.

    The loss is computed as the p norm of the difference between the predicted and true spectrograms.
    The spectrogram is computed using nnAudio's STFT class.

    Using the :arg:`form` argument, the loss can be computed in different ways:
    - **None**: The loss is computed as the p norm of the difference between the predicted and true spectrograms.
    - **yamamoto**: The loss is computed as the Frobenius norm of the difference between the predicted and true spectrograms, divided by the Frobenius norm of the true spectrogram. The log term is computed as the L1 norm of the difference between the predicted and true log spectrograms, divided by the number of elements in the true log spectrogram.
    - **magenta**: The loss is computed as the L1 norm of the difference between the predicted and true spectrograms, divided by the number of elements in the true spectrogram. The log term is computed as the L1 norm of the difference between the predicted and true log spectrograms, divided by the number of elements in the true log spectrogram.

    Attributes:
        - **nfft** (list): A list of FFT sizes to compute the multi-scale spectrograms.
        - **overlap** (float): The overlap ratio for the STFT computation. Default is 0.75.
        - **sample_rate** (int): The sampling rate of the audio signals. Default is 48000.
        - **energy_norm** (bool): Whether to normalize the energy of the input signals. Default is False.
        - **device** (str): The device to run the computations on (e.g., "cpu" or "cuda"). Default is "cpu".
        - **name** (str): A name for the loss function. Default is "MelMSS".
        - **nfft** (list): A list of FFT sizes to compute the multi-scale spectrograms.
        - **overlap** (float): The overlap ratio for the STFT computation. Default is 0.75.
        - **apply_mask** (bool): Whether to apply a mask based on SNR. Default is False.
        - **threshold** (float): The SNR threshold for masking. Default is 5.
        - **p** (str): The order of the norm to be used. Default is "fro" (Frobenius norm).
        - **log_term** (bool): Whether to include the log term in the loss computation. Default is False.
        - **alpha** (float): A scaling factor for the log term in the loss computation. Default is 1.0.
        - **form** (str): The form of the loss to be used. Default is None.
        - **noise_energy** (float): The energy of the noise to be used for masking. Default is None.

    References:
        - Yamamoto, R., Song, E., & Kim, J. M. (2020, May). Parallel WaveGAN: A fast waveform generation model based on generative adversarial networks with multi-resolution spectrogram. In ICASSP 2020-2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) (pp. 6199-6203). IEEE.
        - Engel, J., Hantrakul, L., Gu, C., & Roberts, A. (2020). DDSP: Differentiable digital signal processing. arXiv preprint arXiv:2001.04643.
    """
    def __init__(
        self,
        nfft: List[int] = [128, 256, 512, 1024, 2048, 4096],
        overlap: float = 0.75,
        sample_rate: int = 48000,
        energy_norm: bool = False,
        device="cpu",
        name: str = "MSS",
        apply_mask: bool = False,
        threshold: float = 5,
        p: str = "fro", 
        log_term: bool = False,
        alpha: float = 1.0,
        form: str = None,
        noise_energy = None,
    ):
        super().__init__()
        self.nfft = nfft
        self.overlap = overlap
        self.sample_rate = sample_rate
        self.energy_norm = energy_norm
        self.name = name
        self.device = device
        self.apply_mask = apply_mask
        self.threshold = threshold
        self.p = p 
        self.log_term = log_term
        self.alpha = alpha
        self.form = form
        self.noise_energy = noise_energy

    def forward(self, y_pred, y_true):
        # assert that y_pred and y_true have the same shape = (n_batch, n_samples, n_channels)
        if len(y_pred.shape) == 1:
            y_pred = y_pred.unsqueeze(0).unsqueeze(-1)
            y_true = y_true.unsqueeze(0).unsqueeze(-1)
        assert (y_pred.shape == y_true.shape) & (
            len(y_true.shape) == 3
        ), "y_pred and y_true must have the same shape (n_batch, n_samples, n_channels)"

        n_channels = y_pred.shape[-1]
        batch_size = y_pred.shape[0]

        if self.energy_norm:
            y_pred = y_pred / torch.norm(y_pred, p=2)
            y_true = y_true / torch.norm(y_true, p=2)

        # reshape it to (num_audio, len_audio) as indicated by nnAudio
        y_pred = torch.reshape(y_pred, (-1, y_pred.shape[1]))
        y_true = torch.reshape(y_true, (-1, y_true.shape[1]))

        loss = 0  # initialize match loss
        for i, nfft in enumerate(self.nfft):
            # initialize stft function with new nfft
            hop_length = int(nfft * (1 - self.overlap))
            lin_stft = features.stft.STFT(
                n_fft=nfft,
                hop_length=hop_length,
                window="hann",
                freq_scale="linear",
                sr=self.sample_rate,
                fmin=20,
                fmax=self.sample_rate // 2,
                output_format="Magnitude",
                verbose=False,
            )
            lin_stft = lin_stft.to(self.device)

            h, w = tuple(lin_stft(y_pred).shape[-2:])
            Y_pred_lin = torch.reshape(lin_stft(y_pred), (batch_size, h, w, n_channels))
            Y_true_lin = torch.reshape(lin_stft(y_true), (batch_size, h, w, n_channels))
            Y_pred_log = torch.reshape(torch.log(lin_stft(y_pred)), (batch_size, h, w, n_channels))
            Y_true_log = torch.reshape(torch.log(lin_stft(y_true)), (batch_size, h, w, n_channels))

            mask = torch.ones_like(Y_true_lin)
            if self.apply_mask:
                if not self.noise_energy:
                    # compute the noise energy as the mean of the last 0.01s
                    self.noise_energy = torch.mean(
                        torch.pow(
                            Y_true_lin[
                                :, :, -int(0.01 * self.sample_rate / hop_length), :
                            ],
                            2,
                        )
                    )
                SNR = 10 * torch.log10(
                    torch.max(Y_true_lin**2, self.noise_energy * 1.01)
                    - self.noise_energy
                ) - 10 * torch.log10(self.noise_energy)
                mask[SNR < self.threshold] = 0
                N = torch.sum(mask)
            else:
                N = torch.numel(Y_true_lin)

            # update match loss
            if self.form == None:
                loss += torch.norm((Y_true_lin - Y_pred_lin) * mask, p=self.p) / N
                if self.log_term:
                    loss += self.alpha * torch.norm((Y_true_log - Y_pred_log) * mask, p=self.p) / N
            elif self.form == 'yamamoto':  
                loss += torch.norm((Y_true_lin - Y_pred_lin) * mask, p="fro") / torch.norm(
                    Y_true_lin, p="fro"
                ) + self.alpha * torch.norm((Y_true_log - Y_pred_log) * mask, p=1) / torch.numel(
                    Y_true_log
                )
            elif self.form == 'magenta':
                loss += (
                    torch.norm((Y_true_lin - Y_pred_lin) * mask, p=1)
                    + self.alpha * torch.sum(torch.abs(Y_true_log - Y_pred_log) * mask)
                ) / torch.numel(Y_true_lin)

        return loss

class AveragePower(nn.Module):
    r"""
    Average Power Loss.

    This loss function computes the average power convergence between prediction and target.
    It calculates the normalized Frobenius norm of the difference between the windowed spectrograms of the predicted and true signals.

    Attributes:
        - **energy_norm** (bool): Whether to normalize the energy of the input signals. Default is False.
        - **name** (str): A name for the loss function. Default is "Average Power".
        - **stride** (int): The stride for the convolution operation. Default is (4,4).
        - **device** (str): The device to run the computations on (e.g., "cpu" or "cuda"). Default is "cpu".
    
    References:
        - Dal Santo, Gloria, et al. "Similarity metrics for late reverberation." 2024 58th Asilomar Conference on Signals, Systems, and Computers. IEEE, 2024.
    """
    def __init__(
        self, 
        energy_norm: bool = False, 
        name: str = "Average Power", 
        stride: tuple = (4, 4),
        device="cpu"
    ):
        super(AveragePower, self).__init__()
        self.name = name
        self.energy_norm = energy_norm
        self.stride = stride
        self.device = device

    def forward(self, y_pred, y_true):
        # assert that y_pred and y_true have the same shape = (n_batch, n_samples, n_channels)
        if len(y_pred.shape) == 1:
            y_pred = y_pred.unsqueeze(0).unsqueeze(-1)
            y_true = y_true.unsqueeze(0).unsqueeze(-1)
        assert (y_pred.shape == y_true.shape) & (
            len(y_true.shape) == 3
        ), "y_pred and y_true must have the same shape (n_batch, n_samples, n_channels)"

        if self.energy_norm:
            y_pred = y_pred / torch.norm(y_pred, p=2)
            y_true = y_true / torch.norm(y_true, p=2)
        return self.average_power(y_pred, y_true)[0]
    
    def average_power(self, y_pred, y_true): 
        # compute the magnitude spectrogram
        S1 = torch.abs(
            torch.stft(
                y_pred.squeeze(),
                n_fft=1024,
                hop_length=256,
                window=torch.hann_window(1024).to(self.device),
                return_complex=True,
            )
        )
        S2 = torch.abs(
            torch.stft(
                y_true.squeeze(),
                n_fft=1024,
                hop_length=256,
                window=torch.hann_window(1024).to(self.device),
                return_complex=True,
            )
        )

        # create 2d window
        win = self.window2d(torch.hann_window(64, dtype=S1.dtype, device=self.device))
        # convolve spectrograms with the window
        S1_win = F.conv2d(
            S1.unsqueeze(0).unsqueeze(0), win.unsqueeze(0).unsqueeze(0), stride=self.stride
        ).squeeze()
        S2_win = F.conv2d(
            S2.unsqueeze(0).unsqueeze(0), win.unsqueeze(0).unsqueeze(0), stride=self.stride
        ).squeeze()
        # compute the normalized difference between the two windowed spectrograms
        return (
            torch.norm(S2_win - S1_win, p="fro") / torch.norm(S1_win, p="fro"),
            S1_win,
            S2_win,
        )

    def window2d(self, window):
        """create a 2D window from a given 1D window"""
        return window[:, None] * window[None, :]
    
## -------------------- ENERGY DECAY RELIEF LOSSES
class edr_loss(nn.Module):
    r"""
    Energy Decay Relief (EDR) Loss.

    This loss function computes the frequency-dependent loss on the mel-scale energy decay relief (EDR).

    Attributes:
        - **nfft** (int): The FFT size for the STFT computation. Default is 1024.
        - **overlap** (float): The overlap ratio for the STFT computation. Default is 0.5.
        - **sample_rate** (int): The sampling rate of the audio signals. Default is 48000.
        - **energy_norm** (bool): Whether to normalize the energy of the input signals. Default is False.
        - **device** (str): The device to run the computations on (e.g., "cpu" or "cuda"). Default is "cpu".
        - **name** (str): A name for the loss function. Default is "EDR".

    References:
        - Mezza, A. I., Giampiccolo, R., & Bernardini, A. (2024). Modeling the frequency-dependent sound energy decay of acoustic environments with differentiable feedback delay networks. In Proceedings of the 27th International Conference on Digital Audio Effects (DAFx24) (pp. 238-245).
    """
    def __init__(
        self,
        nfft: int = 1024,
        overlap: float = 0.5,
        sample_rate: int = 48000,
        energy_norm: bool = False,
        device: str = "cpu",
        name: str = "EDR",
    ):
        super().__init__()
        self.nfft = nfft
        self.overlap = overlap
        self.sample_rate = sample_rate
        self.energy_norm = energy_norm
        self.win_length = int(0.020 * self.sample_rate)
        self.name = name
        self.device = device

    def discard_last_n_percent(self, x, n_percent):
        # Discard last n%
        last_id = int(np.round((1 - n_percent / 100) * x.shape[1]))
        out = x[:, 0:last_id, :]

        return out

    def schroeder_backward_int(self, x):
        # expected shape (batch_size, h, w, n_channels)
        # Backwards integral
        out = torch.flip(x, dims=[-2])
        out = torch.cumsum(out**2, dim=-2)
        out = torch.flip(out, dims=[-2])

        # Normalize to 1
        if self.energy_norm:
            norm_vals = torch.max(out, dim=-2, keepdim=True)[0]  # per channel
        else:
            norm_vals = torch.ones(out.shape, device=out.device)

        out = out / norm_vals

        return out, norm_vals

    def get_edr(self, x):
        # Remove filtering artefacts (last 5 permille)
        out = self.discard_last_n_percent(x, 0.5)
        # compute EDCs
        out = self.schroeder_backward_int(self.filterbank(out))[0]
        # get energy in dB
        out = 10 * torch.log10(out + 1e-32)

        return out

    def mel_stft(self, x):
        # compute the mel spectrogram
        mel_stft = features.mel.MelSpectrogram(
            n_fft=self.nfft,
            hop_length=int(self.win_length * (1 - self.overlap)),
            window="hann",
            win_length=self.win_length,
            sr=self.sample_rate,
            fmin=20,
            fmax=self.sample_rate // 2,
            n_mels=64,
            verbose=False,
        ).to(self.device, dtype=x.dtype)

        return mel_stft(x)

    def forward(self, y_pred, y_true):
        # assert that y_pred and y_true have the same shape = (n_batch, n_samples, n_channels)
        if len(y_pred.shape) == 1:
            y_pred = y_pred.unsqueeze(0).unsqueeze(-1)
            y_true = y_true.unsqueeze(0).unsqueeze(-1)

        assert (y_pred.shape == y_true.shape) & (
            len(y_true.shape) == 3
        ), "y_pred and y_true must have the same shape (n_batch, n_samples, n_channels)"

        n_channels = y_pred.shape[-1]
        batch_size = y_pred.shape[0]
        # reshape it to (num_audio, len_audio) as indicated by nnAudio
        y_pred = torch.reshape(y_pred, (-1, y_pred.shape[1]))
        y_true = torch.reshape(y_true, (-1, y_true.shape[1]))

        h, w = tuple(self.mel_stft(y_pred).shape[-2:])
        Y_pred = torch.reshape(self.mel_stft(y_pred), (batch_size, h, w, n_channels))
        Y_true = torch.reshape(self.mel_stft(y_true), (batch_size, h, w, n_channels))

        Y_pred_edr = 10 * torch.log10(self.schroeder_backward_int(Y_pred)[0])
        Y_true_edr = 10 * torch.log10(self.schroeder_backward_int(Y_true)[0])

        clip_indx = torch.nonzero(
            Y_true_edr == torch.tensor(-float("inf"), device=self.device),
            as_tuple=True,
        )
        Y_true_edr[clip_indx] = torch.finfo(Y_true_edr.dtype).eps
        Y_pred_edr[clip_indx] = torch.finfo(Y_pred_edr.dtype).eps
        # create a mask for values 
        loss = torch.norm(Y_true_edr - Y_pred_edr, p=1) / torch.norm(Y_true_edr, p=1)
        if torch.isnan(loss):
            print("EDR loss is NaN, returning 0")
            return torch.tensor(0.0, device=self.device)
        return loss


## -------------------- ENERGY DECAY CURVE LOSSES
class edc_loss(nn.Module):
    r"""
    Energy Decay Curve (EDC) Loss.

    This loss function computes the loss on energy decay curves (EDCs).
    It evaluates the similarity between the predicted and target EDCs, either in broadband or subband.

    Attributes:
        - **sample_rate** (int): The sampling rate of the audio signals. Default is 48000.
        - **nfft** (int): The FFT size. Default is 96000.
        - **is_broadband** (bool): Whether to compute the loss in broadband or subband. Default is False.
        - **n_fractions** (int): The number of fractional octave bands for subband analysis. Default is 1.
        - **energy_norm** (bool): Whether to normalize the energy of the input signals. Default is False.
        - **convergence** (bool): Whether to compute the normalized mean squared error. Default is False.
        - **clip** (bool): Whether to clip the EDCs at -60 dB. Default is False.
        - **name** (str): A name for the loss function. Default is "EDC".
        - **device** (str): The device to run the computations on (e.g., "cpu" or "cuda"). Default is "cpu".
    """
    def __init__(
        self,
        sample_rate: int = 48000,
        is_broadband: bool = False,
        n_fractions: int = 1,
        energy_norm: bool = False,
        convergence: bool = False,
        clip: bool = False,
        name: str = "EDC",
        device: str = "cpu",
    ):
        super().__init__()
        self.sample_rate = sample_rate
        self.is_broadband = is_broadband
        self.n_fractions = n_fractions
        self.energy_norm = energy_norm
        self.convergence = convergence
        self.clip = clip
        self.name = name
        self.device = device
        self.discard_n = 0.5
        self.mse = nn.MSELoss(reduction="mean")
        
    def filterbank(self, x):
        impulse = torch.zeros(x.shape[1])
        impulse[0] = 1.0    
        filter = torch.tensor(
            pf.dsp.filter.fractional_octave_bands(
                pf.Signal(impulse.numpy(), self.sample_rate),
                num_fractions=self.n_fractions,    
                frequency_range=(63, 16000),
            ).freq.T
        ).squeeze()
        y = torch.zeros(*x.shape, filter.shape[1])

        for i_band in range(filter.shape[-1]):
            y[..., i_band] = torch.fft.irfft(
                torch.einsum(
                    "nfb,f->nfb",
                    torch.fft.rfft(x, dim=1, n = x.shape[1]*2 - 1),
                    torch.nn.functional.pad(filter[:, i_band],  (0, x.shape[1] - filter.shape[0])),
                ),
                dim=1,
                n = x.shape[1],
            )
        return y
    
    def discard_last_n_percent(self, x, n_percent):
        # Discard last n%
        last_id = int(np.round((1 - n_percent / 100) * x.shape[1]))
        out = x[:, 0:last_id, :]

        return out

    def schroeder_backward_int(self, x):

        # Backwards integral
        out = torch.flip(x, dims=[1])
        out = torch.cumsum(out**2, dim=1)
        out = torch.flip(out, dims=[1])

        # Normalize to 1
        if self.energy_norm:
            norm_vals = torch.max(out, dim=1, keepdim=True)[0]  # per channel
        else:
            norm_vals = torch.ones_like(out)

        out = out / norm_vals

        return out, norm_vals

    def get_edc(self, x):
        # Remove filtering artefacts (last 5 permille)
        out = self.discard_last_n_percent(x, self.discard_n)
        # compute EDCs
        if self.is_broadband:
            out = self.schroeder_backward_int(out)[0]
        else:
            out = self.schroeder_backward_int(self.filterbank(out))[0]
        # get energy in dB
        out = torch.clamp(out, min=torch.finfo(out.dtype).eps)
        out = 10 * torch.log10(out)

        return out

    def forward(self, y_pred, y_true):
        # assert that y_pred and y_true have the same shape = (n_batch, n_samples, n_channels)
        if len(y_pred.shape) == 1:
            y_pred = y_pred.unsqueeze(0).unsqueeze(-1)
            y_true = y_true.unsqueeze(0).unsqueeze(-1)
        assert (y_pred.shape == y_true.shape) & (
            len(y_true.shape) == 3
        ), "y_pred and y_true must have the same shape (n_batch, n_samples, n_channels)"

        # compute the edcs
        y_pred_edc = self.get_edc(y_pred)
        y_true_edc = self.get_edc(y_true)

        if self.clip:
            try:
                clip_indx = torch.nonzero(
                    y_true_edc < (torch.max(y_true_edc, dim=1, keepdim=True)[0] - 60),
                    as_tuple=True,
                )
                y_pred_edc[clip_indx] = -180
                y_true_edc[clip_indx] = -180
            except:
                pass
        else:
            clip_indx = torch.nonzero(
                y_true_edc == torch.tensor(-float("inf"), device=self.device),
                as_tuple=True,
            )
            y_true_edc[clip_indx] = torch.finfo(y_true_edc.dtype).eps
            clip_indx = torch.nonzero(
                y_pred_edc == torch.tensor(-float("inf"), device=self.device),
                as_tuple=True,
            )
            y_pred_edc[clip_indx] = torch.finfo(y_pred_edc.dtype).eps

        # compute normalized mean squared error on the EDCs
        num = self.mse(y_pred_edc, y_true_edc)
        den = torch.mean(torch.pow(y_true_edc, 2))
        if self.convergence:
            return num / den
        else:
            return num

## -------------------- ECHO DENSITY PROFILE LOSSES
class soft_edp_loss(nn.Module):
    """
    Soft echo density profile loss as in
    "Modeling the frequency-dependent sound energy decay of acoustic environments
    with differentiable feedback delay networks"
    """

    def __init__(
        self,
        sample_rate: int = 48000,
        energy_norm: bool = False,
        window_size: int = 512,
        device: str = "cpu",
        name: str = "EDP",
    ):
        super().__init__()
        self.sample_rate = sample_rate
        self.energy_norm = energy_norm
        self.window_size = window_size
        self.name = name
        self.device = device
        self.kappa_min = 10**2
        self.kappa_max = 10**5
        window = torch.hann_window((2 * window_size + 1), device=device)
        self.window = window / torch.sum(window)

    def edp(self, x):
        L = x.shape[-1]
        edp = torch.empty((x.shape[0], L))
        # pad the input
        x = F.pad(x, (self.window_size * 2 + 1, 0, 0, 0))
        for n in range(0, L):
            kappa = self.kappa_min + (self.kappa_max - self.kappa_min) / L * n
            frame = x[..., n : (n + 2 * self.window_size + 1)]
            frame_std = torch.std(frame, dim=-1)
            frame = torch.sigmoid(torch.abs(frame * kappa) - frame_std)
            edp[..., n] = torch.sum(frame * self.window) / torch.erfc(
                torch.tensor(1 / np.sqrt(2), device=self.device)
            )

        return edp

    def forward(self, y_pred, y_true):
        if self.energy_norm:
            y_pred = y_pred / torch.norm(y_pred, p=2)
            y_true = y_true / torch.norm(y_true, p=2)
        # squeeze last channel dimension
        y_pred = y_pred.squeeze(-1)
        y_true = y_true.squeeze(-1)

        edp_pred = self.edp(y_pred)
        edp_true = self.edp(y_true)

        loss = torch.mean(torch.pow(edp_true - edp_pred, 2))
        return loss
