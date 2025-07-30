"""Image Hash Command-line tool."""

from pathlib import Path
from typing import List
import cv2
import numpy as np


class ImagePHash:  # pylint: disable=too-many-instance-attributes
    """ImagePHash Class."""

    def __init__(self, filename: str, mode: str, flip_v: bool, flip_h: bool):
        """__init__."""
        self.filename = filename
        self.mode = mode
        self.hash: List[np.ndarray] = []
        self.flip_h = flip_h
        self.flip_v = flip_v

        # parameters for some hash functions
        self.block_mean_hash_mode = 0
        self.marr_hildreth_hash_alpha = 2.0
        self.marr_hildreth_hash_scale = 1.0
        self.radial_variance_hash_sigma = 1.0
        self.radial_variance_hash_num_of_angle_line = 180

    def __str__(self) -> str:
        """__str__."""
        return f"{self.filename}({self.mode})"

    def compute_hash(self, img: np.array) -> np.array:  # type: ignore # noqa: MC0001
        # pylint: disable=too-many-arguments,too-many-locals
        # pylint: disable=too-many-return-statements
        """compute_hash."""
        if self.mode == "pHash":
            try:
                return cv2.img_hash.pHash(img)
            except:  # pylint: disable=bare-except
                return cv2.img_hash.pHash(np.zeros((256, 256, 3), np.uint8))
        if self.mode == "averageHash":
            try:
                return cv2.img_hash.averageHash(img)
            except:  # pylint: disable=bare-except
                return cv2.img_hash.pHash(np.zeros((256, 256, 3), np.uint8))
        if self.mode == "blockMeanHash":
            # return cv2.img_hash.blockMeanHash(img)
            try:
                return cv2.img_hash.blockMeanHash(
                    img, mode=self.block_mean_hash_mode
                )
            except:  # pylint: disable=bare-except
                return cv2.img_hash.pHash(np.zeros((256, 256, 3), np.uint8))
        if self.mode == "marrHildrethHash":
            # return cv2.img_hash.marrHildrethHash(img)
            try:
                return cv2.img_hash.marrHildrethHash(
                    img,
                    alpha=self.marr_hildreth_hash_alpha,
                    scale=self.marr_hildreth_hash_scale,
                )
            except:  # pylint: disable=bare-except
                return cv2.img_hash.pHash(np.zeros((256, 256, 3), np.uint8))
        if self.mode == "radialVarianceHash":
            # return cv2.img_hash.radialVarianceHash(img)
            try:
                return cv2.img_hash.radialVarianceHash(
                    img,
                    sigma=self.radial_variance_hash_sigma,
                    numOfAngleLine=self.radial_variance_hash_num_of_angle_line,
                )
            except:  # pylint: disable=bare-except
                return cv2.img_hash.pHash(np.zeros((256, 256, 3), np.uint8))
        if self.mode == "colorMomentHash":
            try:
                return cv2.img_hash.colorMomentHash(img)
            except:  # pylint: disable=bare-except
                return cv2.img_hash.pHash(np.zeros((256, 256, 3), np.uint8))
        raise ValueError("Hash mode not found", self.mode)

    def image_hash_file(self) -> np.ndarray:
        """img-phash-tools from filename."""
        my_file = Path(self.filename)
        if not my_file.is_file():
            raise ValueError("Filename not found", self.filename)
        img = cv2.imread(self.filename)
        if img is None:  # in case of error, we use a blank image
            img = np.zeros((256, 256, 3), np.uint8)
        h = self.compute_hash(img)
        self.hash.append(
            h[0]  # type: ignore # pylint: disable=unsubscriptable-object
        )
        if self.flip_v:
            img = cv2.flip(img, 0)
            h = self.compute_hash(img)
            self.hash.append(
                h[0]  # type: ignore # pylint: disable=unsubscriptable-object
            )
        if self.flip_h:
            img = cv2.flip(img, 1)
            h = self.compute_hash(img)
            self.hash.append(
                h[0]  # type: ignore # pylint: disable=unsubscriptable-object
            )
        if self.flip_v and self.flip_h:
            img = cv2.flip(img, 0)
            h = self.compute_hash(img)
            self.hash.append(
                h[0]  # type: ignore # pylint: disable=unsubscriptable-object
            )
        return self.hash[0]

    @staticmethod
    def hash_to_str(f_hash: np.ndarray) -> str:
        """hash_to_str."""
        return str(
            int.from_bytes(f_hash.tobytes(), byteorder="big", signed=False)
        )

    @staticmethod
    def str_to_hash(f_hash: str, mode: str) -> np.ndarray:
        """str_to_hash."""
        cnt = 8
        if mode == "pHash":
            cnt = 8
        elif mode == "averageHash":
            cnt = 8
        elif mode == "blockMeanHash":
            cnt = 32
        elif mode == "marrHildrethHash":
            cnt = 72
        elif mode == "radialVarianceHash":
            cnt = 40
        elif mode == "colorMomentHash":
            # return np.frombuffer(int(f_hash).to_bytes(42,
            # "big", signed=False), dtype=np.float64)
            # return np.frombuffer(float(f_hash).to_bytes(
            # 42, "big", signed=False), dtype=np.float64)
            # Not yet implemented
            raise ValueError("Hash mode not yet implemented", mode)
        else:
            raise ValueError("Hash mode not known", mode)
        return np.frombuffer(
            int(f_hash).to_bytes(cnt, "big", signed=False), dtype=np.uint8
        )

    @staticmethod
    def min_hash_distance(
        a: List[np.ndarray], b: List[np.ndarray], verbose: bool = False
    ) -> float:
        """min_hash_distance."""
        min_dist = -1.0
        for _, h1 in enumerate(a):
            for _, h2 in enumerate(b):
                dist = ImagePHash.hamming_distance(h1, h2)
                if min_dist == -1.0:
                    min_dist = dist
                min_dist = min(dist, min_dist)
                if verbose:
                    print(str(dist) + ";", end="")
        if verbose:
            print("")
            print(str(min_dist) + ";")
        return min_dist

    @staticmethod
    def hamming_distance_v3(a: np.ndarray, b: np.ndarray) -> int:
        """hamming_distance_v3."""
        r = (1 << np.arange(8))[:, None]
        return int(np.count_nonzero((a & r) != (b & r)))

    @staticmethod
    def hamming_distance_v2(a: np.ndarray, b: np.ndarray) -> int:
        """hamming_distance_v2."""
        r = (1 << np.arange(8))[:, None]
        return int(np.count_nonzero((np.bitwise_xor(a, b) & r) != 0))

    @staticmethod
    def hamming_distance(a: np.ndarray, b: np.ndarray) -> float:
        """hamming_distance."""
        return float(str(cv2.norm(a, b, normType=cv2.NORM_HAMMING)))
        # return float(str(cv2.norm(a, b, normType=cv2.NORM_HAMMING2)))
