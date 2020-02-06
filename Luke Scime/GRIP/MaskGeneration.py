# Author: Luke Scime
# Date: 2019-01-17
# Purpose: generates masks used by GRIP for the sync fiducial
#------------------------------------------------------------------------------

# Import libraries
from IPython import get_ipython; # needed to run magic commands
ipython = get_ipython(); # needed to run magic commands
import cv2;
import numpy as np;
import matplotlib.pyplot as plt;

# Change Environment settings
ipython.magic('matplotlib qt'); # display figures in a separate window

#------------------------------------------------------------------------------

# Load the reference image
path_ref = 'mask_ref.jpg';
I = cv2.imread(path_ref);

# Show the reference image
plt.figure('ref image');
plt.imshow(I);

# Generate the small mask
rowa = 0;
rowb = 1;
cola = 0;
colb = 1;
I_smallmask = I[rowa:rowb,cola:colb,:] = 0;
plt.figure('I_smallmask');
plt.imshow(I_smallmask);





