# sagemaker_jupyterlab_extension:

This package includes the JupyterLab extension built by SageMaker team that includes basic SageMaker JupyterLab IDE features, including resource usage (CPU, memory and storage), SageMaker JupyterLab session management and Git clone dialog. 

## Requirements
* JupyterLab >= 4
* sagemaker_jupyterlab_extension_common
* async-lru
* aws_embedded_metrics

## Installing the extension
To install the extension within local Jupyter environment, a Docker image/container or in SageMaker Studio, run:
```
pip install sagemaker_jupyterlab_extension-<version>-py3-none-any.whl`
```

## Uninstalling the extension
To uninstall this extension, run:
```
pip uninstall sagemaker_jupyterlab_extension`
```

## Troubleshooting
If you are seeing the frontend extension, but it is not working, check that the server extension is enabled:

```
jupyter serverextension list
```

If the server extension is installed and enabled, but you are not seeing the frontend extension, check the frontend extension is installed:
```
jupyter labextension list
```

If the frontend extension is installed and enabled, open Browser console and see if there are any JavaScript error that is related to the extension in Browser console.

## See DEVELOPING.md for more instructions on dev setup and contributing guidelines
