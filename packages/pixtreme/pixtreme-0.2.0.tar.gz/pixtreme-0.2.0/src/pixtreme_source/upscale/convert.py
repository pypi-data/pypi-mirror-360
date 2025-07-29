import os
import sys

import onnx
import spandrel_extra_arches as ex_arch
import tensorrt as trt
import torch
from spandrel import ModelDescriptor, ModelLoader


def check_torch_model(model_path: str) -> None:
    """check_torch_model
    Check if the PyTorch model file exists and is valid, and analyze input constraints.

    Args:
        model_path: Path to the PyTorch model file (.pth or .pt)
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    try:
        ex_arch.install()
        model_desc: ModelDescriptor = ModelLoader().load_from_file(model_path)
        print(f"✅ Valid PyTorch model found at: {model_path}")

        # アーキテクチャ情報
        print(f"\n🏗️ Architecture: {model_desc.architecture.name}")
        print(f"   ID: {model_desc.architecture.id}")
        print(f"   Purpose: {model_desc.purpose}")

        # モデル特性
        print("\n📊 Model Properties:")
        print(f"   Scale: {model_desc.scale}x")
        print(f"   Input channels: {model_desc.input_channels}")
        print(f"   Output channels: {model_desc.output_channels}")
        print(f"   Tiling support: {model_desc.tiling.name}")

        # 精度サポート
        print("\n🎯 Precision Support:")
        print(f"   FP16: {'✅' if model_desc.supports_half else '❌'}")
        print(f"   BF16: {'✅' if model_desc.supports_bfloat16 else '❌'}")
        print("   FP32: ✅")

        # サイズ要件の分析
        size_req = model_desc.size_requirements
        print("\n📏 Size Requirements:")
        print(f"   Minimum size: {size_req.minimum} pixels")
        print(f"   Multiple of: {size_req.multiple_of}")
        print(f"   Square required: {'✅' if size_req.square else '❌'}")

        if size_req.none:
            print("   🔄 No specific size constraints")
        else:
            print("   ⚠️ Has size constraints")

        # 推奨入力サイズ範囲の計算
        print("\n🎯 Recommended Input Size Ranges:")

        # 最小サイズの計算
        min_size = max(64, size_req.minimum)
        if size_req.multiple_of > 1:
            min_size = ((min_size - 1) // size_req.multiple_of + 1) * size_req.multiple_of

        # 最適サイズの計算
        optimal_sizes = [512, 768, 1024]
        valid_optimal = []
        for size in optimal_sizes:
            adjusted = size
            if size_req.multiple_of > 1:
                adjusted = ((size - 1) // size_req.multiple_of + 1) * size_req.multiple_of
            if adjusted >= size_req.minimum:
                valid_optimal.append(adjusted)

        # 最大サイズの計算
        max_size = 4096
        if size_req.multiple_of > 1:
            max_size = (max_size // size_req.multiple_of) * size_req.multiple_of

        print(f"   Minimum: {min_size}x{min_size}")
        print(f"   Optimal: {', '.join([f'{s}x{s}' for s in valid_optimal[:3]])}")
        print(f"   Maximum: {max_size}x{max_size} (practical limit)")

        if size_req.square:
            print("   ⚠️ Model requires square input (width == height)")

        # タイリング推奨事項
        print("\n🧩 Tiling Recommendations:")
        if model_desc.tiling.name == "SUPPORTED":
            print("   ✅ Tiling supported - safe for large images")
            print("   💡 Recommended tile size: 512x512 to 1024x1024")
        elif model_desc.tiling.name == "DISCOURAGED":
            print("   ⚠️ Tiling discouraged - may cause artifacts")
            print("   💡 Use smaller images or full-size processing")
        elif model_desc.tiling.name == "INTERNAL":
            print("   🔄 Model handles tiling internally")
            print("   💡 Do not tile externally - process full images")

        # ONNX変換用の推奨設定
        print("\n🚀 ONNX Export Recommendations:")
        recommended_shape = (
            1,
            model_desc.input_channels,
            valid_optimal[0] if valid_optimal else min_size,
            valid_optimal[0] if valid_optimal else min_size,
        )
        print(f"   Recommended input_shape: {recommended_shape}")
        print("   Dynamic axes suggested for flexible sizing")

        # Tags情報
        if model_desc.tags:
            print(f"\n🏷️ Model Tags: {', '.join(model_desc.tags)}")

    except Exception as e:
        raise RuntimeError(f"Failed to load PyTorch model: {e}")


def check_onnx_model(model_path: str) -> None:
    """check_onnx_model
    Check if the ONNX model file exists and is valid, and show dynamic input constraints.

    Args:
        model_path: Path to the ONNX model file (.onnx)
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"ONNX model file not found: {model_path}")

    try:
        model = onnx.load(model_path)
        onnx.checker.check_model(model)
        print(f"✅ Valid ONNX model found at: {model_path}")

        # 入力情報の分析
        for i, input_info in enumerate(model.graph.input):
            print(f"\n📥 Input {i}: {input_info.name}")
            print(f"   Data Type: {onnx.TensorProto.DataType.Name(input_info.type.tensor_type.elem_type)}")

            # 入力の形状を分析
            shape_info = input_info.type.tensor_type.shape
            shape_str = []
            dynamic_dims = []

            for dim_idx, dim in enumerate(shape_info.dim):
                if dim.HasField("dim_value"):
                    # 固定サイズ
                    shape_str.append(str(dim.dim_value))
                elif dim.HasField("dim_param"):
                    # パラメータ名による動的サイズ
                    shape_str.append(f"{dim.dim_param}")
                    dynamic_dims.append((dim_idx, dim.dim_param))
                else:
                    # 制約なし動的サイズ
                    shape_str.append("?")
                    dynamic_dims.append((dim_idx, "unconstrained"))

            print(f"   Shape: [{', '.join(shape_str)}]")

            if dynamic_dims:
                print(f"   🔄 Dynamic dimensions: {len(dynamic_dims)} found")
                for dim_idx, dim_name in dynamic_dims:
                    print(f"      Axis {dim_idx}: {dim_name}")

                    # 制約情報の推測（一般的なパターン）
                    if dim_idx == 0:
                        print("         💡 Likely batch dimension (typical range: 1-16)")
                    elif dim_idx == 1:
                        print("         💡 Likely channel dimension (typically fixed)")
                    elif dim_idx >= 2:
                        print("         💡 Likely spatial dimension (height/width)")
                        print("            🔍 Common ranges for upscaling models:")
                        print("               Min: 64-128 pixels")
                        print("               Max: 2048-8192 pixels")
                        print("               Optimal: 512-1024 pixels")
            else:
                print("   📏 Static shape (no dynamic dimensions)")

        # Output information analysis
        for i, output_info in enumerate(model.graph.output):
            print(f"\n📤 Output {i}: {output_info.name}")
            print(f"   Data Type: {onnx.TensorProto.DataType.Name(output_info.type.tensor_type.elem_type)}")

            # Analyze output shape
            shape_info = output_info.type.tensor_type.shape
            shape_str = []

            for dim in shape_info.dim:
                if dim.HasField("dim_value"):
                    shape_str.append(str(dim.dim_value))
                elif dim.HasField("dim_param"):
                    shape_str.append(f"{dim.dim_param}")
                else:
                    shape_str.append("?")

            print(f"   Shape: [{', '.join(shape_str)}]")

        # TensorRT engine creation recommendations
        print("\n🚀 TensorRT optimization profile recommendations:")
        print("   For dynamic models, consider using these typical ranges:")
        print("   - Batch size: min=1, opt=1, max=4")
        print("   - Height/Width: min=256, opt=512, max=2048")
        print("   - Use onnx_to_trt_dynamic_shape() for dynamic input handling")

    except Exception as e:
        raise RuntimeError(f"Failed to load ONNX model: {e}")


