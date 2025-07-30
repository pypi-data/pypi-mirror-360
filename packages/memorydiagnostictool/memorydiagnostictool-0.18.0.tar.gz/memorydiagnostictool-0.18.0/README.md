# Memory Diagnostic Tool (MDT)

The **Memory Diagnostic Tool (MDT)** is a Python-based utility designed to analyze memory training data and generate a detailed report that includes memory training results, train values, and eye diagrams. It processes inputs from **ABL/PMU4 logs (Turin/Venice)** and **BDAT (Venice)**, generating a comprehensive summary to aid in memory diagnostics.

## Features

- **Input Processing**: 
  - Accepts **ABL/PMU4 log files (Turin/Venice)**.
  - Accepts **BDAT files (Venice)**.
  
- **Output Report**:
  - Generates a report that shows:
    - **Memory Training Results**: Detailed outcomes of the memory training process.
    - **Train Value**: Numerical values derived from the training results.
    - **Eye Diagram**: A graphical representation of the signal quality during memory training.

## Requirements

Before using MDT, make sure that you have the following installed:

- Python 3.x or above
- Required Python libraries (can be installed using `pip`)

You can install the required dependencies using the following command:

```bash
pip install -r requirements.txt
