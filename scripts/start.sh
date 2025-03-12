pip install -r requirements.txt

export PYTHONPATH=/app

alembic upgrade head

cd src

python initial_data.py

uvicorn main:app --host 0.0.0.0 --port 8000 --reload