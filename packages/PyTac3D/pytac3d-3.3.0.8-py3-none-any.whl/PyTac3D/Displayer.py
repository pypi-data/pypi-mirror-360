from . import Presets
from .Analyzer import Analyzer

import vedo
import numpy as np
import vtk
import threading
import time
import copy

class SensorView:
    def __init__(self, SN:str, color=None):
        '''
        A view for visualizing tactile sensor data. The data to be displayed can
        be configured by setting the following boolean values:

        view = SensorView(SN)
        
        view.enable_Mesh = True
        view.enable_Pointcloud = False
        view.enable_Displacements = False
        view.enable_Normals = False
        view.enable_Forces = True
        view.enable_3D_ResForce = False
        view.enable_3D_ResMoment = False
        view.enable_Contact = True          # frame['ContactRegion'] is required.
            call analyzer.detectContact(frame) to obtain frame['ContactRegion']
        view.enable_Object = True           # frame['ContactRegions'][i]['object']
            is required. call analyzer.detectObjects(frame) to obtain
            frame['ContactRegion'][i]['objects'].

        Parameters
        ----------
        SN: str
            Sensor SN. Subsequent frames visualized using the SensorView must have
            the same SN to ensure the correctness of display.
        color (optional):
            Color scheme for rendering. Default is `PyTac3D.Presets.Mesh_Color_1`
        '''

        self.SN = SN
        self.setConfig(Presets.getConfig(self.SN))

        self._analyzer = Analyzer(self.SN)
        
        self.enable_Mesh = True
        self.enable_Pointcloud = False
        self.enable_Contact = False
        self.enable_Displacements = False
        self.enable_Normals = False
        self.enable_Forces = True
        self.enable_Object = True
        self.enable_3D_ResForce = False
        self.enable_3D_ResMoment = False
        
        if color is None:
            color = Presets.Mesh_Color_1
        
        self.color_mesh1 = color['mesh1']
        self.color_mesh2 = color['mesh2']
        self.color_mesh_c1 = color['mesh_c1']
        self.color_mesh_c2 = color['mesh_c2']
        self.color_arrow_RF = color['arrow_RF']
        self.color_arrow_RM = color['arrow_RM']
        self.color_box1 = color['box1']
        self.color_box2 = color['box2']
        self.color_sphere = color['sphere']
        self.color_cylinder = color['cylinder']
        self.color_outline = color['outline']

        self._cubeSize = (25, 25, 10)

        self.reset()

    def setConfig(self, config):
        '''
        Set the current view configuration. Please obtain the current configuration
        via `getConfig` before using `setConfig`.
        Parameters
        ----------
        config: dict
            Please refer to PyTac3D.Presets._config_XXX_series for the config format
        '''
        self._config = copy.deepcopy(config)
        self._meshSize = self._config['mesh']
        self._mesh_upsample = self._config['mesh_upsample']
        self._meshSize_upsample = (int(self._meshSize[0]*self._mesh_upsample), int(self._meshSize[1]*self._mesh_upsample))
        self._faces = self._gen_faces(self._meshSize_upsample[1], self._meshSize_upsample[0])

    def getConfig(self):
        '''
        Get the current view configuration.

        Return
        ----------
        config: dict
            Please refer to PyTac3D.Presets._config_XXX_series for the config format  
        '''
        return copy.deepcopy(self._config)

    def clear(self):
        '''
        Clear all objects to be rendered in this view.
        '''
        self._frame = None
        self._displayObjList = []

    def reset(self):
        '''
        Clear all objects to be rendered in this view and reset the rotation matrix 
        and translation matrix.
        '''
        self._frame = None
        self._displayObjList = []
        self._base_rotation = np.matrix(np.eye(3), np.float64)
        self._base_translation = np.matrix(np.zeros((3,1), np.float64))

    def getRotation(self):
        '''
        Get the rotation matrix of the rendered objects in this view.

        Return
        ----------
        mat: np.matrix
            A 3x3 rotation matrix.
        '''
        return self._base_rotation

    def getTranslation(self):
        '''
        Get the translation matrix of the rendered objects in this view.

        Return
        ----------
        mat: np.matrix
            A 3x1 translation matrix.
        '''
        return self._base_translation

    def setRotation(self, R):
        '''
        Set the rotation matrix of the rendered objects in this view.

        Parameters
        ----------
        R: np.matrix
            A 3x3 rotation matrix.
        '''
        self._base_rotation = np.matrix(R, np.float64).reshape((3,3))

    def setTranslation(self, T):
        '''
        Set the translation matrix of the rendered objects in this view.

        Parameters
        ----------
        T: np.matrix
            A 3x1 translation matrix.
        '''
        self._base_translation = np.matrix(T, np.float64).reshape((3,1))

    def _transform_r(self, field):
        if field is None:
            return None
        return np.array((self._base_rotation * np.matrix(field).T).T)

    def _transform_rt(self, field):
        if field is None:
            return None
        return np.array((self._base_rotation * np.matrix(field).T + self._base_translation).T)

    def put(self, frame=None, rotation=None, translation=None, dev=False):
        '''
        Put the frame to be visualized.

        Parameters
        ----------
        frame: dict
            A tactile data frame.

        rotation (optional): np.matrix
            A 3x1 rotation matrix.

        translation (optional): np.matrix
            A 3x1 translation matrix.
        '''
        if not frame is None:
            if self.SN != frame['SN']:
                print('[Warning] The input frame does not match the SensorView. (SensorView: {}  frame: {})'.format(self.SN, frame['SN']))
                return
            self._frame = frame
        
        if not rotation is None:
            self._base_rotation = np.matrix(rotation).reshape((3,3))
        if not translation is None:
            self._base_translation = np.matrix(translation).reshape((3,1))

        if self._frame is None:
            return
        
        frame = self._frame
        
        L0 = frame.get('3D_Positions')
        D0 = frame.get('3D_Displacements')
        F0 = frame.get('3D_Forces')
        N0 = frame.get('3D_Normals')
        RF0 = frame.get('3D_ResultantForce')
        RM0 = frame.get('3D_ResultantMoment')

        L = self._transform_rt(L0)
        D = self._transform_r(D0)
        F = self._transform_r(F0)
        N = self._transform_r(N0)
        RF = self._transform_r(RF0)
        RM = self._transform_r(RM0)

        localForces = frame.get('LocalForces')
        # contactRegion = frame.get('ContactRegion')
        contactRegions = frame.get('ContactRegions')
        
        displayObjList = []
        
        if self.enable_Mesh:
            if not L is None: # 展示表面
                tmp_L = self._analyzer.resample(L, self._meshSize, self._meshSize_upsample)
                # 渐变着色
                tmp_L_xy = tmp_L[:,0:2]
                tmp_L_xy = tmp_L_xy - tmp_L_xy.mean(axis=0)
                tmp_val = np.linalg.norm(tmp_L_xy, axis=1)
                tmp_val = np.matrix(tmp_val / tmp_val.max()).T
                tmp_color = tmp_val * self.color_mesh2 + (1-tmp_val) * self.color_mesh1

                if self.enable_Contact and not localForces is None: # 接触区高亮
                    if dev: # 专用于演示滑移的模式 ！！！！！
                        tmp_Fim = localForces
                    else:
                        tmp_Fim = self._analyzer.resample(localForces, self._meshSize, self._meshSize_upsample) 
                    tmp_Fim = tmp_Fim.reshape([-1])
                    region = tmp_Fim > self._config['contact_F']
                    f_min = self._config['contact_F']
                    f_max = f_min * 1.2
                    tmp_Fim[tmp_Fim>f_max] = f_max
                    tmp_Fim -= f_min
                    tmp_Fim[tmp_Fim<0] = 0
                    
                    tmp_Fim /= f_max - f_min
                    tmp_Fim = np.matrix(tmp_Fim).T
                    tmp_c_color = tmp_Fim * self.color_mesh_c1 + (1-tmp_Fim) * self.color_mesh_c2
                    tmp_color[region,:] = tmp_c_color[region,:]  # 接触区着色

                mesh = vedo.Mesh([tmp_L, self._faces])
                mesh.pointcolors = np.array(tmp_color)     
                # mesh.subdivide(2).smooth(boundary=True)
                displayObjList.append(mesh)

        if self.enable_Pointcloud and not L is None:
            pc = vedo.Points(L, r=2, c=[255,255,255])
            displayObjList.append(pc)

        if self.enable_Displacements and not L is None and not D is None:
            # 位移场
            arrs = self._gen_arrows(L, D, self._config['scaleD'], offset=-0.2)
            displayObjList.append(arrs)
            
        if self.enable_Forces and not L is None and not F is None:
            # 分布力
            arrs = self._gen_arrows(L, F, self._config['scaleF'], offset=-0.2)
            displayObjList.append(arrs)
            
        if self.enable_Normals and not L is None and not N is None:
            # 表面法线
            arrs = self._gen_arrows(L, N, self._config['scaleN'], offset=0.1)
            displayObjList.append(arrs)

        if self.enable_3D_ResForce:
            p0 = L.mean(axis=0)
            v = RF.reshape(-1) * self._config['scaleRF']
            p1 = p0 + v
            arr = vedo.Arrow(p0, p1, c=self.color_arrow_RF[0:3], s=np.sqrt(np.linalg.norm(v))*0.015)
            displayObjList.append(arr)

        if self.enable_3D_ResMoment:
            p0, faces =self._get_RF_Arrow(RM[0,2])
            T = [0, 0, (L0[:,2].max() + 1)]
            # T = None
            R = np.matrix([[-1, 0, 0],
                           [0, -1, 0],
                           [0, 0,  1] ], np.float64)
            
            p1 = self._analyzer.transform(p0, translation=T)
            p2 = self._analyzer.transform(p0, rotation=R, translation=T)
            p1 = self._transform_rt(p1)
            p2 = self._transform_rt(p2)

            arr1 = vedo.Mesh([p1, faces], c=self.color_arrow_RM[0:3])
            arr2 = vedo.Mesh([p2, faces], c=self.color_arrow_RM[0:3])
            displayObjList.append(arr1)
            displayObjList.append(arr2)
        
        if self.enable_Object and not contactRegions is None:
            for region in contactRegions:
                obj = region.get('object')
                if not obj is None:
                    if obj['type'] == 'plane':
                        displayObjList.extend(self._gen_plane(obj))
                    elif obj['type'] == 'sphere':
                        displayObjList.extend(self._gen_sphere(obj))
                    elif obj['type'] == 'cylinder':
                        displayObjList.extend(self._gen_cylinder(obj))
        self._displayObjList = displayObjList

    def _get_RF_Arrow(self, Mz):
        n1 = 20
        n2 = 20
        R = self._config['scaleRM_r']
        ang = self._config['scaleRM'] * Mz
        r = R * np.sqrt(np.abs(ang)) * 0.1
        angs = np.linspace(0, ang, n2)
        theta = np.linspace(0,np.pi*2, n1)
        sin_t = np.sin(theta).T
        cos_t = np.cos(theta).T
        pos0 = np.array([sin_t, np.zeros(theta.shape), cos_t]).T
        posii = []
        for a in angs:
            R_mat = np.matrix([[np.cos(a), -np.sin(a), 0],
                                [np.sin(a),  np.cos(a), 0],
                                [        0,          0, 1]])
            posi = self._analyzer.transform(pos0*r, rotation=R_mat, translation=[np.cos(a)*R, np.sin(a)*R, 0])
            posii.append(posi)
        
        R_mat = np.matrix([[np.cos(ang), -np.sin(ang), 0],
                            [np.sin(ang),  np.cos(ang), 0],
                            [        0,          0,    1]])
        posi = self._analyzer.transform(pos0*r*2, rotation=R_mat, translation=[np.cos(ang)*R, np.sin(ang)*R, 0])
        posii.append(posi)

        R_mat = np.matrix([[np.cos(ang), -np.sin(ang), 0],
                            [np.sin(ang),  np.cos(ang), 0],
                            [        0,          0,    1]])
        if ang >= 0:
            r2 = r
        else:
            r2 = -r
        posi = self._analyzer.transform(pos0*0, rotation=R_mat, translation=[np.cos(ang)*R-np.sin(ang)*r2*5, np.sin(ang)*R+np.cos(ang)*r2*5, 0])
        posii.append(posi)
        posii = np.vstack(posii)

        # posii 变换
        faces = []
        for j in range(n2+1):
            for i in range(n1-1):
                base_i = i+j*n1
                faces.append([base_i, base_i+1, base_i+n1])
                faces.append([base_i+n1, base_i+1, base_i+n1+1])
        return posii, faces

    def _gen_plane(self, obj):
        normal = self._transform_r(obj['normal'])[0]
        center = self._transform_rt(obj['center'])[0]
        origin = self._transform_rt([[0, 0, 0]])[0]

        vz = normal
        vx = np.cross(np.array(self._base_rotation)[:,1], normal)
        vx = vx / np.linalg.norm(vx)
        vy = np.cross(vz, vx)

        base_z = np.array(self._base_rotation[:,2]).reshape(-1)

        center00 = np.dot(center-origin, normal) / np.dot(base_z, normal) * base_z + origin
        
        sx, sy, sz = self._cubeSize
        
        R = np.array([vx, vy, vz])
        # F_r = (np.matrix(R) * RF.T).T
        # M_r = (np.matrix(R) * RM.T).T
        # rz = (M_r[0,2] - center[0]*F_r[0,1]-center[1]*F_r[0,0]) * 0.5 / 180 * np.pi
        rz = 0
        Rz = np.matrix([
                        [np.cos(rz), -np.sin(rz), 0],
                        [np.sin(rz),  np.cos(rz), 0],
                        [0,          0,        1]
                    ])
        
        centercube = center00 + sz / 2 * vz

        cube = vedo.Box(size=(sx, sy, sz), alpha=self.color_box1[3]/255, c=self.color_box1[0:3]).apply_transform(np.array(R.T*Rz))
        
        cube.pos(centercube[0], centercube[1], centercube[2])
        outline = cube.silhouette()
        outline.color(self.color_outline[0:3])
        outline.alpha(self.color_outline[3]/255*0.6)
        
        v = np.array(Rz*R.T).T
        vx1 = v[0]
        vy1 = v[1]
        vz1 = v[2]
        ax = vedo.Arrow(center00, center00+vx1*10, c=[255,80,80], s=0.02)
        ay = vedo.Arrow(center00, center00+vy1*10, c=[80,255,80], s=0.02)
        az = vedo.Arrow(center00, center00+vz1*10, c=[80,80,255], s=0.02)
        
        return [cube, outline, ax, ay, az]
    
    def _gen_sphere(self, obj):
        center = self._transform_rt(obj['center'])[0]
        r = obj['radius']
        
        sphere = vedo.Sphere(pos=center, r=r)
        sphere.alpha(self.color_sphere[3]/255)
        sphere.lighting('glossy')
        sphere.color(self.color_sphere[0:3])
        sphere.wireframe(False)
        
        outline = sphere.silhouette()
        outline.color(self.color_outline[0:3])
        outline.alpha(self.color_outline[3]/255)
        return [sphere, outline]

    def _gen_cylinder(self, obj):
        axis = self._transform_r(obj['axis'])[0]
        center = self._transform_rt(obj['center'])[0]
        r = obj['radius']
        
        nn = 120
        base_z = np.array(self._base_rotation[:,2]).reshape(-1)
        theta = np.linspace(0,np.pi*2, nn)
        sin_t = np.matrix(np.sin(theta)).T * r
        cos_t = np.matrix(np.cos(theta)).T * r

        ax_1 = np.cross(axis, base_z)
        ax_1 = ax_1 / np.linalg.norm(ax_1)
        ax_2 = np.cross(axis, ax_1)
        ax_2 = ax_2 / np.linalg.norm(ax_2)

        height=min(max(20, r*2), 40)
        ps0 = sin_t * ax_1 + cos_t * ax_2 + center
        
        c1p = ps0+axis*height
        c2p = ps0-axis*height
        points = np.row_stack((c1p, c2p))

        c1 = vedo.Spline(c1p)
        c2 = vedo.Spline(c2p)
        c1.color(self.color_outline[0:3])
        c1.alpha(self.color_outline[3]/255)
        c2.color(self.color_outline[0:3])
        c2.alpha(self.color_outline[3]/255)
        
        faces = []
        for i in range(nn-1):
            faces.append([i+0, i+1, i+1+nn, i+nn])

        faces = np.array(faces)
        cylinder = vedo.Mesh([points, faces], alpha=self.color_cylinder[3]/255, c=self.color_cylinder[0:3])
        cylinder.lighting("glossy")
        return [cylinder, c1, c2]
            
    def _gen_arrows(self, L, field, scale, offset=-0.3):
        v = field * scale
        L0 = L + np.array(self._base_rotation[:,2].T) * offset
        
        tmp_val = np.linalg.norm(v, axis=1)
        vmax = 4 # 对应显示长度2mm，达到颜色图的顶端
        tmp_c = tmp_val / vmax
        tmp_c[tmp_c>1] = 1
        tmp_c = 0.7 - tmp_c * 0.7
        
        arrs = vedo.Arrows(list(L0), list(L0+v), s=2)
        arrs.cmap('hsv', np.repeat(tmp_c , 61), vmin=0, vmax=1)
        return arrs
        
    def _gen_faces(self, nx, ny):
        faces = []
        for iy in range(ny-1):
            for ix in range(nx-1):
                idx = iy * nx + ix
                faces.append([idx, idx+1, idx+nx])
                faces.append([idx+nx+1, idx+nx, idx+1])
        return faces

