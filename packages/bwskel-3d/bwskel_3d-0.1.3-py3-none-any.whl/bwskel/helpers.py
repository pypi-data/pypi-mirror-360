import numpy as np


def pk_get_nh_idx(img, indices):
    width, height, depth = img.shape
    x, y, z = np.unravel_index(indices, (width, height, depth), order='F')

    nhood = np.zeros((len(indices), 27), dtype=int)
    count = 0

    for xx in range(3):
        for yy in range(3):
            for zz in range(3):

                n_x = x + (xx - 1)
                n_y = y + (yy - 1)
                n_z = z + (zz - 1)

                # Mask: Valid neighbor positions
                valid = (
                    (n_x >= 0) & (n_x < width) &
                    (n_y >= 0) & (n_y < height) &
                    (n_z >= 0) & (n_z < depth)
                )

                # Compute valid linear indices in MATLAB's column-major order
                linear_indices = np.zeros_like(n_x)
                linear_indices[valid] = np.ravel_multi_index(
                    (n_x[valid], n_y[valid], n_z[valid]),
                    (width, height, depth),
                    order='F'
                )

                nhood[:, count] = linear_indices
                count += 1

    return nhood




def pk_get_nh(img, indices):
    width, height, depth = img.shape
    x, y, z = np.unravel_index(indices, (width, height, depth), order='F')

    nhood = np.zeros((len(indices), 27), dtype=bool)
    count = 0

    for xx in range(3):
        for yy in range(3):
            for zz in range(3):

                n_x = x + (xx - 1)
                n_y = y + (yy - 1)
                n_z = z + (zz - 1)

                # Out-of-bounds check
                valid = (
                    (n_x >= 0) & (n_x < width) &
                    (n_y >= 0) & (n_y < height) &
                    (n_z >= 0) & (n_z < depth)
                )

                nhood[valid, count] = img[n_x[valid], n_y[valid], n_z[valid]]
                count += 1

    return nhood



def pk_follow_link(skel_label, node, k, j, idx, cans, c2n):
    vox = []
    n_idx = None
    ep = 0
    vox.append(node[k]['idx'][j])
    isdone = False

    while not isdone:
        next_cand = c2n[idx]
        cand = cans[next_cand, 1]
        if cand == vox[-1]:
            cand = cans[next_cand, 2]
        if skel_label.flat[cand] > 1:
            vox.append(idx)
            vox.append(cand)
            n_idx = skel_label.flat[cand] - 2
            if node[n_idx]['ep']:
                ep = 1
            isdone = True
        else:
            vox.append(idx)
            idx = cand

    return vox, n_idx, ep
