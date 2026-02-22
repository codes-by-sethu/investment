"""
Core Streamlet Engine for notarization and finalization logic.
Implements the 2n/3 quorum and consecutive epoch rules[cite: 674, 679].
"""
import hashlib
from typing import List, Optional, Set
from .models import MarketBlock, Vote

class StreamletEngine:
    def __init__(self, total_nodes: int):
        """
        Initialize the engine with the total number of nodes in the network.
        The quorum requirement is strictly 2n/3[cite: 674].
        """
        self.total_nodes = total_nodes
        # Quorum is defined as at least 2n/3 distinct signatures[cite: 674, 714].
        self.quorum_threshold = (2 * total_nodes // 3) + 1

    @staticmethod
    def compute_hash(block: MarketBlock) -> str:
        """
        Computes the SHA-256 hash of a block to uniquely identify it[cite: 106, 708].
        """
        return hashlib.sha256(block.to_json().encode()).hexdigest()

    def is_notarized(self, votes: List[Vote]) -> bool:
        """
        A block is notarized if it gains votes from at least 2n/3 distinct nodes[cite: 674].
        """
        unique_voters: Set[str] = {v.node_id for v in votes}
        return len(unique_voters) >= self.quorum_threshold

    def get_finalized_chain(self, notarized_chain: List[MarketBlock]) -> List[MarketBlock]:
        """
        Finalization Rule: If three adjacent blocks have consecutive epoch numbers,
        the prefix up to the second of the triple is considered final[cite: 679, 729].
        """
        if len(notarized_chain) < 3:
            return []

        final_index = -1
        # Iterate through the chain to find three consecutive epochs (e, e+1, e+2)[cite: 679, 735].
        for i in range(len(notarized_chain) - 2):
            b0 = notarized_chain[i]
            b1 = notarized_chain[i+1]
            b2 = notarized_chain[i+2]

            if b1.epoch == b0.epoch + 1 and b2.epoch == b1.epoch + 1:
                # The second block in the triple and its prefix are final[cite: 679, 729].
                final_index = i + 1

        if final_index != -1:
            return notarized_chain[:final_index + 1]
        return []