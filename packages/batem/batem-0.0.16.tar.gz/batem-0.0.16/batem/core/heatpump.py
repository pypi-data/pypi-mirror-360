import CoolProp.CoolProp as CP
from CoolProp.CoolProp import PropsSI


class Fluid:
    
    known_fluids: list[str] = CP.get_global_param_string("FluidsList").split(",")
    # property_names: list[str] = CP.get_global_param_string("output_keys").split(',')
    
    def __init__(self, name, default_temperature_celsius: float = 20, default_bar: float = 101325, default_quality: float = 0):
        self.default_temperature_celsius = default_temperature_celsius
        self.default_pressure_bar = default_bar
        self.default_quality = default_quality
        if name not in self.known_fluids:
            raise ValueError(f"Fluid {name} is not known. Known fluids are: {self.known_fluids}")
        self.fluid_name = name
        
    def property(self, property_name: str = None, temperature_celsius: float = None, pressure_bar: float = None, quality: float = None):
        if temperature_celsius is None:
            temperature_celsius = self.default_temperature_celsius
        if pressure_bar is None:
            pressure_bar = self.default_pressure_bar
        if quality is None:
            quality = self.default_quality
        temperature_K = temperature_celsius + 273.15
        pressure_Pa = pressure_bar * 1e5
        H = PropsSI('H', 'T', temperature_K, 'P', pressure_Pa, self.fluid_name) / 1000  # kJ/kg
        U = PropsSI('U', 'T', temperature_K, 'P', pressure_Pa, self.fluid_name) / 1000  # kJ/kg
        S = PropsSI('S', 'T', temperature_K, 'P', pressure_Pa, self.fluid_name) / 1000  # kJ/kg.K
        v = 1 / PropsSI('D', 'T', temperature_K, 'P', pressure_Pa, self.fluid_name)     # m³/kg
        h0 = PropsSI('H', 'P', pressure_Pa, 'Q', 0, self.fluid_name) / 1000  # kJ/kg
        h1 = PropsSI('H', 'P', pressure_Pa, 'Q', 1, self.fluid_name) / 1000  # kJ/kg
        t3 = PropsSI('T', 'P', pressure_Pa, 'Q', 0, self.fluid_name) - 273.15  # kJ/kg
        
        return {
            'FLUID': self.fluid_name,
            'Specified temperature [°C]': temperature_celsius,
            'Specified pressure [bar]': pressure_bar,
            'Specific enthalpy (H) [kJ/kg]': H,
            'Specific Internal Energy (U) [kJ/kg]': U,
            'Specific Entropy (S) [kJ/kg.K]': S,
            'Specific Density (rho) [m³/kg]': v,
            'Latent energy [kJ/kg]': h1-h0,
            'Temperature at specified pressure (T) [°C]': t3,
        }


if __name__ == "__main__":
    fluid = Fluid("R134a")
