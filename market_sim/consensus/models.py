"""
Data models for the Streamlet implementation.
Based on Chapter 7 of 'Foundations of Distributed Consensus and Blockchains'.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class MarketBlock(BaseModel):
    """
    A block in a Streamlet blockchain[cite: 697].
    """
    parent_hash: str = Field(..., description="Hash of the prefix chain [cite: 698]")
    epoch: int = Field(..., description="Epoch number of the block [cite: 700]")
    price_data: float = Field(..., description="The market price payload [cite: 702]")

    def to_json(self) -> str:
        """Serializes the block for consistent hashing."""
        return self.model_dump_json(sort_keys=True)

class Vote(BaseModel):
    """
    A digital signature cast by a node on a specific block[cite: 673, 713].
    """
    node_id: str
    block_hash: str
    signature: str