# Kirkwood Fleet Electrification: A Benefit-Cost Analysis
# Mark Attwood
# University of Missouri – Saint Louis
# Prepared: 25-April-2024

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setting display options for better notebook readability
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

## Read In and Prepare Data

# Import vehicle dataset
vehicles = pd.read_csv("vehicles.csv", index_col=False)

# Explore the data
vehicles.describe().transpose()

# Check data structure
vehicles.info()

# Check vehicle classes
vehicles.Class.value_counts()

# Import ICE vehicle reference data
ICE = pd.read_csv("ICE_table.csv", index_col=False)
ICE.info()

# Import EV vehicle reference data
EV = pd.read_csv("EV_table.csv", index_col=False)
EV.info()

# Clean column names in EV dataframe
rename_cols = {' Energy_ Cost_Mile ': 'Energy_Cost_Mile', ' Edmunds_MSRP ': 'price'}
EV.rename(columns=rename_cols, inplace=True)

# Join vehicle data with EV reference data
query = """
SELECT *
FROM vehicles
JOIN EV
ON vehicles.Class = EV.Class
;
"""
df_EV = sqldf.run(query)

# Join vehicle data with ICE reference data
query = """
SELECT *
FROM vehicles
JOIN ICE
ON vehicles.Class = ICE.Class
;
"""
df_ICE = sqldf.run(query)

# Clean up the joined dataframes by removing duplicate columns
drop_cols = ['index', 'Class'] 
df_EV.drop(labels=drop_cols, axis=1, inplace=True)
df_ICE.drop(labels=drop_cols, axis=1, inplace=True)

## Create a predictive model for cost-benefit analysis

### Define Functions and Constants

def discount_func(time, rate): 
    """Apply discount rate to future values"""
    return (1/(1+rate))**time

# Set baseline parameters
discount_rate = 0.02  # 2% discount rate per OMB Circular A-94
l1_cost = 1185        # Level 1 charger cost
l2_cost = 2780        # Level 2 charger cost

### Simulation 1: ICE Vehicles Only (Baseline)

# Initialize lists to store results
VIN = []
used_car_sales = []
carbon_impacts = []
maintenance_costs = []
fuel_costs = []
car_purchase_costs = []

# Run simulation for each vehicle
for i in range(df_ICE.shape[0]):
    car = df_ICE.iloc[i, :]
    
    VIN.append(car.VIN)
    replacement_score = car.Score_25

    annual_carbon = car.Miles_Driven_24_25 * car.CO2_Mile
    annual_fuel_cost = car.Miles_Driven_24_25 * car.Energy_Cost_Mile
    annual_maintain_cost = car["5yr_Maintenance_Costs"]/5
    
    t = 0
    energy_costs = 0
    purchase_costs = 0
    maintenance = 0
    recovery = 0
    depreciate = 0
    carbon = 0
    
    while t < 11:
        # Beginning of year cost
        discount = discount_func(t, discount_rate)
        
        if replacement_score > 15:
            purchase_costs += car.price * discount
            recovery += 0.5*car.price * discount
            replacement_score = 0

        # Costs incurred over the course of the year
        discount = discount_func(t+0.5, discount_rate)
        
        # Drive the car for a year
        carbon += annual_carbon
        energy_costs += (annual_fuel_cost * discount)
        depreciate += 0.06*car.price
        maintenance += annual_maintain_cost*discount
        replacement_score += car.Score_Delta

        # Move on to the next year
        t += 1

        # If moving on to year 11, we've finished the study period.
        if t == 11:
            # Append Discounted Used Car Sales list
            recovery += (car.price - depreciate)*(1/(1+discount_rate))**10
            used_car_sales.append(round(recovery,0).astype(int))
            
            # Append Carbon Impacts
            carbon_impacts.append(round(carbon,0).astype(int))
           
            # Append Maintenance costs
            maintenance_costs.append(round(maintenance,0).astype(int))

            # Append Fuel Costs
            fuel_costs.append(round(energy_costs,0).astype(int))

            # Append Car Purchases
            car_purchase_costs.append(round(purchase_costs,0).astype(int))

