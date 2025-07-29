# ns-docker-wrapper

**`ns-docker-wrapper`** is a Python library that simplifies using [Nerfstudio](https://docs.nerf.studio/nerfology/methods/index.html) through Docker.
It provides a clean python API to run commands inside a Docker container, handling tasks like file copying, volume management, and command construction.


## Installation

You can install the library directly from the GitHub repository using `pip`:

```bash
pip install git+https://github.com/Jourdelune/ns_docker_wrapper.git
```

## Usage Overview

The goal of `ns-docker-wrapper` is to streamline the process of running Nerfstudio commands in a Dockerized environment.

In this way, you can use Nerfstudio without compiling it locally, but you can still use it in a Pythonic way to integrate it into your projects.


### Basic Example

Here’s a simple end-to-end example showing how to process a set of images and train a Nerfstudio model:

```python
import ns_docker_wrapper as nsdw
from ns_docker_wrapper.utils import select_largest_model

RAW_IMAGES_INPUT_PATH = "PATH_TO_YOUR_RAW_IMAGES"  # Replace this with your actual path
OUTPUT_BASE_PATH = "./nerfstudio_output"

# Initialize the ns_docker_wrapper with the base output path
nsdw.init(output_base_path=OUTPUT_BASE_PATH)

# Process the raw images and prepare the data for training
nsdw.process_data("images", nsdw.path(RAW_IMAGES_INPUT_PATH)).output_dir(
    "processed_data"
).run()

# fix colmap sparse issue from nerfstudio https://github.com/nerfstudio-project/nerfstudio/issues/3435
nsdw.process_data("images", nsdw.path(RAW_IMAGES_INPUT_PATH)).output_dir(
    "processed_data"
).skip_image_processing().skip_colmap().colmap_model_path(
    nsdw.path(str(select_largest_model()))
).run()

# Train a Nerfstudio model using the processed data
nsdw.train("splatfacto").data(
    nsdw.path("./nerfstudio_output/processed_data")
).viewer.quit_on_train_completion(True).output_dir(
    "trained_models"
).viewer_websocket_port(
    7007
).run()
```

## Available Commands

The `nsdw` object (short for `ns_docker_wrapper`) provides convenient factory methods for commonly used Nerfstudio commands.

### `nsdw.train(method: str) -> Command`

Creates a `ns-train` command for training with the specified method (e.g., `nerfacto`, `splatfacto`).

```python
nsdw.train("nerfacto")
```


### `nsdw.process_data(processor: str, data_path: Union[str, PathArgument]) -> Command`

Launches `ns-process-data` with the specified processor (e.g., `"images"`, `"video"`).

If you're using a local file path, make sure to wrap it with `nsdw.path()` so it can be copied into the container:

```python
nsdw.process_data("images", nsdw.path("/path/to/raw_images"))
```

### `nsdw.process_images(input_image_path: Union[str, PathArgument], output_dir: str) -> Command`

A shortcut for `ns-process-data images`. It simplifies the common use case of processing raw images:

```python
nsdw.process_images(nsdw.path("/path/to/images"), "processed_data")
```

### `nsdw.custom_command(command_string: str) -> Command`

Use this if you want to run a custom Nerfstudio command that's not yet covered by a built-in method:

```python
nsdw.custom_command("ns-export").add_positional_arg("colmap").run()
```


### `nsdw.path(local_path: str) -> PathArgument`

Wrap any local file or directory path with this function.
It ensures that the resource is copied into the Docker container and mapped correctly.

```python
nsdw.train("nerfacto").data(nsdw.path("/your/local/data"))
```


## Adding Arguments to Commands

Once you create a command object, you can chain argument methods to it.
The library handles kebab-case conversion and supports various argument types.


### Simple Named Arguments

Use method calls that correspond to argument names. For example:

```python
nsdw.train("nerfacto").viewer_port(7008).run()
# Translates to: ns-train nerfacto --viewer-port 7008
```

If you don’t pass a value, the argument will be included as a flag:

```python
nsdw.train("nerfacto").no_debug().run()
# Translates to: ns-train nerfacto --no-debug
```


### Nested Arguments (Dot-Notation)

Use chained methods to build nested CLI options:

```python
nsdw.train("nerfacto").pipeline.model.field_of_view(60).run()
# Translates to: ns-train nerfacto --pipeline.model.field-of-view 60
```

### Positional Arguments

For positional CLI arguments (those without `--key=value`), use `.add_positional_arg()`:

```python
nsdw.custom_command("ns-export").add_positional_arg("colmap").run()
# Translates to: ns-export colmap
```

### Local Paths and Volumes

When providing a local path, always wrap it with `nsdw.path()`.
This ensures the file or directory is made accessible inside the container:

```python
nsdw.train("nerfacto").data(nsdw.path("./datasets/my_scene")).run()
```


## License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! If you have suggestions or improvements, please open an issue or submit a pull request.
