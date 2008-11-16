from physics.vector3d import Vector3d
from physics.shape import Shape

sh = Shape(10.0)
sh.forces.append(Vector3d(1., 2., 3.))
#sh.forces_res.append(0.5)
sh.calculate_aceleration()
print sh.aceleration.x