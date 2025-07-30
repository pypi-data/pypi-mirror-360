"""Script to check the installed CUDA version."""

import onnxruntime as ort
import torch

from mynd.utils.log import logger


def main() -> None:
    """Main function."""

    # Check CUDA availability
    logger.info("")
    logger.info("---------- Torch ----------")
    logger.info(f"Torch CUDA available:     {torch.cuda.is_available()}")
    logger.info(f"Torch CUDA version:       {torch.version.cuda}")
    logger.info("---------------------------")
    logger.info("")

    # Print CUDA path
    # logger.info(f"CUDA path: {torch.utils.cpp_extension.CUDA_HOME}")

    onnx_has_cuda: bool = "CUDAExecutionProvider" in ort.get_available_providers()
    onnx_providers: list[str] = ort.get_available_providers()

    # Check if CUDA EP is available in onnxruntime
    logger.info("")
    logger.info("---------- ONNX ----------")
    logger.info(f"CUDA EP available:        {onnx_has_cuda}")
    logger.info(f"ONNX Providers:           {onnx_providers}")
    logger.info(f"ONNX Runtime version:     {ort.__version__}")
    logger.info(f"ONNX device:              {ort.get_device()}")
    logger.info("--------------------------")
    logger.info("")


if __name__ == "__main__":
    main()