def torch_to_onnx(
    model_path: str,
    onnx_path: str,
    input_shape: tuple | None = None,
    dynamic_axes: dict | None = None,
    opset_version: int = 20,
    precision: str = "fp32",
    device: str = "cuda",
) -> None:
    """torch_to_onnx
    Export a PyTorch model to ONNX format with improved type consistency.

    Args:
        model_path: Path to the PyTorch model file (.pth or .pt)
        onnx_path: Path to save the exported ONNX model
        input_shape: Shape of the input tensor (batch_size, channels, height, width)
        dynamic_axes: Dictionary defining dynamic axes for input and output tensors
        opset_version: ONNX opset version to use (default is 20)
        precision: Precision mode for the model ('fp16', 'bf16', 'fp32')
        device: Device to run the model on ('cuda' or 'cpu'). if VRAM is not enough, use 'cpu' to export the model.
    """
    print(f"Exporting PyTorch model to ONNX: {model_path} → {onnx_path}")
    print(f"Precision: {precision}, Device: {device}")
    ex_arch.install()

    model = ModelLoader().load_from_file(model_path).model.to(torch.device(device)).eval()

    if precision == "fp16":
        dtype = torch.float16
    elif precision == "bf16":
        dtype = torch.bfloat16
    else:
        dtype = torch.float32

    if dynamic_axes is None and input_shape is None:
        dynamic_axes = {
            "input": {0: "batch_size", 2: "height", 3: "width"},
            "output": {0: "batch_size", 2: "height", 3: "width"},
        }

    if input_shape is None:
        input_shape = (1, 3, 128, 128)

    print(f"Input shape: {input_shape}")
    print(f"Dynamic axes: {dynamic_axes}")

    # Use autocast for precision control (reverting to original behavior)
    with torch.autocast(device, dtype=dtype):
        dummy_input = torch.randn(input_shape, device=device)
        try:
            torch.onnx.export(
                model,
                (dummy_input,),
                onnx_path,
                opset_version=opset_version,
                export_params=True,
                do_constant_folding=True,
                input_names=["input"],
                output_names=["output"],
                dynamic_axes=dynamic_axes,
                optimize=True,
            )
            print(f"✅ ONNX model exported to: {onnx_path}")

        except Exception as e:
            print(f"❌ ONNX export failed: {e}")
            if "fp16" in precision.lower() or "half" in str(e).lower():
                print("💡 Suggestion: Try exporting with fp32 precision to avoid type issues")
                print("   Use precision='fp32' parameter")
            raise


