# gpu_detailed_check.py
import paddle
import subprocess
import sys

print("=" * 60)
print("GPU 详细诊断")
print("=" * 60)

# 1. 检查 PaddlePaddle 的 GPU 支持
print("1. PaddlePaddle GPU 支持:")
print(f"   - 编译时CUDA支持: {paddle.device.is_compiled_with_cuda()}")
print(f"   - 可用GPU数量: {paddle.device.cuda.device_count()}")

if paddle.device.cuda.device_count() > 0:
    try:
        current_device = paddle.device.get_device()
        print(f"   - 当前设备: {current_device}")
        print(f"   - GPU名称: {paddle.device.cuda.get_device_name()}")
    except Exception as e:
        print(f"   - 设备信息获取失败: {e}")

# 2. 检查 CUDA 版本兼容性
print("\n2. CUDA 版本检查:")
try:
    paddle_cuda_version = paddle.version.cuda()
    print(f"   - Paddle编译的CUDA版本: {paddle_cuda_version}")
except:
    print("   - 无法获取Paddle CUDA版本")

# 3. 测试 GPU 计算
print("\n3. GPU 计算测试:")
try:
    # 在GPU上创建一个简单的tensor
    if paddle.device.cuda.device_count() > 0:
        x = paddle.to_tensor([1.0, 2.0, 3.0], place=paddle.CUDAPlace(0))
        y = paddle.to_tensor([4.0, 5.0, 6.0], place=paddle.CUDAPlace(0))
        z = x + y
        print(f"   - GPU计算测试: 成功")
        print(f"   - 结果: {z.numpy()}")
    else:
        print("   - 无可用GPU设备")
except Exception as e:
    print(f"   - GPU计算测试失败: {e}")

# 4. 检查系统 CUDA
print("\n4. 系统 CUDA 检查:")
try:
    result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("   - nvcc 找到:", result.stdout.split('\n')[0])
    else:
        print("   - nvcc 未找到")
except:
    print("   - 无法检查 nvcc")

print("=" * 60)