#!python3
""" Iterative template matching parameter tuning.

    Copyright (c) 2024 European Molecular Biology Laboratory

    Author: Valentin Maurer <valentin.maurer@embl-hamburg.de>
"""
import argparse
import subprocess
from sys import exit
from time import time
from shutil import copyfile
from typing import Tuple, List, Dict

import numpy as np
from scipy import optimize
from sklearn.metrics import roc_auc_score

from tme import Orientations, Density
from tme.matching_utils import generate_tempfile_name, load_pickle, write_pickle, create_mask
from tme.matching_exhaustive import MATCHING_EXHAUSTIVE_REGISTER

def parse_range(x : str):
    start, stop,step = x.split(":")
    return range(int(start), int(stop), int(step))

def parse_args():
    parser = argparse.ArgumentParser(
        description="Refine template matching candidates using deep matching.",
    )
    io_group = parser.add_argument_group("Input / Output")
    io_group.add_argument(
        "--orientations",
        required=True,
        type=str,
        help="Path to an orientations file in a supported format. See "
        "https://kosinskilab.github.io/pyTME/reference/api/tme.orientations.Orientations.from_file.html"
        " for available options.",
    )
    io_group.add_argument(
        "--output_prefix", required=True, type=str, help="Path to write output to."
    )
    io_group.add_argument(
        "--iterations",
        required=False,
        default=0,
        type=int,
        help="Number of refinement iterations to perform.",
    )
    io_group.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="More verbose and more files written to disk.",
    )
    matching_group = parser.add_argument_group("Template Matching")
    matching_group.add_argument(
        "--input_file",
        required=False,
        type=str,
        help="Path to the output of match_template.py.",
    )
    matching_group.add_argument(
        "-m",
        "--target",
        dest="target",
        type=str,
        required=False,
        help="Path to a target in CCP4/MRC, EM, H5 or another format supported by "
        "tme.density.Density.from_file "
        "https://kosinskilab.github.io/pyTME/reference/api/tme.density.Density.from_file.html",
    )
    matching_group.add_argument(
        "--target_mask",
        dest="target_mask",
        type=str,
        required=False,
        help="Path to a mask for the target in a supported format (see target).",
    )
    matching_group.add_argument(
        "-i",
        "--template",
        dest="template",
        type=str,
        required=False,
        help="Path to a template in PDB/MMCIF or other supported formats (see target).",
    )
    matching_group.add_argument(
        "--template_mask",
        dest="template_mask",
        type=str,
        required=False,
        help="Path to a mask for the template in a supported format (see target).",
    )
    matching_group.add_argument(
        "--invert_target_contrast",
        dest="invert_target_contrast",
        action="store_true",
        default=False,
        help="Invert the target's contrast and rescale linearly between zero and one. "
        "This option is intended for targets where templates to-be-matched have "
        "negative values, e.g. tomograms.",
    )
    matching_group.add_argument(
        "--angular_sampling",
        dest="angular_sampling",
        required=True,
        default=None,
        help="Angular sampling rate using optimized rotational sets."
        "A lower number yields more rotations. Values >= 180 sample only the identity.",
    )
    matching_group.add_argument(
        "-s",
        dest="score",
        type=str,
        default="FLCSphericalMask",
        choices=list(MATCHING_EXHAUSTIVE_REGISTER.keys()),
        help="Template matching scoring function.",
    )
    matching_group.add_argument(
        "-n",
        dest="cores",
        required=False,
        type=int,
        default=4,
        help="Number of cores used for template matching.",
    )
    matching_group.add_argument(
        "--use_gpu",
        dest="use_gpu",
        action="store_true",
        default=False,
        help="Whether to perform computations on the GPU.",
    )
    matching_group.add_argument(
        "--no_centering",
        dest="no_centering",
        action="store_true",
        help="Assumes the template is already centered and omits centering.",
    )
    matching_group.add_argument(
        "--no_edge_padding",
        dest="no_edge_padding",
        action="store_true",
        default=False,
        help="Whether to not pad the edges of the target. Can be set if the target"
        " has a well defined bounding box, e.g. a masked reconstruction.",
    )
    matching_group.add_argument(
        "--no_fourier_padding",
        dest="no_fourier_padding",
        action="store_true",
        default=False,
        help="Whether input arrays should not be zero-padded to full convolution shape "
        "for numerical stability. When working with very large targets, e.g. tomograms, "
        "it is safe to use this flag and benefit from the performance gain.",
    )

    peak_group = parser.add_argument_group("Peak Calling")
    peak_group.add_argument(
        "--number_of_peaks",
        type=int,
        default=100,
        required=False,
        help="Upper limit of peaks to call, subject to filtering parameters. Default 1000. "
        "If minimum_score is provided all peaks scoring higher will be reported.",
    )
    extraction_group = parser.add_argument_group("Extraction")
    extraction_group.add_argument(
        "--keep_out_of_box",
        action="store_true",
        required=False,
        help="Whether to keep orientations that fall outside the box. If the "
        "orientations are sensible, it is safe to pass this flag.",
    )

    optimization_group = parser.add_argument_group("Optimization")
    optimization_group.add_argument(
        "--lowpass",
        dest="lowpass",
        action="store_true",
        default=False,
        help="Optimize template matching lowpass filter cutoff.",
    )
    optimization_group.add_argument(
        "--highpass",
        dest="highpass",
        action="store_true",
        default=False,
        help="Optimize template matching highpass filter cutoff.",
    )
    optimization_group.add_argument(
        "--lowpass-range",
        dest="lowpass_range",
        type=str,
        default="0:50:5",
        help="Optimize template matching lowpass filter cutoff.",
    )
    optimization_group.add_argument(
        "--highpass-range",
        dest="highpass_range",
        type=str,
        default="0:50:5",
        help="Optimize template matching highpass filter cutoff.",
    )
    optimization_group.add_argument(
        "--translation-uncertainty",
        dest="translation_uncertainty",
        type=int,
        default=None,
        help="Optimize template matching highpass filter cutoff.",
    )


    args = parser.parse_args()

    data_present = args.target is not None and args.template is not None
    if args.input_file is None and not data_present:
        raise ValueError(
            "Either --input_file or --target and --template need to be specified."
        )
    elif args.input_file is not None and data_present:
        raise ValueError(
            "Please specific either --input_file or --target and --template."
        )

    if args.lowpass_range != "None":
        args.lowpass_range = parse_range(args.lowpass_range)
    else:
        args.lowpass_range = (None, )
    if args.highpass_range != "None":
        args.highpass_range = parse_range(args.highpass_range)
    else:
        args.highpass_range = (None, )
    return args


