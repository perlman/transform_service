
import os

# Number of cores used to parallel fetching of locations
MaxWorkers = 8

# Max number of locations per query
MaxLocations = 10e9

# Number of chunks for each worker to read
# Each chunk dimension is multiplied by this.
# e.g. 4 will lead to 64 (4*4*4) chunks per worker
CHUNK_MULTIPLIER = 1

DATASOURCES = {
    'test' : {
        'description' : 'Test volume',  # Description of data
        'type' : 'zarr',                # Which datatype?
        'scales' : [7],                 # List of mip levels available
        'voxel_size' : [4,4,40],        # Base resolution (mip 0)
        'services' : ['transform'],     # Is this for the 'transform' or 'query' service?
        'dtype' : 'float32',            # What datatype is stored?
        'width' : 2,                    # How many elements are stored? (e.g., dx,dy for transforms)
        'tsinfo' : {                    # Details for the tnesorstore library to open the data
            'driver' : 'zarr',
            'kvstore': {
                'driver': 'file',
                'path': 'test.zarr',
            },
        }   
    },
    'fanc_v4_to_v3' : {
        'description' : 'Mapping from FANCv4 to FANCv3',
        'type' : 'zarr-nested',
        'scales' : [2],
        'voxel_size' : [4.3,4.3,45],
        'services' : ['transform'],
        'dtype' : 'float32',
        'width' : 2,
        'tsinfo' : {
            'driver' : 'zarr',
            'kvstore': {
                'driver': 'file',
                'path' : '/data/fields/fanc/field.zarr'
            },
            'key_encoding': '/'
        }  
    },
    'fanc_v4' : {
        'description' : 'Zetta.ai segmentation of FANCv4 ',
        'type' : 'neuroglancer_precomputed',
        # These mip levels are those in the segmentation (@ 17.2nm) and NOT the raw data (@4.3nm)
        'scales' : [2, 3, 4, 5, 6, 7],
        'voxel_size' : [4.3, 4.3, 45],
        'services' : ['query'],
        'dtype' : 'uint64',
        'width' : 1,
        'tsinfo' : {
            'driver' : 'neuroglancer_precomputed',
            'kvstore': {
                'driver': 'file',
                'path': '/data/ssd_data/fanc_precomputed/full_run_v4/'
            }
        }
    },
    'banc_lookup_remote' : {
        'description' : 'Zetta.ai segmentation of BANC',
        'type' : 'neuroglancer_precomputed',
        # These mip levels are those in the segmentation (@ 16nm) and NOT the raw data (@4nm)
        'scales' : [2, 3, 4, 5, 6, 7, 8],
        'voxel_size' : [16, 16, 45],
        'services' : ['query'],
        'dtype' : 'uint64',
        'width' : 1,
        'tsinfo' : {
            'driver' : 'neuroglancer_precomputed',
            'kvstore': {
                'driver': 'gcs',
                'bucket': 'zetta_lee_fly_cns_001_segmentation',
            },
            'path': 'v1_sharded'
        }
    }
}
