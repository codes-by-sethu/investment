import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'core')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'simulation')))


# Market → Consensus Integration Demo (Ch.7 Streamlet)
from consensus.engine import StreamletEngine
from consensus.models import MarketBlock

def demo_market_consensus():
    """Demo: market_sim trades → Streamlet consensus"""
    print("🚀=== MARKET → STREAMLET CONSENSUS DEMO ===")
    
    engine = StreamletEngine(total_nodes=10)
    trades = []
    
    for tick in range(20):
        # Simulate volatile market prices
        price = 50000 + (tick * 80) + (tick % 7 * 300)
        trade = {"tick": tick, "price": price, "symbol": "BTC-USD"}
        trades.append(trade)
        print(f"Tick {tick}: ${price:,.0f}")
        
        # Every 5 trades = 1 epoch → consensus block
        if len(trades) == 5:
            consensus_price = sum(t["price"] for t in trades) / 5
            block = MarketBlock(
                parent_hash=getattr(engine, 'last_notarized', 'genesis'),
                epoch=len(engine.notarized_blocks) + 1,
                price_data=consensus_price
            )
            print(f"📦 EPOCH {block.epoch}: Consensus price ${consensus_price:,.0f}")
            engine.propose_block(block)  # Your Streamlet logic
            trades = []
    
    print("✅ Market → Consensus integration COMPLETE")
    print(f"Final chain length: {len(engine.notarized_blocks)} blocks")

if __name__ == "__main__":
    demo_market_consensus()