def argdict_to_command(input_args: Dict, executable: str) -> List:
    ret = []
    for key, value in input_args.items():
        if value is None:
            continue
        elif isinstance(value, bool):
            if value:
                ret.append(key)
        else:
            ret.extend([key, value])

    ret = [str(x) for x in ret]
    ret.insert(0, executable)
    return " ".join(ret)

def run_command(command):
    ret = subprocess.run(command, capture_output=True, shell=True)
    if ret.returncode != 0:
        print(f"Error when executing: {command}.")
        print(f"Stdout: {ret.stdout.decode('utf-8')}")
        print(f"Stderr: {ret.stderr.decode('utf-8')}")
        exit(-1)

    return None

def create_stacking_argdict(args) -> Dict:
    arg_dict = {
        "--target": args.target,
        "--template": args.template,
        "--orientations": args.orientations,
        "--output_file": args.candidate_stack_path,
        "--keep_out_of_box": args.keep_out_of_box,
    }
    return arg_dict


def create_matching_argdict(args) -> Dict:
    arg_dict = {
        "--target": args.target,
        "--template": args.template,
        "--template_mask": args.template_mask,
        "-o": args.match_template_path,
        "-a": args.angular_sampling,
        "-s": args.score,
        "--no_fourier_padding": True,
        "--no_edge_padding": True,
        "--no_centering": args.no_centering,
        "-n": args.cores,
        "--invert_target_contrast": args.invert_target_contrast,
        "--use_gpu": args.use_gpu,
    }
    return arg_dict


