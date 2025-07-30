import os
import io
import uuid
import base64
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from loguru import logger

# Initialize FastMCP server
mcp = FastMCP("plot_generator")
mcp.settings.host = '0.0.0.0'
mcp.settings.port = 8080

# File upload service configuration
FILE_UPLOAD_API = "https://temp.byteplus-demo.com/api/files/upload"  # Replace with your actual file upload API endpoint

# Configure logger
logger.add("logs/plot_generator.log", rotation="10 MB")


def plot_to_base64(plt):
    """
    Converts a matplotlib plot to a base64 encoded string with proper header.

    Args:
        plt: The matplotlib pyplot object.

    Returns:
        A base64 encoded string of the plot image with data URI prefix.
    """
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # Add data URI prefix for base64 encoded PNG image
    img_str = f"data:image/png;base64,{img_str}"
    
    return img_str


def save_plot_to_file(plt) -> io.BytesIO:
    """
    Saves a matplotlib plot to a BytesIO object.
    
    Args:
        plt: The matplotlib pyplot object.
        
    Returns:
        BytesIO object containing the plot image.
    """
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf


def upload_file_to_service(file_data: io.BytesIO, filename: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Uploads a file to the file management service.
    
    Args:
        file_data: BytesIO object containing the file data.
        filename: Name of the file.
        description: Optional description of the file.
        
    Returns:
        Dictionary containing the response from the file upload service.
    """
    try:
        files = {'file': (filename, file_data, 'image/png')}
        data = {}
        if description:
            data['description'] = description
            
        response = requests.post(FILE_UPLOAD_API, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error uploading file to service: {str(e)}")
        raise ValueError(f"Failed to upload file: {str(e)}")


def parse_csv_data(csv_text):
    """
    Parses CSV text into a pandas DataFrame.

    Args:
        csv_text: A string containing CSV data.

    Returns:
        A pandas DataFrame.
    """
    try:
        # Use StringIO to convert the string to a file-like object
        return pd.read_csv(io.StringIO(csv_text))
    except Exception as e:
        raise ValueError(f"Error parsing CSV data: {str(e)}")



# List of allowed modules for code execution
ALLOWED_MODULES = {
    'matplotlib.pyplot': plt,
    'pandas': pd,
    'numpy': None,  # Will be imported on demand
    'math': None,  # Will be imported on demand
}


@mcp.tool()
def validate_csv_data(csv_text: str):
    """
    Validates CSV text data and returns column information if successful.

    Args:
        csv_text: A string containing CSV data to validate.

    Returns:
        A dictionary containing validation results with a standardized format:
        - success: Boolean indicating if the operation was successful
        - message: Human-readable message about the result
        - columns, row_count, data_preview: Data information (on success)
        - error, error_type: Error details (on failure)
    """
    try:
        # Attempt to parse the CSV data
        df = pd.read_csv(io.StringIO(csv_text))
        
        # If successful, return column information
        return {
            "success": True,
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "data_preview": df.head(3).to_dict(orient="records"),
            "message": "CSV data is valid"
        }
    except Exception as e:
        # If parsing fails, return the error details
        error_message = str(e)
        error_type = type(e).__name__
        logger.error(f"CSV validation error: {error_message}")
        return {
            "success": False,
            "columns": [],
            "row_count": 0,
            "data_preview": [],
            "message": error_message,
        }


@mcp.tool()
def generate_plot(python_code: str, csv_data: str):
    """
    Generates a plot using the provided Python code and CSV data, and uploads it to the file service.

    Args:
        python_code: Python code that uses matplotlib.pyplot to create a plot.
                    The code should use the variable 'df' to access the DataFrame.
        csv_data: CSV formatted data as a string.

    Returns:
        A dictionary containing standardized response with a consistent format:
        - success: Boolean indicating if the operation was successful
        - message: Human-readable message about the result
        - url: Chart URL (on successful upload)

    """
    try:
        # Parse the CSV data into a DataFrame
        df = parse_csv_data(csv_data)

        # Create a namespace for executing the code
        namespace = {
            'df': df,
            'plt': plt,
            'pd': pd
        }

        # Import allowed modules on demand
        for module_name, module_obj in ALLOWED_MODULES.items():
            if module_obj is None and module_name in python_code:
                try:
                    module_name_parts = module_name.split('.')
                    if len(module_name_parts) > 1:
                        # For submodules like matplotlib.pyplot
                        parent_module = __import__(module_name_parts[0])
                        module_obj = parent_module
                        for part in module_name_parts[1:]:
                            module_obj = getattr(module_obj, part)
                    else:
                        # For top-level modules like numpy
                        module_obj = __import__(module_name)

                    namespace[module_name.split('.')[-1]] = module_obj
                    logger.info(f"Imported module: {module_name}")
                except ImportError as e:
                    logger.warning(f"Failed to import module {module_name}: {e}")

        # Execute the provided Python code without timeout
        exec(python_code, namespace)

        try:
            # Plot has been executed

            # Save the plot to a file and upload it
            try:
                # Generate a unique filename
                filename = f"plot_{uuid.uuid4().hex}.png"
                
                # Save plot to BytesIO
                file_data = save_plot_to_file(plt)
                
                # Also get the base64 representation
                base64_image = plot_to_base64(plt)
                
                # Upload the file to the file management service
                upload_response = upload_file_to_service(file_data, filename, None)
                
                # Return standardized successful response
                return {
                    "success": True,
                    "url": f"https://temp.byteplus-demo.com/api/files/download/{upload_response.get('file', {}).get('id')}",
                    "message": "Plot generated and uploaded successfully"
                }
            except Exception as upload_error:
                logger.error(f"Error in file upload process: {str(upload_error)}")

                error_message = str(upload_error)

                return {
                    "success": False,  # Set to False since the upload failed
                    "url": "null",
                    "message": error_message
                }
        except Exception as exec_error:
            plt.close('all')  # Close any open figures
            error_message = f"Code execution error: {str(exec_error)}"
            logger.error(error_message)
            return {
                "success": False,
                "url": "null",
                "message": error_message
            }

    except Exception as e:
        # Return a detailed error message if something went wrong
        error_message = str(e)
        logger.error(f"Error generating plot: {error_message}")
        
        # Create a standardized error response
        return {
            "success": False,
            "url": None,
            "message": error_message
        }


def main():
    """
    Main entry point for the plot generator server.
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger.info("Starting plot-generator MCP server...")
    print("Starting plot-generator MCP server...")
    try:
        mcp.run(transport="sse")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise


if __name__ == "__main__":
    main()