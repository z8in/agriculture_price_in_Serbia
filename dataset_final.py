import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
import json as _json

# Data source (Serbian open data)
URL = "https://opendata.stat.gov.rs/data/WcfJsonRestService.Service1.svc/dataset/0306IND01/2/json"

# ---------------------------
# Fetch and parse JSON robustly
# ---------------------------
resp = requests.get(URL, timeout=30)
resp.raise_for_status()

text = resp.text.lstrip("\ufeff").strip()  # tolerate BOMs

dataset = None
try:
    data = resp.json()  # fast path
except ValueError:
    try:
        data = _json.loads(text)  # fallback
    except Exception:
        # last resort: let pandas parse from string
        dataset = pd.read_json(io.StringIO(text))
        data = None

if dataset is None:
    if isinstance(data, list):
        dataset = pd.DataFrame(data)
    elif isinstance(data, dict):
        # try common wrappers in case the provider changes shape
        for key in ("items", "data", "results", "value"):
            if key in data and isinstance(data[key], list):
                dataset = pd.DataFrame(data[key])
                break
        else:
            dataset = pd.json_normalize(data)
    else:
        raise SystemExit("Unexpected JSON structure from the API.")

# Ensure numeric typing and drop invalid rows
dataset["vrednost"] = pd.to_numeric(dataset["vrednost"], errors="coerce")
dataset["god"] = pd.to_numeric(dataset["god"], errors="coerce")
dataset = dataset.dropna(subset=["vrednost", "god"]).copy()

# ---------------------------
# Product name mapping (SR -> EN)
# ---------------------------
mapping = {
    'Pšenica':'Wheat', 
    'Ječam':'Barley', 
    'Kukuruz':'Corn', 
    'Ovas':'Oat', 
    'Raž':'Rye', 
    'Uljana repica':'Oilseed rape',
    'Šećerna repa':'Sugar beet', 
    'Suncokret':'Sunflower', 
    'Soja':'Soy', 
    'Duvan':'Tobacco', 
    'Krompir':'Potato',
    'Paradajz':'Tomato', 
    'Kupus i kelj':'Cabbage and kale', 
    'Crni luk':'Onion', 
    'Paprika':'Pepper', 
    'Pasulj':'Bean',
    'Dinje i lubenice':'Melon and Watermelon', 
    'Lucerka':'Alfalfa', 
    'Jabuke':'Apples', 
    'Kruške':'Pear', 
    'Šljive':'Plum',
    'Orasi':'Nuts', 
    'Grožđe':'Grapes', 
    'Jagode':'Strawberries', 
    'Maline':'Raspberries', 
    'Trešnje':'Cherries', 
    'Višnje':'Sour cherries',
    'Kajsije':'Apricots', 
    'Breskve':'Peach', 
    'mršave i mesnate svinje':'fleshy pigs',
    'masne i polumasne svinje':'fat pigs', 
    'Ovce - ukupno':'sheeps', 
    'Tovni pilići':'Chickens',
    'Kravlje mleko, mil.l':'Cow milk', 
    'Ovčije mleko, mil.l':'Sheep milk', 
    'Jaja, mil.kom.':'Eggs',
    'Vuna, t':'Wool', 
    'Med, t':'Honey'
}

# Apply mapping
if "nProizvod" in dataset.columns:
    dataset['nProizvod'] = dataset['nProizvod'].replace(mapping)
else:
    raise SystemExit("Column 'nProizvod' is missing from the dataset.")

# ---------------------------
# Interactive selection
# ---------------------------
unique_names = sorted(map(str, dataset['nProizvod'].dropna().unique()))
print("Here is a list of products for which you can check prices over the years:\n")
for name in unique_names:
    print(" -", name)

user_input = input("\nEnter product name exactly as shown above: ").strip()
lookup = {x.casefold(): x for x in unique_names}
if user_input.casefold() not in lookup:
    raise SystemExit(f"Product '{user_input}' not found. Please run again and choose one from the list.")
product = lookup[user_input.casefold()]

# ---------------------------
# Filtering and metrics
# ---------------------------
cond = dataset.loc[dataset['nProizvod'] == product].copy()
cond = cond.sort_values('god')
cond['price_relation_to_previous_year'] = (
    cond['vrednost'].pct_change().fillna(0).round(4)
)
cond = cond.loc[:, ['nProizvod', 'god', 'vrednost', 'price_relation_to_previous_year']]

# Largest decrease & increase (YoY)
max_dec = cond['price_relation_to_previous_year'].min()
max_inc = cond['price_relation_to_previous_year'].max()

year_max_dec = int(cond.loc[cond['price_relation_to_previous_year'] == max_dec, 'god'].iloc[0])
year_max_inc = int(cond.loc[cond['price_relation_to_previous_year'] == max_inc, 'god'].iloc[0])

price_at_dec = float(cond.loc[cond['god'] == year_max_dec, 'vrednost'].iloc[0])
price_before_dec = round(price_at_dec / (1 + max_dec), 2)

price_at_inc = float(cond.loc[cond['god'] == year_max_inc, 'vrednost'].iloc[0])
price_before_inc = round(price_at_inc / (1 + max_inc), 2)

print(
    f"\nFor {product} biggest decrease in price was in year {year_max_dec} "
    f"where price was {price_at_dec} RSD, a total decrease of {round(max_dec*100, 2)}% "
    f"from the previous year {year_max_dec - 1} where price was {price_before_dec} RSD."
)
print(
    f"For {product} biggest increase in price was in year {year_max_inc} "
    f"where price was {price_at_inc} RSD, a total increase of {round(max_inc*100, 2)}% "
    f"from the previous year {year_max_inc - 1} where price was {price_before_inc} RSD."
)

# ---------------------------
# Plot
# ---------------------------
fig, ax = plt.subplots()
ax.bar(cond['god'].astype(int), cond['vrednost'])
ax.set_xlabel('Year')
ax.set_ylabel('Price (RSD)')
ax.set_title(
    f"Price of {product} from year {int(cond['god'].min())}-{int(cond['god'].max())}"
)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()