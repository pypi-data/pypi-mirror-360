# crudclient.response_strategies

This module provides strategies for converting raw HTTP API responses into structured Python data, such as Pydantic models or standard Python dictionaries and lists.

## Core Concept: `ResponseModelStrategy`

The core of this module is the abstract base class `ResponseModelStrategy[T]`. It defines the interface for response conversion strategies. Subclasses must implement two methods:

*   `convert_single(data: RawResponse) -> Union[T, JSONDict]`: Converts a raw response expected to contain a single data item. It should return either an instance of the target Pydantic model `T` or a JSON dictionary (`JSONDict`).
*   `convert_list(data: RawResponse) -> Union[List[T], JSONList, ApiResponse]`: Converts a raw response expected to contain a list of data items. It can return a list of Pydantic models (`List[T]`), a raw JSON list (`JSONList`), or a structured `ApiResponse` object (often used for paginated results).

The type variable `T` is bound to `ModelDumpable`, indicating that the target Pydantic models should support the `model_dump()` method.

## Implementations

This module provides two concrete implementations of `ResponseModelStrategy`:

### 1. `DefaultResponseModelStrategy`

This strategy provides a straightforward conversion mechanism:

*   **Initialization**: Can be configured with an optional `datamodel` (a Pydantic model class for individual items), an optional `api_response_model` (a Pydantic model class inheriting from `crudclient.models.ApiResponse` for handling structured list responses like pagination), and `list_return_keys` (a list of common dictionary keys like `"data"`, `"results"`, `"items"` where list data might be found).
*   **`convert_single`**: Attempts to convert the input data (handling raw `dict`, JSON `str`, or UTF-8 encoded `bytes`) into an instance of the provided `datamodel`. If no `datamodel` is specified, it returns the data as a `JSONDict`.
*   **`convert_list`**:
    *   If an `api_response_model` is provided, it attempts to parse the entire response using that model.
    *   Otherwise, it checks if the input data is a dictionary and looks for list data under the keys specified in `list_return_keys`. If the input is already a list, it uses that directly.
    *   If a `datamodel` is provided, it attempts to convert each item in the found list into an instance of the `datamodel`. If no `datamodel` is specified, it returns the raw `JSONList`.

### 2. `PathBasedResponseModelStrategy`

This strategy extends the conversion logic by allowing data extraction from nested structures using dot-notation paths:

*   **Initialization**: Similar to `DefaultResponseModelStrategy`, it accepts optional `datamodel` and `api_response_model`. Additionally, it takes:
    *   `single_item_path: Optional[str]`: A dot-notation path (e.g., `"result.data"`) to locate the single item data within the response.
    *   `list_item_path: Optional[str]`: A dot-notation path to locate the list data within the response.
    *   `pre_transform: Optional[ResponseTransformer]`: A callable function to modify the raw response data *before* path extraction or model conversion.
*   **`convert_single`**: Prepares the data (handles `dict`, `str`, `bytes`), applies the `pre_transform` if provided, extracts the relevant part using `single_item_path` if provided, and then converts it using the `datamodel` (or returns the extracted `JSONDict` if no model). Path segments may include numeric indices to access list elements (for example `"results.0.item"`).
*   **`convert_list`**: Prepares the data, applies `pre_transform`. If an `api_response_model` is provided and the data is a dictionary, it attempts to parse using that model. Otherwise, it extracts the list data using `list_item_path` if provided. Numeric indices in the path are also supported. Finally, it converts list items using the `datamodel` if specified, or returns the extracted `JSONList`.

## Supporting Types

*   `ApiResponseType`: A type alias for the class `crudclient.models.ApiResponse`.
*   `ResponseTransformer`: A type alias for a callable `Callable[[Any], Any]` used for pre-transformation in `PathBasedResponseModelStrategy`.
*   `ModelDumpable`: A protocol requiring a `model_dump()` method.

## Usage

These strategies are typically used internally by CRUD endpoint configurations within the `crudclient` library to define how API responses should be processed and converted into usable Python objects. The choice between `DefaultResponseModelStrategy` and `PathBasedResponseModelStrategy` depends on the structure of the specific API endpoint's responses.