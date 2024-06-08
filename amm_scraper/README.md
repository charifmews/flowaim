# clean_scrape.py

## Overview

`clean_scrape.py` is a Python script designed to scrape data from a web page using Selenium and BeautifulSoup, process the data, and save it in a JSON format. This script is specifically tailored to scrape Automated Market Maker (AMM) pool data from `https://xrpscan.com/amms`.

## Prerequisites

Before running the script, ensure that the following software and libraries are installed on your system:

- Python 3.x
- Google Chrome browser
- ChromeDriver compatible with your version of Chrome

## Installation

1. Install the required Python libraries from the root folder using `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

2. Download and install ChromeDriver:
   - Ensure that ChromeDriver is in your system's PATH, or place it in the same directory as `clean_scrape.py`.

## Requirements

The `requirements.txt` file should include the following libraries:

```text
pandas
beautifulsoup4
selenium
```

## Usage

1. Open a terminal or command prompt.

2. Navigate to the directory containing `clean_scrape.py`.

3. Run the script:
   ```bash
   python clean_scrape.py
   ```

## Script Details

- **Selenium WebDriver Setup:**
  The script sets up Selenium WebDriver with options to ignore certificate errors and uses ChromeDriver.

- **Web Page Fetching:**
  The script navigates to the URL `https://xrpscan.com/amms` and waits for the page to load completely.

- **Data Scraping:**
  The script uses BeautifulSoup to parse the HTML content and extract data from the second table on the page. It initializes lists to store the scraped data.

- **Pagination Handling:**
  The script determines the total number of pages and navigates through each page, scraping data accordingly.

- **Data Transformation:**
  The script converts the scraped data into a JSON format, processes it into a structured dictionary, and then into a transformed JSON format.

- **Output:**
  The final JSON data is printed to the console and saved to a file named `full_ammpool_data.json` in the `output` directory.

## Example Output

The output JSON file will have the following structure:

```json
[
    {
        "Rank": "1",
        "Asset Pair": "XRP/USD",
        "Market": "XRPL DEX",
        "AMM Account": "r...",
        "XRP Locked": "1000",
        "Trading Fee": "0.01",
        "LPToken Balance": "500"
    },
    ...
]
```

## Notes

- The script includes sleep periods to ensure that dynamic content loads completely.
- Adjust the sleep time if the page loading time varies.
- Ensure that the ChromeDriver version matches your installed Chrome browser version.
