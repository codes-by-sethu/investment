from pydantic import BaseModel
from typing import List, Optional
import numpy as np

class PriceProposal(BaseModel):
    node_id: str
    asset: str
    price: float

class PriceOracle:
    """
    Implements a Distributed Consensus Oracle.
    Ensures market prices are agreed upon by a majority of nodes.
    """
    def __init__(self, total_nodes: int):
        self.total_nodes = total_nodes
        self.quorum = (total_nodes // 2) + 1

    def validate_price(self, proposals: List[PriceProposal]) -> Optional[float]:
        # Check for Quorum (Standard Distributed Systems requirement)
        if len(proposals) < self.quorum:
            print(f"Consensus Failed: Only {len(proposals)} nodes voted.")
            return None
        
        # Use Median to filter out 'Byzantine' (malicious/noisy) nodes
        prices = [p.price for p in proposals]
        consensus_price = np.median(prices)
        
        return float(consensus_price)

# Sample Input for testing
if __name__ == "__main__":
    test_proposals = [
        PriceProposal(node_id="node_1", asset="BTC", price=50000),
        PriceProposal(node_id="node_2", asset="BTC", price=50010),
        PriceProposal(node_id="node_3", asset="BTC", price=49990),
    ]
    
    oracle = PriceOracle(total_nodes=5)
    result = oracle.validate_price(test_proposals)
    print(f"Agreed Market Price: {result}")