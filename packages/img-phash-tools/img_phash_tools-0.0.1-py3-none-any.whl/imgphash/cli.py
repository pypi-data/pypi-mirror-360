"""Image Hash Command-line tool."""

import typer
from typing_extensions import Annotated
from imgphash.image_phash import ImagePHash


def imgphash_cli(  # pylint: disable=too-many-arguments,too-many-locals
    filename: Annotated[
        str,
        typer.Argument(help="The file name."),
    ] = ".",
    *,
    mode: Annotated[
        str,
        typer.Option(
            help="The hash mode : [averageHash, blockMeanHash, "
            "colorMomentHash, marrHildrethHash, pHash, radialVarianceHash]."
        ),
    ] = "pHash",
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
    verbose: Annotated[
        bool,
        typer.Option(help="Print more informations"),
    ] = False,
    compare: Annotated[
        str,
        typer.Option(
            help="Compare to an other image filename and return distance."
        ),
    ] = "",
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
    Use to print the perceptual hash of an image.

    See https://www.phash.org or

    https://www.phash.org/docs/pubs/thesis_zauner.pdf

    for more informations on the algorithms.

    It return the hashes into an integer, you can use hamming
    distance on his bits to find similar images.

    With --compare option, it will return the hamming distance
    between the two images.
    """
    img_hash = ImagePHash(
        filename=filename, mode=mode, flip_v=flip_v, flip_h=flip_h
    )
    img_hash.block_mean_hash_mode = block_mean_hash_mode
    img_hash.marr_hildreth_hash_scale = marr_hildreth_hash_scale
    img_hash.marr_hildreth_hash_alpha = marr_hildreth_hash_alpha
    img_hash.radial_variance_hash_num_of_angle_line = (
        radial_variance_hash_num_of_angle_line
    )
    img_hash.radial_variance_hash_sigma = radial_variance_hash_sigma
    f_hash = img_hash.image_hash_file()
    if not compare or verbose:
        print(ImagePHash.hash_to_str(f_hash) + ";", end="")
        for i in range(1, len(img_hash.hash)):
            print(ImagePHash.hash_to_str(img_hash.hash[i]) + ";", end="")
        print(mode + ";")
    if compare != "":
        img_hash2 = ImagePHash(
            filename=compare, mode=mode, flip_v=flip_v, flip_h=flip_h
        )
        img_hash2.block_mean_hash_mode = block_mean_hash_mode
        img_hash2.marr_hildreth_hash_scale = marr_hildreth_hash_scale
        img_hash2.marr_hildreth_hash_alpha = marr_hildreth_hash_alpha
        img_hash2.radial_variance_hash_num_of_angle_line = (
            radial_variance_hash_num_of_angle_line
        )
        img_hash2.radial_variance_hash_sigma = radial_variance_hash_sigma
        f_hash2 = img_hash2.image_hash_file()
        if verbose:
            print(ImagePHash.hash_to_str(f_hash2) + ";", end="")
            for j in range(1, len(img_hash2.hash)):
                print(ImagePHash.hash_to_str(img_hash2.hash[j]) + ";", end="")
            print(mode + ";")

        dist = ImagePHash.min_hash_distance(
            img_hash.hash, img_hash2.hash, verbose=verbose
        )
        if not verbose:
            print(str(dist) + ";")


app = typer.Typer()
app.command()(imgphash_cli)


if __name__ == "__main__":
    app()
