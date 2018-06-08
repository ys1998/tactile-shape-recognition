"""
Wrappers for handling PCD files.
"""

import numpy as np
import os, sys
sys.path.append('..')

import pypcd.pypcd as pcd

"""
Load point cloud as numpy ndarray from PCD file.
"""
def load_point_cloud(filepath):
    with open(filepath, 'r') as f:
        pc = pcd.point_cloud_from_fileobj(f)
        pts = pc.pc_data
        # NOTE Hack for converting structured array to ndarray
        pts = pts.view(pts.dtype[0]).reshape(pts.shape + (-1,))
    return pts

"""
Save point clouds (numpy ndarray) to PCD file.
"""
def save_point_cloud(pts, filename):
    pc = pcd.make_xyz_point_cloud(pts)
    # Write point cloud to file in PCD format
    metadata = pc.get_metadata()
    with open(filename, 'w') as fileobj:
        # Write headers
        template = "VERSION {version}\nFIELDS {fields}\nSIZE {size}\nTYPE {type}\nCOUNT {count}\nWIDTH {width}\nHEIGHT {height}\nVIEWPOINT {viewpoint}\nPOINTS {points}\nDATA {data}\n"
        new_fields = []
        for f in metadata['fields']:
            if f == '_':
                new_fields.append('padding')
            else:
                new_fields.append(f)
        metadata['fields'] = ' '.join(new_fields)
        metadata['size'] = ' '.join(map(str, metadata['size']))
        metadata['type'] = ' '.join(metadata['type'])
        metadata['count'] = ' '.join(map(str, metadata['count']))
        metadata['width'] = str(metadata['width'])
        metadata['height'] = str(metadata['height'])
        metadata['viewpoint'] = ' '.join(map(str, metadata['viewpoint']))
        metadata['points'] = str(metadata['points'])
        metadata['data'] = 'ascii'
        tmpl = template.format(**metadata)
        fileobj.write(tmpl)

        pts = pc.pc_data
        # NOTE Hack to convert structured numpy array to ndarray
        pts = np.squeeze(pts.view(pts.dtype[0]).reshape(pts.shape + (-1,)))
        # Write the data
        np.savetxt(fileobj, pts, fmt='%.8f')
