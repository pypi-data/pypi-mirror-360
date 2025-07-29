import bisect
import math
from copy import deepcopy
from typing import Mapping
from tqdm import tqdm
from simera.shipment import sc
from simera.utils import DataInputError


class Cost:
    # Class variables - defaults and choices
    # Note: config values are taken from sc.config (not from ratesheet) as ratesheet could have older version
    _config_ratesheet_cost_types = sc.config.ratesheet.get('cost_types')
    _total_name = 'total'  # Name for totals

    def __init__(self, shipment, ratesheet):
        self.sh = shipment
        self.rs = ratesheet

        # Finding zone and transit time
        self.zone = self._get_dest_zone()
        self.transit_time = self._get_transit_time()

        # Shipment data unique to ratesheet
        self.sh_units = self.sh.units.copy()

        # Cost calculation process
        self.cost_types = self._process_cost_types()
        self.cost_groups, self.cost_total = self._process_cost_groups()
        self.cost_breakdown = self._get_cost_breakdown()

        # Shipment summary
        self.cost_summary = self._get_shipment_summary()

    def __repr__(self):
        return 'ShipmentCost'

    def _get_dest_zone(self):
        # dest_zone can be already provided with shipment.lane. If not, found it based on dest_ctry and dest_zip
        if (zone := self.sh.lane.get('dest_zone')) is None:
            # Check if country is in ratesheet.find_dest_zone
            ctry_attributes = self.rs.lane.find_dest_zone.get(self.sh.lane.get('dest_ctry'))
            if ctry_attributes is None:
                raise DataInputError(f"Ratesheet '{self.rs}' have no requested 'dest_ctry' for shipment: id='{self.sh.id}' (dest_ctry='{self.sh.lane.get('dest_ctry')}', dest_zip='{self.sh.lane.get('dest_zip')})'",
                                     solution=f"Exclude ratesheet from cost calculation input or add 'dest_ctry' to lane. Countries covered: '{'-'.join(self.rs.shortcuts.dest_countries)}'.")

            integer_key = ctry_attributes['key_function'](self.sh.lane.get('dest_zip'))
            position_in_list = bisect.bisect_right(ctry_attributes['dest_zip_from'], integer_key) - 1
            # Just to confirm it was found properly
            if position_in_list >= 0 and integer_key <= ctry_attributes['dest_zip_to'][position_in_list]:
                return ctry_attributes['dest_zone'][position_in_list]
            else:
                raise DataInputError(f"'dest_zone' not found for shipment: id='{self.sh.id}' (dest_ctry='{self.sh.lane.get('dest_ctry')}', dest_zip='{self.sh.lane.get('dest_zip')})'",
                                     solution=f"Check lane input for ratesheet: '{self.rs}'.")
        else:
            return zone

    def _get_transit_time(self):
        # Transit time can be missing in ratesheet.
        ctry_attributes = self.rs.lane.find_transit_time.get(self.sh.lane.get('dest_ctry'))
        if ctry_attributes is None:
            return None
        else:
            integer_key = ctry_attributes['key_function'](self.sh.lane.get('dest_zip'))
            position_in_list = bisect.bisect_right(ctry_attributes['dest_zip_from'], integer_key) - 1
            # Just to confirm it was found properly
            if position_in_list >= 0 and integer_key <= ctry_attributes['dest_zip_to'][position_in_list]:
                return ctry_attributes['transit_time'][position_in_list]

    @staticmethod
    def calculate_packages(shipment_units, package_size_max):
        """
        Calculate the number of packages needed based on shipment units and package size limits.
        Args:
            shipment_units (dict): Dictionary containing shipment quantities by unit type
            package_size_max (dict): Dictionary containing maximum allowed quantities per package by unit type
        Returns:
            dict: Dictionary with 'package' key containing the number of packages needed
        """
        # If package_size_max is empty, return 1 package
        if not package_size_max:
            return {'package': 1}

        max_packages = 1  # Start with 1 package minimum

        # Check each unit in package_size_max
        for unit, max_per_package in package_size_max.items():
            # Only calculate if the unit exists in shipment_units
            if unit in shipment_units:
                shipment_quantity = shipment_units[unit]

                # Calculate packages needed for this unit (round up)
                packages_needed = math.ceil(shipment_quantity / max_per_package)

                # Keep the maximum packages needed across all units
                max_packages = max(max_packages, packages_needed)

        return {'package': max_packages}

    @staticmethod
    def split_shipment_units(shipment_units: dict, shipment_size_max: dict) -> dict:
        """
        Splits shipment_units into 'full' and 'rest' blocks based on one or more constraints of shipment_size_max.
        Uses 'total_shipments' in each block to indicate how many sub-shipments were created.
        """
        # No constraints → single shipment
        if not shipment_size_max:
            return {'full': {'total_shipments': 1, **shipment_units}}

        # Compute split ratios for each constrained unit
        ratios = {}
        for u, max_u in shipment_size_max.items():
            orig = shipment_units.get(u, 0)
            if max_u > 0:
                ratios[u] = orig / max_u

        # If nothing exceeds its max, return one shipment of everything
        if not ratios or all(r <= 1 for r in ratios.values()):
            return {'full': {'total_shipments': 1, **shipment_units}}

        # Pick the “driver” unit with the largest ratio
        driver = max(ratios, key=ratios.get)
        max_driver = shipment_size_max[driver]
        orig_driver = shipment_units.get(driver, 0.0)

        # How many full loads, and what’s left?
        full_count = int(orig_driver // max_driver)
        remainder  = orig_driver - full_count * max_driver

        # Build a block that carries `amount_driver` of the driver unit
        def build_block(amount_driver: float, num_shipments: int):
            block = {'total_shipments': num_shipments}
            scale = (amount_driver / orig_driver) if orig_driver else 0
            for k, v in shipment_units.items():
                if k == 'total_shipments':
                    # skip scaling the original count key
                    continue
                block[k] = v * scale
            return block
        result = {}
        if full_count > 0:
            result['full'] = build_block(max_driver, full_count)
            result['full'].update({'shipment': 1})  # To make sure all is evaluated as 1 shipment
        if remainder > 0:
            result['rest'] = build_block(remainder, 1)  # To make sure all is evaluated as 1 shipment
            result['rest'].update({'shipment': 1})
        return result

    def merge_full_and_rest(self, d1, d2, parent_keys=None):
        """
        Recursively merges d2 into d1, summing numeric leaves,
        except that if key == 'mul' and it's directly under a top-level
        group (i.e. parent_keys length == 1), we take d1['mul'] verbatim.
        """
        if parent_keys is None:
            parent_keys = []
        result = deepcopy(d1)

        for key, val in d2.items():
            if key in result:
                # special case: top‐level mul under 'full'/'rest'
                if key == 'mul' and len(parent_keys) == 1:
                    # just take the 'full' side wholesale
                    result[key] = deepcopy(result[key])
                elif isinstance(val, Mapping) and isinstance(result[key], Mapping):
                    # recurse, carrying the current key in the path
                    result[key] = self.merge_full_and_rest(
                        result[key], val, parent_keys + [key]
                    )
                else:
                    # normal numeric leaf: sum
                    result[key] = result[key] + val
            else:
                # new key entirely: copy it in
                result[key] = deepcopy(val)
        return result

    def _process_cost_types(self):
        # Processing all cost_types relevant to ratesheet

        # Naming convention
        m3_chargeable = 'm3_chg'
        kg_chargeable = 'kg_chg'

        # Step1. If ratesheet has chargeable_ratios, make sure that shipment have both weight and volume units provided.
        # Note: volume and weight shipment units (if present) are automatically converted to m3 and kg in Shipment class.
        if (chargeable_ratio_kg_per_m3:=self.rs.meta.chargeable_ratios.get('kg/m3')) is not None:
            shipment_kg = self.sh_units.get('kg')
            shipment_m3 = self.sh_units.get('m3')
            if shipment_kg is None or shipment_m3 is None:
                raise DataInputError(f"Shipment misses volume and/or weight units that are required to calculate chargeable units for ratesheet '{self.rs.input}'.\n"
                                     f"Available volume units: {[i for i in self.sh_units if i in self.sh._config_choices_volume]}\n"
                                     f"Available weight units: {[i for i in self.sh_units if i in self.sh._config_choices_weight]}",
                                     solution=f"Add missing units to shipment.")
            shipment_m3_chargeable = max(shipment_kg * (1/chargeable_ratio_kg_per_m3), shipment_m3)
            shipment_kg_chargeable = max(shipment_m3 * chargeable_ratio_kg_per_m3, shipment_kg)
            # Add chargeable values to shipment.units
            self.sh_units.update({m3_chargeable: shipment_m3_chargeable,
                                  kg_chargeable: shipment_kg_chargeable})

        # ==============================================================================================================
        # Calculate nb of packages in shipment with <package_max_size>
        # ==============================================================================================================
        # Add to shipment.units nb of packages ('package': x) based on package_max_size.func_input
        # Note: splitting of shipments is based on standard weight and volume (not chargeable).
        #  Package size max is assumed to be related to physical constraints, that may trigger cost in other areas.
        self.sh_units.update(self.calculate_packages(self.sh_units, self.rs.meta.package_size_max.get('func_input', {})))

        # ==============================================================================================================
        # Split shipment if exceeds <shipment_max_size>
        # ==============================================================================================================
        # Convert shipment.units into shipment.units_max_size
        # Note: splitting of shipments is based on standard weight and volume. It's before chargeable ratio is applied.
        #  Shipment size max is assumed to be related to physical constraints, while chargeable weight only to cost.
        setattr(self, 'sh_units_max_size', self.split_shipment_units(self.sh_units, self.rs.meta.shipment_size_max.get('func_input', {})))

        # todo: loop over units_split per cost_type. Not sure if it's enough to simply replace units with units_split
        #  Make sure somwhere below units are not updated (if are should be updated as units_split)
        #  Run cost calculation for full and rest, apply * total_shipments and summaries the cost
        #  Make sute that if no split is needed, speed betweem units and units_split is same

        # Process separately for 'full' and 'rest' units_max_size
        output_per_category = {}
        for unit_category, shipment_units in self.sh_units_max_size.items():

            # Step2: Processing of cost_types separately.
            output = {}
            for cost_type, cost_type_items in self.rs.cost.find_cost.get(self.zone).items():
                range_unit = cost_type_items.get('range_unit')
                # Check if chargeable ratios should be applied to cost_type (when chargeable_ratio exist in ratesheet and cost_type have chargeable_ratio=True)
                # if so, overwrite range_unit to chargeable m3_chg or kg_chg
                chargeable_ratio_in_ratesheet = chargeable_ratio_kg_per_m3 is not None
                chargeable_ratio_in_cost_type = self._config_ratesheet_cost_types.get(cost_type, {}).get('chargeable_ratios', False)
                use_chargeable_ratios = chargeable_ratio_in_ratesheet and chargeable_ratio_in_cost_type
                # Apply chargeable part1/2. To range unit
                if use_chargeable_ratios:
                    range_unit = {'m3': m3_chargeable, 'kg': kg_chargeable}.get(range_unit, range_unit)

                # shipment_unit_value = self.shipment.units.get(range_unit)
                shipment_unit_value = shipment_units.get(range_unit)

                # Check if shipment.units has required range_unit
                if shipment_unit_value is None:
                    raise DataInputError(f"Ratesheet range_unit '{range_unit}' not found in shipment data: {shipment_units}"
                                         f"\nReference: shipment={self.sh}, ratesheet={self.rs}",
                                         solution=f"Make sure shipment has all required units. Example: '{range_unit}: 10'")

                # Determine position in range_value that will be used for shipment_unit_value
                position_in_list = max(bisect.bisect_left(cost_type_items.get('range_value_from'), shipment_unit_value) - 1, 0)
                # Check if shipment units value does not exceed ratesheet max range_value for given cost_type
                if shipment_unit_value > cost_type_items['range_value_to'][position_in_list]:
                    raise DataInputError(
                        f"Shipment unit '{range_unit}: {shipment_unit_value}' exceeds max range_value for cost_type '{cost_type}: {max(cost_type_items.get('range_value_to'))} [{range_unit}]' "
                        f"\nReference: shipment={self.sh}, ratesheet={self.rs}",
                        solution=f"Make range_value bigger or reduce shipment size for unit '{range_unit}'")

                # Apply chargeable part2/2. To cost unit
                cost_unit = cost_type_items.get('cost_unit')[position_in_list]
                if use_chargeable_ratios:
                    cost_unit = {'m3': m3_chargeable, 'kg': kg_chargeable}.get(cost_unit, cost_unit)

                # Build cost_type_items
                output[cost_type] = {
                    'chargeable_ratios': use_chargeable_ratios,
                    'range_unit': range_unit,
                    'range_value_shipment': shipment_unit_value,
                    'range_value_from': cost_type_items.get('range_value_from')[position_in_list],
                    'range_value_to': cost_type_items.get('range_value_to')[position_in_list],
                    'range_position_in_list': position_in_list,
                    'cost_unit': cost_unit,
                    'cost_rate': cost_type_items.get('cost_rate')[position_in_list],
                }

                # Adding shipment unit to cost_type
                # <SpecialCase> For cost_types with function: 'mul' (surcharges/discounts), cost_unit is set to 'cost_value'
                if self.rs.cost.types.get(cost_type).get('function') == 'mul':
                    output[cost_type].update({
                        'cost_unit': 'cost_value',
                        'shipment_unit_value': 1,
                        'shipment_unit_value_origin': 'auto-script-mul'})
                else:
                    if (cost_unit := output[cost_type].get('cost_unit')) not in shipment_units:
                        raise DataInputError(f"Cost unit '{cost_unit}' does not exist in shipments units '{shipment_units}'",
                                             solution=f"Add '{cost_unit}' to shipment.units")
                    else:
                        output[cost_type].update(
                            {'shipment_unit_value': shipment_units.get(cost_unit),
                             'shipment_unit_value_origin': '(tbd) provided_with_data'}
                            # todo: Calculated from Receipt, Taken from Assumptions (inc list of assumption)
                        )
                output_per_category.update({unit_category: output})
        return output_per_category

    def _process_cost_groups(self):
        # Calculation of cost inside each cost_group. Summarizing ('sum'), applying minimum_charge ('max') and
        # final surcharge/discounts ('mul')

        output_per_category = {}
        # Separately for 'full' and 'rest'
        for category, cost_types_per_category in self.cost_types.items():
            _total_shipments = self.sh_units_max_size[category]['total_shipments']

            # Process each cost_group and their functions
            cost_groups_per_category = {}
            for cost_group, cost_group_items in self.rs.cost.get_cost.items():
                cost_groups_per_category.update({cost_group: {'total_shipments': _total_shipments}})

                # Step1 - Calculation inside function per cost_group
                for function, cost_types in cost_group_items['functions'].items():
                    # Some function will not have cost_types, skip those
                    if cost_types:
                        cost_groups_per_category[cost_group].update({function: {}})
                        cost_values = []
                        for cost_type in cost_types:
                            cost_value = round(cost_types_per_category.get(cost_type).get('cost_rate') * cost_types_per_category.get(cost_type).get('shipment_unit_value'), 6)
                            # For function with 'sum' and 'max' multiply with total_shipments, for 'mul', not
                            if function in ['sum', 'max']:
                                cost_value *= _total_shipments
                            cost_groups_per_category[cost_group][function].update({f'{cost_type}': cost_value})
                            cost_values.append(cost_value)
                        # Final aggregation based on function type:
                        if function == 'sum':
                            cost_groups_per_category[cost_group][function].update({self._total_name: sum(cost_values)})
                        if function == 'max':
                            cost_groups_per_category[cost_group][function].update({self._total_name: max(cost_values)})
                        if function == 'mul':
                            cost_groups_per_category[cost_group][function].update({self._total_name: math.prod(cost_values)})

            # Step2 - Calculate inside cost_group
            total_cost = 0
            for cost_group, cost_group_items in cost_groups_per_category.items():
                _sum = cost_group_items.get('sum', {}).get(self._total_name, 0)
                _max = cost_group_items.get('max', {}).get(self._total_name, 0)
                _mul_rate = cost_group_items.get('mul', {}).get(self._total_name, 1)
                _sum_max = max(_sum, _max)
                _mul = (_sum_max * _mul_rate) - _sum_max
                _all = _sum_max + _mul
                cost_group_items.update({self._total_name: {'sum_max': _sum_max, 'mul': _mul, self._total_name: _all}})
                total_cost += _all
            cost_groups_per_category.update({self._total_name: {self._total_name: {self._total_name: total_cost}}})
            output_per_category.update({category: cost_groups_per_category})

        # Summarize full end rest to 'total'
        full = output_per_category.get('full', {})
        rest = output_per_category.get('rest')
        if rest is None:
            output_per_category[self._total_name] = full
        else:
            output_per_category[self._total_name] = self.merge_full_and_rest(full, rest)

        total_cost = output_per_category[self._total_name][self._total_name][self._total_name][self._total_name]
        return output_per_category, total_cost

    def _get_cost_breakdown(self):
        breakdown = {}
        for cost_group, cost_group_items in self.cost_groups.get(self._total_name).items():
            for function, function_items in cost_group_items.items():
                if function != 'total_shipments':
                    for cost_type, value in function_items.items():
                        breakdown[f'{cost_group}|{function}|{cost_type}'] = round(value, 6)
        return breakdown

    def _get_shipment_summary(self):
        output = {}
        # Input
        output.update({'sh_id': self.sh.id})
        output.update(self.sh.input_data.get('lane', {}))
        output.update(self.sh.display)
        # Zone & transit-time
        output.update({'zone': self.zone})
        output.update({'transit_time': self.transit_time})
        # Units input
        output.update(self.sh_units)
        # Units calculated
        # Total shipments if split with shipment_max_size
        total_shipments = self.sh_units_max_size.get('full', {}).get('total_shipments', 0) + self.sh_units_max_size.get('rest', {}).get('total_shipments', 0)
        output.update({'total_shipments': total_shipments})
        # Service
        output.update({'rs_id': self.rs})
        output.update(self.rs.shortcuts.display_on_shipment_summary)
        # output.update({'sheet_name': self.rs.shortcuts.display_on_shipment_summary.get('sheet_name')})
        # Cost total
        output.update({'cost_total': self.cost_total})
        # Cost breakdown
        output.update(self.cost_breakdown)
        return output


def calculate_cost(
        shipments_input,
        ratesheets_input,
        must_match: list[str] | None = None
):
    """
    shipments_input: iterable of shipment objects
    ratesheets_input: iterable of ratesheet objects
    must_match: list of keys to additionally match on;
        any subset of ['src_site','trpmode'], or None for all.
        Note: 'dest_ctry' is ALWAYS applied.
    """
    results = []

    # Determine which fields to enforce:
    # dest_ctry is mandatory; src_site and trpmode are optional via must_match
    optional = {'src_site', 'trpmode'}
    if must_match is None:
        fields = {'dest_ctry'}
    else:
        fields = (set(must_match) & optional) | {'dest_ctry'}

    valid_combinations = []
    shipments_with_ratesheets = 0
    shipments_without_ratesheets = []
    for sh in shipments_input:
        found = False
        for rs in ratesheets_input:
            checks = {
                'src_site': sh.lane.get('src_site') in rs.shortcuts.src_sites,
                'trpmode': sh.meta.get('trpmode') == rs.meta.service.get('trpmode'),
                'dest_ctry': sh.lane.get('dest_ctry') in rs.shortcuts.dest_countries,
            }
            # require every field in `fields`
            if all(checks[f] for f in fields):
                valid_combinations.append((sh, rs))
                found = True
        if not found:
            shipments_without_ratesheets.append(sh)
        else:
            shipments_with_ratesheets += 1

    total = len(shipments_input)
    with_rs = shipments_with_ratesheets
    without_rs = len(shipments_without_ratesheets)
    combos = len(valid_combinations)

    pct_with = (with_rs / total * 100) if total else 0
    pct_without = (without_rs / total * 100) if total else 0

    # neatly align the summary
    labels = [
        "Shipments inserted",
        "Shipments with ratesheets",
        "Shipments without ratesheets",
    ]
    width = max(len(lbl) for lbl in labels)

    print(
        f"{'Shipments inserted':<{width}}: {total}\n"
        f"{'Shipments with ratesheets':<{width}}: "
        f"{with_rs} ({pct_with:.1f}%) => {combos} combinations\n"
        f"{'Shipments without ratesheets':<{width}}: "
        f"{without_rs} ({pct_without:.1f}%)\n"
        f"{'Matching on':<{width}}: {sorted(fields)}"
    )

    for sh, rs in tqdm(
            valid_combinations,
            desc="Calculating shipment-ratesheet costs",
            mininterval=1
    ):
        results.append(Cost(sh, rs))

    return results, shipments_without_ratesheets
