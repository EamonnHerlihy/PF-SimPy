"""
This script simulates the progression of multiple assets through a multi-phase development pipeline using SimPy.
Each asset is initialized at a random time within a 52-week window (based on the Ph1 phase duration), then proceeds
sequentially through a series of phases (ID1, ID2, Ph1, Ph2A, Ph2B, Ph3, File). Each phase has a defined duration
and probability of success. If an asset fails a phase, it does not proceed to subsequent phases. The simulation
prints the timing and outcome for each asset at each phase, and summarizes the results at the end.
"""

import simpy
import random

NUM_ASSETS = 10

# Define phase names and parameters
PHASES = [
    {"name": "ID1",   "duration": 10,  "success_prob": 0.95},
    {"name": "ID2",   "duration": 12,  "success_prob": 0.90},
    {"name": "Ph1",   "duration": 52,  "success_prob": 0.5},
    {"name": "Ph2A",  "duration": 52,  "success_prob": 0.6},
    {"name": "Ph2B",  "duration": 52,  "success_prob": 0.7},
    {"name": "Ph3",   "duration": 104, "success_prob": 0.5},
    {"name": "File",  "duration": 26,  "success_prob": 0.9},
]

def asset_trajectory(env, asset_id, results):
    # Asset is initialized at a random time (0-52 weeks)
    start_time = random.uniform(0, PHASES[2]["duration"])  # Use Ph1 duration for randomization
    yield env.timeout(start_time)
    print(f"Asset {asset_id} initialized at week {env.now:.1f}")
    phase_results = {}
    current_time = env.now
    success = True

    for idx, phase in enumerate(PHASES):
        if not success:
            break
        print(f"Asset {asset_id} enters {phase['name']} at week {env.now:.1f}")
        yield env.timeout(phase["duration"])
        success = random.random() < phase["success_prob"]
        outcome = "SUCCESS" if success else "FAILURE"
        print(f"Asset {asset_id} completed {phase['name']} at week {env.now:.1f} with {outcome}")
        phase_results[phase["name"]] = {
            "start_time": current_time,
            "end_time": env.now,
            "outcome": outcome
        }
        current_time = env.now
        # Example: If you want to branch at Ph2A/Ph2B, you can add logic here

    results[asset_id] = phase_results

def run_simulation(num_assets):
    env = simpy.Environment()
    results = {}
    for asset_id in range(1, num_assets + 1):
        env.process(asset_trajectory(env, asset_id, results))
    env.run()
    return results

if __name__ == "__main__":
    results = run_simulation(NUM_ASSETS)
    print("\nSimulation Results:")
    for asset_id, info in results.items():
        print(f"Asset {asset_id}:")
        for phase in PHASES:
            pname = phase["name"]
            if pname in info:
                p = info[pname]
                print(f"  {pname}: Started at week {p['start_time']:.1f}, Ended at week {p['end_time']:.1f}, Outcome: {p['outcome']}")
            else:
                break