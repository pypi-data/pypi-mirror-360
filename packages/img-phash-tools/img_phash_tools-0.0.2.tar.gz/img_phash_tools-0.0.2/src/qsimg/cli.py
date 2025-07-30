"""Image Hash Command-line tool."""

from pathlib import Path

import random
import typer
from typing_extensions import Annotated
from imgphash.image_phash import ImagePHash

from dupimg.cli import run_fast_scandir


def qsimg_cli(  # noqa: MC0001
    # pylint: disable=too-many-arguments,too-many-locals
    directory: Annotated[
        str,
        typer.Argument(help="The directory name."),
    ] = ".",
    *,
    reference: Annotated[
        str,
        typer.Argument(
            help="Reference file name. If given, it will "
            "sort only by similarity with this image."
        ),
    ] = "",
    rand: Annotated[
        bool,
        typer.Option(help="Use a random reference"),
    ] = True,
    seed: Annotated[
        int,
        typer.Option(help="Seed for the random generator"),
    ] = -1,
    extensions: Annotated[
        str,
        typer.Option(
            help="List of extensions to filter " "separated by a coma."
        ),
    ] = "jpg,jpeg,png,gif,webp,bmp",
    mode: Annotated[
        str,
        typer.Option(
            help="The hash mode : [averageHash, blockMeanHash, "
            "marrHildrethHash, pHash, radialVarianceHash]."
        ),
    ] = "pHash",
    recurse: Annotated[
        bool,
        typer.Option(help="Recurse over folders."),
    ] = True,
    flip_v: Annotated[
        bool,
        typer.Option(
            help="Flip the image vertically (so hash will be flip resistant)."
        ),
    ] = False,
    flip_h: Annotated[
        bool,
        typer.Option(
            help="Flip the image horizontally (so hash will be flip "
            "resistant)."
        ),
    ] = False,
    block_mean_hash_mode: Annotated[
        int,
        typer.Option(help="block_mean_hash_mode int, default:0"),
    ] = 0,
    marr_hildreth_hash_alpha: Annotated[
        float,
        typer.Option(help="marr_hildreth_hash_alpha float, default:2.0"),
    ] = 2.0,
    marr_hildreth_hash_scale: Annotated[
        float,
        typer.Option(help="marr_hildreth_hash_scale float, default:1.0"),
    ] = 1.0,
    radial_variance_hash_sigma: Annotated[
        float,
        typer.Option(help="radial_variance_hash_sigma float, default:1.0"),
    ] = 1.0,
    radial_variance_hash_num_of_angle_line: Annotated[
        int,
        typer.Option(
            help="radial_variance_hash_num_of_angle_line int, default:180"
        ),
    ] = 180,
    verbose: Annotated[
        bool,
        typer.Option(help="Print more values."),
    ] = False,
) -> None:
    """
    Quick Find Similar images with perceptual hash algorithms.

    It returns an ordered list by similarity with the reference image.

    In random mode, it will find a random reference.

    """
    if reference != "" and not Path(reference).is_file():
        raise ValueError("Filename not found", reference)
    if reference != "" and Path(reference).is_file():
        rand = False
    if not Path(directory).is_dir():
        raise ValueError("Directory not found", directory)
    ext: list[str] = []
    for ex in extensions.split(","):
        ext.append("." + ex)
    _, files = run_fast_scandir(directory, ext, recurse)
    if seed != -1:
        random.seed(seed)
    if rand:
        reference = files[random.randint(0, len(files) - 1)]  # nosec B311
    my_file = Path(reference)
    if not my_file.is_file():
        raise ValueError("File not found", reference)
    img_hash = ImagePHash(
        filename=reference, mode=mode, flip_v=flip_v, flip_h=flip_h
    )
    img_hash.block_mean_hash_mode = block_mean_hash_mode
    img_hash.marr_hildreth_hash_scale = marr_hildreth_hash_scale
    img_hash.marr_hildreth_hash_alpha = marr_hildreth_hash_alpha
    img_hash.radial_variance_hash_num_of_angle_line = (
        radial_variance_hash_num_of_angle_line
    )
    img_hash.radial_variance_hash_sigma = radial_variance_hash_sigma
    img_hash.image_hash_file()
    ref_hashes = img_hash.hash

    files_dist: dict[str, float] = {}
    for _, file in enumerate(files):
        img_hash = ImagePHash(
            filename=file, mode=mode, flip_v=flip_v, flip_h=flip_h
        )
        img_hash.block_mean_hash_mode = block_mean_hash_mode
        img_hash.marr_hildreth_hash_scale = marr_hildreth_hash_scale
        img_hash.marr_hildreth_hash_alpha = marr_hildreth_hash_alpha
        img_hash.radial_variance_hash_num_of_angle_line = (
            radial_variance_hash_num_of_angle_line
        )
        img_hash.radial_variance_hash_sigma = radial_variance_hash_sigma
        img_hash.image_hash_file()
        files_dist[file] = ImagePHash.min_hash_distance(
            ref_hashes, img_hash.hash, verbose=False
        )
    files_dist = dict(sorted(files_dist.items(), key=lambda item: item[1]))
    for k, v in files_dist.items():
        if verbose:
            print(f"{k};{v:.0f};")
        else:
            print(k)


app = typer.Typer()
app.command()(qsimg_cli)


if __name__ == "__main__":
    app()
