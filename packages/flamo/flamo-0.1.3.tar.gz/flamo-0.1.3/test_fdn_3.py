import torch
import torch.nn as nn
import argparse
import os
import time
import auraloss
import scipy
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
from flamo.auxiliary.reverb import parallelFDNPEQ
from losses import *

torch.manual_seed(130799)
# set datatype to float64
torch.set_default_dtype(torch.float64)
def assign_parameters(args, model, param, perturb=False):
    with torch.no_grad():
        core = model.get_core()
        for key, value in param.items():
            try:
                tensor_value = torch.tensor(value, device=args.device)
            except:
                continue
            if key == "A":
                core.feedback_loop.feedback.mixing_matrix.assign_value(tensor_value)
            elif key == "B":
                core.input_gain.assign_value(tensor_value.T)
            elif key == "C":
                core.output_gain.assign_value(tensor_value)

        model.set_core(core)

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
    delay_lengths = torch.tensor([997, 1153, 1327, 1559, 1801, 2099])
    ## ---------------- CONSTRUCT FDN ---------------- ##

    # Input and output gains
    input_gain = dsp.Gain(
        size=(N, 1),
        nfft=args.nfft,
        requires_grad=False,
        alias_decay_db=alias_decay_db,
        device=args.device,
    )
    output_gain = dsp.Gain(
        size=(1, N),
        nfft=args.nfft,
        requires_grad=False,
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
        requires_grad=False,
        device=args.device,
    )
    attenuation = parallelFDNPEQ(
        nfft=args.nfft,
        fs=args.samplerate,
        delays=delay_lengths,
        design='biquad',
        requires_grad=True,
        device=args.device,
    )
    attenuation.map = lambda x: x
    
    boradband_attenuation = dsp.parallelGain(
        size=(N,),
        nfft=args.nfft,
        # map = lambda x: torch.sigmoid(x),
        map = lambda x: x,
        requires_grad=True,
        alias_decay_db=alias_decay_db,
        device=args.device,
    )
    boradband_attenuation.map = lambda x: 10**((x[0]*delay_lengths)/20)
    # boradband_attenuation.assign_value(10**((-60/ (args.samplerate * torch.tensor(-1))*delay_lengths)/20))
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
    output_layer = dsp.iFFT(nfft=args.nfft)
    model = system.Shell(core=FDN, input_layer=input_layer, output_layer=output_layer)

    ## ---------------- OVERWRITE PARAMS ---------------- ##

    input_imp = signal_gallery(
        1,
        n_samples=args.nfft,
        n=1,
        signal_type="impulse",
        fs=args.samplerate,
        device=args.device,
    )

    ## create target 
    param = scipy.io.loadmat("data/params/parameters_optim.mat")
    perturb = True
    assign_parameters(args, model, param, perturb)
    # 20.0000, 43.0887, 92.8318, 200.0000, 430.8870, 928.3179, 2000.0002, 4308.8696, 9283.1777, 20000.0000
    rt = torch.tensor([2.0730, 2.5073, 2.4073, 2.0081, 1.8886, 1.7032, 1.6435, 1.0094, 0.6855,  0.5500])
    gain = -60 / 48000 / rt 
    # get the minimum value of the gain along the first axis
    min_gain = torch.min(gain, dim=0)[0]  # shift by one to avoid staying on the 0db axis  
    gain = gain - min_gain
    freqs = -1000*torch.ones(10) # this is just the bias 
    R = torch.tensor(2) /  torch.sqrt( 2* torch.ones(10))
    new_param = torch.cat((freqs.unsqueeze(1), R.unsqueeze(1), gain.unsqueeze(1)), dim=1).unsqueeze(-1)
    min_gain = (min_gain * torch.ones(6))
    ## assign target PEQ
    core = model.get_core()
    core.feedback_loop.feedback.peq.assign_value(new_param)
    core.feedback_loop.feedback.broadband_attenuation.assign_value(min_gain)
    model.set_core(core)

    target_rir_fdn = model.get_time_response(identity=False, fs=args.samplerate).squeeze()
    save_audio(
        os.path.join(args.train_dir, f"target_fdn.wav"),
        target_rir_fdn / torch.max(torch.abs(target_rir_fdn)),
        fs=args.samplerate,
    )

    # input_imp = signal_gallery(
    #     1,
    #     n_samples=args.nfft,
    #     n=1,
    #     signal_type="impulse",
    #     fs=args.samplerate,
    #     device=args.device,
    # )

    # Hatt = core.feedback_loop.feedback.peq(torch.fft.rfft(input_imp, n=args.nfft, dim=1).repeat(1, 1, 6))
    # Hatt = 20*torch.log10(torch.abs(Hatt)).squeeze()
    # RT = -60 / (Hatt * args.samplerate) * delay_lengths
    # freqs_axis = torch.fft.rfftfreq(args.nfft, 1 / args.samplerate)

    # plt.figure()
    # for i in range(N):
    #     plt.semilogx(freqs_axis, RT[:, i].detach(), label=f"channel {i}")
    # plt.plot(core.feedback_loop.feedback.peq.center_freq_bias.detach().numpy(), rt, "x", label="target")
    # plt.xlabel("Frequency (Hz)")
    # plt.ylabel("RT60 (s)")
    # plt.savefig(os.path.join(args.train_dir, f"RT60_{index}.png"))


    # perturb the trainable parameters 
    core = model.get_core()
    core.feedback_loop.feedback.peq.assign_value( new_param * torch.rand_like(new_param))
    core.feedback_loop.feedback.broadband_attenuation.assign_value(min_gain * torch.rand_like(min_gain))
    model.set_core(core)


    ## ---------------- OPTIMIZATION SET UP ---------------- ##


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
        # target_rir = torch.tensor(data.iloc[index].rir, dtype=torch.float32).to(args.device)
        # save_audio(
        #     os.path.join(args.train_dir, f"target_{index}.wav"),
        #     target_rir / torch.max(torch.abs(target_rir)),
        #     fs=args.samplerate,
        # )
        # # remove offset 
        # rir_onset = find_onset(target_rir)
        # target_rir = target_rir[rir_onset : (rir_onset + args.nfft)].view(1, -1, 1)
        # # zeropad the rest of the RIR or truncate it to the nfft
        # if target_rir.shape[1] < args.nfft:
        #     target_rir = torch.nn.functional.pad(
        #         target_rir, (0, args.nfft - target_rir.shape[1])
        #     )
        # elif target_rir.shape[1] > args.nfft:
        #     target_rir = target_rir[:, :args.nfft]
        # generate the dataset 
        dataset = Dataset(
            input=input_imp,
            target=target_rir_fdn.unsqueeze(0).unsqueeze(-1),
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
        trainer.register_criterion(edr_loss(energy_norm=True), 1)

        ## ---------------- TRAIN ---------------- ##

        # Train the model
        trainer.train(train_loader, valid_loader)

        # get the optimized attenuation filter 
        core = model.get_core()
        Hatt = core.feedback_loop.feedback.peq(torch.fft.rfft(input_imp, n=args.nfft, dim=1).repeat(1, 1, 6))
        Hatt *= core.feedback_loop.feedback.broadband_attenuation(torch.fft.rfft(input_imp, n=args.nfft, dim=1).repeat(1, 1, 6))
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
        # plt.plot([125, 250, 500, 1000, 2000, 4000, 8000], data.iloc[index].t60, "x", label="target")
        plt.plot([125, 250, 500, 1000, 2000, 4000, 8000], rt, "x", label="target")
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

    parser.add_argument("--nfft", type=int, default=96000*2, help="FFT size")
    parser.add_argument("--samplerate", type=int, default=48000, help="sampling rate")
    parser.add_argument("--num", type=int, default=100, help="dataset size")
    parser.add_argument(
        "--device", type=str, default="cuda", help="device to use for computation"
    )
    parser.add_argument(
        "--batch_size", type=int, default=1, help="batch size for training"
    )
    parser.add_argument(
        "--max_epochs", type=int, default=40, help="maximum number of epochs"
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


## desigining the PEQ + gain
## (10, 3, 6) PEQ
## (6) broadband attenuation 
## rt = [3.4073 3.0081 2.8886 2.7032 2.6435 1.6694 0.6855]