# Create DataFrame with results
df_ICE_out = pd.DataFrame({
    "VIN": VIN,
    "used_car_sales": used_car_sales,
    "carbon_impacts": carbon_impacts,
    "maintenance_costs": maintenance_costs,
    "fuel_costs": fuel_costs,
    "car_purchase_costs": car_purchase_costs
})

# Display results
df_ICE_out.head(3)

# Calculate total costs (minus used car sales)
ice_total_costs = df_ICE_out.sum().iloc[2:].sum() - df_ICE_out.sum().iloc[1]
print(f"Total ICE costs (excluding used car sales): ${ice_total_costs:,}")

### Simulation 2: EV Transition (Baseline)

# Initialize lists for results
VIN = []
used_car_sales = []
carbon_impacts = []
maintenance_costs = []
fuel_costs = []
car_purchase_costs = []
charger_costs = []

# Run simulation for each vehicle
for i in range(df_ICE.shape[0]):
    car = df_ICE.iloc[i, :]
    ICE_flag = True
    
    VIN.append(car.VIN)
    replacement_score = car.Score_25

    annual_carbon = car.Miles_Driven_24_25 * car.CO2_Mile
    annual_fuel_cost = car.Miles_Driven_24_25 * car.Energy_Cost_Mile
    annual_maintain_cost = car["5yr_Maintenance_Costs"]/5
    
    t = 0
    energy_costs = 0
    purchase_costs = 0
    maintenance = 0
    recovery = 0
    depreciate = 0
    carbon = 0
    charger_cost = 0
    
    while t < 11:
        # Beginning of year cost
        discount = discount_func(t, discount_rate)
        
        if replacement_score > 15:
            # Replace with EV
            car = df_EV.iloc[i, :]
            purchase_costs += car.price * discount
            if ICE_flag:
                # Sell old ICE car
                recovery += 0.5*df_ICE.iloc[i, :].price * discount
                
                # Update its Carbon Impact, fuel cost, and maintenance
                annual_carbon = car.Miles_Driven_24_25 * car.CO2_Mile
                annual_fuel_cost = car.Miles_Driven_24_25 * car.Energy_Cost_Mile
                annual_maintain_cost = car["5yr_Maintenance_Costs"]/5
                
                # Add charger costs for the new EV
                if car.Charger == "Level 1":
                    charger_cost = l1_cost * discount
                else:
                    charger_cost = l2_cost * discount
                ICE_flag = False
            else:
                recovery += 0.4*car.price * discount
            replacement_score = 0
        
        # Costs incurred over the course of the year
        discount = discount_func(t+0.5, discount_rate)
        
        # Drive the car for a year
        carbon += annual_carbon
        energy_costs += (annual_fuel_cost * discount)
        depreciate += 0.06*car.price
        maintenance += annual_maintain_cost*discount
        replacement_score += car.Score_Delta
        
        # Move on to the next year
        t += 1

        # If moving on to year 11, we've finished the study period.
        if t == 11:
            # Append Discounted Used Car Sales list
            recovery += (car.price - depreciate)*(1/(1+discount_rate))**10
            used_car_sales.append(round(recovery,0).astype(int))
            
            # Append Carbon Impacts
            carbon_impacts.append(round(carbon,0).astype(int))
           
            # Append Maintenance costs
            maintenance_costs.append(round(maintenance,0).astype(int))

            # Append Fuel Costs
            fuel_costs.append(round(energy_costs,0).astype(int))

            # Append Car Purchases
            car_purchase_costs.append(round(purchase_costs,0).astype(int))

            # Add on Costs for the Chargers
            charger_costs.append(int(round(charger_cost,0)))

