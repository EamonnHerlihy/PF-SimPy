"""
This script simulates the progression of multiple assets through a single development phase using SimPy.
Each asset is initialized at a random time within a 52-week window, enters the phase, and after the phase duration,
its success or failure is determined probabilistically. The simulation prints the timing and outcome for each asset.
"""

import simpy
import random

NUM_ASSETS = 10
PHASE = "ph1"
PHASE_DURATION = 52  # weeks
SUCCESS_PROB = 0.5


def asset_process(env, asset_id, results):
    # Asset is initialized at a random time (0-52 weeks)
    start_time = random.uniform(0, PHASE_DURATION)
    yield env.timeout(start_time)
    print(f"Asset {asset_id} initialized at week {env.now:.1f}")
    print(f"Asset {asset_id} enters {PHASE} at week {env.now:.1f}")
    yield env.timeout(PHASE_DURATION)
    # Determine success
    success = random.random() < SUCCESS_PROB
    outcome = "SUCCESS" if success else "FAILURE"
    print(f"Asset {asset_id} completed {PHASE} at week {env.now:.1f} with {outcome}")
    results[asset_id] = {
        "start_time": start_time,
        "end_time": env.now,
        "outcome": outcome
    }


def run_simulation(num_assets):
    env = simpy.Environment()
    results = {}
    for asset_id in range(1, num_assets + 1):
        env.process(asset_process(env, asset_id, results))
    env.run()
    return results

if __name__ == "__main__":
    results = run_simulation(NUM_ASSETS)
    print("\nSimulation Results:")
    for asset_id, info in results.items():
        print(f"Asset {asset_id}: Started at week {info['start_time']:.1f}, Ended at week {info['end_time']:.1f}, Outcome: {info['outcome']}") 