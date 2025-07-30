@echo off
echo ===================================
echo 开始构建和发布视频解析MCP服务到PyPI
echo ===================================

:: 清理旧的构建文件
echo 清理旧的构建文件...
if exist dist rmdir /S /Q dist
if exist build rmdir /S /Q build
if exist yby6_parse_video.egg-info rmdir /S /Q yby6_parse_video.egg-info

:: 构建包
echo 构建包...
python -m build

:: 上传到PyPI
echo 上传到PyPI...
echo 请确认您已经配置了PyPI凭据
pause
python -m twine upload dist/*

echo ===================================
echo 发布完成！
echo ===================================
echo 现在可以使用以下命令安装和运行:
echo pip install yby6-parse-video-mcp
echo parse-video-mcp --help
echo ===================================
pause 