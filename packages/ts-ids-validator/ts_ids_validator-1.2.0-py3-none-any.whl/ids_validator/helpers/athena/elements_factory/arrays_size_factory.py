from typing import Dict

from ids_validator.helpers.athena.constants import DEFAULT_ELEMENTS_IN_ARRAYS

TWO = 2
ONE = 1
THREE = 3


class ArraysSizeFactory:
    def get_array_size(self, table_name: str) -> int:
        return self._array_sizes().get(table_name, DEFAULT_ELEMENTS_IN_ARRAYS)

    def _array_sizes(self) -> Dict[str, int]:
        return {
            "agilent_chemstation_v3_root": ONE,
            "agilent_chemstation_v3_systems": THREE,
            "agilent_chemstation_v3_systems_software": ONE,
            "agilent_chemstation_v3_systems_component_modules": ONE,
            "agilent_chemstation_v3_systems_component_columns": ONE,
            "agilent_chemstation_v3_users": ONE,
            "agilent_chemstation_v3_runs": ONE,
            "agilent_chemstation_v3_methods": ONE,
            "agilent_chemstation_v3_methods_injection_pumps": ONE,
            "agilent_chemstation_v3_methods_injection_pumps_solvents": ONE,
            "agilent_chemstation_v3_methods_injection_pumps_gradient_settings": ONE,
            "agilent_chemstation_v3_methods_injection_pumps_gradient_settings_composition": ONE,
            "agilent_chemstation_v3_methods_detection_uv_vis_settings": ONE,
            "agilent_chemstation_v3_methods_detection_mass_spectrometer_settings": ONE,
            "agilent_chemstation_v3_methods_detection_mass_spectrometer_settings_selected_ions": ONE,
            "agilent_chemstation_v3_methods_detection_charged_aerosol_settings": ONE,
            "agilent_chemstation_v3_methods_detection_other_detector_settings": ONE,
            "agilent_chemstation_v3_samples": ONE,
            "agilent_chemstation_v3_samples_properties": ONE,
            "agilent_chemstation_v3_samples_labels": ONE,
            "agilent_chemstation_v3_results": ONE,
            "agilent_chemstation_v3_results_peaks": ONE,
        }
