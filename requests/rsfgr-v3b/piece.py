#!/usr/bin/env python3
"""Р.С.Ф.Г.Р. 1920–2000, третья редакция, вариант Б (идеи 1–7). Партитура — ../rsfgr-v3a/score_v3.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rsfgr-v3a"))
import score_v3  # noqa: E402


def build(ctx):
    return score_v3.build(ctx, "B")
