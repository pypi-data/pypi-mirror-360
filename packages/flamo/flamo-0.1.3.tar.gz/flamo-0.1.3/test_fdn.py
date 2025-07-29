import torch
import torch.nn as nn
import argparse
import os
import time
import auraloss
import soundfile as sf
import matplotlib.pyplot as plt
import pandas as pd
from collections import OrderedDict
from flamo.optimize.dataset import Dataset, load_dataset
from flamo.optimize.trainer import Trainer
from flamo.processor import dsp, system
from flamo.optimize.loss import sparsity_loss
from flamo.utils import save_audio
from flamo.functional import signal_gallery, find_onset
from flamo.auxiliary.reverb import parallelFDNGEQ
from losses import *

torch.manual_seed(130799)


class MultiResoSTFT(nn.Module):
    """compute the mean absolute error between the auraloss of two RIRs"""

    def __init__(self):
        super().__init__()
        self.MRstft = auraloss.freq.MultiResolutionSTFTLoss()

    def forward(self, rir1, rir2):
        return self.MRstft(rir1.permute(0, 2, 1), rir2.permute(0, 2, 1))
    
class filter_mse_loss(nn.Module):
    r"""
    Wrapper for the mean squared error loss.

    .. math::

        \mathcal{L} = \frac{1}{N} \sum_{i=1}^{N} \left( y_{\text{pred},i} -  y_{\text{true},i} \right)^2

    where :math:`N` is the number of nfft points and :math:`M` is the number of channels.

    **Arguments / Attributes**:
        - **nfft** (int): Number of FFT points.
        - **device** (str): Device to run the calculations on.

    """

    def __init__(self, nfft: int, delays: torch.Tensor, target: torch.Tensor, fs: int, device: str = "cpu"):

        super().__init__()
        self.nfft = nfft
        self.delays = delays
        self.fs = fs
        self.target = target  
        # interpolate the target so that it has the same number of points as the nfft
        self.target = torch.tensor(self.target, dtype=torch.float32).to(device)
        self.bands = torch.tensor([125, 250, 500, 1000, 2000, 4000, 8000])
        self.device = device
        self.mse_loss = nn.MSELoss()
        self.input_imp = signal_gallery(
            1,
            n_samples=nfft,
            n=1,
            signal_type="impulse",
            fs=fs,
            device=device)
    

    def forward(self, y_pred, y_true, model: nn.Module,):
        """
        Calculates the mean squared error loss.
        If :attr:`is_masked` is set to True, the loss is calculated using a masked version of the predicted output. This option is useful to introduce stochasticity, as the mask is generated randomly.

        **Arguments**:
            - **y_pred** (torch.Tensor): The predicted output.
            - **y_true** (torch.Tensor): The target output.

        Returns:
            torch.Tensor: The calculated MSE loss.
        """
        core = model.get_core()
        Hatt = core.feedback_loop.feedback.attenuation(torch.fft.rfft(self.input_imp, n=self.nfft, dim=1).repeat(1, 1, 6))
        Hatt = 20*torch.log10(torch.abs(Hatt)).squeeze()
        RT = -60 / (Hatt * self.fs) * self.delays
        freqs = torch.fft.rfftfreq(self.nfft, 1 / self.fs)
        # find the closest frequency to the target bands
        target_bands = torch.zeros((len(self.bands)))
        for i in range(len(self.bands)):
            target_bands[i] = torch.argmin(torch.abs(freqs - self.bands[i]))
        return self.mse_loss(RT[target_bands.int(), 0], torch.tensor(self.target,dtype=RT.dtype).to(self.device))
    
