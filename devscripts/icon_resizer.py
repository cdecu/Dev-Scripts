#!/usr/bin/python

# The MIT License (MIT)
#
# Copyright (c) 2016 Markus Paeschke
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
# Android Icon Resizer

Small python script to convert a single input image to all necessary Android drawables sizes.

Written and tested in python 2.7


# Installation

At first you have to install PIL.
On linux there are several ways to do this.
I recommend to use pip for that:
$ pip install PIL

Eventually you have to sudo it:
$ sudo pip install PIL

After that you are ready to use the script.

# Usage

print the help with:
$ python android_icon_resizer.py -h

simplest usage:
$ python android_icon_resizer.py -i /path/to/your/file.png -o /destination/folder/

with playstore folder:
$ python android_icon_resizer.py -i /path/to/your/file.png -o /destination/folder/ -p

use relative sizes based on given mdpi size in px:
$ python android_icon_resizer.py -i /path/to/your/file.png -o /destination/folder/ -s 190

or simply use the longest side of the image as target size
$ python android_icon_resizer.py -i /path/to/your/file.png -o /destination/folder/ -s 0

combine it with playstore file you will realize, that the playstore file will always be 512px because thats the default size in the playstore
$ python android_icon_resizer.py -i /path/to/your/file.png -o /destination/folder/ -s 0 -p
"""

import os
import PIL
import re
import argparse
from PIL import Image
from os.path import basename

__version__ = '1.1.0'
__author__ = 'Markus Paeschke'
__email__ = "markus.paeschke@gmail.com"
__license__ = 'The MIT License (MIT)'
__copyright__ = 'Copyright 2016 Markus Paeschke'

RESOLUTION_TYPES = ('ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi',)
RESOLUTION_SIZES = {
    'ldpi': 36,
    'mdpi': 48,
    'hdpi': 72,
    'xhdpi': 96,
    'xxhdpi': 144,
    'xxxhdpi': 192,
}
RELATIVE_SIZES = {
    'ldpi': .75,
    'mdpi': 1.0,
    'hdpi': 1.5,
    'xhdpi': 2.0,
    'xxhdpi': 3.0,
    'xxxhdpi': 4.0,
}
PLAYSTORE_SIZE = 512
DRAWABLE_FOLDER_PATH = 'res/drawable-%s'
PLAYSTORE_FOLDER_PATH = 'res/playstore'


class AndroidIconResizer(object):
    def __init__(self, output_folder):
        self.output_folder = output_folder


    def create_directories(self):
        """
        Create directories for all resolution types
        """
        for resolution_type in RESOLUTION_TYPES:
            try:
                path = os.path.join(self.output_folder, DRAWABLE_FOLDER_PATH % resolution_type)
                os.makedirs(path, 0755)
            except OSError:
                pass

    def create_playstore_directory(self):
        try:
            path = os.path.join(self.output_folder, PLAYSTORE_FOLDER_PATH)
            os.makedirs(path, 0755)
        except OSError:
            pass

    def normalize_file_name(self, file_name):
        """
        Normalize the file name to fit android specification
        """
        return re.sub("@[0-9]+x", "", file_name).replace('-', '_')

    def get_width_height(self, width, height, target_size):
        """
        Returns the new width and hight regarding a target size
        """
        if width > height:
            new_width = target_size
            wpercent = (target_size / float(width))
            new_height = int((float(height) * float(wpercent)))
        else:
            new_height = target_size
            wpercent = (target_size / float(height))
            new_width = int((float(width) * float(wpercent)))
        return (new_width, new_height)

    def resize(self, file_path, desired_size_mdpi=0, with_playstore=False):
        """
        Resizes the images
        """
        self.create_directories()
        file_name = basename(file_path)
        image = Image.open(file_path)
        width, height = image.size
        desired_size_mdpi = width if width > height else height
        new_width = 0
        new_height = 0
        for resolution_type in RESOLUTION_SIZES:
            image_to_resize = image
            target_size = RESOLUTION_SIZES.get(resolution_type)
            if desired_size_mdpi > 0:
                target_size = int(desired_size_mdpi * RELATIVE_SIZES.get(resolution_type))
            new_width, new_height = self.get_width_height(width, height, target_size)
            image_to_resize = image_to_resize.resize((new_width, new_height), PIL.Image.ANTIALIAS)
            path = os.path.join(self.output_folder, DRAWABLE_FOLDER_PATH % resolution_type, self.normalize_file_name(file_name))
            image_to_resize.save(path, quality=100)
        if with_playstore:
            self.create_playstore_directory()
            image_to_resize = image
            new_width, new_height = self.get_width_height(width, height, PLAYSTORE_SIZE)
            image_to_resize = image_to_resize.resize((new_width, new_height), PIL.Image.ANTIALIAS)
            path = os.path.join(self.output_folder, PLAYSTORE_FOLDER_PATH, self.normalize_file_name(file_name))
            image_to_resize.save(path, quality=100)

def main():
    try:
        __import__('imp').find_module('PIL')
    except ImportError:
        raise ImportError('PIL not found. Please install PIL first\nfor example: pip install PIL')

    parser = argparse.ArgumentParser(description='Android Icon Resizer')
    parser.add_argument('-i','--input', help='Input file name', required=True)
    parser.add_argument('-o','--output',help='Output folder for icons', required=True)
    parser.add_argument('-s','--size', help='Changing the size based on the longest side for mdpi in px; if size is 0 the longest image size will be choosen', type=int, required=False)
    parser.add_argument('-p','--playstore', help='Creates a playstore image as well', action='store_true', required=False)
    args = parser.parse_args()
    print "Starting image resizing..."

    android_icon_resizer = AndroidIconResizer(args.output)

    android_icon_resizer.resize(args.input, args.size, args.playstore)

    print "Done..."

if __name__ == "__main__":
    main()