import os
import json
import base64
import io
from pathlib import Path
from typing import Dict, List, Union
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from PIL import Image


class HTMLRenderer:
    """Renders logged scalar data as an interactive HTML report with charts."""
    
    def __init__(self):
        # Set up Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template("report.html")
    
    def render(self, data: Dict[str, List[Union[int, float]]], images: Dict[str, List[Image.Image]], target_path: str, hyperparameters: Dict = None) -> None:
        """
        Render the data as an HTML file with interactive charts and image galleries.
        
        Args:
            data: Dictionary where keys are metric names and values are lists of scalar values
            images: Dictionary where keys are image names and values are lists of PIL Image objects
            target_path: Path where the HTML file should be saved
            hyperparameters: Dictionary of hyperparameters to display in the report
        """
        if not data and not images and not hyperparameters:
            print("No data to render")
            return
        
        # Prepare data for charts
        chart_configs = self._prepare_chart_configs(data)
        
        # Prepare images for gallery
        image_galleries = self._prepare_image_galleries(images)
        
        # Calculate total data points
        total_data_points = sum(len(values) for values in data.values())
        total_images = sum(len(img_list) for img_list in images.values())
        
        # Prepare template context
        context = {
            "title": "OneLog Report",
            "chart_configs": chart_configs,
            "image_galleries": image_galleries,
            "hyperparameters": hyperparameters or {},
            "total_data_points": total_data_points,
            "total_images": total_images,
            "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Render template
        html_content = self.template.render(context)
        
        # Ensure target directory exists
        Path(target_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write HTML file
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report saved to: {target_path}")
    
    def _prepare_chart_configs(self, data: Dict[str, List[Union[int, float]]]) -> List[Dict]:
        """Prepare chart configurations for Chart.js."""
        chart_configs = []
        
        for metric_name, values in data.items():
            if not values:
                continue
                
            # Create x-axis labels (step numbers)
            labels = list(range(1, len(values) + 1))
            
            # Generate a color for this metric
            color = self._generate_color(len(chart_configs))
            
            chart_config = {
                "id": f"chart_{metric_name.replace(' ', '_').replace('-', '_')}",
                "title": metric_name,
                "type": "line",
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "label": metric_name,
                        "data": values,
                        "borderColor": color,
                        "backgroundColor": color + "20",  # Add transparency
                        "borderWidth": 2,
                        "fill": True,
                        "tension": 0.1
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": metric_name,
                            "font": {"size": 16}
                        },
                        "legend": {
                            "display": False
                        }
                    },
                    "scales": {
                        "x": {
                            "title": {
                                "display": True,
                                "text": "Step"
                            }
                        },
                        "y": {
                            "title": {
                                "display": True,
                                "text": "Value"
                            }
                        }
                    }
                }
            }
            
            chart_configs.append(chart_config)
        
        return chart_configs
    
    def _generate_color(self, index: int) -> str:
        """Generate a color for the chart based on index."""
        colors = [
            "#3B82F6",  # Blue
            "#EF4444",  # Red
            "#10B981",  # Green
            "#F59E0B",  # Yellow
            "#8B5CF6",  # Purple
            "#06B6D4",  # Cyan
            "#F97316",  # Orange
            "#84CC16",  # Lime
            "#EC4899",  # Pink
            "#6B7280",  # Gray
        ]
        return colors[index % len(colors)]
    
    def _prepare_image_galleries(self, images: Dict[str, List[Image.Image]]) -> List[Dict]:
        """Prepare image galleries for the HTML template with base64 encoding."""
        if not images:
            return []
        
        galleries = []
        
        for gallery_name, image_list in images.items():
            if not image_list:
                continue
                
            gallery_images = []
            
            for i, image in enumerate(image_list):
                # Convert image to base64
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                gallery_images.append({
                    "base64": img_str,
                    "index": i + 1,
                    "alt": f"{gallery_name} - Image {i + 1}"
                })
            
            galleries.append({
                "name": gallery_name,
                "images": gallery_images,
                "count": len(gallery_images)
            })
        
        return galleries 