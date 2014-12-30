from app import app
import os

if __name__ == '__main__':
    if not os.path.exists('db_repository'):
        db_create.py
    app.run(debug=True)

