"""
Middleware implementing the Engine API (Geth-Prysm Bridge).
"""
class EngineAPI:
    def __init__(self, consensus_engine):
        self.consensus = consensus_engine

    def forkchoice_updated(self, head_block_hash: str):
        """Signals Geth to update its head based on Consensus."""
        return {"status": "SUCCESS", "payloadId": head_block_hash}

    def new_payload(self, block):
        """Passes Execution payload to Consensus."""
        return self.consensus.process_new_payload(block)