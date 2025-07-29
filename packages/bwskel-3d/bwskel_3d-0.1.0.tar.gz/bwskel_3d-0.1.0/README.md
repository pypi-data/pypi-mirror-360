# 📦 BWSkeleton3D
# Overview
BWSkeleton3D is a Python implementation that closely replicates the functionality of MATLAB's bwskel function for 3D binary volumes.

It provides:

* 3D skeletonization of binary volumes,

* Optional pruning of skeleton branches by minimum branch length,

* Input validation to ensure proper data format.

Installation
Install dependencies via:

```bash
pip install numpy scipy scikit-image
```

# Usage
``` python
from bwskel import BWSkeleton3D
import numpy as np

# Create a sample 3D binary volume
volume = np.zeros((20, 20, 20), dtype=bool)
volume[5:15, 10, 10] = True

# Initialize and compute skeleton
skel = BWSkeleton3D(volume, min_branch_length=3)
skeleton = skel.compute_skeleton()
```

# Class: BWSkeleton3D
`__init__(input_volume, min_branch_length=0)`

* `input_volume`: 3D boolean NumPy array representing the binary volume.

* `min_branch_length`: Minimum branch length for pruning (default 0 means no pruning).

`compute_skeleton()`
Computes and optionally prunes the skeleton of the input volume. Returns a 3D boolean array.

# Requirements

* Python 3.7+
* numpy
* scipy
* scikit-image

# Author
Yunze Du - University of Toronto