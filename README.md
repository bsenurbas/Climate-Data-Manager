
# Climate Data Manager

## Overview

**Climate Data Manager** is a user-friendly tool for managing and analyzing climate data. The application features data import from Excel files, storage in an SQLite database, and visualization through a graphical interface.

## Features

- **Excel Data Import**: Easily import climate data from Excel files.
- **Data Storage**: Securely store data in an SQLite database.
- **Graphical Interface**: Visualize your data through an intuitive graphical interface.

## Installation

To set up the Climate Data Manager on your local machine, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/bsenurbas/Climate-Data-Manager.git
   cd Climate-Data-Manager
   ```

2. **Set Up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

## Usage

After installation, you can start the application and perform the following actions:

- Import data from Excel files.
- Store climate data in the SQLite database.
- Visualize the data graphically.

## Project Structure

- `main.py`: The entry point for the application.
- `data/`: Manages data storage and retrieval.
- `utils/`: Utility functions for various tasks.
- `venv/`: Virtual environment folder (excluded from version control).
- `requirements.txt`: List of dependencies.


## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## Contact

For any inquiries or issues, please contact [busenurb277@gmail.com](mailto:busenurb277@gmail.com).
