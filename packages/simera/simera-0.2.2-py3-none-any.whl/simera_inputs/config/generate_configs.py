"""
Generate initial inputs to configs. Mostly from Excel files
"""
import numpy as np
import pandas as pd
import yaml

from simera.config import Config

sc = Config()


def country_excel_to_yaml(excel_path, yaml_path):
    """
    Converts an Excel file to a YAML file.
    """
    # Read the Excel file
    df = pd.read_excel(excel_path, dtype=str)  # Keep everything as string for safety
    df['latitude'] = pd.to_numeric(df['latitude'])
    df['longitude'] = pd.to_numeric(df['longitude'])

    # Replace NaN with None
    df = df.replace({np.nan: None})

    # Convert DataFrame into a dictionary with 'ctry' as the key
    data_dict = {row["ctry"]: row.to_dict() for _, row in df.iterrows()}

    # Remove 'ctry' from values since it's already the key
    for key in data_dict:
        data_dict[key].pop("ctry", None)

    # Save as YAML
    with open(yaml_path, "w", encoding="utf-8") as file:
        yaml.dump(data_dict, file, default_flow_style=False, allow_unicode=True)

    print(f"YAML file saved successfully at: {yaml_path}")
    print(f"Remember to copy-paste that to simera/config.country.yaml (!)")


def currency_excel_to_yaml(excel_path, yaml_path):
    """
    Converts an Excel file to a YAML file.
    """
    # Read the Excel file
    df = pd.read_excel(excel_path)

    yaml_dict = {}

    for _, row in df.iterrows():
        base_currency = row['from']
        target_currency = row['currency']
        rate = row['rate']

        if base_currency not in yaml_dict:
            yaml_dict[base_currency] = {}

        yaml_dict[base_currency][target_currency] = rate

    # Save as YAML
    with open(yaml_path, "w", encoding="utf-8") as file:
        yaml.dump(yaml_dict, file, default_flow_style=False, allow_unicode=True)

    print(f"YAML file saved successfully at: {yaml_path}")
    print(f"Remember to copy-paste that to simera/config.country.yaml (!)")


def generate_config_country():
    excel_path = sc.path.base_dir / 'simera_inputs/config/country.xlsx'
    yaml_path = sc.path.base_dir / 'simera_inputs/config/country.yaml'
    country_excel_to_yaml(excel_path, yaml_path)


def generate_config_currency():
    excel_path = sc.path.base_dir / 'simera_inputs/config/currency.xlsx'
    yaml_path = sc.path.base_dir / 'simera_inputs/config/currency.yaml'
    currency_excel_to_yaml(excel_path, yaml_path)


if __name__ == '__main__':
    generate_config_country()
    generate_config_currency()
