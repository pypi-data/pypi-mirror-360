# ===================================================
#
#    Copyright (c) 2023-2024
#      SPARKX Team
#
#    GNU General Public License (GPLv3 or later)
#
# ===================================================

from sparkx.flow import FlowInterface
from sparkx.Particle import Particle
import numpy as np
from typing import List, Union


class ReactionPlaneFlow(FlowInterface.FlowInterface):
    """
    This class implements a reaction plane flow analysis algorithm.

    For this method, the flow is calculated under the assumption that the
    reaction plane angle is constant throughout all events, i.e., the impact
    parameter is always oriented in the same direction.
    The flow is calculated as

    .. math::

        v_n = \\left\\langle \\exp{in\\phi_i}\\right\\rangle,

    where we average over all particles of all events. We return complex
    numbers, which contain the information about the magnitude and the angle.
    If a weight is set for the particles in the `Particle` objects, then this
    is used in the flow calculation.


    Parameters
    ----------
    n : int, optional
        The value of the harmonic. Default is 2.


    Methods
    -------
    integrated_flow:
        Computes the integrated flow.
    differential_flow:
        Computes the differential flow.

    Examples
    --------

    A demonstration how to calculate flow with the reaction plane method.

    .. highlight:: python
    .. code-block:: python
        :linenos:

        >>> from sparkx.Jetscape import Jetscape
        >>> from sparkx.flow.ReactionPlaneFlow import ReactionPlaneFlow
        >>>
        >>> JETSCAPE_FILE_PATH_FLOW = [Jetscape_directory]/particle_lists_flow.dat

        >>> # Jetscape object containing the particles on which we want to calculate flow
        >>> jetscape_flow = Jetscape(JETSCAPE_FILE_PATH_FLOW)
        >>>
        >>> # Create flow objects for v2
        >>> flow2 = ReactionPlaneFlow(n=2).particle_objects_list()
        >>>
        >>> # Calculate the integrated flow with error
        >>> v2 = flow2.integrated_flow(jetscape_flow)
        >>>
        >>> # Calculate the differential flow with error
        >>> pT_bins = [0.0,0.5,1.0,2.0,3.0,4.0]
        >>> v2_differential = flow2.integrated_flow(jetscape_flow,pT_bins,'pT')

    """

    def __init__(self, n: int = 2) -> None:
        """
        Initialize the ReactionPlaneFlow object.

        Parameters
        ----------
        n : int, optional
            The value of the harmonic. Default is 2.
        """
        if not isinstance(n, int):
            raise TypeError("n has to be int")
        elif n <= 0:
            raise ValueError(
                "n-th harmonic with value n<=0 can not be computed"
            )
        else:
            self.n_ = n

    def integrated_flow(self, particle_data: List[List[Particle]]) -> complex:
        """
        Compute the integrated flow.

        Parameters
        ----------
        particle_data : list
            List of particle data.

        Returns
        -------
        complex
            The integrated flow value, represented as a complex number.
        """
        flow_event_average = 0.0 + 0.0j
        number_particles = 0.0
        for event in range(len(particle_data)):
            flow_event = 0.0 + 0.0j
            for particle in range(len(particle_data[event])):
                weight = (
                    1.0
                    if np.isnan(particle_data[event][particle].weight)
                    else particle_data[event][particle].weight
                )
                phi = particle_data[event][particle].phi()
                flow_event += weight * np.exp(1j * self.n_ * phi)
                number_particles += weight
            if number_particles != 0.0:
                flow_event_average += flow_event
            else:
                flow_event_average = 0.0 + 0.0j
        flow_event_average /= number_particles
        return flow_event_average

    def differential_flow(
        self,
        particle_data: List[List[Particle]],
        bins: Union[np.ndarray, List[float]],
        flow_as_function_of: str,
    ) -> List[complex]:
        """
        Compute the differential flow.

        Parameters
        ----------
        particle_data : list
            List of particle data.
        bins : list or np.ndarray
            Bins used for the differential flow calculation.
        flow_as_function_of : str
            Variable on which the flow is calculated ("pT", "rapidity", or "pseudorapidity").

        Returns
        -------
        list
            A list of complex numbers representing the flow values for each bin.
        """
        if not isinstance(bins, (list, np.ndarray)):
            raise TypeError("bins has to be list or np.ndarray")
        if not isinstance(flow_as_function_of, str):
            raise TypeError("flow_as_function_of is not a string")
        if flow_as_function_of not in ["pT", "rapidity", "pseudorapidity"]:
            raise ValueError(
                "flow_as_function_of must be either 'pT', 'rapidity', 'pseudorapidity'"
            )

        particles_bin = []
        for bin in range(len(bins) - 1):
            events_bin = []
            for event in range(len(particle_data)):
                particles_event = []
                for particle in particle_data[event]:
                    val = 0.0
                    if flow_as_function_of == "pT":
                        val = particle.pT_abs()
                    elif flow_as_function_of == "rapidity":
                        val = particle.rapidity()
                    elif flow_as_function_of == "pseudorapidity":
                        val = particle.pseudorapidity()
                    if val >= bins[bin] and val < bins[bin + 1]:
                        particles_event.append(particle)
                events_bin.extend([particles_event])
            particles_bin.extend([events_bin])

        return self.__differential_flow_calculation(particles_bin)

    def __differential_flow_calculation(
        self, binned_particle_data: List[List[List[Particle]]]
    ) -> List[complex]:
        flow_differential = [
            0.0 + 0.0j for i in range(len(binned_particle_data))
        ]
        for bin in range(len(binned_particle_data)):
            number_particles = 0.0
            flow_event_average = 0.0 + 0.0j
            for event in range(len(binned_particle_data[bin])):
                flow_event = 0.0 + 0.0j
                for particle in range(len(binned_particle_data[bin][event])):
                    weight = (
                        1.0
                        if np.isnan(
                            binned_particle_data[bin][event][particle].weight
                        )
                        else binned_particle_data[bin][event][particle].weight
                    )
                    phi = binned_particle_data[bin][event][particle].phi()
                    flow_event += weight * np.exp(1j * self.n_ * phi)
                    number_particles += weight
                flow_event_average += flow_event
            if number_particles != 0.0:
                flow_event_average /= number_particles
            else:
                flow_event_average = 0.0 + 0.0j
            flow_differential[bin] = flow_event_average
        return flow_differential
