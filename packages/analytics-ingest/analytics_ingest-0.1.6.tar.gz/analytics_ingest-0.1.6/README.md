# Analytics Ingest Client

A lightweight Python library to batch and push signals, DTCs, GPS data, and network stats to a GraphQL backend, with optional JWT or certificate-based auth.

---

## 🔧 Features

- Supports Python 3.11+
- Clean, single-class interface: `AnalyticsIngestClient`
- In-memory caching for resolved IDs (message id or configuration)
- Batching support (by interval, count, or signal limit)
- Async-safe request queuing (only 1 request at a time)
- JWT (`SEC_AUTH_TOKEN`) or cert-based authentication
- Minimal dependency footprint
- Easy to test and integrate

---

## 🚀 Installation

```bash
pip3 install analytics-ingest

or

pip install analytics-ingest

```

## Run Test Cases

```
PYTHONPATH=src python3 -m unittest tests.test_add_signal
```
