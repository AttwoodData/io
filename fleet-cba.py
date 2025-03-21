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

class Vehicle:
    """Base class for all vehicles in the analysis"""
    def __init__(self, vehicle_data):
        self.data = vehicle_data
        self.vin = vehicle_data.VIN
        self.replacement_score = vehicle_data.Score_25
        self.miles_driven = vehicle_data.Miles_Driven_24_25
        self.price = vehicle_data.price
        self.co2_per_mile = vehicle_data.CO2_Mile
        self.energy_cost_per_mile = vehicle_data.Energy_Cost_Mile
        self.maintenance_annual = vehicle_data["5yr_Maintenance_Costs"]/5
        self.score_delta = vehicle_data.Score_Delta
        
    def annual_carbon_impact(self):
        """Calculate annual carbon impact"""
        return self.miles_driven * self.co2_per_mile
    
    def annual_energy_cost(self):
        """Calculate annual energy cost"""
        return self.miles_driven * self.energy_cost_per_mile
    
    def depreciate(self):
        """Calculate annual depreciation"""
        return 0.06 * self.price

class ICEVehicle(Vehicle):
    """Internal Combustion Engine vehicle"""
    def __init__(self, vehicle_data):
        super().__init__(vehicle_data)
        self.type = "ICE"
        
    def residual_value_factor(self):
        """Return residual value factor for ICE vehicles"""
        return 0.5

class EVVehicle(Vehicle):
    """Electric vehicle"""
    def __init__(self, vehicle_data, charger_type="Level 2", carbon_factor=1.0):
        super().__init__(vehicle_data)
        self.type = "EV"
        self.charger_type = charger_type
        self.carbon_factor = carbon_factor
        
    def annual_carbon_impact(self):
        """Calculate annual carbon impact with potential carbon reduction factor"""
        return super().annual_carbon_impact() * self.carbon_factor
    
    def residual_value_factor(self):
        """Return residual value factor for EV vehicles"""
        return 0.4
    
    def charger_cost(self, l1_cost, l2_cost):
        """Return the charger cost based on charger type"""
        if self.charger_type == "Level 1":
            return l1_cost
        else:
            return l2_cost

