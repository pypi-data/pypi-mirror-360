"""An experimental module for reparameterizations of orbital elements."""

import jax

jax.config.update("jax_enable_x64", True)

from functools import partial

import jax.numpy as jnp

from jorbit.utils.kepler import M_from_f, kepler


@jax.jit
def square_to_unit_disk(a: float, b: float) -> tuple[float, float]:
    """Map two points in the unit square to the unit disk.

    Implements the algorithm from `Shirley & Chiu 1997 <https://doi.org/10.1080/10867651.1997.10487479>`_.

    Args:
        a (float):
            x-coordinate in the unit square.
        b (float):
            y-coordinate in the unit square.

    Returns:
        tuple[float, float]:
            (r, phi) in the unit disk.
    """
    # https://doi.org/10.1080/10867651.1997.10487479
    a = 2 * a - 1
    b = 2 * b - 1

    flag1 = a > -b
    flag2 = a > b
    flag3 = a < b

    r = (
        (a * flag1 * flag2)
        + (b * flag1 * ~flag2)
        + (-a * ~flag1 * flag3)
        + (-b * ~flag1 * ~flag3)
    )
    phi = (
        (((jnp.pi / 4) * (b / a)) * flag1 * flag2)
        + ((jnp.pi / 4) * (2 - (a / b)) * flag1 * ~flag2)
        + ((jnp.pi / 4) * (4 + (b / a)) * ~flag1 * flag3)
        + ((jnp.pi / 4) * (6 - (a / b)) * ~flag1 * ~flag3)
    )

    return r, phi


@jax.jit
def unit_disk_to_square(r: float, phi: float) -> tuple[float, float]:
    """Map two points in the unit disk to the unit square.

    Implements the algorithm from `Shirley & Chiu 1997 <https://doi.org/10.1080/10867651.1997.10487479>`_.

    Args:
        r (float):
            Radius in the unit disk.
        phi (float):
            Angle in the unit disk.

    Returns:
        tuple[float, float]:
            (x, y) in the unit square.
    """
    # inverse of square_to_unit_disk
    cond1 = (phi <= jnp.pi / 4) | (phi > 7 * jnp.pi / 4)
    cond2 = (phi > jnp.pi / 4) & (phi <= 3 * jnp.pi / 4)
    cond3 = (phi > 3 * jnp.pi / 4) & (phi <= 5 * jnp.pi / 4)
    cond4 = (phi > 5 * jnp.pi / 4) & (phi <= 7 * jnp.pi / 4)

    A = jnp.zeros_like(r)
    B = jnp.zeros_like(r)

    phi1 = jnp.where(phi > 7 * jnp.pi / 4, phi - 2 * jnp.pi, phi)
    A = jnp.where(cond1, r, A)
    B = jnp.where(cond1, (4 * r / jnp.pi) * phi1, B)

    A = jnp.where(cond2, r * (2 - (4 / jnp.pi) * phi), A)
    B = jnp.where(cond2, r, B)

    A = jnp.where(cond3, -r, A)
    B = jnp.where(cond3, r * (4 - (4 / jnp.pi) * phi), B)

    A = jnp.where(cond4, r * ((4 / jnp.pi) * phi - 6), A)
    B = jnp.where(cond4, -r, B)

    a = (A + 1) / 2
    b = (B + 1) / 2

    return a, b


