from .Presets import getConfig
import numpy as np
from scipy.ndimage import label
from scipy.optimize import least_squares
import cv2

def pca_axis(centered_points):
    cov_matrix = np.cov(centered_points, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    
    # 最大主轴方向
    axis_max = eigenvectors[:, np.argmax(eigenvalues)]
    # 最小主轴方向
    axis_min = eigenvectors[:, np.argmin(eigenvalues)]
    
    return axis_max, axis_min

class Analyzer:
    def __init__(self, SN: str):
        '''
        Parameters
        ----------
        SN: str
            Sensor SN. Subsequent frames analyzed using the analyzer must have the
            same SN to ensure the correctness of analysis results.
        '''
        self.SN = SN
        self._config = getConfig(SN)
        self._meshSize = self._config['mesh'] # (ny, nx)
        self._contact_F = self._config['contact_F']
        self._plane_fit_cfg = self._config.get('plane')
        self._sphere_fit_cfg = self._config.get('sphere')
        self._cylinder_fit_cfg = self._config.get('cylinder')
        self.supportIdentify = (self._plane_fit_cfg != None) and (self._sphere_fit_cfg != None) and (self._cylinder_fit_cfg != None)
        
    def points2matrix(self, points, shape=None):
        '''
        Convert scattered data into matrix form. For example, transform 400x3
        "3D_Forces" data into a 20x20 3-channel image:

        `force_img = analyzer.points2matrix(frame['3D_Forces'])`

        Parameters
        ----------
        points: np.ndarray
            An MxN input matrix, where M = Number of sensing points (e.g., 400 for
            DL1 series sensors), N = Number of data channels (e.g., 3 for "3D_Forces"
            data). 
        shape: (ny:int, nx:int)
            A tuple in (ny, nx) format, representing the rows and columns of the
            converted image. If unspecified, the Analyzer will automatically determine
            the image dimensions based on the sensor's preset parameters.
        
        Return
        ----------
        mat: np.ndarray
            The converted multi-channel matrix (image).
        '''
        if shape is None:
            return points.reshape((self._meshSize[0], self._meshSize[1], -1))
        else:
            return points.reshape((shape[0], shape[1], -1))
        
    def matrix2points(self, mat, shape=None):
        '''
        Convert multi-channel matrix into scattered form. It is the inverse operation
        of `Analyzer.points2matrix`. For example:
        
        `force_img = analyzer.points2matrix(frame['3D_Forces'])`
        `forces = analyzer.matrix2points(force_img)`

        Here, `forces` will be the same as `frame['3D_Forces']`

        Parameters
        ----------
        mat: np.ndarray
            The converted multi-channel matrix (image).
            
        shape (optional): (ny:int, nx:int)
            A tuple in (ny, nx) format, representing the rows and columns of the
            converted image. If unspecified, the Analyzer will automatically determine
            the image dimensions based on the sensor's preset parameters.
        
        Return
        ----------
        points: np.ndarray
            An MxN matrix, where M = Number of sensing points (or ny*nx),
            N = Number of data channels (e.g., 3 for "3D_Forces" data). 
        '''
        if shape is None:
            return mat.reshape((self._meshSize[0]*self._meshSize[1], -1))
        else:
             return mat.reshape((shape[0]*shape[1], -1))
    
    def transform(self, field, rotation=None, translation=None):
        '''
        Applies the specified rotation and translation transformations to the input
        3D data.  

        Parameters
        ----------
        field: np.ndarray
            An Nx3 matrix, where the 3 columns represent x, y, z components  
        rotation: np.ndarray or np.matrix
            A 3x3 rotation matrix  
        translation: np.ndarray or np.matrix or list
            A 3x1 translation matrix

        Return
        ----------
        mat: np.matrix
            The transformed Nx3 matrix.
        '''

        if field is None:
            return None
        
        if not rotation is None:
            rotation = np.matrix(rotation).reshape((3,3))
        else:
            rotation = np.matrix(np.eye(3), np.float64)
        
        if not translation is None:
            translation = np.matrix(translation).reshape((3,1))
        else:
            translation = np.matrix(np.zeros((3,1), np.float64))

        return np.array((rotation * np.matrix(field).T + translation).T)

    def resample(self, points, shape_in=None, shape_out=None):
        '''
        Resample the scattered data. For example, DL1 series sensors have 400 sensing
        points arranged in a 20x20 array, where frame['3D_Positions'] are 400x3
        matrices representing the positions and displacements of the sensing points.
        Through `resampled_P = Analyzer.resample(frame['3D_Positions'], shape_out=(30,30))`,
        a 900x3 matrix `resampled_P` can be obtained, corresponding to the data at
        the sensing points of the 30x30 array. Note that this operation only changes
        the sampling rate of the data points and cannot improve the actual spatial
        resolution.
        
        Parameters
        ----------
        points: np.ndarray
            The scattered data, like frame['3D_Positions'], frame['3D_Displacements'],
            frame['3D_Normals'], ect.
            
        shape_in (optional): (ny:int, nx:int)
            A tuple in (ny, nx) format describing the shape of the sampling point
            array of the input data. If unspecified, the Analyzer will automatically
            determine the shape based on the sensor's preset parameters.

        shape_out (optional): (ny:int, nx:int)
            A tuple in (ny, nx) format describing the shape of the sampling point
            array of the output data. If unspecified, the Analyzer will automatically
            determine the shape based on the sensor's preset parameters.
        
        Return
        ----------
        points: np.ndarray
            An MxN matrix, where M = shape_out[0] * shape_out[1], N = Number of
            data channels (e.g., 3 for "3D_Forces" data). 
        '''

        if shape_in is None:
            shape_in = self._meshSize
        if shape_out is None:
            shape_out = self._meshSize
        if shape_in == shape_out:
            return points.copy()
        mat = self.points2matrix(points, shape_in)
        mat = cv2.resize(mat, (shape_out[1], shape_out[0]), interpolation=cv2.INTER_CUBIC)
        # mat = cv2.resize(mat, (shape_out[1], shape_out[0]))
        return self.matrix2points(mat, shape_out)

    def _checkSN(self, frame):
        if frame['SN'] != self.SN:
            print('[Warning] The input frame does not match the Analyzer. (Analyzer: {}  frame: {})'.format(self.SN, frame['SN']))
            return False
        else:
            return True

    def detectContact(self, frame):
        '''
        Detects the contact area in the input data frame. Upon successful detection,
        the following key-value pairs will be added to the frame:

        frame['LocalForces']: np.ndarray
            An Mx1 matrix, where N = Number of sensing points (e.g., 400 for DL1
            series sensors). Each element represents the absolute value of the local
            force at the corresponding sensing point.

        frame['ContactRegion']: dict
            {
                'region': np.ndarray - An Mx1 bool matrix. True represents the contact
                          point.
                'area':   Total number of contact points.
            }

        frame['ContactRegions']: list[dict, ...]
            The contact regions are segmented into connected domain. Each item in the
            list represents a connected domain of the contact regions.
            [
                {
                    'region': np.ndarray - An Mx1 bool matrix. True represents the contact
                          point of current connected domain.
                    'area':   Total number of contact points in connected domain.
                },
                ...
            ]

        Parameters
        ----------
        frame: dict
            A tactile data frame.
        
        Return
        ----------
        result: bool
            True: Detection successful.
            False: Failed, typically due to encountering an error.
        '''

        if not self._checkSN(frame):
            return False

        if not frame.get('LocalForces') is None and not frame.get('ContactRegion') is None and not frame.get('ContactRegions') is None:
            # Already exists, do not need to calculate
            return True

        localForces = np.linalg.norm(frame['3D_Forces'], axis=1)
        frame['LocalForces'] = localForces.reshape(-1,1)
        mask = localForces > self._contact_F
        mask2D = mask.reshape(self._meshSize)
        labeled_mask2D, num_features = label(mask2D)
        labeled_mask = labeled_mask2D.reshape((self._meshSize[0]*self._meshSize[1], -1))
        
        frame['ContactRegion'] = {'region': mask.reshape(-1,1),
                                   'area': mask.sum()}
        frame['ContactRegions'] = []
        for i in range(num_features):
            region = labeled_mask==(i+1)
            frame['ContactRegions'].append({'region': region,
                                            'area': region.sum()})
        return True
    
    def _fit_plane(self, points):
        N = points.shape[0]  # 点的数量
        if N < self._plane_fit_cfg['min_area']:
            return None
        center = np.mean(points, axis=0)
        centered_points = points - center
        axis_max, axis_min = pca_axis(centered_points)
        if np.dot(axis_min, center) < 0:
            axis_min = -axis_min
        # 计算残差
        res = centered_points * np.matrix(axis_min).reshape((3,1))
        residuce = np.sqrt(np.multiply(res, res).mean())
        
        if residuce < self._plane_fit_cfg['residue']:
            return {'type': 'plane',
                    'normal': axis_min,
                    'center': center,
                    'residuce': residuce,
                    }
        else:
            return None

    def _fit_sphere(self, points):
        N = points.shape[0]  # 点的数量
        if N < self._sphere_fit_cfg['min_area']:
            return None
        x, y, z = points.T   # 转置成 (x, y, z) 三个数组
        # 构造矩阵
        A = np.column_stack([x, y, z, np.ones(N)])
        b = x**2 + y**2 + z**2  # x² + y² + z²
        # 最小二乘解 Ax = b
        x0, y0, z0, D = np.linalg.lstsq(A, b, rcond=None)[0]
        # 计算球心和半径
        center = np.array([x0, y0, z0]) / 2
        r = np.sqrt(x0**2 + y0**2 + z0**2 + 4 * D) / 2
        # 计算残差
        r_pos = points - center
        if r_pos[:,2].mean() > 0: # 限定为凸球面
            return None
        res = np.linalg.norm(r_pos, axis=1) - r  # 点到球心的距离
        residuce = np.sqrt(np.multiply(res, res).mean())
        
        r_min, r_max = self._sphere_fit_cfg['radius_range']
        if residuce < self._sphere_fit_cfg['residue'] and r > r_min and r < r_max:
            return {'type': 'sphere',
                    'center': center,
                    'radius': r,
                    'residuce': residuce,
                    }
        else:
            return None
        
    def _fit_cylinder(self, points, localForces):
        mask2 = localForces.reshape(-1) > (self._contact_F * 1.4)
        maskedPoints2 = points[mask2, :]
        
        N = maskedPoints2.shape[0]  # 点的数量
        if N < self._cylinder_fit_cfg['min_area']:
            return None

        vz = np.array([0,0,1], np.float64)
        
        center = np.mean(maskedPoints2, axis=0)
        centered_points = maskedPoints2 - center
        axis_max, axis_min = pca_axis(centered_points)
        
        def cylinderLoss(params, pts, axis):
            """计算点到圆柱面的距离平方"""
            x0, y0, z0, r = params
            # 轴线方向必须是单位向量
            a = np.array(axis)
            a = a / np.linalg.norm(a)
            # 计算点到圆柱的垂直距离
            p0 = np.array([x0, y0, z0])  # 圆柱轴线上某点
            p = pts - p0  # 相对坐标
            # 点到圆柱的距离: sqrt((p • p) - (p • a)²) - r
            dist = np.sqrt(np.sum(p**2, axis=1) - np.dot(p, a)**2) - r
            return dist
        
        # 初始猜测参数
        center0 = center + vz * 5
        params0 = np.array([
            center0[0], center0[1], center0[2],  # 中心点 (x0, y0, z0)
            5         # 半径 r（初始猜测 3）
        ])
        
        res = least_squares(cylinderLoss, params0, args=(maskedPoints2, axis_max))
        residuce = np.sqrt(np.power(res.fun, 2).mean())
        x0, y0, z0, r = res.x
        r_min, r_max = self._cylinder_fit_cfg['radius_range']
        if residuce < self._cylinder_fit_cfg['residue'] and r > r_min and r < r_max:
            p0 = np.array([x0, y0, z0])
            dst = np.dot(p0-center, axis_max)
            p0 -= dst * axis_max
            
            return {'type': 'cylinder',
                    'center': p0,
                    'radius': r,
                    'axis': axis_max,
                    'residuce': residuce,
                    }
        else:
            return None
        
    def detectObjects(self, frame):
        '''
        Detects the object within each contact regions. Upon successful detection,
        the key-value pairs ('object') will be added to the each item in frame['ContactRegions']:

        frame['ContactRegions'][i]: dict
            {
                'region': ...
                'area':   ...
                'object' (ADDED):  dict or None (if the object cannot be identified)
                    {
                        'type': str 
                            'plane', 'sphere' or 'cylinder'
                        'center': [x, y, z]
                            The center of the plane, sphere or cylinder.
                        'radius': r
                            This value exists if the object is 'sphere' or 'cylinder'.
                        'axis': [vx, vy, vz]
                            The axis of the cylinder. This value exists if the 
                            object is 'cylinder'.
                        'normal': [vx, vy, vz]
                            the normal direction of the plane. This value exists
                            if the object is 'plane'.
                        'residuce': residuce,
                            Variance of fitting residuals.
                    }
            }


        Parameters
        ----------
        frame: dict
            A tactile data frame.
        
        Return
        ----------
        result: bool
            True: Detection successful.
            False: Failed, typically due to encountering an error.
        '''

        if not self._checkSN(frame):
            return False
        
        if not self.supportIdentify:
            print('[Warning] this sensor does not support detectObjects .(Analyzer: {})'.format(self.SN))
            return False
        
        if frame.get('ContactRegions') is None:
            self.detectContact(frame)

        obj = None
        for regionInfo in frame['ContactRegions']:
            pos = frame['3D_Positions']
            region = regionInfo['region'].reshape(-1)
            masked_pos = pos[region,:]
            obj = self._fit_plane(masked_pos)
            if obj is None:
                obj = self._fit_sphere(masked_pos)
            if obj is None:
                masked_force = frame['LocalForces'][region,:]
                obj = self._fit_cylinder(masked_pos, masked_force)
            regionInfo['object'] = obj
        return True
    
    # def detectSlip(self, frame):
    #     '''
    #     '''
    #     if not self._checkSN(frame):
    #         return False
    #     self._slipFrameStack.append(frame)
    #     pass
    #     return False


