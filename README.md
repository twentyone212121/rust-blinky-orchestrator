# Zephyr RTOS & Rust Integration Orchestrator

A comprehensive project demonstrating embedded development with Zephyr RTOS using both C and Rust, featuring automated build and flash orchestration through Python tooling.

## Overview

This project showcases the complete lifecycle of embedded firmware development:
- **C Implementation**: Traditional Zephyr blinky application
- **Rust Integration**: Modern systems programming approach with Rust on Zephyr
- **Python Orchestration**: Automated build, flash, and logging system

The orchestrator tool provides seamless automation for building and flashing both implementations while capturing comprehensive telemetry data.

## Hardware Target

- **Board**: NXP FRDM-MCXN947
- **MCU**: MCXN947
- **Debugger**: LinkServer (on-board MCU-LINK)

## Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows (with WSL2)
- **Python**: 3.8 or higher
- **Git**: For version control

### Zephyr Development Environment

1. **Zephyr SDK**: Follow the [Zephyr Getting Started Guide](https://docs.zephyrproject.org/latest/develop/getting_started/index.html)
   - Zephyr RTOS installation
   - West meta-tool
   - Zephyr SDK toolchain

2. **LinkServer**: NXP LinkServer for flashing FRDM-MCXN947
   - Download from [NXP LinkServer](https://www.nxp.com/linkserver)
   - Add to PATH: `/Applications/LinkServer_<version>` (macOS)

### Rust Toolchain

1. **Rust**: Install via rustup
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Zephyr Rust Support**: Follow [Zephyr Rust Documentation](https://docs.zephyrproject.org/latest/develop/languages/rust/index.html)
   - ARM Cortex-M target support
   - Rust embedded toolchain components

### Python Dependencies

```bash
cd orchestrator
pip install -r requirements.txt
```

## Project Structure

```
rust-blinky-orchestrator/
├── README.md                    # This file
├── .gitignore                   # Git ignore patterns
├── c-blinky/                    # C implementation
│   ├── CMakeLists.txt
│   ├── prj.conf
│   ├── src/
│   │   └── main.c
│   └── boards/
├── rust-blinky/                 # Rust implementation
│   ├── CMakeLists.txt
│   ├── prj.conf
│   ├── Cargo.toml
│   └── src/
│       └── main.rs
├── orchestrator/                # Python orchestration tool
│   ├── orchestrator.py
│   └── requirements.txt
├── logs/                        # Generated logs (gitignored)
├── docs/                        # Additional documentation
│   └── architecture.md
└── examples/                    # Sample logs for demonstration
```

## Quick Start

### 1. Environment Setup

Ensure your Zephyr environment is activated:

```bash
cd ~/zephyrproject
source .venv/bin/activate
```

### 2. Build C Implementation

```bash
cd ~/zephyrproject/rust-blinky-orchestrator/c-blinky
west build -b frdm_mcxn947/mcxn947/cpu0
```

### 3. Flash C Implementation

Connect your FRDM-MCXN947 board and run:

```bash
west flash
```

### 4. Verify Operation

The onboard LED should blink at 1 Hz.

## Development Workflow

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
# TODO: Add Rust build commands once implemented
```

### Automated Orchestration

Use the Python orchestrator to automate the entire process:

```bash
cd orchestrator
python orchestrator.py --build --flash --target both
```

See [Orchestrator Documentation](docs/architecture.md) for detailed usage.

## Testing

1. Connect FRDM-MCXN947 to your computer via USB (MCU-LINK port)
2. Verify board is detected: `LinkServer probes`
3. Run the orchestrator or manual build/flash commands
4. Observe LED blinking behavior

## Documentation

- [Architecture Overview](docs/architecture.md) - System design and component interaction
- [Setup Guide](docs/setup.md) - Detailed environment configuration (coming soon)
- [API Reference](docs/api.md) - Orchestrator tool API (coming soon)

## Troubleshooting

### LinkServer Not Found

Add LinkServer to your PATH in `~/.zshrc` or `~/.bashrc`:
```bash
export PATH="/Applications/LinkServer_24.9.75:$PATH"
```

Then reload: `source ~/.zshrc`

### No Probes Detected

- Ensure USB cable is data-capable (not charge-only)
- Connect to the MCU-LINK/Debug USB port on the board
- Try different USB ports on your computer
- Check if board is powered (LEDs should be on)

### Build Failures

- Verify Zephyr SDK is properly installed
- Activate the Python virtual environment
- Check that west is installed: `west --version`
- Ensure you're in the correct directory

## License

[Specify your license here]

## Authors

Denis Kyslytsyn

## Acknowledgments

- Zephyr Project for the excellent RTOS framework
- NXP for the FRDM-MCXN947 development board
- Rust embedded community for Zephyr integration efforts
