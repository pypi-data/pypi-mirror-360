import os
import json
import time
import textwrap
import logging
from typing import Dict, Any, Union, Tuple
from io import BytesIO
import numpy as np
from google.cloud import storage
from ..helper.decorators import require_token, require_api_key, require_auth
TORCH_AVAILABLE = False
SKL2ONNX_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None

try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    from sklearn.base import BaseEstimator
    SKL2ONNX_AVAILABLE = True
except ImportError:
    convert_sklearn = None
    FloatTensorType = None
    BaseEstimator = None

from io import BytesIO
from typing import Tuple

class ModelManagement:
    def __init__(self, client):
        self._client = client

    @require_api_key
    def generate_ai_dataset(
        self,
        name: str,
        aoi_geojson: str,
        expression_x: str,
        filter_x_rate: float,
        filter_y_rate: float,
        samples: int,
        tile_size: int,
        expression_y: str = "skip",
        filter_x: str = "skip",
        filter_y: str = "skip",
        crs: str = "epsg:4326",
        res: float = 0.001,
        region: str = "aus",
        start_year: int = None,
        end_year: int = None,
    ) -> dict:
        """
        Generate an AI dataset using specified parameters.

        Args:
            name (str): Name of the dataset to generate
            aoi_geojson (str): Path to GeoJSON file containing area of interest
            expression_x (str): Expression for X variable (e.g. "MSWX.air_temperature@(year=2021, month=1)")
            filter_x (str): Filter for X variable (e.g. "MSWX.air_temperature@(year=2021, month=1)")
            filter_x_rate (float): Filter rate for X variable (e.g. 0.5)
            expression_y (str): Expression for Y variable with {year} placeholder
            filter_y (str): Filter for Y variable (e.g. "MSWX.air_temperature@(year=2021, month=1)")
            filter_y_rate (float): Filter rate for Y variable (e.g. 0.5)
            samples (int): Number of samples to generate
            tile_size (int): Size of tiles in degrees
            crs (str, optional): Coordinate reference system. Defaults to "epsg:4326"
            res (float, optional): Resolution in degrees. Defaults to 0.001
            region (str, optional): Region code. Defaults to "aus"
            start_year (int, optional): Start year for data generation. Required if end_year provided
            end_year (int, optional): End year for data generation. Required if start_year provided

        Returns:
            dict: Response from the AI dataset generation API

        Raises:
            APIError: If the API request fails
        """
        # Build config for expressions and filters
        config = {
            "expressions": [{"expr": expression_x, "res": res, "prefix": "x"}],
            "filters": []
        }

        if expression_y != "skip":
            config["expressions"].append({"expr": expression_y, "res": res, "prefix": "y"})

        if filter_x != "skip":
            config["filters"].append({"expr": filter_x, "res": res, "rate": filter_x_rate})
        if filter_y != "skip":
            config["filters"].append({"expr": filter_y, "res": res, "rate": filter_y_rate})

        # Replace year placeholders if start_year is provided
        if start_year is not None:
            expression_x = expression_x.replace("{year}", str(start_year))
            if expression_y != "skip":
                expression_y = expression_y.replace("{year}", str(start_year))
            if filter_x != "skip":
                filter_x = filter_x.replace("{year}", str(start_year))
            if filter_y != "skip":
                filter_y = filter_y.replace("{year}", str(start_year))

        # Load AOI GeoJSON
        with open(aoi_geojson, 'r') as f:
            aoi_data = json.load(f)

        task_response = self._client.mass_stats.random_sample(
            name=name,
            config=config,
            aoi=aoi_data,
            samples=samples,
            year_range=[start_year, end_year],
            crs=crs,
            tile_size=tile_size,
            res=res,
            region=region,
            output="netcdf",
            server=self._client.url,
            bucket="terrakio-mass-requests",
            overwrite=True
        )
        task_id = task_response["task_id"]

        # Wait for job completion with progress bar
        while True:
            result = self._client.track_mass_stats_job(ids=[task_id])
            status = result[task_id]['status']
            completed = result[task_id].get('completed', 0)
            total = result[task_id].get('total', 1)
            
            # Create progress bar
            progress = completed / total if total > 0 else 0
            bar_length = 50
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            percentage = progress * 100
            
            self._client.logger.info(f"Job status: {status} [{bar}] {percentage:.1f}% ({completed}/{total})")   

            if status == "Completed":
                self._client.logger.info("Job completed successfully!")
                break
            elif status == "Error":
                self._client.logger.info("Job encountered an error")
                raise Exception(f"Job {task_id} encountered an error")
            
            # Wait 5 seconds before checking again
            time.sleep(5)

        # after all the random sample jobs are done, we then start the mass stats job
        task_id = self._client.mass_stats.start_mass_stats_job(task_id)
        return task_id
    
    @require_api_key
    async def upload_model(self, model, model_name: str, input_shape: Tuple[int, ...] = None):
        """
        Upload a model to the bucket so that it can be used for inference.
        Converts PyTorch and scikit-learn models to ONNX format before uploading.
        
        Args:
            model: The model object (PyTorch model or scikit-learn model)
            model_name: Name for the model (without extension)
            input_shape: Shape of input data for ONNX conversion (e.g., (1, 10) for batch_size=1, features=10)
                        Required for PyTorch models, optional for scikit-learn models
        
        Raises:
            APIError: If the API request fails
            ValueError: If model type is not supported or input_shape is missing for PyTorch models
            ImportError: If required libraries (torch or skl2onnx) are not installed
        """
        uid = (await self._client.auth.get_user_info())["uid"]
        
        client = storage.Client()
        bucket = client.get_bucket('terrakio-mass-requests')
        
        # Convert model to ONNX format
        onnx_bytes = self._convert_model_to_onnx(model, model_name, input_shape)
        
        # Upload ONNX model to bucket
        blob = bucket.blob(f'{uid}/{model_name}/models/{model_name}.onnx')
        
        blob.upload_from_string(onnx_bytes, content_type='application/octet-stream')
        self._client.logger.info(f"Model uploaded successfully to {uid}/{model_name}/models/{model_name}.onnx")

    def _convert_model_to_onnx(self, model, model_name: str, input_shape: Tuple[int, ...] = None) -> bytes:
        """
        Convert a model to ONNX format and return as bytes.
        
        Args:
            model: The model object (PyTorch or scikit-learn)
            model_name: Name of the model for logging
            input_shape: Shape of input data
            
        Returns:
            bytes: ONNX model as bytes
            
        Raises:
            ValueError: If model type is not supported
            ImportError: If required libraries are not installed
        """
        # Early check for any conversion capability
        if not (TORCH_AVAILABLE or SKL2ONNX_AVAILABLE):
            raise ImportError(
                "ONNX conversion requires additional dependencies. Install with:\n"
                "  pip install torch  # For PyTorch models\n"
                "  pip install skl2onnx  # For scikit-learn models\n"
                "  pip install torch skl2onnx  # For both"
            )
        
        # Check if it's a PyTorch model using isinstance (preferred) with fallback
        is_pytorch = False
        if TORCH_AVAILABLE:
            is_pytorch = (isinstance(model, torch.nn.Module) or 
                         hasattr(model, 'state_dict'))
        
        # Check if it's a scikit-learn model
        is_sklearn = False
        if SKL2ONNX_AVAILABLE:
            is_sklearn = (isinstance(model, BaseEstimator) or 
                         (hasattr(model, 'fit') and hasattr(model, 'predict')))
        
        if is_pytorch and TORCH_AVAILABLE:
            return self._convert_pytorch_to_onnx(model, model_name, input_shape)
        elif is_sklearn and SKL2ONNX_AVAILABLE:
            return self._convert_sklearn_to_onnx(model, model_name, input_shape)
        else:
            # Provide helpful error message
            model_type = type(model).__name__
            model_module = type(model).__module__
            available_types = []
            missing_deps = []
            
            if TORCH_AVAILABLE:
                available_types.append("PyTorch (torch.nn.Module)")
            else:
                missing_deps.append("torch")
                
            if SKL2ONNX_AVAILABLE:
                available_types.append("scikit-learn (BaseEstimator)")
            else:
                missing_deps.append("skl2onnx")
            
            if missing_deps:
                raise ImportError(
                    f"Model type {model_type} from {model_module} detected, but required dependencies missing: {', '.join(missing_deps)}. "
                    f"Install with: pip install {' '.join(missing_deps)}"
                )
            else:
                raise ValueError(
                    f"Unsupported model type: {model_type} from {model_module}. "
                    f"Supported types: {', '.join(available_types)}"
                )

    def _convert_pytorch_to_onnx(self, model, model_name: str, input_shape: Tuple[int, ...]) -> bytes:
        """Convert PyTorch model to ONNX format with dynamic input dimensions."""
        if input_shape is None:
            raise ValueError("input_shape is required for PyTorch models")
        
        self._client.logger.info(f"Converting PyTorch model {model_name} to ONNX...")
        
        try:
            # Set model to evaluation mode
            model.eval()
            
            # Create dummy input
            dummy_input = torch.randn(input_shape)
            
            # Use BytesIO to avoid creating temporary files
            onnx_buffer = BytesIO()
            
            # Determine dynamic axes based on input shape
            # Common patterns for different input types:
            if len(input_shape) == 4:  # Convolutional input: (batch, channels, height, width)
                dynamic_axes = {
                    'float_input': {
                        0: 'batch_size',
                        2: 'height',    # Make height dynamic for variable input sizes
                        3: 'width'      # Make width dynamic for variable input sizes
                    },
                    'output': {0: 'batch_size'}
                }
            elif len(input_shape) == 3:  # Could be (batch, sequence, features) or (batch, height, width)
                dynamic_axes = {
                    'float_input': {
                        0: 'batch_size',
                        1: 'dim1',      # Generic dynamic dimension
                        2: 'dim2'       # Generic dynamic dimension
                    },
                    'output': {0: 'batch_size'}
                }
            elif len(input_shape) == 2:  # Likely (batch, features)
                dynamic_axes = {
                    'float_input': {
                        0: 'batch_size'
                        # Don't make features dynamic as it usually affects model architecture
                    },
                    'output': {0: 'batch_size'}
                }
            else:
                # For other shapes, just make batch size dynamic
                dynamic_axes = {
                    'float_input': {0: 'batch_size'},
                    'output': {0: 'batch_size'}
                }
            
            torch.onnx.export(
                model,
                dummy_input,
                onnx_buffer,
                export_params=True,
                opset_version=11,
                do_constant_folding=True,
                input_names=['float_input'],
                output_names=['output'],
                dynamic_axes=dynamic_axes
            )
            
            self._client.logger.info(f"Successfully converted {model_name} with dynamic axes: {dynamic_axes}")
            return onnx_buffer.getvalue()
            
        except Exception as e:
            raise ValueError(f"Failed to convert PyTorch model {model_name} to ONNX: {str(e)}")


    def _convert_sklearn_to_onnx(self, model, model_name: str, input_shape: Tuple[int, ...] = None) -> bytes:
        """Convert scikit-learn model to ONNX format."""
        self._client.logger.info(f"Converting scikit-learn model {model_name} to ONNX...")
        
        # Try to infer input shape if not provided
        if input_shape is None:
            if hasattr(model, 'n_features_in_'):
                input_shape = (1, model.n_features_in_)
            else:
                raise ValueError(
                    "input_shape is required for scikit-learn models when n_features_in_ is not available. "
                    "This usually happens with older sklearn versions or models not fitted yet."
                )
        
        try:
            # Convert scikit-learn model to ONNX
            initial_type = [('float_input', FloatTensorType(input_shape))]
            onnx_model = convert_sklearn(model, initial_types=initial_type)
            return onnx_model.SerializeToString()
            
        except Exception as e:
            raise ValueError(f"Failed to convert scikit-learn model {model_name} to ONNX: {str(e)}")
        
    @require_api_key
    async def upload_and_deploy_cnn_model(self, model, model_name: str, dataset: str, product: str, input_expression: str, dates_iso8601: list, input_shape: Tuple[int, ...] = None):
        """
        Upload a CNN model to the bucket and deploy it.
        
        Args:
            model: The model object (PyTorch model or scikit-learn model)
            model_name: Name for the model (without extension)
            dataset: Name of the dataset to create
            product: Product name for the inference
            input_expression: Input expression for the dataset
            dates_iso8601: List of dates in ISO8601 format
            input_shape: Shape of input data for ONNX conversion (required for PyTorch models)

        Raises:
            APIError: If the API request fails
            ValueError: If model type is not supported or input_shape is missing for PyTorch models
            ImportError: If required libraries (torch or skl2onnx) are not installed
        """
        await self.upload_model(model=model, model_name=model_name, input_shape=input_shape)
        # so the uploading process is kinda similar, but the deployment step is kinda different
        await self.deploy_cnn_model(dataset=dataset, product=product, model_name=model_name, input_expression=input_expression, model_training_job_name=model_name, dates_iso8601=dates_iso8601)

    @require_api_key
    async def upload_and_deploy_model(self, model, model_name: str, dataset: str, product: str, input_expression: str, dates_iso8601: list, input_shape: Tuple[int, ...] = None):
        """
        Upload a model to the bucket and deploy it.
        
        Args:
            model: The model object (PyTorch model or scikit-learn model)
            model_name: Name for the model (without extension)
            dataset: Name of the dataset to create
            product: Product name for the inference
            input_expression: Input expression for the dataset
            dates_iso8601: List of dates in ISO8601 format
            input_shape: Shape of input data for ONNX conversion (required for PyTorch models)
        """
        await self.upload_model(model=model, model_name=model_name, input_shape=input_shape)
        await self.deploy_model(dataset=dataset, product=product, model_name=model_name, input_expression=input_expression, model_training_job_name=model_name, dates_iso8601=dates_iso8601)

    @require_api_key
    def train_model(
        self, 
        model_name: str, 
        training_dataset: str, 
        task_type: str, 
        model_category: str, 
        architecture: str, 
        region: str, 
        hyperparameters: dict = None
    ) -> dict:
        """
        Train a model using the external model training API.
        
        Args:
            model_name (str): The name of the model to train.
            training_dataset (str): The training dataset identifier.
            task_type (str): The type of ML task (e.g., regression, classification).
            model_category (str): The category of model (e.g., random_forest).
            architecture (str): The model architecture.
            region (str): The region identifier.
            hyperparameters (dict, optional): Additional hyperparameters for training.
            
        Returns:
            dict: The response from the model training API.
            
        Raises:
            APIError: If the API request fails
        """
        payload = {
            "model_name": model_name,
            "training_dataset": training_dataset,
            "task_type": task_type,
            "model_category": model_category,
            "architecture": architecture,
            "region": region,
            "hyperparameters": hyperparameters
        }
        return self._client._terrakio_request("POST", "/train_model", json=payload)

    @require_api_key
    async def deploy_model(
        self, 
        dataset: str, 
        product: str, 
        model_name: str, 
        input_expression: str, 
        model_training_job_name: str, 
        dates_iso8601: list
    ) -> Dict[str, Any]:
        """
        Deploy a model by generating inference script and creating dataset.
        
        Args:
            dataset: Name of the dataset to create
            product: Product name for the inference
            model_name: Name of the trained model
            input_expression: Input expression for the dataset
            model_training_job_name: Name of the training job
            dates_iso8601: List of dates in ISO8601 format
            
        Returns:
            dict: Response from the deployment process
            
        Raises:
            APIError: If the API request fails
        """
        # Get user info to get UID
        user_info = await self._client.auth.get_user_info()
        uid = user_info["uid"]
        
        # Generate and upload script
        script_content = self._generate_script(model_name, product, model_training_job_name, uid)
        script_name = f"{product}.py"
        self._upload_script_to_bucket(script_content, script_name, model_training_job_name, uid)
        
        # Create dataset
        return await self._client.datasets.create_dataset(
            name=dataset,
            collection="terrakio-datasets",
            products=[product],
            path=f"gs://terrakio-mass-requests/{uid}/{model_training_job_name}/inference_scripts",
            input=input_expression,
            dates_iso8601=dates_iso8601,
            padding=0
        )
    
    @require_api_key
    async def deploy_cnn_model(
        self, 
        dataset: str, 
        product: str, 
        model_name: str, 
        input_expression: str, 
        model_training_job_name: str, 
        dates_iso8601: list
    ) -> Dict[str, Any]:
        """
        Deploy a CNN model by generating inference script and creating dataset.
        
        Args:
            dataset: Name of the dataset to create
            product: Product name for the inference
            model_name: Name of the trained model
            input_expression: Input expression for the dataset
            model_training_job_name: Name of the training job
            dates_iso8601: List of dates in ISO8601 format

        Returns:
            dict: Response from the deployment process

        Raises:
            APIError: If the API request fails
        """
        # Get user info to get UID
        user_info = await self._client.auth.get_user_info()
        uid = user_info["uid"]
        
        # Generate and upload script
        script_content = self.generate_cnn_script(model_name, product, model_training_job_name, uid)
        script_name = f"{product}.py"
        self._upload_script_to_bucket(script_content, script_name, model_training_job_name, uid)
        # Create dataset
        return await self._client.datasets.create_dataset(
            name=dataset,
            collection="terrakio-datasets",
            products=[product],
            path=f"gs://terrakio-mass-requests/{uid}/{model_training_job_name}/inference_scripts",
            input=input_expression,
            dates_iso8601=dates_iso8601,
            padding=0
        )

    @require_api_key
    def _generate_script(self, model_name: str, product: str, model_training_job_name: str, uid: str) -> str:
        """
        Generate Python inference script for the model.
        
        Args:
            model_name: Name of the model
            product: Product name
            model_training_job_name: Training job name
            uid: User ID
            
        Returns:
            str: Generated Python script content
        """
        return textwrap.dedent(f'''
            import logging
            from io import BytesIO

            import numpy as np
            import pandas as pd
            import xarray as xr
            from google.cloud import storage
            from onnxruntime import InferenceSession

            logging.basicConfig(
                level=logging.INFO
            )

            def get_model():
                logging.info("Loading model for {model_name}...")

                client = storage.Client()
                bucket = client.get_bucket('terrakio-mass-requests')
                blob = bucket.blob('{uid}/{model_training_job_name}/models/{model_name}.onnx')

                model = BytesIO()
                blob.download_to_file(model)
                model.seek(0)

                session = InferenceSession(model.read(), providers=["CPUExecutionProvider"])
                return session

            def {product}(*bands, model):
                logging.info("start preparing data")
                
                data_arrays = list(bands)
                                
                reference_array = data_arrays[0]
                original_shape = reference_array.shape
                logging.info(f"Original shape: {{original_shape}}")
                
                if 'time' in reference_array.dims:
                    time_coords = reference_array.coords['time']
                    if len(time_coords) == 1:
                        output_timestamp = time_coords[0]
                    else:
                        years = [pd.to_datetime(t).year for t in time_coords.values]
                        unique_years = set(years)
                        
                        if len(unique_years) == 1:
                            year = list(unique_years)[0]
                            output_timestamp = pd.Timestamp(f"{{year}}-01-01")
                        else:
                            latest_year = max(unique_years)
                            output_timestamp = pd.Timestamp(f"{{latest_year}}-01-01")
                else:
                    output_timestamp = pd.Timestamp("1970-01-01")

                averaged_bands = []
                for data_array in data_arrays:
                    if 'time' in data_array.dims:
                        averaged_band = np.mean(data_array.values, axis=0)
                        logging.info(f"Averaged band from {{data_array.shape}} to {{averaged_band.shape}}")
                    else:
                        averaged_band = data_array.values
                        logging.info(f"No time dimension, shape: {{averaged_band.shape}}")

                    flattened_band = averaged_band.reshape(-1, 1)
                    averaged_bands.append(flattened_band)

                input_data = np.hstack(averaged_bands)

                logging.info(f"Final input shape: {{input_data.shape}}")

                output = model.run(None, {{"float_input": input_data.astype(np.float32)}})[0]

                logging.info(f"Model output shape: {{output.shape}}")

                if len(original_shape) >= 3:
                    spatial_shape = original_shape[1:]
                else:
                    spatial_shape = original_shape

                output_reshaped = output.reshape(spatial_shape)

                output_with_time = np.expand_dims(output_reshaped, axis=0)

                if 'time' in reference_array.dims:
                    spatial_dims = [dim for dim in reference_array.dims if dim != 'time']
                    spatial_coords = {{dim: reference_array.coords[dim] for dim in spatial_dims if dim in reference_array.coords}}
                else:
                    spatial_dims = list(reference_array.dims)
                    spatial_coords = dict(reference_array.coords)

                result = xr.DataArray(
                    data=output_with_time.astype(np.float32),
                    dims=['time'] + list(spatial_dims),
                    coords={{
                        'time': [output_timestamp.values],
                        'y': spatial_coords['y'].values,
                        'x': spatial_coords['x'].values
                    }}
                )
                return result
            ''').strip()
    
    @require_api_key
    def generate_cnn_script(self, model_name: str, product: str, model_training_job_name: str, uid: str) -> str:
        """
        Generate Python inference script for CNN model with time-stacked bands.
        
        Args:
            model_name: Name of the model
            product: Product name
            model_training_job_name: Training job name
            uid: User ID
            
        Returns:
            str: Generated Python script content
        """
        return textwrap.dedent(f'''
            import logging
            from io import BytesIO

            import numpy as np
            import pandas as pd
            import xarray as xr
            from google.cloud import storage
            from onnxruntime import InferenceSession

            logging.basicConfig(
                level=logging.INFO
            )

            def get_model():
                logging.info("Loading CNN model for {model_name}...")

                client = storage.Client()
                bucket = client.get_bucket('terrakio-mass-requests')
                blob = bucket.blob('{uid}/{model_training_job_name}/models/{model_name}.onnx')

                model = BytesIO()
                blob.download_to_file(model)
                model.seek(0)

                session = InferenceSession(model.read(), providers=["CPUExecutionProvider"])
                return session

            def {product}(*bands, model):
                logging.info("Start preparing CNN data with time-stacked bands")
                
                data_arrays = list(bands)
                
                if not data_arrays:
                    raise ValueError("No bands provided")
                    
                reference_array = data_arrays[0]
                original_shape = reference_array.shape
                logging.info(f"Original shape: {{original_shape}}")
                
                # Get time coordinates - all bands should have the same time dimension
                if 'time' not in reference_array.dims:
                    raise ValueError("Time dimension is required for CNN processing")
                    
                time_coords = reference_array.coords['time']
                num_timestamps = len(time_coords)
                logging.info(f"Number of timestamps: {{num_timestamps}}")
                
                # Get spatial dimensions
                spatial_dims = [dim for dim in reference_array.dims if dim != 'time']
                height = reference_array.sizes[spatial_dims[0]]  # assuming first spatial dim is height
                width = reference_array.sizes[spatial_dims[1]]   # assuming second spatial dim is width
                logging.info(f"Spatial dimensions: {{height}} x {{width}}")
                
                # Stack bands across time dimension
                # Result will be: (num_bands * num_timestamps, height, width)
                stacked_channels = []
                
                for band_idx, data_array in enumerate(data_arrays):
                    logging.info(f"Processing band {{band_idx + 1}}/{{len(data_arrays)}}")
                    
                    # Ensure consistent time coordinates across bands
                    if not np.array_equal(data_array.coords['time'].values, time_coords.values):
                        logging.warning(f"Band {{band_idx}} has different time coordinates, aligning...")
                        data_array = data_array.sel(time=time_coords, method='nearest')
                    
                    # Extract values and ensure proper ordering (time, height, width)
                    band_values = data_array.values
                    if band_values.ndim == 3:
                        # Reorder dimensions if needed to ensure (time, height, width)
                        time_dim_idx = data_array.dims.index('time')
                        if time_dim_idx != 0:
                            axes_order = [time_dim_idx] + [i for i in range(len(data_array.dims)) if i != time_dim_idx]
                            band_values = np.transpose(band_values, axes_order)
                    
                    # Add each timestamp of this band to the channel stack
                    for t in range(num_timestamps):
                        stacked_channels.append(band_values[t])
                        
                # Stack all channels: (num_bands * num_timestamps, height, width)
                input_channels = np.stack(stacked_channels, axis=0)
                total_channels = len(data_arrays) * num_timestamps
                logging.info(f"Stacked channels shape: {{input_channels.shape}}")
                logging.info(f"Total channels: {{total_channels}} ({{len(data_arrays)}} bands × {{num_timestamps}} timestamps)")
                
                # Add batch dimension: (1, num_channels, height, width)
                input_data = np.expand_dims(input_channels, axis=0).astype(np.float32)
                logging.info(f"Final input shape for CNN: {{input_data.shape}}")
                
                # Run inference
                output = model.run(None, {{"float_input": input_data}})[0]
                logging.info(f"Model output shape: {{output.shape}}")
                
                # Process output back to xarray format
                # Assuming output is (1, height, width) or (1, 1, height, width)
                if output.ndim == 4 and output.shape[1] == 1:
                    # Remove channel dimension if it's 1
                    output_2d = output[0, 0]
                elif output.ndim == 3:
                    # Remove batch dimension
                    output_2d = output[0]
                else:
                    # Handle other cases
                    output_2d = np.squeeze(output)
                    if output_2d.ndim != 2:
                        raise ValueError(f"Unexpected output shape after processing: {{output_2d.shape}}")
                
                # Determine output timestamp (use the latest timestamp)
                output_timestamp = time_coords[-1]
                
                # Get spatial coordinates from reference array
                spatial_coords = {{dim: reference_array.coords[dim] for dim in spatial_dims}}
                
                # Create output DataArray
                result = xr.DataArray(
                    data=np.expand_dims(output_2d.astype(np.float32), axis=0),
                    dims=['time'] + spatial_dims,
                    coords={{
                        'time': [output_timestamp.values],
                        spatial_dims[0]: spatial_coords[spatial_dims[0]].values,
                        spatial_dims[1]: spatial_coords[spatial_dims[1]].values
                    }}
                )
                
                logging.info(f"Final result shape: {{result.shape}}")
                return result
            ''').strip()
    
    @require_api_key
    def _upload_script_to_bucket(self, script_content: str, script_name: str, model_training_job_name: str, uid: str):
        """Upload the generated script to Google Cloud Storage"""

        client = storage.Client()
        bucket = client.get_bucket('terrakio-mass-requests')
        blob = bucket.blob(f'{uid}/{model_training_job_name}/inference_scripts/{script_name}')
        blob.upload_from_string(script_content, content_type='text/plain')
        logging.info(f"Script uploaded successfully to {uid}/{model_training_job_name}/inference_scripts/{script_name}")
