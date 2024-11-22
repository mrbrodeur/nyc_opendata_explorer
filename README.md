# Explorer for NYC Open Data

## App
This app is built on Streamlit. It can be self-hosted or can be hosted on Streamlit Community. 

## Scrape
A simple scraper gets the metadata from the NYC Open Data website. The data is included in the data.json file. 

To run a scrapy spider and output the json, install scrapy in your environment, and then run `scrapy crawl nycopendata -O data.json`
