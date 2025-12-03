# IMPORTS

# csv
import csv

# json
import json

# os
import os


# CSV TO DICT FORMATTER

def csv_to_dict(path_csv):

    # open csv file and store each line into f_lines
    with open(path_csv, mode="r", encoding="utf-8") as f:

        f_lines = f.readlines()
    
    # get index of separator between metadata and nutritional data
    sep_index = f_lines.index("\n")

    # parse metadata
    metadata = {}
    metadata_lines = f_lines[:sep_index]
    for line in metadata_lines:

        # check if line is not empty or whitespace only
        if line := line.lstrip('\ufeff').strip():

            # store into metadata dict
            key, value = line.split(",", 1)
            metadata[key] = value.strip("\"")
    
    # parse nutritional data
    data = {}
    data_lines = f_lines[(sep_index + 1):]
    reader = csv.reader(data_lines)
    header = next(reader)
    for row in reader:

        # break on empty line
        if not row: break

        # format nutrient name
        row[0] = row[0].strip()

        # format both per 100ml and per serving data
        for i in (1, 2):

            # handle missing data or dashes as null
            row[i] = float(row[i].strip()) if row[i].replace(".", "", 1).isdigit() else None

            # store into data dict
            data[row[0]] = {header[i]: row[i]}

    # combine metadata and nutritional data
    json_data = metadata
    json_data["Nutritional Data"] = data

    return json_data


# FOOD DATA COLLATION

# loop through each csv file in food folder
food_data = {}
for file_name in os.listdir("./food"):

    if file_name.endswith(".csv"):

        # get path to csv file
        file_path = os.path.join("./food", file_name)

        # insert results to food data
        results = csv_to_dict(file_path)
        food_data[results["Food Name"]] = results

# write food data to foodData.json
with open("./foodData.json", "w", encoding="utf-8") as f:

    json.dump(food_data, f, ensure_ascii=False, indent=2)