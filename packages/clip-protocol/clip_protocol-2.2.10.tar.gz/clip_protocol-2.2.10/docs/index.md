# Homepage
<p align="center">
  <img src="assets/images/logo.png" alt="CLiP Protocol Logo" width="400">
</p>

## Welcome to CLiP Protocol
The **CLiP protocol** (context-aware Local Information Protection Protocol) is a novel solution for **frequency estimation** with personalized privacy budgets.

It empowers individual data owners — _such as students_ — to protect their personal data while still enabling meaningful learning analytics.

Unlike traditional Local Differential Privacy (LDP) approaches, which assign a uniform privacy budget to all users, the CLiP Protocol introduces a personalized privacy-by-design approach. This ensures that individual characteristics and privacy preferences are respected without sacrificing the utility of the collected data.

## ✨ Why CLiP Protocol?
In conventional LDP implementations, data collectors define a general privacy budget for all participants, regardless of personal sensitivity or data variability. This "_one-size-fits-all_" model is insufficient when users have diverse privacy needs.

**CLiP Protocol** solves this by:
- Allowing each individual to select their privacy level.
- Preserving critical data utility for learning analytics.
- Supporting privacy without relying on trusted servers.

## 🛠️ How It Works
The CLiP Protocol relies on **privacy sketching** and **LDP** techniques for sequential data events like:
- Student activity logs
- Click counts
- Interaction events

The process is divided into two main components:


| **Client Side** | | **Server Side** |
|:---------------:|:---:|:-------------:|
| Runs on the data owner's device | | Runs on the data collector’s server |
| Preprocesses and privatizes data | | Aggregates privatized data and handles queries |
| Applies the privacy mechanism locally | | Updates frequency sketches and responds to frequency queries |



The server is treated as **untrusted**: it only receives already privatized data.

## 👥 Main Actors
- **Data Owner**: An individual providing raw information (e.g., students, researchers).

- **Data Collector**: Institutions like universities managing the privatized data.

- **Data Consumer**: External researchers or parties requesting frequency-based insights.

## 🧩 Workflow Stages
The CLiP Protocol operates through four functional stages:

1. **Setup**: Configuration of privacy parameters prior to data collection.

2. **Mask**: Client-side anonymization of raw data based on personalized privacy budgets.

3. **Aggregation**: Server-side update of frequency sketches with privatized input.

4. **Estimation**: Server-side frequency estimation and response to queries.

Only the **Mask** stage occurs on the client side, ensuring that raw data never leaves the owner’s device unprotected.

<p align="center">
  <img src="assets/images/overview.png" alt="CLiP Protocol Logo" width="500">
</p>

The figure above illustrates the complete CLiP Protocol workflow, showing how privacy and utility are balanced across client and server components.


