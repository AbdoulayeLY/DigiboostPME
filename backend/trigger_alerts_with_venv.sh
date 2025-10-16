#!/bin/bash
# Script pour déclencher les alertes avec le virtualenv activé

cd "$(dirname "$0")"
source venv/bin/activate
python trigger_test_alerts.py
