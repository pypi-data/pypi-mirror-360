import yaml
import pandas as pd
from pathlib import Path
from simera.utils import DataInputError, compute_all_conversions_between_units_in_ratios
# future - Config url_resources via os.environ to resources on company sharepoint for local employees use.
# todo - config is kept as package to allow inserting yaml file. Probably that's not needed.
#  Yaml can be replace with CONST inside class, as user will not change that anyhow.

class Config:
    """Handles configuration file loading and resource path management."""

    def __init__(self, url_resources=None):
        self.path = self._Path(url_resources)
        self.config = self._Config(self.path)

    def __repr__(self):
        return 'SimeraConfig'

    class _Path:
        """Handles directory paths for resources and configurations."""

        def __init__(self, url_resources):
            # Path to folder where app is installed
            self.base_dir = Path.cwd().resolve()
            # Path to user configuration files
            self.resources = Path(url_resources).resolve() if url_resources else self.base_dir / 'simera_resources'
            # Path to builtin configuration files in config package
            self.config = Path(__file__).resolve().parent

            # For running and testing with interactive interpreter __file__ is <input>:
            if __file__.startswith('<'):
                self.config = Path.cwd() / 'simera/config'

    class _Config:
        """Loads and manages configuration settings from YAML files."""

        def __init__(self, path):
            self._path = path
            # Builtin
            yaml_country = self._path.config / 'country.yaml'
            # todo: country should be moved to resources. Currently is not used. Initially stored
            #  Application example: mapping ctry to region to be used in

            # Resources
            yaml_currency = self._path.resources / 'config' / 'currency.yaml'
            yaml_units_of_measure = self._path.resources / 'config' / 'units_of_measure.yaml'
            yaml_ratesheet = self._path.resources / 'config' / 'ratesheet.yaml'
            yaml_sites = self._path.resources / 'config' / 'sites.yaml'

            # Country attributes
            self.country = self.setup_country(yaml_country)

            # Currency default and rates
            self.currency = self.setup_currency(yaml_currency)

            # Units of Measure
            self.units_of_measure = self.setup_units_of_measure(yaml_units_of_measure)

            # Transport setup
            self.ratesheet = self.setup_ratesheet(yaml_ratesheet)

            # Warehouse setup
            self.site = self.read_yaml(yaml_sites)

        @staticmethod
        def read_yaml(file_path):
            """Reads a YAML configuration file and returns its contents."""
            try:
                with file_path.open('r', encoding='utf-8') as file:
                    return yaml.safe_load(file) or {}
            except FileNotFoundError:
                print(f"Warning: {file_path.name} not found at {file_path}. Returning an empty dictionary.")
                return {}
            except yaml.YAMLError as e:
                print(f"Error parsing {file_path}: {e}")
                return {}

        def setup_country(self, file_path):
            return self.read_yaml(file_path)

        def setup_currency(self, file_path):
            """Consolidate builtin and resource config for currency. """
            data = self.read_yaml(file_path)

            # Default currency. If None, set EUR
            default_currency = data.get('default', 'EUR')

            # Exchange rates. If rates are not provided, set only default to default = 1 (e.g. {EUR: {EUR: 1}}
            rates = data.get('rates', {default_currency: {default_currency: 1}})

            currency = {}
            currency.update({'default': default_currency})
            currency.update({'rates': rates})
            return currency

        def setup_units_of_measure(self, file_path):
            data = self.read_yaml(file_path)

            # Default
            default = data.get('default')

            # Conversions
            conversions = data.get('conversions')
            for key, value in conversions.items():
                conversions.update({key: compute_all_conversions_between_units_in_ratios(value)})

            # Choices based on keys in conversions
            choices = {key: list(value.keys()) for key, value in conversions.items()}
            choices.update({'volume_and_weight': choices.get('volume') + choices.get('weight')})

            # Consolidate all
            units_of_measure = {}
            units_of_measure.update({'default': default})
            units_of_measure.update({'choices': choices})
            units_of_measure.update({'conversions': conversions})

            # Validation - default uom is in list of choices for given category
            for key, value in units_of_measure.get('default').items():
                if value not in (choices_list := units_of_measure.get('choices').get(key)):
                    raise DataInputError(f"Invalid 'default Unit of Measure' for '{key}'. '{value}' is not in choices list '{choices_list}'",
                                         solution = f"Change 'default' value or update 'choices' and 'conversions' in config file. ",
                                         file_path=f"{file_path}",
                                         values=f"{value}, allowed: {choices_list}")
            return units_of_measure

        def setup_ratesheet(self, file_path):
            """Initial transport settings for ratesheets"""

            data = self.read_yaml(file_path)

            # Custom ratios
            custom_ratios = data.get('custom_ratios', {'shipment per shipment': 1})
            custom_ratios = compute_all_conversions_between_units_in_ratios(custom_ratios, keep_none=False)

            config_volume_choices = self.units_of_measure.get('choices').get('volume')
            config_weight_choices = self.units_of_measure.get('choices').get('weight')
            config_choices_volume_and_weight = self.units_of_measure.get('choices').get('volume_and_weight')

            # Custom defaults
            custom_defaults = data.get('custom_defaults', {'shipment': 1})

            # CostGroups
            cost_groups = data.get('cost_groups')
            if cost_groups is None:  # todo: cost_groups input check
                raise DataInputError(f"Missing input for cost_groups.",
                                     solution = f"Set 'cost_group' attributes in config file. ",
                                     file_path=f"{file_path}")

            # Convert CostGroups to flat dataframe (for easier conversions in next steps)
            rows = []
            for cg_key, cg_val in cost_groups.items():
                for ct_key, ct_val in cg_val['cost_types'].items():
                    # In case only CostType header is defined
                    if ct_val is None:
                        ct_val = {'function': 'sum'}
                    row = {
                        # CostGroup
                        'cg_id': cg_key,
                        'cg_display': cg_val.get('display', cg_key),
                        'cg_describe': cg_val.get('describe', cg_key),
                        # CostType
                        'ct_id': ct_key,
                        'ct_function': ct_val.get('function', 'sum'),
                        'ct_mapping': ct_val.get('mapping', []),
                        'ct_chargeable_ratios': ct_val.get('chargeable_ratios', False),
                        'ct_describe': ct_val.get('describe', ct_key),
                        'ct_display': ct_val.get('display', ct_key)
                    }
                    rows.append(row)
            df_cost_groups = pd.DataFrame(rows)

            # Get relevant attributes per cost group
            cost_groups = df_cost_groups.groupby('cg_id').agg(display=('cg_display', 'first'), describe=('cg_describe', 'first'), cost_types=('ct_id', list)).to_dict(orient='index')
            # Add all function with cost type to each group
            all_funcs = list(df_cost_groups['ct_function'].unique())
            func_table = df_cost_groups.groupby(['cg_id', 'ct_function'])['ct_id'].agg(list).unstack(fill_value=[]).reindex(columns=all_funcs, fill_value=[])
            for cg_id, row in func_table.iterrows():
                cost_groups[cg_id]['functions'] = row.to_dict()

            # Get relevant attributes per cost type
            use_columns = {'ct_function': 'function', 'ct_display': 'display', 'ct_describe': 'describe',
                           'ct_chargeable_ratios': 'chargeable_ratios', 'cg_id': 'cost_group', 'ct_mapping': 'mapping'}
            cost_types = df_cost_groups.rename(columns=use_columns).set_index('ct_id')[use_columns.values()].to_dict(orient='index')

            # Get mul cost function (in ratesheet should not be converted to currency)
            cost_types_function_mul = df_cost_groups.loc[df_cost_groups.ct_function.isin(['mul'])]['ct_id'].unique()
            # Get all cost functions
            # cost_functions = df_cost_groups.groupby('ct_function').agg(cost_types=('ct_id', list)).to_dict(orient='index')

            # Get all cost types mapping
            df_exploded = df_cost_groups.explode('ct_mapping').dropna(subset=['ct_mapping'])
            cost_types_mapping = dict(zip(df_exploded['ct_mapping'], df_exploded['ct_id']))

            # Shipment and package max size
            size_max = {}
            attributes = ['shipment_size_max', 'package_size_max']
            for attribute in attributes:
                attribute_size_max = data.get(attribute)
                size_max.update({attribute: {}})
                # Process per each transport mode separately
                for trpmode, value_per_uom in attribute_size_max.items():
                    size_max.get(attribute).update({trpmode: {}})
                    volume_init = {}
                    weight_init = {}
                    for uom, value in value_per_uom.items():
                        if uom not in config_choices_volume_and_weight:
                            raise DataInputError(f"Invalid Unit '{uom}' for '<{attribute}>'. "
                                                 f"Available weight & volume choices: '{config_choices_volume_and_weight}'.",
                                                 solution=f"Set correct unit.",
                                                 file_path=file_path,
                                                 values=f"<{attribute}><{trpmode}><{uom}:{value}>"
                                                 )
                        if uom in config_volume_choices and value is not None:
                            volume_init.update({uom: value})
                        if uom in config_weight_choices and value is not None:
                            weight_init.update({uom: value})

                    # Calculate values for weight and volume in kg and m3
                    volume_converted_to_m3 = {f'{k} => m3': round(v / self.units_of_measure['conversions']['volume'][k]['m3'], 5) for k, v in volume_init.items()}
                    weight_converted_to_kg = {f'{k} => kg': round(v / self.units_of_measure['conversions']['weight'][k]['kg'], 5) for k, v in weight_init.items()}

                    # Get minimum values for shipment size (if more than 1 value provided for uom)
                    volume_size = min(volume_converted_to_m3.values()) if volume_converted_to_m3 else None
                    weight_size = min(weight_converted_to_kg.values()) if weight_converted_to_kg else None

                    # Set attributes that will be used in script
                    size_max.get(attribute).get(trpmode).update({'m3': volume_size})
                    size_max.get(attribute).get(trpmode).update({'kg': weight_size})
                    size_max.get(attribute).get(trpmode).update({'_volume_config_input': volume_init})
                    size_max.get(attribute).get(trpmode).update({'_volume_config_calculation': f'Config: {volume_converted_to_m3}' if volume_converted_to_m3 else None})
                    size_max.get(attribute).get(trpmode).update({'_weight_config_input': weight_init})
                    size_max.get(attribute).get(trpmode).update({'_weight_config_calculation': f'Config: {weight_converted_to_kg}' if weight_converted_to_kg else None})

            transport_ratesheet = {}
            transport_ratesheet.update({'custom_ratios': custom_ratios})
            transport_ratesheet.update({'custom_defaults': custom_defaults})
            transport_ratesheet.update({'df_cost_groups': df_cost_groups})
            transport_ratesheet.update({'cost_groups': cost_groups})
            transport_ratesheet.update({'cost_types': cost_types})
            transport_ratesheet.update({'cost_types_function_mul': cost_types_function_mul})
            # transport_ratesheet.update({'cost_functions': cost_functions})
            transport_ratesheet.update({'cost_types_mapping': cost_types_mapping})
            transport_ratesheet.update(size_max)

            return transport_ratesheet

if __name__ == '__main__':
    sc = Config()
