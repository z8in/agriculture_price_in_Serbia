Agricultural Prices Analysis

## Introduction
This project contains a Python script (`dataset_final.py`) that fetches agricultural product price data from the **Serbian Open Data Portal**. The script:
- Downloads JSON data of agricultural product prices.
- Maps product names from Serbian to English.
- Lets you select a product interactively.
- Computes year-to-year price changes (increase/decrease).
- Prints a summary of the biggest increase and decrease.
- Displays a bar chart of prices by year.

## Requirements
- Python 3.8+
- The following Python packages:
  - `requests`
  - `pandas`
  - `matplotlib`
  - `numpy`

## Installation
1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip3 install requests | pandas | matplotlib