# PlotTwister Backend

This is the backend for the PlotTwister project, built using [FastAPI](https://fastapi.tiangolo.com/). It provides APIs for interacting with the application. This guide will help you set up and run the backend on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Python**: Version 3.11 or higher (but less than 3.13).
2. **Poetry**: A dependency management tool for Python. You can install it by following the instructions [here](https://python-poetry.org/docs/#installation).

## Setup Instructions

Follow these steps to set up and run the backend:

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone <repository-url>
cd PlotTwister/backend

## 2. Install Dependencies
Use Poetry to install the required dependencies:

poetry install

## to run the backend

poetry run uvicorn src.main:app --reload
