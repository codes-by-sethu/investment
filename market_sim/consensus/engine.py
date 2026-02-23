"""
Turing Test Blockchain: Consensus Client (Prysm-style)
Implements Streamlet 3-epoch Finality, Slashing, and Persistence.
"""
import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import List, Set, Dict
from market_sim.core.models.base import Trade

@dataclass
class TuringBlock:
    """The Execution Payload wrapper for Consensus."""
    parent_hash: str
    epoch: int
    trades: List[Trade]
    # Mapping of node_id to their cryptographic signature
    votes: Dict[str, str] = field(default_factory=dict) 

    def get_hash(self) -> str:
        """Generates a unique SHA-256 hash for the block content."""
        content = f"{self.parent_hash}{self.epoch}{[str(t.id) for t in self.trades]}"
        return hashlib.sha256(content.encode()).hexdigest()

class StreamletEngine:
    def __init__(self, initial_nodes: List[str]):
        self.validators = set(initial_nodes)
        self.slashed_nodes: Set[str] = set()
        self.votes_log: Dict[int, Dict[str, str]] = {} # epoch -> node_id -> block_hash
        self.notarized_chain: List[TuringBlock] = []
        self.persistence_file = "chain_state.json"

    def process_new_payload(self, block: TuringBlock, latency_ms: int = 0) -> bool:
        """Processes block. Handles P2P Latency, Slashing, and Notarization."""
        # 1. P2P Latency Simulation (Reject if > 200ms)
        if latency_ms > 200:
            return False 

        valid_votes = 0
        block_hash = block.get_hash()

        for node_id, sig in block.votes.items():
            if node_id in self.slashed_nodes or node_id not in self.validators:
                continue
            
            # 2. Slashing Check (Detect Equivocation)
            if self._is_equivocating(node_id, block.epoch, block_hash):
                continue
            
            valid_votes += 1

        # 3. Dynamic Quorum (2n/3 + 1 of active nodes)
        active_nodes = self.validators - self.slashed_nodes
        quorum = (2 * len(active_nodes) // 3) + 1
        
        if valid_votes >= quorum:
            self.notarized_chain.append(block)
            self._persist_state()
            return True
        return False

    def _is_equivocating(self, node_id: str, epoch: int, block_hash: str) -> bool:
        """Detects if a validator voted for multiple blocks in the same epoch."""
        epoch_log = self.votes_log.setdefault(epoch, {})
        if node_id in epoch_log and epoch_log[node_id] != block_hash:
            self.slashed_nodes.add(node_id)
            return True
        epoch_log[node_id] = block_hash
        return False

    def _persist_state(self):
        """Saves current chain health to disk."""
        state = {
            "height": len(self.notarized_chain),
            "slashed_count": len(self.slashed_nodes),
            "active_validators": list(self.validators - self.slashed_nodes)
        }
        with open(self.persistence_file, "w") as f:
            json.dump(state, f)

    def get_finalized_state(self) -> List[Trade]:
        """Applies Streamlet 3-epoch finality: b, b+1, b+2."""
        if len(self.notarized_chain) < 3:
            return []
        
        final_trades = []
        for i in range(len(self.notarized_chain) - 2):
            b0, b1, b2 = self.notarized_chain[i:i+3]
            # Check for strictly consecutive epochs
            if b1.epoch == b0.epoch + 1 and b2.epoch == b1.epoch + 1:
                # All blocks up to b0 are now finalized
                for b in self.notarized_chain[:i+1]:
                    final_trades.extend(b.trades)
                # Cleanup: remove finalized prefix from chain
                self.notarized_chain = self.notarized_chain[i+1:]
                break
        return final_trades