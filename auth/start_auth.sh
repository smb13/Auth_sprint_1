#!/usr/bin/env bash
alembic upgrade head

gunicorn main:app