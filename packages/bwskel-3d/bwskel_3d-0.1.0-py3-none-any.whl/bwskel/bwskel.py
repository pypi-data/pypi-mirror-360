import numpy as np
from prune_edges3 import prune_edges3
from skimage.morphology import skeletonize


class BWSkeleton3D:
    def __init__(self, input_volume, min_branch_length=0):
        """
        Initialize the BWSkeleton object.

        Parameters:
        - input_volume: 3D boolean NumPy array representing the binary volume.
        - min_branch_length: Minimum allowed branch length for pruning (default is 0, meaning no pruning).
        """
        self.input_volume = input_volume
        self.min_branch_length = min_branch_length
        self._validate_inputs()  # Validate the provided inputs.


    def _validate_inputs(self):
        """
        Ensure that the input volume is valid: a 3D boolean NumPy array.
        Also check that min_branch_length is a non-negative integer.
        """
        if not isinstance(self.input_volume, np.ndarray) or not self.input_volume.dtype == bool:
            raise ValueError('Input must be a 3D logical (boolean) NumPy array.')

        if self.input_volume.ndim != 3:
            raise ValueError('Input volume must be a 3D array.')

        if not isinstance(self.min_branch_length, int) or self.min_branch_length < 0:
            raise ValueError('MinBranchLength must be a non-negative integer.')


    def compute_skeleton(self):
        """
        Compute the skeleton of the input volume and optionally prune small branches.

        Returns:
        - Skeletonized and optionally pruned binary volume.
        """
        padded_img = np.pad(self.input_volume, pad_width=1, mode='constant', constant_values=0)

        if self.input_volume.ndim == 3:
            # If 3D, use 3D skeletonization
            skel = skeletonize(padded_img, method='lee')
        else:
            raise ValueError("Input must be a 2D or 3D binary image")
            
        # Optional pruning: remove branches shorter than min_branch_length
        if self.min_branch_length > 0:
            skel = prune_edges3(skel, self.min_branch_length)

        # Unpad the skeletonized image to return to original size
        skel = skel[1:-1, 1:-1, 1:-1]

        return skel