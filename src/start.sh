#!/bin/bash

alembic upgrade head
python src/app.py