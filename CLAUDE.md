# CLAUDE.md - Project Context Guide

> This file provides context for AI agents (Claude Code or other assistants) working on this project.

---

## Project Overview

**Name**: Zephyr RTOS & Rust Integration Orchestrator
**Goal**: Demonstrate embedded development proficiency with Zephyr RTOS using both C and Rust, featuring automated build/flash orchestration through Python

**Current Status**: All phases complete ✅

---

## Hardware & Environment

- **Board**: NXP FRDM-MCXN947 (board identifier: `frdm_mcxn947/mcxn947/cpu0`)
- **MCU**: MCXN947 with ARM Cortex-M33 (ARMv8-M architecture with hardware float)
- **Debugger**: LinkServer (on-board MCU-LINK)
- **Zephyr Version**: 4.3.99
- **Workspace**: `/Users/deniskyslytsyn/zephyrproject/`
- **Project Root**: `/Users/deniskyslytsyn/zephyrproject/rust-blinky-orchestrator/`
- **Python venv**: `/Users/deniskyslytsyn/zephyrproject/.venv/`

---

## Project Structure

```
rust-blinky-orchestrator/
├── c-blinky/              # ✅ C implementation
│   ├── src/main.c         # GPIO blinky (2000ms toggle)
│   ├── CMakeLists.txt
│   └── prj.conf
├── rust-blinky/           # ✅ Rust implementation
│   ├── src/lib.rs         # GPIO blinky (200ms toggle)
│   ├── Cargo.toml         # name = "rustapp", staticlib
│   ├── CMakeLists.txt     # rust_cargo_application() + DT_AUGMENTS override
│   ├── dt-rust.yaml       # Custom devicetree mapping (flash partition workaround)
│   ├── build.rs           # Devicetree code generation
│   └── prj.conf
├── orchestrator/          # ✅ Python build/flash tool (uv project)
│   ├── pyproject.toml     # entry point: "orch"
│   └── src/orchestrator/
│       ├── cli.py         # argparse CLI: build/flash/run subcommands
│       ├── core.py        # ExecutionResult dataclass + WestExecutor
│       └── logger.py      # JSONL append logger (logs/orchestrator.jsonl)
├── docs/
│   ├── task.md           # Original requirements
│   └── progress.md       # Checklist tracker
├── logs/                 # Generated during orchestrator runs
└── examples/sample-logs/ # Reference logs
```

---

## What's Already Done

### C Blinky (`c-blinky/`)
- Standard Zephyr GPIO blinky using devicetree API
- LED via `led0` alias, 2000ms toggle, prints "LED state: ON/OFF"
- Builds and flashes successfully

### Rust Blinky (`rust-blinky/`)
- `#![no_std]` bare-metal, uses `zephyr` crate for GPIO
- 200ms toggle (faster for visual feedback)
- Required workaround for devicetree flash partition code generation bug (see Lessons Learned below)
- Builds successfully, hardware-tested

### Python Orchestrator (`orchestrator/`)
- **uv project** — run with `uv run orch <command>`
- Three subcommands: `build`, `flash`, `run` (build+flash)
- **JSONL logging** — appends to single `logs/orchestrator.jsonl` file
- Each JSON line has a `type` field (`"operation"` or `"summary"`) and a `session_id`
- `ExecutionResult` dataclass carries: project_name, operation, success, return_code, duration_seconds, stdout, stderr, command, board

#### Orchestrator CLI Usage

```bash
cd orchestrator
uv run orch build ../c-blinky                     # build c-blinky
uv run orch build ../rust-blinky --pristine        # clean build rust-blinky
uv run orch flash ../c-blinky                      # flash
uv run orch run ../c-blinky -b frdm_mcxn947/mcxn947/cpu0  # build + flash
uv run orch build ../c-blinky -v                   # verbose (stream output)
```

#### JSONL Log Format

Each run appends lines to `logs/orchestrator.jsonl`:

```jsonl
{"type": "operation", "session_id": "20260207_203757", "timestamp": "...", "project": "c-blinky", "operation": "build", "board": "frdm_mcxn947/mcxn947/cpu0", "command": ["west", "build", "-b", "frdm_mcxn947/mcxn947/cpu0"], "success": true, "return_code": 0, "duration_seconds": 14.7, "stdout": "...", "stderr": "..."}
{"type": "summary", "session_id": "20260207_203757", "timestamp": "...", "total_duration_seconds": 14.8, "operations": [{"project": "c-blinky", "operation": "build", "success": true, "duration_seconds": 14.7}], "all_succeeded": true}
```

---

## Key Technical Details

### Build System Integration

