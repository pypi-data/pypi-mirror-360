#!/usr/bin/env python3
from __future__ import annotations
from soup_files import ProgressBarAdapter, ProgressBarSimple
from typing import Optional


class CreatePbar(object):
    _instance: Optional['CreatePbar'] = None

    def __new__(cls, pbar: 'ProgressBarAdapter' = None):
        if cls._instance is None:
            cls._instance = super(CreatePbar, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, pbar: 'ProgressBarAdapter' = None):
        if not self._initialized:
            self.pbar: ProgressBarAdapter = pbar or ProgressBarAdapter()
            self._initialized = True

    def get(self) -> 'ProgressBarAdapter':
        return self.pbar


