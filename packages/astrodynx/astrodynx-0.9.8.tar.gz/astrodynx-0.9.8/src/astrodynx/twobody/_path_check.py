from jax import numpy as jnp
from jax import Array
from jax.typing import ArrayLike, DTypeLike
import astrodynx as adx
from jax.numpy.linalg import vector_norm


def nmax_by_periapsis(
    rp_min: DTypeLike = 0.97,
    r1: DTypeLike = 1.0,
    r2: DTypeLike = 1.0,
    tof: DTypeLike = jnp.pi,
    mu: DTypeLike = 1,
) -> Array:
    r"""Returns the maximum number of revolutions that can occur between two points in an orbit, given the minimum periapsis radius.

    Args:
        rp_min: The minimum periapsis radius.
        r1: The radius at the first point.
        r2: The radius at the second point.
        tof: The time of flight between the two points.
        mu: The gravitational parameter.

    Returns:
        The maximum number of revolutions that can occur between the two points.

    Notes:
        The maximum number of revolutions is calculated using the formula:
        $$
        N_{max} = \left\lfloor \frac{T}{2\pi} \sqrt{\frac{\mu}{a_{min}^3}} \right\rfloor
        $$
        where $N_{max}$ is the maximum number of revolutions, $T$ is the time of flight, $\mu$ is the gravitational parameter, and $a_{min}$ is the minimum semimajor axis:
        $$
        a_{min} = \frac{1}{2} \left( \max(r_1, r_2) + r_{p_{min}} \right)
        $$
        where $r_1$ and $r_2$ are the radii at the two points, and $r_{p_{min}}$ is the minimum periapsis radius.

    References:
        Battin, 1999, pp.184.

    Examples:
        A simple example:

        >>> import jax.numpy as jnp
        >>> import astrodynx as adx
        >>> rp_min = 0.97
        >>> r1 = 1.0
        >>> r2 = 1.0
        >>> tof = jnp.pi
        >>> mu = 1.0
        >>> adx.twobody.nmax_by_periapsis(rp_min, r1, r2, tof, mu)
        Array(0., dtype=float32, weak_type=True)
    """
    amin = 0.5 * (jnp.maximum(r1, r2) + rp_min)
    return jnp.floor(tof / (2 * jnp.pi) * jnp.sqrt(mu / amin**3))


def is_short_way(r1: ArrayLike, v1: ArrayLike, r2: ArrayLike) -> Array:
    r"""Returns True if the short way between two points in an orbit is taken.

    Args:
        r1: (3,) The position vector at the first point.
        v1: (3,) The velocity vector at the first point.
        r2: (3,) The position vector at the second point.

    Returns:
        True if the short way between the two points is taken, False otherwise.

    Notes:
        The short way is taken only if:
        $$
        (\boldsymbol{r}_1 \times \boldsymbol{v}_1) \cdot (\boldsymbol{r}_1 \times \boldsymbol{r}_2) > 0
        $$

    Examples:
        A simple example:

        >>> import jax.numpy as jnp
        >>> import astrodynx as adx
        >>> r1 = jnp.array([1.0, 0.0, 0.0])
        >>> v1 = jnp.array([0.0, 1.0, 0.0])
        >>> r2 = jnp.array([0.0, 1.0, 0.0])
        >>> adx.twobody.is_short_way(r1, v1, r2)
        Array(True, dtype=bool)
    """
    return jnp.inner(jnp.cross(r1, v1), jnp.cross(r1, r2)) > 0


def pass_perigee(
    r1: ArrayLike, v1: ArrayLike, r2: ArrayLike, mu: DTypeLike = 1
) -> Array:
    r"""Returns True if the orbit passes through perigee between two points.

    Args:
        r1: (3,) The position vector at the first point.
        v1: (3,) The velocity vector at the first point.
        r2: (3,) The position vector at the second point.
        mu: (optional) The gravitational parameter.

    Returns:
        True if the orbit passes through perigee between the two points, False otherwise.

    Notes:
        Let's define
        $$
        \boldsymbol{b}_1 = (\boldsymbol{r}_1 \times \boldsymbol{r}_2) \cdot (\boldsymbol{r}_1 \times \boldsymbol{e}) > 0
        $$
        and
        $$
        \boldsymbol{b}_2 = (\boldsymbol{r}_1 \times \boldsymbol{r}_2) \cdot (\boldsymbol{e} \times \boldsymbol{r}_2) > 0
        $$
        where $\boldsymbol{e}$ is the eccentricity vector.
        Then, the orbit passes through perigee if:
        $$
        \boldsymbol{b}_1 \land \boldsymbol{b}_2 = \text{is_short_way}(\boldsymbol{r}_1, \boldsymbol{v}_1, \boldsymbol{r}_2)
        $$


    Examples:
        A simple example:

        >>> import jax.numpy as jnp
        >>> import astrodynx as adx
        >>> r1 = jnp.array([1.0, 0.0, 0.0])
        >>> v1 = jnp.array([0.0, 1.0, 0.0])
        >>> r2 = jnp.array([0.0, 1.0, 0.0])
        >>> adx.twobody.pass_perigee(r1, v1, r2)
        Array(False, dtype=bool)
    """
    e = adx.eccentricity_vector(r1, v1, mu)
    b1 = jnp.inner(jnp.cross(r1, r2), jnp.cross(r1, e)) > 0
    b2 = jnp.inner(jnp.cross(r1, r2), jnp.cross(e, r2)) > 0
    return jnp.logical_and(b1, b2) == is_short_way(r1, v1, r2)


def rp_islower_rmin(
    rmin: DTypeLike, r: ArrayLike, v: ArrayLike, mu: DTypeLike = 1
) -> Array:
    r"""Returns True if the periapsis radius is lower than the minimum radius.

    Args:
        rmin: The minimum radius.
        r: (3,) The position vector.
        v: (3,) The velocity vector.
        mu: (optional) The gravitational parameter.

    Returns:
        True if the periapsis radius is lower than the minimum radius, False otherwise.

    Examples:
        A simple example:

        >>> import jax.numpy as jnp
        >>> import astrodynx as adx
        >>> rmin = 0.97
        >>> r = jnp.array([1.0, 0.0, 0.0])
        >>> v = jnp.array([0.0, 1.0, 0.0])
        >>> adx.twobody.rp_islower_rmin(rmin, r, v)
        Array(False, dtype=bool)
    """
    p = adx.semiparameter(vector_norm(adx.angular_momentum(r, v)), mu)
    e = vector_norm(adx.eccentricity_vector(r, v, mu))
    return adx.radius_periapsis(p, e) < rmin
