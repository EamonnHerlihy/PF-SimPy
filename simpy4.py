"""
This script simulates the progression of multiple assets through a multi-phase development pipeline using SimPy.
Each asset is initialized at a random time within a 52-week window (based on the Ph1 phase duration), then proceeds
sequentially through a series of phases (ID1, ID2, Ph1, Ph2A, Ph2B, Ph3, File). Each phase has a defined duration
and probability of success. If an asset fails a phase, it does not proceed to subsequent phases. The simulation
prints the timing and outcome for each asset at each phase, and stores all simulation details in a Pandas DataFrame
for further analysis. This version runs for 10 replications.
"""

import simpy
import random
import pandas as pd
import time

NUM_REPLICATIONS = 1000

# Option to turn on/off printing
VERBOSE = False

# Store important simulation details in a dictionary for easy access and reference
SIMULATION_DETAILS = {
    "num_assets": 1000,
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
    # Asset is initialized at a random time (0-52 weeks)
    start_time = random.uniform(0, SIMULATION_DETAILS["phases"][2]["duration"])  # Use Ph1 duration for randomization
    yield env.timeout(start_time)
    if verbose:
        print(f"[Replication {replication_id}] Asset {asset_id} initialized at week {env.now:.1f}")
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
    return results, records

if __name__ == "__main__":

    all_records = []
    all_results = []

    start_time_wall = time.time()

    for rep in range(1, NUM_REPLICATIONS + 1):
        if VERBOSE:
            print(f"\n=== Starting Replication {rep} ===")
        results, records = run_simulation(SIMULATION_DETAILS["num_assets"], rep, verbose=VERBOSE)
        all_results.append({"replication": rep, "results": results})
        all_records.extend(records)
        if VERBOSE:
            print(f"\nSimulation Results for Replication {rep}:")
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