import matplotlib.pyplot as plt
import iohub
from iohub import open_ome_zarr
from viscy.light.engine import VSUNet
from ipyfilechooser import FileChooser
import IPython
import os
import numpy as np
from typing import NamedTuple
import iohub

import os
from glob import glob
from pathlib import Path

import numpy as np
import torch
from iohub import open_ome_zarr
from numpy.typing import ArrayLike
from scipy import ndimage
from tqdm import tqdm
from viscy.light.engine import VSUNet
import ttach as tta
import argparse

def min_max_scale(image: ArrayLike) -> ArrayLike:
    "Normalizing the image using min-max scaling"
    min_val = image.min()
    max_val = image.max()
    return (image - min_val) / (max_val - min_val)


def normalize_fov(input:ArrayLike):
    "Normalizing the fov with zero mean and unit variance"
    mean = np.mean(input)
    std = np.std(input)
    return (input - mean) / std


def main():

    # Initialize the argument parser
    # NOTE: argument parser template written with copilot
    parser = argparse.ArgumentParser(
        description="Apply a VS model to on OME zarr dataset with regularization for temporal intensity fluctuations.")

    # Add arguments
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to the input ome zarr dataset."
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        required=True,
        help="Path to the model checkpoint."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=False,
        default="out.zarr",
        help="Path to save the output file. (default: out.zarr)"
    )
    parser.add_argument(
        "--smoothing",
        type=str,
        required=False,
        default=None,
        help="Smoothing mode (None for no temporal smoothing [default], gaussian for gaussian blur, tta for test-time augmentation)."
    )

    # Parse the arguments
    args = parser.parse_args()

    # Display the parsed arguments (for demonstration purposes)
    model_path = args.model
    zarr_path = args.input
    output_path = args.output
    smoothing = args.smoothing
    print(model_path, zarr_path, output_path, smoothing)
    if not model_path.endswith(".ckpt"):
        raise ValueError(f"{model_path} is not a .zarr file.")
    if not zarr_path.endswith(".zarr"):
        raise ValueError(f"{zarr_path} is not a .zarr file.")
    if smoothing not in [None, "gaussian", "tta"]:
        raise ValueError(f"{smoothing} is not a valid smoothing mode. Valid modes: None, gaussian, tta.")

    model_config = dict(
        in_channels=1,
        out_channels=2,
        encoder_blocks=[3, 3, 9, 3],
        dims=[96, 192, 384, 768],
        decoder_conv_blocks=2,
        stem_kernel_size=(1, 2, 2),
        in_stack_depth=1,
        pretraining=False,
    )
    # Load the model checkpoint
    model = VSUNet.load_from_checkpoint(
        model_path,
        architecture="UNeXt2_2D",
        model_config=model_config,
        accelerator='gpu'
    )
    model.eval()

    zarr: iohub.ngff.Plate = open_ome_zarr(zarr_path)
    output_zarr = open_ome_zarr(output_path, channel_names=['nuc_pred', 'mem_pred'], mode='w', layout='hcs')

    channel_names = zarr.channel_names
    print(f'Channel names: {channel_names}')

    # Finding the channel indices for the corresponding channel names
    phase_cidx = channel_names.index("Phase3D")

    # Iterating through the test dataset positions to:
    positions = zarr.positions()

    if smoothing == "tta":
        transforms = tta.Compose(
            [
                tta.HorizontalFlip(),
                tta.VerticalFlip(),
                tta.Rotate90(angles=[0, 180]),
                tta.Multiply(factors=[0.9, 1, 1.1]),
            ]
        )

    # Initializing the progress bar with the total number of positions
    for fov, pos in positions:
        print(f'FOV: {fov}')
        T, C, Z, Y, X = pos.data.shape
        padding = ((0, 0), (0, 0), (0, 0), (1, 1), (22, 23))
        position = output_zarr.create_position(*Path(f"{fov}/0").parts)
        output_array = np.zeros((T, 2, 1, Y, X), dtype=np.float32)
        print(T, C, Z, Y, X)
        with tqdm(total=T, desc="Processing timepoints") as pbar:
            # Iterating through the test dataset positions
            for t in range(T):
                # Getting the arrays and the center slices
                Z_slice = slice(Z // 2, Z // 2 + 1)
                phase_image = pos.data[t:t + 1, phase_cidx:phase_cidx + 1, Z_slice]

                # normalize the phase
                phase_image = normalize_fov(phase_image)

                # pad to 2048 x 2048 so that the input dimensions are divisible by 32
                phase_image = np.pad(phase_image, padding, mode="reflect")

                # Running the prediction
                phase_image = torch.from_numpy(phase_image).type(torch.float32)
                with torch.inference_mode():  # turn off gradient computation.
                    if smoothing == "tta":
                        augmentation_mem = np.zeros((24, 1, 1, 1, 2048, 2048))
                        augmentation_nuc = np.zeros((24, 1, 1, 1, 2048, 2048))
                        for t_num, transformer in enumerate(transforms):
                            augmented_image = transformer.augment_image(phase_image[:, :, 0, :, :]).to(model.device)
                            augmented_image = augmented_image[:, :, None, :, :]
                            out = model(augmented_image)
                            out_mem = transformer.deaugment_mask(out[:, 1:2, 0, :, :]).cpu().numpy()
                            out_nuc = transformer.deaugment_mask(out[:, 0:1, 0, :, :]).cpu().numpy()
                            out_mem = out_mem[:, :, None, :, :]
                            out_nuc = out_nuc[:, :, None, :, :]
                            augmentation_mem[t_num] = out_mem
                            augmentation_nuc[t_num] = out_nuc
                        predicted_mem = np.mean(augmentation_mem, axis=0).squeeze(0)
                        predicted_nuc = np.mean(augmentation_nuc, axis=0).squeeze(0)

                    else:
                        phase_image = phase_image.to(model.device)
                        predicted_image = model(phase_image)
                        predicted_image = predicted_image.cpu().numpy().squeeze(0)
                        predicted_mem = predicted_image[1, ...].squeeze(0)
                        predicted_nuc = predicted_image[0, ...].squeeze(0)

                # Crop back to original shape
                predicted_mem = predicted_mem[..., 1:-1, 22:-23]
                predicted_nuc = predicted_nuc[..., 1:-1, 22:-23]

                # Normalizing the output using min-max scaling
                predicted_mem = min_max_scale(predicted_mem)
                predicted_nuc = min_max_scale(predicted_nuc)

                # Save the predictions
                output_array[t, 0, 0, :, :] = predicted_nuc
                output_array[t, 1, 0, :, :] = predicted_mem

                # Update the progress bar
                pbar.update(1)

            if smoothing == "gaussian":
                # Gaussian smoothing helps a bit to remove intensity fluctuations but when the structures move a lot
                # between timepoints we get phantom artifacts from adjacent frames
                output_array = ndimage.gaussian_filter1d(output_array, sigma=3, axis=0)  # searched for with copilot

            position.create_image(f"{0}", output_array)

    # Close the OME-Zarr files
    zarr.close()
    output_zarr.close()


if __name__ == "__main__":
    main()