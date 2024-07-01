import requests
from bs4 import BeautifulSoup
import pandas as pd
import yaml
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(config_path='config.yaml'):
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def fetch_page(url):
    """Fetch the content of the given URL."""
    try:
        page = requests.get(url)
        page.raise_for_status()
        return page.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching page {url}: {e}")
        return None


def parse_table(page_content, table_index):
    """Parse the specified table from the page content."""
    try:
        soup = BeautifulSoup(page_content, 'html.parser')
        table = soup.find_all('table')[table_index]
        return table
    except (IndexError, AttributeError) as e:
        logging.error(f"Error parsing table at index {table_index}: {e}")
        return None


def extract_data_from_table(table):
    """Extract data from the HTML table and return as a DataFrame."""
    try:
        headers = [th.text.strip() for th in table.find_all('th')]
        rows = table.find_all('tr')[1:]
        data = [[td.text.strip() for td in row.find_all('td')] for row in rows]

        dataframe = pd.DataFrame(data, columns=headers)
        return dataframe
    except Exception as e:
        logging.error(f"Error extracting data from table: {e}")
        return pd.DataFrame()


def save_to_csv(dataframe, output_file):
    """Save the DataFrame to a CSV file."""
    try:
        dataframe.to_csv(output_file, index=False)
        logging.info(f"Data successfully saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving data to {output_file}: {e}")


def main(config_path='config.yaml'):
    config = load_config(config_path)

    for source in config['data_sources']:
        logging.info(f"Processing data source: {source['name']}")

        page_content = fetch_page(source['url'])
        if page_content:
            table = parse_table(page_content, source['table_index'])
            if table:
                dataframe = extract_data_from_table(table)
                if not dataframe.empty:
                    save_to_csv(dataframe, source['output_file'])


if __name__ == "__main__":
    main()
