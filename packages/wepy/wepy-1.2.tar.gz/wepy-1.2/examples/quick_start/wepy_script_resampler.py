from copy import copy

import openmm as omm
import openmm.unit as unit

from wepy.util.test_system_builder import NaClPair
from wepy.util.mdtraj import mdtraj_to_json_topology

from wepy.resampling.resamplers.resampler import NoResampler
from wepy.runners.openmm import OpenMMRunner, gen_walker_state
from wepy.walker import Walker
from wepy.sim_manager import Manager

from wepy.reporter.dashboard import DashboardReporter
from wepy.reporter.openmm import OpenMMRunnerDashboardSection
from wepy.reporter.revo.dashboard import REVODashboardSection

from wepy.resampling.distances.distance import Distance
from wepy.resampling.resamplers.revo import REVOResampler

import numpy as np

# we define a simple distance metric for this system, assuming the
# positions are in a 'positions' field
class PairDistance(Distance):

    def __init__(self):
        pass

    def image(self, state):
        return np.sqrt(np.sum(np.square(state['positions'][0] - state['positions'][1])))

    def image_distance(self, image_a, image_b):
        return np.abs(image_a - image_b)

    
# number of cycles of sampling to perform
n_cycles = 5
# number of steps in each dynamics run
n_steps = 1000
steps = [n_steps for i in range(n_cycles)]
# number of parallel simulations to run
n_walkers = 50

# use a ready made system for OpenMM MD simulation
test_sys = NaClPair()

test_mdj_topology = test_sys.mdtraj_topology
json_top = mdtraj_to_json_topology(test_mdj_topology)

integrator = omm.LangevinIntegrator(300.0*unit.kelvin,
                                    1/unit.picosecond,
                                    0.002*unit.picoseconds)

init_state = gen_walker_state(test_sys.positions, test_sys.system, integrator)
# create the initial walkers with equal weights
init_weight = 1.0 / n_walkers
init_walkers = [Walker(copy(init_state), init_weight) for i in range(n_walkers)]

runner = OpenMMRunner(test_sys.system, test_sys.topology, integrator,
                      platform='Reference')

distance = PairDistance()

# Set up the REVO Resampler with the parameters
resampler = REVOResampler(distance=distance,
                          init_state=init_state,
                          weights=True,
                          pmax=0.1,
                          dist_exponent=4,
                          merge_dist=0.25,
                          char_dist=0.1)

# Set up the dashboard reporter
dashboard_path = 'wepy.dash.org'
openmm_dashboard_sec = OpenMMRunnerDashboardSection(runner)
revo_dashboard_sec = REVODashboardSection(resampler)
dashboard_reporter = DashboardReporter(file_path = dashboard_path,
                                       runner_dash = openmm_dashboard_sec,
                                       resampler_dash = revo_dashboard_sec)

sim_manager = Manager(init_walkers,
                      runner=runner,
                      resampler=resampler,
                      reporters=[dashboard_reporter]
                      )

# run the simulation and get the results
final_walkers, _ = sim_manager.run_simulation(n_cycles, steps)
