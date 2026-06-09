import pandas as pd
from collections import defaultdict

# Load the CSV
df = pd.read_csv('../data/nfl_players.csv')

# Filter for offensive positions only
OFFENSIVE_POSITIONS = ['QB', 'WR', 'RB', 'TE', 'FB']
df = df[df['position'].isin(OFFENSIVE_POSITIONS)]

print(f"Filtering to {len(df)} offensive players (QB, WR, RB, TE, FB)\n")

# Create a key: first_initial + last_name
df['key'] = df['first_name'].str[0] + '.' + df['last_name']

# Group by the key and find duplicates
duplicates = defaultdict(list)

for _, row in df.iterrows():
    key = row['key']
    duplicates[key].append({
        'first_name': row['first_name'],
        'last_name': row['last_name'],
        'team': row['team'],
        'position': row['position']
    })

# Filter to only keys with multiple players
conflicts = {k: v for k, v in duplicates.items() if len(v) > 1}

# Print results
print(f"Found {len(conflicts)} conflicts among offensive players:\n")

for key, players in sorted(conflicts.items()):
    print(f"\n{key} ({len(players)} players):")
    for i, p in enumerate(sorted(players, key=lambda x: x['first_name']), 1):
        print(f"  {i}. {p['first_name']} {p['last_name']} - {p['team']} ({p['position']})")

# Generate override CSV
print("\n" + "="*60)
print("GENERATING OVERRIDE CSV...")
print("="*60 + "\n")

overrides = []
for key, players in sorted(conflicts.items()):
    sorted_players = sorted(players, key=lambda x: x['first_name'])
    
    # First player alphabetically gets the simple abbreviation
    first_player = sorted_players[0]
    overrides.append({
        'player_name': f"{first_player['first_name']} {first_player['last_name']}",
        'abbreviation': key
    })
    
    # Others need extended abbreviations
    for player in sorted_players[1:]:
        # Find minimum characters needed
        chars_needed = 2
        while chars_needed <= len(player['first_name']):
            abbr = player['first_name'][:chars_needed] + '.' + player['last_name']
            # Check if this conflicts with any other player
            conflict = False
            for other in sorted_players:
                if other != player and other['first_name'][:chars_needed] == player['first_name'][:chars_needed]:
                    conflict = True
                    break
            if not conflict:
                break
            chars_needed += 1
        
        final_abbr = player['first_name'][:chars_needed] + '.' + player['last_name']
        overrides.append({
            'player_name': f"{player['first_name']} {player['last_name']}",
            'abbreviation': final_abbr
        })

override_df = pd.DataFrame(overrides)
override_df.to_csv('../data/name_overrides.csv', index=False)
