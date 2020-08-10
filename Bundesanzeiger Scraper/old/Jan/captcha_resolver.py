import pytesseract

# noinspection PyUnresolvedReferences
import sys
import argparse

try:
    import Image
except ImportError:
    from PIL import Image
from subprocess import check_output


def resolve(path):
    print("Resampling the Image")
    check_output(["C:/Program Files/ImageMagick-7.0.10-Q16-HDRI/magick.exe", path, '-resample', '600', path])
    return pytesseract.image_to_string(Image.open(path))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('path', help='Captcha file path')
    args = argparser.parse_args()
    path = args.path
    print('Resolving Captcha')
    captcha_text = resolve(path)
    print('Extracted Text', captcha_text)
