import os
import os.path
import numpy as np

import scipy
import scipy.special
import scipy.integrate

import openmm
from openmm import unit
from openmm import app

class TestSystem(object):

    """Abstract base class for test systems, demonstrating how to implement a test system.

    Parameters
    ----------

    Attributes
    ----------
    system : openmm.System
        System object for the test system
    positions : list
        positions of test system
    topology : list
        topology of the test system

    Notes
    -----

    Unimplemented methods will default to the base class methods, which raise a NotImplementedException.

    Examples
    --------

    Create a test system.

    >>> testsystem = TestSystem()

    Retrieve a deep copy of the System object.

    >>> system = testsystem.system

    Retrieve a deep copy of the positions.

    >>> positions = testsystem.positions

    Retrieve a deep copy of the topology.

    >>> topology = testsystem.topology

    Serialize system and positions to XML (to aid in debugging).

    >>> (system_xml, positions_xml) = testsystem.serialize()

    """

    def __init__(self, **kwargs):
        """Abstract base class for test system.

        Parameters
        ----------

        """

        # Create an empty system object.
        self._system = openmm.System()

        # Store positions.
        self._positions = unit.Quantity(np.zeros([0, 3], float), unit.nanometers)

        # Empty topology.
        self._topology = app.Topology()
        # MDTraj Topology is built on demand.
        self._mdtraj_topology = None

        return

    @property
    def system(self):
        """The openmm.System object corresponding to the test system."""
        return self._system

    @system.setter
    def system(self, value):
        self._system = value

    @system.deleter
    def system(self):
        del self._system

    @property
    def positions(self):
        """The openmm.unit.Quantity object containing the particle positions, with units compatible with openmm.unit.nanometers."""
        return self._positions

    @positions.setter
    def positions(self, value):
        self._positions = value

    @positions.deleter
    def positions(self):
        del self._positions

    @property
    def topology(self):
        """The openmm.app.Topology object corresponding to the test system."""
        return self._topology

    @topology.setter
    def topology(self, value):
        self._topology = value
        self._mdtraj_topology = None

    @topology.deleter
    def topology(self):
        del self._topology

    @property
    def mdtraj_topology(self):
        """The mdtraj.Topology object corresponding to the test system (read-only)."""
        import mdtraj as md
        if self._mdtraj_topology is None:
            self._mdtraj_topology = md.Topology.from_openmm(self._topology)
        return self._mdtraj_topology
    
 
def construct_restraining_potential(particle_indices, K):
    """Make a CustomExternalForce that puts an origin-centered spring on the chosen particles"""

    # Add a restraining potential centered at the origin.
    energy_expression = '(K/2.0) * (x^2 + y^2 + z^2);'
    energy_expression += 'K = %f;' % (K / (unit.kilojoules_per_mole / unit.nanometers ** 2))  # in OpenMM units
    force = openmm.CustomExternalForce(energy_expression)
    for particle_index in particle_indices:
        force.addParticle(particle_index, [])
    return force 
    
class NaClPair(TestSystem):
    
    """Create a NaCl pair
    """
    
    def __init__(self, cutoff=None, switch_width=None, **kwargs):
        
        TestSystem.__init__(self, **kwargs)

        # Default parameters for Na and Cl
        mass_Na = 22.99 * unit.amu
        mass_Cl = 35.45 * unit.amu
        q_Na = 1.0 * unit.elementary_charge
        q_Cl = -1.0 * unit.elementary_charge
        sigma_Na = 2.0 * unit.angstrom
        sigma_Cl = 4.0 * unit.angstrom
        epsilon_Na = 0.1 * unit.kilojoule_per_mole
        epsilon_Cl = 0.2 * unit.kilojoule_per_mole

        scaleStepSizeX = 1.0
        scaleStepSizeY = 1.0
        scaleStepSizeZ = 1.0

        # Create an empty system object.
        system = openmm.System()

        # Create a nonperiodic NonbondedForce object.
        nb = openmm.NonbondedForce()

        if cutoff is None:
            nb.setNonbondedMethod(openmm.NonbondedForce.NoCutoff)
        else:
            nb.setNonbondedMethod(openmm.NonbondedForce.CutoffNonPeriodic)
            nb.setCutoffDistance(cutoff)
            nb.setUseDispersionCorrection(False)
            nb.setUseSwitchingFunction(False)
            if switch_width is not None:
                nb.setUseSwitchingFunction(True)
                nb.setSwitchingDistance(cutoff - switch_width)

        positions = unit.Quantity(np.zeros([2, 3], np.float32), unit.angstrom)  # Two atoms: Na and Cl

        # Add Na
        system.addParticle(mass_Na)
        nb.addParticle(q_Na, sigma_Na, epsilon_Na)
        x = sigma_Na * scaleStepSizeX * (-0.5)  # Place Na at -0.5 sigma in x direction
        y = sigma_Na * scaleStepSizeY * (-0.5)  # Place Na at -0.5 sigma in y direction
        z = sigma_Na * scaleStepSizeZ * (-0.5)  # Place Na at -0.5 sigma in z direction
        positions[0, 0] = x
        positions[0, 1] = y
        positions[0, 2] = z

        # Add Cl
        system.addParticle(mass_Cl)
        nb.addParticle(q_Cl, sigma_Cl, epsilon_Cl)
        x = sigma_Cl * scaleStepSizeX * (0.5)  # Place Cl at 0.5 sigma in x direction
        y = sigma_Cl * scaleStepSizeY * (0.5)  # Place Cl at 0.5 sigma in y direction
        z = sigma_Cl * scaleStepSizeZ * (0.5)  # Place Cl at 0.5 sigma in z direction
        positions[1, 0] = x
        positions[1, 1] = y
        positions[1, 2] = z

        # Add the nonbonded force.
        system.addForce(nb)

        # Create topology.
        topology = app.Topology()
        chain = topology.addChain()

        # Add Na
        residue_Na = topology.addResidue('Na', chain)
        element_Na = app.Element.getBySymbol('Na')
        topology.addAtom('Na', element_Na, residue_Na)

        # Add Cl
        residue_Cl = topology.addResidue('Cl', chain)
        element_Cl = app.Element.getBySymbol('Cl')
        topology.addAtom('Cl', element_Cl, residue_Cl)

        self.topology = topology

        self.system, self.positions = system, positions