def onnx_to_trt_dynamic_shape(
    onnx_path: str,
    engine_path: str,
    precision: str = "fp16",
    workspace: int = 1024 << 20,  # 1024MB
    size_requirements: tuple = (16, 512, 2048),  # Conservative sizes
    batch_requirements: tuple = (1, 1, 1),
) -> None:
    """
    Convert ONNX upscale model to TensorRT engine with optimization profile for dynamic shapes.

    ⚠️ WARNING: Transformer-based models (DAT, SwinIR, etc.) may not be compatible with TensorRT
    due to unsupported operations like complex attention mechanisms, dynamic reshaping, etc.
    Consider using PyTorch inference instead for such models.

    Args:
        onnx_path: Path to input ONNX model
        engine_path: Path to output TensorRT engine
        precision: Precision mode ('fp16', 'fp32', 'int8')
        workspace: Workspace size in bytes
        size_requirements: Tuple of (min_size, opt_size, max_size) for spatial dimensions
        batch_requirements: Tuple of (min_batch, opt_batch, max_batch) for batch dimension
    """
    print(f"Building TensorRT engine for upscale model from ONNX model: {onnx_path}")
    print("⚠️  WARNING: Transformer-based upscale models may not be compatible with TensorRT")
    print(f"Size requirements: min={size_requirements[0]}, opt={size_requirements[1]}, max={size_requirements[2]}")
    print(f"Batch requirements: min={batch_requirements[0]}, opt={batch_requirements[1]}, max={batch_requirements[2]}")
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)

    # Analyze ONNX model
    with open(onnx_path, "rb") as f:
        if not parser.parse(f.read()):
            for i in range(parser.num_errors):
                print(parser.get_error(i), file=sys.stderr)
            raise RuntimeError("Failed to parse the ONNX model")

    # BuilderConfi
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, workspace)
    if precision == "fp16" and builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.FP16)
    elif precision == "bf16" and builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.BF16)
    elif precision == "int8" and builder.platform_has_fast_int8:
        config.set_flag(trt.BuilderFlag.INT8)
    else:
        config.set_flag(trt.BuilderFlag.TF32)

    # Create optimization profile for dynamic shapes
    profile = builder.create_optimization_profile()

    # Get input tensor info
    input_tensor = network.get_input(0)
    input_name = input_tensor.name

    print(f"Input tensor name: {input_name}")
    print(f"Input tensor shape: {input_tensor.shape}")

    # Analyze ONNX tensor shape to detect dynamic dimensions
    onnx_shape = input_tensor.shape
    shape_list = []
    dynamic_dims = []

    # Convert TensorRT Dims to list
    for i in range(len(onnx_shape)):
        dim = onnx_shape[i]
        shape_list.append(dim)
        if dim == -1:
            dynamic_dims.append(i)

    print(f"Shape list: {shape_list}")
    print(f"Dynamic dimensions detected at axes: {dynamic_dims}")

    if not dynamic_dims:
        print("No dynamic dimensions found - no optimization profile needed")
        # For static shapes, we don't need an optimization profile
    else:
        # Build optimization profile based on detected dynamic dimensions
        min_size, opt_size, max_size = size_requirements
        min_batch, opt_batch, max_batch = batch_requirements

        min_shape = []
        opt_shape = []
        max_shape = []

        for i, dim in enumerate(shape_list):
            if dim == -1:  # Dynamic dimension
                if i == 0:  # Batch dimension
                    min_shape.append(min_batch)  # Minimum batch
                    opt_shape.append(opt_batch)  # Optimal batch
                    max_shape.append(max_batch)  # Maximum batch
                elif i >= 2:  # Height/Width dimensions (assuming NCHW format)
                    min_shape.append(min_size)  # Minimum spatial size
                    opt_shape.append(opt_size)  # Optimal spatial size
                    max_shape.append(max_size)  # Maximum spatial size
                else:  # Other dynamic dimensions (likely channels)
                    min_shape.append(1)
                    opt_shape.append(3)  # Assume channels for face detection
                    max_shape.append(4)
            else:  # Static dimension
                static_dim = int(dim)
                min_shape.append(static_dim)
                opt_shape.append(static_dim)
                max_shape.append(static_dim)

        min_shape = tuple(min_shape)
        opt_shape = tuple(opt_shape)
        max_shape = tuple(max_shape)

        print("Optimization profile set:")
        print(f"  Min shape: {min_shape}")
        print(f"  Opt shape: {opt_shape}")
        print(f"  Max shape: {max_shape}")

        # Type: ignore for TensorRT Dims compatibility
        profile.set_shape(input_name, min_shape, opt_shape, max_shape)  # type: ignore
        config.add_optimization_profile(profile)

    # Build engine
    print("Building TensorRT engine... This may take several minutes.")
    try:
        engine_bytes = builder.build_serialized_network(network, config)
        if engine_bytes is None:
            raise RuntimeError("Engine build failed - no bytes returned")
    except Exception as e:
        error_msg = str(e).lower()
        print(f"❌ TensorRT engine build failed: {e}")
        print("\n💡 Troubleshooting suggestions:")

        # Detect Transformer/Attention related errors
        if any(keyword in error_msg for keyword in ["transpose", "reshape", "gather", "attention", "foreignnode"]):
            print("\n🔍 DETECTED: Transformer/Attention model incompatibility")
            print("   Your model appears to use Transformer operations (DAT, SwinIR, etc.)")
            print("   that are not well supported by TensorRT.")
            print("\n✅ RECOMMENDED SOLUTIONS:")
            print("   1. 🚀 Use PyTorch inference instead (fastest option):")
            print("      - Load model with spandrel and use model_desc(image)")
            print("   2. 📦 Try ONNX Runtime for inference:")
            print("      - onnxruntime-gpu provides good performance")
            print("   3. 🔄 Convert to simpler architecture:")
            print("      - Try ESRGAN, RealESRGAN, or EDSR models")
            print("      - These CNN-based models work better with TensorRT")
        else:
            print("   1. Try using onnx_to_trt_fixed_shape() with a fixed input size")
            print(f"   2. Reduce workspace size further (current: {workspace // 1024 // 1024}MB)")
            print("   3. Try FP32 precision instead of FP16")
            print("   4. Check if model operations are supported by TensorRT")
            print("   5. Consider using smaller size_requirements:")
            print("      - size_requirements=(64, 128, 256)")
            print("      - Or fixed shape like (1, 3, 256, 256)")

        raise RuntimeError(f"TensorRT build failed. See suggestions above. Error: {e}")

    with open(engine_path, "wb") as f:
        f.write(engine_bytes)

    if not os.path.exists(engine_path):
        raise RuntimeError(f"Failed to save TensorRT engine to {engine_path}")

    print(f"✅ TensorRT upscale engine saved to: {engine_path}")


