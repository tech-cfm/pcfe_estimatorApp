import os

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
import json
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
import base64
import plotly.graph_objs as go
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.contrib.auth import logout
from .forms import LoginForm
from .forms import SignUpForm
from .models import Profile
from .utils import calculate_footprint, HOME_ENERGY_EMISSIONS_FACTORS, TRANSPORTATION_EMISSIONS_FACTORS, \
    FOOD_EMISSION_FACTORS

# Personal carbon emissions scale
PERSONAL_CARBON_FOOTPRINT_SCALE = {
    'Low': (0, 5),
    'Moderate': (5, 10),
    'High': (10, 15),
    'Very High': (15, float('inf'))
}


def home(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        footprint_history = profile.footprint_history
        if footprint_history:
            latest_footprint = list(footprint_history.values())[-1]
        else:
            latest_footprint = None
        return render(request, 'index.html', {'latest_footprint': latest_footprint})
    else:
        return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def calculate_view(request):
    if request.method == 'POST':
        # Get user input data from the form
        electricity_usage = float(request.POST.get('electricity_usage', 0))
        gas_usage = float(request.POST.get('gas_usage', 0))

        petrol_car_distance = float(request.POST.get('petrol_car_distance', 0))
        diesel_car_distance = float(request.POST.get('diesel_car_distance', 0))
        lpg_car_distance = float(request.POST.get('lpg_car_distance', 0))
        bus_distance = float(request.POST.get('bus_distance', 0))
        national_rail_distance = float(request.POST.get('national_rail_distance', 0))
        domestic_flight_distance = float(request.POST.get('domestic_flight_distance', 0))

        beef_consumption = float(request.POST.get('beef_consumption', 0))
        lamb_consumption = float(request.POST.get('lamb_consumption', 0))
        pork_consumption = float(request.POST.get('pork_consumption', 0))
        poultry_consumption = request.POST.get('poultry_consumption', 0)
        fish_consumption = float(request.POST.get('fish_consumption', 0))
        eggs_consumption = float(request.POST.get('eggs_consumption', 0))
        dairy_consumption = float(request.POST.get('dairy_consumption', 0))
        vegetables_fruits_consumption = float(request.POST.get('vegetables_fruits_consumption', 0))
        cereals_consumption = float(request.POST.get('cereals_consumption', 0))

        # Calculate the carbon footprint
        home_energy = {
            "electricity_usage": float(electricity_usage),
            "gas_usage": float(gas_usage),
        }
        transportation = {
            "petrol_car_distance": float(petrol_car_distance),
            "diesel_car_distance": float(diesel_car_distance),
            "lpg_car_distance": float(lpg_car_distance),
            "bus_distance": float(bus_distance),
            "national_rail_distance": float(national_rail_distance),
            "domestic_flight_distance": float(domestic_flight_distance),
        }
        food = {
            "beef_consumption": float(beef_consumption),
            "lamb_consumption": float(lamb_consumption),
            "pork_consumption": float(pork_consumption),
            "poultry_consumption": float(poultry_consumption),
            "fish_consumption": float(fish_consumption),
            "eggs_consumption": float(eggs_consumption),
            "dairy_consumption": float(dairy_consumption),
            "vegetables_fruits_consumption": float(vegetables_fruits_consumption),
            "cereals_consumption": float(cereals_consumption),
        }
        footprint = calculate_footprint(home_energy, transportation, food)
        # Converting footprint values to tonnes and 2s.f
        # footprint = f'{footprint/1000: .2f}'
        # footprint = str(footprint)

        # Save the footprint to the user's history
        profile = Profile.objects.get(user=request.user)
        footprint_history = profile.footprint_history
        footprint_history = footprint_history
        timestamp = timezone.now().isoformat()
        footprint_history[timestamp] = footprint
        profile.footprint_history = footprint_history
        profile.save()

        # Determine the carbon footprint category
        category = None
        for name, (lower, upper) in PERSONAL_CARBON_FOOTPRINT_SCALE.items():
            if lower <= footprint / 1000 < upper:
                category = name
                break

        # Render the results
        return render(request, 'results.html', {'footprint': f'{footprint/1000: .2f}', 'category': category})
    else:
        return render(request, 'calculate.html', {
            'home_energy_emissions_factors': HOME_ENERGY_EMISSIONS_FACTORS,
            'transportation_emissions_factors': TRANSPORTATION_EMISSIONS_FACTORS,
            'food_emission_factors': FOOD_EMISSION_FACTORS,
        })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def data_visualisation(request):
    """

    :param request:
    :return:
    """
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        footprint_history = profile.footprint_history

        if footprint_history:
            # Prepare data for charts
            timestamps = list(footprint_history.keys())
            footprints = list(footprint_history.values())

            # Home energy data
            home_energy_data = [
                {'label': 'Electricity', 'value': footprints[-1] * HOME_ENERGY_EMISSIONS_FACTORS["Electricity"]},
                {'label': 'Main Gas', 'value': footprints[-1] * HOME_ENERGY_EMISSIONS_FACTORS["Main_Gas"]},
            ]

            # Transportation data
            transportation_data = [
                {'label': 'Petrol Car', 'value': footprints[-1] * TRANSPORTATION_EMISSIONS_FACTORS["petrol_car"]},
                {'label': 'Diesel Car', 'value': footprints[-1] * TRANSPORTATION_EMISSIONS_FACTORS["diesel_car"]},
                {'label': 'LPG Car', 'value': footprints[-1] * TRANSPORTATION_EMISSIONS_FACTORS["LPG_car"]},
                {'label': 'Bus', 'value': footprints[-1] * TRANSPORTATION_EMISSIONS_FACTORS["Bus"]},
                {'label': 'National Rail', 'value': footprints[-1] * TRANSPORTATION_EMISSIONS_FACTORS["National_rail"]},
                {'label': 'Domestic Flight',
                 'value': footprints[-1] * TRANSPORTATION_EMISSIONS_FACTORS["domestic_flight"]},
            ]

            # Food data
            food_data = [
                {'label': 'Beef', 'value': footprints[-1] * FOOD_EMISSION_FACTORS["Beef"]},
                {'label': 'Lamb', 'value': footprints[-1] * FOOD_EMISSION_FACTORS["Lamb"]},
                {'label': 'Pork', 'value': footprints[-1] * FOOD_EMISSION_FACTORS["Pork"]},
                {'label': 'Poultry', 'value': footprints[-1] * FOOD_EMISSION_FACTORS["Poultry"]},
                {'label': 'Fish', 'value': footprints[-1] * FOOD_EMISSION_FACTORS["Fish "]},
                {'label': 'Eggs', 'value': footprints[-1] * FOOD_EMISSION_FACTORS["Eggs"]},
                {'label': 'Dairy', 'value': footprints[-1] * FOOD_EMISSION_FACTORS["Dairy "]},
                {'label': 'Vegetables and Fruits', 'value': footprints[-1] * FOOD_EMISSION_FACTORS["Vegetables "]},
                {'label': 'Cereals', 'value': footprints[-1] * FOOD_EMISSION_FACTORS["Cereals "]},
            ]

            return render(request, 'visualise.html', {
                'timestamps': json.dumps(timestamps),
                'footprints': json.dumps(footprints),
                'home_energy_data': json.dumps(home_energy_data),
                'transportation_data': json.dumps(transportation_data),
                'food_data': json.dumps(food_data),
            })
        else:
            return render(request, 'visualise.html')
    else:
        return redirect('login')


def get_global_footprint_data(request):
    # Get the full path to the Excel file
    xlsx_file_path = 'data/NFBA 2023 Public Data Package 1.1.xlsx'

    # Load the Excel file into a pandas DataFrame
    data = pd.read_excel(xlsx_file_path, sheet_name='Country Results (2019)')
    # data = pd.read_excel(df, sheet_name='Country Results (2019)')

    # Assign column names to the DataFrame
    # data.columns = data.iloc[1]  # Assuming the first row contains column names
    # data = data.iloc[9:]  # Drop the first row (column names)
    # Convert the 'Region' column to a Categorical data type
    data['Region'] = pd.Categorical(data['Region'])

    # Create interactive visualizations
    fig1 = px.scatter(data, x='Total Ecological Footprint (Consumption)', y='Total biocapacity ', color='Region',
                      hover_data=['Country'])
    fig2 = px.bar(data, x='Country', y='Total Ecological Footprint (Consumption)', color='Region')
    fig3 = px.choropleth(data, locations="Country", color="Total Ecological Footprint (Consumption)",
                         hover_name="Country", projection="natural earth")

    # Generate static visualization
    plt.figure(figsize=(10, 6))
    plt.scatter(data['Total Ecological Footprint (Consumption)'], data['Total biocapacity '],
                c=data['Region'].cat.codes, cmap='viridis')
    plt.xlabel('Total Ecological Footprint (Consumption)')
    plt.ylabel('Total Biocapacity')
    plt.colorbar(label='Region')
    plt.tight_layout()

    # Save the static plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    # Base64 encode the static plot
    static_plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Create an interactive table
    table = go.Figure(data=[go.Table(
        header=dict(values=list(data.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[data[col] for col in data.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    # Pass the visualizations to the template for rendering
    context = {
        'data_table': table.to_html(full_html=False, include_plotlyjs='cdn'),
        'scatter_plot': fig1.to_html(),
        'bar_plot': fig2.to_html(),
        'map_plot': fig3.to_html(),
        'static_plot': static_plot_base64
    }

    return render(request, 'global_footprint.html', context)

    # Base64 encode the static plot
# static_plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

# Process the data as needed
# # Extract the total Ecological Footprint and Biocapacity values
# total_ecological_footprint = ecological_data['totalData']['ecological_footprint']
# total_biocapacity = ecological_data['totalData']['biocapacity']
#
# # Extract the Ecological Footprint and Biocapacity values for each component
# components = ecological_data['componentData']
# component_data = []
# for component in components:
#     component_data.append({
#         'name': component['name'],
#         'ecological_footprint': component['ecologicalFootprint'],
#         'biocapacity': component['biocapacity']
#     })
#
#     # Calculate the total Ecological Deficit or Biocapacity Reserve
#     ecological_deficit_reserve = total_biocapacity - total_ecological_footprint
#
#     # Prepare the data for rendering
#     context = {
#         'total_ecological_footprint': total_ecological_footprint,
#         'total_biocapacity': total_biocapacity,
#         'ecological_deficit_reserve': ecological_deficit_reserve,
#         'component_data': component_data
#     }
#
#     return render(request, 'global_footprint.html', context)
# else:
#     error = 'Failed to fetch data from the API'

# if ecological_data:

# Render a template with the data
#   return render(request, 'global_footprint.html', {'ecological_data': ecological_data})
# else:
# Handle the error case
#   return render(request, 'error.html', {'error': 'Failed to fetch data from the API'})
