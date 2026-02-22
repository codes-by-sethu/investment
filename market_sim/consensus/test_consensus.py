import pytest
# Absolute imports to ensure the modules are found from the root
from market_sim.consensus.models import MarketBlock, Vote
from market_sim.consensus.engine import StreamletEngine

def test_streamlet_notarization():
    """Validates the 2n/3 quorum requirement."""
    engine = StreamletEngine(total_nodes=10) # Quorum threshold is 7
    
    # 6/10 votes should fail notarization
    votes_fail = [Vote(node_id=f"n{i}", block_hash="h", signature="s") for i in range(6)]
    assert engine.is_notarized(votes_fail) is False
    
    # 7/10 votes should pass notarization
    votes_pass = [Vote(node_id=f"n{i}", block_hash="h", signature="s") for i in range(7)]
    assert engine.is_notarized(votes_pass) is True

def test_streamlet_finalization():
    """Tests finalization with 3 consecutive epochs."""
    engine = StreamletEngine(total_nodes=10)
    
    # Blocks with consecutive epochs: 10, 11, 12
    b1 = MarketBlock(parent_hash="0", epoch=10, price_data=100.0)
    b2 = MarketBlock(parent_hash="h1", epoch=11, price_data=110.0)
    b3 = MarketBlock(parent_hash="h2", epoch=12, price_data=120.0)
    
    chain = [b1, b2, b3]
    finalized = engine.get_finalized_chain(chain)
    
    # Finalizes up to the second block (epoch 11)
    assert len(finalized) == 2
    assert finalized[-1].epoch == 11