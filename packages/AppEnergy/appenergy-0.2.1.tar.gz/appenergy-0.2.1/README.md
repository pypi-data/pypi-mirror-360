# AppEnergy

An Energy consumption calculator for Software applications.

## Description

AppEnergy is a Python package that analyzes applications and provide you application energy consumption levels. It fetches application data from multiple sources including Snapcraft, Flathub, Apple Store, GOG, Itch.io, and, MyAbandonware, then uses intelligent matching algorithms to determine energy usage patterns.

## Features

- **Multi-source Data Fetching**: Gathers application information from 5+ different sources
- **Intelligent Tag Normalization**: Cleans and standardizes tags from various sources
- **Category Matching**: Uses fuzzy matching algorithms with confidence scoring
- **Energy Level Classification**: Categorizes applications as low-cpu, moderate-cpu, or high-cpu
- **Command Line Interface**: Simple CLI for quick energy assessments
- **Python API**: Programmatic access for integration into other projects

## Installation

```bash
pip install AppEnergy
```
## Quick Start
Command Line Usage
bash# Single word applications

```bash 
AppEnergy Facebook
# Output: low-energy-level

# Multi-word applications
AppEnergy "Google Chrome"
# Output: moderate-energy-level

```