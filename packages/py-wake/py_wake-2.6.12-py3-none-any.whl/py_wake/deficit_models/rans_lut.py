import xarray as xr
from py_wake.deficit_models.deficit_model import XRLUTDeficitModel
from py_wake import np
from py_wake.superposition_models import LinearSum
from py_wake.wind_farm_models.engineering_models import All2AllIterative
from py_wake.turbulence_models.rans_lut_turb import RANSLUTTurbulence
from py_wake.utils.rans_lut_utils import RANSLUTModel
from py_wake.tests import ptf
from pathlib import Path


class RANSLUT(All2AllIterative):
    def __init__(self, lut, site, windTurbines, rotorAvgModel=None):
        """
        Parameters
        ----------
        lut : str, Path or xarray.Dataset
            if str or Path: path to xarray.Dataset with tables including velocity deficit and wake added ti
            if Dataset: Dataset containing deficit and wake added_ti
        site : Site
            Site object
        windTurbines : WindTurbines
            WindTurbines object representing the wake generating wind turbines
        rotorAvgModel : RotorAvgModel, optional
            Model defining one or more points at the down stream rotors to
            calculate the rotor average wind speeds from.\n
            if None, default, the wind speed at the rotor center is used
        """
        if not isinstance(lut, (list, tuple)):
            lut = [lut]
        lut_lst = lut

        def load_lut(lut):
            if not isinstance(lut, xr.Dataset):
                lut = xr.load_dataset(lut)
            return lut
        lut_lst = [load_lut(lut) for lut in lut_lst]
        deficit = RANSLUTDeficit(lut=[lut.deficits for lut in lut_lst], rotorAvgModel=rotorAvgModel)
        turb = RANSLUTTurbulence(lut=[lut.added_ti for lut in lut_lst], rotorAvgModel=rotorAvgModel)

        All2AllIterative.__init__(self, site, windTurbines,
                                  wake_deficitModel=deficit,
                                  blockage_deficitModel=deficit,
                                  turbulenceModel=turb,
                                  superpositionModel=LinearSum())


class RANSLUTDeficit(RANSLUTModel, XRLUTDeficitModel):
    """Expects LUT velocity deficit xarray"""

    def __init__(self, lut, rotorAvgModel=None, groundModel=None, use_effective_ws=True,
                 use_effective_ti=False):
        assert use_effective_ws, "RANSLUTDeficit only makes sense when scaling with effective wind speed"
        XRLUTDeficitModel.__init__(self, self.get_lut(lut, 'deficits'),
                                   bounds='limit', rotorAvgModel=rotorAvgModel, groundModel=groundModel,
                                   use_effective_ws=True, use_effective_ti=use_effective_ti)

    def wake_radius(self, dw_ijlk, **kwargs):
        # Required for PyWake but not needed for RANS LUT model
        wake_radius_ijlk = np.ones(dw_ijlk.shape)
        return wake_radius_ijlk


class RANSLUTDemoDeficit(RANSLUTDeficit):
    def __init__(self, rotorAvgModel=None, groundModel=None, use_effective_ws=True, use_effective_ti=False):
        # Load default RANS LUT file based on a demo V80 LUT
        demo_lut = ptf('ranslut/V80_ranslut_demo.nc',
                       '846213eb655255f6e2201a47c2406f9e77f243f369398cb389bf7320b457dea8')

        RANSLUTDeficit.__init__(self, demo_lut, rotorAvgModel=rotorAvgModel, groundModel=groundModel,
                                use_effective_ws=use_effective_ws, use_effective_ti=use_effective_ti)
