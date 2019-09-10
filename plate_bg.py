import skimage.io as io
from skimage.color import rgb2gray
from skimage import img_as_float, img_as_int, img_as_uint
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
parser.add_argument('outdir', type=str,help = 'output directory base with "average" and "background" subdirectories. Will be created if does not exist.')

args = parser.parse_args()

if(not os.path.isdir(args.readdir)):
    print("Not a valid directory")
    exit(1)

outdirs = [args.outdir,
            os.path.join(args.outdir,"average"),
            os.path.join(args.outdir,"background")]

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

# create a dataframe from dictionaries, used to select all images
# pertaining to a unique section, of a unique plate
df = pd.DataFrame(dicts)

# group images by unique plate
groups = df.groupby(['run','date','time','chamber','rep'])

# for every unique plate, create a median image and a gaussian approx background
for index, group_df in groups:
    # get a list of filenames associated with the plate 
    # and turn it into a numpy stack
    files = group_df.rstr.unique()
    path_files = [os.path.join(args.readdir,f) for f in files]
    ic = io.ImageCollection(path_files)
    istack = np.stack(ic)
    # calculate the mean image and save
    median_img = (np.median(istack,axis=0))/(255)
    #mean_img = exposure.rescale_intensity(img_as_float(mean_img),out_range='dtype')
    #print(mean_img.dtype)
    #print(mean_img.max())
    #print(mean_img.min())
    #print(mean_img.shape)

    # new output name should remove section and update postproc 
    newf = re.sub(r'sec-\d+_','',files[0])
    newf = re.sub(r'postproc-secmedian','postproc-platemedian',newf)
    # don't forget to keep exif tags, which should be identical for a section
    tags = Image.open(path_files[0])
    # using pil, since this works with our tiffs
    io.imsave(os.path.join(args.outdir,"average",newf),img_as_float(median_img),plugin="pil",tiffinfo=tags.tag)

    # calculate the smoothed background
    smoothed = img_as_float(gaussian(median_img,sigma=150))
    newf = re.sub(r'postproc-platemedian','postproc-platebg',newf)
    io.imsave(os.path.join(args.outdir,"background",newf),img_as_float(smoothed),plugin="pil",tiffinfo=tags.tag)

    
   
