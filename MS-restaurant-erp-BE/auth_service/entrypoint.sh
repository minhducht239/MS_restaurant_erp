#!/bin/sh
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
uvicorn main:app --host 0.0.0.0 --port 8000
