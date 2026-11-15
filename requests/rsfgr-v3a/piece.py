#!/usr/bin/env python3
"""Р.С.Ф.Г.Р. 1920–2000, третья редакция, вариант А (идеи 1, 2, 4, 5). Партитура — score_v3.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_v3  # noqa: E402


def build(ctx):
    return score_v3.build(ctx, "A")
