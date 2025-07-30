"""Unit tests for the refactored weather system.

This module demonstrates the testability improvements in the refactored
weather system with comprehensive unit tests.
"""
import unittest
from unittest.mock import Mock, patch
import json
import os

from batem.core.utils import FilePathBuilder
from weather_refactored import (
    HumidityCalculator, ElevationService, WeatherFormatChecker,
    OpenMeteoDataParser, WeatherData, WeatherDataBuilder,
    WeatherDataProvider, WeatherDataManager
)


class TestHumidityCalculator(unittest.TestCase):
    """Test cases for HumidityCalculator class."""

    def test_absolute_humidity_kg_per_m3(self):
        """Test absolute humidity calculation in kg/m³."""
        # Test with known values
        temp = 20.0  # 20°C
        rh = 50.0    # 50% relative humidity

        result = HumidityCalculator.absolute_humidity_kg_per_m3(temp, rh)

        # Should be a positive value
        self.assertGreater(result, 0)
        # Should be reasonable for 20°C, 50% RH (around 0.0087 kg/m³)
        self.assertLess(result, 0.01)

    def test_absolute_humidity_kg_per_kg(self):
        """Test absolute humidity calculation in kg/kg."""
        temp = 25.0
        rh = 60.0
        pressure = 1013.25  # Standard atmospheric pressure

        result = HumidityCalculator.absolute_humidity_kg_per_kg(
            temp, rh, pressure
        )

        # Should be a positive value
        self.assertGreater(result, 0)
        # Should be reasonable for 25°C, 60% RH (around 0.012 kg/kg)
        self.assertLess(result, 0.02)

    def test_relative_humidity(self):
        """Test relative humidity calculation."""
        temp = 20.0
        abs_humidity = 0.0087  # kg/m³

        result = HumidityCalculator.relative_humidity(temp, abs_humidity)

        # Should be between 0 and 100
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 100)


class TestElevationService(unittest.TestCase):
    """Test cases for ElevationService class."""

    def setUp(self):
        """Set up test fixtures."""
        # self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        # self.temp_file.close()
        data_folder = FilePathBuilder().get_data_folder()
        self.temp_file = os.path.join(data_folder, 'localizations_test.json')
        with open(self.temp_file, 'w') as f:
            json.dump({}, f)
        self.service = ElevationService(self.temp_file)

    def tearDown(self):
        """Clean up test fixtures."""
        os.remove(self.temp_file)

    def test_load_elevation_data_empty_file(self):
        """Test loading elevation data from empty file."""
        # File is empty, should return empty dict
        data = self.service._load_elevation_data()
        self.assertEqual(data, {})

    def test_load_elevation_data_with_data(self):
        """Test loading elevation data from file with data."""
        # Write test data
        test_data = {"(1.0,2.0)": 100.0}
        with open(self.temp_file, 'w') as f:
            json.dump(test_data, f)

        # Reload service to read the data
        service = ElevationService(self.temp_file)
        data = service._load_elevation_data()
        self.assertEqual(data, test_data)

    @patch('weather_refactored.requests.post')
    def test_fetch_elevation_from_api_success(self, mock_post):
        """Test successful elevation fetch from API."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [{'elevation': 150.0}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.service._fetch_elevation_from_api(1.0, 2.0)
        self.assertEqual(result, 150.0)

    @patch('weather_refactored.requests.post')
    def test_fetch_elevation_from_api_failure(self, mock_post):
        """Test elevation fetch failure handling."""
        # Mock failed response
        mock_post.side_effect = Exception("API Error")

        # Should handle the error gracefully
        with self.assertRaises(Exception):
            self.service._fetch_elevation_from_api(1.0, 2.0)


class TestWeatherFormatChecker(unittest.TestCase):
    """Test cases for WeatherFormatChecker class."""

    def test_is_open_meteo_file_true(self):
        """Test Open-Meteo file detection with valid data."""
        data = {'generationtime_ms': 123}
        result = WeatherFormatChecker.is_open_meteo_file(data)
        self.assertTrue(result)

    def test_is_open_meteo_file_false(self):
        """Test Open-Meteo file detection with invalid data."""
        data = {'other_field': 'value'}
        result = WeatherFormatChecker.is_open_meteo_file(data)
        self.assertFalse(result)


class TestOpenMeteoDataParser(unittest.TestCase):
    """Test cases for OpenMeteoDataParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = OpenMeteoDataParser("Europe/Paris")

    def test_parse_open_meteo_data(self):
        """Test parsing Open-Meteo data."""
        # Sample Open-Meteo data
        data = {
            'hourly': {
                'epochtimems': [1640995200000, 1640998800000],
                'temperature_2m': [15.0, 16.0],
                'humidity_2m': [60.0, 65.0]
            },
            'hourly_units': {
                'temperature_2m': '°C',
                'humidity_2m': '%'
            }
        }

        timestamps, values, units = self.parser.parse(data)

        # Check timestamps
        self.assertEqual(len(timestamps), 2)
        self.assertEqual(timestamps[0], 1640995200000)

        # Check values
        self.assertIn('temperature', values)
        self.assertEqual(values['temperature'], [15.0, 16.0])

        # Check units
        self.assertEqual(units['temperature'], '°C')


