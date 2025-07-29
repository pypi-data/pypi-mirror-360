# coding: utf-8

"""
Computes scattering with the Strong-Contrast Expansion (SCE) from Torquato and Kom 2021.
This SCE is the quasi-static version, called "local approximation" in Torquato and "short range" in Tsang's books.
It applies to low frequency or small scatterers.
Because of this assumption, local and non-local are undistinguishable, so that Rechtmans and Torquato, 2008
also provides a good reference for this implementation.
"""

# Stdlib import

# other import

# local import
from smrt.permittivity.generic_mixing_formula import maxwell_garnett_for_spheres
from .common import AdjustableEffectivePermittivityMixin, derived_EMModel
from .sce_common import SCEBase

#
# For developers: all emmodel must implement the `effective_permittivity`, `ke` and `phase` functions with the same arguments as here
# initialisation and precomputation can be done in the prepare method that is called only once for each layer whereas
# phase, ke and effective_permittivity can be called several times.
#


def derived_SCETK21_ShortRange(effective_permittivity_model):
    """Return a new SCE_ShortRange model with variant from the default SCE_ShortRange.

    Args:
        effective_permittivity_model: Permittivity mixing formula.

    Returns:
        class: A new class inheriting from SCE_ShortRange but with patched methods.
    """

    return derived_EMModel(SCETK21_ShortRange, effective_permittivity_model)


class SCETK21_ShortRange(AdjustableEffectivePermittivityMixin, SCEBase):

    """
    To be documented.
    """

    # default effective_permittivity_model is maxwell_garnett according to the SCE theory
    effective_permittivity_model = staticmethod(maxwell_garnett_for_spheres)

    def __init__(self, sensor, layer, scaled=True):

        super().__init__(sensor, layer, local=True, symmetrical=False, scaled=scaled)