class Displayer:
    def __init__(self, lights=None):
        '''
        Create a rendering window to display the content from SensorView.
        
        Parameters
        ----------
        lights (optional):
            light scheme for rendering. Default is `PyTac3D.Presets.Lights_1`        
        '''
        self._viewList = {}
        self._recvFirstFrame = False
        self._plotter = vedo.Plotter(bg='#101010')
        self._plotter.camera.SetFocalPoint([0,0,0])
        self._plotter.camera.SetViewUp([0, 0, 1])
        self._plotter.camera.SetPosition([-30,-180,270])
        self._plotter.camera.SetClippingRange(0.1, 10000)

        if lights is None:
            lights = Presets.Lights_1

        lightsList = [vtk.vtkLight() for i in range(6)]
        lightsList[0].SetPosition(0, 0, 100) # 光源位置（方向由位置和焦点决定）
        lightsList[1].SetPosition(0, 0, -100)
        lightsList[2].SetPosition(100, 0, 100*lights['side']['slanted'][0])
        lightsList[3].SetPosition(-100, 0, -100*lights['side']['slanted'][0])
        lightsList[4].SetPosition(0, 100, 100*lights['side']['slanted'][1])
        lightsList[5].SetPosition(0, -100, -100*lights['side']['slanted'][1])
        lightsList[0].SetColor(*lights['front']['color'])    # RGB范围 0~1
        lightsList[1].SetColor(*lights['front']['color']) 
        lightsList[2].SetColor(*lights['side']['color'])
        lightsList[3].SetColor(*lights['side']['color'])
        lightsList[4].SetColor(*lights['side']['color'])
        lightsList[5].SetColor(*lights['side']['color'])
        lightsList[0].SetIntensity(lights['front']['intensity'])   # 光照强度
        lightsList[1].SetIntensity(lights['front']['intensity'])
        lightsList[2].SetIntensity(lights['side']['intensity'])
        lightsList[3].SetIntensity(lights['side']['intensity'])
        lightsList[4].SetIntensity(lights['side']['intensity'])
        lightsList[5].SetIntensity(lights['side']['intensity'])

        for i in range(6):
            lightsList[i].SetLightTypeToSceneLight()  # 设置为场景光源
            lightsList[i].SetFocalPoint(0, 0, 0)      # 焦点方向（决定光线平行方向）
            self._plotter.renderer.AddLight(lightsList[i])
        
        self.buttonCallback_Restart = None
        self.buttonCallback_Calibrate = None

        self._button_calibrate = self._plotter.add_button(
                    self._buttonFunc_Calibrate,
                    states=["calibrate"],
                    font="Kanopus",
                    pos=(0.7, 0.9),
                    size=20,
                )
        self._button_switch = self._plotter.add_button(
                    self._buttonFunc_Restart,
                    states=["Restart"],
                    font="Kanopus",
                    pos=(0.2, 0.9),
                    size=20,
                )
        
        self.running = True
        self._dt = 80
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def put(self, frame):
        '''
        Put the frame to be visualized. This function automatically checks the frame's
        SN and places it into the corresponding SensorView (if it exists).

        Parameters
        ----------
        frame: dict
            A tactile data frame.
        '''
        view = self._viewList.get(frame['SN'])
        if not view is None:
            view.put(frame)
        else:
            print('[Warning] No SensorView matching the SN ({}) was found. Please use `Displayer.addView` to add a SensorView first.'.format(frame['SN']))

    def addView(self, view: SensorView):
        '''
        Add a SensorView to be displayed.
        
        Parameters
        ----------
        view: SensorView
            SensorView to be displayed
        '''
        self._viewList[view.SN] = view

    def deleteView(self, SN: str):
        '''
        Remove the SensorView corresponding to the specified SN.

        Parameters
        ----------
        SN: str
            Sensor SN.
        '''
        if not self._viewList.get(SN) is None:
            del self._viewList[SN]
    
    def _run(self):
        self._plotter.show(interactive=False)
        self._timer_id = self._plotter.timer_callback('create', dt=10)
        self._timerevt = self._plotter.add_callback('timer', self._showOnce)
        self._plotter.interactive()
        self.close()
    
    def _showOnce(self, event):
        self._plotter.clear()
        displayObjs = []
        for view in self._viewList.values():
            displayObjs.extend(view._displayObjList)
        if len(displayObjs) > 0:
            self._plotter.add(*displayObjs)
            if not self._recvFirstFrame:
                self._recvFirstFrame = True
                self._plotter.reset_camera()
                self._plotter.camera.SetFocalPoint([0,0,0])
                self._plotter.camera.SetViewUp([0, 0, 1])
                self._plotter.camera.SetPosition([-20,-90,140])
            self._plotter.camera.SetClippingRange(0.1, 10000)
        self._plotter.render()
        time.sleep(self._dt / 1000)
    
    def _buttonFunc_Restart(self):
        if not self.buttonCallback_Restart is None:
            self.buttonCallback_Restart()

    def _buttonFunc_Calibrate(self):
        if not self.buttonCallback_Calibrate is None:
            self.buttonCallback_Calibrate()
    
    def isRunning(self):
        '''
        Returns whether the Display is running.

        Return
        ----------
        result: bool
            True: running
            False: stopped
        '''
        return self.running

    def close(self):
        '''
        Close the rendering window.
        '''
        self._plotter.close()
        self.running = False
        

