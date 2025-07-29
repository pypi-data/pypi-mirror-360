import itertools
from tqdm import tqdm
from pathlib import Path
import pandas as pd
from simera import Ratesheet, Shipment, Cost, Config, ZipcodeManager, calculate_cost, merge_ratesheets

sc = Config()
zm = ZipcodeManager()

# for f in (sc.path.resources / 'ratesheets').glob('*.*'):
#     print(f"Path(sc.path.resources / 'ratesheets/{f.name}'),")

# Get ratesheets
test_files = [
    Path(sc.path.resources / 'ratesheets/DC_FR_LPP.xlsb'),
    Path(sc.path.resources / 'ratesheets/DC_GB_Northampton.xlsb'),
    Path(sc.path.resources / 'ratesheets/DC_GR_Athens.xlsb'),
    Path(sc.path.resources / 'ratesheets/DC_IE_Dublin.xlsb'),
    Path(sc.path.resources / 'ratesheets/DC_NL_Eindhoven_1.xlsb'),
    Path(sc.path.resources / 'ratesheets/DC_NL_Eindhoven_2.xlsb'),
    Path(sc.path.resources / 'ratesheets/DC_PL_Pila_1.xlsb'),
    Path(sc.path.resources / 'ratesheets/DC_PL_Pila_2.xlsb'),
    Path(sc.path.resources / 'ratesheets/FA_BE_Turnhout.xlsb'),
    Path(sc.path.resources / 'ratesheets/FA_DK_Copenhagen.xlsb'),
    Path(sc.path.resources / 'ratesheets/FA_ES_Valladolid.xlsb'),
    Path(sc.path.resources / 'ratesheets/FA_HU_Tamasi.xlsb'),
    Path(sc.path.resources / 'ratesheets/FA_PL_Ketrzyn.xlsb'),
    Path(sc.path.resources / 'ratesheets/FA_PL_Pila_1.xlsb'),
    Path(sc.path.resources / 'ratesheets/FA_PL_Pila_2.xlsb'),
    Path(sc.path.resources / 'ratesheets/PAR_DHL_STD_MULTI_exc_WHS.xlsb'),
    Path(sc.path.resources / 'ratesheets/PAR_DHL_STD_SINGL_exc_WHS.xlsb'),
    Path(sc.path.resources / 'ratesheets/PAR_UPS_EXP_SINGL_exc_WHS.xlsb'),
    Path(sc.path.resources / 'ratesheets/PAR_UPS_STD_MULTI_exc_WHS.xlsb'),
    Path(sc.path.resources / 'ratesheets/PAR_UPS_STD_SINGL_exc_WHS.xlsb'),
]

test_files = [
    Path(sc.path.resources / 'ratesheets/PAR_DHL_STD_MULTI_exc_WHS.xlsb'),
    Path(sc.path.resources / 'ratesheets/PAR_DHL_STD_SINGL_exc_WHS.xlsb'),
    Path(sc.path.resources / 'ratesheets/PAR_UPS_EXP_SINGL_exc_WHS.xlsb'),
    Path(sc.path.resources / 'ratesheets/PAR_UPS_STD_MULTI_exc_WHS.xlsb'),
    Path(sc.path.resources / 'ratesheets/PAR_UPS_STD_SINGL_exc_WHS.xlsb'),
]

sheet_names = {file: pd.ExcelFile(file).sheet_names for file in test_files}
sheet_names_tuple = []
for k, v in sheet_names.items():
    for item in v:
        sheet_names_tuple.append((k, item))
ratesheets = [Ratesheet(file, sheet_name) for file, sheet_name in sheet_names_tuple]
ratesheets = [rs for rs in ratesheets if rs.shortcuts.src_sites[0].startswith('DC_')]

rs = ratesheets[0]
rs_dc = Ratesheet(Path(sc.path.resources /'ratesheets/whs/DC_cost.xlsb'), 'DC_IE_DUBLIN')
rs_with_whs = merge_ratesheets(rs, rs_dc, '2025')

# countries = set()
# for ratesheet in ratesheets:
#     for c in ratesheet.shortcuts.dest_countries:
#         countries.add(c)

countries = ['DE']
# shipments = [Shipment({'lane': {'dest_ctry': ctry, 'dest_zip': zm.zipcode_clean_first[ctry]}, 'unit': {'m3': m3, 'shipment': 1, 'kg': m3 * 150}}) for ctry in countries for m3 in [0.01, 0.1, 1, 10, 20, 45, 50]]
shipments = [Shipment({'display': {'fuck': 123}, 'lane': {'dest_ctry': ctry, 'dest_zip': zm.zipcode_clean_first[ctry]},
                       'unit': {'m3': kg / 150, 'shipment': 1, 'kg': kg, 'putaway': 10, 'orderline': 10}}) for ctry in countries for kg in [0.1, 1, 10, 30, 40, 50]]