class mse_loss(nn.Module):
    r"""
    Wrapper for the mean squared error loss.

    .. math::

        \mathcal{L} = \frac{1}{N} \sum_{i=1}^{N} \left( y_{\text{pred},i} -  y_{\text{true},i} \right)^2

    where :math:`N` is the number of nfft points and :math:`M` is the number of channels.

    **Arguments / Attributes**:
        - **nfft** (int): Number of FFT points.
        - **device** (str): Device to run the calculations on.

    """

    def __init__(self, nfft: int, delays: torch.Tensor, device: str = "cpu"):

        super().__init__()
        self.nfft = nfft
        self.delays = delays
        self.device = device
        self.mse_loss = nn.MSELoss()

    def forward(self, y_pred, y_true, model: nn.Module,):
        """
        Calculates the mean squared error loss.
        If :attr:`is_masked` is set to True, the loss is calculated using a masked version of the predicted output. This option is useful to introduce stochasticity, as the mask is generated randomly.

        **Arguments**:
            - **y_pred** (torch.Tensor): The predicted output.
            - **y_true** (torch.Tensor): The target output.

        Returns:
            torch.Tensor: The calculated MSE loss.
        """
        core = model.get_core()
        try:
            A = core.feedback_loop.feedback.map(core.feedback_loop.feedback.param)
        except:
            A = core.feedback_loop.feedback.mixing_matrix.map(
                core.feedback_loop.feedback.mixing_matrix.param
            )
        B = core.input_gain.map(core.input_gain.param)
        C = core.output_gain.map(core.output_gain.param)
        B = torch.complex(B, torch.zeros_like(B))
        C = torch.complex(C, torch.zeros_like(C))
        angle = torch.linspace(0, 1, self.nfft)
        abs = torch.ones((self.nfft), )
        z = abs * torch.exp(1j * angle * torch.pi) 
        D = torch.diag_embed(torch.unsqueeze(z, dim=-1) ** self.delays)
        Gamma = torch.complex(torch.diag(torch.tensor(0.9999)**self.delays), torch.zeros_like(A))
        Hchannel = torch.matmul(torch.inverse(D - torch.matmul(torch.complex(A, torch.zeros_like(A)),Gamma)), B)
        H = Hchannel.squeeze()*C.squeeze()  
        
        y_pred_sum = torch.sum(torch.abs(H), dim=-1)
        return self.mse_loss(y_pred_sum, abs)
    
def normalize_energy(
        model,
        target_energy=1,
    ):
        """energy normalization done in the frequency domain
        Note that the energy computed from the frequency response is not the same as the energy of the impulse response
        Read more at https://pytorch.org/docs/stable/generated/torch.fft.rfft.html
        """

        H = model.get_freq_response(identity=False)
        energy_H = torch.mean(torch.pow(torch.abs(H), 2))
        target_energy = torch.tensor(target_energy)
        # apply energy normalization on input and output gains only
        with torch.no_grad():
            core = model.get_core()
            core.input_gain.assign_value(
                torch.div(
                    core.input_gain.param, torch.pow(energy_H / target_energy, 1 / 4)
                )
            )
            core.output_gain.assign_value(
                torch.div(
                    core.output_gain.param, torch.pow(energy_H / target_energy, 1 / 4)
                )
            )
            model.set_core(core)

        # recompute the energy of the FDN
        H = model.get_freq_response(identity=False)
        energy_H = torch.mean(torch.pow(torch.abs(H), 2))
        # assert (
        #     abs(energy_H - target_energy) / target_energy < 0.001
        # ), "Energy normalization failed"
        return model
    
