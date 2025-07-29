from pathlib import Path
import copy
from datetime import datetime

import numpy as np
import pandas as pd

from simera import Config, ZipcodeManager
from simera.utils import (
    DataInputError,
    compute_all_conversions_between_units_in_ratios,
    standardize_ratio_key,
    standardize_ratio_key_is_valid,
    ExcelCache
)

# future - sc and zm not be inside Ratesheet? IT SHOULD. self.sc, self.zm
# todo: merge sc and zm into Ratesheet, this is one of the bugs.

sc = Config()
zm = ZipcodeManager()
ec = ExcelCache(sc.path.resources / '_excel_cache')

class Ratesheet:
    def __init__(self, file_path, sheet_name):
        self.input = self._Input(file_path, sheet_name)
        self.meta = self._Meta(self.input)
        self.lane = self._Lane(self.input, self.meta)
        self.cost = self._Cost(self.input, self.meta)
        self.shortcuts = self._Shortcuts(self.input, self.lane, self.meta)
        self._run_ratesheet_consistency_check()

        # This is to show if ratesheet was combined with other
        self.combines = [repr(self)]

    def __repr__(self):
        site = self.meta.src.get("site")
        carrier = self.meta.service.get("carrier")
        trpmode = self.meta.service.get("trpmode")
        service = self.meta.service.get("service")
        service1 = self.meta.service.get("service1")
        service2 = self.meta.service.get("service2")
        countries = self.shortcuts.dest_countries

        # Build the optional second service segment only if present
        service_segment = service
        if service1:
            service_segment = f"{service_segment}-{service1}"
        if service2:
            service_segment = f"{service_segment}-{service2}"

        # Shorten list of countries if more than 3 items
        len_countries = len(countries)
        n = 3
        if len_countries > n:
            countries = countries[:1] + ['...'] + [f'{len_countries}']
        countries = "-".join(countries)

        return (
            f"<{site}>"
            f"<{trpmode}-{carrier}-{service_segment}>"
            f"<{countries}>"
        )

    def _run_ratesheet_consistency_check(self):
        # All lane dest_zone are present in cost zones
        for lane_dest_zone in self.lane.zones:
            if lane_dest_zone not in self.cost.zones:
                raise DataInputError(f"Dest_zone (specified as lane) not found in cost dest_zones: '{lane_dest_zone}'.",
                                     solution=f"Make sure that '{lane_dest_zone}' is available in cost zones {self.cost.zones}.",
                                     file_path=self.input.file_path, sheet_name=self.input.sheet_name,
                                     column=f'<dest_zone> and cost_zones',
                                     values=f"<{lane_dest_zone}>")

    class _Shortcuts:
        def __init__(self, input_rs, lane_rs, meta_rs):
            self._input = input_rs
            self._lane = lane_rs
            self._meta = meta_rs
            self.dest_countries = list(self._lane.df_dest_zone.dest_ctry.unique())
            self.display_on_shipment_summary = {'src_site': self._meta.src.get('site')}
            self.display_on_shipment_summary.update({k: v for k, v in self._meta.service.items() if v is not None})
            self.display_on_shipment_summary.update({'sheet_name': self._input.sheet_name})
            self.src_sites = self._get_src_sites()

        def __repr__(self):
            return 'Ratesheet Shortcuts'

        def _get_src_sites(self):
            src_site = self._meta.src.get('site')
            if src_site is not None:
                return [site.strip() for site in src_site.split(',')]
            else:
                return [None]

    @staticmethod
    def clear_cache():
        ec.clear_cache()

    class _Input:
        _INPUT_COLUMNS_DTYPES = {
            # Lane
            '<src_site>': 'string',
            '<src_region>': 'string',
            '<src_ctry>': 'string',
            '<src_zip>': 'string',
            '<src_zone>': 'string',
            '<dest_site>': 'string',
            '<dest_region>': 'string',
            '<dest_ctry>': 'string',
            '<dest_zip>': 'string',
            '<dest_zone>': 'string',
            '<transit_time>': np.float64,

            # Cost
            '<cost_type>': 'string',
            '<cost_unit>': 'string',
            '<range_value>': np.float64,
            '<range_unit>': 'string',
        }

        def __init__(self, file_path, sheet_name):
            self.file_path = file_path
            self.sheet_name = sheet_name
            self.input_data = self._read_excel_data()

        def __repr__(self):
            return f"Input(file_path='{self.file_path.parts[-1]}', sheet_name='{self.sheet_name}')"

        def _read_excel_data(self):
            # Set fixed dtypes
            dtypes = self._INPUT_COLUMNS_DTYPES.copy()

            # Read the Excel file header to get the available columns
            available_columns = ec.read_excel_cached(self.file_path, sheet_name=self.sheet_name, nrows=0).columns.tolist()
            # available_columns = pd.read_excel(io=self.file_path, sheet_name=self.sheet_name, nrows=0).columns.tolist()

            # Filter the dtype_dict to include only columns that exist in the file
            filtered_dtypes = {col: dtype for col, dtype in dtypes.items() if col in available_columns}

            # Read the Excel file with the filtered dtypes. If empty, would error would be raised.
            if filtered_dtypes:
                df = ec.read_excel_cached(self.file_path, sheet_name=self.sheet_name, dtype=filtered_dtypes, engine='calamine')
                # df = pd.read_excel(io=self.file_path, sheet_name=self.sheet_name, dtype=filtered_dtypes, engine='calamine')
            else:
                df = ec.read_excel_cached(self.file_path, sheet_name=self.sheet_name, engine='calamine')
                # df = pd.read_excel(io=self.file_path, sheet_name=self.sheet_name, engine='calamine')

            df.dropna(how='all', inplace=True, ignore_index=True)
            return df

    class _Meta:
        def __init__(self, input_trs):
            self._input = input_trs
            self.input_data = self._get_input_data()
            self._set_initial_attributes()
            self._set_input()
            self._set_settings()
            self._set_validity()
            self._set_currency()
            self._set_service()
            self._set_src()
            self._set_dest()
            self._set_max_size(attribute='shipment_size_max')
            self._set_max_size(attribute='package_size_max')
            self._set_chargeable_ratios(attribute='chargeable_ratios')
            self._set_custom_ratios()
            self._set_custom_defaults()

        def __repr__(self):
            return f"Meta(file_path='{self._input.file_path.parts[-1]}', sheet_name='{self._input.sheet_name}')"

        def _get_input_data(self):
            use_cols = ['<meta>', '<meta_value>']
            df = self._input.input_data.copy().reindex(columns=use_cols).dropna(subset=['<meta>'], ignore_index=True)
            df.columns = df.columns.str.replace(r'[<>]', '', regex=True)
            # Names in groups may have required indication '*' as suffix. That is removed from variable name.
            df['meta'] = df['meta'].astype('str').str.replace(r'[*]', '', regex=True)
            return df

        def _set_initial_attributes(self):
            """Convert <meta> and <meta_value> columns of ratesheet and sets all <group_name> as meta attribute.
            Meta and meta_value are converted to dict. Nan values are converter to None.
            Example: <input>'url': 'file.xlsx' it set as '.meta.input.{'url': 'file.xlsx'}'
            """

            # Get rawdata for meta
            df = self.input_data.copy()

            # Set all <groups> as meta attributes
            df_meta = df[df['meta'].str.contains('<.+>', regex=True)].copy()
            df_meta['idx_from'] = df_meta.index + 1
            df_meta['idx_to'] = (df_meta.idx_from.shift(-1) - 2).fillna(df.shape[0] - 1).astype(int)
            df_meta['meta_value'] = df_meta['meta'].str.replace(r'[<>]', '', regex=True)
            for _, row in df_meta.iterrows():
                attr_dict = df[row.idx_from:row.idx_to + 1].set_index('meta')['meta_value'].to_dict()
                # Convert all nans to None
                attr_dict_clean = {k: v if v is not None and not pd.isna(v) else None for k, v in attr_dict.items()}
                setattr(self, row.meta_value, attr_dict_clean)

        # ==============================================================================================================
        # Functions and variables
        # ==============================================================================================================
        # Get defaults and choices
        _config_choices_volume = sc.config.units_of_measure.get('choices').get('volume')
        _config_choices_weight = sc.config.units_of_measure.get('choices').get('weight')
        _config_choices_volume_and_weight = sc.config.units_of_measure.get('choices').get('volume_and_weight')

        _true_valid_choices = [True, 'True', 'TRUE', 'true', 'Yes', 'Y']
        _false_valid_choices = [False, 'False', 'FALSE', 'false', 'No', 'N']

        @classmethod
        def _bool_format_method(cls, x):
            return (True if x in cls._true_valid_choices else
                    False if x in cls._false_valid_choices else x)

        @classmethod
        def _str_upper(cls, x):
            return str.upper(str(x))

        def _set_attribute(self, group, group_item,
                           required=False,
                           default=None,
                           allowed_values: list = None,
                           format_method=None):
            """ Sets attribute values based on ratesheet input, default values and allowed options.
            group: attribute name of a group. Example: <settings>
            group_item: item in group. Example in <settings>: <ratesheet_type>
            required: if True, field can not get None
            default: value set if group_item value is np.nan/None
            allowed: list of allowed values.
            format_method: function used on item to convert it into proper dtype and format
            """

            # If group does not exist in ratesheet, create it.
            if not hasattr(self, group):
                setattr(self, group, {})
            x = getattr(self, group).get(group_item)

            # Set default
            if x is None and default is not None:
                x = default

            # Apply formatting function
            if format_method is not None and x is not None:
                x = format_method(x)

            # Check against allowed options
            if allowed_values is not None:
                if x not in allowed_values:
                    raise DataInputError(f"Invalid input for <{group}>{group_item}: {x}.",
                                         solution=f"Use one of allowed options: {allowed_values}. Check also dtypes.",
                                         file_path=self._input.file_path,
                                         sheet_name=self._input.sheet_name,
                                         column=f'<meta><{group}>{group_item}: {x}',
                                         values=x)

            # Check against required
            if required and x is None:
                raise DataInputError(f"Invalid input for <{group}>{group_item}: {x}.",
                                     solution=f"Value is required and can not return None",
                                     file_path=self._input.file_path,
                                     sheet_name=self._input.sheet_name,
                                     column=f'<meta><{group}>{group_item}: {x}',
                                     values=x)
            getattr(self, group).update({group_item: x})

        # ==============================================================================================================
        # Input
        # ==============================================================================================================
        def _set_input(self):
            self._set_attribute('input', 'file_path')
            self._set_attribute('input', 'sheet_name')
            self._set_attribute('input', 'issues')

        # ==============================================================================================================
        # Settings
        # ==============================================================================================================
        def _set_settings(self):
            allowed_values = [None, 'downstream', 'mainstream']
            self._set_attribute('settings', 'ratesheet_type', default='downstream', allowed_values=allowed_values)

            allowed_values = ['starting', 'ending']
            self._set_attribute('settings', 'dest_zip_to', default='starting', allowed_values=allowed_values)

        # ==============================================================================================================
        # Validity
        # ==============================================================================================================
        def _set_validity(self):
            format_method = pd.to_datetime
            self._set_attribute('validity', 'last_update', format_method=format_method)
            self._set_attribute('validity', 'valid_from', format_method=format_method)
            self._set_attribute('validity', 'valid_to', format_method=format_method)

        # ==============================================================================================================
        # Currency
        # ==============================================================================================================
        def _set_currency(self):
            default_currency = sc.config.currency.get('default')
            self._set_attribute('currency', 'currency', default=default_currency)
            self._set_attribute('currency', 'reference_currency', default=default_currency)
            currency = getattr(self, 'currency').get('currency')
            reference_currency = getattr(self, 'currency').get('reference_currency')

            # if currency is same as default
            if currency == reference_currency:
                self._set_attribute('currency', 'rate', default=1)
                rate_logic = f'1 {reference_currency} = 1 {currency} ;)'
            else:
                try:
                    rate = sc.config.currency.get('rates').get(reference_currency).get(currency)
                except AttributeError:
                    pass
                if rate is None:
                    raise DataInputError(f"Unknown exchange rate for '{currency}' to '{reference_currency}' (set as default)",
                                         solution=f"Update 'rates':'{reference_currency}':'{currency}' "
                                         f"in simera_resources/config/currency.yaml",
                                         file_path=self._input.file_path,
                                         sheet_name=self._input.sheet_name,
                                         column=f'<meta><currency><ratesheet_currency>',
                                         values=currency)
                else:
                    self._set_attribute('currency', 'rate', default=rate)
                    rate_logic = f'1 {reference_currency} = {rate:0,.3f} {currency}, 1 {currency} = {1/rate:0,.3f} {reference_currency}'
            self._set_attribute('currency', '_rate_logic', default=rate_logic)

        # ==============================================================================================================
        # Service
        # ==============================================================================================================
        def _set_service(self):
            default_carrier = f'{self._input.sheet_name} [{datetime.now()}]'
            default_trpmode = f'{self._input.sheet_name}'
            default_service = f'{self._input.sheet_name}'
            self._set_attribute('service', 'carrier', default=default_carrier, format_method=self._str_upper)
            self._set_attribute('service', 'trpmode', default=default_trpmode, format_method=self._str_upper)
            self._set_attribute('service', 'service', default=default_service, format_method=self._str_upper)
            self._set_attribute('service', 'service1', format_method=self._str_upper)
            self._set_attribute('service', 'service2', format_method=self._str_upper)
            allowed_values = self._true_valid_choices + self._false_valid_choices
            self._set_attribute('service', 'default_ratesheet', default=True, allowed_values=allowed_values, format_method=self._bool_format_method)

        # ==============================================================================================================
        # Src - Lane Source
        # ==============================================================================================================
        def _set_src(self):
            self._set_attribute('src', 'site', format_method=self._str_upper)
            self._set_attribute('src', 'region', format_method=self._str_upper)
            self._set_attribute('src', 'ctry', format_method=self._str_upper)
            self._set_attribute('src', 'zone', format_method=self._str_upper)
            self._set_attribute('src', 'zip', format_method=self._str_upper)

        # ==============================================================================================================
        # Dest - Lane Destination
        # ==============================================================================================================
        def _set_dest(self):
            self._set_attribute('dest', 'site', format_method=self._str_upper)
            self._set_attribute('dest', 'region', format_method=self._str_upper)
            self._set_attribute('dest', 'ctry', format_method=self._str_upper)
            self._set_attribute('dest', 'zone', format_method=self._str_upper)
            self._set_attribute('dest', 'zip', format_method=self._str_upper)

        # ==============================================================================================================
        # Max Size for shipment and package
        # ==============================================================================================================
        def _set_max_size(self, attribute):
            """
            Process initial values for shipment_size_max and package_size_max and converts that into
            kg and m3. Those units will be converted to default units with TransportRatesheetManager.
            :param attribute: shipment_size_max or package_size_max
            :return: None (set shipment_size_max and package_size_max dicts as attribute to ratesheet meta)
            """

            # If attribute (e.g. shipment_size_max) is not in ratesheet, set it up with empty dict as value
            if not hasattr(self, attribute):
                setattr(self, attribute, {})

            # Get initial values for attribute (if exist). If ratesheet has units not in choices, raise error.
            volume_init = {}
            weight_init = {}
            for unit, value in getattr(self, attribute).items():
                # Check if unit is in choices. If not, raise
                # error
                if unit not in self._config_choices_volume_and_weight:
                    raise DataInputError(f"Invalid Unit '{unit}' for '<{attribute}>'. "
                                         f"Avail. weight & volume choices: '{self._config_choices_volume_and_weight}'",
                                         solution=f"Set correct unit",
                                         file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                         column='<meta>',
                                         values=f"<{attribute}>{unit}: {value}")
                if unit in self._config_choices_volume and value is not None:
                    volume_init.update({unit: value})
                if unit in self._config_choices_weight and value is not None:
                    weight_init.update({unit: value})

            # Calculate values for weight and volume in kg and m3
            volume_converted_to_m3 = {f'{k} => m3': round(
                v / sc.config.units_of_measure['conversions']['volume'][k]['m3'], 5) for k, v in
                volume_init.items()}
            weight_converted_to_kg = {f'{k} => kg': round(
                v / sc.config.units_of_measure['conversions']['weight'][k]['kg'], 5) for k, v in
                weight_init.items()}

            # Get minimum values for shipment size (if more than 1 value provided for unit)
            volume_size = min(volume_converted_to_m3.values()) if volume_converted_to_m3 else None
            weight_size = min(weight_converted_to_kg.values()) if weight_converted_to_kg else None

            # Set attributes that will be used in script
            setattr(self, attribute, {'func_input': {}})
            getattr(self, attribute).update({'m3': volume_size})
            getattr(self, attribute).update({'kg': weight_size})
            getattr(self, attribute).update({'_origin': 'Ratesheet'})
            volume_msg = f'Ratesheet: {volume_converted_to_m3}' if volume_converted_to_m3 else None
            getattr(self, attribute).update({'_volume_ratesheet_input': volume_init})
            getattr(self, attribute).update({'_volume_ratesheet_calculation': volume_msg})
            weight_msg = f'Ratesheet: {weight_converted_to_kg}' if weight_converted_to_kg else None
            getattr(self, attribute).update({'_weight_ratesheet_input': weight_init})
            getattr(self, attribute).update({'_weight_ratesheet_calculation': weight_msg})

            # If volume & weights are None, get values based on transport_ratesheet.yaml config file (if exist)
            ratesheet_trpmode = getattr(self, 'service').get('trpmode')
            if getattr(self, attribute)['m3'] is None and getattr(self, attribute)['kg'] is None:
                try:
                    volume = sc.config.ratesheet.get(attribute).get(ratesheet_trpmode).get('m3')
                    if volume is not None:
                        getattr(self, attribute).update({'m3': volume})
                        getattr(self, attribute).update({'_origin': 'Config'})
                    getattr(self, attribute).update({'_volume_config_input': sc.config.ratesheet.get(attribute).get(ratesheet_trpmode).get('_volume_config_input')})
                    getattr(self, attribute).update({'_volume_config_calculation': sc.config.ratesheet.get(attribute).get(ratesheet_trpmode).get('_volume_config_calculation')})
                except AttributeError:  # Transport mode in config may not be present
                    pass

                try:
                    weight = sc.config.ratesheet.get(attribute).get(ratesheet_trpmode).get('kg')
                    if weight is not None:
                        getattr(self, attribute).update({'kg': weight})
                        getattr(self, attribute).update({'_origin': 'Config'})
                    getattr(self, attribute).update({'_weight_config_input': sc.config.ratesheet.get(attribute).get(ratesheet_trpmode).get('_weight_config_input')})
                    getattr(self, attribute).update({'_weight_config_calculation': sc.config.ratesheet.get(attribute).get(ratesheet_trpmode).get('_weight_config_calculation')})
                except AttributeError:  # Transport mode in config may not be present
                    pass

            # Create easy_to_use func_input to function
            func_input = {}
            if (volume_size:=getattr(self, attribute)['m3']) is not None:
                func_input.update({'m3': volume_size})
            if (weight_size:=getattr(self, attribute)['kg']) is not None:
                func_input.update({'kg': weight_size})
            getattr(self, attribute).update({'func_input': func_input})

        # ==============================================================================================================
        # Chargeable ratios
        # ==============================================================================================================
        def _set_chargeable_ratios(self, attribute='chargeable_ratios'):
            # Check: Attribute not in ratesheet, set it up with empty dict
            if not hasattr(self, attribute):
                setattr(self, attribute, {})

            # Check: Only one entry allowed with a non-None/non-NaN value.
            chargeable_ratios_init = getattr(self, attribute).copy()
            if chargeable_ratios_init:
                nb_valid_ratios = sum(1 for v in chargeable_ratios_init.values() if v is not None)
                if nb_valid_ratios > 1:
                    _wrong_ratios = {k: v for k, v in chargeable_ratios_init.items() if v is not None}
                    raise DataInputError(
                        f"Only one chargeable ratio allowed (with value). Received {nb_valid_ratios} ratios with values: {_wrong_ratios}.",
                        solution=f"Use value for only one ratio.",
                        file_path=self._input.file_path,
                        sheet_name=self._input.sheet_name,
                        column="<meta>",
                        values=f"<{attribute}><{chargeable_ratios_init}>"
                    )

            # Classify initial ratios to correct/incorrect. Only correct will be processed.
            ratios_correct = {}
            ratios_incorrect = {}
            for k, v in chargeable_ratios_init.items():
                if v is not None:
                    ratios_correct.update({k: v})
                else:
                    ratios_incorrect.update({k: None})

            # Check: ratio is proper format 'x/y'
            if ratios_correct:
                k = list(ratios_correct.keys())[-1]
                k_converted = standardize_ratio_key(k)
                if not standardize_ratio_key_is_valid(k_converted):
                    raise DataInputError(f"Incorrect format for chargeable ratio: '{k}'.",
                                         solution=f"Proper format examples: `m3 per kg`, 'in3/lb', 'cft / kg'.",
                                         file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                         column=f'<meta><{attribute}>',
                                         values=f"<{k}>")

            # Generate ratio conversions for ratios_correct
            ratio_conversions = compute_all_conversions_between_units_in_ratios(ratios_correct, include_self=False)

            # Classify unit for weight_unit, volume_unit, ratio_unit
            if ratio_conversions:
                volume_unit = [unit for unit in ratio_conversions if unit in self._config_choices_volume]
                weight_unit = [unit for unit in ratio_conversions if unit in self._config_choices_weight]

                if not volume_unit or not weight_unit:
                    raise DataInputError(f"Incorrect units for ratios. Proper volume units: {volume_unit}. Proper weight units: {weight_unit}.",
                                         solution=f"Proper ratio format: volume/weight or weight/volume (E.g.: 'kg per m3', 'in3/lb'. Allowed units: {self._config_choices_volume_and_weight}",
                                         file_path=self._input.file_path,
                                         sheet_name=self._input.sheet_name,
                                         column="<meta>",
                                         values=f"<{attribute}>{chargeable_ratios_init}")

                volume_unit = volume_unit[-1]
                weight_unit = weight_unit[-1]

                # Calculate fixed unit ratio kg/m3 (independent of input)
                weight_to_volume_value_correct_ratio = ratio_conversions[weight_unit][volume_unit]
                # Get ratios to kg and m3
                ratio_to_m3 = sc.config.units_of_measure['conversions']['volume'][volume_unit]['m3']
                ratio_to_kg = sc.config.units_of_measure['conversions']['weight'][weight_unit]['kg']
                kg_to_m3_ratio = (weight_to_volume_value_correct_ratio / ratio_to_kg) * ratio_to_m3
            else:
                kg_to_m3_ratio = None

            setattr(self, attribute, {'kg/m3': kg_to_m3_ratio})
            getattr(self, attribute).update({'_ratesheet_input': {'correct': ratios_correct, 'skipped': ratios_incorrect}})
            getattr(self, attribute).update({'_ratesheet_calculation': f"Ratesheet: {ratios_correct} => 'kg/m3': {kg_to_m3_ratio}"})


        # ==============================================================================================================
        # Custom ratios
        # ==============================================================================================================
        def _set_custom_ratios(self, attribute='custom_ratios'):
            # If not in ratesheet, make empty dict.
            if not hasattr(self, attribute):
                setattr(self, attribute, {})
            ratesheet_input = getattr(self, attribute)

            # Remove attributes
            setattr(self, attribute, {})

            # Check if ratio is valid
            if ratesheet_input:
                for k, v in ratesheet_input.items():
                    if not standardize_ratio_key_is_valid(standardize_ratio_key(k)):
                        raise DataInputError(f"Incorrect format for custom ratio: '{k}'.",
                                             solution=f"Proper format examples: `m3 per kg`, 'in3/lb', 'cft / kg'.",
                                             file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                             column=f'<meta><{attribute}>',
                                             values=f"<{k}>")

            # Get all conversions for custom_ratios
            ratesheet_input_converted = compute_all_conversions_between_units_in_ratios(ratesheet_input, keep_none=False)

            # Get config input
            config_input = sc.config.ratesheet.get('custom_ratios').copy()
            config_input_updated = copy.deepcopy(config_input)

            # Overwrite config with ratesheet input
            for k_trs, v_trs in ratesheet_input_converted.items():
                if config_input_updated.get(k_trs) is not None:
                    config_input_updated.get(k_trs).update(v_trs)
                else:
                    config_input_updated.update({k_trs: v_trs})

            # setattr(self, attribute, compute_all_conversions_between_units_in_ratios(ratios_init))
            getattr(self, attribute).update(config_input_updated)
            getattr(self, attribute).update({'_ratesheet_input': ratesheet_input})
            getattr(self, attribute).update({'_ratesheet_input_converted': ratesheet_input_converted})
            getattr(self, attribute).update({'_config_input_init': config_input})

        # ==============================================================================================================
        # Custom defaults
        # ==============================================================================================================
        def _set_custom_defaults(self, attribute='custom_defaults'):
            # If not in ratesheet, make empty dict.
            if not hasattr(self, attribute):
                setattr(self, attribute, {})
            ratesheet_input = getattr(self, attribute)

            # Remove attributes
            setattr(self, attribute, {})

            # Check if ratio is valid
            if ratesheet_input:
                for k, v in ratesheet_input.items():
                    if v is None:
                        raise DataInputError(f"Incorrect value for custom default: '{k}'.",
                                             solution=f"Value can not be None",
                                             file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                             column=f'<meta><{attribute}>',
                                             values=f"<{k}>")

            # Get config input
            config_input = sc.config.ratesheet.get('custom_defaults').copy()
            config_input_updated = copy.deepcopy(config_input)

            # Overwrite config with ratesheet input
            config_input_updated.update(ratesheet_input)

            # setattr(self, attribute, compute_all_conversions_between_units_in_ratios(ratios_init))
            getattr(self, attribute).update(config_input_updated)
            getattr(self, attribute).update({'_ratesheet_input': ratesheet_input})
            getattr(self, attribute).update({'_config_input_init': config_input})

    class _Lane:
        def __init__(self, input_trs, meta_trs):
            self._input = input_trs
            self._meta = meta_trs
            self.input_data = self._get_input_data()
            self.output_data = self._normalize_input_data()
            self.df_dest_zone = self._set_df_dest_zone()
            self.df_transit_time = self._set_df_transit_time()
            self.find_dest_zone = self._set_fast_lookup_for_lane(self.df_dest_zone, 'dest_zone')
            self.find_transit_time = self._set_fast_lookup_for_lane(self.df_transit_time, 'transit_time')
            self.zones = self._set_unique_zones()  # Currently only {'zones': all_unique_zones}
            self._check_zone_completeness()

        def __repr__(self):
            return f"Lane(file_path='{self._input.file_path.parts[-1]}', sheet_name='{self._input.sheet_name}')"

        def _get_input_data(self):
            # future - all <src_> and <dest_> will be included
            #  use_cols = list(self._input._LANE_COLUMNS_DTYPES.keys())
            use_cols = ['<dest_ctry>', '<dest_zip>', '<dest_zone>', '<transit_time>']
            df = self._input.input_data.copy().reindex(columns=use_cols).dropna(how='all', ignore_index=True)
            df.columns = df.columns.str.replace(r'[<>]', '', regex=True)
            if df.shape[0] == 0:
                raise DataInputError(f"Missing TransportRatesheet Lane input.",
                                     solution=f"At least one row of data is required with <dest_ctry>.",
                                     file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                     column=f'<dest_ctry>',
                                     values=f"Example: 'PL'")
            return df

        def _normalize_input_data(self):
            # Classify and normalize data
            df = self.input_data.copy()

            # Country of destination '<dest_ctry>' must be always provided
            if df.dest_ctry.isna().any():
                raise DataInputError(f"Missing Country <dest_ctry> in TransportRatesheet Lane input.",
                                     solution=f"Column <dest_ctry> can not be empty if other columns are filled.",
                                     file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                     column=f'<dest_ctry>',
                                     values=f"\n{df[df.dest_ctry.isna()]}")

                # Classify input based on provided data
            df['input_structure'] = df.apply(lambda row: row['dest_ctry'] + ', ' + ', '.join([col for col in df.columns if pd.notna(row[col])]), axis=1)
            df['input_structure'] = df['input_structure'].map({v: f'{i}. {v}' for i, v in enumerate(df['input_structure'].unique())})
            df['input_structure'] = df['input_structure'].astype('string')

            # Step0. Exception for parcel: If only country is provided (and zone is missing), set zone as country
            df.loc[df.dest_zip.isna() & df.dest_zone.isna() & df.transit_time.isna(), 'dest_zone'] = df.dest_ctry

            # Step1. Remove entries where both dest_zone and transit_time are NaN
            mask = df.dest_zone.isna() & df.transit_time.isna()
            df = df.loc[~mask].copy()
            if df.empty:
                raise DataInputError(f"TransportRatesheet does not have any valid input for Lane.",
                                     solution=f"Provide at least single valid row of data (with zone or transit_time).",
                                     file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                     column=f'<dest_ctry><dest_zip><dest_zone><transit_time>')

            # Step2. Replace NaN dest_zip with first zipcode for given country
            df.rename(columns={'dest_zip': 'dest_zip_init'}, inplace=True)
            df['dest_zip'] = df.dest_zip_init
            df.loc[df.dest_zip.isna(), 'dest_zip'] = df.dest_ctry.map(zm.zipcode_clean_first)

            # Step3. Clean zipcode input before allocation to list or range
            # Replace list indicators ';' or '.' with comma
            df['dest_zip'] = df['dest_zip'].str.replace(r'[;.]', ',', regex=True)
            # Keep only a-z, A_Z, 0-9, '-', ','
            df['dest_zip'] = df['dest_zip'].str.replace(r'[^a-zA-Z0-9,-]', '', regex=True)
            # Remove ',' if no chars/number follows it
            df['dest_zip'] = df['dest_zip'].str.replace(r',(?=\s|$|[^a-zA-Z0-9])', '', regex=True)

            # Step4. Expand zipcode input as list (create new rows)
            df['dest_zip'] = df['dest_zip'].str.split(',')
            df = df.explode('dest_zip').reset_index(drop=True)
            df['dest_zip'] = df['dest_zip'].astype('string')
            # Note: Sorting with input_structure is essential to maintain integrity (difference vs previous version)
            df.sort_values(by=['dest_ctry', 'input_structure', 'dest_zip'], inplace=True)

            # Step5. Converts dest_zip to range (zip_from, zip_to). If input is range, split it. If not, zip_to is ps.NA
            df['dest_zip_as_range'] = df['dest_zip'].str.contains(rf'^[a-zA-Z0-9]+-[a-zA-Z0-9]+$')
            df['clean_first'] = df.dest_ctry.map(zm.zipcode_clean_first).astype('string')
            df['clean_last'] = df.dest_ctry.map(zm.zipcode_clean_last).astype('string')
            if df['dest_zip_as_range'].any():  # Without this check, error is raised as only one item exist in list
                df[['dest_zip_from', 'dest_zip_to']] = df['dest_zip'].str.split('-', expand=True).fillna(pd.NA)
            else:
                df['dest_zip_from'] = df['dest_zip']
                df['dest_zip_to'] = pd.NA
                df['dest_zip_to'] = df['dest_zip_to'].astype("string")
            df.loc[df['dest_zip_to'].isna(), 'dest_zip_to'] = df.groupby(['dest_ctry', 'input_structure'])['dest_zip_from'].transform(pd.Series.shift, -1).fillna(np.nan)

            # Step6. Get zip_to range meta (starting or ending).
            df['dest_zip_to_meta'] = self._meta.settings.get('dest_zip_to')
            df['dest_zip_to_meta'] = df['dest_zip_to_meta'].astype('string')
            df.loc[~df.dest_zip_as_range, 'dest_zip_to_meta'] = 'ending'

            # Step7: 'dest_zip_from' as full format (99999: 00-10 -> 00000-...; 10-20 -> 10000-...)
            df['dest_zip_from_clean'] = df.apply(lambda row: zm.clean_zipcode(row['dest_ctry'], row['dest_zip_from']), axis=1)
            df['dest_zip_from_clean'] = df['dest_zip_from_clean'].astype('string')

            # Step8: 'dest_zip_to' with 'starting' as full format (99999: 00-10 -> ...-10999; 10-20 -> ...-20999)
            mask = df.dest_zip_to.notna() & (df.dest_zip_to_meta == 'starting')
            df.loc[mask, 'dest_zip_to_clean'] = df.loc[mask].apply(lambda row: zm.clean_zipcode(row['dest_ctry'], row['dest_zip_to'], variant='last'), axis=1)
            df['dest_zip_to_clean'] = df['dest_zip_to_clean'].astype('string')

            # Step9: 'dest_zip_to' with 'ending' as full format (99999: 00-10 -> ...-09999; 10-20 -> ...-19999)
            mask = df.dest_zip_to.notna() & (df.dest_zip_to_meta == 'ending')
            df.loc[mask, 'dest_zip_to_clean'] = df.loc[mask].apply(lambda row: zm.clean_zipcode(row['dest_ctry'], row['dest_zip_to']), axis=1)
            df.loc[mask, 'dest_zip_to_clean'] = df.loc[mask].apply(lambda row: zm.adjacent_zipcode(row['dest_ctry'], row['dest_zip_to_clean'], direction='previous'), axis=1)

            # Step10. Special case when input is given as all zipcodes in full length (PL - 00000, 00001, ..., 99999)
            #  Turns out it's not needed. For now at least.


            # Step11: 'dest_zip_to' with 'ending' & pd.NA as last full format
            #  (99999: 00-NA -> ...-99999; 10-NA -> ...-99999)
            mask = df.dest_zip_to_clean.isna()
            df.loc[mask, 'dest_zip_to_clean'] = df['clean_last']

            # Step12 - Make sure that 'clean_first' and 'clean_last' in included in zipcode ranges per 'input_structure'
            # Typically, ratesheets start with '01' or '10' (so not include first clean zip). May also not include last.
            # Note: this does not exist in previous version.
            gr = df.groupby(['dest_ctry', 'input_structure'], as_index=False)[['dest_zip_from_clean', 'dest_zip_to_clean', 'clean_first', 'clean_last']].agg({'dest_zip_from_clean': 'min', 'dest_zip_to_clean': 'max', 'clean_first': 'first', 'clean_last': 'first'})

            mask = gr.clean_first < gr.dest_zip_from_clean
            if not gr.loc[mask].empty:
                gr.loc[mask, 'from_first'] = gr.clean_first
                gr.loc[mask, 'from_last'] = gr.loc[mask].apply(lambda row: zm.adjacent_zipcode(row['dest_ctry'], row['dest_zip_from_clean'], direction='previous'), axis=1)
                gr.loc[mask, 'extra_from_range'] = gr.from_first + '-' + gr.from_last
                gr_first = gr.loc[mask, ['input_structure', 'dest_zip_from_clean', 'extra_from_range']].copy()

                df = df.merge(gr_first, how='left', on=['input_structure', 'dest_zip_from_clean'])
                mask = df.extra_from_range.notna()
                df.loc[mask, 'dest_zip_from_clean'] = df.loc[mask, 'extra_from_range'] + ',' + df.loc[mask, 'dest_zip_from_clean']
                df['dest_zip_from_clean'] = df['dest_zip_from_clean'].str.split(',')
                df = df.explode('dest_zip_from_clean').reset_index(drop=True)
                df['dest_zip_from_clean'] = df['dest_zip_from_clean'].astype('string')
                mask_range = df['dest_zip_from_clean'].str.contains(rf'^[a-zA-Z0-9]+-[a-zA-Z0-9]+$', na=False)
                df.loc[mask_range, ['dest_zip_from_clean', 'dest_zip_to_clean']] = df.loc[mask_range, 'dest_zip_from_clean'].str.split('-', expand=True).values
                df.loc[mask_range, 'extra_from_range'] += ' (added)'
                df.loc[df.extra_from_range.notna() & ~df.extra_from_range.str.contains('added'), 'extra_from_range'] += ' (input)'

            mask = gr.clean_last > gr.dest_zip_to_clean
            if not gr.loc[mask].empty:
                gr.loc[mask, 'to_first'] = gr.loc[mask].apply(lambda row: zm.adjacent_zipcode(row['dest_ctry'], row['dest_zip_to_clean'], direction='next'), axis=1)
                gr.loc[mask, 'to_last'] = gr.clean_last
                gr.loc[mask, 'extra_to_range'] = gr.to_first + '-' + gr.to_last
                gr_last = gr.loc[mask, ['input_structure', 'dest_zip_to_clean', 'extra_to_range']].copy()

                df = df.merge(gr_last, how='left', on=['input_structure', 'dest_zip_to_clean'])
                mask = df.extra_to_range.notna()
                df.loc[mask, 'dest_zip_to_clean'] = df.loc[mask, 'dest_zip_to_clean'] + ',' + df.loc[mask, 'extra_to_range']
                df['dest_zip_to_clean'] = df['dest_zip_to_clean'].str.split(',')
                df = df.explode('dest_zip_to_clean').reset_index(drop=True)
                df['dest_zip_to_clean'] = df['dest_zip_to_clean'].astype('string')
                mask_range = df['dest_zip_to_clean'].str.contains(rf'^[a-zA-Z0-9]+-[a-zA-Z0-9]+$', na=False)
                df.loc[mask_range, ['dest_zip_from_clean', 'dest_zip_to_clean']] = df.loc[mask_range, 'dest_zip_to_clean'].str.split('-', expand=True).values
                df.loc[mask_range, 'extra_to_range'] += ' (added)'
                df.loc[df.extra_to_range.notna() & ~df.extra_to_range.str.contains('added'), 'extra_to_range'] += ' (input)'

            return df

        def _set_df_dest_zone(self):
            # Final version for dest zone
            mask_zone = self.output_data.dest_zone.notna()
            columns_zone = ['dest_ctry', 'dest_zip_from_clean', 'dest_zip_to_clean', 'dest_zone']
            df = self.output_data.loc[mask_zone, columns_zone].copy()
            df.rename(columns={'dest_zip_from_clean': 'dest_zip_from', 'dest_zip_to_clean': 'dest_zip_to'}, inplace=True)
            return df

        def _set_df_transit_time(self):
            # Final version for dest zone
            mask_zone = self.output_data.transit_time.notna()
            columns_transit_time = ['dest_ctry', 'dest_zip_from_clean', 'dest_zip_to_clean', 'transit_time']
            df = self.output_data.loc[mask_zone, columns_transit_time].copy()
            df.rename(columns={'dest_zip_from_clean': 'dest_zip_from', 'dest_zip_to_clean': 'dest_zip_to'}, inplace=True)
            return df

        def _set_unique_zones(self):
            return list(self.df_dest_zone.dest_zone.unique())

        # To increase performance in lookups (it's used with bisect)
        @staticmethod
        def _set_fast_lookup_for_lane(dataframe, lookup_item):
            output_dict = {}
            for country, group in dataframe.groupby('dest_ctry'):
                key_function = zm.get_zipcode_key_fn(country)  # This func translate zipcode to unique integer
                output_tuple = []
                for _, row in group.iterrows():
                    key_from_str = row.dest_zip_from
                    key_to_str = row.dest_zip_to
                    key_from = key_function(row.dest_zip_from)
                    key_to = key_function(row.dest_zip_to)
                    output_tuple.append((key_from_str, key_to_str, key_from, key_to, row[lookup_item]))
                # Sort by dest_zip_from (it should be already done in df_dest_zone)
                output_tuple.sort(key=lambda x: x[0])
                zip_from_str, zip_to_str, zip_from, zip_to, item = zip(*output_tuple)
                output_dict[country] = {
                    'dest_zip_from_str': list(zip_from_str), 'dest_zip_to_str': list(zip_to_str),
                    'dest_zip_from': list(zip_from), 'dest_zip_to': list(zip_to),
                    f'{lookup_item}': list(item), 'key_function': key_function
                }
            return output_dict

        def _check_zone_completeness(self):
            # Checks if previous zip from 'dest_zip_from' is equal to 'dest_zip_to' from range above
            df = self.df_dest_zone.copy()
            df['range_to'] = df.apply(lambda row: zm.adjacent_zipcode(row['dest_ctry'], row['dest_zip_from'], 'previous'), axis=1)
            df['range_from'] = df.dest_zip_to.shift(1)
            df['ctry_prev'] = df.dest_ctry.shift(1)
            missing_zips = df.loc[df.range_from.notna() & (df.range_from != df.range_to) & (df.dest_ctry == df.ctry_prev)][['dest_ctry', 'range_from', 'range_to']]
            if not missing_zips.empty:
                raise DataInputError(f'Missing zipcode_ranges in ratesheet:\n{missing_zips}',
                                     solution=f"Check lane input for ratesheet.",
                                     file_path=self._input.file_path,
                                     sheet_name=self._input.sheet_name)

    class _Cost:
        _COST_META_COLUMNS = ['<cost_type>', '<cost_unit>', '<range_value>', '<range_unit>']
        _DEFAULT_MISSING_RANGE_VALUE = 99999999
        _DEFAULT_MISSING_UNIT = 'm3'

        def __init__(self, input_trs, meta_trs):
            self._input = input_trs
            self._meta = meta_trs
            self.input_data = self._get_input_data()
            self.zones = self._get_zones()
            self.df_cost = self._normalize_input_data()
            self.types = self._get_ratesheet_cost_types_from_config()
            self.get_cost = self._get_ratesheet_cost_groups_from_config()
            self.find_cost = self._set_fast_lookup_for_cost()

        def __repr__(self):
            return f"Cost(file_path='{self._input.file_path.parts[-1]}', sheet_name='{self._input.sheet_name}')"

        def _get_input_data(self):
            # Get names of columns for cost
            columns_cost = self._COST_META_COLUMNS[:]
            # columns_zone = [col for col in self._input.input_data.columns[self._input.input_data.columns.get_loc('<range_unit>') + 1:] if not col.startswith('Unnamed:')]
            columns_zone = [col for col in self._input.input_data.columns[self._input.input_data.columns.get_loc('<range_unit>') + 1:] if not str(col).startswith('Unnamed:')]
            columns_cost.extend(columns_zone)

            # Drop empty rows
            df = self._input.input_data.copy().reindex(columns=columns_cost).dropna(how='all', ignore_index=True)

            # Change zone columns to numeric
            for col in df[columns_zone].select_dtypes(include=['object', 'string']).columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Drop empty columns
            df = df.dropna(axis=1, how='all', ignore_index=True)

            df.columns = df.columns.astype('string')
            df.columns = df.columns.str.replace(r'[<>]', '', regex=True)

            if df.empty:
                raise DataInputError(f"Missing TransportRatesheet Cost input.",
                                     solution=f"At least one row of data is required",
                                     file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                     column=f'{columns_cost}')
            return df


        def _get_zones(self):
            cost_columns_strip = [col.strip('<>') for col in self._COST_META_COLUMNS]
            return [col for col in self.input_data.columns if col not in cost_columns_strip]

        def _normalize_input_data(self):
            df = self.input_data.copy()

            # Missing range values and unit are filled with defaults
            if 'range_value' not in df.columns:
                df.insert(df.columns.get_loc('cost_unit') + 1, 'range_value', np.nan)
            if 'range_unit' not in df.columns:
                df.insert(df.columns.get_loc('range_value') + 1, 'range_unit', pd.NA)
                df['range_unit'] = pd.NA

            df['range_value'] = df.range_value.fillna(self._DEFAULT_MISSING_RANGE_VALUE)
            df['range_unit'] = df.range_unit.fillna(self._DEFAULT_MISSING_UNIT)

            # Map ratesheet cost_type to defined in config files (ratesheet.yaml)
            df['cost_type'] = df['cost_type'].replace(sc.config.ratesheet.get('cost_types_mapping'))

            # Convert cost input to reference currency
            setattr(self, 'currency', {
                'input_currency': self._meta.currency.get('currency'),
                'output_currency': self._meta.currency.get('reference_currency'),
            })
            # Convert values to proper currency (exclude cost_types with 'mul' function)
            mask_none_mul_types = ~df.cost_type.isin(sc.config.ratesheet.get('cost_types_function_mul'))
            df.loc[mask_none_mul_types, self.zones] /= self._meta.currency.get('rate')
            # df[self.zones] /= self._meta.currency.get('rate')

            # Add 'range_value_from' for lookup in ShipmentCost
            # Categorical is used for sorting only (to keep same sequence)
            df['cost_type'] = pd.Categorical(df['cost_type'], categories=df.cost_type.drop_duplicates(), ordered=True)
            df.drop_duplicates(['cost_type', 'range_value'], keep='first', inplace=True)
            df.sort_values(by=['cost_type', 'range_value'], inplace=True)
            df.insert(df.columns.get_loc('range_value'), 'range_value_from', df.groupby(['cost_type'], observed=True)['range_value'].transform(pd.Series.shift, 1).fillna(0))
            df['cost_type'] = df.cost_type.astype('string')
            df.rename(columns={'range_value': 'range_value_to'}, inplace=True)

            # Check if there's max one range_unit per cost_type. This is required for Cost class.
            for cost_type, range_unit in df.groupby('cost_type')['range_unit'].unique().items():
                if len(range_unit) > 1:
                    alternative_names = [f'{cost_type}_{unit}' for unit in range_unit]
                    raise DataInputError(f"Cost_type '{cost_type}' has more than one range_unit: '{list(range_unit)}'. Only one is allowed.",
                                         solution=f"Use only one range_unit per cost_type or introduce another cost_type like '{alternative_names}'.",
                                         file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                         column=f'<cost_type><range_unit>',
                                         values=f"<{range_unit}>")
            # ==========================================================================================================
            # Check if all potentially needed units are provided. This is in case ratios are needed and not specified on
            #  shipment level.
            # ==========================================================================================================
            # Step1 - Convert weight and volume units to 'kg' and 'm3'
            # cost_unit change cost in zones
            for cost_unit in df.cost_unit.unique():
                # if cost_unit in volume
                default_volume = 'm3'
                if cost_unit in sc.config.units_of_measure.get('choices').get('volume') and cost_unit != default_volume:
                    mask = (df.cost_unit == cost_unit)
                    df.loc[mask, 'cost_unit'] = default_volume
                    df.loc[mask, self.zones] *= sc.config.units_of_measure.get('conversions').get('volume').get(cost_unit).get(default_volume)
                # if cost_unit in weight
                default_weight = 'kg'
                if cost_unit in sc.config.units_of_measure.get('choices').get('weight') and cost_unit != default_weight:
                    mask = (df.cost_unit == cost_unit)
                    df.loc[mask, 'cost_unit'] = default_weight
                    df.loc[mask, self.zones] *= sc.config.units_of_measure.get('conversions').get('weight').get(cost_unit).get(default_weight)
            # range_unit change cost in zones
            for range_unit in df.range_unit.unique():
                # if range_unit in volume
                default_volume = 'm3'
                if range_unit in sc.config.units_of_measure.get('choices').get('volume') and range_unit != default_volume:
                    mask = (df.range_unit == range_unit)
                    df.loc[mask, 'range_unit'] = default_volume
                    df.loc[mask, 'range_value_to'] /= sc.config.units_of_measure.get('conversions').get('volume').get(range_unit).get(default_volume)
                # if range_unit in weight
                default_weight = 'kg'
                if range_unit in sc.config.units_of_measure.get('choices').get('weight') and range_unit != default_weight:
                    mask = (df.range_unit == range_unit)
                    df.loc[mask, 'range_unit'] = default_weight
                    df.loc[mask, 'range_value_to'] /= sc.config.units_of_measure.get('conversions').get('weight').get(range_unit).get(default_weight)
                    df.loc[mask, 'range_value_from'] /= sc.config.units_of_measure.get('conversions').get('weight').get(range_unit).get(default_weight)

            # ==========================================================================================================
            # Step2 - Determine quantities/drivers (for cost and range units)
            # There are 2 options to get driver value.
            # 1. From meta.custom_ratios (best works with volume, kg, pallets, etc.)
            # 2. from meta.custom_defaults (best for surcharges like shipment, drop, long_prod, whs operations, etc.)
            # If driver is not given in one of the two, error will be raised to add it.
            # ==========================================================================================================
            # Get all
            units = list(pd.unique(df[['cost_unit', 'range_unit']].values.ravel()))
            setattr(self, 'units', units)
            for unit in units:
                if unit not in self._meta.custom_ratios and unit not in self._meta.custom_defaults:
                    raise DataInputError(f"Missing default quantity driver for ratesheet unit: '{unit}'.",
                                         solution=f"Add value to <custom_ratios> e.g. '{unit}/m3=1' or to <custom_defaults> e.g. '{unit}=0'",
                                         file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                         column=f'<meta><custom_ratios>|<custom_defaults>',
                                         values=f"<{unit}>")
            return df

        def _get_ratesheet_cost_types_from_config(self):
            # Get unique cost_types in ratesheet, check if exist in config, filter config cost_types to existing in ratesheer
            ratesheet_cost_types = self.df_cost['cost_type'].unique()

            # Check if each ratesheet_cost_type exists in config file (ratesheet.yaml/cost_groups) and has defined functional_behaviour
            for ratesheet_cost_type in ratesheet_cost_types:
                if ratesheet_cost_type not in (config_cost_types:=sc.config.ratesheet.get('cost_types')):
                    available_options = {cost_type: list(cost_type_items.get('mapping')) for cost_type, cost_type_items in config_cost_types.items()}
                    raise DataInputError(f"Ratesheet <cost_type> '{ratesheet_cost_type}' not found in ratesheet config file (ratesheet.yaml/cost_groups).\nCurrently available options and mapping list: {available_options} ",
                                         solution=f"Add '{ratesheet_cost_type}' to one of cost_groups or add it's name to cost_type.mapping.",
                                         file_path=self._input.file_path, sheet_name=self._input.sheet_name,
                                         column=f'<cost_type>',
                                         values=f"'{ratesheet_cost_type}'")

            # Filter config cost_types to those that exist in ratesheet
            config_cost_types = {cost_type: cost_type_items for cost_type, cost_type_items in sc.config.ratesheet.get('cost_types').items() if cost_type in ratesheet_cost_types}
            return config_cost_types

        def _get_ratesheet_cost_groups_from_config(self):
            # This is dict supporting shipment cost calculation.
            # Filter cost_groups and cost_Types relevant for ratesheet

            # Get ratesheet cost_groups
            rs_cost_groups_unique = []
            for ct, ct_items in self.types.items():
                rs_cost_groups_unique.append(ct_items.get('cost_group'))
            rs_cost_groups_unique = list(set(rs_cost_groups_unique))

            # Copy config cost_groups if exist in ratesheet (including cost_types that are not in ratesheet)
            ratesheet_cost_groups = {}
            for config_cost_group, config_cost_items in sc.config.ratesheet.get('cost_groups').items():
                # Check if cg exist in ratesheet
                if config_cost_group not in rs_cost_groups_unique:
                    continue
                # config_cost_items have nested dicts for functions. Without deepcopy, config.ratesheet.cost_groups were overwritter
                ratesheet_cost_groups.update({config_cost_group: copy.deepcopy(config_cost_items)})

            # Remove cost_types that does not exist in ratesheet
            for cg, cg_items in ratesheet_cost_groups.items():
                cg_items['cost_types'] = [ct for ct in cg_items.get('cost_types') if ct in self.types]
                # Remove from 'cost_types'
                for func, func_ct in cg_items.get('functions').items():
                    cg_items['functions'][func] = [ct for ct in func_ct if ct in self.types]
                # Sort functions
                cg_items['functions'] = {k: cg_items['functions'][k] for k in sorted(cg_items['functions'], key=lambda x: ['sum', 'max', 'mul'].index(x))}
            return ratesheet_cost_groups

        def _set_fast_lookup_for_cost(self):
            output_dict = {}
            for zone in self.zones:
                cost_type_dict = {}
                for cost_type, group in self.df_cost.groupby('cost_type'):
                    cost_tuple = []
                    for _, row in group.iterrows():
                        cost_tuple.append((row.range_unit, row.range_value_from, row.range_value_to, row.cost_unit, row[zone]))
                    # Sorting and converting that to lists
                    cost_tuple.sort(key=lambda x: x[1])  # Sort on 2nd element (just for sure, as df_cost is already sorted)
                    range_unit, range_value_from, range_value_to, cost_unit, cost = zip(*cost_tuple)
                    cost_type_dict[cost_type] = {
                        'range_unit': list(range_unit)[0],
                        'range_value_from': list(range_value_from),
                        'range_value_to': list(range_value_to),
                        'cost_unit': list(cost_unit),
                        'cost_rate': list(cost),
                    }

                output_dict[zone] = cost_type_dict

            return output_dict


