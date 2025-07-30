import src.onelog as onelog
from PIL import Image
import numpy as np


def create_test_image(width=100, height=100, color=(255, 0, 0)):
    """Create a simple test image with the specified color."""
    img_array = np.full((height, width, 3), color, dtype=np.uint8)
    return Image.fromarray(img_array)


def test_logger():
    logger = onelog.Logger()

    hyperparameters = {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10,
        "optimizer": "Adam",
    }
    logger.log_hyperparameters(hyperparameters)

    for i in range(10):
        logger.log_scalar(i, "Dummy Loss")
        logger.log_scalar(i*2, "Dummy Loss 2")

    for i in range(100):
        logger.log_scalar(i**2, "Very High Values")

    # Create and log some test images
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    
    # Log images for "training_samples"
    for i in range(5):
        img = create_test_image(200, 150, colors[i])
        logger.log_image(img, "training_samples")
    
    # Log images for "validation_results"
    for i in range(3):
        img = create_test_image(150, 200, colors[i % len(colors)])
        logger.log_image(img, "validation_results")
    
    logger.finish(html_path="test.html")
    
    assert len(logger.data["Dummy Loss"]) == 10
    assert len(logger.data["Dummy Loss 2"]) == 10