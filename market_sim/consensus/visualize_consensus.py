"""
Visualization script for Streamlet Finalization.
Plots the growth of notarized blocks vs finalized blocks.
"""
import matplotlib.pyplot as plt
from engine import StreamletEngine
from models import MarketBlock

def visualize_streamlet():
    engine = StreamletEngine(total_nodes=10)
    
    # 1. Simulate a notarized chain with gaps and consecutive runs
    # Epochs: 0 (Genesis), 1, 3, 4, 5 (Run), 7, 8, 9 (Run)
    epochs = [0, 1, 3, 4, 5, 7, 8, 9]
    prices = [50000 + (i * 10) for i in range(len(epochs))]
    
    notarized_chain = []
    parent_hash = "0"
    
    for epoch, price in zip(epochs, prices):
        block = MarketBlock(parent_hash=parent_hash, epoch=epoch, price_data=price)
        notarized_chain.append(block)
        parent_hash = engine.compute_hash(block)

    # 2. Get finalized segments at each step of growth
    finalized_counts = []
    for i in range(1, len(notarized_chain) + 1):
        current_finalized = engine.get_finalized_chain(notarized_chain[:i])
        finalized_counts.append(len(current_finalized))

    # 3. Plotting
    plt.figure(figsize=(10, 6))
    plt.step(epochs, [i+1 for i in range(len(epochs))], where='post', label='Notarized Blocks', color='blue', linestyle='--')
    plt.step(epochs, finalized_counts, where='post', label='Finalized Blocks', color='green', linewidth=2)
    
    plt.title("Streamlet Consensus: Notarization vs. Finalization")
    plt.xlabel("Epochs")
    plt.ylabel("Block Count")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    print("Generating consensus_plot.png...")
    plt.savefig("consensus_plot.png")
    plt.show()

if __name__ == "__main__":
    visualize_streamlet()