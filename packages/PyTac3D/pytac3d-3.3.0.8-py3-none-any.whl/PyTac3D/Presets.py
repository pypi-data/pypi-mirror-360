_config_A_DL_series = {
    'mesh': (20,20), # (ny, nx)
    'mesh_upsample': 1,
    'scaleF': 30,
    'scaleD': 5,
    'scaleN': 1.0,
    'scaleRF': 2,
    'scaleRM': 0.1,
    'scaleRM_r': 5,
    'contact_F': 0.030,
    'plane': {'min_area': 30,
            'residue': 0.05,
            },
    'sphere': {'min_area': 16,
                'residue': 0.07,
                'radius_range': (1, 40),
                },
    'cylinder': {'min_area': 12,
                'residue': 0.09,
                'radius_range': (1, 40),
                }
    }

_config_DM_series = {
    'mesh': (20,20), # (ny, nx)
    'mesh_upsample': 1,
    'scaleF': 30,
    'scaleD': 5,
    'scaleN': 1.0,
    'scaleRF': 2,
    'scaleRM': 0.1,
    'scaleRM_r': 5,
    'contact_F': 0.020,
    'plane': {'min_area': 30,
            'residue': 0.03,
            },
    'sphere': {'min_area': 16,
                'residue': 0.04,
                'radius_range': (1, 40),
                },
    'cylinder': {'min_area': 16,
                'residue': 0.06,
                'radius_range': (1, 40),
                }
    }

_config_DS_series = {
    'mesh': (16,16), # (ny, nx)
    'mesh_upsample': 1,
    'scaleF': 30,
    'scaleD': 5,
    'scaleN': 0.7,
    'scaleRF': 2,
    'scaleRM': 0.1,
    'scaleRM_r': 5,
    'contact_F': 0.025,
    # 'plane': {'min_area': 30,
    #         'residue':  0.05,
    #         },
    # 'sphere': {'min_area': 16,
    #             'residue':  0.3,
    #             'radius_range': (1, 25),
    #             },
    # 'cylinder': {'min_area': 10,
    #             'residue':  0.1,
    #             'radius_range': (1, 25),
    #             }
    }

_config_Others = {
    'mesh': (20,20), # (ny, nx)
    'mesh_upsample': 1,
    'scaleF': 30,
    'scaleD': 5,
    'scaleN': 1,
    'scaleRF': 2,
    'scaleRM': 0.1,
    'scaleRM_r': 5,
    'contact_F': 0.025,
}

_config_table = {'A1': _config_A_DL_series,
                 'AD2': _config_A_DL_series,
                 'HDL1': _config_A_DL_series,
                 'DL1': _config_A_DL_series,
                  'DM1': _config_DM_series,
                  'DS1': _config_DS_series,
                  'DSt1': _config_DS_series,
                  'B1': _config_DS_series,
                  'UNKNOWN': _config_Others,
                  }

def getModelName(SN):
    model = SN.split('-')[0]
    if model:
        if model[0] == 'Y':
            model = model[1:]

    if model in _config_table.keys():
        return model
    else:
        print('[Warning] Unable to determine the model name of {}.'.format(SN))
        return 'UNKNOWN'

def getConfig(SN):
    return _config_table[getModelName(SN)]

def inputSN():
    SN = ""
    modelName = 'UNKNOWN'
    while modelName == 'UNKNOWN':
        SN = input('Please enter your sensor\'s SN: ')
        modelName = getModelName(SN)
    return SN

Mesh_Color_1 = {
    'mesh1': [60,95,170, 170],
    'mesh2': [35,38,60,170],
    'mesh_c2': [0, 242,255,170],
    'mesh_c1': [75, 159, 255,170],
    'arrow_RF': [200, 30, 30, 255],
    'arrow_RM': [30, 200, 30, 255],
    'box1': [180,197,255,25],
    'box2': [180,180,230,255],
    'sphere': [180,197,255,50],
    'cylinder': [180,197,255,50],
    'outline': [120,110,200,70],
     }

Mesh_Color_2 = {
    'mesh1': [60,95,170, 255],
    'mesh2': [35,38,60,255],
    'mesh_c2': [0, 242,255,255],
    'mesh_c1': [75, 159, 255,255],
    'arrow_RF': [200, 30, 30, 255],
    'arrow_RM': [30, 200, 30, 255],
    'box1': [180,197,255,25],
    'box2': [180,180,230,255],
    'sphere': [180,197,255,50],
    'cylinder': [180,197,255,50],
    'outline': [120,110,200,70],
     }


Lights_1 = {
    'front': {
        'intensity': 1.7,
        'color': [0.9, 0.9, 1.0],
        },
    'side' : {
        'intensity': 1.0,
        'color': [0.9, 0.9, 1.0],
        'slanted': [0.3, 0.3]
        }
    }

Lights_2 = {
    'front': {
        'intensity': 1.7,
        'color': [0.9, 0.9, 1.0],
        },
    'side' : {
        'intensity': 0.0,
        'color': [0.9, 0.9, 1.0],
        'slanted': [0.3, 0.3]
        }
    }
