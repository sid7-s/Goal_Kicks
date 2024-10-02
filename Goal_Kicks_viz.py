import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from matplotlib.colors import LinearSegmentedColormap
import os

bg_color = '#ffffff'  # Background color for the pitch
line_color = '#000000'  # Line color for the pitch

def visualize_gk(ax, df, team_name, col):
    # Create the pitch with the line_zorder to control layering
    pitch = Pitch(pitch_type='opta', pitch_color=bg_color, line_color=line_color, linewidth=1, line_zorder=2, corner_arcs=True)
    pitch.draw(ax=ax)

    # Filtering goal kicks for the specific team
    team_df = df[df['team_name'] == team_name]

    # Plot the heatmap for the goal kick end points using KDE
    flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors", [bg_color, col], N=500)
    kde = pitch.kdeplot(team_df.end_x, team_df.end_y, ax=ax, fill=True, levels=100, thresh=0.02, cut=4, cmap=flamingo_cmap)

    # Plot the passes with thinner lines
    pitch.lines(team_df.x, team_df.y, team_df.end_x, team_df.end_y, lw=0.1, transparent=True, comet=True, color='#00a0de', ax=ax, alpha=0.5)

    # Plot scatter points at the end of each pass with smaller markers
    pitch.scatter(team_df.end_x, team_df.end_y, s=1, edgecolor='#00a0de', linewidth=0.1, color='#00a0de', zorder=3, ax=ax)

    # Set title for each subplot with smaller font size
    ax.set_title(f"{team_name}", color=line_color, fontsize=9, fontweight='bold')

# Directory containing match data files
directory_path = 'Matches/League/'

# Initialize an empty DataFrame to append data from all matches
all_matches_df = pd.DataFrame()

# Loop over all CSV files in the directory and concatenate them into one DataFrame
for file_name in os.listdir(directory_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(directory_path, file_name)
        match_df = pd.read_csv(file_path)

        # Append data to all_matches_df
        all_matches_df = pd.concat([all_matches_df, match_df], ignore_index=True)

# Remove rows where 'typeId' is "Deleted event"
all_matches_df = all_matches_df[all_matches_df['typeId'] != "Deleted event"]

# Filter the DataFrame for goal kicks
df = all_matches_df[all_matches_df.isin(["Goal Kick"]).any(axis=1) & (all_matches_df["outcome"]=="Successful")]

# Extract values for 'Pass End X' and 'Pass End Y'
target_value_x = 'Pass End X'
target_value_y = 'Pass End Y'

# Function to extract values next to a target column
def extract_next_value(row, target_value):
    for col_index, cell_value in enumerate(row):
        if cell_value == target_value and col_index < len(row) - 1:
            return float(row[col_index + 1])
    return None

# Apply the function along the rows of the DataFrame to create new columns for end_x and end_y
df['end_x'] = df.apply(lambda row: extract_next_value(row, target_value_x), axis=1).fillna(0)
df['end_y'] = df.apply(lambda row: extract_next_value(row, target_value_y), axis=1).fillna(0)

# Get unique team names and sort them alphabetically
team_names = sorted(df['team_name'].unique())

# Create subplots based on the number of teams
num_teams = len(team_names)
cols = 3
rows = 5

fig, axs = plt.subplots(rows, cols, figsize=(6, 6))

axs = axs.flatten()

# Loop through the teams and create a subplot for each team's goal kicks
for i, team_name in enumerate(team_names):
    if i == num_teams-1:
        ax = axs[i+1]
    else:
        ax = axs[i]
    visualize_gk(ax, df, team_name, hcol)

# Remove unused subplots
for j in ([i, i+2]):
    fig.delaxes(axs[j])

# Show the plot
plt.tight_layout()
fig.savefig('output_figure.png', dpi=300, bbox_inches='tight')
plt.show()
