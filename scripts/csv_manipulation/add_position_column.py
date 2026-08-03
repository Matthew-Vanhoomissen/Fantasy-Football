def assign_position(row):
    passing = row['average_passing_yards']
    rushing = row['average_rushing_yards']
    receiving = row['average_recieving_yards']

    total = passing + rushing + receiving

    # Minimum threshold - if total activity is too low, classify as unknown
    if total < 10:
        return -1

    pass_ratio = passing / total
    rush_ratio = rushing / total
    rec_ratio = receiving / total

    # Position only assigned if one category
    # is clearly dominant, not just slightly higher than others
    dominance_threshold = 0.45

    if pass_ratio >= dominance_threshold:
        return 0  # QB

    if rush_ratio >= dominance_threshold:
        return 1  # RB

    if rec_ratio >= dominance_threshold:
        return 2  # WR/TE

    # Does a lot of everything or no clear role (Taysom Hill types)
    return -1
