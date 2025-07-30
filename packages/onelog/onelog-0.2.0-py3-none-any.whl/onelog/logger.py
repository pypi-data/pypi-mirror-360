from .html_renderer import HTMLRenderer
from PIL import Image


class Logger:
    def __init__(self):
        self.data = {}
        self.images = {}
        self.hyperparameters = {}
        self.html_renderer = HTMLRenderer()

    def log_hyperparameters(self, value: dict):
        self.hyperparameters = value

    def log_scalar(self, value: int | float, name: str):
        if name not in self.data:
            self.data[name] = []
        self.data[name].append(value)

    def log_image(self, image: Image.Image, name: str):
        if name not in self.images:
            self.images[name] = []
        self.images[name].append(image)
    
    def finish(self, html_path: str = None):
        """
        Finish logging and optionally save an HTML report.
        
        Args:
            html_path: Optional path to save HTML report. If not provided, only prints data.
        """
        print(self.data)
        
        if html_path:
            self.html_renderer.render(self.data, self.images, html_path, self.hyperparameters)
    
    def save_html(self, target_path: str):
        """
        Save the current logged data as an HTML report.
        
        Args:
            target_path: Path where the HTML file should be saved
        """
        self.html_renderer.render(self.data, self.images, target_path, self.hyperparameters)
