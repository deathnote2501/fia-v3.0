"""
FIA v3.0 - Chart Generation Schemas
Pydantic schemas for chart generation with Bootstrap color integration
"""

from typing import List, Dict, Any, Literal, Optional, Union
from pydantic import BaseModel, Field, validator


# Bootstrap theme colors (hex values)
BOOTSTRAP_COLORS = {
    "primary": "#0d6efd",    # Blue
    "secondary": "#6c757d",  # Gray
    "success": "#198754",    # Green
    "info": "#0dcaf0",       # Cyan
    "warning": "#ffc107",    # Yellow
    "danger": "#dc3545",     # Red
    "light": "#f8f9fa",      # Light gray
    "dark": "#212529"        # Dark gray
}

# Predefined color palettes for charts using Bootstrap colors
CHART_COLOR_PALETTES = {
    "default": [
        BOOTSTRAP_COLORS["primary"],
        BOOTSTRAP_COLORS["success"], 
        BOOTSTRAP_COLORS["warning"],
        BOOTSTRAP_COLORS["danger"],
        BOOTSTRAP_COLORS["info"],
        BOOTSTRAP_COLORS["secondary"]
    ],
    "blues": [
        BOOTSTRAP_COLORS["primary"],
        BOOTSTRAP_COLORS["info"],
        "#4dabf7",  # Light blue variant
        "#1c7ed6",  # Dark blue variant
        "#339af0",  # Medium blue variant
        BOOTSTRAP_COLORS["secondary"]
    ],
    "success": [
        BOOTSTRAP_COLORS["success"],
        "#51cf66",  # Light green variant
        "#37b24d",  # Medium green variant
        "#2f9e44",  # Dark green variant
        BOOTSTRAP_COLORS["info"],
        BOOTSTRAP_COLORS["primary"]
    ]
}


class ChartDataPoint(BaseModel):
    """Individual data point for charts"""
    label: str = Field(..., description="Label for this data point")
    value: float = Field(..., description="Numeric value for this data point")


class ChartConfig(BaseModel):
    """Configuration for a single chart"""
    type: Literal["line", "pie", "radar"] = Field(..., description="Type of chart to generate")
    title: str = Field(..., description="Title for the chart")
    description: Optional[str] = Field(None, description="Optional description explaining what the chart shows")
    labels: List[str] = Field(..., description="Labels for chart data points")
    data: Union[List[float], List[List[float]]] = Field(..., description="Numeric data values (accepts nested arrays)")
    color_palette: Literal["default", "blues", "success"] = Field(
        "default", 
        description="Bootstrap color palette to use"
    )
    sources: Optional[List[Dict[str, str]]] = Field(
        default_factory=list,
        description="List of web sources used for chart data with title and url"
    )
    
    @validator('labels', pre=True)
    def extract_labels(cls, v, values):
        """Extract labels from data if they're embedded in dict format"""
        if not v and 'data' in values:
            # If no labels provided but data contains dicts with 'name' field, extract them
            data = values['data']
            if isinstance(data, list) and data and isinstance(data[0], dict) and 'name' in data[0]:
                return [item['name'] for item in data if isinstance(item, dict) and 'name' in item]
        return v
    
    @validator('data')
    def flatten_data(cls, v):
        """Flatten and extract data from various VertexAI response formats"""
        if not v:
            return []
        
        flattened = []
        for item in v:
            if isinstance(item, dict):
                # Handle object format like {'name': 'TikTok', 'value': 1000}
                if 'value' in item:
                    val = item['value']
                    if isinstance(val, (int, float)):
                        flattened.append(float(val))
                    elif isinstance(val, list):
                        # Handle nested values like {'name': 'TikTok', 'value': [1000, 1500, 1700]}
                        for nested_val in val:
                            if isinstance(nested_val, (int, float)):
                                flattened.append(float(nested_val))
                # Handle object format like {'team': 'Marketing', 'values': [78, 82, 85, 85]}
                elif 'values' in item:
                    values = item['values']
                    if isinstance(values, list):
                        for val in values:
                            if isinstance(val, (int, float)):
                                flattened.append(float(val))
                # Handle format like {'name': 'Platform', 'data': [1000, 1200]}
                elif 'data' in item:
                    data = item['data']
                    if isinstance(data, list):
                        for val in data:
                            if isinstance(val, (int, float)):
                                flattened.append(float(val))
                # If dict has numeric keys or just extract any numeric values
                else:
                    for key, val in item.items():
                        if isinstance(val, (int, float)):
                            flattened.append(float(val))
                        elif isinstance(val, list):
                            for nested_val in val:
                                if isinstance(nested_val, (int, float)):
                                    flattened.append(float(nested_val))
            elif isinstance(item, list):
                # Flatten nested list
                for subitem in item:
                    if isinstance(subitem, (int, float)):
                        flattened.append(float(subitem))
                    elif isinstance(subitem, dict):
                        # Recursively handle dicts in lists
                        if 'value' in subitem and isinstance(subitem['value'], (int, float)):
                            flattened.append(float(subitem['value']))
                    elif isinstance(subitem, str) and subitem.replace('.', '').replace('-', '').isdigit():
                        flattened.append(float(subitem))
            elif isinstance(item, (int, float)):
                flattened.append(float(item))
            elif isinstance(item, str) and item.replace('.', '').replace('-', '').isdigit():
                flattened.append(float(item))
        
        return flattened if flattened else v


class ChartGenerationRequest(BaseModel):
    """Request for chart generation"""
    slide_content: str = Field(..., min_length=10, description="Content of the slide to analyze")
    slide_title: Optional[str] = Field(None, description="Title of the slide")
    max_charts: int = Field(3, ge=1, le=5, description="Maximum number of charts to generate")


class ChartGenerationResponse(BaseModel):
    """Response containing generated chart configurations"""
    success: bool = Field(..., description="Whether chart generation was successful")
    charts: List[ChartConfig] = Field(default_factory=list, description="List of generated chart configurations")
    message: str = Field(..., description="Status message or explanation")
    processing_time_seconds: Optional[float] = Field(None, description="Time taken to generate charts")
    

class ChartAnalysisResult(BaseModel):
    """Internal model for VertexAI structured output"""
    recommended_charts: List[ChartConfig] = Field(
        default_factory=list, 
        description="List of recommended chart configurations"
    )