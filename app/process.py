from pathos.threading import ThreadPool

import numpy as np
import pandas as pd

#
# Code based on https://github.com/flyconnectome/CloudVolumeServer/blob/master/process.py
#


def _get_ids(vol, bl, co):
    """Fetch block and extract IDs.

    Parameters
    ----------
    vol :       CloudVolume
                Volume to query.
    bl :        list-like
                Coordinates defining the block:
                left, right, top, bottom, z1, z2
    co :        numpy array
                x/y/z coordinates WITHIN block
                of segment IDs to fetch.

    """
    # Unpack block indices
    l, r, t, b, z1, z2 = bl

    # Use integer coordinates (for now...)
    co = co.astype(int)

    # Subset block to relevant parts (i.e. those containing
    # requested coordinates) to save memory
    mn = co.min(axis=0)
    mx = co.max(axis=0) + 1
    l, r = l + mn[0], l + mx[0]
    t, b = t + mn[1], t + mx[1]
    z1, z2 = z1 + mn[2], z1 + mx[2]

    # Offset coordinates too
    co -= mn

    # Get the block
    chunk = vol[l:r, t:b, z1:z2]

    # Get the IDs out of the block
    co_id = chunk[co[:, 0], co[:, 1], co[:, 2]]

    return co_id


def get_multiple_ids(x, vol, max_workers=4, blocksize=np.array([512, 512, 32])):
    """Return multiple segment IDs using cloudvolume.

    Parameters
    ----------
    x :       numpy array
              Array with x/y/z coordinates to fetch
              segmentation IDs for.
    vol :     cloudvolume.CloudVolume

    """
    # Make sure x is array
    if not isinstance(x, np.ndarray):
        x = np.array(x)

    if not max_workers:
        max_workers = 1

    # Make bins to fit with blocksize
    xbins = np.arange(0, np.nanmax(x) + blocksize[0] + 1, blocksize[0]).astype(int)
    ybins = np.arange(0, np.nanmax(x) + blocksize[1] + 1, blocksize[1]).astype(int)
    zbins = np.arange(0, np.nanmax(x) + blocksize[2] + 1, blocksize[2]).astype(int)

    # Sort data into bins
    cbin = pd.DataFrame(x)
    cbin['x_bin'] = pd.cut(cbin[0], xbins, include_lowest=True, right=False)
    cbin['y_bin'] = pd.cut(cbin[1], ybins, include_lowest=True, right=False)
    cbin['z_bin'] = pd.cut(cbin[2], zbins, include_lowest=True, right=False)
    # This is now a dictionary of bin -> indices of coordinates
    # blocked = cbin.groupby(['x_bin', 'y_bin', 'z_bin']).indices

    # Throw out NaNs
    cbin = cbin.loc[~np.any(cbin.isnull(), axis=1)]

    # This is now a dictionary of bin -> indices of coordinates
    blocked = cbin.groupby(['x_bin', 'y_bin', 'z_bin']).indices

    # Map filtered indices back to non-filtered indices
    blocked = {k: cbin.index[v] for k,v in blocked.items()}

    # Start process pool (do not use max cpu count -> appears to be a bottle neck)

    with ThreadPool(nodes=max_workers) as pool:
        seg_ix = []
        ranges = []
        cos = []
        # Iterate over all blocks
        for bl, co_ix in blocked.items():
            # Get this block's (i.e. the bin's) indices
            l, r, t, b, z1, z2 = (int(bl[0].left), int(bl[0].right),
                                  int(bl[1].left), int(bl[1].right),
                                  int(bl[2].left), int(bl[2].right))

            # Get the coordinates in this bin
            co = x[co_ix]

            # Offset coordinates by the chunk's coordinates
            # to produce "in block coordinates"
            co = co - np.array([l, t, z1])

            # Keep track of the indices of the coordinates we are querying
            # in this iteration
            seg_ix.append(co_ix)

            #  Add to list of coordinates
            cos.append(co)

            # Add to list of indices
            ranges.append( [l, r, t, b, z1, z2])

        result = pool.map(_get_ids, [vol] * len(seg_ix), ranges, cos)
        seg_ids = np.vstack(result)

        pool.clear()

    # Turn list of list of indices into a flat array
    seg_ix = np.hstack(seg_ix)

    # Generate placeholder of NaNs. Get data width from the returned data.
    ordered = np.full((x.shape[0], seg_ids.shape[1]), np.nan)

    # Populate with segment IDs
    ordered[seg_ix] = seg_ids

    return ordered
