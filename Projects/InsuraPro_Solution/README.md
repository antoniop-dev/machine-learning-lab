# InsuraPro Solution

InsuraPro is a C++ terminal CRM built for insurance workflow practice.  
It manages clients, agents, and sales interactions (appointments and contracts) with CSV-based persistence.

## Features

- Client lifecycle: add, list, edit, delete, and search clients.
- Interaction tracking:
  - Appointments (topic, datetime, location, completion status)
  - Contracts (policy number, product, premium, start/end dates)
- Query tools to list interactions by client, by agent, or globally.
- Input normalization and validation for names, email, phone, dates, IDs, and addresses.
- Save/load support through `clients.csv` and `interactions.csv`.
- Built-in default agent dataset loaded at startup.

## Tech Stack

- C++17
- Standard Library containers/utilities
- CSV files for local persistence
- Doxygen for API documentation

## Project Structure

```text
InsuraPro_Solution/
├─ include/            # headers (domain models, manager, UI, utilities)
├─ src/                # implementations
├─ clients.csv         # client data (created/updated by the app)
├─ interactions.csv    # interaction data (created/updated by the app)
├─ main.cpp            # entry point
├─ Doxyfile            # Doxygen configuration
└─ README.md
```

## Build and Run

From `Projects/InsuraPro_Solution`:

```bash
g++ -std=c++17 -Wall -Wextra -Iinclude main.cpp src/*.cpp src/utilities/*.cpp -o insurapro
./insurapro
```

Recommended terminal width: `80` columns for cleaner menu/table rendering.

## Data Persistence

- On startup, the app loads default agents and then tries to load existing CSV data.
- If CSV files are missing, the app still runs and creates data files when you save.
- Save/load actions are also available directly from the main menu.

## Documentation

Generate docs with:

```bash
doxygen Doxyfile
```

Open `docs/html/index.html` to browse the generated reference.
