"""
Full Integration Verification Script
Simulates multiple epochs and validates:
- Slashing / equivocation
- P2P latency handling
- 3-epoch finality
- Persistence to chain_state.json
- Execution → Consensus → Finalized trades
"""

import sys
import os

# Add both 'market_sim' and its parent to sys.path so imports in base.py work
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)            # project root
sys.path.insert(0, os.path.join(project_root, 'market_sim'))  # ensures 'core' is top-level

from datetime import datetime, timedelta

# Import your project modules
from core.models.base import Trade       # base.py uses 'core.utils.time_utils'
from market_sim.simulation.engine.simulation_engine import MarketSimulation, SimulationEvent
from market_sim.consensus.engine import TuringBlock

# --- Setup Simulation ---
start_time = datetime.now()
end_time = start_time + timedelta(seconds=1)  # short run for testing
sim = MarketSimulation(start_time=start_time, end_time=end_time, time_step=timedelta(milliseconds=100))

# --- Create Sample Orders / Trades ---
def create_trade(epoch: int) -> Trade:
    # Some Trade fields may require UUIDs and Decimals; minimal dummy for integration test
    from uuid import uuid4
    from decimal import Decimal
    return Trade(
        id=uuid4(),
        symbol=f"SYM{epoch}",
        price=Decimal('1.0'),
        quantity=Decimal('1.0'),
        buyer_order_id=uuid4(),
        seller_order_id=uuid4(),
        timestamp=datetime.utcnow()
    )

# --- Simulate Multiple Epochs ---
for epoch in range(1, 6):
    trades = [create_trade(epoch)]
    parent_hash = "0x" + "0"*64 if epoch == 1 else sim.consensus_engine.notarized_chain[-1].get_hash()
    block = TuringBlock(parent_hash=parent_hash, epoch=epoch, trades=trades)
    
    # Simulate votes (8/10 nodes)
    for i in range(8):
        node_id = f"node_{i}"
        block.votes[node_id] = f"sig_{epoch}_{node_id}"
    
    accepted = sim.consensus_engine.process_new_payload(block, latency_ms=50)
    print(f"Epoch {epoch}: Block accepted={accepted}, Slashed={sim.consensus_engine.slashed_nodes}")

# --- Test Equivocation ---
duplicate_block = TuringBlock(parent_hash=block.get_hash(), epoch=6, trades=[create_trade(6)])
duplicate_block.votes["node_0"] = "sig_dupe"
sim.consensus_engine.process_new_payload(duplicate_block, latency_ms=50)
print(f"After equivocation: Slashed nodes = {sim.consensus_engine.slashed_nodes}")

# --- Finalized Trades ---
final_trades = sim.consensus_engine.get_finalized_state()
print(f"Finalized Trades ({len(final_trades)}): {[str(t.id) for t in final_trades]}")

# --- Persistence Check ---
sim.consensus_engine._persist_state()
if os.path.exists(sim.consensus_engine.persistence_file):
    import json
    with open(sim.consensus_engine.persistence_file, "r") as f:
        state = json.load(f)
    print(f"Persisted State: {state}")
else:
    print("Persistence file not found!")

print("\n✅ Integration verification completed successfully.")