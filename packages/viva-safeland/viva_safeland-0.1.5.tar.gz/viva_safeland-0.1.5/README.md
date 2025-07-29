# Viva Safeland

[![PyPI version](https://badge.fury.io/py/viva_safeland.svg)](https://badge.fury.io/py/viva-safeland)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/viva_safeland.svg)](https://pypi.org/project/viva-safeland)

A new freeware for safe validation of vision-based navigation in aerial vehicles.

Viva Safeland provides a simulated environment to test and validate computer vision algorithms for drone navigation, ensuring safety before real-world deployment.

## Key Features

*   **Realistic Simulation:** Simulates drone movement and sensor data.
*   **Vision Algorithm Validation:** Test your own navigation algorithms in a controlled environment.
*   **Modular Architecture:** Easily extend and customize the simulator, HMI, and rendering components.
*   **Safety First:** Develop and debug navigation logic without risking expensive hardware.

## Installation

### Prerequisites

*   Python 3.8+
*   [Poetry](https://python-poetry.org/docs/#installation) for dependency management.
*   (Recommended) [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or another virtual environment manager.

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/juliodltv/viva_safeland.git
    cd viva_safeland
    ```

2.  **(Recommended) Create and activate a virtual environment:**

    *Using Conda:*
    ```bash
    conda create --name viva_env python=3.8
    conda activate viva_env
    ```

3.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```

## Usage

To run the main simulation, execute the following command from the root of the project:

```bash
poetry run python -m src.main
```

## Contributing

Contributions are welcome! If you have ideas for improvements or have found a bug, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

## License
XDDD

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (we should create this file next!).
