import jax.numpy as jnp
from numpyro.distributions import Distribution, constraints
from .math_utils import custom_gammaincc, schechter_mag, SUPPORTED_ALPHA_DOMAIN_DEPTHS


class SchechterMag(Distribution):
    """
    NumPyro-compatible distribution based on the Schechter luminosity function in absolute magnitude space.

    This distribution models galaxy number densities using the Schechter parameterisation in magnitude space:
        φ(M) ∝ 10**[0.4(α + 1)(M* − M)] * exp[−10**(0.4(M* − M))]

    Normalisation is handled via a custom, recurrence-based computation of the upper incomplete gamma function,
    allowing support for automatic differentiation in JAX/NumPyro.

    Constraints:
    - `alpha` must be real and non-integer.
    - By default, the valid domain for `alpha + 1` is (−3, 3), corresponding to `alpha_domain_depth=3`. To support broader domains, increase `alpha_domain_depth` (see note).
    - `mag_obs` must contain values such that `10**(0.4(M_star − M)) > 0`.

    Note:
    To ensure compatibility with NUTS/HMC (which uses JAX's reverse-mode autodiff), only a fixed set of
    `alpha_domain_depth` values are supported.
    See `SchechterMag.supported_depths()` for available options (e.g., 3, 5, 10, 15).
    """

    support = constraints.real

    @property
    def has_rsample(self) -> bool:
        return False
    
    @staticmethod
    def supported_depths():
        """
        Returns a list of supported values for `alpha_domain_depth`, corresponding to increasing valid alpha ranges.
        Larger `alpha_domain_depth` will see reduced performance due to the corresponding increase in recursions.
        """
        return SUPPORTED_ALPHA_DOMAIN_DEPTHS

    def __init__(self, alpha, M_star, logphi, mag_obs, alpha_domain_depth=3, validate_args=None):
        self.alpha = alpha
        self.M_star = M_star
        self.logphi = logphi
        self.phi_star = jnp.exp(logphi)
        self.mag_obs = mag_obs
        self.alpha_domain_depth = alpha_domain_depth

        # Normalisation over observed magnitude range
        M_min, M_max = jnp.min(mag_obs), jnp.max(mag_obs)
        a = alpha + 1.0
        x_min = 10 ** (0.4 * (M_star - M_max))
        x_max = 10 ** (0.4 * (M_star - M_min))
        norm = self.phi_star * (custom_gammaincc(a, x_min, recur_depth=self.alpha_domain_depth) - custom_gammaincc(a, x_max, recur_depth=self.alpha_domain_depth))
        self.norm = jnp.where(norm > 0, norm, jnp.inf)

        super().__init__(batch_shape=(), event_shape=(), validate_args=validate_args)

    def __str__(self):
        return (
            f"SchechterMag distribution\n"
            f"  alpha = {self.alpha}\n"
            f"  M_star = {self.M_star}\n"
            f"  logphi = {self.logphi}\n"
            f"  alpha_domain_depth = {self.alpha_domain_depth}"
        )

    def __repr__(self):
        return str(self)

    def log_prob(self, value):
        pdf = schechter_mag(self.phi_star, self.M_star, self.alpha, value) / self.norm
        return jnp.log(pdf + 1e-30)

    def sample(self, key, sample_shape=()):
        raise NotImplementedError("Sampling not implemented for SchechterMag.")
