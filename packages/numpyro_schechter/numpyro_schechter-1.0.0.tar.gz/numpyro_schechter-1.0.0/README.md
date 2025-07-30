# numpyro_schechter

**Schechter galaxy luminosity distribution for NumPyro**

<p align="center">
  <img src="https://raw.githubusercontent.com/alserene/numpyro_schechter/main/docs/assets/logo.png" alt="Schechter distribution logo for numpyro_schechter" width="300"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/numpyro-schechter/">
    <img src="https://img.shields.io/pypi/pyversions/numpyro-schechter.svg" alt="Python Versions">
  </a>
  <a href="https://numpyro-schechter.readthedocs.io/en/latest/?badge=latest">
    <img src="https://readthedocs.org/projects/numpyro-schechter/badge/?version=latest" alt="Docs Status">
  </a>
  <a href="https://pypi.org/project/numpyro-schechter/">
    <img src="https://img.shields.io/pypi/v/numpyro-schechter.svg" alt="PyPI">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  </a>
  <a href="https://github.com/alserene/numpyro_schechter/actions/workflows/tests.yml">
    <img src="https://github.com/alserene/numpyro_schechter/actions/workflows/tests.yml/badge.svg" alt="Tests">
  </a>
</p>

---

## Overview

`numpyro_schechter` provides a NumPyro-compatible probability distribution for Bayesian inference with Schechter luminosity functions in absolute magnitude space.

Built for astronomers and statisticians, it includes a JAX-compatible, differentiable implementation of the upper incomplete gamma function, enabling stable and efficient modelling in probabilistic programming frameworks.

---

## Parameter Constraints

Due to the custom normalisation logic, some constraints apply:

- `alpha` must be real and non-integer.
- The valid range of `alpha + 1` depends on `alpha_domain_depth`. By default, `alpha_domain_depth=3`, which supports the domain `-3 < alpha + 1 < 3`.
- To model more extreme values of `alpha`, increase the `alpha_domain_depth` parameter (see below).
- The list of valid depths is fixed and can be queried programmatically:
  ```python
  from numpyro_schechter import SchechterMag
  SchechterMag.supported_depths()
  # -> [3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30]
  ```

---

## Installation

From PyPI:

```bash
pip install numpyro_schechter
```

From GitHub (latest development version):

```bash
pip install git+https://github.com/alserene/numpyro_schechter.git
```

---

## Usage

Here is a minimal example showing how to use the `SchechterMag` distribution:

```python
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro_schechter.distribution import SchechterMag

# Simulated observed magnitudes
mag_obs = jnp.linspace(-24, -18, 100)

def model(mag_obs):
    # Priors
    alpha = numpyro.sample("alpha", dist.Uniform(-3.0, 1.0))
    M_star = numpyro.sample("M_star", dist.Uniform(-24.0, -20.0))
    logphi = numpyro.sample("logphi", dist.Normal(-3.0, 1.0))

    # Custom likelihood using the SchechterMag distribution
    schechter_dist = SchechterMag(alpha=alpha, M_star=M_star, logphi=logphi, mag_obs=mag_obs)
    
    # Use numpyro.factor to inject the log-likelihood
    log_likelihood = jnp.sum(schechter_dist.log_prob(mag_obs))
    numpyro.factor("likelihood", log_likelihood)

# You can now run inference with NumPyro's MCMC
# e.g., numpyro.infer.MCMC(...).run(rng_key, model, mag_obs=...)

# Note: Sampling is not implemented for SchechterMag; it is intended for use as a likelihood in inference.
```

For detailed usage and API documentation, please visit the [Documentation](https://numpyro-schechter.readthedocs.io/).

---

## Development

If you want to contribute or develop locally:

```bash
git clone https://github.com/alserene/numpyro_schechter.git
cd numpyro_schechter
poetry install
poetry run pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.

---

## Contact

Created by Alice — [aserene@swin.edu.au](mailto:aserene@swin.edu.au)

---

*Happy modelling!*