def create_postprocessing_argdict(args) -> Dict:
    arg_dict = {
        "--input_file": args.match_template_path,
        "--target_mask": args.target_mask,
        "--output_prefix": args.new_orientations_path,
        "--peak_caller": "PeakCallerMaximumFilter",
        "--number_of_peaks": args.number_of_peaks,
        "--output_format": "orientations",
        "--mask_edges": True,
    }
    if args.target_mask is not None:
        arg_dict["--mask_edges"] = False
    return arg_dict


def update_orientations(old : Orientations, new : Orientations, args, **kwargs) -> Orientations:
    stack_shape = Density.from_file(args.candidate_stack_path, use_memmap=True).shape
    stack_center = np.add(np.divide(stack_shape, 2).astype(int), np.mod(stack_shape, 2))

    peak_number = new.translations[:, 0].astype(int)
    new_translations = np.add(
        old.translations[peak_number],
        np.subtract(new.translations, stack_center)[:, 1:],
    )
    ret = old.copy()
    ret.scores[:] = 0
    ret.scores[peak_number] = new.scores
    ret.translations[peak_number] = new_translations

    # The effect of --align_orientations should be handled herer
    return ret


class DeepMatcher:
    def __init__(self, args, margin : float = 0.5):
        self.args = args
        self.margin = margin
        self.orientations = Orientations.from_file(args.orientations)

        match_template_args = create_matching_argdict(args)
        match_template_args["--target"] = args.candidate_stack_path
        self.match_template_args = match_template_args

        self.filter_parameters = {}
        if args.lowpass:
            self.filter_parameters["--lowpass"] = 0
        if args.highpass:
            self.filter_parameters["--highpass"] = 200
        # self.filter_parameters["--whiten"] = False
        self.filter_parameters["--no_filter_target"] = False


        self.postprocess_args = create_postprocessing_argdict(args)
        self.postprocess_args["--number_of_peaks"] = 1

    def get_initial_values(self) -> Tuple[float]:
        ret = tuple(float(x) for x in self.filter_parameters.values())
        return ret

    def format_parameters(self, parameter_values: Tuple[float]) -> Dict:
        ret = {}
        for value, key in zip(parameter_values, self.filter_parameters.keys()):
            ret[key] = value
            if isinstance(self.filter_parameters[key], bool):
                ret[key] = value > 0.5
        return ret

    def forward(self, x : Tuple[float]):


        # Label 1 -> True positive, label 0 -> false positive
        orientations_new = self(x)
        label, score = orientations_new.details, orientations_new.scores
        # loss = np.add(
        #     (1 - label) * np.square(score),
        #     label * np.square(np.fmax(self.margin - score, 0.0))
        # )
        # loss = loss.mean()



        loss = roc_auc_score(label, score)
        # print(
        #     np.mean(score[label == 1]), np.mean(score[label == 0]),
        #     *x, loss, time()
        # )

        return loss

    def __call__(self, x: Tuple[float]):
        filter_parameters = self.format_parameters(x)
        self.match_template_args.update(filter_parameters)
        match_template = argdict_to_command(
            self.match_template_args,
            executable="python3 $HOME/src/pytme/scripts/match_template_filters.py",
        )
        run_command(match_template)

        # Assume we get a new peak for each input in the same order
        postprocess = argdict_to_command(
            self.postprocess_args,
            executable="python3 $HOME/src/pytme/scripts/postprocess.py",
        )
        run_command(postprocess)

        orientations_new = Orientations.from_file(
            f"{self.postprocess_args['--output_prefix']}.tsv"
        )
        orientations_new = update_orientations(
            new=orientations_new,
            old=self.orientations,
            args=self.args
        )

        label, score = orientations_new.details, orientations_new.scores
        loss = roc_auc_score(label, score)
        print(
            np.mean(score[label == 1]), np.mean(score[label == 0]),
            *x, 0, loss, time()
        )


        # Rerun with noise correction
        temp_args = self.match_template_args.copy()
        background_file = generate_tempfile_name(".pickle")
        temp_args["--scramble_phases"] = True
        temp_args["-o"] = background_file
        match_template = argdict_to_command(
            temp_args,
            executable="python3 $HOME/src/pytme/scripts/match_template_filters.py",
        )
        run_command(match_template)
        temp_args = self.match_template_args.copy()
        temp_args["--background_file"] = background_file
        postprocess = argdict_to_command(
            self.postprocess_args,
            executable="python3 $HOME/src/pytme/scripts/postprocess.py",
        )
        run_command(postprocess)

        orientations_new = Orientations.from_file(
            f"{self.postprocess_args['--output_prefix']}.tsv"
        )
        orientations_new = update_orientations(
            new=orientations_new,
            old=self.orientations,
            args=self.args
        )

        label, score = orientations_new.details, orientations_new.scores
        loss = roc_auc_score(label, score)
        print(
            np.mean(score[label == 1]), np.mean(score[label == 0]),
            *x, 1, loss, time()
        )

        return orientations_new

    # def __call__(self, x: Tuple[float]):
    #     filter_parameters = self.format_parameters(x)
    #     # print(filter_parameters)
    #     self.match_template_args.update(filter_parameters)
    #     match_template = argdict_to_command(
    #         self.match_template_args,
    #         executable="python3 $HOME/src/pytme/scripts/match_template_filters.py",
    #     )
    #     run_command(match_template)

    #     data = load_pickle(self.args.match_template_path)
    #     temp_args = self.match_template_args.copy()
    #     temp_args["--scramble_phases"] = True
    #     # write_pickle(data, "/home/vmaurer/deep_matching/t.pickle")

    #     match_template = argdict_to_command(
    #         temp_args,
    #         executable="python3 $HOME/src/pytme/scripts/match_template_filters.py",
    #     )
    #     run_command(match_template)
    #     data_norm = load_pickle(self.args.match_template_path)
    #     # write_pickle(data_norm, "/home/vmaurer/deep_matching/noise.pickle")

    #     data[0] = (data[0] - data_norm[0]) / (1 - data_norm[0])
    #     data[0] = np.fmax(data[0], 0)
    #     write_pickle(data, self.args.match_template_path)

    #     # Assume we get a new peak for each input in the same order
    #     postprocess = argdict_to_command(
    #         self.postprocess_args,
    #         executable="python3 $HOME/src/pytme/scripts/postprocess.py",
    #     )
    #     run_command(postprocess)

    #     orientations_new = Orientations.from_file(
    #         f"{self.postprocess_args['--output_prefix']}.tsv"
    #     )
    #     orientations_new = update_orientations(
    #         new=orientations_new,
    #         old=self.orientations,
    #         args=self.args
    #     )

    #     return orientations_new


