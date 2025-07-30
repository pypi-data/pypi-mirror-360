import configparser
import os
import requests
config = configparser.ConfigParser()
config.read('setup.ini')


def load_data(zenodo_record_id: str, folder: str = 'data') -> None:
    if not os.path.isdir(config['folders'][folder]):
        os.mkdir(config['folders'][folder])

    output_dir: str = config['folders'][folder]
    
    # Use the proper Zenodo API endpoint
    api_url = f"https://zenodo.org/api/records/{zenodo_record_id}"
    response: requests.Response = requests.get(api_url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch record: {response.status_code} - {response.text}")
    
    record = response.json()
    print(f"Found record: {record['metadata']['title']}")
    
    for file in record['files']:
        file_name = file['key']
        file_url = file['links']['self']
        file_path = os.path.join(output_dir, file_name)

        if os.path.isfile(file_path):
            print(f"File {file_name} already exists in folder{output_dir}")
        else:
            print(f"Downloading {file_name}...")
            file_data = requests.get(file_url).content
            with open(os.path.join(output_dir, file_name), 'wb') as f:
                f.write(file_data)

    print(f"All files downloaded in folder {output_dir}")
