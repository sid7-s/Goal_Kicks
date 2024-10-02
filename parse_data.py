import json
import pandas as pd
import os

# Directory containing the JSON files
directory_path = 'tmp/'  # Change this to your directory path


# Function to expand the 'qualifier' column into id, qualifierId, and value
def expand_qualifiers(df, qualifier_col, max_qualifiers=16):
    qualifiers = ['id', 'qualifierId', 'value']
    for i in range(max_qualifiers):
        for qual in qualifiers:
            col_name = f'qualifier/{i}/{qual}'
            df[col_name] = df[qualifier_col].apply(
                lambda x: x[i].get(qual) if i < len(x) and isinstance(x[i], dict) else None
            )
    return df


# Load Events and Qualifiers data
events = pd.read_excel("Opta Events.xlsx")
qualifiers = pd.read_excel("Opta Qualifiers.xlsx")

# Optimize replacement using map for 'typeId' (matching with events)
event_map = dict(zip(events['Code'], events['Event']))

# Optimize replacement for qualifiers using map
qualifier_map = dict(zip(qualifiers['Code'], qualifiers['Qualifier']))

# Loop over all .txt files in the directory
for file_name in os.listdir(directory_path):
    if file_name.endswith('.txt'):
        file_path = os.path.join(directory_path, file_name)

        # Load the JSON data from the file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Extract home and away team names
        home_team = data['matchInfo']['contestant'][0]['officialName']
        home_team_id = data['matchInfo']['contestant'][0]['id']
        away_team = data['matchInfo']['contestant'][1]['officialName']
        away_team_id = data['matchInfo']['contestant'][1]['id']

        print(f"Processing file: {file_name}")
        print(f"Home Team: {home_team} (ID: {home_team_id})")
        print(f"Away Team: {away_team} (ID: {away_team_id})")

        # Extract liveData and convert it to DataFrame
        live_data = data['liveData']['event']
        df = pd.json_normalize(live_data)

        # Apply the expansion function to the DataFrame
        df = expand_qualifiers(df, 'qualifier')

        # Drop the original 'qualifier' column since it has been expanded
        df = df.drop(columns=['qualifier'])

        # Replace typeId with corresponding event from Events data
        df['typeId'] = df['typeId'].map(event_map)

        # Replace qualifierId with corresponding qualifier from Qualifiers data
        columns = [f'qualifier/{i}/qualifierId' for i in range(16)]
        for column in columns:
            df[column] = df[column].map(qualifier_map)

        # Replace outcome with descriptive values
        df['outcome'] = df['outcome'].replace({0: 'Unsuccessful', 1: 'Successful'})

        # Rename contestantId column to team_name and replace team IDs with names
        df.rename(columns={'contestantId': 'team_name'}, inplace=True)
        team_map = {home_team_id: home_team, away_team_id: away_team}
        df['team_name'] = df['team_name'].replace(team_map)

        # Define output file path based on team names and save to CSV
        output_file_name = f"Matches/League/{home_team} vs {away_team}.csv"
        df.to_csv(output_file_name, index=False)

        print(f"Saved file: {output_file_name}")

print("All files processed successfully.")
