import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial import distance
from collections import Counter

# Read the CSV file
df = pd.read_csv('data/orginal_data_100.csv')

print("=" * 80)
print("TRAJECTORY DATA EXPLORATION")
print("=" * 80)

# Basic dataset info
print(f"\n1. BASIC DATASET INFORMATION")
print(f"   Total number of trajectories: {len(df)}")
print(f"   Column name: {df.columns[0]}")

# Parse trajectories
trajectories = []
for idx, row in df.iterrows():
    try:
        traj = json.loads(row['Position'])
        trajectories.append(traj)
    except:
        print(f"   Warning: Could not parse trajectory {idx}")

print(f"   Successfully parsed trajectories: {len(trajectories)}")

# Trajectory length statistics
trajectory_lengths = [len(traj) for traj in trajectories]
print(f"\n2. TRAJECTORY LENGTH STATISTICS")
print(f"   Min points per trajectory: {min(trajectory_lengths)}")
print(f"   Max points per trajectory: {max(trajectory_lengths)}")
print(f"   Mean points per trajectory: {np.mean(trajectory_lengths):.2f}")
print(f"   Median points per trajectory: {np.median(trajectory_lengths):.2f}")
print(f"   Std dev: {np.std(trajectory_lengths):.2f}")

# Geographic bounds
all_lons = []
all_lats = []
for traj in trajectories:
    for point in traj:
        all_lons.append(point[0])
        all_lats.append(point[1])

print(f"\n3. GEOGRAPHIC BOUNDS")
print(f"   Longitude range: [{min(all_lons):.6f}, {max(all_lons):.6f}]")
print(f"   Latitude range: [{min(all_lats):.6f}, {max(all_lats):.6f}]")
print(f"   Center point: ({np.mean(all_lons):.6f}, {np.mean(all_lats):.6f})")
print(f"   Approx. area: {(max(all_lons) - min(all_lons)):.4f}° × {(max(all_lats) - min(all_lats)):.4f}°")
print(f"   Location: Porto, Portugal (based on coordinates)")

# Calculate trajectory distances
def haversine_distance(point1, point2):
    """Calculate distance between two points in km"""
    lon1, lat1 = point1
    lon2, lat2 = point2
    R = 6371  # Earth radius in km
    
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

trajectory_distances = []
for traj in trajectories:
    if len(traj) > 1:
        dist = sum(haversine_distance(traj[i], traj[i+1]) for i in range(len(traj)-1))
        trajectory_distances.append(dist)
    else:
        trajectory_distances.append(0)

print(f"\n4. TRAJECTORY DISTANCE STATISTICS (in km)")
print(f"   Min distance: {min(trajectory_distances):.3f} km")
print(f"   Max distance: {max(trajectory_distances):.3f} km")
print(f"   Mean distance: {np.mean(trajectory_distances):.3f} km")
print(f"   Median distance: {np.median(trajectory_distances):.3f} km")
print(f"   Total distance covered: {sum(trajectory_distances):.3f} km")

# Trajectory starting points clustering
print(f"\n5. TRAJECTORY STARTING POINTS")
start_points = [traj[0] for traj in trajectories if len(traj) > 0]
start_lons = [p[0] for p in start_points]
start_lats = [p[1] for p in start_points]
print(f"   Longitude range: [{min(start_lons):.6f}, {max(start_lons):.6f}]")
print(f"   Latitude range: [{min(start_lats):.6f}, {max(start_lats):.6f}]")

# Trajectory ending points
print(f"\n6. TRAJECTORY ENDING POINTS")
end_points = [traj[-1] for traj in trajectories if len(traj) > 0]
end_lons = [p[0] for p in end_points]
end_lats = [p[1] for p in end_points]
print(f"   Longitude range: [{min(end_lons):.6f}, {max(end_lons):.6f}]")
print(f"   Latitude range: [{min(end_lats):.6f}, {max(end_lats):.6f}]")

# Displacement (straight-line distance from start to end)
displacements = []
for traj in trajectories:
    if len(traj) > 1:
        disp = haversine_distance(traj[0], traj[-1])
        displacements.append(disp)