# Create DataFrame with results
df_EV_out = pd.DataFrame({
    "VIN": VIN,
    "used_car_sales": used_car_sales,
    "carbon_impacts": carbon_impacts,
    "maintenance_costs": maintenance_costs,
    "fuel_costs": fuel_costs,
    "car_purchase_costs": car_purchase_costs, 
    "charger_costs": charger_costs
})

# Display results
df_EV_out.info()
df_EV_out.sum()

# Check EV charger distribution
df_EV.Charger.value_counts()

### Simulation 3: ICE Favorable Scenario

l_cost = 10000              # Increased charger cost
discount_rate_hi = 0.05     # Higher discount rate

# Initialize lists for results
VIN = []
used_car_sales = []
carbon_impacts = []
maintenance_costs = []
fuel_costs = []
car_purchase_costs = []
charger_costs = []

# Run simulation with parameters favorable to ICE
for i in range(df_ICE.shape[0]):
    car = df_ICE.iloc[i, :]
    ICE_flag = True
    
    VIN.append(car.VIN)
    replacement_score = car.Score_25

    annual_carbon = car.Miles_Driven_24_25 * car.CO2_Mile
    annual_fuel_cost = car.Miles_Driven_24_25 * car.Energy_Cost_Mile
    annual_maintain_cost = car["5yr_Maintenance_Costs"]/5
    
    t = 0
    energy_costs = 0
    purchase_costs = 0
    maintenance = 0
    recovery = 0
    depreciate = 0
    carbon = 0
    charger_cost = 0
    
    while t < 11:
        # Beginning of year cost
        discount = discount_func(t, discount_rate_hi)
        
        if replacement_score > 15:
            # Replace with EV
            car = df_EV.iloc[i, :]
            purchase_costs += car.price * discount
            if ICE_flag:
                # Sell old ICE car
                recovery += 0.5*df_ICE.iloc[i, :].price * discount
                
                # Update its Carbon Impact, fuel cost, and maintenance
                annual_carbon = car.Miles_Driven_24_25 * car.CO2_Mile
                annual_fuel_cost = car.Miles_Driven_24_25 * car.Energy_Cost_Mile
                annual_maintain_cost = car["5yr_Maintenance_Costs"]/5
                
                # Add charger costs for the new EV
                if car.Charger == "Level 1":
                    charger_cost = l_cost * discount
                else:
                    charger_cost = l_cost * discount
                ICE_flag = False
            else:
                recovery += 0.4*car.price * discount
            replacement_score = 0
        
        # Costs incurred over the course of the year
        discount = discount_func(t+0.5, discount_rate_hi)
        
        # Drive the car for a year
        carbon += annual_carbon
        energy_costs += (annual_fuel_cost * discount)
        depreciate += 0.06*car.price
        maintenance += annual_maintain_cost*discount
        replacement_score += car.Score_Delta
        
        # Move on to the next year
        t += 1

        # If moving on to year 11, we've finished the study period.
        if t == 11:
            # Append Discounted Used Car Sales list
            recovery += (car.price - depreciate)*(1/(1+discount_rate))**10
            used_car_sales.append(round(recovery,0).astype(int))
            
            # Append Carbon Impacts
            carbon_impacts.append(round(carbon,0).astype(int))
           
            # Append Maintenance costs
            maintenance_costs.append(round(maintenance,0).astype(int))

            # Append Fuel Costs
            fuel_costs.append(round(energy_costs,0).astype(int))

            # Append Car Purchases
            car_purchase_costs.append(round(purchase_costs,0).astype(int))

            # Add on Costs for the Chargers
            charger_costs.append(int(round(charger_cost,0)))

# Create DataFrame with ICE favorable results for EVs
df_EV_ICE_favorable = pd.DataFrame({
    "VIN": VIN,
    "used_car_sales": used_car_sales,
    "carbon_impacts": carbon_impacts,
    "maintenance_costs": maintenance_costs,
    "fuel_costs": fuel_costs,
    "car_purchase_costs": car_purchase_costs, 
    "charger_costs": charger_costs
})

