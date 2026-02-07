# SPDX-License-Identifier: Apache-2.0 OR MIT

cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(rust-blinky)

# Override devicetree-to-Rust mapping to work around flash partition bug
set(DT_AUGMENTS "${CMAKE_CURRENT_SOURCE_DIR}/dt-rust.yaml" CACHE INTERNAL "" FORCE)

rust_cargo_application()
