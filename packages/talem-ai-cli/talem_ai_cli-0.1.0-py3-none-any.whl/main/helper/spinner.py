"""Module for displaying a spinning cursor animation in the command line."""

import time

def spinning_cursor():
    """Generator that yields a spinning cursor animation."""
    yield from '|/-\\'  # Use 'yield from' to directly yield the sequence

def spinner():
    """Display a spinner in the CLI while a task is running."""
    spin = spinning_cursor()
    for _ in range(20):  # Adjust count as needed
        print(next(spin), end='\r', flush=True)
        time.sleep(0.1)
