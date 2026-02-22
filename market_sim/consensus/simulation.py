"""
Simulation script for Streamlet Consensus.
Generates sample input and validates finalization.
"""
from models import MarketBlock, Vote
from engine import StreamletEngine

def run_simulation():
    # 1. Setup a network with 10 nodes (Quorum = 7)[cite: 674].
    engine = StreamletEngine(total_nodes=10)
    
    # 2. Simulate a chain of blocks with consecutive epochs: 1, 2, 3[cite: 735].
    # Genesis block is traditionally epoch 0[cite: 704].
    genesis = MarketBlock(parent_hash="0", epoch=0, price_data=0.0)
    g_hash = engine.compute_hash(genesis)

    # Block 1 (Epoch 1)
    b1 = MarketBlock(parent_hash=g_hash, epoch=1, price_data=50100.5)
    b1_hash = engine.compute_hash(b1)

    # Block 2 (Epoch 2)
    b2 = MarketBlock(parent_hash=b1_hash, epoch=2, price_data=50150.2)
    b2_hash = engine.compute_hash(b2)

    # Block 3 (Epoch 3)
    b3 = MarketBlock(parent_hash=b2_hash, epoch=3, price_data=50200.0)

    # 3. Assemble a notarized chain[cite: 715].
    notarized_chain = [genesis, b1, b2, b3]

    # 4. Check for finalization[cite: 729].
    finalized = engine.get_finalized_chain(notarized_chain)

    print(f"Total Blocks in Notarized Chain: {len(notarized_chain)}")
    print(f"Total Blocks Finalized: {len(finalized)}")
    
    if finalized:
        # The second block in the triple (Epoch 2) should be the latest finalized block[cite: 679, 735].
        latest = finalized[-1]
        print(f"Latest Finalized Price: {latest.price_data} at Epoch {latest.epoch}")

if __name__ == "__main__":
    run_simulation()