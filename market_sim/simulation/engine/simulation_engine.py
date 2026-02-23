"""
Market Simulation Engine (Execution Layer)
Integrated with Turing Test Blockchain (Consensus Layer).
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import heapq
import logging

from core.models.base import Order, Trade, Asset
from market.exchange.matching_engine import MatchingEngine
from market.agents.base_agent import BaseAgent
from market_sim.consensus.engine import StreamletEngine, TuringBlock

class SimulationEvent:
    def __init__(self, timestamp: datetime, event_type: str, data: Any):
        self.timestamp = timestamp
        self.event_type = event_type
        self.data = data

    def __lt__(self, other):
        return self.timestamp < other.timestamp

class MarketSimulation:
    def __init__(self, start_time: datetime, end_time: datetime, time_step: timedelta = timedelta(milliseconds=100)):
        self.start_time = start_time
        self.end_time = end_time
        self.time_step = time_step
        self.current_time = start_time

        # Components
        self.exchanges: Dict[str, MatchingEngine] = {}
        self.agents: Dict[str, BaseAgent] = {}
        self.assets: Dict[str, Asset] = {}

        # Consensus Integration (Prysm Layer)
        validators = [f"node_{i}" for i in range(10)]
        self.consensus_engine = StreamletEngine(initial_nodes=validators)
        self.epoch_counter = 0

        # Event queue & Results
        self.event_queue = []
        self.trades: List[Trade] = []
        self.metrics: Dict[str, List[Dict]] = {
            'order_book_snapshots': [],
            'agent_metrics': [],
            'market_metrics': []
        }

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def process_order(self, order: Order) -> List[Trade]:
        """Geth-style execution gated by Consensus finality."""
        if order.symbol not in self.exchanges:
            return []

        exchange = self.exchanges[order.symbol]
        new_trades = exchange.process_order(order)

        if new_trades:
            # Propose Execution Payload to Consensus
            new_block = TuringBlock(
                parent_hash="0x" + "0"*64, 
                epoch=self.epoch_counter, 
                trades=new_trades
            )
            self.epoch_counter += 1
            
            # Simulate voting (8/10 nodes)
            for i in range(8): 
                new_block.votes[f"node_{i}"] = f"sig_{new_block.get_hash()}"

            # Submit to Consensus with simulated latency
            self.consensus_engine.process_new_payload(new_block, latency_ms=50)

        # Commit only finalized trades to state
        finalized_trades = self.consensus_engine.get_finalized_state()
        for f_trade in finalized_trades:
            if f_trade not in self.trades:
                self.trades.append(f_trade)
                self._notify_agents_of_trade(f_trade)

        return new_trades

    # ... [Rest of the methods: add_exchange, add_agent, run, etc. remain the same] ...

    def _notify_agents_of_trade(self, trade: Trade) -> None:
        for agent in self.agents.values():
            agent.on_trade(trade)

    def run(self) -> Dict[str, Any]:
        self.logger.info(f"Starting simulation...")
        while self.current_time <= self.end_time:
            while self.event_queue and self.event_queue[0].timestamp <= self.current_time:
                event = heapq.heappop(self.event_queue)
                if event.event_type == 'order':
                    self.process_order(event.data)
            
            for agent in self.agents.values():
                agent.on_time_update(self.current_time)
            
            self.current_time += self.time_step
        return {}