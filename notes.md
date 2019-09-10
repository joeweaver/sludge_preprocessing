# Personal notes for running scripts manually
Includes hints about data locations

## Validating
1. Run validate_dir on dir containing raw images
1a. In general, image dir is a symlink in ./data which goes to temporary image dir on local machine
2. Fix any invalid filenames
2a. Can rename bad files with zmv

## Image processing
4. get section averages section_average.py
4a. often sent to output/sec_averages
5. get backgrounds using plate_bg.py
5a. creates both medians and blurred
5b. usually output/plate_backgrounds
6. devignette using plate_devignette.py
6a. devignette.py output/sec_averages output/plate_backgrounds/background output/final
7. working machine needs only final images (Plates * Sections)

# Cleanup
1. Move intermediate images to long-term storage (see data locations section)
2. Retain final devignetted images on analysis computer

# Data locations
Raw initial images (i.e. all single captures of each section of each plate before time averaging) are on:
* external HDD - long-term
* imaging computer - short-term

Intermediate images (median average, background, etc)
* external HDD - long-term
* processing computer - short-term
* published 
  
Final images (devignetted, median averaged, i.e. 1 for each day-chamber-plate-sec)
* external HDD - long term
* analysis computer - long-term (at least project lifetime)
* published 

# Automation
```proc_images.sh ``` should be able to, when pointed at a subdirectory full of raw images, create final images

A counterpart bat file should be written for Win10 #TODO

A script to copy intermediate/original images to long-term HDD and then delete from local machine should be written.  #TODO

