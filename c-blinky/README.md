# C Blinky - FRDM-MCXN947

Standard Zephyr RTOS LED blinky application in C.

## Quick Start

```bash
cd ~/zephyrproject/rust-blinky-orchestrator/c-blinky
source ~/zephyrproject/.venv/bin/activate
west build -b frdm_mcxn947/mcxn947/cpu0
west flash
```

**LED Behavior:** Toggles LED every 2000ms

## Key Files

- `src/main.c` - Main application using Zephyr GPIO API
- `CMakeLists.txt` - Standard Zephyr build configuration
- `prj.conf` - Enables GPIO support (`CONFIG_GPIO=y`)
- `boards/nrf54h20dk_nrf54h20_cpuppr.overlay` - LED configuration overlay
  - **Note:** Filename is from Zephyr sample template; actual board is FRDM-MCXN947

## Prerequisites

See parent [README.md](../README.md) for Zephyr SDK setup instructions.
