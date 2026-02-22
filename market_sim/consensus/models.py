import json
from pydantic import BaseModel, Field
from typing import List, Optional

class MarketBlock(BaseModel):
    """
    A block in a Streamlet blockchain.
    """
    parent_hash: str = Field(..., description="Hash of the prefix chain")
    epoch: int = Field(..., description="Epoch number of the block")
    price_data: float = Field(..., description="The market price payload")

    def to_json(self) -> str:
        """Serializes the block with sorted keys for consistent hashing."""
        # We dump to a dict first, then use standard json.dumps for sort_keys support
        return json.dumps(self.model_dump(), sort_keys=True)

class Vote(BaseModel):
    """
    A digital signature cast by a node on a block.
    """
    node_id: str
    block_hash: str
    signature: str