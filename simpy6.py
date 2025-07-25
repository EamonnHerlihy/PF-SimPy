"""
Simulates asset progression through a multi-phase development pipeline using SimPy.
Years and number of assets per year are now defined by variables (NUM_YEARS, ASSETS_PER_YEAR).
Each year, NUM_ASSETS_PER_YEAR new assets are initialized at a random time within that year, for NUM_YEARS years.
Assets proceed sequentially through phases (ID1, ID2, Ph1, Ph2A, Ph2B, Ph3, File), each with defined duration and probability of success.
Failed assets do not proceed further. Simulation details are stored in a Pandas DataFrame.
Runs multiple replications in parallel using ProcessPoolExecutor and prints total running time.
"""

import simpy
import random
import pandas as pd
import concurrent.futures
import time
import os

NUM_REPLICATIONS = 1000
NUM_YEARS = 10
ASSETS_PER_YEAR = 50
TOTAL_ASSETS = NUM_YEARS * ASSETS_PER_YEAR

# Option to turn on/off printing
VERBOSE = False

# Store important simulation details in a dictionary for easy access and reference
SIMULATION_DETAILS = {
    "num_years": NUM_YEARS,
    "assets_per_year": ASSETS_PER_YEAR,
    "phases": [
        {"name": "ID1",   "duration": 10,  "success_prob": 0.95},
        {"name": "ID2",   "duration": 12,  "success_prob": 0.90},
        {"name": "Ph1",   "duration": 52,  "success_prob": 0.5},
        {"name": "Ph2A",  "duration": 52,  "success_prob": 0.6},
        {"name": "Ph2B",  "duration": 52,  "success_prob": 0.7},
        {"name": "Ph3",   "duration": 104, "success_prob": 0.5},
        {"name": "File",  "duration": 26,  "success_prob": 0.9},
    ]
}

def asset_trajectory(env, asset_id, results, records, replication_id, verbose=VERBOSE):
    # Asset is initialized at a random time within its assigned year
    year = (asset_id - 1) // ASSETS_PER_YEAR
    year_start = year * 52  # Each year is 52 weeks
    start_time = year_start + random.uniform(0, 52)
    yield env.timeout(start_time)
    if verbose:
        print(f"[Replication {replication_id}] Year {year+1} Asset {asset_id - year*ASSETS_PER_YEAR} (Global Asset {asset_id}) initialized at week {env.now:.1f}")
    phase_results = {}
    current_time = env.now
    success = True

    for idx, phase in enumerate(SIMULATION_DETAILS["phases"]):
        if not success:
            break
        if verbose:
            print(f"[Replication {replication_id}] Asset {asset_id} enters {phase['name']} at week {env.now:.1f}")
        yield env.timeout(phase["duration"])
        success = random.random() < phase["success_prob"]
        outcome = "SUCCESS" if success else "FAILURE"
        if verbose:
            print(f"[Replication {replication_id}] Asset {asset_id} completed {phase['name']} at week {env.now:.1f} with {outcome}")
        phase_results[phase["name"]] = {
            "start_time": current_time,
            "end_time": env.now,
            "outcome": outcome
        }
        # Store all important simulation information in a table (list of dicts)
        records.append({
            "replication": replication_id,
            "asset_id": asset_id,
            "phase": phase["name"],
            "phase_idx": idx,
            "phase_duration": phase["duration"],
            "phase_success_prob": phase["success_prob"],
            "phase_start_time": current_time,
            "phase_end_time": env.now,
            "phase_outcome": outcome,
            "asset_init_time": start_time
        })
        current_time = env.now

    results[asset_id] = phase_results

def run_simulation(num_assets, replication_id, verbose=VERBOSE):
    env = simpy.Environment()
    results = {}
    records = []
    for asset_id in range(1, num_assets + 1):
        env.process(asset_trajectory(env, asset_id, results, records, replication_id, verbose=verbose))
    env.run()
    return replication_id, results, records

if __name__ == "__main__":
    all_records = []
    all_results = []

    start_time_wall = time.time()

    max_workers = min(8, os.cpu_count() or 1)
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(run_simulation, TOTAL_ASSETS, rep_id, VERBOSE)
            for rep_id in range(1, NUM_REPLICATIONS + 1)
        ]
        for future in concurrent.futures.as_completed(futures):
            rep_id, results, records = future.result()
            all_results.append({"replication": rep_id, "results": results})
            all_records.extend(records)
            if VERBOSE:
                print(f"\nSimulation Results for Replication {rep_id}:")
                for asset_id, info in results.items():
                    print(f"Asset {asset_id}:")
                    for phase in SIMULATION_DETAILS["phases"]:
                        pname = phase["name"]
                        if pname in info:
                            p = info[pname]
                            print(f"  {pname}: Started at week {p['start_time']:.1f}, Ended at week {p['end_time']:.1f}, Outcome: {p['outcome']}")
                        else:
                            break

    end_time_wall = time.time()
    elapsed = end_time_wall - start_time_wall
    print(f"\nTotal running time: {elapsed:.2f} seconds")

    # Store all important simulation information in a table (Pandas DataFrame) for further analysis
    df = pd.DataFrame(all_records)
    print("\nFull Simulation Table (first 10 rows):")
    print(df.head(10))