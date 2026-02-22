"""
Visualization script for Streamlet Finalization.
Plots the growth of notarized blocks vs finalized blocks.
"""
import matplotlib.pyplot as plt
# Ensure absolute imports for consistency with pytest setup
from market_sim.consensus.engine import StreamletEngine
from market_sim.consensus.models import MarketBlock

def visualize_streamlet():
    # Initialize with 10 nodes (Quorum = 7)
    engine = StreamletEngine(total_nodes=10)
    
    # 1. Simulate a notarized chain with gaps and consecutive runs
    # Consecutive epochs trigger finalization (e.g., 3, 4, 5)
    epochs = [0, 1, 3, 4, 5, 7, 8, 9]
    prices = [50000 + (i * 10) for i in range(len(epochs))]
    
    notarized_chain = []
    parent_hash = "0"
    
    for epoch, price in zip(epochs, prices):
        block = MarketBlock(parent_hash=parent_hash, epoch=epoch, price_data=price)
        notarized_chain.append(block)
        parent_hash = engine.compute_hash(block)

    # 2. Track finalized block count at each step of the simulation
    finalized_counts = []
    for i in range(1, len(notarized_chain) + 1):
        current_finalized = engine.get_finalized_chain(notarized_chain[:i])
        finalized_counts.append(len(current_finalized))

    # 3. Create the plot
    plt.figure(figsize=(10, 6))
    
    # Notarized blocks grow with every epoch update
    plt.step(epochs, [i+1 for i in range(len(epochs))], where='post', 
             label='Notarized Blocks (2n/3 votes)', color='blue', linestyle='--')
    
    # Finalized blocks only jump when the 3-consecutive-epoch rule is met
    plt.step(epochs, finalized_counts, where='post', 
             label='Finalized Blocks (3 Consecutive Epochs)', color='green', linewidth=2)
    
    plt.title("Streamlet Consensus Progress")
    plt.xlabel("Epoch Number")
    plt.ylabel("Cumulative Block Count")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = "consensus_plot.png"
    print(f"Generating {output_file}...")
    plt.savefig(output_file)
    plt.show()

if __name__ == "__main__":
    visualize_streamlet()