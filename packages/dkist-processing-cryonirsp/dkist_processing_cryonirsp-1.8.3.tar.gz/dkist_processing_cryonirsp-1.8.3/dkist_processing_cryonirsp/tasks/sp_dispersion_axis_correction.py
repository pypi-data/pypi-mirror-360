"""Cryonirsp SP dispersion axis calibration task."""
import warnings

import numpy as np
from astropy import constants as const
from astropy import units as u
from astropy.coordinates import EarthLocation
from astropy.coordinates.spectral_coordinate import SpectralCoord
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
from dkist_processing_common.codecs.asdf import asdf_encoder
from dkist_processing_common.models.dkist_location import location_of_dkist
from dkist_service_configuration.logging import logger
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import differential_evolution
from scipy.optimize import OptimizeResult
from sunpy.coordinates import HeliocentricInertial

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_access_decoder
from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

__all__ = ["SPDispersionAxisCorrection"]


class SPDispersionAxisCorrection(CryonirspTaskBase):
    """Task class for correcting the dispersion axis wavelength values.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    record_provenance = True

    def run(self):
        """
        Run method for the task.

        For each beam
            - Gather 1D characteristic spectrum.
            - Compute the theoretical dispersion.
            - Load the telluric and non-telluric FTS atlases and grab only the portion of the atlases that pertain to the current observation.
            - Shift the preliminary wavelength vector (from the data) so that it generally aligns with the FTS atlas data.
            - Account for the speed at which DKIST was moving relative to the sun's center at the time of observation.
            - Define fitting bounds and fit the profile using scipy.optimize.differential_evolution.
            - Write results to disk.


        Returns
        -------
        None
        """
        spectrum = self.load_1d_char_spectrum()

        solar_header = self.load_header()

        dispersion, order, alpha = self.get_theoretical_dispersion()

        expected_wavelength_vector = self.compute_expected_wavelength_vector(spectrum, solar_header)

        (
            telluric_atlas_wave,
            telluric_atlas_trans,
            solar_atlas_wave_air,
            solar_atlas_trans_flipped,
        ) = self.load_and_resample_fts_atlas(expected_wavelength_vector)

        (fts_wave, fts_solar, fts_telluric) = self.initial_alignment(
            spectrum,
            expected_wavelength_vector,
            solar_atlas_wave_air,
            solar_atlas_trans_flipped,
            telluric_atlas_wave,
            telluric_atlas_trans,
        )

        doppler_shift = self.get_doppler_shift()

        fit_result = self.fit_dispersion_axis_to_FTS(
            fts_wave,
            fts_telluric,
            fts_solar,
            dispersion,
            alpha,
            doppler_shift,
            spectrum,
            order,
            self.constants.grating_constant,
        )

        self.write_fit_results(spectrum, order, fit_result)

    def write_fit_results(
        self, spectrum: np.ndarray, order: int, fit_result: OptimizeResult
    ) -> None:
        """Save the fit results to disk to later be used to update the l1 headers."""
        updated_headers = {
            "CRPIX1": np.size(spectrum) // 2 + 1,
            "CRVAL1": fit_result.x[0],
            "CDELT1": fit_result.x[1],
            "PV1_0": self.constants.grating_constant,
            "PV1_1": order,
            "PV1_2": fit_result.x[2],
            "CRPIX1A": np.size(spectrum) // 2 + 1,
            "CRVAL1A": fit_result.x[0],
            "CDELT1A": fit_result.x[1],
            "PV1_0A": self.constants.grating_constant,
            "PV1_1A": order,
            "PV1_2A": fit_result.x[2],
        }

        self.write(
            data=updated_headers,
            tags=[CryonirspTag.task_spectral_fit(), CryonirspTag.intermediate()],
            encoder=asdf_encoder,
        )

    def load_1d_char_spectrum(self) -> np.ndarray:
        """Load intermediate 1d characteristic measured_spectra for beam 1."""
        # Only fitting with the left beam.
        beam = 1
        array_generator = self.read(
            tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task("SOLAR_CHAR_SPEC")],
            decoder=cryo_fits_array_decoder,
        )

        return next(array_generator)

    def load_header(self) -> fits.header.Header:
        """Grab a header from a random solar gain frame to be used to find a rough initial wavelength estimate."""
        # Only fitting with the left beam.
        beam = 1
        solar_tags = [CryonirspTag.linearized_frame(), CryonirspTag.task("SOLAR_GAIN")]
        solar_obj = next(
            self.read(
                tags=solar_tags,
                decoder=cryo_fits_access_decoder,
                fits_access_class=CryonirspL0FitsAccess,
            )
        )
        solar_header = solar_obj.header
        return solar_header

    def get_theoretical_dispersion(self) -> tuple[u.Quantity, int, float]:
        """Compute theoretical dispersion value using the following grating equation.

        m = d/lambda * (sin(alpha) + sin(beta))

        where
        m = order
        d = grating spacing
        lambda = wavelength
        alpha = incident angle
        beta = diffraction angle

        """
        wavelength = self.constants.wavelength * u.nanometer
        grating_position_angle_phi = np.deg2rad(self.constants.grating_position_deg)
        grating_littrow_angle_theta = np.deg2rad(self.constants.grating_littrow_angle_deg)
        alpha = grating_position_angle_phi + grating_littrow_angle_theta
        beta = grating_position_angle_phi - grating_littrow_angle_theta
        grating_spacing_distance = (1.0 / self.constants.grating_constant) * u.m
        order = int(grating_spacing_distance / wavelength * (np.sin(alpha) + np.sin(beta)))
        camera_mirror_focal_length = self.parameters.camera_mirror_focal_length_mm
        pixpitch = self.parameters.pixel_pitch_micron
        linear_disp = order / (grating_spacing_distance * np.cos(beta)) * camera_mirror_focal_length
        theoretical_dispersion = (pixpitch / linear_disp).to(u.nanometer)

        return theoretical_dispersion, order, alpha

    def compute_expected_wavelength_vector(
        self, spectrum: np.ndarray, header: fits.header.Header
    ) -> u.Quantity:
        """Compute the expected wavelength vector based on the header information.""" ""
        # resample atlases
        number_of_wave_pix = np.size(spectrum)
        header["CRPIX1"] = number_of_wave_pix // 2 + 1
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  ## TO ELIMINATE datafix warnings
            wcs = WCS(header)
            # get wavelength based on header info (not fully accurate)
            expected_wavelength_vector = wcs.spectral.pixel_to_world(
                np.arange(number_of_wave_pix)
            ).to(u.nm)

        return expected_wavelength_vector

    def load_and_resample_fts_atlas(
        self, expected_wavelength_vector: u.Quantity
    ) -> tuple[u.Quantity, np.ndarray, u.Quantity, np.ndarray]:
        """Load telluric and non-telluric FTS atlas data, resample both atlases to be on the same, linear wavelength grid, select the portion of atlas that pertains to bandpass used."""
        solar_atlas_wavelength, solar_atlas_transmission = self.parameters.solar_atlas
        solar_atlas_wavelength = solar_atlas_wavelength * u.nm
        telluric_atlas_wavelength, telluric_atlas_transmission = self.parameters.telluric_atlas
        telluric_atlas_wavelength = telluric_atlas_wavelength * u.nm

        expected_wavelength_range = (
            expected_wavelength_vector.max() - expected_wavelength_vector.min()
        )
        min_wavelength = expected_wavelength_vector.min() - 0.25 * expected_wavelength_range
        max_wavelength = expected_wavelength_vector.max() + 0.25 * expected_wavelength_range

        cropped_telluric_mask = (telluric_atlas_wavelength > min_wavelength) * (
            telluric_atlas_wavelength < max_wavelength
        )
        telluric_atlas_wavelength = telluric_atlas_wavelength[cropped_telluric_mask]
        telluric_atlas_transmission = telluric_atlas_transmission[cropped_telluric_mask]

        cropped_solar_mask = (solar_atlas_wavelength > min_wavelength) * (
            solar_atlas_wavelength < max_wavelength
        )
        solar_atlas_wavelength = solar_atlas_wavelength[cropped_solar_mask]
        solar_atlas_transmission = solar_atlas_transmission[cropped_solar_mask]

        return (
            telluric_atlas_wavelength,
            telluric_atlas_transmission,
            solar_atlas_wavelength,
            solar_atlas_transmission,
        )

    def get_doppler_shift(self) -> u.Quantity:
        """Find the speed at which DKIST is moving relative to the Sun's center.

        Positive values refer to when DKIST is moving away from the sun.
        """
        coord = location_of_dkist.get_gcrs(obstime=Time(self.constants.solar_gain_ip_start_time))
        heliocentric_coord = coord.transform_to(
            HeliocentricInertial(obstime=Time(self.constants.solar_gain_ip_start_time))
        )
        obs_vr_kms = heliocentric_coord.d_distance
        return obs_vr_kms

    def initial_alignment(
        self,
        spectrum: np.ndarray,
        expected_wavelength_vector: SpectralCoord,
        solar_atlas_wave_air: u.Quantity,
        solar_atlas_trans_flipped: np.ndarray,
        telluric_atlas_wave: u.Quantity,
        telluric_atlas_trans: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Determine a shift of the preliminary wavelength vector so that it generally aligns with the data itself."""
        shifts = np.linspace(-2, 2, 550) * u.nm
        merit = np.zeros(len(shifts))
        for n, shift in enumerate(shifts):
            preliminary_wavelength = expected_wavelength_vector + shift
            fts_solar = np.interp(
                preliminary_wavelength, solar_atlas_wave_air, solar_atlas_trans_flipped
            )
            fts_telluric = np.interp(
                preliminary_wavelength, telluric_atlas_wave, telluric_atlas_trans
            )
            # calculate a merit value to be minimized
            merit[n] = np.std(spectrum - fts_solar * fts_telluric)

        # get minimum
        shift = shifts[np.argmin(merit)]

        # recalculate spectral axis and atlas spectrum for the best shift value
        fts_wave = expected_wavelength_vector + shift
        fts_solar = np.interp(fts_wave, solar_atlas_wave_air, solar_atlas_trans_flipped)
        fts_telluric = np.interp(fts_wave, telluric_atlas_wave, telluric_atlas_trans)

        return fts_wave.value, fts_solar, fts_telluric

    @staticmethod
    def fitness(
        parameters: np.ndarray,
        spectrum: np.ndarray,
        fts_wave: np.ndarray,
        fts_telluric: np.ndarray,
        fts_solar: np.ndarray,
        order: int,
        grating_constant: float,
        doppler_shift: float,
    ) -> float:
        """
        Model function for profile fitting.

        Parameters
        ----------
        crval1
            Wavelength at crpix1

        cdelt1
            Spectral dispersion at crpix1

        incident_light_angle
            Incident angle in degrees

        resolving_power
            Resolving power -- used to estimate the line spread function (may not be correct off limb)

        opacity
            Opacity scaling applied to telluric absorption

        stray_light_frac
            Inferred straylight fraction in the spectrograph --> This scales the lines non-linearly.

        continuum_amplitude
            Amplitude of the scattered light continuum
        """
        (
            crval1,
            cdelt1,
            incident_light_angle,
            resolving_power,
            opacity,
            stray_light_frac,
            continuum_amplitude,
        ) = parameters

        # calculate the spectral axis
        # Representations of spectral coordinates in FITS
        # https://ui.adsabs.harvard.edu/abs/2006A%26A...446..747G/abstract
        # https://specreduce.readthedocs.io/en/latest/api/specreduce.utils.synth_data.make_2d_arc_image.html

        number_of_wave_pix = np.size(spectrum)

        non_linear_header = {
            "CTYPE1": "AWAV-GRA",  # Grating dispersion function with air wavelengths
            "CUNIT1": "nm",  # Dispersion units
            "CRPIX1": number_of_wave_pix // 2 + 1,  # Reference pixel [pix]
            "PV1_0": grating_constant,  # Grating density
            "PV1_1": order,  # Diffraction order
            "CRVAL1": crval1,  # Reference value [nm] (<<<< TO BE OPTMIZED <<<<<<)
            "CDELT1": cdelt1,  # Linear dispersion [nm/pix] (<<<< TO BE OPTMIZED <<<<<<)
            "PV1_2": incident_light_angle,  # Incident angle [deg] (<<<< TO BE OPTMIZED <<<<<<)
        }

        non_linear_wcs = WCS(non_linear_header)
        wavelength_vector = (
            (non_linear_wcs.spectral.pixel_to_world(np.arange(number_of_wave_pix))).to(u.nm).value
        )

        # Gaussian convolution of the FTS atlas
        fwhm_wavelength = np.divide(crval1, resolving_power)
        sigma_wavelength = fwhm_wavelength / (2.0 * np.sqrt(2.0 * np.log(2)))
        kern_pix = sigma_wavelength / np.abs(cdelt1)

        # interpolate the telluric spectral atlas onto the new wavelength axis and scale by the opacity value that is being optimized
        fts_atmosphere_interp = np.interp(wavelength_vector, fts_wave, fts_telluric)
        fts_telluric_interp = np.exp(opacity * np.log(fts_atmosphere_interp))

        # interpolate the solar spectral atlas onto the new wavelength axis and apply a shift according to the Doppler shift due to orbital motions
        fts_solar_interp = np.interp(
            wavelength_vector,
            fts_wave + doppler_shift / (const.c.to("km/s")).value * crval1,
            fts_solar,
        )

        # apply telluric absorption spectrum to solar spectrum
        fts_modulated = fts_telluric_interp * fts_solar_interp
        # add flat value of straylight contamination
        fts_modulated_with_straylight = (fts_modulated + stray_light_frac) / (
            1.0 + stray_light_frac
        )
        # scale for total intensity of the continuum
        fit_amplitude = fts_modulated_with_straylight * continuum_amplitude

        # convolution for spectrograph line spread function
        fit_amplitude = gaussian_filter1d(fit_amplitude, kern_pix)

        # chisquare calculation for fit metric
        res_amplitude = np.sum((spectrum - fit_amplitude) ** 2)

        return res_amplitude

    def fit_dispersion_axis_to_FTS(
        self,
        fts_wave: np.ndarray,
        fts_telluric: np.ndarray,
        fts_solar: np.ndarray,
        dispersion: u.Quantity,
        alpha: float,
        doppler_shift: u.Quantity,
        spectrum: np.ndarray,
        order: int,
        grating_constant: float,
    ) -> OptimizeResult:
        """Define the bounds and send the fitting model on its way."""
        parameter_names = (
            "crval1 (wavelength at crpix1)",
            "cdelt1 (spectral dispersion at crpix1)",
            "incident_light_angle",
            "resolving_power",
            "opacity",
            "stray_light_frac",
            "continuum_amplitude",
        )
        crpix1_updated = np.size(spectrum) // 2 + 1
        crval1 = fts_wave[crpix1_updated]  # initial guess
        bounds = [
            # [nm[ +\- 0.5 nm range used for finding CRVAL1
            (crval1 - 0.5, crval1 + 0.5),
            # [nm/pix] 5% bounds on the dispersion at CRPIX1
            (
                dispersion.value - 0.05 * dispersion.value,
                dispersion.value + 0.05 * dispersion.value,
            ),
            # [radian] Incident angle range is +/- 5 degree from value in header
            (np.rad2deg(alpha) - 5, np.rad2deg(alpha) + 5),
            # resolving power range
            (20000, 125000),
            # opacity factor bounds
            (0.0, 10),
            # straylight fraction
            (0.0, 0.5),
            # continuum intensity correction
            (0.8 * np.nanpercentile(spectrum, 75), 1.2 * np.nanpercentile(spectrum, 75)),
        ]

        for repeat_fit in range(5):  # repeat just in case the fitting gets stuck in a local minimum
            fit_result = differential_evolution(
                SPDispersionAxisCorrection.fitness,
                args=(
                    spectrum,
                    fts_wave,
                    fts_telluric,
                    fts_solar,
                    order,
                    grating_constant,
                    doppler_shift.value,
                ),
                popsize=2,
                maxiter=300,
                bounds=bounds,
                disp=True,
                polish=True,
                tol=1.0e-9,
            )
            if fit_result.fun < 0.03:
                logger.info(" Convergence good based on fit func value")
                break

        logger.info("Fitted Values:")
        logger.info(" ")
        for p in range(len(parameter_names)):
            logger.info(
                f"Parameter: {parameter_names[p]},   Fit Result: {fit_result.x[p]},    Bounds: {bounds[p]}"
            )

        fit_amplitude = SPDispersionAxisCorrection.fitness(
            fit_result.x,
            spectrum,
            fts_wave,
            fts_telluric,
            fts_solar,
            order,
            grating_constant,
            doppler_shift.value,
        )

        return fit_result