def example_fdn(args):
    """
    Example function that demonstrates the construction and training of a Feedback Delay Network (FDN) model.
    Args:
        args: A dictionary or object containing the necessary arguments for the function.
    Returns:
        None
    """

    # FDN parameters
    N = 6  # number of delays
    alias_decay_db = 0  # alias decay in dB
    delay_lengths = torch.tensor([593, 743, 929, 1153, 1399, 1699])
    ## ---------------- CONSTRUCT FDN ---------------- ##

    # Input and output gains
    input_gain = dsp.Gain(
        size=(N, 1),
        nfft=args.nfft,
        requires_grad=True,
        alias_decay_db=alias_decay_db,
        device=args.device,
    )
    output_gain = dsp.Gain(
        size=(1, N),
        nfft=args.nfft,
        requires_grad=True,
        device=args.device,
    )
    # Feedback loop with delays
    delays = dsp.parallelDelay(
        size=(N,),
        max_len=delay_lengths.max(),
        nfft=args.nfft,
        isint=True,
        requires_grad=False,
        device=args.device,
    )
    delays.assign_value(delays.sample2s(delay_lengths))
    # Feedback path with orthogonal matrix
    mixing_matrix = dsp.Matrix(
        size=(N, N),
        nfft=args.nfft,
        matrix_type="orthogonal",
        requires_grad=True,
        device=args.device,
    )
    attenuation = dsp.parallelPEQ(
        size=(N,),
        nfft=args.nfft,
        fs=args.samplerate,
        design='biquad',
        requires_grad=True,
        device=args.device,
    )
    boradband_attenuation = dsp.parallelGain(
        size=(N,),
        nfft=args.nfft,
        map = lambda x: torch.sigmoid(x),
        requires_grad=True,
        alias_decay_db=alias_decay_db,
        device=args.device,
    )
    boradband_attenuation.assign_value(10**((-60/ (args.samplerate * torch.tensor(1))*delay_lengths)/20))
    attenuation_series = system.Series(
        OrderedDict(
            {
                "peq": attenuation,
                "broadband_attenuation": boradband_attenuation,
            }
        )
    )
    # attenuation.map = lambda x: 20 * torch.log10(torch.sigmoid(x))
    feedback = system.Series(
        OrderedDict({"mixing_matrix": mixing_matrix, "attenuation": attenuation_series})
    )

    # Recursion
    feedback_loop = system.Recursion(fF=delays, fB=feedback)

    # Full FDN
    FDN = system.Series(
        OrderedDict(
            {
                "input_gain": input_gain,
                "feedback_loop": feedback_loop,
                "output_gain": output_gain,
            }
        )
    )
    # Create the model with Shell
    input_layer = dsp.FFT(args.nfft)
    # Since time aliasing mitigation is enabled, we use the iFFTAntiAlias layer
    # to undo the effect of the anti aliasing modulation introduced by the system's layers
    output_layer = dsp.iFFT(nfft=args.nfft)
    model = system.Shell(core=FDN, input_layer=input_layer, output_layer=output_layer)
    model = normalize_energy(model, target_energy=1)

    ## ---------------- OPTIMIZATION SET UP ---------------- ##

    input_imp = signal_gallery(
        1,
        n_samples=args.nfft,
        n=1,
        signal_type="impulse",
        fs=args.samplerate,
        device=args.device,
    )
    # load data as dataframe 
    datafile = "/Users/dalsag1/Aalto Dropbox/Gloria Dal Santo/aalto/projects/speech2fdn/speech2fdn/data/rirs_dataframe_sampled.pkl"
    data = pd.read_pickle(datafile)
    for index in range(len(data)):
        # Get initial impulse response
        with torch.no_grad():
            ir_init = model.get_time_response(identity=False, fs=args.samplerate).squeeze()
            save_audio(
                os.path.join(args.train_dir,  f"ir_init_{index}.wav"),
                ir_init / torch.max(torch.abs(ir_init)),
                fs=args.samplerate,
            )
        target_rir = torch.tensor(data.iloc[index].rir, dtype=torch.float32).to(args.device)
        save_audio(
            os.path.join(args.train_dir, f"target_{index}.wav"),
            target_rir / torch.max(torch.abs(target_rir)),
            fs=args.samplerate,
        )
        # remove offset 
        rir_onset = find_onset(target_rir)
        target_rir = target_rir[rir_onset : (rir_onset + args.nfft)].view(1, -1, 1)
        # zeropad the rest of the RIR or truncate it to the nfft
        if target_rir.shape[1] < args.nfft:
            target_rir = torch.nn.functional.pad(
                target_rir, (0, args.nfft - target_rir.shape[1])
            )
        elif target_rir.shape[1] > args.nfft:
            target_rir = target_rir[:, :args.nfft]
        # generate the dataset 
        dataset = Dataset(
            input=input_imp,
            target=target_rir,
            expand=args.num,
            device=args.device,
        )
        train_loader, valid_loader = load_dataset(dataset, batch_size=args.batch_size)

        # Initialize training process
        trainer = Trainer(
            model,
            max_epochs=args.max_epochs,
            lr=args.lr,
            train_dir=args.train_dir,
            device=args.device,
        )
        # trainer.register_criterion(filter_mse_loss(nfft=args.nfft, delays=delay_lengths, target=data.iloc[index].t60, fs=args.samplerate), 1, requires_model=True)
        # trainer.register_criterion(sparsity_loss(), 0.1, requires_model=True)
        # trainer.register_criterion(mse_loss(args.nfft, delays = delay_lengths), 0.1, requires_model=True)
        # trainer.register_criterion(edc_loss(energy_norm=True, clip=True, convergence=True), 1)
        trainer.register_criterion(mel_mss_loss(energy_norm=True, apply_mask=True), 1)

        ## ---------------- TRAIN ---------------- ##

        # Train the model
        trainer.train(train_loader, valid_loader)

        # get the optimized attenuation filter 
        core = model.get_core()
        Hatt = core.feedback_loop.feedback.attenuation(torch.fft.rfft(input_imp, n=args.nfft, dim=1).repeat(1, 1, 6))
        Hatt = 20*torch.log10(torch.abs(Hatt)).squeeze()
        RT = -60 / (Hatt * args.samplerate) * delay_lengths
        freqs = torch.fft.rfftfreq(args.nfft, 1 / args.samplerate)
        # Get optimized impulse response
        with torch.no_grad():
            ir_optim = model.get_time_response(identity=False, fs=args.samplerate).squeeze()
            save_audio(
                os.path.join(args.train_dir, f"ir_optim_{index}.wav"),
                ir_optim / torch.max(torch.abs(ir_optim)),
                fs=args.samplerate,
            )
        plt.figure()
        for i in range(N):
            plt.semilogx(freqs, RT[:, i].detach(), label=f"channel {i}")
        plt.plot([125, 250, 500, 1000, 2000, 4000, 8000], data.iloc[index].t60, "x", label="target")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("RT60 (s)")
        plt.savefig(os.path.join(args.train_dir, f"RT60_{index}.png"))

        # initialize all the parameters to the initial values
        with torch.no_grad():
            core = model.get_core()
            core.input_gain.init_param()
            core.output_gain.init_param()
            core.feedback_loop.feedback.mixing_matrix.init_param()
            model.set_core(core)
            model = normalize_energy(model, target_energy=1)
            trainer.optimizer.zero_grad()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--nfft", type=int, default=96000, help="FFT size")
    parser.add_argument("--samplerate", type=int, default=48000, help="sampling rate")
    parser.add_argument("--num", type=int, default=100, help="dataset size")
    parser.add_argument(
        "--device", type=str, default="cuda", help="device to use for computation"
    )
    parser.add_argument(
        "--batch_size", type=int, default=1, help="batch size for training"
    )
    parser.add_argument(
        "--max_epochs", type=int, default=10, help="maximum number of epochs"
    )
    parser.add_argument("--lr", type=float, default=1e-3, help="learning rate")
    parser.add_argument(
        "--train_dir", type=str, help="directory to save training results"
    )
    parser.add_argument(
        "--masked_loss", type=bool, default=False, help="use masked loss"
    )
    parser.add_argument(
        "--target_rir",
        type=str,
        default="rirs/arni_35_3541_4_2.wav",
        help="filepath to target RIR",
    )

    args = parser.parse_args()

    # check for compatible device
    if args.device == "cuda" and not torch.cuda.is_available():
        args.device = "cpu"

    # make output directory
    if args.train_dir is not None:
        if not os.path.isdir(args.train_dir):
            os.makedirs(args.train_dir)
    else:
        args.train_dir = os.path.join("output", time.strftime("%Y%m%d-%H%M%S"))
        os.makedirs(args.train_dir)

    # save arguments
    with open(os.path.join(args.train_dir, "args.txt"), "w") as f:
        f.write(
            "\n".join(
                [
                    str(k) + "," + str(v)
                    for k, v in sorted(vars(args).items(), key=lambda x: x[0])
                ]
            )
        )

    example_fdn(args)