**C Projects**: Standard Zephyr CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(blinky)
target_sources(app PRIVATE src/main.c)
```

**Rust Projects**: Use Rust-specific CMake macro

```cmake
cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(rust_blinky)
rust_cargo_application()
```

### Critical Rust Constraints

- Package name MUST be `"rustapp"` in Cargo.toml
- Crate type MUST be `["staticlib"]`
- Use `#![no_std]` for bare-metal
- Entry point: `#[no_mangle] pub extern "C" fn main()`
- Use `src/lib.rs` NOT `src/main.rs`
- Rust target: `thumbv8m.main-none-eabi` (software float, **not** `eabihf`)

### Device Tree Overlay Naming

**Convention**: Board identifier with underscores, not slashes
- Correct: `frdm_mcxn947_mcxn947_cpu0.overlay`
- Place in: `{project}/boards/{overlay_name}.overlay`

### West Command Execution

Always activate venv first:

```bash
source /Users/deniskyslytsyn/zephyrproject/.venv/bin/activate
cd rust-blinky-orchestrator/{project}
west build -b frdm_mcxn947/mcxn947/cpu0
west flash
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Rust Target Mismatch

**Issue**: Build fails with "error: couldn't find crate for target"
**Solution**: `rustup target add thumbv8m.main-none-eabi` (software float, not `eabihf`)

### Pitfall 2: Wrong Cargo Package Name

**Issue**: CMake error: "Could not find rustapp staticlib"
**Solution**: Ensure `name = "rustapp"` and `crate-type = ["staticlib"]` in Cargo.toml

### Pitfall 3: Missing Rust Module

**Issue**: CMake error: "Unknown CMake command: rust_cargo_application"
**Solution**: `west config manifest.project-filter +zephyr-lang-rust && west update`

### Pitfall 4: Devicetree API Names

**Issue**: Sample code uses `GPIO_OUTPUT_ACTIVE`
**Solution**: Use `ZR_GPIO_OUTPUT_ACTIVE` (new API naming convention)

### Pitfall 5: Zephyr Rust Crates Not on crates.io

**Solution**: Create `.cargo/config.toml` with path patches (relative to `../../modules/lang/rust/zephyr`). Don't commit — it's setup-dependent. Add `.cargo/` to `.gitignore`.

### Pitfall 6: rust-analyzer Doesn't Work

**Reason**: Build scripts need CMake environment variables that rust-analyzer can't provide
**Workaround**: Disable build scripts in IDE settings. Use `west build` as source of truth.

---

## Rust Implementation Lessons Learned

### Critical Issue: Devicetree Code Generation Bug

**Problem**: Zephyr Rust devicetree binding generator produces broken code for FRDM-MCXN947 flash partitions:
```
error[E0425]: cannot find function `get_instance_raw` in module `super::super::super`
```

**Root Cause**: Bug in `modules/lang/rust/dt-rust.yaml` — flash partition binding generation assumes a devicetree hierarchy that doesn't match this board.

**Solution Implemented**:
1. Created custom `rust-blinky/dt-rust.yaml` excluding the flash-partition rule
2. Modified `rust-blinky/CMakeLists.txt` to override `DT_AUGMENTS`
3. GPIO/LED/timers work fine; only flash partition APIs are unavailable

**If upstream fixes this**: Remove `dt-rust.yaml` and the `DT_AUGMENTS` override from CMakeLists.txt. Test with: `cd modules/lang/rust/samples/blinky && west build -b frdm_mcxn947/mcxn947/cpu0`

---

## Useful Commands

```bash
# Activate environment
source /Users/deniskyslytsyn/zephyrproject/.venv/bin/activate

# Build (clean)
west build -p always -b frdm_mcxn947/mcxn947/cpu0

# Flash
west flash

# Orchestrator
cd orchestrator && uv run orch build ../c-blinky

# Check JSONL logs
python3 -c "import json; [print(json.loads(l)['type'], json.loads(l)['session_id']) for l in open('logs/orchestrator.jsonl')]"
```

---

## Dependencies & Prerequisites

- **Zephyr SDK**: 0.17.4 or later
- **Python**: 3.8+ (with west installed in venv)
- **Rust**: 1.85.0 or later
- **LinkServer**: For flashing NXP boards
- **CMake**: 3.20.0+
- **uv**: For running the orchestrator (`uv run orch`)

---

## For AI Agents

1. **Don't re-implement** existing code unless asked to modify it
2. **Test orchestrator changes** with: `cd orchestrator && uv run orch build ../c-blinky`
3. **Logs go to** `logs/orchestrator.jsonl` (single JSONL file, append mode)

---

**Last Updated**: 2026-02-08
**Status**: All phases complete ✅
