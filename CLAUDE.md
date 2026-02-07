# CLAUDE.md - Project Context Guide

> This file provides context for AI agents (Claude Code or other assistants) working on this project.

---

## Project Overview

**Name**: Zephyr RTOS & Rust Integration Orchestrator
**Goal**: Demonstrate embedded development proficiency with Zephyr RTOS using both C and Rust, featuring automated build/flash orchestration through Python

**Current Status**: C blinky implementation complete ✅, Rust integration and Python orchestrator pending

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
├── c-blinky/              # ✅ Complete - C implementation
│   ├── src/main.c         # GPIO blinky (2000ms toggle)
│   ├── CMakeLists.txt
│   ├── prj.conf
│   └── boards/*.overlay
├── rust-blinky/           # 🚧 To be implemented
├── orchestrator/          # 🚧 To be implemented
├── docs/
│   ├── task.md           # Original requirements
│   ├── progress.md       # Checklist tracker
│   └── architecture.md   # (to be created)
├── logs/                 # Generated during orchestrator runs
└── examples/sample-logs/ # Reference logs
```

---

## Key Technical Details

### C Blinky Implementation (Reference)

**File**: `c-blinky/src/main.c`

- Uses Zephyr's GPIO devicetree API
- LED accessed via `led0` alias from devicetree
- Toggle interval: 2000ms (defined as `SLEEP_TIME_MS`)
- Prints LED state to console: "LED state: ON/OFF"
- Error handling: checks GPIO ready and configuration return codes

**Build Command**: `west build -b frdm_mcxn947/mcxn947/cpu0`
**Flash Command**: `west flash`

### Rust Integration Requirements

**Rust Target**: `thumbv8m.main-none-eabihf` (ARM Cortex-M33 with hardware float)

**Zephyr Rust Module**:

- Optional module: `zephyr-lang-rust`
- Enable with: `west config manifest.project-filter +zephyr-lang-rust && west update`
- Located at: `modules/lang/rust/` after enabling
- Provides: CMake macros (`rust_cargo_application()`), `zephyr` crate for hardware abstraction

**Critical Constraints**:

- Package name MUST be `"rustapp"` in Cargo.toml (Zephyr requirement)
- Crate type MUST be `["staticlib"]`
- Use `#![no_std]` for bare-metal
- Entry point: `#[no_mangle] pub extern "C" fn main()`
- Use `src/lib.rs` NOT `src/main.rs`

### Python Orchestrator Requirements

**Purpose**: Automate `west build` and `west flash` for both C and Rust implementations

**Key Features**:

- Subprocess management with real-time output capture
- JSON-based logging (timestamped sessions)
- Error handling (build failures, board disconnects)
- CLI interface with argparse

**Logging Format**:

```json
{
  "timestamp": "ISO8601",
  "project": "c-blinky",
  "operation": "build",
  "success": true,
  "return_code": 0,
  "duration_seconds": 45.3,
  "stdout": "...",
  "stderr": "..."
}
```

---

## Important Patterns & Conventions

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

### Device Tree Overlay Naming

**Convention**: Board identifier with underscores, not slashes

- ❌ Wrong: `nrf54h20dk_nrf54h20_cpuppr.overlay` (copied from sample)
- ✅ Correct: `frdm_mcxn947_mcxn947_cpu0.overlay`

Place in: `{project}/boards/{overlay_name}.overlay`

### West Command Execution

Always activate venv and execute from project directory:

```bash
cd /Users/deniskyslytsyn/zephyrproject
source .venv/bin/activate
cd rust-blinky-orchestrator/{project}
west build -b frdm_mcxn947/mcxn947/cpu0
west flash
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Rust Target Mismatch

**Issue**: Build fails with "error: couldn't find crate for target"

**Solution**: Install correct ARM Cortex-M33 target

```bash
rustup target add thumbv8m.main-none-eabihf
```

### Pitfall 2: Wrong Cargo Package Name

**Issue**: CMake error: "Could not find rustapp staticlib"

**Solution**: Ensure Cargo.toml has:

```toml
[package]
name = "rustapp"  # MUST be exactly this

[lib]
crate-type = ["staticlib"]
```

### Pitfall 3: Subprocess Deadlocks

**Issue**: Python orchestrator hangs during large builds

**Solution**: Use non-blocking subprocess with proper buffering

```python
proc = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, text=True)
# Read stdout/stderr in real-time or with threading
```

### Pitfall 4: Board Naming Inconsistency

**Issue**: C blinky overlay references wrong board (nrf54h20dk vs frdm_mcxn947)

**Solution**: This is a naming artifact from copying Zephyr samples. The actual board is FRDM-MCXN947. Rename overlay files to match proper convention.

### Pitfall 5: Missing Rust Module

**Issue**: CMake error: "Unknown CMake command: rust_cargo_application"

**Solution**: Enable the optional Rust module

```bash
west config manifest.project-filter +zephyr-lang-rust
west update
```

### Pitfall 6: Devicetree API Confusion

**Issue**: Rust devicetree macros differ from C API

**Solution**: Reference sample code in `modules/lang/rust/samples/` for correct API usage. Use `west build -t rustdoc` to generate local API documentation.

---

## Testing Strategy

### Rust Blinky Testing

1. **Build test**: `west build -b frdm_mcxn947/mcxn947/cpu0` → expect clean build
2. **Flash test**: `west flash` → expect successful flash
3. **Functional test**: LED should blink at 2000ms intervals (same as C version)
4. **Console test**: UART output should show "LED state: ON/OFF" messages

### Orchestrator Testing

1. **CLI test**: `python orchestrator.py --help` → verify all flags
2. **Build test**: `python orchestrator.py build --target both` → both projects build
3. **Flash test**: `python orchestrator.py flash --target both` → both flash successfully
4. **Log test**: Verify JSON logs created in `logs/{session}/`
5. **Error test**: Disconnect board, verify graceful error handling

---

## Code Quality Standards

**C**:

- Follow Zephyr coding style
- Use devicetree macros for hardware abstraction
- Include error checking on all GPIO operations

**Rust**:

- Use `#![no_std]` for bare-metal
- Run `cargo clippy` for idiomatic code
- Comment FFI boundaries and Zephyr-specific patterns
- Use Result types for error handling

**Python**:

- Type hints throughout
- Docstrings for all public functions
- PEP 8 formatting
- Use dataclasses for configuration
- consider using uv

---

## Useful Commands Reference

### Zephyr/West Commands

```bash
# Activate environment
source /Users/deniskyslytsyn/zephyrproject/.venv/bin/activate

# Build with pristine (clean) build
west build -p always -b frdm_mcxn947/mcxn947/cpu0

# Flash to board
west flash

# View build configuration
west build -t menuconfig

# Generate Rust docs (if Rust module enabled)
west build -t rustdoc
```

### Rust Commands

```bash
# Add target
rustup target add thumbv8m.main-none-eabihf

# Check installed targets
rustup target list --installed

# Clippy for linting
cargo clippy
```

### Debugging

```bash
# View west configuration
west config -l

# Check for board support
west boards | grep frdm

# Verbose build output
west build -v
```

---

## Dependencies & Prerequisites

- **Zephyr SDK**: 0.17.4 or later
- **Python**: 3.8+ (with west installed in venv)
- **Rust**: 1.85.0 or later
- **LinkServer**: For flashing NXP boards
- **CMake**: 3.20.0+

---

## Next Steps for AI Agents

When continuing work on this project:

1. **Check `docs/progress.md`** to see what's already completed
2. **Reference C blinky** (`c-blinky/src/main.c`) as the functional specification
3. **Follow the implementation order**: Environment setup → Rust blinky → Python orchestrator → Documentation
4. **Test incrementally**: Build and verify each component before moving to the next
5. **Update progress.md**: Check off completed tasks as you go

---

**Last Updated**: 2026-02-07
**Status**: C blinky complete, Rust & orchestrator pending
