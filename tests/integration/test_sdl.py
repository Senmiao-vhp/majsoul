import pytest
import ctypes
import os
from pathlib import Path

def test_sdl_load():
    """测试SDL2库加载"""
    try:
        # 尝试多个可能的SDL2路径
        sdl_paths = [
            "C:\\msys64\\mingw64\\bin\\SDL2.dll",
            "/usr/lib/libSDL2.so",
            "/usr/local/lib/libSDL2.dylib"
        ]
        
        for sdl_path in sdl_paths:
            if os.path.exists(sdl_path):
                sdl2 = ctypes.CDLL(sdl_path)
                assert sdl2 is not None
                return
                
        pytest.skip("SDL2库未找到")
    except Exception as e:
        pytest.fail(f"SDL2库加载失败: {e}")

def test_sdl_version():
    """测试SDL2版本信息"""
    try:
        sdl_path = "C:\\msys64\\mingw64\\bin\\SDL2.dll"
        if os.path.exists(sdl_path):
            sdl2 = ctypes.CDLL(sdl_path)
            # SDL2应该提供GetVersion函数
            assert hasattr(sdl2, "SDL_GetVersion")
        else:
            pytest.skip("SDL2库未找到")
    except Exception as e:
        pytest.fail(f"SDL2版本检查失败: {e}") 