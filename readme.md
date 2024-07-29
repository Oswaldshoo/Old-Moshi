# Old Moshi

Old Moshi is a web application built using Flask and Supabase. This project is structured to support different user roles such as admin, academic, teacher, and parent.

## Project Structure
old_moshi_secondary/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   └── __init__.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── views/
│       ├── __init__.py
│       ├── admin.py
│       ├── academic.py
│       ├── teacher.py
│       └── parent.py
│
├── tests/
│   └── __init__.py
│
├── venv/
├── .env
├── .gitignore
├── requirements.txt
└── run.py
## Setup

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd Old-Moshi
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv env
    source env/Scripts/activate  # On Windows
    source env/bin/activate      # On Unix or MacOS
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    Create a `.env` file in the root directory and add your Supabase URL and Key:
    ```env
    SUPABASE_URL=<your-supabase-url>
    SUPABASE_KEY=<your-supabase-key>
    ```

5. Run the application:
    ```sh
    flask run
    ```

## Configuration

The application configuration is managed in the [`Config`](app/config.py) class. You can modify the configuration settings as needed.

## Blueprints

The application uses Flask blueprints to organize the code for different user roles:

- Admin: [`admin`](app/views/admin.py)
- Academic: [`academic`](app/views/academic.py)
- Teacher: [`teacher`](app/views/teacher.py)
- Parent: [`parent`](app/views/parent.py)

## License

This project is licensed under the MIT License.