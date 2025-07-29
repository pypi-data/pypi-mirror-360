"""
Science Facts Module
Comprehensive scientific facts and calculations
"""
from typing import Dict, List, Optional, Any
import math

class ScienceFacts:
    """
    Scientific facts, formulas, and calculations across multiple disciplines
    """
    
    def __init__(self):
        """Initialize science facts database"""
        self.constants = self._load_constants()
        self.formulas = self._load_formulas()
        self.facts = self._load_facts()
    
    def _load_constants(self) -> Dict[str, Dict[str, Any]]:
        """Load scientific constants"""
        return {
            'physics': {
                'c': {'value': 299792458, 'unit': 'm/s', 'name': 'Speed of light'},
                'h': {'value': 6.62607015e-34, 'unit': 'J⋅s', 'name': 'Planck constant'},
                'G': {'value': 6.67430e-11, 'unit': 'm³/kg⋅s²', 'name': 'Gravitational constant'},
                'k_B': {'value': 1.380649e-23, 'unit': 'J/K', 'name': 'Boltzmann constant'},
                'e': {'value': 1.602176634e-19, 'unit': 'C', 'name': 'Elementary charge'},
                'mu_0': {'value': 4*math.pi*1e-7, 'unit': 'H/m', 'name': 'Permeability of free space'},
                'epsilon_0': {'value': 8.8541878128e-12, 'unit': 'F/m', 'name': 'Permittivity of free space'}
            },
            'chemistry': {
                'N_A': {'value': 6.02214076e23, 'unit': 'mol⁻¹', 'name': 'Avogadro constant'},
                'R': {'value': 8.314462618, 'unit': 'J/(mol⋅K)', 'name': 'Gas constant'},
                'F': {'value': 96485.33212, 'unit': 'C/mol', 'name': 'Faraday constant'},
                'atm': {'value': 101325, 'unit': 'Pa', 'name': 'Standard atmosphere'}
            },
            'astronomy': {
                'AU': {'value': 1.495978707e11, 'unit': 'm', 'name': 'Astronomical unit'},
                'ly': {'value': 9.4607304725808e15, 'unit': 'm', 'name': 'Light year'},
                'pc': {'value': 3.0857e16, 'unit': 'm', 'name': 'Parsec'},
                'solar_mass': {'value': 1.98847e30, 'unit': 'kg', 'name': 'Solar mass'}
            }
        }
    
    def _load_formulas(self) -> Dict[str, Dict[str, str]]:
        """Load scientific formulas"""
        return {
            'physics_mechanics': {
                'newton_second_law': 'F = ma',
                'kinetic_energy': 'KE = (1/2)mv²',
                'potential_energy': 'PE = mgh',
                'momentum': 'p = mv',
                'work': 'W = Fd',
                'power': 'P = W/t',
                'centripetal_force': 'F = mv²/r'
            },
            'physics_waves': {
                'wave_speed': 'v = fλ',
                'wave_energy': 'E = hf',
                'snells_law': 'n₁sin(θ₁) = n₂sin(θ₂)',
                'doppler_effect': "f' = f(v ± v₀)/(v ± vₛ)"
            },
            'physics_electricity': {
                'ohms_law': 'V = IR',
                'power_electrical': 'P = VI = I²R = V²/R',
                'coulombs_law': 'F = kq₁q₂/r²',
                'electric_field': 'E = F/q = kQ/r²',
                'capacitance': 'C = Q/V'
            },
            'chemistry_gas_laws': {
                'ideal_gas_law': 'PV = nRT',
                'boyles_law': 'P₁V₁ = P₂V₂',
                'charles_law': 'V₁/T₁ = V₂/T₂',
                'gay_lussacs_law': 'P₁/T₁ = P₂/T₂',
                'combined_gas_law': 'P₁V₁/T₁ = P₂V₂/T₂'
            },
            'chemistry_solutions': {
                'molarity': 'M = n/V',
                'ph': 'pH = -log[H⁺]',
                'henderson_hasselbalch': 'pH = pKa + log([A⁻]/[HA])',
                'beer_lambert_law': 'A = εbc'
            },
            'biology_genetics': {
                'hardy_weinberg': 'p² + 2pq + q² = 1',
                'population_growth': 'dN/dt = rN',
                'logistic_growth': 'dN/dt = rN(1 - N/K)'
            }
        }
    
    def _load_facts(self) -> Dict[str, List[str]]:
        """Load scientific facts"""
        return {
            'physics': [
                "Newton's laws describe the relationship between forces and motion",
                "Energy cannot be created or destroyed, only transformed",
                "The speed of light in vacuum is constant for all observers",
                "Entropy of an isolated system always increases",
                "Electric charge is conserved in all interactions"
            ],
            'chemistry': [
                "Atoms are the basic building blocks of matter",
                "Chemical reactions involve rearrangement of atoms",
                "pH scale ranges from 0 to 14, with 7 being neutral",
                "Catalysts speed up reactions without being consumed",
                "Gases behave ideally at high temperature and low pressure"
            ],
            'biology': [
                "DNA carries genetic information in all living organisms",
                "Cell theory states all life is composed of cells",
                "Evolution occurs through natural selection",
                "Photosynthesis converts sunlight into chemical energy",
                "Homeostasis maintains stable internal conditions"
            ],
            'earth_science': [
                "Plate tectonics explains continental drift and earthquakes",
                "Rock cycle describes transformation between rock types",
                "Water cycle drives weather and climate patterns",
                "Greenhouse gases trap heat in the atmosphere",
                "Solar system formed from a collapsing gas and dust cloud"
            ]
        }
    
    def get_constant(self, name: str, field: str = None) -> Optional[Dict[str, Any]]:
        """Get a scientific constant by name"""
        for field_name, constants in self.constants.items():
            if field and field.lower() != field_name.lower():
                continue
            if name.lower() in [k.lower() for k in constants.keys()]:
                for const_name, const_data in constants.items():
                    if const_name.lower() == name.lower():
                        return {
                            'name': const_name,
                            'field': field_name,
                            **const_data
                        }
        return None
    
    def get_formula(self, name: str, category: str = None) -> Optional[Dict[str, str]]:
        """Get a scientific formula by name"""
        for cat_name, formulas in self.formulas.items():
            if category and category.lower() not in cat_name.lower():
                continue
            for formula_name, formula in formulas.items():
                if name.lower() in formula_name.lower():
                    return {
                        'name': formula_name,
                        'formula': formula,
                        'category': cat_name
                    }
        return None
    
    def calculate_physics(self, formula_type: str, **kwargs) -> Dict[str, Any]:
        """Calculate physics problems"""
        if formula_type.lower() == 'kinetic_energy':
            mass = kwargs.get('mass', kwargs.get('m'))
            velocity = kwargs.get('velocity', kwargs.get('v'))
            if mass and velocity:
                ke = 0.5 * mass * velocity**2
                return {
                    'formula': 'KE = (1/2)mv²',
                    'kinetic_energy': ke,
                    'mass': mass,
                    'velocity': velocity,
                    'unit': 'J'
                }
        
        elif formula_type.lower() == 'potential_energy':
            mass = kwargs.get('mass', kwargs.get('m'))
            gravity = kwargs.get('gravity', kwargs.get('g', 9.81))
            height = kwargs.get('height', kwargs.get('h'))
            if mass and height:
                pe = mass * gravity * height
                return {
                    'formula': 'PE = mgh',
                    'potential_energy': pe,
                    'mass': mass,
                    'gravity': gravity,
                    'height': height,
                    'unit': 'J'
                }
        
        elif formula_type.lower() == 'force':
            mass = kwargs.get('mass', kwargs.get('m'))
            acceleration = kwargs.get('acceleration', kwargs.get('a'))
            if mass and acceleration:
                force = mass * acceleration
                return {
                    'formula': 'F = ma',
                    'force': force,
                    'mass': mass,
                    'acceleration': acceleration,
                    'unit': 'N'
                }
        
        elif formula_type.lower() == 'wave_speed':
            frequency = kwargs.get('frequency', kwargs.get('f'))
            wavelength = kwargs.get('wavelength', kwargs.get('lambda', kwargs.get('λ')))
            if frequency and wavelength:
                speed = frequency * wavelength
                return {
                    'formula': 'v = fλ',
                    'wave_speed': speed,
                    'frequency': frequency,
                    'wavelength': wavelength,
                    'unit': 'm/s'
                }
        
        return {'error': f"Unknown formula type '{formula_type}' or missing parameters"}
    
    def calculate_chemistry(self, calculation_type: str, **kwargs) -> Dict[str, Any]:
        """Calculate chemistry problems"""
        if calculation_type.lower() == 'molarity':
            moles = kwargs.get('moles', kwargs.get('n'))
            volume = kwargs.get('volume', kwargs.get('v'))
            if moles and volume:
                molarity = moles / volume
                return {
                    'formula': 'M = n/V',
                    'molarity': molarity,
                    'moles': moles,
                    'volume': volume,
                    'unit': 'M'
                }
        
        elif calculation_type.lower() == 'ideal_gas':
            # PV = nRT
            pressure = kwargs.get('pressure', kwargs.get('p'))
            volume = kwargs.get('volume', kwargs.get('v'))
            moles = kwargs.get('moles', kwargs.get('n'))
            temperature = kwargs.get('temperature', kwargs.get('t'))
            R = 8.314  # J/(mol·K)
            
            # Calculate missing variable
            if pressure and volume and moles and not temperature:
                temp = (pressure * volume) / (moles * R)
                return {
                    'formula': 'PV = nRT',
                    'temperature': temp,
                    'pressure': pressure,
                    'volume': volume,
                    'moles': moles,
                    'unit': 'K'
                }
            elif pressure and volume and temperature and not moles:
                n = (pressure * volume) / (R * temperature)
                return {
                    'formula': 'PV = nRT',
                    'moles': n,
                    'pressure': pressure,
                    'volume': volume,
                    'temperature': temperature,
                    'unit': 'mol'
                }
        
        elif calculation_type.lower() == 'ph':
            h_concentration = kwargs.get('h_concentration', kwargs.get('h+'))
            oh_concentration = kwargs.get('oh_concentration', kwargs.get('oh-'))
            
            if h_concentration:
                ph = -math.log10(h_concentration)
                poh = 14 - ph
                return {
                    'formula': 'pH = -log[H⁺]',
                    'ph': ph,
                    'poh': poh,
                    'h_concentration': h_concentration,
                    'oh_concentration': 10**(-poh)
                }
            elif oh_concentration:
                poh = -math.log10(oh_concentration)
                ph = 14 - poh
                return {
                    'formula': 'pOH = -log[OH⁻], pH + pOH = 14',
                    'ph': ph,
                    'poh': poh,
                    'oh_concentration': oh_concentration,
                    'h_concentration': 10**(-ph)
                }
        
        return {'error': f"Unknown calculation type '{calculation_type}' or missing parameters"}
    
    def get_periodic_element(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get periodic table element information"""
        elements = {
            'H': {'name': 'Hydrogen', 'atomic_number': 1, 'atomic_mass': 1.008, 'group': 1, 'period': 1},
            'He': {'name': 'Helium', 'atomic_number': 2, 'atomic_mass': 4.003, 'group': 18, 'period': 1},
            'Li': {'name': 'Lithium', 'atomic_number': 3, 'atomic_mass': 6.94, 'group': 1, 'period': 2},
            'Be': {'name': 'Beryllium', 'atomic_number': 4, 'atomic_mass': 9.012, 'group': 2, 'period': 2},
            'B': {'name': 'Boron', 'atomic_number': 5, 'atomic_mass': 10.81, 'group': 13, 'period': 2},
            'C': {'name': 'Carbon', 'atomic_number': 6, 'atomic_mass': 12.01, 'group': 14, 'period': 2},
            'N': {'name': 'Nitrogen', 'atomic_number': 7, 'atomic_mass': 14.01, 'group': 15, 'period': 2},
            'O': {'name': 'Oxygen', 'atomic_number': 8, 'atomic_mass': 16.00, 'group': 16, 'period': 2},
            'F': {'name': 'Fluorine', 'atomic_number': 9, 'atomic_mass': 19.00, 'group': 17, 'period': 2},
            'Ne': {'name': 'Neon', 'atomic_number': 10, 'atomic_mass': 20.18, 'group': 18, 'period': 2},
            # Add more elements as needed
        }
        
        # Search by symbol, name, or atomic number
        identifier = str(identifier).strip()
        
        # Try by symbol
        if identifier in elements:
            return elements[identifier]
        
        # Try by name (case insensitive)
        for symbol, data in elements.items():
            if data['name'].lower() == identifier.lower():
                return {**data, 'symbol': symbol}
        
        # Try by atomic number
        try:
            atomic_num = int(identifier)
            for symbol, data in elements.items():
                if data['atomic_number'] == atomic_num:
                    return {**data, 'symbol': symbol}
        except ValueError:
            pass
        
        return None
    
    def get_facts_by_subject(self, subject: str) -> List[str]:
        """Get scientific facts by subject"""
        subject = subject.lower()
        for key, facts in self.facts.items():
            if subject in key.lower():
                return facts
        return []
    
    def search_formulas(self, query: str) -> List[Dict[str, str]]:
        """Search for formulas containing the query"""
        results = []
        query = query.lower()
        
        for category, formulas in self.formulas.items():
            for name, formula in formulas.items():
                if query in name.lower() or query in formula.lower():
                    results.append({
                        'name': name,
                        'formula': formula,
                        'category': category
                    })
        
        return results
    
    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between temperature scales"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # Convert to Celsius first
        if from_unit == 'fahrenheit' or from_unit == 'f':
            celsius = (value - 32) * 5/9
        elif from_unit == 'kelvin' or from_unit == 'k':
            celsius = value - 273.15
        elif from_unit == 'celsius' or from_unit == 'c':
            celsius = value
        else:
            raise ValueError(f"Unknown temperature unit: {from_unit}")
        
        # Convert from Celsius to target
        if to_unit == 'fahrenheit' or to_unit == 'f':
            return celsius * 9/5 + 32
        elif to_unit == 'kelvin' or to_unit == 'k':
            return celsius + 273.15
        elif to_unit == 'celsius' or to_unit == 'c':
            return celsius
        else:
            raise ValueError(f"Unknown temperature unit: {to_unit}")
    
    def astronomical_distances(self, distance: float, from_unit: str, to_unit: str) -> float:
        """Convert astronomical distances"""
        # Convert to meters first
        to_meters = {
            'au': 1.495978707e11,
            'ly': 9.4607304725808e15,
            'pc': 3.0857e16,
            'm': 1,
            'km': 1000
        }
        
        from_meters = {unit: 1/factor for unit, factor in to_meters.items()}
        
        if from_unit.lower() not in to_meters:
            raise ValueError(f"Unknown unit: {from_unit}")
        if to_unit.lower() not in to_meters:
            raise ValueError(f"Unknown unit: {to_unit}")
        
        meters = distance * to_meters[from_unit.lower()]
        return meters * from_meters[to_unit.lower()]