import itertools
from simera import Config
from simera.utils import DataInputError

# class OrderToShipment:
#     pass

sc = Config()

class Shipment:
    """
    Consolidate all orderline level data to shipment data
    """
    # future: itertools.count is unique per python process. When moving to multiprocessing for cost,
    #  make sure it's not shipment are created before split.
    _id_counter = itertools.count(1)

    # Class variables - defaults and choices
    # Note: config values are taken from sc.config (not from ratesheet) as ratesheet could have older version
    _config_choices_volume = sc.config.units_of_measure.get('choices').get('volume')
    _config_choices_weight = sc.config.units_of_measure.get('choices').get('weight')
    _config_choices_volume_and_weight = sc.config.units_of_measure.get('choices').get('volume_and_weight')
    _config_units_of_measure_conversions_volume = sc.config.units_of_measure['conversions']['volume']
    _config_units_of_measure_conversions_weight = sc.config.units_of_measure['conversions']['weight']

    def __init__(self, input_data):
        # Process input data into dict with meta, lane and cost keys. Probably will be extended with SubClasses
        self.id = next(Shipment._id_counter)
        self.input_data = input_data
        self.units = self._get_unit_attributes()
        self.lane = self._get_lane_attributes()
        self.meta = self._get_meta_attributes()
        self.display = self._get_display_in_summary()

    def __repr__(self):
        return f"Shipment <{self.lane.get('dest_ctry')}><{self.id}>"

    def _get_lane_attributes(self):
        lane_items_builtin = [
            'src_site', 'src_region', 'src_ctry', 'src_zip', 'src_zone',
            'dest_site', 'dest_region', 'dest_ctry', 'dest_zip', 'dest_zone',
        ]
        lane_items = dict.fromkeys(lane_items_builtin)
        if (lane_input := self.input_data.get('lane')) is not None:
            lane_items.update(lane_input)

        if lane_items.get('dest_ctry') is None and lane_items.get('dest_zone') is None:
            raise DataInputError(f"Shipment data missing (to determine dest_zone): 'lane.dest_ctry'.",
                                 solution="Provide lane.dest_ctry or lane.dest_zone")
        if lane_items.get('dest_zip') is None and lane_items.get('dest_zone') is None:
            raise DataInputError(f"Shipment data missing (to determine dest_zone): 'lane.dest_zip'.",
                                 solution="Provide lane.dest_zip or lane.dest_zone")
        return lane_items

    def _get_unit_attributes(self):
        cost_units_builtin = []
        cost_units = dict.fromkeys(cost_units_builtin)
        # Update units from input_data
        if (cost_input := self.input_data.get('unit')) is not None:
            cost_units.update(cost_input)

        # Convert weight and volume units to 'default_in_calculation' units (m3 and kg). It's for chargeable_ratios
        converted_cost_units = {}
        for cost_unit in cost_units.keys():
            if cost_unit in self._config_choices_volume:
                ratio_to_m3 = self._config_units_of_measure_conversions_volume[cost_unit]['m3']
                converted_cost_units.update({'m3': cost_units[cost_unit] / ratio_to_m3})
                continue
            if cost_unit in self._config_choices_weight:
                ratio_to_kg = self._config_units_of_measure_conversions_weight[cost_unit]['kg']
                converted_cost_units.update({'kg': cost_units[cost_unit] / ratio_to_kg})
        cost_units.update(converted_cost_units)
        return cost_units

    def _get_meta_attributes(self):
        meta_items_builtin = []
        meta_items = dict.fromkeys(meta_items_builtin)
        if (meta_input := self.input_data.get('meta')) is not None:
            meta_items.update(meta_input)
        return meta_items

    def _get_display_in_summary(self):
        items_builtin = []
        items = dict.fromkeys(items_builtin)
        if (display_input := self.input_data.get('display')) is not None:
            items.update(display_input)
        return items

# future: Process of Calculation
#  Class Shipment:
#   Have recipes (class CostUnit) to calculate CostUnits based on input data.
#   CostUnits will be calculated only when requested by Ratesheet
#  Class Cost:
#   Determine what is needed based on Ratesheet
#   Get required cost unit from Shipment or from Ratesheet.meta custom_default/custom_ratios (and/or raise error/warning/log)


