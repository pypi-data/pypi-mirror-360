"""Image Hash Command-line tool."""

from pathlib import Path

import numpy as np
import typer
from typing_extensions import Annotated
from imgphash.image_phash import ImagePHash

from dupimg.cli import run_fast_scandir


def matrix_to_csv(mat: dict[str, dict[str, float]]) -> None:
    """matrix_to_csv."""
    # print header
    print(";", end="")
    for sh1, _ in mat.items():
        print(sh1 + ";", end="")
    print("")
    for sh1, _ in mat.items():
        print(sh1 + ";", end="")
        for sh2, _ in mat.items():
            # diagonalisation of matrix
            if sh1 in mat and sh2 in mat[sh1]:
                print(f"{mat[sh1][sh2]:.0f};", end="")
            else:
                print(f"{mat[sh2][sh1]:.0f};", end="")
        print("")


def simg_cli(
    # pylint: disable=too-many-arguments,too-many-locals
    directory: Annotated[
        str,
        typer.Argument(help="The directory name."),
    ] = ".",
    *,
    mode: Annotated[
        str,
        typer.Option(
            help="The hash mode : [averageHash, blockMeanHash, "
            "colorMomentHash, marrHildrethHash, pHash, radialVarianceHash]."
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
) -> None:
    """
    Find Similar images with perceptual hash algorithms.

    It returns a distance matrix between found images.

    """
    my_file = Path(directory)
    if not my_file.is_dir():
        raise ValueError("Directory not found", directory)
    _, files = run_fast_scandir(
        directory, [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"], recurse
    )
    files_hashes: dict[str, list[np.ndarray]] = {}

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
        files_hashes[file] = img_hash.hash

    hashes_distance: dict[str, dict[str, float]] = {}
    for sh1, hashes in files_hashes.items():
        for sh2, hashes2 in files_hashes.items():
            # diagonalisation of matrix
            if sh2 in hashes_distance:
                continue
            if sh1 not in hashes_distance:
                hashes_distance[sh1] = {}
            if sh1 == sh2:
                hashes_distance[sh1][sh2] = 0.0
            else:
                hashes_distance[sh1][sh2] = ImagePHash.min_hash_distance(
                    hashes, hashes2, verbose=False
                )
    matrix_to_csv(hashes_distance)


app = typer.Typer()
app.command()(simg_cli)


if __name__ == "__main__":
    app()
