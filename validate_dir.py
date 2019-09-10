import os
import glob
import argparse
import metastring

parser = argparse.ArgumentParser(description='List tif files with invalid metastring formats.')
parser.add_argument('readdir', type=str, 
                    help='directory to read')

args = parser.parse_args()

if(not os.path.isdir(args.readdir)):
    print("Not a valid directory")
    exit(1)

for f in glob.glob(os.path.join(args.readdir,'*.tif')):
    fname = os.path.basename(f)
    try:
        metastring.metastring(fname)
    except:
        print(fname+" INVALID")
        continue 
