import traceback
from typing import Tuple

import numpy as np
from fontTools.misc.arrayTools import pointsInRect
from numpy._typing import ArrayLike
from pydantic import ValidationError

from psf_analysis_CFIM.psf_analysis.fit.estimator import (
    YXEstimator,
    ZEstimator,
    ZYXEstimator,
)
from psf_analysis_CFIM.psf_analysis.fit.fit_1d import evaluate_1d_gaussian
from psf_analysis_CFIM.psf_analysis.fit.fit_2d import evaluate_2d_gaussian
from psf_analysis_CFIM.psf_analysis.fit.fit_3d import evaluate_3d_gaussian
from psf_analysis_CFIM.psf_analysis.image import (
    Calibrated1DImage,
    Calibrated2DImage,
    Calibrated3DImage,
)
from psf_analysis_CFIM.psf_analysis.records import (
    YXFitRecord,
    ZFitRecord,
    ZYXFitRecord,
)
from psf_analysis_CFIM.psf_analysis.sample import YXSample, ZSample, ZYXSample
from psf_analysis_CFIM.psf_analysis.utils import fwhm
from scipy.optimize import curve_fit

class ZFitter:
    """
    Fit a 1D Gaussian to the Z pixel column centered in the YX plane.
    """

    image: Calibrated3DImage
    _estimator: ZEstimator
    _debug: bool = False

    def __init__(self, image: Calibrated3DImage):
        self.image = image
        self._estimator = ZEstimator(image=self.image, z_sample=self._get_z_sample())

    def _get_z_sample(self) -> ZSample:
        shape = self.image.data.shape

        return ZSample(
            image=Calibrated1DImage(
                data=self.image.data[:, shape[1] // 2, shape[2] // 2],
                spacing=(self.image.spacing[0],),
            )
        )

    def _fit_gaussian(self) -> Tuple[ArrayLike, ArrayLike]:
        point_params = [
                    self._estimator.get_background(),
                    self._estimator.get_amplitude(),
                    self._estimator.get_centroid(),
                    self._estimator.get_sigma(),
                ]
        try:

            fit = curve_fit(
                evaluate_1d_gaussian,
                xdata=self._estimator.sample.get_ravelled_coordinates(),
                ydata=self._estimator.sample.image.data,
                p0=point_params,
            )
        except (RuntimeError, TypeError) as e:
            print(f"Error fitting gaussian with Z: {e}")
            raise e
        else:
            return fit

    def fit(self) -> ZFitRecord:
        """
        Fit 1D Gaussian to Z pixel column centered in YX plane.

        Returns
        -------
        Fitted parameters and standard error
        """
        optimal_parameters, covariance = self._fit_gaussian()
        error = np.abs(np.sqrt(np.diag(covariance)))

        return ZFitRecord(
            z_bg=optimal_parameters[0],
            z_amp=optimal_parameters[1],
            z_mu=optimal_parameters[2],
            z_sigma=np.abs(optimal_parameters[3]),
            z_fwhm=fwhm(np.abs(optimal_parameters[3])),
            z_bg_sde=error[0],
            z_amp_sde=error[1],
            z_mu_sde=error[2],
            z_sigma_sde=error[3],
        )


class YXFitter:
    image: Calibrated3DImage
    _estimator: YXEstimator

    def __init__(self, image: Calibrated3DImage):
        self.image = image
        self._estimator = YXEstimator(image=self.image, yx_sample=self._get_yx_sample())

    def _get_yx_sample(self) -> YXSample:
        shape = self.image.data.shape


        return YXSample(
            image=Calibrated2DImage(
                data=self.image.data[shape[0] // 2],
                spacing=self.image.spacing[1:]
            )
        )

    def _fit_gaussian(self) -> Tuple[ArrayLike, ArrayLike]:
        try:
            point_args= [
                    self._estimator.get_background(),
                    self._estimator.get_amplitude(),
                    *self._estimator.get_centroid(),
                    self._estimator.get_sigmas()[0] ** 2,
                    0,
                    self._estimator.get_sigmas()[1] ** 2,
                ]
            return curve_fit(
                evaluate_2d_gaussian,
                xdata=self._estimator.sample.get_ravelled_coordinates(),
                ydata=self._estimator.sample.image.data.ravel(),
                p0=point_args,
            )
        except RuntimeError as e:
            print(f"Error fitting gaussian with YX: {e}")
            raise e

    def _get_principal_components(
        self, optimal_params: ArrayLike
    ) -> Tuple[float, float, float]:
        yx_cov_matrix = np.array(
            [
                [optimal_params[4], optimal_params[5]],
                [optimal_params[5], optimal_params[6]],
            ]
        )
        pc = np.sort(np.abs(np.sqrt(np.linalg.eigvals(yx_cov_matrix))))[::-1]
        return tuple(pc)

    def fit(self) -> YXFitRecord:
        optimal_parameters, covariance = self._fit_gaussian()
        principal_components = self._get_principal_components(optimal_parameters)
        error = np.abs(np.sqrt(np.diag(covariance)))

        return YXFitRecord(
            yx_bg=optimal_parameters[0],
            yx_amp=optimal_parameters[1],
            y_mu=optimal_parameters[2],
            x_mu=optimal_parameters[3],
            yx_cyy=optimal_parameters[4],
            yx_cyx=optimal_parameters[5],
            yx_cxx=optimal_parameters[6],
            y_fwhm=fwhm(np.abs(np.sqrt(optimal_parameters[4]))),
            x_fwhm=fwhm(np.abs(np.sqrt(optimal_parameters[6]))),
            yx_pc1_fwhm=fwhm(principal_components[0]),
            yx_pc2_fwhm=fwhm(principal_components[1]),
            yx_bg_sde=error[0],
            yx_amp_sde=error[1],
            y_mu_sde=error[2],
            x_mu_sde=error[3],
            yx_cyy_sde=error[4],
            yx_cyx_sde=error[5],
            yx_cxx_sde=error[5],
        )


class ZYXFitter:
    image: Calibrated3DImage = None
    _estimator: ZYXEstimator
    _debug: bool = True

    def __init__(self, image: Calibrated3DImage):
        self.image = image
        self._estimator = ZYXEstimator(
            image=self.image,
            zyx_sample=ZYXSample(
                image=self.image,
            ),
        )

    def _fit_gaussian(self) -> Tuple[ArrayLike, ArrayLike]:
        curve_fit_params = [
            self._estimator.get_background(),
            self._estimator.get_amplitude(),
            *self._estimator.get_centroid(),
            self._estimator.get_sigmas()[0] ** 2,
            0,
            0,
            self._estimator.get_sigmas()[1] ** 2,
            0,
            self._estimator.get_sigmas()[2] ** 2,
        ]
        try:
            optimal_params, covariance = curve_fit(
                evaluate_3d_gaussian,
                xdata=self._estimator.sample.get_ravelled_coordinates(),
                ydata=self._estimator.sample.image.data.ravel(),
                p0= curve_fit_params

            )
            if optimal_params[2] < 0 or optimal_params[3] < 0 or optimal_params[4] < 0:
                print(f"Negative mu found: {optimal_params[2:5]}")
                raise RuntimeError("Negative mu")
        except RuntimeError as e:
            print(f"Error fitting gaussian: {e}")
            raise e

        return optimal_params, covariance

    def fit(self) -> ZYXFitRecord:
        try:
            optimal_parameters, covariance = self._fit_gaussian()
        except RuntimeError as e:
            raise e
        principal_components = self._get_principal_components(optimal_parameters)
        error = np.abs(np.sqrt(np.diag(covariance)))
        try:
            if any(optimal_parameters) < 0:
                print(f"Negative mu found: {optimal_parameters[2:5]}")
                raise RuntimeError("Negative mu")
            record = ZYXFitRecord(
                zyx_bg=optimal_parameters[0],
                zyx_amp=optimal_parameters[1],
                zyx_z_mu=optimal_parameters[2],
                zyx_y_mu=optimal_parameters[3],
                zyx_x_mu=optimal_parameters[4],
                zyx_czz=optimal_parameters[5],
                zyx_czy=optimal_parameters[6],
                zyx_czx=optimal_parameters[7],
                zyx_cyy=optimal_parameters[8],
                zyx_cyx=optimal_parameters[9],
                zyx_cxx=optimal_parameters[10],
                zyx_z_fwhm=fwhm(np.abs(np.sqrt(optimal_parameters[5]))),
                zyx_y_fwhm=fwhm(np.abs(np.sqrt(optimal_parameters[8]))),
                zyx_x_fwhm=fwhm(np.abs(np.sqrt(optimal_parameters[10]))),
                zyx_pc1_fwhm=fwhm(principal_components[0]),
                zyx_pc2_fwhm=fwhm(principal_components[1]),
                zyx_pc3_fwhm=fwhm(principal_components[2]),
                zyx_bg_sde=error[0],
                zyx_amp_sde=error[1],
                zyx_z_mu_sde=error[2],
                zyx_y_mu_sde=error[3],
                zyx_x_mu_sde=error[4],
                zyx_czz_sde=error[5],
                zyx_czy_sde=error[6],
                zyx_czx_sde=error[7],
                zyx_cyy_sde=error[8],
                zyx_cyx_sde=error[9],
                zyx_cxx_sde=error[10],

            )
        except (ValueError, TypeError, ValidationError) as e:
            print(f"Error creating record: from image with shape {self.image.data.shape}")
            raise e
        else:
            return record
        # correlation_matrix = covariance / np.outer(error, error)
        # np.fill_diagonal(correlation_matrix, 1)
        # plot_correlation_matrix(correlation_matrix)


    def _get_principal_components(
        self, optimal_params: ArrayLike
    ) -> Tuple[float, float, float]:
        zyx_cov_matrix = np.array(
            [
                [optimal_params[5], optimal_params[6], optimal_params[7]],
                [optimal_params[6], optimal_params[8], optimal_params[9]],
                [optimal_params[7], optimal_params[9], optimal_params[10]],
            ]
        )
        pc = np.sort(np.abs(np.sqrt(np.linalg.eigvals(zyx_cov_matrix))))[::-1]
        return tuple(pc)