class TestWeatherData(unittest.TestCase):
    """Test cases for WeatherData class."""

    def setUp(self):
        """Set up test fixtures."""
        self.weather_data = WeatherData(
            location="Test City",
            latitude_deg_north=45.0,
            longitude_deg_east=5.0,
            timestamps=[1640995200000, 1640998800000],
            albedo=0.2,
            pollution=0.1
        )

    def test_initialization(self):
        """Test WeatherData initialization."""
        self.assertEqual(self.weather_data.location, "Test City")
        self.assertEqual(self.weather_data.latitude_deg_north, 45.0)
        self.assertEqual(self.weather_data.longitude_deg_east, 5.0)
        self.assertEqual(self.weather_data.albedo, 0.2)
        self.assertEqual(self.weather_data.pollution, 0.1)

    def test_add_variable(self):
        """Test adding weather variables."""
        self.weather_data.add_variable(
            'temperature', '°C', [15.0, 16.0]
        )

        self.assertIn('temperature', self.weather_data.variable_names)
        self.assertEqual(
            self.weather_data.get('temperature'), [15.0, 16.0]
        )
        self.assertEqual(
            self.weather_data.units('temperature'), '°C'
        )

    def test_remove_variable(self):
        """Test removing weather variables."""
        self.weather_data.add_variable(
            'temperature', '°C', [15.0, 16.0]
        )

        result = self.weather_data.remove_variable('temperature')
        self.assertTrue(result)
        self.assertNotIn('temperature', self.weather_data.variable_names)

    def test_get_nonexistent_variable(self):
        """Test getting non-existent variable."""
        with self.assertRaises(ValueError):
            self.weather_data.get('nonexistent')

    def test_len(self):
        """Test length of weather data."""
        self.assertEqual(len(self.weather_data), 2)

    def test_contains(self):
        """Test contains operator."""
        self.weather_data.add_variable(
            'temperature', '°C', [15.0, 16.0]
        )

        self.assertTrue('temperature' in self.weather_data)
        self.assertFalse('nonexistent' in self.weather_data)

    def test_absolute_humidity_kg_per_kg(self):
        """Test absolute humidity calculation."""
        # Add required variables
        self.weather_data.add_variable('temperature', '°C', [20.0, 25.0])
        self.weather_data.add_variable('humidity', '%', [50.0, 60.0])
        self.weather_data.add_variable('pressure', 'hPa', [1013.25, 1013.25])

        result = self.weather_data.absolute_humidity_kg_per_kg()

        self.assertEqual(len(result), 2)
        self.assertGreater(result[0], 0)
        self.assertGreater(result[1], 0)


class TestWeatherDataBuilder(unittest.TestCase):
    """Test cases for WeatherDataBuilder class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_provider = Mock(spec=WeatherDataProvider)
        self.builder = WeatherDataBuilder(self.mock_provider)

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        # Should not raise an exception
        self.builder._validate_parameters("Test City", 45.0, 5.0)

    def test_validate_parameters_invalid(self):
        """Test parameter validation with invalid parameters."""
        with self.assertRaises(ValueError):
            self.builder._validate_parameters(None, None, None)

    def test_validate_parameters_partial(self):
        """Test parameter validation with partial parameters."""
        with self.assertRaises(ValueError):
            self.builder._validate_parameters(None, 45.0, None)


class TestWeatherDataManager(unittest.TestCase):
    """Test cases for WeatherDataManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = WeatherDataManager()

    def test_initialization(self):
        """Test WeatherDataManager initialization."""
        self.assertIsNotNone(self.manager.builder)
        self.assertIsNotNone(self.manager.elevation_service)

    @patch('weather_refactored.glob.glob')
    @patch('weather_refactored.FilePathBuilder')
    def test_list_available_weather_files(self, mock_builder, mock_glob):
        """Test listing available weather files."""
        # Mock file path builder
        mock_builder_instance = Mock()
        mock_builder_instance.get_data_folder.return_value = "/test/data/"
        mock_builder.return_value = mock_builder_instance

        # Mock glob results
        mock_glob.return_value = [
            "/test/data/weather1.json",
            "/test/data/weather2.json",
            "/test/data/localizations.json"
        ]

        result = self.manager.list_available_weather_files()

        # Should exclude localizations.json
        self.assertEqual(len(result), 2)
        self.assertIn("/test/data/weather1.json", result)
        self.assertIn("/test/data/weather2.json", result)
        self.assertNotIn("/test/data/localizations.json", result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the weather system."""

    def test_humidity_calculation_consistency(self):
        """Test consistency of humidity calculations."""
        temp = 20.0
        rh = 50.0

        # Calculate absolute humidity
        abs_humidity = HumidityCalculator.absolute_humidity_kg_per_m3(
            temp, rh
        )

        # Calculate relative humidity back
        calculated_rh = HumidityCalculator.relative_humidity(
            temp, abs_humidity
        )

        # Should be close to original (within 1%)
        self.assertAlmostEqual(calculated_rh, rh, delta=1.0)

    def test_weather_data_lifecycle(self):
        """Test complete weather data lifecycle."""
        # Create weather data
        weather_data = WeatherDataManager().get_weather_data(
            location="Grenoble",
            from_date='1/1/2022',
            to_date='3/1/2022'
        )

        # Test properties
        self.assertTrue('temperature' in weather_data)
        # Don't test specific values as they depend on real data

        # Test excerpt - use a smaller date range
        excerpt = weather_data.excerpt('1/1/2022', '2/1/2022')
        self.assertGreater(len(excerpt), 0)  # Should have some data

        # Test removal
        weather_data.remove_variable('temperature')
        self.assertFalse('temperature' in weather_data)


if __name__ == '__main__':
    unittest.main()
