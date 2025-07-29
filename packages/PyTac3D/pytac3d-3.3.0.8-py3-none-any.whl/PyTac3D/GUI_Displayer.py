from . import Presets, Sensor, Displayer, SensorView
import time

class GUI_Displayer:
    def __init__(self, port):
        self.views = {}
        self.analyzers = {}
        self.displayer = Displayer(Presets.Lights_1)
        self.sensor = Sensor(recvCallback=self.callback, port=port)
        
        self.enable_Mesh = True
        self.enable_Pointcloud = False
        self.enable_Contact = True
        self.enable_Displacements = False
        self.enable_Normals = False
        self.enable_Forces = True
        self.enable_Object = True
        self.enable_3D_ResForce = False
        self.enable_3D_ResMoment = False

        posx = 0.05
        posy = 0.9
        dposy = 0.05
        self.button_Mesh = self.displayer._plotter.add_button(
            self.button_Mesh_func,
            states=["\u23F8 Mesh","\u23F5 Mesh"],
            font="Kanopus",
            pos=(posx, posy),
            size=20,
            )
        posy -= dposy
        self.button_Pointcloud = self.displayer._plotter.add_button(
            self.button_Pointcloud_func,
            states=["\u23F8 Point","\u23F5 Point"],
            font="Kanopus",
            pos=(posx, posy),
            size=20,
            )
        posy -= dposy
        self.button_Contact = self.displayer._plotter.add_button(
            self.button_Contact_func,
            states=["\u23F8 Cont.","\u23F5 Cont."],
            font="Kanopus",
            pos=(posx, posy),
            size=20,
            )
        posy -= dposy
        self.button_Displacements = self.displayer._plotter.add_button(
            self.button_Displacements_func,
            states=["\u23F8 Disp.","\u23F5 Disp."],
            font="Kanopus",
            pos=(posx, posy),
            size=20,
            )
        posy -= dposy
        self.button_Normals = self.displayer._plotter.add_button(
            self.button_Normals_func,
            states=["\u23F8 Norm.","\u23F5 Norm."],
            font="Kanopus",
            pos=(posx, posy),
            size=20,
            )
        posy -= dposy
        self.button_Forces = self.displayer._plotter.add_button(
            self.button_Forces_func,
            states=["\u23F8 Force","\u23F5 Force"],
            font="Kanopus",
            pos=(posx, posy),
            size=20,
            )
        posy -= dposy
        self.button_Object = self.displayer._plotter.add_button(
            self.button_Object_func,
            states=["\u23F8 Obje.","\u23F5 Obje."],
            font="Kanopus",
            pos=(posx, posy),
            size=20,
            )
        posy -= dposy
        self.button_3D_ResForce = self.displayer._plotter.add_button(
            self.button_3D_ResForce_func,
            states=["\u23F8 RF","\u23F5 RF"],
            font="Kanopus",
            pos=(posx, posy),
            size=20,
            )
        posy -= dposy
        self.button_3D_ResMoment = self.displayer._plotter.add_button(
            self.button_3D_ResMoment_func,
            states=["\u23F8 RM","\u23F5 RM"],
            font="Kanopus",
            pos=(posx, posy),
            size=20,
            )
        
        if not self.enable_Mesh:
            self.button_Mesh.switch()
        if not self.enable_Pointcloud:
            self.button_Pointcloud.switch()
        if not self.enable_Contact:
            self.button_Contact.switch()
        if not self.enable_Displacements:
            self.button_Displacements.switch()
        if not self.enable_Normals:
            self.button_Normals.switch()
        if not self.enable_Forces:
            self.button_Forces.switch()
        if not self.enable_Object:
            self.button_Object.switch()
        if not self.enable_3D_ResForce:
            self.button_3D_ResForce.switch()
        if not self.enable_3D_ResMoment:
            self.button_3D_ResMoment.switch()

        self.displayer.buttonCallback_Calibrate = self.calibrate
    
    def calibrate(self):
        for SN in self.views.keys():
            self.sensor.calibrate(SN)

    def callback(self, frame, param):
        SN = frame['SN']
        view = self.views.get(SN)
        if view is None:
            view = SensorView(SN)
            cfg = view.getConfig()
            cfg['mesh_upsample'] = 3
            view.setConfig(cfg)
            self.views[SN] = view
            
            self.displayer.addView(view)
            self.updateViewSettings()
        view._analyzer.detectObjects(frame)
        view.put(frame)

    def button_Mesh_func(self):
        self.enable_Mesh = not self.enable_Mesh
        self.button_Mesh.switch()
        self.updateViewSettings()
    def button_Pointcloud_func(self):
        self.enable_Pointcloud = not self.enable_Pointcloud
        self.button_Pointcloud.switch()
        self.updateViewSettings()
    def button_Contact_func(self):
        self.enable_Contact = not self.enable_Contact
        self.button_Contact.switch()
        self.updateViewSettings()
    def button_Displacements_func(self):
        self.enable_Displacements = not self.enable_Displacements
        self.button_Displacements.switch()
        self.updateViewSettings()
    def button_Normals_func(self):
        self.enable_Normals = not self.enable_Normals
        self.button_Normals.switch()
        self.updateViewSettings()
    def button_Forces_func(self):
        self.enable_Forces = not self.enable_Forces
        self.button_Forces.switch()
        self.updateViewSettings()
    def button_Object_func(self):
        self.enable_Object = not self.enable_Object
        self.button_Object.switch()
        self.updateViewSettings()
    def button_3D_ResForce_func(self):
        self.enable_3D_ResForce = not self.enable_3D_ResForce
        self.button_3D_ResForce.switch()
        self.updateViewSettings()
    def button_3D_ResMoment_func(self):
        self.enable_3D_ResMoment = not self.enable_3D_ResMoment
        self.button_3D_ResMoment.switch()
        self.updateViewSettings()

    def updateViewSettings(self):
        offset = 10
        for view in self.views.values():
            view.enable_Mesh = self.enable_Mesh
            view.enable_Pointcloud = self.enable_Pointcloud
            view.enable_Contact = self.enable_Contact
            view.enable_Displacements = self.enable_Displacements
            view.enable_Normals = self.enable_Normals
            view.enable_Forces = self.enable_Forces
            view.enable_Object = self.enable_Object
            view.enable_3D_ResForce = self.enable_3D_ResForce
            view.enable_3D_ResMoment = self.enable_3D_ResMoment
            
            view.setTranslation([0, offset, -10])
            offset += 30
        
    def run(self):
        while self.displayer.isRunning():
            time.sleep(0.3)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 9988
    
    displayer = GUI_Displayer(port)
    displayer.run()
    # displayer.stop()

