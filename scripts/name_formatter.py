

import pandas as pd


def convert(name, file):
    SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
    override = pd.read_csv("data/override.csv", low_memory=False)


    full_name = name.split(" ", 1)
    if len(full_name) != 2:
        return None
    
    last_name = full_name[1]
    first_name = full_name[0]
    first_initial = first_name[0]

    last_parts_raw = last_name.replace(".", " ").split()
    last_parts = []
    for part in last_parts_raw:
        if part.lower() not in SUFFIXES:
            if part == "St ":
                last_parts.append(part + ".")
            else:
                last_parts.append(part)
    
    cleaned_last = ""
    for part in last_parts:
        cleaned_last = cleaned_last + part
    
    player = file[(file['first_name'] == first_name) & (file['last_name'] == last_name)]

    match = override[override['player_name'] == name]
    if not match.empty:
        abbr = match.iloc[0]['abbreviation']
        player = player.iloc[0]
        team = player['team']
        if team == "LAR":
            team = "LA"
        elif team == "WSH":
            team = "WAS"
        return abbr, team, player['position']

    if player.empty:
        return None
    else:
        player = player.iloc[0]
        
        # Find all players with the same last name AND same first initial
        same_last_and_initial = file[
            (file['last_name'] == last_name) & 
            (file['first_name'].str[0] == first_name[0])
        ].sort_values('first_name')
        
        if len(same_last_and_initial) == 1:
            # Only one player with this last name and first initial
            abbr = first_name[0] + "." + cleaned_last
        else:
            # Multiple players with same initial
            all_first_names = same_last_and_initial['first_name'].tolist()
            
            # Find this player's position in alphabetical order
            player_index = all_first_names.index(first_name)
            
            # Check only players that come BEFORE this one alphabetically
            chars_needed = 1
            for i in range(player_index):
                other_first = all_first_names[i]
                # Find how many chars needed to differentiate from this earlier player
                temp_chars = 1
                while temp_chars <= min(len(first_name), len(other_first)):
                    if first_name[:temp_chars] != other_first[:temp_chars]:
                        break
                    temp_chars += 1
                chars_needed = max(chars_needed, temp_chars)
            
            abbr = first_name[:chars_needed] + "." + cleaned_last
        team = player['team']
        if team == "LAR":
            team = "LA"
        elif team == "WSH":
            team = "WAS"
        return abbr, team, player['position']
    
