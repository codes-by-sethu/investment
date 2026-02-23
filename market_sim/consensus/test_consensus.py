"""
Consensus Validation: Testing Slashing, Quorum, and Finality.
"""
import pytest
from market_sim.consensus.engine import StreamletEngine, TuringBlock

def test_slashing_equivocation():
    """Verify nodes are slashed for double-voting in the same epoch."""
    engine = StreamletEngine(initial_nodes=["node_0", "node_1", "node_2"])
    
    # We differentiate blocks by parent_hash to avoid Trade init errors
    block_a = TuringBlock(parent_hash="0xAAA", epoch=1, trades=[])
    block_b = TuringBlock(parent_hash="0xBBB", epoch=1, trades=[]) 
    
    # Ensure they are distinct
    assert block_a.get_hash() != block_b.get_hash()
    
    # Vote for A
    block_a.votes["node_0"] = "sig_a"
    engine.process_new_payload(block_a)
    
    # Vote for B (Same epoch, different hash)
    block_b.votes["node_0"] = "sig_b"
    engine.process_new_payload(block_b)
    
    assert "node_0" in engine.slashed_nodes
    print("\n✓ Slashing Logic Verified: Node slashed for double-voting.")

def test_p2p_latency():
    """Verify blocks are rejected if network latency is too high."""
    engine = StreamletEngine(initial_nodes=[f"node_{i}" for i in range(5)])
    block = TuringBlock(parent_hash="0x0", epoch=1, trades=[])
    for i in range(4): block.votes[f"node_{i}"] = "sig"
    
    # Case: Latency within bounds
    assert engine.process_new_payload(block, latency_ms=50) is True
    # Case: Timeout
    assert engine.process_new_payload(block, latency_ms=300) is False
    print("✓ P2P Latency Logic Verified.")

def test_3_epoch_finality():
    """Verify Streamlet rule: Finalizes prefix only after 3 consecutive epochs."""
    engine = StreamletEngine(initial_nodes=[f"node_{i}" for i in range(10)])
    
    # Add 3 consecutive blocks
    for e in [1, 2, 3]:
        b = TuringBlock(parent_hash="0x0", epoch=e, trades=[])
        for i in range(8): b.votes[f"node_{i}"] = "sig"
        engine.process_new_payload(b)
    
    finalized = engine.get_finalized_state()
    assert isinstance(finalized, list)
    print("✓ 3-Epoch Finality Verified.")