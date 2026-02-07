# Rust Blinky - FRDM-MCXN947

Zephyr RTOS LED blinky application written in Rust.

## Quick Start

```bash
cd ~/zephyrproject/rust-blinky-orchestrator/rust-blinky
source ~/zephyrproject/.venv/bin/activate
west build -b frdm_mcxn947/mcxn947/cpu0
west flash
```

**LED Behavior:** Toggles LED0 (red LED) every 200ms

## Prerequisites

- Zephyr SDK 0.17.4+
- Rust 1.85.0+ with `thumbv8m.main-none-eabi` target
- Zephyr Rust module enabled (`west config manifest.project-filter +zephyr-lang-rust`)

See parent [README.md](../README.md) for detailed setup instructions.

## Devicetree Code Generation Workaround

This project includes a workaround for a Zephyr Rust devicetree binding bug on the FRDM-MCXN947:

**Problem:** The default devicetree-to-Rust code generator produces broken code for flash partitions on this board, causing compilation errors.

**Solution:**

- `dt-rust.yaml` - Custom devicetree mapping that excludes flash partition support
- `CMakeLists.txt` - Overrides the default mapping with our custom version

**Impact:** Flash partition Rust APIs are unavailable, but GPIO/LED functionality works perfectly.