class FleetAnalysis:
    def __init__(self):
        # Baseline parameters
        self.discount_rate = 0.02  # 2% discount rate per OMB Circular A-94
        self.l1_cost = 1185        # Level 1 charger cost
        self.l2_cost = 2780        # Level 2 charger cost
        
        # Load and prepare data
        self.load_data()
        
    def load_data(self):
        """Load and prepare vehicle data"""
        # Import vehicle dataset
        self.vehicles = pd.read_csv("vehicles.csv", index_col=False)
        
        # Import ICE vehicle reference data
        self.ICE = pd.read_csv("ICE_table.csv", index_col=False)
        
        # Import EV vehicle reference data
        self.EV = pd.read_csv("EV_table.csv", index_col=False)
        
        # Clean column names in EV dataframe
        rename_cols = {' Energy_ Cost_Mile ': 'Energy_Cost_Mile', ' Edmunds_MSRP ': 'price'}
        self.EV.rename(columns=rename_cols, inplace=True)
        
        # Join vehicle data with EV and ICE reference data
        self.prepare_dataframes()
    
    def prepare_dataframes(self):
        """Create joined dataframes for analysis"""
        # Join vehicle data with EV reference data
        query = """
        SELECT *
        FROM vehicles
        JOIN EV
        ON vehicles.Class = EV.Class
        ;
        """
        self.df_EV = sqldf.run(query)
        
        # Join vehicle data with ICE reference data
        query = """
        SELECT *
        FROM vehicles
        JOIN ICE
        ON vehicles.Class = ICE.Class
        ;
        """
        self.df_ICE = sqldf.run(query)
        
        # Clean up the joined dataframes by removing duplicate columns
        drop_cols = ['index', 'Class'] 
        self.df_EV.drop(labels=drop_cols, axis=1, inplace=True)
        self.df_ICE.drop(labels=drop_cols, axis=1, inplace=True)
    
    def discount_func(self, time, rate): 
        """Apply discount rate to future values"""
        return (1/(1+rate))**time
    
    def simulate_scenario(self, scenario_type, params=None):
        """Generic simulation function supporting different scenarios
        
        Parameters:
        - scenario_type: "ICE_only", "EV_transition", "ICE_favorable", or "EV_favorable"
        - params: Optional dictionary of parameters to override defaults
        """
        # Set default parameters
        default_params = {
            'discount_rate': self.discount_rate,
            'l1_cost': self.l1_cost,
            'l2_cost': self.l2_cost,
            'carbon_factor': 1.0,  # Carbon reduction factor (for EV favorable)
            'ev_residual': 0.4,    # Default EV residual value
            'ice_residual': 0.5    # Default ICE residual value
        }
        
        # Update with provided parameters
        sim_params = default_params.copy()
        if params:
            sim_params.update(params)
        
        # Initialize result collectors
        results = {
            'VIN': [],
            'used_car_sales': [],
            'carbon_impacts': [],
            'maintenance_costs': [],
            'fuel_costs': [],
            'car_purchase_costs': []
        }
        
        # Add charger costs for EV scenarios
        if scenario_type != "ICE_only":
            results['charger_costs'] = []
        
        # Run appropriate simulation
        if scenario_type == "ICE_only":
            self._simulate_ice_only(results, sim_params)
        else:
            self._simulate_ev_transition(results, sim_params, scenario_type)
        
        # Create DataFrame with results
        return pd.DataFrame(results)
    
    def _simulate_ice_only(self, results, params):
        """Simulate ICE-only fleet"""
        for i in range(self.df_ICE.shape[0]):
            car_data = self.df_ICE.iloc[i, :]
            car = ICEVehicle(car_data)
            
            self._simulate_vehicle_lifecycle(car, results, params, replace_with_ev=False)
    
    def _simulate_ev_transition(self, results, params, scenario_type):
        """Simulate fleet with EV transition"""
        # Adjust parameters based on scenario
        if scenario_type == "ICE_favorable":
            params['discount_rate'] = 0.05  # Higher discount rate
            params['l1_cost'] = 10000       # Higher charger cost
            params['l2_cost'] = 10000       # Higher charger cost
        elif scenario_type == "EV_favorable":
            params['carbon_factor'] = 0.5   # 50% reduction due to cleaner grid
            params['ev_residual'] = 0.5     # Better residual value
        
        for i in range(self.df_ICE.shape[0]):
            ice_car_data = self.df_ICE.iloc[i, :]
            car = ICEVehicle(ice_car_data)
            ev_car_data = self.df_EV.iloc[i, :]
            
            # Pass the data for the EV replacement
            ev_replacement = EVVehicle(ev_car_data, 
                                      charger_type=ev_car_data.Charger,
                                      carbon_factor=params['carbon_factor'])
            
            self._simulate_vehicle_lifecycle(car, results, params, 
                                           replace_with_ev=True, 
                                           ev_replacement=ev_replacement)
    
    def _simulate_vehicle_lifecycle(self, car, results, params, replace_with_ev=False, ev_replacement=None):
        """Simulate a single vehicle lifecycle"""
        VIN = car.vin
        replacement_score = car.replacement_score
        
        # Initialize accumulators
        t = 0
        energy_costs = 0
        purchase_costs = 0
        maintenance = 0
        recovery = 0
        depreciate = 0
        carbon = 0
        charger_cost = 0
        
        # Track if car is still ICE
        is_ice = True
        
        while t < 11:
            # Beginning of year cost
            discount = self.discount_func(t, params['discount_rate'])
            
            if replacement_score > 15:
                if replace_with_ev and is_ice:
                    # Replace ICE with EV
                    recovery += car.residual_value_factor() * car.price * discount
                    
                    # Switch to EV
                    car = ev_replacement
                    is_ice = False
                    
                    # Add charger cost
                    charger_cost = car.charger_cost(params['l1_cost'], params['l2_cost']) * discount
                else:
                    # Replace with the same type
                    recovery += car.residual_value_factor() * car.price * discount
                
                # Add the new vehicle cost
                purchase_costs += car.price * discount
                replacement_score = 0
            
            # Costs incurred over the course of the year
            discount = self.discount_func(t+0.5, params['discount_rate'])
            
            # Drive the car for a year
            carbon += car.annual_carbon_impact()
            energy_costs += car.annual_energy_cost() * discount
            depreciate += car.depreciate()
            maintenance += car.maintenance_annual * discount
            replacement_score += car.score_delta
            
            # Move on to the next year
            t += 1
            
            # If moving on to year 11, we've finished the study period
            if t == 11:
                # Calculate end-of-life value
                end_discount = self.discount_func(10, params['discount_rate'])
                recovery += (car.price - depreciate) * end_discount
                
                # Record results
                results['VIN'].append(VIN)
                results['used_car_sales'].append(round(recovery, 0).astype(int))
                results['carbon_impacts'].append(round(carbon, 0).astype(int))
                results['maintenance_costs'].append(round(maintenance, 0).astype(int))
                results['fuel_costs'].append(round(energy_costs, 0).astype(int))
                results['car_purchase_costs'].append(round(purchase_costs, 0).astype(int))
                
                if 'charger_costs' in results:
                    results['charger_costs'].append(int(round(charger_cost, 0)))

    def run_analysis(self):
        """Run the full analysis with all scenarios and return summary results"""
        print("Running fleet electrification analysis...")
        
        # Run base scenario simulations
        df_ICE_out = self.simulate_scenario("ICE_only")
        df_EV_out = self.simulate_scenario("EV_transition")
        
        # Run sensitivity analysis
        df_ICE_ICE_favorable = self.simulate_scenario("ICE_only", {'discount_rate': 0.05})
        df_EV_ICE_favorable = self.simulate_scenario("ICE_favorable")
        df_EV_EV_favorable = self.simulate_scenario("EV_favorable")
        
        # Calculate total costs
        # Base scenario
        ice_base_costs = df_ICE_out.sum().iloc[2:].sum()
        ev_base_costs = df_EV_out.sum().iloc[2:].sum()
        base_savings = ice_base_costs - ev_base_costs
        
        # ICE favorable
        ice_fav_costs = df_ICE_ICE_favorable.sum().iloc[2:].sum()
        ev_ice_fav_costs = df_EV_ICE_favorable.sum().iloc[2:].sum()
        ice_fav_savings = ice_fav_costs - ev_ice_fav_costs
        
        # EV favorable
        ev_fav_costs = df_EV_EV_favorable.sum().iloc[2:].sum()
        ev_fav_savings = ice_base_costs - ev_fav_costs
        
        # Print summary results
        print("\nBase Case Results:")
        print(f"ICE Total Costs: ${ice_base_costs:,.0f}")
        print(f"EV Total Costs: ${ev_base_costs:,.0f}")
        print(f"Net Savings: ${base_savings:,.0f}")
        
        print("\nICE Favorable Scenario:")
        print(f"ICE Total Costs: ${ice_fav_costs:,.0f}")
        print(f"EV Total Costs: ${ev_ice_fav_costs:,.0f}")
        print(f"Net Savings: ${ice_fav_savings:,.0f}")
        
        print("\nEV Favorable Scenario:")
        print(f"ICE Total Costs: ${ice_base_costs:,.0f}")
        print(f"EV Total Costs: ${ev_fav_costs:,.0f}")
        print(f"Net Savings: ${ev_fav_savings:,.0f}")
        
        print("\nConclusion:")
        print(f"From our sensitivity analysis, we conclude that under various conditions we can")
        print(f"expect an increase in net benefits between ${min(ice_fav_savings, base_savings, ev_fav_savings):,.0f} to")
        print(f"${max(ice_fav_savings, base_savings, ev_fav_savings):,.0f} with an 'average' expected increase of ${base_savings:,.0f}.")
        print(f"Also of note is that some benefits accrue regardless of CO2 emission considerations.")
        
        return {
            'ice_base': df_ICE_out,
            'ev_base': df_EV_out,
            'ice_favorable_ice': df_ICE_ICE_favorable,
            'ice_favorable_ev': df_EV_ICE_favorable,
            'ev_favorable': df_EV_EV_favorable,
            'summary': {
                'base_savings': base_savings,
                'ice_favorable_savings': ice_fav_savings,
                'ev_favorable_savings': ev_fav_savings
            }
        }

# Run the analysis
if __name__ == "__main__":
    analyzer = FleetAnalysis()
    results = analyzer.run_analysis()
