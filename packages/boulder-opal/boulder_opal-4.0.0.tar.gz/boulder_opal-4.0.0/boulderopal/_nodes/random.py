# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import numpy as np

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.node_data import Sequence as Sequence_
from boulderopal._nodes.node_data import (
    Stf,
    Tensor,
)
from boulderopal._nodes.validation import shapeable
from boulderopal._typing import Annotated
from boulderopal._validation import (
    Checker,
    ScalarT,
    pipe,
    validated,
)

if TYPE_CHECKING:
    from boulderopal.graph import Graph


class RandomGraph:  # pylint: disable=unused-argument
    """
    Base class implementing random graph methods.
    """

    def __init__(self, graph: "Graph") -> None:
        self._graph = graph

    @validated
    def colored_noise_stf_signal(
        self,
        power_spectral_density: Annotated[Union[np.ndarray, Tensor], pipe(shapeable)],
        frequency_step: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        batch_shape: Tuple[Annotated[int, pipe(ScalarT.INT().gt(0))], ...] = (),
        seed: Optional[Annotated[int, pipe(ScalarT.INT())]] = None,
    ) -> Stf:
        r"""
        Sample the one-sided power spectral density (PSD) of a random noise process in the
        time domain and returns the resultant noise trajectories as an Stf.

        Parameters
        ----------
        power_spectral_density : np.ndarray or Tensor (1D, real)
            The one-sided power spectral density of the noise sampled at frequencies
            :math:`\{0, \Delta f, 2\Delta f, \ldots , M\Delta f\}`.
        frequency_step : float
            The step size :math:`\Delta f` of power spectrum densities samples
           `power_spectral_density`. Must be a strictly positive number.
        batch_shape : list[int] or tuple[int], optional
            The batch shape of the returned Stf. By default, the batch shape is ``()``, that is,
            the returned Stf represents only one noise trajectory. If the batch shape is
            ``(m, n,...)``, the returned Stf represents `m*n*...` trajectories arranged in
            this batch shape.
        seed : int or None, optional
            A seed for the random number generator used for sampling. When set, same
            trajectories are produced on every run of this function, provided all the other
            arguments also remain unchanged. Defaults to None, in which case the
            generated noise trajectories can be different from one run to another.

        Returns
        -------
        Stf
            An `Stf` signal representing the noise trajectories in the time domain. The
            batch shape of this `Stf` is same as the argument `batch_shape`.

        Notes
        -----
        Given a frequency step size of :math:`\Delta f` and discrete samples
        :math:`P[k] = P(k\Delta f)` of a one-sided power spectral density function
        :math:`P(f)`, the output is a possibly batched Stf which represents one random
        realization of the random noise process. Each such trajectory is periodic with a
        time period of :math:`1/\Delta f`.

        Examples
        --------
        Create a PWC signal by sampling from a power spectral density function
        to define a noise Hamiltonian.

        >>> sigma_z = np.diag([1, -1])
        >>> frequency_step = 2e3
        >>> frequencies = np.arange(0, 2e6, frequency_step)
        >>> frequency_cutoff = 0.05e6
        >>> power_densities = 4e9 / (frequencies + frequency_cutoff)
        >>> noise_stf = graph.random.colored_noise_stf_signal(
        ...     power_spectral_density=power_densities, frequency_step=2000.0, batch_shape=(100,)
        ... )
        >>> noise_stf
        <Stf: operation_name="random_colored_noise_stf_signal", value_shape=(), batch_shape=(100,)>
        >>> noise_pwc = graph.discretize_stf(stf=noise_stf, duration=2e-6, segment_count=50)
        >>> noise_hamiltonian = noise_pwc * sigma_z
        >>> noise_hamiltonian
        <Pwc: name="multiply_#3", operation_name="multiply", value_shape=(2, 2), batch_shape=(100,)>

        Refer to the `How to simulate quantum dynamics subject to noise with graphs
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-quantum-dynamics-
        subject-to-noise-with-graphs>`_ user guide to find the example in context.
        """
        Checker.VALUE(
            len(power_spectral_density.shape) == 1,
            "The power spectral density must be 1D.",
        )

        operation = create_operation(
            self.colored_noise_stf_signal,
            locals(),
            graph=self._graph,
            name="random_colored_noise_stf_signal",
        )
        return Stf(operation, value_shape=(), batch_shape=batch_shape)

    @validated
    def normal(
        self,
        shape: Tuple[Annotated[int, pipe(ScalarT.INT().gt(0))], ...],
        mean: Annotated[float, pipe(ScalarT.REAL())],
        standard_deviation: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        seed: Optional[Annotated[int, pipe(ScalarT.INT())]] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a sample of normally distributed random numbers.

        Parameters
        ----------
        shape : tuple[int, ...]
            The shape of the sampled random numbers.
        mean : float
            The mean of the normal distribution.
        standard_deviation : float
            The standard deviation of the normal distribution.
        seed : int or None, optional
            A seed for the random number generator. Defaults to None,
            in which case a random value for the seed is used.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            A tensor containing a sample of normally distributed random numbers
            with shape ``shape``.

        See Also
        --------
        :func:`Graph.random.choices <random.choices>`
            Create random samples from the data that you provide.
        :func:`Graph.random.uniform <random.uniform>`
            Create a sample of uniformly distributed random numbers.
        :func:`boulderopal.run_stochastic_optimization`
            Function to find the minimum of generic stochastic functions.

        Examples
        --------
        Create a random tensor by sampling from a Gaussian distribution.

        >>> samples = graph.random.normal(
        ...     shape=(3, 1), mean=0.0, standard_deviation=0.05, seed=0, name="samples"
        ... )
        >>> result = bo.execute_graph(graph=graph, output_node_names="samples")
        >>> result["output"]["samples"]["value"]
        array([[-0.03171833], [0.00816805], [-0.06874011]])

        Create a batch of noise signals to construct a PWC Hamiltonian. The signal is defined
        as :math:`a \cos(\omega t)`, where :math:`a` follows a normal distribution and
        :math:`\omega` follows a uniform distribution.

        >>> seed = 0
        >>> batch_size = 3
        >>> sigma_x = np.array([[0, 1], [1, 0]])
        >>> sample_times = np.array([0.1, 0.2])
        >>> a = graph.random.normal((batch_size, 1), mean=0.0, standard_deviation=0.05, seed=seed)
        >>> omega = graph.random.uniform(
        ...     shape=(batch_size, 1), lower_bound=np.pi, upper_bound=2 * np.pi, seed=seed
        ... )
        >>> sampled_signal = a * graph.cos(omega * sample_times[None])
        >>> hamiltonian = graph.pwc_signal(sampled_signal, duration=0.2) * sigma_x
        >>> hamiltonian.name = "hamiltonian"
        >>> result = bo.execute_graph(graph=graph, output_node_names="hamiltonian")
        >>> result["output"]["hamiltonian"]
        {
            'durations': array([0.1, 0.1]),
            'values': array([
                [
                    [[-0.        , -0.02674376], [-0.02674376, -0.        ]],
                    [[-0.        , -0.01338043], [-0.01338043, -0.        ]]
                ],
                [
                    [[ 0.        ,  0.00691007], [ 0.00691007,  0.        ]],
                    [[ 0.        ,  0.00352363], [ 0.00352363,  0.        ]]],
                [
                    [[-0.        , -0.06230612], [-0.06230612, -0.        ]],
                    [[-0.        , -0.04420857], [-0.04420857, -0.        ]]
                ]
            ]),
            'time_dimension': 1
        }

        See more examples in the `How to optimize controls robust to strong noise sources
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-robust-
        to-strong-noise-sources>`_ user guide.
        """

        operation = create_operation(
            self.normal, locals(), self._graph, "random_normal"
        )
        return Tensor(operation, shape=tuple(shape))

    @validated
    def uniform(
        self,
        shape: Tuple[Annotated[int, pipe(ScalarT.INT().gt(0))], ...],
        lower_bound: Annotated[float, pipe(ScalarT.REAL())],
        upper_bound: Annotated[float, pipe(ScalarT.REAL())],
        seed: Optional[Annotated[int, pipe(ScalarT.INT())]] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a sample of uniformly distributed random numbers.

        Parameters
        ----------
        shape : tuple
            The shape of the sampled random numbers.
        lower_bound : float
            The inclusive lower bound of the interval of the uniform distribution.
        upper_bound : float
            The exclusive upper bound of the interval of the uniform distribution.
        seed : int or None, optional
            A seed for the random number generator. Defaults to None,
            in which case a random value for the seed is used.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            A tensor containing a sample of uniformly distributed random numbers
            with shape ``shape``.

        See Also
        --------
        :func:`Graph.random.choices <random.choices>`
            Create random samples from the data that you provide.
        :func:`Graph.random.normal <random.normal>`
            Create a sample of normally distributed random numbers.
        :func:`boulderopal.run_stochastic_optimization`
            Function to find the minimum of generic stochastic functions.

        Examples
        --------
        Create a random tensor by sampling uniformly from :math:`[0,\, 1)`.

        >>> samples = graph.random.uniform(
        ...     shape=(3, 1), lower_bound=0, upper_bound=1, seed=0, name="samples"
        ... )
        >>> result = bo.execute_graph(graph=graph, output_node_names="samples")
        >>> result["output"]["samples"]["value"]
        array([[0.8069013], [0.79011373], [0.38818516]])

        See more examples in the `How to optimize controls robust to strong noise sources
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-
        robust-to-strong-noise-sources>`_ user guide.
        """
        Checker.VALUE(
            lower_bound < upper_bound,
            "The lower bound must be smaller than the upper bound.",
            {"lower_bound": lower_bound, "upper_bound": upper_bound},
        )

        operation = create_operation(
            self.uniform, locals(), self._graph, "random_uniform"
        )
        return Tensor(operation, shape=shape)

    @validated
    def choices(
        self,
        data: List[Annotated[Union[np.ndarray, Tensor], pipe(shapeable)]],
        sample_count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        seed: Optional[Annotated[int, pipe(ScalarT.INT())]] = None,
        *,
        name: Optional[str] = None,
    ) -> Sequence[Tensor]:
        r"""
        Create random samples from the data that you provide.

        You can provide the data as a list and each element of that list represents one component
        of the full data. For example, considering a single variable linear regression problem
        that is described by the input :math:`x` and output :math:`y`, the data you provide would
        be :math:`[x, y]`. The first dimension of the data component in this list is the size of
        the data and therefore must be same for all components. However, all these components can
        have different value shapes, meaning the other dimensions can vary.

        This node effectively chooses a random batch of `sample_count` indices :math:`\{s_i\}`,
        and extracts the corresponding slices :math:`\{c[s_i]\}` of each data component.
        For example, in the case of linear regression, you can use this node to extract a random
        subset of your full data set.

        If this node is evaluated multiple times (for example during an optimization), it samples
        indices without replacement until all indices have been seen, at which point it starts
        sampling from the full set of indices again. You can therefore use this node to create
        minibatches that iterate over your data set in a series of epochs.

        Parameters
        ----------
        data : list[np.ndarray or Tensor]
            A list of data components. The first dimensions of the elements in this
            list denote the total amount of the data, and therefore must be the same.
        sample_count : int
            Number of samples in the returned batch.
        seed : int or None, optional
            Seed for random number generator. Defaults to None. If set, it ensures the
            random samples are generated in a reproducible sequence.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Sequence[Tensor]
            A sequence representing a batch of random samples from `data`.
            You can access the elements of the sequence using integer indices.
            The number of elements of the sequence is the same as the size of `data`.
            Each element of the sequence has the length (along its first dimension)
            as defined by `sample_count`.

        See Also
        --------
        :func:`Graph.random.normal <random.normal>`
            Create a sample of normally distributed random numbers.
        :func:`Graph.random.uniform <random.uniform>`
            Create a sample of uniformly distributed random numbers.
        :func:`boulderopal.run_stochastic_optimization`
            Function to find the minimum of generic stochastic functions.

        Examples
        --------
        >>> x = np.arange(20).reshape((10, 2))
        >>> y = np.arange(10) * 0.2
        >>> sampled_x, sampled_y = graph.random.choices([x, y], 3, seed=1)
        >>> sampled_x.name = "sampled_x"
        >>> sampled_y.name = "sampled_y"
        >>> result = bo.execute_graph(graph=graph, output_node_names=["sampled_x", "sampled_y"])
        >>> result["output"]["sampled_x"]["value"]
        array([[2, 3], [6, 7], [0, 1]])
        >>> result["output"]["sampled_y"]["value"]
        array([0.2, 0.6, 0. ])

        See more examples in the `How to perform Hamiltonian parameter estimation using a large
        amount of measured data
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-perform-parameter-estimation-
        with-a-large-amount-of-data>`_ user guide.
        """
        data_size = data[0].shape[0]
        Checker.VALUE(
            all(value.shape[0] == data_size for value in data),
            "The first dimension of the elements in data must be the same.",
            {"data": data},
        )
        Checker.VALUE(
            sample_count <= data_size,
            "The sample_count must be not greater than the size of the data you provide.",
            {"sample_count": sample_count, "data size": data_size},
        )

        return_tensor_shapes = [(sample_count,) + value.shape[1:] for value in data]
        operation = create_operation(
            self.choices, locals(), self._graph, "random_choices"
        )
        return Sequence_(operation).create_sequence(
            node_constructor=lambda operation, index: Tensor(
                operation, return_tensor_shapes[index]
            ),
            size=len(data),
        )