def main():
    args = parse_args()

    if args.input_file is not None:
        data = load_pickle(args.input_file)
        target_origin, _, sampling_rate, cli_args = data[-1]
        args.target, args.template = cli_args.target, cli_args.template

    args.candidate_stack_path = generate_tempfile_name(suffix=".h5")
    args.new_orientations_path = generate_tempfile_name()
    args.match_template_path = generate_tempfile_name()

    match_deep = DeepMatcher(args)
    initial_values = match_deep.get_initial_values()

    # Do a single pass over the data
    if len(initial_values) == 0:
        create_image_stack = create_stacking_argdict(args)
        create_image_stack = argdict_to_command(
            create_image_stack,
            executable="python3 $HOME/src/pytme/scripts/extract_candidates.py",
        )
        run_command(create_image_stack)

        print("Created image stack")
        if args.verbose:
            copyfile(args.candidate_stack_path, f"{args.output_prefix}_stack.h5")

        print("Starting matching")
        orientations = match_deep(x=())

        if args.verbose:
            copyfile(args.match_template_path, f"{args.output_prefix}_stack.pickle")
        print("Completed matching")
        orientations.to_file(f"{args.output_prefix}.tsv")
        exit(0)

    if args.translation_uncertainty is not None:
        args.target_mask = generate_tempfile_name(suffix=".h5")

    for current_iteration in range(args.iterations):
        create_image_stack = create_stacking_argdict(args)
        create_image_stack = argdict_to_command(
            create_image_stack,
            executable="python3 $HOME/src/pytme/scripts/extract_candidates.py",
        )
        run_command(create_image_stack)

        if args.translation_uncertainty is not None:
            dens = Density.from_file(args.candidate_stack_path)
            stack_center = np.add(
                np.divide(dens.data.shape, 2).astype(int), np.mod(dens.data.shape, 2)
            ).astype(int)[1:]

            out = dens.empty
            out.data[:,...] = create_mask(
                mask_type = "ellipse",
                center = stack_center,
                radius = args.translation_uncertainty,
                shape = dens.data.shape[1:]
            )
            out.to_file(args.target_mask)



        # Perhaps we need a different optimizer here to use sensible steps for each parameter
        parameters, min_loss = (), None
        match_deep = DeepMatcher(args)
        # for lowpass in (0, 10, 20, 50):
        #     for highpass in (50, 100, 150, 200):
        #         for whiten in (False, True):
        #             loss = match_deep.forward((lowpass, highpass, whiten))
        #             # print((lowpass, highpass), loss)
        #             if min_loss is None:
        #                 min_loss = loss
        #             if loss < min_loss:
        #                 min_loss = loss
        #                 parameters = (lowpass, highpass, whiten),

        # for lowpass in (10, 50, 100, 200):
        #     for highpass in (10, 50, 100, 200):
        for lowpass in args.lowpass_range:
            for highpass in args.highpass_range:
                if lowpass is not None and highpass is not None:
                    if lowpass >= highpass:
                        continue
                for no_filter_target in (True, False):
                    loss = match_deep.forward((lowpass, highpass, no_filter_target))
                    if min_loss is None:
                        min_loss = loss
                    if loss < min_loss:
                        min_loss = loss
                        parameters = (lowpass, highpass, no_filter_target)

        # print("Final output", min_loss, parameters)
        import sys
        sys.exit(0)

        # parameters = optimize.minimize(
        #     x0=match_deep.get_initial_values(),
        #     fun=match_deep.forward,
        #     method="L-BFGS-B",
        #     options={"maxiter": 100}
        # )
        parameter_dict = match_deep.format_parameters(parameters)
        print("Converged with parameters", parameters)

        match_template = create_matching_argdict(args)
        match_template.update(parameter_dict)
        match_template = argdict_to_command(
            match_template,
            executable="python3 $HOME/src/pytme/scripts/match_template_filters.py",
        )
        _ = subprocess.run(match_template, capture_output=True, shell=True)

        # Some form of labelling is necessary for these matches
        # 1. All of them are true positives
        # 2. All of them are true positives up to a certain threshold
        # 3. Kernel fitting
        # 4. Perhaps also sensible to include a certain percentage of low scores as true negatives
        postprocess = create_postprocessing_argdict(args)
        postprocess = argdict_to_command(postprocess, executable="postprocess.py")
        _ = subprocess.run(postprocess, capture_output=True, shell=True)
        args.orientations = f"{args.new_orientations_path}.tsv"
        orientations = Orientations.from_file(args.orientations)
        orientations.to_file(f"{args.output_prefix}_{current_iteration}.tsv")


if __name__ == "__main__":
    main()
