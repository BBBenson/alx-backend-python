# Python Generators Project

This project demonstrates advanced usage of Python generators for efficient handling of large datasets, batch processing, and memory-efficient computations.

## Learning Objectives

- Master Python Generators using the `yield` keyword
- Handle Large Datasets with batch processing and lazy loading
- Simulate Real-world Scenarios with live data updates
- Optimize Performance using memory-efficient operations
- Apply SQL Knowledge with dynamic data fetching

## Project Structure

- `scripts/seed.py` - Database setup and seeding
- `0-stream_users.py` - Generator for streaming database rows
- `1-batch_processing.py` - Batch processing with generators
- `2-lazy_paginate.py` - Lazy loading with pagination
- `4-stream_ages.py` - Memory-efficient aggregation
- `user_data.csv` - Sample data for seeding
- Test files: `0-main.py`, `1-main.py`, `2-main.py`, `3-main.py`

## Requirements

- Python 3.x
- MySQL database
- mysql-connector-python package

## Setup

1. Install required packages:
   \`\`\`bash
   pip install mysql-connector-python
   \`\`\`

2. Set up MySQL database with appropriate credentials

3. Run the setup script:
   \`\`\`bash
   python 0-main.py
   \`\`\`

## Usage

Each task can be run independently:

- Task 0: Database setup - `python 0-main.py`
- Task 1: Stream users - `python 1-main.py`
- Task 2: Batch processing - `python 2-main.py`
- Task 3: Lazy pagination - `python 3-main.py`
- Task 4: Average age calculation - `python 4-stream_ages.py`

## Key Features

- **Memory Efficiency**: Uses generators to process large datasets without loading everything into memory
- **Lazy Loading**: Data is fetched only when needed
- **Batch Processing**: Processes data in configurable batch sizes
- **Database Integration**: Seamless integration with MySQL database
- **Error Handling**: Robust error handling for database operations
