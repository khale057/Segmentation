import os
import numpy as np 
import random
import shutil


if len(os.listdir('test_data')) > 0:
    os.system('mv ./test_data/* ./train_data/')
    os.system('mv ./test_mask/* ./train_mask/')

fs = ['vol47_recon_01400_RGB', 'vol47_recon_00584_RGB', 'vol55_recon_00936_RGB', 'vol41_recon_00535_RGB', 'vol32_recon_00204_RGB', 'vol55_recon_00611_RGB', 'vol55_recon_01704_RGB', 'vol32_recon_02105_RGB', 'vol47_recon_00047_RGB', 'vol32_recon_00535_RGB']

# Choose one as the testing image, others as training dataset
f = fs[2]

os.system('mv ./train_data/'+f+'* ./test_data/')
os.system('mv ./train_mask/'+f+'* ./test_mask/')
