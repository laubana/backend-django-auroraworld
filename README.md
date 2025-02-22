# Back-end for the Auroraworld Project

## Available Scripts

In the root directory, you can run the following commands:

### `# python -m venv venv`

### `# venv\Scripts\activate`

### `# pip install -r requirements.txt`

### `# python manage.py migrate`

### `# python manage.py loaddata default`

### `# python manage.py runserver 0.0.0.0:4000`

### `# docker-compose up --build`

The default port is set to 4000, and the default frontend endpoint is set to http://localhost:5173.

The access token secret and refresh token secret must be provided.

SQLite has been selected as the database due to its simple deployment.

Run `python manage.py loaddata default` to populate default data.

The resources used are from https://auroragift.com/ and https://www.auroraworld.com/.