print(f"\n7. DISPLACEMENT STATISTICS (start to end)")
print(f"   Min displacement: {min(displacements):.3f} km")
print(f"   Max displacement: {max(displacements):.3f} km")
print(f"   Mean displacement: {np.mean(displacements):.3f} km")
print(f"   Median displacement: {np.median(displacements):.3f} km")

# Tortuosity (ratio of path length to displacement)
tortuosity = []
for i, traj in enumerate(trajectories):
    if len(traj) > 1 and displacements[i] > 0.001:  # avoid division by zero
        tort = trajectory_distances[i] / displacements[i]
        tortuosity.append(tort)

print(f"\n8. TORTUOSITY (path length / displacement)")
print(f"   Min tortuosity: {min(tortuosity):.3f}")
print(f"   Max tortuosity: {max(tortuosity):.3f}")
print(f"   Mean tortuosity: {np.mean(tortuosity):.3f}")
print(f"   Median tortuosity: {np.median(tortuosity):.3f}")
print(f"   (Values > 1 indicate non-straight paths)")

# Direction analysis
def calculate_bearing(point1, point2):
    """Calculate bearing between two points"""
    lon1, lat1 = np.radians(point1[0]), np.radians(point1[1])
    lon2, lat2 = np.radians(point2[0]), np.radians(point2[1])
    
    dlon = lon2 - lon1
    x = np.sin(dlon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    bearing = np.degrees(np.arctan2(x, y))
    return (bearing + 360) % 360

overall_bearings = []
for traj in trajectories:
    if len(traj) > 1:
        bearing = calculate_bearing(traj[0], traj[-1])
        overall_bearings.append(bearing)

print(f"\n9. OVERALL DIRECTION ANALYSIS")
print(f"   Number of trajectories analyzed: {len(overall_bearings)}")
# Categorize directions
def categorize_bearing(bearing):
    if 337.5 <= bearing or bearing < 22.5:
        return 'N'
    elif 22.5 <= bearing < 67.5:
        return 'NE'
    elif 67.5 <= bearing < 112.5:
        return 'E'
    elif 112.5 <= bearing < 157.5:
        return 'SE'
    elif 157.5 <= bearing < 202.5:
        return 'S'
    elif 202.5 <= bearing < 247.5:
        return 'SW'
    elif 247.5 <= bearing < 292.5:
        return 'W'
    else:
        return 'NW'

direction_counts = Counter([categorize_bearing(b) for b in overall_bearings])
print(f"   Direction distribution:")
for direction in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
    count = direction_counts.get(direction, 0)
    print(f"      {direction}: {count} ({count/len(overall_bearings)*100:.1f}%)")

# Sample trajectory details
print(f"\n10. SAMPLE TRAJECTORIES")
for i in [0, len(trajectories)//2, len(trajectories)-1]:
    traj = trajectories[i]
    print(f"\n   Trajectory #{i}:")
    print(f"      Points: {len(traj)}")
    print(f"      Distance: {trajectory_distances[i]:.3f} km")
    print(f"      Start: ({traj[0][0]:.6f}, {traj[0][1]:.6f})")
    print(f"      End: ({traj[-1][0]:.6f}, {traj[-1][1]:.6f})")
    if i < len(displacements):
        print(f"      Displacement: {displacements[i]:.3f} km")

print("\n" + "=" * 80)
print("EXPLORATION COMPLETE")
print("=" * 80)

# Save summary statistics to file
summary = {
    "total_trajectories": len(trajectories),
    "length_stats": {
        "min": int(min(trajectory_lengths)),
        "max": int(max(trajectory_lengths)),
        "mean": float(np.mean(trajectory_lengths)),
        "median": float(np.median(trajectory_lengths))
    },
    "distance_stats_km": {
        "min": float(min(trajectory_distances)),
        "max": float(max(trajectory_distances)),
        "mean": float(np.mean(trajectory_distances)),
        "median": float(np.median(trajectory_distances)),
        "total": float(sum(trajectory_distances))
    },
    "geographic_bounds": {
        "lon_range": [float(min(all_lons)), float(max(all_lons))],
        "lat_range": [float(min(all_lats)), float(max(all_lats))],
        "center": [float(np.mean(all_lons)), float(np.mean(all_lats))]
    },
    "direction_distribution": dict(direction_counts)
}

with open('trajectory_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\nSummary statistics saved to 'trajectory_summary.json'")