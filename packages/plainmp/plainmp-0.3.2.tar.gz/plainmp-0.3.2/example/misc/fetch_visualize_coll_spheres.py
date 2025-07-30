import time

import numpy as np
from skrobot.model.primitives import Sphere
from skrobot.models.fetch import Fetch
from skrobot.viewers import PyrenderViewer

from plainmp.robot_spec import FetchSpec

fs = FetchSpec()
cst = fs.create_collision_const()
q = np.zeros(8)
cst.update_kintree(q, True)

fetch = Fetch()
fs.set_skrobot_model_state(fetch, q)
v = PyrenderViewer()
v.add(fetch)
for center, r in cst.get_group_spheres():
    s = Sphere(r, pos=center, color=[255, 0, 0, 100])
    v.add(s)

for center, r in cst.get_all_spheres():
    s = Sphere(r, pos=center, color=[0, 255, 0, 100])
    v.add(s)

v.show()
time.sleep(1000)
