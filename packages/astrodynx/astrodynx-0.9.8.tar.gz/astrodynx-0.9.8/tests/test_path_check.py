import jax.numpy as jnp
from astrodynx.twobody import pass_perigee


class TestPassPerigee:
    r1 = jnp.array([8081.226263, -0.0, -0.0])
    v1 = jnp.array([-0.440773, 7.6, 0.133593])
    mu = 3.986e5

    def test_pass_perigee1(self):
        r2 = jnp.array([7902.679945, 1371.949935, 23.947475])
        assert not pass_perigee(self.r1, self.v1, r2, self.mu)
        assert pass_perigee(self.r1, -self.v1, r2, self.mu)

    def test_pass_perigee2(self):
        r2 = jnp.array([-10664.744693, 3855.689988, 67.301319])
        assert pass_perigee(self.r1, self.v1, r2, self.mu)
        assert not pass_perigee(self.r1, -self.v1, r2, self.mu)

    def test_pass_perigee3(self):
        r2 = jnp.array([-3746.681531, -10353.987124, -180.729518])
        assert pass_perigee(self.r1, self.v1, r2, self.mu)
        assert not pass_perigee(self.r1, -self.v1, r2, self.mu)

    def test_pass_perigee4(self):
        r2 = jnp.array([6742.310614, -5513.347909, -96.235846])
        assert pass_perigee(self.r1, self.v1, r2, self.mu)
        assert not pass_perigee(self.r1, -self.v1, r2, self.mu)

    def test_basic_case(self) -> None:
        """Test with a basic circular orbit case."""
        r1 = jnp.array([1.0, 0.0, 0.0])
        v1 = jnp.array([0.0, 1.0, 0.0])
        r2 = jnp.array([0.0, 1.0, 0.0])
        assert not pass_perigee(r1, v1, r2)

    def test_elliptical_orbit(self) -> None:
        """Test with an elliptical orbit where perigee is passed."""
        # Create an elliptical orbit with e=0.5
        r1 = jnp.array([1.5, 0.0, 0.0])  # Starting at apogee
        v1 = jnp.array([0.0, 0.8, 0.0])  # Velocity for elliptical orbit
        r2 = jnp.array([-1.0, 0.0, 0.0])  # Position after passing perigee
        assert pass_perigee(r1, v1, r2)
