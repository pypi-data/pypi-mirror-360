import numpy as np
from scipy.ndimage import label
from .helpers import pk_get_nh_idx, pk_get_nh, pk_follow_link


def prune_edges3(skel, thresh):
    if not np.any(skel):
        return skel

    skel_label = skel.T.astype(np.uint16)

    canal_pts_list = np.flatnonzero(skel.flatten(order='F'))

    nh = pk_get_nh(skel, canal_pts_list)
    nhi = pk_get_nh_idx(skel, canal_pts_list)

    sum_nh = np.sum(nh, axis=1)

    nodes = canal_pts_list[sum_nh > 3]

    if nodes.size == 0:
        return skel

    ep = canal_pts_list[sum_nh == 2]
    cans = canal_pts_list[sum_nh == 3]

    can_nh_idx = pk_get_nh_idx(skel, cans)
    can_nh = pk_get_nh(skel, cans)

    can_nh_idx = np.delete(can_nh_idx, 13, axis=1)
    can_nh = np.delete(can_nh, 13, axis=1)

    can_nb = np.sort(can_nh.astype(bool) * can_nh_idx, axis=1)
    can_nb = can_nb[:, -2:]

    cans = np.column_stack((cans, can_nb))

    node = []
    link = []

    tmp = np.zeros_like(skel.T, dtype=bool)
    tmp.flat[nodes] = True

    structure = np.ones((3, 3, 3), dtype=bool)
    labeled, num_realnodes = label(tmp, structure=structure)

    for i in range(1, num_realnodes + 1):
        idxs = np.flatnonzero(labeled == i)
        node.append({'idx': idxs, 'links': [], 'conn': [], 'ep': 0})
        skel_label.flat[idxs] = i + 1

    tmp = np.zeros_like(skel.T, dtype=bool)
    tmp.flat[ep] = True
    labeled, num_endnodes = label(tmp)

    for i in range(1, num_endnodes + 1):
        idxs = np.flatnonzero(labeled == i)
        ni = num_realnodes + i
        node.append({'idx': idxs, 'links': [], 'conn': [], 'ep': 1})
        skel_label.flat[idxs] = ni + 1

    l_idx = 0
    c2n = np.zeros(skel.size, dtype=int)
    c2n[cans[:, 0]] = np.arange(cans.shape[0])

    s2n = np.zeros(skel.size, dtype=int)
    s2n[nhi[:, 13]] = np.arange(nhi.shape[0])

    for i in range(len(node)):
        link_idx = s2n[node[i]['idx']]

        for j in range(len(link_idx)):
            link_cands = nhi[link_idx[j], nh[link_idx[j], :] == 1]
            link_cands = link_cands[skel_label.flat[link_cands] == 1]

            for cand in link_cands:
                vox, n_idx, ep_flag = pk_follow_link(skel_label, node, i, j, cand, cans, c2n)
                skel_label.flat[vox[1:-1]] = 0
                if (ep_flag and len(vox) > thresh) or (not ep_flag):
                    link.append({'n1': i, 'n2': n_idx, 'point': vox})
                    node[i]['links'].append(l_idx)
                    node[n_idx]['links'].append(l_idx)
                    l_idx += 1

    for i in [idx for idx, n in enumerate(node) if len(n['links']) == 1]:
        node[i]['ep'] = 1

    out = np.zeros_like(skel.T, dtype=bool)
    for n in node:
        if n['links']:
            out.flat[n['idx']] = True
            for o in n['links']:
                if o >= 0:
                    out.flat[link[o]['point']] = True
    
    return out.T

