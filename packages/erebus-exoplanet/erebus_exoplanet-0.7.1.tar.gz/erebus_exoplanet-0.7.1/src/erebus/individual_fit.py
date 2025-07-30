import copy
import hashlib
import json
import os
from typing import List

import batman
import numpy as np
import uncertainties.umath as umath

from erebus.frame_normalized_pca import perform_fn_pca_on_aperture
from erebus.mcmc_model import WrappedMCMC
from erebus.photometry_data import PhotometryData
from erebus.utility.bayesian_parameter import Parameter
from erebus.utility.h5_serializable_file import H5Serializable
from erebus.utility.planet import Planet
from erebus.utility.run_cfg import ErebusRunConfig
from erebus.utility.utils import create_method_signature

EREBUS_CACHE_DIR = "erebus_cache"

class IndividualFit(H5Serializable):
    __instance = None
    
    def _exclude_keys(self):
        '''
        Excluded from serialization
        '''
        return ['config', 'time', 'raw_flux', 'params', 'transit_model', 'mcmc', '__instance', 
                'photometry_data', '_force_clear_cache', 'predicted_t_sec']
    
    def __init__(self, photometry_data : PhotometryData, planet : Planet, config : ErebusRunConfig,
                 force_clear_cache : bool = False, override_cache_path : str = None, index = None):
        self.visit_name = photometry_data.visit_name
        self.config_hash = hashlib.md5(json.dumps(config.model_dump()).encode()).hexdigest()
        self.planet_name = planet.name
        self.planet = planet
        self.order = 'X'
        self.photometry_data = photometry_data

        self._cache_file = f"{EREBUS_CACHE_DIR}/{self.visit_name}_{self.config_hash}_individual_fit.h5"
        
        if override_cache_path is not None:
            self._cache_file = override_cache_path
        
        self.start_trim = 0 if config.trim_integrations is None else config.trim_integrations[0]
        self.end_trim = None if config.trim_integrations is None else -np.abs(config.trim_integrations[1])
        
        self.start_time = np.min(photometry_data.time)
        self.time = photometry_data.time[self.start_trim:self.end_trim] - np.min(photometry_data.time)
        self.raw_flux = photometry_data.raw_flux[self.start_trim:self.end_trim]
        self.config = config
        
        self.results = {}
        self.chain = None
        
        self.params = None
        self.transit_model = None
        
        self.eigenvalues, self.eigenvectors, self.pca_variance_ratios = perform_fn_pca_on_aperture(photometry_data.normalized_frames[self.start_trim:self.end_trim])
                
        mcmc = WrappedMCMC(self._cache_file.replace(".h5", "_mcmc.h5"))
        
        start_time = np.min(photometry_data.time)
        t0 = planet.get_closest_t0(start_time)
        self.predicted_t_sec = planet.get_predicted_tsec(start_time)
        
        lower_limit = 0 if config.prevent_negative_eclipse_depth else -2000e-6
        mcmc.add_parameter("fp", Parameter.uniform_prior(400e-6, lower_limit, 2000e-6))
             
        mcmc.add_parameter("t0", Parameter.prior_from_ufloat(t0, positive_only=True, force_fixed=config.fix_eclipse_timing))
        mcmc.add_parameter("rp_rstar", Parameter.prior_from_ufloat(planet.rp_rstar, positive_only=True))
        mcmc.add_parameter("a_rstar", Parameter.prior_from_ufloat(planet.a_rstar, positive_only=True))
        mcmc.add_parameter("p", Parameter.prior_from_ufloat(planet.p, positive_only=True, force_fixed=config.fix_eclipse_timing))
        mcmc.add_parameter("inc", Parameter.prior_from_ufloat(planet.inc, positive_only=True))
        
        # using ecosw and esinw as parameters instead of using e and w directly
        # since w is circular it causes degeneracies (eg, 10 degrees and 370 degrees)
        if planet.w is not None:
            ecosw = planet.ecc * umath.cos(planet.w * np.pi / 180)
            esinw = planet.ecc * umath.sin(planet.w * np.pi / 180)
            mcmc.add_parameter("esinw", Parameter.prior_from_ufloat(esinw, force_fixed=config.fix_eclipse_timing))
            mcmc.add_parameter("ecosw", Parameter.prior_from_ufloat(ecosw, force_fixed=config.fix_eclipse_timing))
        else:
            # Uniform for cos/sin omega from -1 to 1
            e = (planet.ecc.nominal_value + planet.ecc.std_dev)
            mcmc.add_parameter("esinw", Parameter.uniform_prior(0, -e, e))
            mcmc.add_parameter("ecosw", Parameter.uniform_prior(0, -e, e))
        
        if self.config.fit_fnpca:
            for i in range(0, 5):
                mcmc.add_parameter(f"pc{(i+1)}", Parameter.uniform_prior(0.1, -10, 10))
        else:
            for i in range(0, 5):
                mcmc.add_parameter(f"pc{(i+1)}", Parameter.fixed(0))
        
        if self.config.fit_exponential:
            mcmc.add_parameter("exp1", Parameter.uniform_prior(0.01, -0.1, 0.1))
            mcmc.add_parameter("exp2", Parameter.uniform_prior(-60.0, -200.0, -1.0))
        else:
            mcmc.add_parameter("exp1", Parameter.fixed(0))
            mcmc.add_parameter("exp2", Parameter.fixed(0))

        if self.config.fit_linear:
            mcmc.add_parameter("a", Parameter.uniform_prior(1e-3, -2, 2))
        else:
            mcmc.add_parameter("a", Parameter.fixed(0))
            
        mcmc.add_parameter("b", Parameter.uniform_prior(1e-6, -0.01, 0.01))
            
        if self.config._custom_parameters is not None:
            for key in self.config._custom_parameters:
                param = self.config._custom_parameters[key]
                if index is not None and index in self.config._custom_parameters_override:
                    param = self.config._custom_parameters_override[key]
                mcmc.add_parameter(key, copy.deepcopy(param))
        # y_err always goes last
        mcmc.add_parameter("y_err", Parameter.uniform_prior(400e-6, 0, 2000e-6))      
                  
        self.mcmc = mcmc
                                
        if os.path.isfile(self._cache_file) and not force_clear_cache:
            self.load_from_path(self._cache_file)
        else:
            self.save_to_path(self._cache_file)
        
        self._force_clear_cache = force_clear_cache
    
    def physical_model(self, x : List[float], fp : float, t0 : float, rp_rstar : float,
                       a_rstar : float, p : float, inc : float, esinw : float, ecosw : float) -> List[float]:
        '''
        Model for the lightcurve using batman
        fp is expected written in ppm
        '''
        if self.params is None:
            params = batman.TransitParams()
            params.limb_dark = "quadratic"
            params.u = [0.3, 0.3]
            
        params.t0 = t0
        params.t_secondary = self.predicted_t_sec.nominal_value + 2 * p * ecosw / np.pi
        params.fp = fp
        params.rp = rp_rstar
        params.inc = inc
        params.per = p
        params.a = a_rstar  
        
        ecc = umath.sqrt(ecosw ** 2 + esinw **2)
        w = (umath.atan2(esinw, ecosw) % (2 * np.pi)) * 180 / np.pi

        params.ecc = ecc
        params.w = w % 360
        
        # TODO: if x ever changes since the first call, this breaks
        if self.transit_model is None:
            transit_model = batman.TransitModel(params, x, transittype="secondary")

        flux_model = transit_model.light_curve(params)
        return flux_model
    
    def systematic_model(self, x : List[float], pc1 : float, pc2 : float, pc3 : float, pc4 : float, pc5 : float, 
                         exp1 : float, exp2 : float, a : float, b : float, *extra_params) -> List[float]:
        systematic = np.ones_like(x)
        if self.config.fit_fnpca:
            coeffs = np.array([pc1, pc2, pc3, pc4, pc5])
            pca = np.ones_like(self.eigenvalues[0])
            for i in range(0, 5):
                pca += coeffs[i] * self.eigenvalues[i]
            systematic *= pca
        if self.config.fit_exponential:
            systematic *= (exp1 * np.exp(exp2 * x)) + 1
        if self.config.fit_linear:
            systematic *= (a * x) + 1
        if self.config._custom_systematic_model is not None:
            flat_args = np.array(extra_params).flatten()
            systematic *= self.config._custom_systematic_model(x, *flat_args)
        
        systematic += b
        
        return systematic
        
    @staticmethod
    def __fit_method(x : List[float], fp : float, t0 : float, rp_rstar : float,
                       a_rstar : float, p : float, inc : float, esinw : float, ecosw : float, 
                       pc1 : float, pc2 : float, pc3 : float, pc4 : float, pc5 : float,
                       exp1 : float, exp2 : float, a : float, b : float, *extra_params) -> List[float]:
        systematic = IndividualFit.__instance.systematic_model(x, pc1, pc2, pc3, pc4, pc5, exp1, exp2, a, b, extra_params)
        physical = IndividualFit.__instance.physical_model(x, fp, t0, rp_rstar, a_rstar, p, inc, esinw, ecosw)
        return physical * systematic 
    
    def fit_method(self, x : List[float], *args) -> List[float]:
        '''
        For external use, calls the method used for fitting (*args is a list of the parameters)
        '''
        IndividualFit.__instance = self
        return IndividualFit.__fit_method(x, *args)

    def run(self):
        # Since the MCMC runs off a static method set the static instance to this object first
        IndividualFit.__instance = self
        
        # Build the method here based on fit_method and custom systematic parameters
        args = ["x"] + [key for key in self.mcmc.params][:-1]
        fit_method = create_method_signature(IndividualFit.__fit_method, args)
        self.mcmc.set_method(fit_method)

        self.mcmc.run(self.time, self.raw_flux,
                      force_clear_cache=self._force_clear_cache)
        self.results = self.mcmc.results
        self.chain = self.mcmc.sampler.get_chain(discard=200, thin=15, flat=True)
        print(self.mcmc.results)
        
        self.auto_correlation = self.mcmc.auto_correlation
        self.iterations = self.mcmc.iterations
        
        self.save_to_path(self._cache_file)
        
    def has_converged(self):
        return hasattr(self, "auto_correlation") and self.auto_correlation is not None \
            and np.isfinite(self.auto_correlation)
