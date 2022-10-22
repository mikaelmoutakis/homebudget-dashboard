#!/usr/bin/env bash
docker compose up -d && \
	sleep 3 && \
	open "http://localhost:8501"