def merge_ratesheets(first_ratesheet, second_ratesheet, use_zone=None):
    """
    Add all cost input from second_ratesheet to first_ratesheet to improve ratesheet management.
    Example: user can combine transport cost_types with warehouse cost_types without multiplying info in each rs.
    :param first_ratesheet:
    :param second_ratesheet:
    :param use_zone: zone in ratesheet2 to be applied to ratesheet1
    :return: deepcopy of first_ratesheet
    """

    # todo temp args
    rs1 = copy.deepcopy(first_ratesheet)
    rs2 = copy.deepcopy(second_ratesheet)

    # Get zone from rs2 to be appended to all zones from rs1
    if use_zone is None:
        zone = rs2.cost.zones[0]
    else:
        zone = use_zone
        if zone not in rs2.cost.zones:
            raise DataInputError(f"use_zone '{zone}' not found in ratesheet: '{rs2}'.",
                                 solution=f"Pick existing zone available in cost zones: {rs2.cost.zones}",
                                 file_path=rs2.input.file_path, sheet_name=rs2.input.sheet_name,
                                 column=f'<dest_zone> and cost_zones',
                                 values=f"<{zone}>")

    # Update df_cost. Note currency is always set to EUR as we are working on processed worksheets.
    _needed_columns = ['cost_type', 'cost_unit', 'range_value_from', 'range_value_to', 'range_unit', zone]
    df_cost2 = rs2.cost.df_cost[_needed_columns].copy()
    for z in rs1.cost.zones:
        df_cost2[z] = df_cost2[zone]
    df_cost2.drop(columns=zone, inplace=True)
    rs1.cost.df_cost = pd.concat([rs1.cost.df_cost.copy(), df_cost2])

    # Rerun script with new df_cost
    rs1.cost.types = rs1.cost._get_ratesheet_cost_types_from_config()
    rs1.cost.get_cost = rs1.cost._get_ratesheet_cost_groups_from_config()
    rs1.cost.find_cost = rs1.cost._set_fast_lookup_for_cost()

    # Update units and inputs
    rs1.cost.units = list(set(rs1.cost.units + rs2.cost.units))
    rs1.combines.append(repr(rs2))

    return rs1


if __name__ == '__main__':
    rs1 = Ratesheet(Path(sc.path.resources /'ratesheets/ratesheets A.xlsb'), 's1')
    rs2 = Ratesheet(Path(sc.path.resources /'ratesheets/ratesheets B.xlsb'), 'a1')
    rs3 = merge_ratesheets(rs1, rs2)
