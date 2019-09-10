import skimage.io as io
from skimage.color import rgb2gray
from skimage import img_as_float, img_as_int
import numpy as np
from skimage.filters import gaussian
from skimage.util import invert
from skimage import exposure
from skimage import transform
from skimage.color import rgb2gray
from PIL import Image
import glob
import os
import re
import argparse
import metastring
import pandas as pd

parser = argparse.ArgumentParser(description='Combine multiple images of same section per plate into means and median averaged images.')
parser.add_argument('readdir', type=str, 
                    help='directory to read')
parser.add_argument('bgdir', type=str, help = 'location of estimated backgrounds')
parser.add_argument('outdir', type=str,help = 'output directory. Will be created if does not exist.')

args = parser.parse_args()

if(not os.path.isdir(args.readdir)):
    print("Not a valid directory")
    exit(1)

outdirs = [args.outdir]

for od in outdirs:
    if(not os.path.isdir(od)):
        try:
            os.mkdir(od)
        except:
            print("Could not create output directory: " + od)
            exit(1)


# create a list of metadata dictionaries based on filenames
# we are just using medians of sections here
dicts = []
for f in glob.glob(os.path.join(args.readdir,'*_postproc-secmedian.tif')):
    dicts.append(metastring.metastring(os.path.basename(f)))

for f in glob.glob(os.path.join(args.bgdir,'*.tif')):
    dicts.append(metastring.metastring(os.path.basename(f)))

# create a dataframe from dictionaries, used to select all images
# pertaining to a unique section, of a unique plate
df = pd.DataFrame(dicts)

# group images by unique plate
groups = df.groupby(['run','date','time','chamber','rep'])

# for every unique plate, create a mean image and a gaussian approx background
for index, group_df in groups:
    # get a list of filenames associated with the plate 
    # and turn it into a numpy stack
    secavgs = group_df.loc[df['postproc'] == "secmedian"]
    platebg = group_df.loc[df['postproc'] == "platebg"]
    files = secavgs.rstr.unique()
    path_files = [os.path.join(args.readdir,f) for f in files]
    bg_files = [os.path.join(args.bgdir,f) for f in platebg.rstr.unique()]
    ic = io.ImageCollection(path_files)
    bgimg = Image.open(bg_files[0])
    for im,fn in zip(ic,ic.files):
        print(fn)
        print(bg_files[0])
        diffimg = im/bgimg
        diffimg = exposure.rescale_intensity(diffimg,out_range='dtype')
    
        # new output name should update postproc 
        newf = re.sub(r'postproc-secmedian','postproc-devignette',os.path.basename(fn))
        # don't forget to keep exif tags, which should be identical for a section
        tags = Image.open(fn)
        # using pil, since this works with our tiffs
        io.imsave(os.path.join(args.outdir,newf),img_as_float(diffimg),plugin="pil",tiffinfo=tags.tag)
