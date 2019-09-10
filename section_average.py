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

parser = argparse.ArgumentParser(description='Combine multiple images of same section per plate into median averaged images.')
parser.add_argument('readdir', type=str, 
                    help='directory to read')
parser.add_argument('outdir', type=str,help = 'output directory. Will be created if does not exist.')

args = parser.parse_args()

if(not os.path.isdir(args.readdir)):
    print("Not a valid directory")
    exit(1)

if(not os.path.isdir(args.outdir)):
    try:
        os.mkdir(args.outdir)
    except:
        print("Could not create output directory: " + args.outdir)
        exit(1)

# create a list of metadata dictionaries based on filenames
dicts = []
for f in glob.glob(os.path.join(args.readdir,'*.tif')):
    #print(f)
    #print(os.path.basename(f))
    dicts.append(metastring.metastring(os.path.basename(f)))

# create a dataframe from dictionaires, used to select all images
# pertaining to a unique section, of a unique plate
df = pd.DataFrame(dicts)

# group images by unique section
groups = df.groupby(['run','date','time','chamber','rep','sec'])

# for every unique section, create a median and mean image
for index, group_df in groups:
    # get a list of filenames associated with the section 
    # and turn it into a numpy stack
    files = group_df.rstr.unique()
    path_files = [os.path.join(args.readdir,f) for f in files]
    ic = io.ImageCollection(path_files)
    istack = np.stack(ic)
    
    # calculate the mean image and save
#    mean_img = np.mean(istack,axis=0)
#    mean_img = mean_img/255#exposure.rescale_intensity(img_as_float(mean_img),out_range='dtype')
    
    # new output name should replace num-0000 with postrpoc-proc
#    newf = re.sub(r'num-\d+','postproc-secmean',files[0])
    # don't forget to keep exif tags, which should be identical for a section
#    tags = Image.open(path_files[0])
    # using pil, since this works with our tiffs
#    io.imsave(os.path.join(args.outdir,newf),mean_img,plugin="pil",tiffinfo=tags.tag)
    
    # calculate median image and save, as we did with mean
    median_img = np.median(istack,axis=0)
    median_img = median_img/255#exposure.rescale_intensity(img_as_float(median_img),out_range='dtype')
    newf = re.sub(r'num-\d+','postproc-secmedian',files[0])
    tags = Image.open(path_files[0])
    io.imsave(os.path.join(args.outdir,newf),median_img,plugin="pil",tiffinfo=tags.tag)