# shipments = [Shipment({'lane': {'dest_ctry': ctry, 'dest_zip': f'{zi:0>2}000'}, 'unit': {'m3': m3, 'shipment': 1, 'kg': m3 * 150}}) for ctry in countries for m3 in range(10, 46) for zi in [range(100)]]

shipments_cost, shipments_without_cost = calculate_cost(shipments, ratesheets)
shipments_cost, shipments_without_cost = calculate_cost(shipments, [rs])
shipments_cost, shipments_without_cost = calculate_cost(shipments, [rs_with_whs])
cost = pd.DataFrame([shp.cost_summary for shp in shipments_cost]).sort_values(['sh_id', 'cost_total'], ignore_index=True)
cost_best = cost.sort_values(by=['sh_id', 'cost_total'], ascending=[True, True]).drop_duplicates(subset=['sh_id'], keep='first')


# ratesheets_scope = []
# for ratesheet in ratesheets:
#     if 'DC_PL_PILA' in ratesheet.shortcuts.src_sites and 'DE' in ratesheet.shortcuts.dest_countries:
#         ratesheets_scope.append(ratesheet)

# carriers = set()
# for ratesheet in ratesheets:
#     carriers.add(ratesheet.meta.service.get('carrier'))
#     if (x:=ratesheet.meta.input.get('issues')) is not None:
#         print(ratesheet, x)

# sites = set()
# for ratesheet in ratesheets:
#     sites.add(ratesheet.meta.src.get('site'))
# print(sites)

# countries = set()
# for ratesheet in ratesheets:
#     for c in ratesheet.shortcuts.dest_countries:
#         countries.add(c)


# DHL script
# import re
# import pycountry
#
# data = """Countries & Territories	Zone		Countries & Territories	Zone		Countries & Territories	Zone		Countries & Territories	Zone
# Austria (AT)	3		Germany (DE)	2		Luxembourg (LU)	1		Slovakia (SK)	5
# Belgium (BE)	1		Greece (GR)	4		Monaco (MC)	2		Slovenia (SI)	5
# Bulgaria (BG)	5		Hungary (HU)	5		Norway (NO)	6		Spain (ES)	3
# Croatia (HR)	5		Ireland, Rep. Of (IE)	4		Poland (PL)	5		Sweden (SE)	4
# Czech Rep., The (CZ)	5		Italy (IT)	3		Portugal (PT)	3		Switzerland (CH)	6
# Denmark (DK)	3		Latvia (LV)	5		Romania (RO)	5		United Kingdom (GB) *1	3
# Estonia (EE)	5		Liechtenstein (LI)	6		San Marino (SM)	6		United Kingdom (GB) *2	7
# Finland (FI)	4		Lithuania (LT)	5		Serbia, Rep. Of (RS)	6		Vatican City (VA)	3
# France (FR)	2
#
# """
#
# records = []
# # Skip the header line
# for line in data.strip().splitlines()[1:]:
#     # split on tabs and drop any empty strings
#     parts = [p for p in line.split('\t') if p.strip()]
#     # Walk in pairs: country+code, zone
#     for country_part, zone_part in zip(parts[0::2], parts[1::2]):
#         # extract the ISO code inside parentheses
#         m = re.search(r'\(([^)]+)\)', country_part)
#         if m:
#             records.append({
#                 'country': m.group(1),
#                 'zone': int(zone_part)
#             })
#
# dfa = pd.DataFrame(records)
# dfa.insert(1, 'zip', '')
# dfa.to_clipboard(index=False)
#
# data = """
# Countries & Territories	Zone		Countries & Territories	Zone		Countries & Territories	Zone		Countries & Territories	Zone
# Austria	1		Germany	2		Monaco	3		Slovakia	1
# Belgium	3		Greece	4		Netherlands	3		Slovenia	2
# Bulgaria	3		Ireland	3		Norway	6		Spain	4
# Croatia	2		Italy	3		Poland	2		Sweden	4
# Czechia	2		Latvia	4		Portugal	4		Switzerland	6
# Denmark	4		Liechtenstein	6		Romania	2
# Estonia	4		Lithuania	4		San Marino	6		United Kingdom *2	5
# Finland	4		Luxembourg	3		Serbia	6		Vatican 	3
# France	3
# """
# def get_iso2(country_name):
#     # strip any footnotes like " *1"
#     base = re.sub(r'\s*\*.*', '', country_name).strip()
#     try:
#         return pycountry.countries.lookup(base).alpha_2
#     except (LookupError, AttributeError):
#         return None
#
# records = []
# for line in data.strip().splitlines()[1:]:
#     parts = [p for p in line.split('\t') if p.strip()]
#     for country_part, zone_part in zip(parts[0::2], parts[1::2]):
#         code = get_iso2(country_part)
#         if code:
#             records.append({
#                 'country': code,
#                 'zone': int(zone_part)
#             })
#         else:
#             print(f"⚠️ could not find code for “{country_part}”")
#
# dfa = pd.DataFrame(records)
# dfa.insert(1, 'zip', '')
# dfa.to_clipboard(index=False)

