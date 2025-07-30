#!/usr/bin/python

"""Image Hash Command-line tool."""
import os
from pathlib import Path
import cv2
import numpy as np
import pytest
from imgphash.image_phash import ImagePHash


@pytest.fixture
def make_images():
    if not os.path.exists("./tests/datas"):
        os.makedirs("./tests/datas")
    if not os.path.exists("./tests/datas/2"):
        os.makedirs("./tests/datas/2")
    newImage = np.zeros((768, 768, 3), np.uint8)
    cv2.imwrite(
        "./tests/datas/imageBlack.png",
        newImage,
        [cv2.IMWRITE_PNG_COMPRESSION, 0],
    )
    if not Path("./tests/datas/imageBlack.png").is_file():
        cv2.imwrite(
            "./tests/datas/imageBlack.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
    if not Path("./tests/datas/imageRedBlue.png").is_file():
        # blue channel
        newImage[0 : 768 // 2, :, 0] = 255
        newImage[768 // 2 : 768, :, 0] = 0
        # green channel
        newImage[0 : 768 // 2, :, 1] = 0
        newImage[768 // 2 : 768, :, 1] = 0
        # red images
        newImage[0 : 768 // 2, :, 2] = 0
        newImage[768 // 2 : 768, :, 2] = 255
        cv2.imwrite(
            "./tests/datas/imageRedBlue.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
    if not Path("./tests/datas/imageWhite.png").is_file():
        # blue channel
        newImage[:, :, 0] = 255
        # green channel
        newImage[:, :, 1] = 255
        # red channel
        newImage[:, :, 2] = 255
        cv2.imwrite(
            "./tests/datas/imageWhite.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )

    center_point: tuple[int, int] = (200, 200)
    radius_circle: int = 100
    color_line: tuple[int, int, int] = (0, 0, 255)
    line_thickness: int = -1
    if not Path("./tests/datas/imageWhiteCircle1.png").is_file():
        cv2.circle(
            newImage, center_point, radius_circle, color_line, line_thickness
        )
        cv2.imwrite(
            "./tests/datas/imageWhiteCircle1.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
        newImage = cv2.flip(newImage, 0)
        cv2.imwrite(
            "./tests/datas/imageWhiteCircle1fv.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
        newImage = cv2.flip(newImage, 1)
        cv2.imwrite(
            "./tests/datas/2/imageWhiteCircle1fvfh.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
        newImage = cv2.flip(newImage, 0)
        cv2.imwrite(
            "./tests/datas/imageWhiteCircle1fh.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
    if not Path("./tests/datas/imageWhiteCircle2.png").is_file():
        newImage[:, :, 0] = 255
        newImage[:, :, 1] = 255
        newImage[:, :, 2] = 255
        cv2.circle(newImage, center_point, 150, color_line, line_thickness)
        cv2.imwrite(
            "./tests/datas/imageWhiteCircle2.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
    if not Path("./tests/datas/imageWhiteCircle3.png").is_file():
        newImage[:, :, 0] = 255
        newImage[:, :, 1] = 255
        newImage[:, :, 2] = 255
        cv2.circle(newImage, center_point, 150, color_line, 10)
        cv2.imwrite(
            "./tests/datas/imageWhiteCircle3.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
    if not Path("./tests/datas/imageBlackCircle1.png").is_file():
        newImage[:, :, 0] = 0
        newImage[:, :, 1] = 0
        newImage[:, :, 2] = 0
        cv2.circle(
            newImage, (400, 300), radius_circle, color_line, line_thickness
        )
        cv2.imwrite(
            "./tests/datas/imageBlackCircle1.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
    if not Path("./tests/datas/imageBlackRectangle1.png").is_file():
        newImage[:, :, 0] = 0
        newImage[:, :, 1] = 0
        newImage[:, :, 2] = 0
        cv2.rectangle(
            newImage, (300, 200), (500, 400), color=(255, 0, 0), thickness=10
        )
        cv2.imwrite(
            "./tests/datas/imageBlackRectangle1.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
    if not Path("./tests/datas/imageBlackRectangle2.png").is_file():
        newImage[:, :, 0] = 0
        newImage[:, :, 1] = 0
        newImage[:, :, 2] = 0
        cv2.rectangle(
            newImage, (300, 200), (500, 400), color=(255, 0, 0), thickness=-1
        )
        cv2.imwrite(
            "./tests/datas/imageBlackRectangle2.png",
            newImage,
            [cv2.IMWRITE_PNG_COMPRESSION, 0],
        )
    return True


def test_toStr(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="pHash",
        flip_v=False,
        flip_h=False,
    )
    assert str(img_hash) == "./tests/datas/imageBlackRectangle2.png(pHash)"


def test_bad_mode(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="sdfdsfsdf",
        flip_v=False,
        flip_h=False,
    )
    with pytest.raises(Exception):
        f_hash = img_hash.image_hash_file()
        assert ImagePHash.hash_to_str(f_hash) == "11067990150089382910"


def test_bad_filename(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="/tmp/dataNotFound.png",
        mode="pHash",
        flip_v=False,
        flip_h=False,
    )
    with pytest.raises(Exception):
        f_hash = img_hash.image_hash_file()
        assert ImagePHash.hash_to_str(f_hash) == "11067990150089382910"


def test_pHash(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="pHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "11067990150089382910"
    assert (
        ImagePHash.hash_to_str(
            ImagePHash.str_to_hash(ImagePHash.hash_to_str(f_hash), "pHash")
        )
        == "11067990150089382910"
    )
    with pytest.raises(Exception):
        assert (
            ImagePHash.hash_to_str(
                ImagePHash.str_to_hash(ImagePHash.hash_to_str(f_hash), "TEST")
            )
            == "11067990150089382910"
        )

    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle1.png",
        mode="pHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "8319147471542838937"
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackCircle1.png",
        mode="pHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "11067990150089382374"
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlack.png",
        mode="pHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "0"
    img_hash = ImagePHash(
        filename="./tests/datas/imageWhite.png",
        mode="pHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "0"
    img_hash = ImagePHash(
        filename="./tests/datas/imageWhiteCircle1.png",
        mode="pHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "4340418648956181752"


def test_averageHash(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="averageHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "26491358281728"
    assert (
        ImagePHash.hash_to_str(
            ImagePHash.str_to_hash(
                ImagePHash.hash_to_str(f_hash), "averageHash"
            )
        )
        == "26491358281728"
    )


def test_blockMeanHash(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="blockMeanHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert (
        ImagePHash.hash_to_str(f_hash)
        == "4708568615394428010519620309870212934089941258315990302720"
    )
    assert (
        ImagePHash.hash_to_str(
            ImagePHash.str_to_hash(
                ImagePHash.hash_to_str(f_hash), "blockMeanHash"
            )
        )
        == "4708568615394428010519620309870212934089941258315990302720"
    )


def test_marrHildrethHash(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="marrHildrethHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert (
        ImagePHash.hash_to_str(f_hash)
        == "25482809819799752521272967904782465118405599539750524436738731381942189100914021150153166941243469212048728742286905172028806218439071928825474226728864603222210835837455951"
        or ImagePHash.hash_to_str(f_hash)
        == "150270835317669957762723653744460230143878919778699801513548337344892614900664649703115090262454622976337584590297974955283386254333524992123949586010279903474896900699701552"
    )
    assert (
        ImagePHash.hash_to_str(
            ImagePHash.str_to_hash(
                ImagePHash.hash_to_str(f_hash), "marrHildrethHash"
            )
        )
        == "25482809819799752521272967904782465118405599539750524436738731381942189100914021150153166941243469212048728742286905172028806218439071928825474226728864603222210835837455951"
        or ImagePHash.hash_to_str(
            ImagePHash.str_to_hash(
                ImagePHash.hash_to_str(f_hash), "marrHildrethHash"
            )
        )
        == "150270835317669957762723653744460230143878919778699801513548337344892614900664649703115090262454622976337584590297974955283386254333524992123949586010279903474896900699701552"
    )


def test_radialVarianceHash(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="radialVarianceHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert (
        ImagePHash.hash_to_str(f_hash)
        == "701098954365952339631195776418226034447310628990253611246130361972980936340383745096279972337493"
    )
    assert (
        ImagePHash.hash_to_str(
            ImagePHash.str_to_hash(
                ImagePHash.hash_to_str(f_hash), "radialVarianceHash"
            )
        )
        == "701098954365952339631195776418226034447310628990253611246130361972980936340383745096279972337493"
    )


def test_colorMomentHash(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="colorMomentHash",
        flip_v=False,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert (
        ImagePHash.hash_to_str(f_hash)
        == "20022558097416197357142269234771802705946225291146232497241770230660849506924986917791492459958055675893195011818104653717565431437649375187263170404774220901633534769349442160666321938577675689520828274390767765326457783021192785244043886215835318110716985098107829734864257266869443093758574436161166574847903164543307246799779062712216571103444626767987453813663436424148736705081494968276986531563948306884435734721233362387083457715563285871604675244273972519648273108409513662517244957751504246025626190955471276737309231802943046960796257414511296087096501511806649924251906898877691922923870376211237069019863992166855215469714073263635456671464083768518372830592846258199670511832674718852800403528211847323385445311615643167559257461588360279316824542120218851399918099751715239767405386223288773177"
        or "66574847906290472275097079330810033531430058235059661718187756560411474872672123142300706088030362495065935660709175031062566584888342571445611915336822260400194420050946504083648334869518964491887202131729618798219392531367010120327168441734087775458093671610225425888586681671319734590429343766088356090356461899440459787391240333226541499249128699886657759728493147612986366681057310316999967200524288328429610461229428541273417028415995728871303561707701620739073027577034718631205508391243550110388513337"
        or ImagePHash.hash_to_str(f_hash)
        == "20022558097416197357142269234771802705946225291146232497241770230660849506924986917791492459958055675893195011818104653717565431437649375187263170404774220901633534769349442160666321938577675689520828274390767765326457783021192785244043886215835318110716985098107829734864257266869443093758574436161166574847906290472275097079330810033531430058235059661718187756560411474872672123142300706088030362495065935660709175031062566584888342571445611915336822260400194420050946504083648334869518964491887202131729618798219392531367010120327168441734087775458093671610225425888586681671319734590429343766088356090356461899440459787391240333226541499249128699886657759728493147612986366681057310316999967200524288328429610461229428541273417028415995728871303561707701620739073027577034718631205508391243550110388513337"
        or "66574847906290472275097079330810033531430058235059661718187756560411474872672123142300706088030362495065935660709175031062566584888342571445611915336822260400194420050946504083648334869518964491887202131729618798219392531367010120327168441734087775458093671610225425888586681671319734590429343766088356090356461899440459787391240333226541499249128699886657759728493147612986366681057310316999967200524288328429610461229428541273417028415995728871303561707701620739073027577034718631205508391243550110388513337"
    )
    with pytest.raises(Exception):
        ImagePHash.hash_to_str(
            ImagePHash.str_to_hash(
                ImagePHash.hash_to_str(f_hash), "colorMomentHash"
            )
        )


def test_flip_v(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="pHash",
        flip_v=True,
        flip_h=False,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "11067990150089382910"
    assert len(img_hash.hash) == 2
    assert ImagePHash.hash_to_str(img_hash.hash[1]) == "11053635145317129211"


def test_flip_h(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="pHash",
        flip_v=False,
        flip_h=True,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "11067990150089382910"
    assert len(img_hash.hash) == 2
    assert ImagePHash.hash_to_str(img_hash.hash[1]) == "3689517699298472958"


def test_flip_v_h(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="pHash",
        flip_v=True,
        flip_h=True,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "11067990150089382910"
    assert len(img_hash.hash) == 4
    assert ImagePHash.hash_to_str(img_hash.hash[1]) == "11053635145317129211"
    assert ImagePHash.hash_to_str(img_hash.hash[2]) == "3732582713615234043"
    assert ImagePHash.hash_to_str(img_hash.hash[3]) == "3689517699298472958"


def test_distance(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="pHash",
        flip_v=True,
        flip_h=True,
    )
    f_hash = img_hash.image_hash_file()
    assert ImagePHash.hash_to_str(f_hash) == "11067990150089382910"
    assert len(img_hash.hash) == 4
    assert (
        ImagePHash.hamming_distance_v3(img_hash.hash[0], img_hash.hash[1])
        == 26
    )
    assert (
        ImagePHash.hamming_distance_v2(img_hash.hash[0], img_hash.hash[2])
        == 27
    )
    assert (
        ImagePHash.hamming_distance(img_hash.hash[0], img_hash.hash[3]) == 25.0
    )
    assert (
        ImagePHash.hamming_distance_v2(img_hash.hash[1], img_hash.hash[0])
        == 26
    )
    assert (
        ImagePHash.hamming_distance_v3(img_hash.hash[1], img_hash.hash[2])
        == 25
    )
    assert (
        ImagePHash.hamming_distance(img_hash.hash[1], img_hash.hash[3]) == 27.0
    )


def test_min_distance(make_images):
    assert make_images == True
    img_hash = ImagePHash(
        filename="./tests/datas/imageBlackRectangle2.png",
        mode="pHash",
        flip_v=True,
        flip_h=True,
    )
    img_hash.image_hash_file()
    img_hash2 = ImagePHash(
        filename="./tests/datas/imageBlackRectangle1.png",
        mode="pHash",
        flip_v=True,
        flip_h=True,
    )
    img_hash2.image_hash_file()
    assert (
        ImagePHash.min_hash_distance(
            img_hash.hash, img_hash2.hash, verbose=True
        )
        == 18.0
    )
