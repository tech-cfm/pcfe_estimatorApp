# Emission factors 2023
from django.contrib.sites import requests
import requests
from dotenv import load_dotenv
import os
import pandas as pd
from django.shortcuts import render

HOME_ENERGY_EMISSIONS_FACTORS = {
    "Electricity": 0.000527,  # 0.000527(original figure) kg CO2e per kWh
    "Main_Gas": 0.184  # kg CO2e per kWh
}

TRANSPORTATION_EMISSIONS_FACTORS = {
    "petrol_car": 2.31,  # kg CO2e per litre
    "diesel_car": 2.68,  # kg CO2e per litre
    "LPG_car": 1.51,  # kg CO2e per litre
    "Bus": 0.12,  # DIESEL, kg CO2e per passenger-km
    "National_rail": 0.03,  # ELECTRIC; kg CO2e per passenger-km
    "domestic_flight": 0.15653,  # kg CO2e per passenger km
}

FOOD_EMISSION_FACTORS = {
    "Beef": 27,  # kg CO2e per kg
    "Lamb": 39,  # kg CO2e per kg
    "Pork": 12,  # kg CO2e per kg
    "Poultry": 6,  # kg CO2e per kg --- (chicken, turkey)
    "Fish ": 5,  # kg CO2e per kg ---(farmed)
    "Eggs": 4,  # kg CO2e per kg
    "Dairy ": 2.5,  # kg CO2e per kg ---(milk, cheese, yoghurt)
    "Vegetables ": 1.5,  # kg CO2e per kg (varies widely) ---and fruits
    "Cereals ": 1,  # kg CO2e per kg ---(wheat, rice, etc.)
}


def calculate_footprint(home_energy, transportation, food):
    footprint = 0

    # Home energy
    footprint += (
            home_energy["electricity_usage"] * HOME_ENERGY_EMISSIONS_FACTORS["Electricity"]
            + home_energy["gas_usage"] * HOME_ENERGY_EMISSIONS_FACTORS["Main_Gas"]
    )

    # Transportation
    footprint += (
            transportation["petrol_car_distance"] * TRANSPORTATION_EMISSIONS_FACTORS["petrol_car"]
            + transportation["diesel_car_distance"] * TRANSPORTATION_EMISSIONS_FACTORS["diesel_car"]
            + transportation["lpg_car_distance"] * TRANSPORTATION_EMISSIONS_FACTORS["LPG_car"]
            + transportation["bus_distance"] * TRANSPORTATION_EMISSIONS_FACTORS["Bus"]
            + transportation["national_rail_distance"] * TRANSPORTATION_EMISSIONS_FACTORS["National_rail"]
            + transportation["domestic_flight_distance"] * TRANSPORTATION_EMISSIONS_FACTORS["domestic_flight"]
    )

    # Food
    footprint += (
            food["beef_consumption"] * FOOD_EMISSION_FACTORS["Beef"]
            + food["lamb_consumption"] * FOOD_EMISSION_FACTORS["Lamb"]
            + food["pork_consumption"] * FOOD_EMISSION_FACTORS["Pork"]
            + food["poultry_consumption"] * FOOD_EMISSION_FACTORS["Poultry"]
            + food["fish_consumption"] * FOOD_EMISSION_FACTORS["Fish "]
            + food["eggs_consumption"] * FOOD_EMISSION_FACTORS["Eggs"]
            + food["dairy_consumption"] * FOOD_EMISSION_FACTORS["Dairy "]
            + food["vegetables_fruits_consumption"] * FOOD_EMISSION_FACTORS["Vegetables "]
            + food["cereals_consumption"] * FOOD_EMISSION_FACTORS["Cereals "]
    )

    return footprint


# Extracting API access credentials
load_dotenv()
url = "https://www.carboninterface.com/api/v1/auth"
user_name = os.getenv("GLOBAL_FOOTPRINT_USERNAME")
api_key = os.getenv("GLOBAL_FOOTPRINT_API_KEY")
headers = {"HTTP_ACCEPT": "application/json"}
#
xlsx_file_path = "NFBA 2023 Public Data Package 1.0.xlsx"


# Load the Excel file into a pandas DataFrame
#def excel_data_view():
  #  response = requests.get(url, auth=(user_name, api_key), headers=headers)

   # print('Status code:', response.status_code)
    # print('JSON', response.json())


#excel_data_view()

# def fetch_ecological_data():
# Get the full path to the Excel file
# file_path = '.data/data/NFBA 2023 Public Data Package 1.0.xlsx'
# xlsx_file_path = "data/NFBA 2023 Public Data Package 1.0.xlsx"
# # Load the Excel file into a pandas DataFrame
# df = pd.read_excel(xlsx_file_path)
# # Load the required sheet by  name
# df_results = pd.read_excel(df, sheet_name='Country Results (2019)')
# if df_results:
#     return df_results
# else:
#     return "No Country Results"
# Make a GET request to the API
# response = requests.get(url, auth=(user_name, api_key), headers=headers)
# # Check if the request was successful
# print('Status code: {}'.format(response.status_code))
# print('JSON', response.json())
# if response.status_code == 200:
#     # Parse the JSON response
#     data = response.json()
#     print(data)
#     return data
# else:
#     return None