@partial(jax.jit, static_argnums=(3))
def unit_cube_to_orbital_elements(
    u: jnp.ndarray, a_low: float, a_high: float, uniform_inc: bool
) -> jnp.ndarray:
    """Map six points in the unit cube to orbital elements.

    One potential mapping from the unit cube to orbital elements. This particular one
    samples in sqrt(e)*cos(omega), sqrt(e)*sin(omega), sin(i/2)sin(Omega),
    sin(i/2)cos(Omega), log(a), and mean longitude. The goal was to a) avoid periodic
    parameters for mcmc and b) keep everything in the unit cube for nested sampling.

    Args:
        u (jnp.ndarray):
            Six points in the unit cube.
        a_low (float):
            Lower bound on the semi-major axis.
        a_high (float):
            Upper bound on the semi-major axis.
        uniform_inc (bool):
            Whether to use uniform inclination. If not, uses uniform in cos(i)

    Returns:
        jnp.ndarray:
            Orbital elements.
    """
    _r, _theta = square_to_unit_disk(u[0], u[1])
    _r = _r**2  # this gives us uniform e
    h = _r * jnp.cos(_theta)
    k = _r * jnp.sin(_theta)
    e = _r
    omega = jnp.arctan2(h, k) + jnp.pi

    _r, _theta = square_to_unit_disk(u[2], u[3])
    if uniform_inc:
        _r = jnp.sin(jnp.pi * _r**2 / 2)  # this gives us uniform i
    p = _r * jnp.cos(_theta)
    q = _r * jnp.sin(_theta)
    i = 2 * jnp.arcsin(_r)
    Omega = jnp.arctan2(q, p) + jnp.pi

    _r, _theta = square_to_unit_disk(u[4], u[5])
    a = jnp.exp(jnp.log(a_low) + (jnp.log(a_high) - jnp.log(a_low)) * _r**2)
    # helio_r = jnp.exp(jnp.log(a_low) + (jnp.log(a_high) - jnp.log(a_low)) * _r**2)
    lamb = _theta
    lamb = jnp.where(lamb < 0, lamb + 2 * jnp.pi, lamb)
    M = lamb - omega - Omega
    M = jnp.where(M < 0, M + 2 * jnp.pi, M)
    f = kepler(M, e)
    # a = helio_r * (1 + e * jnp.cos(f)) / (1 - e**2)

    return jnp.array(
        [
            a,
            e,
            i * 180 / jnp.pi,
            Omega * 180 / jnp.pi,
            omega * 180 / jnp.pi,
            f * 180 / jnp.pi,
        ]
    )


@partial(jax.jit, static_argnums=(3))
def orbital_elements_to_unit_cube(
    orb: jnp.ndarray, a_low: float, a_high: float, uniform_inc: bool
) -> jnp.ndarray:
    """The inverse mapping of unit_cube_to_orbital_elements.

    Again, just one potential mapping from orbital elements to the unit cube.

    Args:
        orb (jnp.ndarray):
            Orbital elements in a, e, i, Omega, omega, f order.
        a_low (float):
            Lower bound on the semi-major axis.
        a_high (float):
            Upper bound on the semi-major axis.
        uniform_inc (bool):
            Whether to use uniform inclination. If not, uses uniform in cos(i)

    Returns:
        jnp.ndarray:
            Six points in the unit cube.
    """
    a, e, i, Omega, omega, f = orb
    i = i * jnp.pi / 180
    Omega = Omega * jnp.pi / 180
    omega = omega * jnp.pi / 180
    f = f * jnp.pi / 180

    theta1 = 3 * jnp.pi / 2 - omega
    theta1 = jnp.where(theta1 < 0, theta1 + 2 * jnp.pi, theta1)
    r1 = jnp.sqrt(e)
    u0, u1 = unit_disk_to_square(r1, theta1)

    r2 = jnp.sin(i / 2)
    if uniform_inc:
        r2 = jnp.sqrt(2 / jnp.pi) * jnp.sqrt(jnp.arcsin(r2))
    theta2 = Omega - jnp.pi
    theta2 = jnp.where(theta2 < 0, theta2 + 2 * jnp.pi, theta2)
    u2, u3 = unit_disk_to_square(r2, theta2)

    r3 = (jnp.log(a) - jnp.log(a_low)) / (jnp.log(a_high) - jnp.log(a_low))
    r3 = jnp.sqrt(r3)
    # helio_r = a * (1-e**2) / (1 + e * jnp.cos(f))
    # r3 = (jnp.log(helio_r) - jnp.log(a_low)) / (jnp.log(a_high) - jnp.log(a_low))
    # r3 = jnp.sqrt(r3)

    M = M_from_f(f, e)  # This function must be provided.
    lamb = M + omega + Omega
    lamb = jnp.where(lamb < 0, lamb + 2 * jnp.pi, lamb)
    lamb = jnp.mod(lamb, 2 * jnp.pi)
    u4, u5 = unit_disk_to_square(r3, lamb)

    return jnp.array([u0, u1, u2, u3, u4, u5])
