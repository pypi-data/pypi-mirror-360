"""Handles accelerations that can be used in the integrator."""

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp

from jorbit.accelerations.gr import ppn_gravity
from jorbit.accelerations.grav_harmonics import grav_harmonics
from jorbit.accelerations.newtonian import newtonian_gravity
from jorbit.accelerations.nongrav import nongrav_acceleration
from jorbit.ephemeris.ephemeris_processors import EphemerisProcessor
from jorbit.utils.states import SystemState

__all__ = [
    "create_default_ephemeris_acceleration_func",
    "create_ephem_grav_harmonics_acceleration_func",
    "create_gr_ephemeris_acceleration_func",
    "create_newtonian_ephemeris_acceleration_func",
    "nongrav_acceleration",
]


def create_newtonian_ephemeris_acceleration_func(
    ephem_processor: EphemerisProcessor,
) -> jax.tree_util.Partial:
    """Create and return a function that adds newtonian gravity from fixed perturbers.

    Args:
        ephem_processor (EphemerisProcessor): The ephemeris processor that will provide
            the perturber positions and velocities.

    Returns:
        A jax.tree_util.Partial function that takes a SystemState and returns the
            accelerations due to the perturbers.

    """

    def func(inputs: SystemState) -> jnp.ndarray:
        perturber_xs, perturber_vs = ephem_processor.state(inputs.time)
        perturber_log_gms = ephem_processor.log_gms

        new_state = SystemState(
            massive_positions=jnp.concatenate([perturber_xs, inputs.massive_positions]),
            massive_velocities=jnp.concatenate(
                [perturber_vs, inputs.massive_velocities]
            ),
            tracer_positions=inputs.tracer_positions,
            tracer_velocities=inputs.tracer_velocities,
            log_gms=jnp.concatenate([perturber_log_gms, inputs.log_gms]),
            time=inputs.time,
            acceleration_func_kwargs=inputs.acceleration_func_kwargs,
        )

        accs = newtonian_gravity(new_state)

        num_perturbers = perturber_xs.shape[0]
        return accs[num_perturbers:]

    return jax.tree_util.Partial(func)


def create_gr_ephemeris_acceleration_func(
    ephem_processor: EphemerisProcessor,
) -> jax.tree_util.Partial:
    """Create and return a function that adds gr gravity from fixed perturbers.

    Args:
        ephem_processor (EphemerisProcessor): The ephemeris processor that will provide
            the perturber positions and velocities.

    Returns:
        A jax.tree_util.Partial function that takes a SystemState and returns the
            accelerations due to the perturbers.

    """

    def func(inputs: SystemState) -> jnp.ndarray:
        perturber_xs, perturber_vs = ephem_processor.state(inputs.time)
        perturber_log_gms = ephem_processor.log_gms

        new_state = SystemState(
            massive_positions=jnp.concatenate([perturber_xs, inputs.massive_positions]),
            massive_velocities=jnp.concatenate(
                [perturber_vs, inputs.massive_velocities]
            ),
            tracer_positions=inputs.tracer_positions,
            tracer_velocities=inputs.tracer_velocities,
            log_gms=jnp.concatenate([perturber_log_gms, inputs.log_gms]),
            time=inputs.time,
            acceleration_func_kwargs=inputs.acceleration_func_kwargs,
        )

        accs = ppn_gravity(new_state)

        num_perturbers = perturber_xs.shape[0]
        return accs[num_perturbers:]

    return jax.tree_util.Partial(func)


def create_default_ephemeris_acceleration_func(
    ephem_processor: EphemerisProcessor,
) -> jax.tree_util.Partial:
    """Create and return a function that adds gravity from fixed perturbers for the default ephemeris.

    This adds GR corrections for the 10 planets and newtonian corrections for the 16
    asteroids.

    Args:
        ephem_processor (EphemerisProcessor): The ephemeris processor that will provide
            the perturber positions and velocities.

    Returns:
        A jax.tree_util.Partial function that takes a SystemState and returns the
            accelerations due to the perturbers.

    """

    def func(inputs: SystemState) -> jnp.ndarray:
        num_gr_perturbers = 11  # the "planets", including the sun, moon, and pluto
        num_newtonian_perturbers = 16  # the asteroids

        perturber_xs, perturber_vs = ephem_processor.state(inputs.time)
        perturber_log_gms = ephem_processor.log_gms

        gr_state = SystemState(
            massive_positions=jnp.concatenate(
                [perturber_xs[:num_gr_perturbers], inputs.massive_positions]
            ),
            massive_velocities=jnp.concatenate(
                [perturber_vs[:num_gr_perturbers], inputs.massive_velocities]
            ),
            tracer_positions=inputs.tracer_positions,
            tracer_velocities=inputs.tracer_velocities,
            log_gms=jnp.concatenate(
                [perturber_log_gms[:num_gr_perturbers], inputs.log_gms]
            ),
            time=inputs.time,
            acceleration_func_kwargs=inputs.acceleration_func_kwargs,
        )
        gr_acc = ppn_gravity(gr_state)[num_gr_perturbers:]

        newtonian_state = SystemState(
            massive_positions=jnp.concatenate(
                [perturber_xs[num_gr_perturbers:], inputs.massive_positions]
            ),
            massive_velocities=jnp.concatenate(
                [perturber_vs[num_gr_perturbers:], inputs.massive_velocities]
            ),
            tracer_positions=inputs.tracer_positions,
            tracer_velocities=inputs.tracer_velocities,
            log_gms=jnp.concatenate(
                [perturber_log_gms[num_gr_perturbers:], inputs.log_gms]
            ),
            time=inputs.time,
            acceleration_func_kwargs=inputs.acceleration_func_kwargs,
        )
        newtonian_acc = newtonian_gravity(newtonian_state)[num_newtonian_perturbers:]

        return gr_acc + newtonian_acc

    return jax.tree_util.Partial(func)


def create_ephem_grav_harmonics_acceleration_func(
    ephem_processor: EphemerisProcessor, ephem_index: int, state_index: int
) -> jax.tree_util.Partial:
    """Create and return a function that computes gravitational harmonics from a perturber sourced from an Ephemeris.

    Args:
        ephem_processor (EphemerisProcessor): The ephemeris processor that will provide
            the perturber positions and velocities.
        ephem_index (int): The index of the perturber from the EphemerisProcessor output.
        state_index (int): The index of the state in the acceleration function kwargs.

    Returns:
        A jax.tree_util.Partial function that takes a SystemState and returns the
            gravitational harmonics acceleration.

    """

    def func(inputs: SystemState) -> jnp.ndarray:
        perturber_xs, _ = ephem_processor.state(inputs.time)
        perturber_log_gms = ephem_processor.log_gms

        xs = jnp.concatenate((inputs.massive_positions, inputs.tracer_positions))

        return grav_harmonics(
            body_gm=jnp.exp(perturber_log_gms[ephem_index]),
            body_req=inputs.acceleration_func_kwargs["js_req"][state_index],
            body_pos=perturber_xs[ephem_index],
            pole_ra=inputs.acceleration_func_kwargs["js_pole_ra"][state_index],
            pole_dec=inputs.acceleration_func_kwargs["js_pole_dec"][state_index],
            jns=inputs.acceleration_func_kwargs["js"][state_index],
            particle_xs=xs,
        )

    return jax.tree_util.Partial(func)