# Display results
df_EV_ICE_favorable.sum()

# Now run ICE simulation with the same favorable parameters for comparison
VIN = []
used_car_sales = []
carbon_impacts = []
maintenance_costs = []
fuel_costs = []
car_purchase_costs = []

for i in range(df_ICE.shape[0]):
    car = df_ICE.iloc[i, :]
    
    VIN.append(car.VIN)
    replacement_score = car.Score_25

    annual_carbon = car.Miles_Driven_24_25 * car.CO2_Mile
    annual_fuel_cost = car.Miles_Driven_24_25 * car.Energy_Cost_Mile
    annual_maintain_cost = car["5yr_Maintenance_Costs"]/5
    
    t = 0
    energy_costs = 0
    purchase_costs = 0
    maintenance = 0
    recovery = 0
    depreciate = 0
    carbon = 0
    
    while t < 11:
        # Beginning of year cost
        discount = discount_func(t, discount_rate_hi)
        
        if replacement_score > 15:
            purchase_costs += car.price * discount
            recovery += 0.5*car.price * discount
            replacement_score = 0

        # Costs incurred over the course of the year
        discount = discount_func(t+0.5, discount_rate_hi)
        
        # Drive the car for a year
        carbon += annual_carbon
        energy_costs += (annual_fuel_cost * discount)
        depreciate += 0.06*car.price
        maintenance += annual_maintain_cost*discount
        replacement_score += car.Score_Delta

        # Move on to the next year
        t += 1

        # If moving on to year 11, we've finished the study period.
        if t == 11:
            # Append Discounted Used Car Sales list
            recovery += (car.price - depreciate)*(1/(1+discount_rate_hi))**10
            used_car_sales.append(round(recovery,0).astype(int))
            
            # Append Carbon Impacts
            carbon_impacts.append(round(carbon,0).astype(int))
           
            # Append Maintenance costs
            maintenance_costs.append(round(maintenance,0).astype(int))

            # Append Fuel Costs
            fuel_costs.append(round(energy_costs,0).astype(int))

            # Append Car Purchases
            car_purchase_costs.append(round(purchase_costs,0).astype(int))

# Create DataFrame with ICE favorable results for ICE vehicles
df_ICE_ICE_favorable = pd.DataFrame({
    "VIN": VIN,
    "used_car_sales": used_car_sales,
    "carbon_impacts": carbon_impacts,
    "maintenance_costs": maintenance_costs,
    "fuel_costs": fuel_costs,
    "car_purchase_costs": car_purchase_costs
})

# Display results
df_ICE_ICE_favorable.sum()

### Simulation 4: EV Favorable Scenario

# Initialize lists for results
VIN = []
used_car_sales = []
carbon_impacts = []
maintenance_costs = []
fuel_costs = []
car_purchase_costs = []
charger_costs = []

