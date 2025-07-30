"""Image Hash Command-line tool."""

import os
from pathlib import Path
from typing import Tuple

import typer
from typing_extensions import Annotated
from imgphash.image_phash import ImagePHash


def run_fast_scandir(
    directory: str, ext: list[str], recurse: bool = True
) -> Tuple[list[str], list[str]]:
    """run_fast_scandir."""
    subfolders: list[str] = []
    files: list[str] = []
    for f in os.scandir(directory):
        if recurse:
            if f.is_dir():
                subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)
    if recurse:
        for directory2 in list(subfolders):
            sf, fi = run_fast_scandir(directory2, ext)
            subfolders.extend(sf)
            files.extend(fi)
    return subfolders, files


def dupimg_cli(  # pylint: disable=too-many-arguments,too-many-locals
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
    Find duplicates images with perceptual hash algorithms.

    It returns a list of filenames separated by a ';'

    On the same line, the files are similar.

    On other lines, there is other duplicate files.

    """
    my_file = Path(directory)
    if not my_file.is_dir():
        raise ValueError("Directory not found", directory)
    _, files = run_fast_scandir(
        directory, [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"], recurse
    )
    files_hash: dict[str, dict[str, bool]] = {}
    duplicates: dict[str, dict[str, bool]] = {}
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
        for _, f_hash in enumerate(img_hash.hash):
            str_hash = ImagePHash.hash_to_str(f_hash)
            if str_hash in files_hash:
                if file not in files_hash[str_hash]:
                    files_hash[str_hash].update({file: True})
                    duplicates[str_hash] = files_hash[str_hash]
            else:
                files_hash[str_hash] = {file: True}
    # This list is used when there where flipped images,
    # two hashes will give the same list, and we don't print it
    printed: dict[str, bool] = {}
    for _, k in duplicates.items():
        prt = ""
        for file, _ in k.items():
            prt = prt + file + ";"
        if prt not in printed:
            print(prt)
            printed.update({prt: True})


app = typer.Typer()
app.command()(dupimg_cli)


if __name__ == "__main__":
    app()
