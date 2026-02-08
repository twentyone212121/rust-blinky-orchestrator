# Zephyr RTOS & Rust Integration Orchestrator

Embedded development demonstration featuring Zephyr RTOS implementations in both C and Rust, with automated Python orchestration for build and flash operations.

**Target Hardware:** NXP FRDM-MCXN947

## Project Overview

This project demonstrates:

- **C Implementation** - Standard Zephyr blinky (`c-blinky/`)
- **Rust Implementation** - Same functionality in Rust (`rust-blinky/`)
- **Python Orchestrator** - Automated build/flash tool with logging (`orchestrator/`)

## Setup Instructions

### 1. Zephyr Environment

Follow the [Zephyr Getting Started Guide](https://docs.zephyrproject.org/latest/develop/getting_started/index.html) to install:

- Zephyr RTOS workspace
- West meta-tool
- Zephyr SDK 0.17.4+

**Install LinkServer** (NXP board programmer):

- Download from [NXP LinkServer](https://www.nxp.com/linkserver)
- Add to PATH: `export PATH="/Applications/LinkServer_24.9.75:$PATH"`

### 2. Rust Toolchain

```bash
# Install Rust 1.85.0+
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add ARM Cortex-M33 target
rustup target add thumbv8m.main-none-eabi

# Enable Zephyr Rust module
cd ~/zephyrproject
west config manifest.project-filter +zephyr-lang-rust
west update
```

### 3. Activate Environment

```bash
cd ~/zephyrproject
source .venv/bin/activate
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                Python Orchestrator                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │  CLI (argparse)                                 │    │
│  │  - build/flash commands                         │    │
│  │  - target selection (c/rust/both)               │    │
│  └──────────────┬──────────────────────────────────┘    │
│                 │                                       │
│                 v                                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │  West Executor (subprocess)                     │    │
│  │  - Spawns: west build / west flash              │    │
│  │  - Captures: stdout/stderr                      │    │
│  │  - Handles: errors, timeouts                    │    │
│  └──────────────┬──────────────────────────────────┘    │
│                 │                                       │
│                 v                                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Log Manager                                    │    │
│  │  - JSONL append to logs/orchestrator.jsonl      │    │
│  │  - Session ID correlates related entries        │    │
│  │  - Success/failure tracking                     │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                         │
                         │ invokes
                         v
         ┌───────────────────────────────┐
         │   West Build System           │
         │   (Zephyr + CMake + Ninja)    │
         └───────────────────────────────┘
                         │
                         v
         ┌───────────────────────────────┐
         │   LinkServer Programmer       │
         │   (Flashes FRDM-MCXN947)      │
         └───────────────────────────────┘
                         │
                         v
                   [Hardware LED Blinks]
```

## Execution Guide

### Manual Build & Flash

**C Version:**

```bash
cd c-blinky
west build -b frdm_mcxn947/mcxn947/cpu0
west flash
```

**Rust Version:**

```bash
cd rust-blinky
west build -b frdm_mcxn947/mcxn947/cpu0
west flash
```

See `c-blinky/README.md` and `rust-blinky/README.md` for implementation details.

### Automated Orchestration

```bash
cd orchestrator

# Build a project
uv run orch build ../c-blinky
uv run orch build ../rust-blinky --pristine

# Flash a project
uv run orch flash ../c-blinky

# Build + flash in one step
uv run orch run ../c-blinky

# Verbose output (stream west output in real-time)
uv run orch build ../c-blinky -v
```

**Output Logs:** All operations are appended to `logs/orchestrator.jsonl`. Each line is a compact JSON object with a `session_id` to correlate entries from the same invocation.

```jsonl
{"type": "operation", "session_id": "20260207_203757", "project": "c-blinky", "operation": "build", "board": "frdm_mcxn947/mcxn947/cpu0", "success": true, ...}
{"type": "summary", "session_id": "20260207_203757", "total_duration_seconds": 14.7, "all_succeeded": true, ...}
```

## Sample Logs

Example log files demonstrating successful operations are provided in `examples/sample-logs/`.

## Project Structure

```
rust-blinky-orchestrator/
├── c-blinky/           # C implementation
├── rust-blinky/        # Rust implementation
├── orchestrator/       # Python automation tool
├── docs/               # Additional documentation
│   ├── task.md         # Original requirements
│   └── progress.md     # Implementation tracker
└── examples/           # Sample logs
```

## Troubleshooting

**Build Failures:**

- Verify Zephyr SDK installed: `west --version`
- Activate environment: `source ~/zephyrproject/.venv/bin/activate`
- For Rust: Ensure module enabled and target installed

**Flash Failures:**

- Check board connection: `LinkServer probes`
- Use data-capable USB cable
- Connect to MCU-LINK/Debug port

## Status

- ✅ C Implementation - Complete
- ✅ Rust Implementation - Complete (hardware testing done)
- ✅ Python Orchestrator - Complete (JSONL logging)
- ⬜ Sample Logs - Pending

See `docs/progress.md` for detailed task completion status.

## Author

Denys Kyslytsyn
