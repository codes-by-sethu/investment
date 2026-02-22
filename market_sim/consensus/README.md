\# Streamlet Consensus (Ch. 7 - Foundations of Distributed Consensus)



\## Implemented Features

✅ \*\*Streamlet Protocol\*\* (Elaine Shi book Ch. 7)\[file:1]

\- Epoch-based leader rotation via hash-oracle

\- `MarketBlock` with price\_data integration  

\- 2n/3 voting thresholds (`Vote` model)

\- Notarization → Finalization (3 consecutive epochs)

\- Fault tolerant: <n/3 Byzantine nodes



\## Tests ✅

```bash

pytest test\_consensus.py -v



