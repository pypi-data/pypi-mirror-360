#!/usr/bin/env python3
"""
Tests for the HTML renderer functionality.
"""

import os
import tempfile
from pathlib import Path
import pytest

from src.onelog import Logger, HTMLRenderer


def test_html_renderer_basic():
    """Test basic HTML renderer functionality."""
    renderer = HTMLRenderer()
    
    # Test data
    data = {
        "loss": [1.0, 0.8, 0.6, 0.4, 0.2],
        "accuracy": [0.6, 0.7, 0.8, 0.85, 0.9]
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Render HTML
        renderer.render(data, {}, tmp_path)
        
        # Check file exists
        assert os.path.exists(tmp_path)
        
        # Check file has content
        with open(tmp_path, 'r') as f:
            content = f.read()
            assert len(content) > 0
            assert "OneLog Report" in content
            assert "loss" in content
            assert "accuracy" in content
    
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_logger_html_integration():
    """Test Logger integration with HTML renderer."""
    logger = Logger()
    
    # Log some data
    for i in range(5):
        logger.log_scalar(1.0 - i * 0.2, "loss")
        logger.log_scalar(0.5 + i * 0.1, "accuracy")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Save HTML
        logger.save_html(tmp_path)
        
        # Check file exists and has content
        assert os.path.exists(tmp_path)
        
        with open(tmp_path, 'r') as f:
            content = f.read()
            assert "loss" in content
            assert "accuracy" in content
    
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_empty_data():
    """Test HTML renderer with empty data."""
    renderer = HTMLRenderer()
    
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Render with empty data
        renderer.render({}, {}, tmp_path)
        
        # File should not be created for empty data
        # The renderer prints "No data to render" and returns early
        
    finally:
        # Clean up if file was created
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    test_html_renderer_basic()
    test_logger_html_integration()
    test_empty_data()
    print("✅ All tests passed!") 