import configparser
import os

config = configparser.ConfigParser()
config.read('setup.ini')


class WeatherFilePathBuilder:

    def __init__(self):
        pass

    def get_weather_json_file_path(self, location: str) -> str:
        """
        Get the path to the weather json file for a given location.

        Args:
            location: The location to get the weather json file path for.

        Returns:
            The path to the weather json file for the given location.
        """

        path = os.path.join(config['folders']['data'],
                            f"{location}.json")

        return path