if __name__ == '__main__':
    pass
    # from simera import ZipcodeManager
    # zm = ZipcodeManager()
    #
    # def calc_cost(shipments_input, ratesheets_input):
    #     results = []
    #     shipments_ratesheets = itertools.product(shipments_input, ratesheets_input)
    #     # Filter shipments-ratesheets pairs
    #     all_shipments = 0
    #     shipments_with_matched_ratesheets = []
    #     for _sh, _rs in shipments_ratesheets:
    #         if _sh.lane.get('dest_ctry') in _rs.shortcuts.dest_countries:
    #             shipments_with_matched_ratesheets.append((_sh, _rs))
    #         all_shipments += 1
    #     print(f"{len(shipments_with_matched_ratesheets)}/{all_shipments} have at least one ratesheet")
    #     for _sh, _rs in tqdm(shipments_with_matched_ratesheets, desc="Calculating shipment-ratesheet costs", mininterval=1):
    #         results.append(Cost(_sh, _rs))
    #     return results
    #
    # # Get ratesheets
    # test_file = Path(sc.path.resources /'ratesheets/DC_PL_Pila.xlsb')
    # sheet_names = pd.ExcelFile(test_file).sheet_names
    # ratesheets = [Ratesheet(test_file, sheet_name) for sheet_name in sheet_names if not sheet_name.startswith('_')]
    #
    # # get shipments
    # countries = ['DE', 'DK', 'FI', 'NO', 'SE', 'FR', 'BE', 'NL', 'LU', 'AT', 'GB', 'ES', 'IT', 'PT', 'PL', 'LT', 'LV', 'EE', 'CH', 'HR', 'IE', 'BG', 'CZ', 'GR', 'HU', 'RO', 'SI', 'SK']
    # shipments = [Shipment({'lane': {'dest_ctry': ctry, 'dest_zip': zm.zipcode_clean_first[ctry]}, 'unit': {'m3': 0.1, 'shipment': 1}}) for ctry in countries]
    #
    # shipments_cost = calc_cost(shipments, ratesheets)
    # df = pd.DataFrame([shp.cost_summary for shp in shipments_cost])
    # rss = [Ratesheet(Path(r'simera_inputs\transport\Simera Ratesheet Tester.xlsb'), f't{i}') for i in range(1, 4)]

    # Mass testing
    # rs_file = Path(r'simera_inputs\transport\Simera Ratesheet Tester.xlsb')
    # ratesheets = [Ratesheet(rs_file, s) for s in pd.ExcelFile(rs_file).sheet_names]

    # sh_inputs = (
    #     {'lane': {'dest_ctry': 'PL', 'dest_zip': '10000'}, 'unit': {'m3': 1, 'shipment': 1, 'kg': 100, 'pal_ful': 2}},
    #     # {'lane': {'dest_ctry': 'PL', 'dest_zip': '10000'}, 'unit': {'m3': 1, 'shipment': 1, 'kg': 150}},
    #     # {'lane': {'dest_ctry': 'PL', 'dest_zip': '20000'}, 'unit': {'m3': 1.5, 'shipment': 1, 'kg': 240}},
    #     # {'lane': {'dest_ctry': 'SK', 'dest_zip': '30000'}, 'unit': {'m3': 2.1, 'shipment': 1, 'kg': 400}},
    # )
    # shipments = [Shipment(i) for i in sh_inputs]
    # costs = []
    # for sh in shipments:
    #     for rs in ratesheets:
    #         costs.append(Cost(sh, rs))
    # df = pd.DataFrame([cost.shipment_summary for cost in costs])
    
    # todo: Make an interactive demonstration and share with people: shipments to DE zip per many different modes and carriers
    # todo: splitting packages package, large_package (this is name for surcharge: new costGroup trp_sur>large_package 65.7 (per large_package), trp_sur>lps_discount 0.4%
    # todo: make shipment_summary more readable
    # todo: how to apply parcel not allowed
    # todo: translate orders into shipment -> that should be in Shipment itself (Orders to Shipment)
    # todo: cost_type display to get table with shipment_summary
    # todo: add a check that is shipment_size_max or package_size_max is provided and have m3 and/or kg, than shipment also should have them.

    # Testing for speed
    # def calc(shps, rss):
    #     results = []
    #     shpsrss = list(itertools.product(shps, rss))
    #     for shp, rs in tqdm(shpsrss, desc="Calculating shipment-ratesheet costs", mininterval=1):
    #         results.append(Cost(shp, rs))
    #     # for shp in tqdm(shps, desc="Calculating shipment costs", mininterval=10):
    #     #     results.append(Cost(shp, rs))
    #     return results
    #
    # shps = [Shipment({'lane': {'dest_ctry': 'PL', 'dest_zip': f'{i:0>5}'}, 'unit': {'m3': i/1000, 'kg': 100+1*i, 'drop': 0, 'shipment': 1, 'pal_ful': 1, 'box_ful': i}}) for i in range(100000)]
    # rss = [Ratesheet(Path(r'simera_inputs\transport\Simera Ratesheet Tester.xlsb'), f't{i}') for i in range(1, 4)]
    # shp_cost = calc(shps, rss)
    # all_cost_summaries = [shp.cost_summary for shp in shp_cost]
    # df = pd.DataFrame(all_cost_summaries)

    # Super to check computing time per function
    # ------------------------------------------
    # prof = cProfile.Profile()
    # prof.enable()
    # shp_cost = calc(shps, rss)
    # prof.disable()
    # stats = pstats.Stats(prof).sort_stats('tottime')
    # stats.print_stats()

    # rs = Ratesheet(Path(r'simera_inputs\transport\Simera Ratesheet Tester.xlsb'), '3')

    # Optilo
    # df = pd.read_csv(Path(r'simera_inputs\transport\ifc_output_20250610.csv'), sep=';', low_memory=False, header=[1])
    # a = pd.DataFrame(df.isna().all(), columns=['check'])
    # show_columns = a[a.check]
    # df.drop(columns=show_columns.index, inplace=True)
    # df.info(show_counts=True)
    # df.ccw_zaokraglanie.value_counts()
