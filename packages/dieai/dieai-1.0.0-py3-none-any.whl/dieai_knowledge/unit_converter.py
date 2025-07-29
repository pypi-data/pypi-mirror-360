"""
Unit Converter Module
Comprehensive unit conversion for various measurement systems
"""
from typing import Dict, List, Optional, Any

class UnitConverter:
    """
    Universal unit converter for length, mass, volume, energy, and more
    """
    
    def __init__(self):
        """Initialize unit conversion tables"""
        self.conversion_factors = self._load_conversion_factors()
    
    def _load_conversion_factors(self) -> Dict[str, Dict[str, float]]:
        """Load conversion factors for different unit types"""
        return {
            'length': {
                # Base unit: meter
                'm': 1.0,
                'meter': 1.0,
                'meters': 1.0,
                'cm': 0.01,
                'centimeter': 0.01,
                'centimeters': 0.01,
                'mm': 0.001,
                'millimeter': 0.001,
                'millimeters': 0.001,
                'km': 1000.0,
                'kilometer': 1000.0,
                'kilometers': 1000.0,
                'in': 0.0254,
                'inch': 0.0254,
                'inches': 0.0254,
                'ft': 0.3048,
                'foot': 0.3048,
                'feet': 0.3048,
                'yd': 0.9144,
                'yard': 0.9144,
                'yards': 0.9144,
                'mi': 1609.344,
                'mile': 1609.344,
                'miles': 1609.344,
                'nm': 1852.0,  # Nautical mile
                'nautical_mile': 1852.0,
                'ly': 9.4607304725808e15,  # Light year
                'light_year': 9.4607304725808e15,
                'au': 1.495978707e11,  # Astronomical unit
                'astronomical_unit': 1.495978707e11,
            },
            'mass': {
                # Base unit: kilogram
                'kg': 1.0,
                'kilogram': 1.0,
                'kilograms': 1.0,
                'g': 0.001,
                'gram': 0.001,
                'grams': 0.001,
                'mg': 1e-6,
                'milligram': 1e-6,
                'milligrams': 1e-6,
                'lb': 0.453592,
                'pound': 0.453592,
                'pounds': 0.453592,
                'oz': 0.0283495,
                'ounce': 0.0283495,
                'ounces': 0.0283495,
                'ton': 1000.0,
                'metric_ton': 1000.0,
                'st': 6.35029,  # Stone
                'stone': 6.35029,
            },
            'volume': {
                # Base unit: liter
                'l': 1.0,
                'liter': 1.0,
                'liters': 1.0,
                'ml': 0.001,
                'milliliter': 0.001,
                'milliliters': 0.001,
                'cl': 0.01,
                'centiliter': 0.01,
                'centiliters': 0.01,
                'dl': 0.1,
                'deciliter': 0.1,
                'deciliters': 0.1,
                'm3': 1000.0,
                'cubic_meter': 1000.0,
                'cubic_meters': 1000.0,
                'cm3': 0.001,
                'cubic_centimeter': 0.001,
                'cubic_centimeters': 0.001,
                'gal': 3.78541,  # US gallon
                'gallon': 3.78541,
                'gallons': 3.78541,
                'qt': 0.946353,  # US quart
                'quart': 0.946353,
                'quarts': 0.946353,
                'pt': 0.473176,  # US pint
                'pint': 0.473176,
                'pints': 0.473176,
                'cup': 0.236588,
                'cups': 0.236588,
                'fl_oz': 0.0295735,  # US fluid ounce
                'fluid_ounce': 0.0295735,
                'fluid_ounces': 0.0295735,
                'tbsp': 0.0147868,  # Tablespoon
                'tablespoon': 0.0147868,
                'tablespoons': 0.0147868,
                'tsp': 0.00492892,  # Teaspoon
                'teaspoon': 0.00492892,
                'teaspoons': 0.00492892,
            },
            'energy': {
                # Base unit: joule
                'j': 1.0,
                'joule': 1.0,
                'joules': 1.0,
                'kj': 1000.0,
                'kilojoule': 1000.0,
                'kilojoules': 1000.0,
                'cal': 4.184,
                'calorie': 4.184,
                'calories': 4.184,
                'kcal': 4184.0,
                'kilocalorie': 4184.0,
                'kilocalories': 4184.0,
                'btu': 1055.06,  # British thermal unit
                'wh': 3600.0,  # Watt hour
                'watt_hour': 3600.0,
                'kwh': 3.6e6,  # Kilowatt hour
                'kilowatt_hour': 3.6e6,
                'erg': 1e-7,
                'ergs': 1e-7,
                'ft_lb': 1.35582,  # Foot-pound
                'foot_pound': 1.35582,
            },
            'power': {
                # Base unit: watt
                'w': 1.0,
                'watt': 1.0,
                'watts': 1.0,
                'kw': 1000.0,
                'kilowatt': 1000.0,
                'kilowatts': 1000.0,
                'mw': 1e6,
                'megawatt': 1e6,
                'megawatts': 1e6,
                'hp': 745.7,  # Horsepower
                'horsepower': 745.7,
                'ps': 735.5,  # Metric horsepower
                'metric_horsepower': 735.5,
            },
            'pressure': {
                # Base unit: pascal
                'pa': 1.0,
                'pascal': 1.0,
                'pascals': 1.0,
                'kpa': 1000.0,
                'kilopascal': 1000.0,
                'kilopascals': 1000.0,
                'mpa': 1e6,
                'megapascal': 1e6,
                'megapascals': 1e6,
                'bar': 100000.0,
                'bars': 100000.0,
                'atm': 101325.0,
                'atmosphere': 101325.0,
                'atmospheres': 101325.0,
                'psi': 6894.76,  # Pounds per square inch
                'mmhg': 133.322,  # Millimeters of mercury
                'torr': 133.322,
                'torrs': 133.322,
            },
            'temperature': {
                # Special case - handled separately due to offset conversions
                'c': 'celsius',
                'celsius': 'celsius',
                'f': 'fahrenheit',
                'fahrenheit': 'fahrenheit',
                'k': 'kelvin',
                'kelvin': 'kelvin',
                'r': 'rankine',
                'rankine': 'rankine',
            },
            'time': {
                # Base unit: second
                's': 1.0,
                'second': 1.0,
                'seconds': 1.0,
                'min': 60.0,
                'minute': 60.0,
                'minutes': 60.0,
                'h': 3600.0,
                'hour': 3600.0,
                'hours': 3600.0,
                'day': 86400.0,
                'days': 86400.0,
                'week': 604800.0,
                'weeks': 604800.0,
                'month': 2629746.0,  # Average month
                'months': 2629746.0,
                'year': 31556952.0,  # Average year
                'years': 31556952.0,
                'ms': 0.001,
                'millisecond': 0.001,
                'milliseconds': 0.001,
                'μs': 1e-6,
                'microsecond': 1e-6,
                'microseconds': 1e-6,
                'ns': 1e-9,
                'nanosecond': 1e-9,
                'nanoseconds': 1e-9,
            },
            'area': {
                # Base unit: square meter
                'm2': 1.0,
                'square_meter': 1.0,
                'square_meters': 1.0,
                'cm2': 0.0001,
                'square_centimeter': 0.0001,
                'square_centimeters': 0.0001,
                'mm2': 1e-6,
                'square_millimeter': 1e-6,
                'square_millimeters': 1e-6,
                'km2': 1e6,
                'square_kilometer': 1e6,
                'square_kilometers': 1e6,
                'in2': 0.00064516,
                'square_inch': 0.00064516,
                'square_inches': 0.00064516,
                'ft2': 0.092903,
                'square_foot': 0.092903,
                'square_feet': 0.092903,
                'yd2': 0.836127,
                'square_yard': 0.836127,
                'square_yards': 0.836127,
                'acre': 4046.86,
                'acres': 4046.86,
                'hectare': 10000.0,
                'hectares': 10000.0,
            }
        }
    
    def convert(self, value: float, from_unit: str, to_unit: str, unit_type: str = None) -> Dict[str, Any]:
        """
        Convert between units
        
        Args:
            value: The value to convert
            from_unit: Source unit
            to_unit: Target unit
            unit_type: Optional unit type hint (length, mass, etc.)
        
        Returns:
            Dictionary with conversion result
        """
        from_unit = from_unit.lower().replace(' ', '_')
        to_unit = to_unit.lower().replace(' ', '_')
        
        # Special handling for temperature
        if unit_type == 'temperature' or self._is_temperature_unit(from_unit) or self._is_temperature_unit(to_unit):
            return self._convert_temperature(value, from_unit, to_unit)
        
        # Find the unit type if not provided
        if unit_type is None:
            unit_type = self._detect_unit_type(from_unit, to_unit)
        
        if unit_type is None:
            return {'error': f"Could not determine unit type for {from_unit} and {to_unit}"}
        
        if unit_type not in self.conversion_factors:
            return {'error': f"Unsupported unit type: {unit_type}"}
        
        factors = self.conversion_factors[unit_type]
        
        if from_unit not in factors:
            return {'error': f"Unknown unit: {from_unit}"}
        
        if to_unit not in factors:
            return {'error': f"Unknown unit: {to_unit}"}
        
        # Convert to base unit, then to target unit
        base_value = value * factors[from_unit]
        result = base_value / factors[to_unit]
        
        return {
            'original_value': value,
            'original_unit': from_unit,
            'converted_value': result,
            'converted_unit': to_unit,
            'unit_type': unit_type,
            'conversion_factor': factors[to_unit] / factors[from_unit]
        }
    
    def _detect_unit_type(self, from_unit: str, to_unit: str) -> Optional[str]:
        """Detect unit type from unit names"""
        for unit_type, factors in self.conversion_factors.items():
            if unit_type == 'temperature':
                continue  # Special case
            if from_unit in factors and to_unit in factors:
                return unit_type
        return None
    
    def _is_temperature_unit(self, unit: str) -> bool:
        """Check if unit is a temperature unit"""
        temp_units = ['c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin', 'r', 'rankine']
        return unit.lower() in temp_units
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Convert temperature units with proper offset handling"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # Normalize unit names
        unit_map = {
            'c': 'celsius', 'f': 'fahrenheit', 'k': 'kelvin', 'r': 'rankine'
        }
        from_unit = unit_map.get(from_unit, from_unit)
        to_unit = unit_map.get(to_unit, to_unit)
        
        # Convert to Celsius first
        if from_unit == 'celsius':
            celsius = value
        elif from_unit == 'fahrenheit':
            celsius = (value - 32) * 5/9
        elif from_unit == 'kelvin':
            celsius = value - 273.15
        elif from_unit == 'rankine':
            celsius = (value - 491.67) * 5/9
        else:
            return {'error': f"Unknown temperature unit: {from_unit}"}
        
        # Convert from Celsius to target
        if to_unit == 'celsius':
            result = celsius
        elif to_unit == 'fahrenheit':
            result = celsius * 9/5 + 32
        elif to_unit == 'kelvin':
            result = celsius + 273.15
        elif to_unit == 'rankine':
            result = celsius * 9/5 + 491.67
        else:
            return {'error': f"Unknown temperature unit: {to_unit}"}
        
        return {
            'original_value': value,
            'original_unit': from_unit,
            'converted_value': result,
            'converted_unit': to_unit,
            'unit_type': 'temperature'
        }
    
    def get_supported_units(self, unit_type: str = None) -> Dict[str, List[str]]:
        """Get list of supported units by type"""
        if unit_type:
            unit_type = unit_type.lower()
            if unit_type in self.conversion_factors:
                return {unit_type: list(self.conversion_factors[unit_type].keys())}
            else:
                return {'error': f"Unknown unit type: {unit_type}"}
        else:
            return {
                unit_type: list(units.keys()) 
                for unit_type, units in self.conversion_factors.items()
            }
    
    def convert_multiple(self, value: float, from_unit: str, target_units: List[str]) -> Dict[str, Any]:
        """Convert one value to multiple target units"""
        results = {}
        unit_type = None
        
        # Detect unit type from first conversion
        if target_units:
            first_conversion = self.convert(value, from_unit, target_units[0])
            if 'unit_type' in first_conversion:
                unit_type = first_conversion['unit_type']
        
        for target_unit in target_units:
            conversion_result = self.convert(value, from_unit, target_unit, unit_type)
            if 'converted_value' in conversion_result:
                results[target_unit] = conversion_result['converted_value']
            else:
                results[target_unit] = conversion_result.get('error', 'Conversion failed')
        
        return {
            'original_value': value,
            'original_unit': from_unit,
            'conversions': results,
            'unit_type': unit_type
        }
    
    def find_unit_suggestions(self, partial_unit: str) -> List[str]:
        """Find unit suggestions based on partial input"""
        suggestions = []
        partial = partial_unit.lower()
        
        for unit_type, units in self.conversion_factors.items():
            for unit in units.keys():
                if partial in unit or unit.startswith(partial):
                    suggestions.append(f"{unit} ({unit_type})")
        
        return sorted(suggestions)
    
    def conversion_chain(self, value: float, unit_chain: List[str]) -> Dict[str, Any]:
        """Convert through a chain of units"""
        if len(unit_chain) < 2:
            return {'error': 'Unit chain must have at least 2 units'}
        
        current_value = value
        conversions = []
        
        for i in range(len(unit_chain) - 1):
            from_unit = unit_chain[i]
            to_unit = unit_chain[i + 1]
            
            result = self.convert(current_value, from_unit, to_unit)
            
            if 'error' in result:
                return {'error': f"Failed at step {i+1}: {result['error']}"}
            
            conversions.append({
                'step': i + 1,
                'from_value': current_value,
                'from_unit': from_unit,
                'to_value': result['converted_value'],
                'to_unit': to_unit
            })
            
            current_value = result['converted_value']
        
        return {
            'original_value': value,
            'final_value': current_value,
            'unit_chain': unit_chain,
            'conversions': conversions
        }
    
    def calculate_ratio(self, value1: float, unit1: str, value2: float, unit2: str) -> Dict[str, Any]:
        """Calculate ratio between two quantities with units"""
        # Convert both to the same unit (use unit1 as reference)
        conversion = self.convert(value2, unit2, unit1)
        
        if 'error' in conversion:
            return conversion
        
        converted_value2 = conversion['converted_value']
        ratio = value1 / converted_value2 if converted_value2 != 0 else float('inf')
        
        return {
            'value1': value1,
            'unit1': unit1,
            'value2': value2,
            'unit2': unit2,
            'value2_converted': converted_value2,
            'ratio': ratio,
            'description': f"{value1} {unit1} is {ratio:.4f} times {value2} {unit2}"
        }