# Run simulation with parameters favorable to EV
for i in range(df_ICE.shape[0]):
    car = df_ICE.iloc[i, :]
    ICE_flag = True
    
    VIN.append(car.VIN)
    replacement_score = car.Score_25

    annual_carbon = car.Miles_Driven_24_25 * car.CO2_Mile
    annual_fuel_cost = car.Miles_Driven_24_25 * car.Energy_Cost_Mile
    annual_maintain_cost = car["5yr_Maintenance_Costs"]/5
    
    t = 0
    energy_costs = 0
    purchase_costs = 0
    maintenance = 0
    recovery = 0
    depreciate = 0
    carbon = 0
    charger_cost = 0
    
    while t < 11:
        # Beginning of year cost
        discount = discount_func(t, 0.02)
        
        if replacement_score > 15:
            # Replace with EV
            car = df_EV.iloc[i, :]
            purchase_costs += car.price * discount
            if ICE_flag:
                # Sell old ICE car
                recovery += 0.5*df_ICE.iloc[i, :].price * discount
                
                # Update its Carbon Impact, fuel cost, and maintenance
                # Reduced carbon impact due to cleaner grid
                annual_carbon = car.Miles_Driven_24_25 * car.CO2_Mile * 0.5
                annual_fuel_cost = car.Miles_Driven_24_25 * car.Energy_Cost_Mile
                annual_maintain_cost = car["5yr_Maintenance_Costs"]/5
                
                # Add charger costs for the new EV
                if car.Charger == "Level 1":
                    charger_cost = l1_cost * discount
                else:
                    charger_cost = l2_cost * discount
                ICE_flag = False
            else:
                # Better residual value for EV
                recovery += 0.5*car.price * discount
            replacement_score = 0
        
        # Costs incurred over the course of the year
        discount = discount_func(t+0.5, 0.02)
        
        # Drive the car for a year
        carbon += annual_carbon
        energy_costs += (annual_fuel_cost * discount)
        depreciate += 0.06*car.price
        maintenance += annual_maintain_cost*discount
        replacement_score += car.Score_Delta
        
        # Move on to the next year
        t += 1

        # If moving on to year 11, we've finished the study period.
        if t == 11:
            # Append Discounted Used Car Sales list
            recovery += (car.price - depreciate)*(1/(1+discount_rate))**10
            used_car_sales.append(round(recovery,0).astype(int))
            
            # Append Carbon Impacts
            carbon_impacts.append(round(carbon,0).astype(int))
           
            # Append Maintenance costs
            maintenance_costs.append(round(maintenance,0).astype(int))

            # Append Fuel Costs
            fuel_costs.append(round(energy_costs,0).astype(int))

            # Append Car Purchases
            car_purchase_costs.append(round(purchase_costs,0).astype(int))

            # Add on Costs for the Chargers
            charger_costs.append(int(round(charger_cost,0)))

# Create DataFrame with EV favorable results
df_EV_EV_favorable = pd.DataFrame({
    "VIN": VIN,
    "used_car_sales": used_car_sales,
    "carbon_impacts": carbon_impacts,
    "maintenance_costs": maintenance_costs,
    "fuel_costs": fuel_costs,
    "car_purchase_costs": car_purchase_costs, 
    "charger_costs": charger_costs
})

# Display results
df_EV_EV_favorable.sum()

## Results Summary

print("Base Case Results:")
print("ICE Total Costs:", df_ICE_out.sum().iloc[2:].sum())
print("EV Total Costs:", df_EV_out.sum().iloc[2:].sum())
print("Net Savings:", df_ICE_out.sum().iloc[2:].sum() - df_EV_out.sum().iloc[2:].sum())
print("\nICE Favorable Scenario:")
print("ICE Total Costs:", df_ICE_ICE_favorable.sum().iloc[2:].sum())
print("EV Total Costs:", df_EV_ICE_favorable.sum().iloc[2:].sum())
print("Net Savings:", df_ICE_ICE_favorable.sum().iloc[2:].sum() - df_EV_ICE_favorable.sum().iloc[2:].sum())
print("\nEV Favorable Scenario:")
print("ICE Total Costs:", df_ICE_out.sum().iloc[2:].sum())
print("EV Total Costs:", df_EV_EV_favorable.sum().iloc[2:].sum())
print("Net Savings:", df_ICE_out.sum().iloc[2:].sum() - df_EV_EV_favorable.sum().iloc[2:].sum())

## Conclusion
# From our sensitivity analysis, we conclude that under various conditions we can 
# expect an increase in net benefits between $339,000 to $952,000 with an "average" 
# expected increase of $691,000. Also of note is that some benefits accrue regardless 
# of CO2 emission considerations.
#
# As a result, it is recommended that the City of Kirkwood adopt a policy of transitioning 
# its light and medium vehicles to electric versions in pursuit of its underlying goal 
# to mitigate climate change through targeted environmental initiatives.