def onnx_to_trt_fixed_shape(
    onnx_path: str,
    engine_path: str,
    fixed_shape: tuple = (1, 3, 512, 512),
    precision: str = "fp16",
    workspace: int = 1024 << 20,
) -> None:
    """
    Convert ONNX model to TensorRT engine with fixed input shape.
    This function first modifies the ONNX model to have fixed dimensions,
    then converts it to TensorRT for optimized performance.

    Args:
        onnx_path: Path to input ONNX model
        engine_path: Path to output TensorRT engine
        fixed_shape: Fixed input shape (batch, channels, height, width)
        precision: Precision mode ('fp16', 'fp32', 'int8')
        workspace: Workspace size in bytes
    """

    print(f"Building TensorRT engine with fixed shape from ONNX model: {onnx_path}")
    print(f"Fixed input shape: {fixed_shape}")

    # Load and modify ONNX model to fix input shape
    model = onnx.load(onnx_path)

    # Get the input tensor info
    input_info = model.graph.input[0]
    original_shape = [dim.dim_value if dim.dim_value > 0 else -1 for dim in input_info.type.tensor_type.shape.dim]

    print(f"Original ONNX input shape: {original_shape}")

    # Create new input with fixed shape
    input_info.type.tensor_type.ClearField("shape")
    for dim_size in fixed_shape:
        dim = input_info.type.tensor_type.shape.dim.add()
        dim.dim_value = int(dim_size)

    print(f"Modified ONNX input to fixed shape: {fixed_shape}")

    # Validate the modified model
    try:
        onnx.checker.check_model(model)
        print("✓ Modified ONNX model is valid")
    except Exception as e:
        print(f"⚠ ONNX model validation warning: {e}")

    # Convert modified ONNX to TensorRT
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)

    # Parse the modified ONNX model
    if not parser.parse(model.SerializeToString()):
        for i in range(parser.num_errors):
            print(parser.get_error(i), file=sys.stderr)
        raise RuntimeError("Failed to parse the modified ONNX model")

    # Verify input shape
    input_tensor = network.get_input(0)
    print(f"TensorRT input tensor name: {input_tensor.name}")
    print(f"TensorRT input shape: {input_tensor.shape}")

    # BuilderConfig
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, workspace)
    if precision == "fp16" and builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.FP16)
    elif precision == "int8" and builder.platform_has_fast_int8:
        config.set_flag(trt.BuilderFlag.INT8)

    # No optimization profile needed for fixed shapes
    print("Using fixed shape - no optimization profile required")

    # Build engine
    engine_bytes = builder.build_serialized_network(network, config)
    if engine_bytes is None:
        raise RuntimeError("Engine build failed")

    with open(engine_path, "wb") as f:
        f.write(engine_bytes)

    if not os.path.exists(engine_path):
        raise RuntimeError(f"Failed to save TensorRT engine to {engine_path}")

    print(f"✅ TensorRT engine with fixed shape saved to: {engine_path}")


