# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import requests
import glob
from pathlib import Path
from datetime import datetime

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

def download_file(uri, data_id, file_path):
    # response = requests.get(uri)
    # # Check if the request was successful (status code 200)
    # if response.status_code == 200:
    #     # Open a local file to write the CSV data to
    #     with open(file_path, 'wb') as file:
    #         file.write(response.content)  # Write the binary content to the file
    with open(file_path, 'wb') as f, requests.get(uri, stream=True) as r:
        for line in r.iter_lines():
            f.write(line+'\n'.encode())
    print(f'{data_id} - File downloaded successfully.')
    return 'success'
    # else:
    #     print(f"{data_id} - Failed to download file. Status code: {response.status_code}")
    #     return 'fail'


class NycopendataScrapePipeline:
    def __init__(self):
        # Set the directory where the JSON files will be saved
        self.output_dir = 'data'
        self.today_date = datetime.today().strftime('%Y%m%d')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if os.path.isdir(self.output_dir):
            list_of_files = glob.glob(f"{self.output_dir}/*")
            self.downloaded_id_list = [Path(f).stem for f in list_of_files]


    def process_item(self, item, spider):
        
        data_id = item.get('id')  # get id from item
        
        # skip if in already dl'd dataset. DELETE THIS after done
        if data_id in self.downloaded_id_list:
            print(f"{data_id} was found in the 'already downloaded' list. Not processing again. Returning item.")
            return item
        
        print(f"Starting to process {item.get('name')} at id {data_id}")
        data_type = item.get('data_type')
       
        if data_type == 'Dataset':
            print(f"Identified as DATASET. Processing - {data_id}")
            uri = f'https://data.cityofnewyork.us/api/views/{data_id}/rows.csv?date={self.today_date}&accessType=DOWNLOAD'
            file_type = 'csv'
        elif data_type == 'Map':
            print(f"Identified as MAP. Processing - {data_id}")
            uri = f'https://data.cityofnewyork.us/api/geospatial/{data_id}?method=export&format=GeoJSON'
            file_type = 'geojson'
        else:
            print(f"NOT identified as dataset or map. Skipping - {data_id} - data_type:{data_type}")
            return item
        
        file_path = os.path.join(self.output_dir, f'{data_id}.{file_type}')
        
        r = download_file(uri, data_id, file_path)
        if r == 'success':
            item['file_download'] = True

        # some Map datasets do not have geojson. If so, they will download as a 53byte almost-empty
        # file. Check if the file is less than 1k, if so, delete it and download it as a csv. If they
        # do not have a geojson, they will have a csv.
        if data_type == 'Map' and os.path.getsize(file_path) < 100:
            Path.unlink(file_path)
            item['file_download'] = False
            print(f'Data for {data_id} did not include geojson data. Not downloading.')

        return item
    
    # offset = 0
        # data_rows = []
        # while True:
        #     uri = f'https://data.cityofnewyork.us/resource/{data_id}.json?$offset={offset}'
        #     r = requests.get(uri)
        #     if r.status_code == 200:
        #         time.sleep(10)
        #         if r.json():
        #             data_rows += r.json()
        #             offset += 1000
        #         else:
        #             break
        #     else:
        #         print(r.text)

        # # Save the item as a JSON file
        # with open(file_path, 'w', encoding='utf-8') as f:
        #     json.dump(data_rows, f, ensure_ascii=False, indent=4)

        # Return the item to allow further processing
