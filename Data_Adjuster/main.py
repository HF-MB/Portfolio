import os
import sys
import logging
import pandas as pd
import numpy as np
import yaml

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(message)s')

# A --- GENERAL CONFIGURATION ---
# A1. Load the data
input_folder = 'input'
output_file = os.path.join('result', 'result.csv')

csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
if not csv_files:
    logging.error("No CSV file found in the 'input' folder. Please add one.")
    sys.exit(1)

input_file = os.path.join(input_folder, csv_files[0])
logging.info(f"Reading data from {input_file}")

# A2. Read data and safeguards the data by renaming existing conflicting columns names.
df = pd.read_csv(input_file)
reserved_columns = [
    'starting_index',
    'copied',
    'remove',
    'main_adjuster',
    'second_adjuster',
    'third_adjuster',
    'positive_avg_adjuster',
    'negative_avg_adjuster'
]

rename_map = {}
for col in reserved_columns:
    if col in df.columns:
        new_name = f"{col}_original"
        rename_map[col] = new_name
        logging.warning(f"Column '{col}' already exists in dataset → renamed to '{new_name}' to avoid conflict.")

if rename_map:
    df.rename(columns=rename_map, inplace=True)

# A3. Index all starting rows and mark them with flags
df['starting_index'] = df.index
df['copied'] = False
df['remove'] = False

logging.info(f"Starting data: {len(df)} rows loaded successfully.")


# B --- READ CONFIG.YML ---
config_file = 'config.yml'
# B1. Check if config exists
if not os.path.exists(config_file):
    logging.error("No config.yml found. Please add it to the project folder.")
    sys.exit(1)

with open(config_file, 'r') as f:
    config = yaml.safe_load(f) or {}

logging.info("Config.yml loaded successfully")
logging.debug(config)

# B2. Set random Seed
random_seed = config.get('random_seed', 1)  # Default to 1 if key is missing
try:
    random_seed = int(random_seed)
except (ValueError, TypeError):
    logging.warning("Invalid or missing 'random_seed' in config.yml → using default value 1.")
    random_seed = 1
np.random.seed(random_seed)
logging.info(f"random_seed = {random_seed}")

# C --- FILL AND CALCULATE MULTIPLIER COLUMNS BASED ON CONFIG ---
# C1. Initialize columns with NaN
df['main_adjuster'] = np.nan
df['second_adjuster'] = np.nan
df['third_adjuster'] = np.nan

adjuster_columns = ['main_adjuster', 'second_adjuster', 'third_adjuster']

# C2. Apply Adjusters to data
for section_name in ['main', 'second', 'third']:
    # if section missing or not a dict, skip
    section = config.get(section_name)
    if not isinstance(section, dict):
        logging.warning(f"'{section_name}' section not found or not a dict in config.yml → {section_name}_adjuster stays NaN.")
        continue

    # Dimension must be provided AND exist in df
    dim = section.get('dimension')
    if not dim or dim not in df.columns:
        logging.warning(f"'{section_name}': 'dimension' ({dim}) is invalid or missing → {section_name}_adjuster stays NaN.")
        continue

    # Adjusters must be a non-empty dict
    justers = section.get('adjuster')
    if not isinstance(justers, dict) or len(justers) == 0:
        logging.debug(f"'{section_name}': no 'adjusters' configured → {section_name}_adjuster stays NaN.")
        continue

    # Robust mapping conversion (ignore non-numeric multipliers)
    safe_mapping = {}
    for k, v in justers.items():
        try:
            safe_mapping[str(k)] = float(v)
        except (ValueError, TypeError):
            logging.warning(f"Ignoring non-numeric adjuster for '{k}' in section '{section_name}'.")
    mapping = safe_mapping

    # Apply mapping; values not listed remain NaN
    df[f'{section_name}_adjuster'] = df[dim].astype(str).map(mapping)

    # Logging
    filled = df[f'{section_name}_adjuster'].notna().sum()
    logging.info(f"{section_name}: applied adjusters on '{dim}' → total of {filled} rows.")
    series_str = df[dim].astype(str)
    for val, juster in mapping.items():
        cnt = (series_str == val).sum()
        logging.info(f"{section_name}: value '{val}' (adjuster {juster}) → matched {cnt} rows.")

# C3. Positive average = mean of values > 0 (ignores NaN & negatives)
positive_df = df[adjuster_columns].where(df[adjuster_columns] > 0)
df['positive_avg_adjuster'] = positive_df.mean(axis=1, skipna=True)

# C4. Negative average = mean of values < 0 (ignores NaN & positives)
negative_df = df[adjuster_columns].where(df[adjuster_columns] < 0)
df['negative_avg_adjuster'] = negative_df.mean(axis=1, skipna=True)

# C5. Clean up
df.drop(columns=['main_adjuster', 'second_adjuster', 'third_adjuster'], inplace=True)
logging.info("Calculated per-row positive and negative average adjusters and dropped individual adjuster columns to keep dataset clean.")

# D --- ADJUSTING STEP (based on positive_avg_adjuster) ---

copies = []  # collect copied rows here

# D1. Go through the rows and roll the dice for creating copies 
for row in df.itertuples(index=True):
    m = getattr(row, 'positive_avg_adjuster', np.nan)

    # Skip if missing or not positive
    if pd.isna(m) or m <= 0:
        continue

    base = int(np.floor(m))          # guaranteed copies
    frac = float(m - base)           # fractional remainder in [0, 1)

    copies_to_make = base + (1 if (frac > 0 and np.random.rand() < frac) else 0)

    # Make the copies
    for _ in range(copies_to_make):
        new_row = df.loc[row.Index].copy()  # duplicate the original row by index
        new_row['copied'] = True          # mark as generated copy
        copies.append(new_row)

# D2. Append all copies to the main dataframe
if copies:
    copies_df = pd.DataFrame(copies)
    df = pd.concat([df, copies_df], ignore_index=True)
    logging.info(f"Adding step: created {len(copies_df)} copies. New total rows: {len(df)}.")
else:
    logging.info("Adding step: no copies created.")

# E --- REMOVAL STEP (based on negative_avg_adjuster) ---
removed_count = 0

# E1. Go through the rows (including the copy rows ) and roll the dice for removal flagging
for row in df.itertuples(index=True):
    m = getattr(row, 'negative_avg_adjuster', np.nan)

    # Skip if missing or not negative
    if pd.isna(m) or m >= 0:
        continue

    # Clamp to at most -1.0 (each row can only be deleted once)
    p = min(abs(m), 1.0)  # probability in [0, 1]

    # Bernoulli removal: if p == 1.0 -> always remove
    if p >= 1.0 or np.random.rand() < p:
        df.at[row.Index, 'remove'] = True
        removed_count += 1

logging.info(f"Removal step: flagged {removed_count} rows for removal (including copies).")

# F --- SAVE RESULT ---
os.makedirs(os.path.dirname(output_file), exist_ok=True)
df.to_csv(output_file, index=False)
logging.info(f"Final dataset saved to {output_file}")

logging.info("Process completed successfully.")