def onnx_to_trt(
    onnx_path: str,
    engine_path: str,
    input_shape: tuple | None = None,
    dynamic_axes: dict | None = None,
    precision: str = "fp16",
    workspace: int = 512 << 20,
    size_requirements: tuple = (16, 512, 2048),
    batch_requirements: tuple = (1, 1, 1),
) -> None:
    """
    Convert ONNX model to TensorRT engine with automatic dynamic/fixed shape handling.

    This function automatically chooses between dynamic and fixed shape optimization
    based on the provided parameters, similar to torch_to_onnx.

    Args:
        onnx_path: Path to input ONNX model
        engine_path: Path to output TensorRT engine
        input_shape: Fixed input shape (batch, channels, height, width). If None, uses dynamic shape.
        dynamic_axes: Dictionary defining dynamic axes (ignored if input_shape is provided)
        precision: Precision mode ('fp16', 'fp32', 'bf16', 'int8')
        workspace: Workspace size in bytes
        size_requirements: Tuple of (min_size, opt_size, max_size) for dynamic spatial dimensions
        batch_requirements: Tuple of (min_batch, opt_batch, max_batch) for dynamic batch dimension
    """
    print(f"Converting ONNX to TensorRT: {onnx_path} → {engine_path}")

    # If input_shape is provided, use fixed shape mode
    if input_shape is not None:
        print(f"🔒 Using FIXED shape mode: {input_shape}")
        print("⚠️  WARNING: Fixed shape may not work with Transformer-based models")

        # Fixed shape TensorRT conversion
        try:
            onnx_to_trt_fixed_shape(
                onnx_path=onnx_path, engine_path=engine_path, fixed_shape=input_shape, precision=precision, workspace=workspace
            )
        except Exception as e:
            print(f"\n❌ Fixed shape conversion failed: {e}")
            print("💡 Suggestion: Try dynamic shape mode instead")
            print("   Remove input_shape parameter or set it to None")
            raise
    else:
        print("🔄 Using DYNAMIC shape mode")
        print("⚠️  WARNING: Transformer-based models may not be compatible with TensorRT")

        # Dynamic shape TensorRT conversion
        try:
            onnx_to_trt_dynamic_shape(
                onnx_path=onnx_path,
                engine_path=engine_path,
                precision=precision,
                workspace=workspace,
                size_requirements=size_requirements,
                batch_requirements=batch_requirements,
            )
        except Exception as e:
            print(f"\n❌ Dynamic shape conversion failed: {e}")
            print("💡 Suggestion: Try fixed shape mode instead")
            print("   Use input_shape=(1, 3, 512, 512) for example")
            raise

    # Final message on success
    print("\n✅ TensorRT conversion completed successfully!")
    print(f"   Engine saved to: {engine_path}")
    print(f"   Mode: {'Fixed' if input_shape else 'Dynamic'} shape")
    print(f"   Precision: {precision}")
    print(f"   Workspace: {workspace // 1024 // 1024}MB")
