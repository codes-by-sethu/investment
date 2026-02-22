import matplotlib.pyplot as plt
import numpy as np
from oracle import PriceOracle, PriceProposal

def run_simulation():
    true_price = 50000
    nodes = 10
    oracle = PriceOracle(total_nodes=nodes)
    
    # Simulate 100 time steps
    history = []
    
    for _ in range(100):
        proposals = []
        for i in range(nodes):
            # Add some random noise to each node
            noise = np.random.normal(0, 50) 
            # Simulate one 'Malicious' node that sends huge errors
            if i == 0: noise = 5000 
            
            proposals.append(PriceProposal(
                node_id=f"node_{i}", 
                asset="BTC", 
                price=true_price + noise
            ))
        
        consensus = oracle.validate_price(proposals)
        history.append(consensus)

    plt.figure(figsize=(10, 5))
    plt.plot(history, label='Consensus Price', color='green', linewidth=2)
    plt.axhline(y=true_price, color='r', linestyle='--', label='True Market Price')
    plt.title("Distributed Consensus Stability (Handling 10% Byzantine Nodes)")
    plt.xlabel("Time Steps")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    run_simulation()