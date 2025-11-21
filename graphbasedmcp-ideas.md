# MCP Server Concepts: Office & Operations

This document outlines architectural concepts for three distinct Model Context Protocol (MCP) servers designed to visualize and manage internal organizational data. These servers utilize non-PII data to provide insights via LLM interactions.

## 1. The "Office Fuel Station" (Cafeteria & Pantry)
**Theme:** A bridge between physical food/beverage operations and AI, optimizing inventory and tracking sustainability.

### Data Sources
* **POS Logs:** Anonymized transaction times and item names.
* **IoT/Telemetry:** Coffee machine status, smart fridge sensors.
* **Manual Logs:** Daily waste weight logs.

### MCP Tools (Functions)
| Tool Name | Description | Use Case |
| :--- | :--- | :--- |
| `get_live_inventory(category: str)` | Checks current stock levels. | "Do we have any Greek yogurt left?" |
| `get_traffic_stats(time_range: str)` | Returns transactions per 15-min bucket. | "Is the cafeteria busy right now?" |
| `get_waste_metrics(date: str)` | Returns pre-consumer vs. post-consumer waste data. | "How much food did we waste yesterday?" |
| `get_machine_status(machine_id: str)` | Returns error codes and cleaning cycle status. | "Is the espresso machine working?" |

### Visualizations
* **"Caffeine Rush" Heatmap:**
    * *Type:* 2D Heatmap (Day of Week vs. Hour of Day).
    * *Insight:* visualizes peak coffee consumption times.
    * *Library:* Seaborn or Plotly Express.
* **"Waste Stream" Sankey Diagram:**
    * *Type:* Sankey Flow Diagram.
    * *Insight:* Tracks flow from Inventory → Kitchen Prep → Plate Waste.
    * *Library:* Plotly Graph Objects.
* **"Bean Gauge" Indicators:**
    * *Type:* Radial Gauge (Speedometer).
    * *Insight:* Real-time levels for beans, milk, and waste bins.

### Complexity Assessment
* **PoC (Static):** Use static CSVs for timestamps and inventory. **Effort: Low.**
* **MVP (Integrated):** Requires connecting to InvenTree API or Grocy API. **Effort: Medium.**

---

## 2. The "Repo Radiologist" (Codebase Health)
**Theme:** A health monitor for the codebase to identify bottlenecks, risk, and velocity without manual PR inspection.

### Data Sources
* **Git History:** Commit logs, timestamps, author hashes.
* **CI/CD Logs:** Build durations, failure rates.

### MCP Tools (Functions)
| Tool Name | Description | Use Case |
| :--- | :--- | :--- |
| `get_hotspot_files(limit: int)` | Identifies files with highest churn/edit rate. | "Where is the most technical debt accumulating?" |
| `analyze_bus_factor()` | Finds modules edited by only 1 person >80% of the time. | "What is our risk if Dev X leaves?" |
| `get_pr_velocity(sprint_id: str)` | Calculates average time-to-merge and stale PRs. | "Are reviews slowing us down?" |

### Visualizations
* **"The Punchcard" Heatmap:**
    * *Type:* Scatter/Heatmap (Commits by Hour vs. Day).
    * *Insight:* Identifies overwork (late night commits) or risky deploy times.
* **"Spaghetti Detector" Network Graph:**
    * *Type:* Node-link diagram.
    * *Insight:* Visualizes file dependencies to find "God classes."
    * *Library:* NetworkX + PyVis.

### Complexity Assessment
* **PoC (Static):** Parse a local `git log` export or static JSON. **Effort: Low.**
* **MVP (Integrated):** GitHub API / GitLab API integration. Requires handling rate limits and pagination. **Effort: High.**

---

## 3. The "Space Optimiser" (Meeting Rooms)
**Theme:** An air-traffic controller for office resources to reduce "ghost meetings" and optimize usage.

### Data Sources
* **Calendar APIs:** Google Calendar / Outlook 365.
* **Room Sensors:** Occupancy sensors (if available).

### MCP Tools (Functions)
| Tool Name | Description | Use Case |
| :--- | :--- | :--- |
| `find_smart_slot(duration, attendees)` | Finds a room that fits the *exact* group size. | "Find a room for 4 people at 2 PM." |
| `get_ghost_meetings(threshold: int)` | Identifies bookings where no one checked in. | "Show me wasted room hours this week." |
| `optimize_schedule(room_id: str)` | Suggests defragging meetings to create large free blocks. | "How can we free up the Boardroom for an hour?" |

### Visualizations
* **"Room Utilization" Gantt Chart:**
    * *Type:* Horizontal Timeline.
    * *Insight:* Visualizes fragmentation (useless 15-min gaps) across all rooms.
* **"The Squatters" Bar Chart:**
    * *Type:* Bar Chart (Ranked).
    * *Insight:* Compares Booked Hours vs. Actual Usage by department.

### Complexity Assessment
* **PoC (Static):** A `schedule.json` file with nested room/event data. **Effort: Low.**
* **MVP (Integrated):** Google/Microsoft Graph API. Complex due to timezone handling and recurrence rules. **Effort: High.**

---

## Recommended Open Source Resources

### Inventory & Food
* **[InvenTree](https://github.com/inventree/InvenTree):** Open-source inventory management (Python/Django).
* **[Grocy](https://github.com/grocy/grocy):** ERP for fridges and pantries.
* **[SpeziSpezl](https://github.com/TUMFTM/SpeziSpezl):** DIY vending machine telemetry.

### Visualization Libraries (Python)
* **[Plotly Express](https://plotly.com/python/plotly-express/):** Best for interactive web-based charts (Sankeys, Heatmaps).
* **[Seaborn](https://seaborn.pydata.org/):** Excellent for statistical heatmaps.
* **[NetworkX](https://networkx.org/):** Essential for code dependency graphs.
