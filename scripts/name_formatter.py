
def convert(name, file):
    full_name = name.split(" ")
    first_initial = full_name[0][0]
    last_name = full_name[1]
    first_name = full_name[0]
    abbr = first_initial + "." + last_name

    player = file[(file['first_name'] == first_name) & (file['last_name'] == last_name)]

    if player.empty:
        return None
    else:
        player = player.iloc[0]
        return abbr, player['team'], player['position']
