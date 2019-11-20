import numpy as np
import scipy


class metrics:

    def __init__(self, ref, sat):
        self.N = len(sat)
        self.ref = ref
        self.diff = sat - ref
        self.difflog = np.log10(sat) - np.log10(ref)

        self.rmse = self._rmse()
        self.rmse_log = self._rmse_log()
        self.bias = self._bias()
        self.bias_log = self._bias_log()
        self.mae = self._mae()
        self.mae_log = self._mae_log()
        self.mape = self._mape()
        self.medape = self._med_ape()

        self.slope, self.intercept, self.r_value, self.p_value, self.std_err = \
            scipy.stats.linregress(ref, sat)

    def to_dict(self):
        return {
            'N': self.N,
            'rmse': self.rmse,
            'rmse_log': self.rmse_log,
            'bias': self.bias,
            'bias_log': self.bias_log,
            'mae': self.mae,
            'mae_log': self.mae_log,
            'mape': self.medape, # to fit with ACIX nomenclature
            'slope': self.slope,
            'intercept': self.intercept,
            'r_value': self.r_value,
            #'p_value': self.p_value,
            #'std_err': self.std_err,
        }

    def _rmse_log(self):
        return np.sqrt(np.sum(self.difflog ** 2) / self.N)

    def _bias_log(self):
        return 10 ** (np.sum(self.difflog) / self.N)

    def _mae_log(self):
        return 10 ** (np.sum(np.abs(self.difflog)) / self.N)

    def _rmse(self):
        return np.sqrt(np.sum(self.diff ** 2) / self.N)

    def _bias(self):
        return np.sum(self.diff) / self.N

    def _mae(self):
        return np.sum(np.abs(self.diff)) / self.N

    def _med_ape(self):
        return 100 * np.median(np.abs(self.diff) / self.ref)

    def _mape(self):
        return 100 * np.mean(np.abs(self.diff) / self.ref)
