import pandas as pd

# === Load players from nflverse ===
players_url = "https://github.com/nflverse/nflverse-data/releases/download/players/players.csv.gz"
players = pd.read_csv(players_url, compression="gzip", low_memory=False)


# === Normalize names ===
def normalize_name(name):
    if pd.isna(name):
        return ""
    return name.replace(".", "").replace(" ", "").replace("-", "").replace("'", "").strip()


# Create multiple normalized versions
players["norm_initial"] = (
    players["first_name"].str[0].fillna("") + players["last_name"].fillna("")
).apply(normalize_name)

players["norm_full"] = (
    players["first_name"].fillna("") + players["last_name"].fillna("")
).apply(normalize_name)

players["norm_display"] = players["display_name"].apply(normalize_name)

# Keep only fantasy-relevant positions
skill_positions = ["QB", "RB", "WR", "TE"]
players = players[players["position"].isin(skill_positions)]

# === Load your normalized name list ===
pbp_names = pd.read_csv("../data/player_name_map.csv")
if "position" in pbp_names.columns:
    pbp_names = pbp_names.drop(columns=["position"])
    
pbp_names["normalized_name"] = pbp_names["normalized_name"].apply(normalize_name)

# === Try matching with different strategies ===
# Strategy 1: Match with initial + last name
merged = pbp_names.merge(
    players[["norm_initial", "position"]].rename(columns={"norm_initial": "normalized_name"}),
    on="normalized_name",
    how="left"
)

# Strategy 2: For unmatched, try full name
unmatched = merged[merged["position"].isna()].copy()
matched = merged[merged["position"].notna()].copy()

if len(unmatched) > 0:
    unmatched = unmatched.drop(columns=["position"])
    unmatched2 = unmatched.merge(
        players[["norm_full", "position"]].rename(columns={"norm_full": "normalized_name"}),
        on="normalized_name",
        how="left"
    )
    matched = pd.concat([matched, unmatched2[unmatched2["position"].notna()]])
    unmatched = unmatched2[unmatched2["position"].isna()]

# Strategy 3: For still unmatched, try display name
if len(unmatched) > 0:
    unmatched = unmatched.drop(columns=["position"])
    unmatched3 = unmatched.merge(
        players[["norm_display", "position"]].rename(columns={"norm_display": "normalized_name"}),
        on="normalized_name",
        how="left"
    )
    matched = pd.concat([matched, unmatched3[unmatched3["position"].notna()]])
    unmatched = unmatched3[unmatched3["position"].isna()]

# Combine results
merged = pd.concat([matched, unmatched], ignore_index=True)

# === Deduplicate ===
position_priority = {"QB": 1, "RB": 2, "WR": 3, "TE": 4}
merged["priority"] = merged["position"].map(position_priority).fillna(999)
merged = merged.sort_values("priority").drop_duplicates(subset=["normalized_name"], keep="first")
merged = merged.drop(columns=["priority"])

# === Export ===
merged.to_csv("../data/player_position_mapping_clean.csv", index=False)
print(f"Matched: {merged['position'].notna().sum()} / {len(merged)}")
print(f"\nUnmatched players:")
print(merged[merged["position"].isna()][["raw_name", "normalized_name"]])