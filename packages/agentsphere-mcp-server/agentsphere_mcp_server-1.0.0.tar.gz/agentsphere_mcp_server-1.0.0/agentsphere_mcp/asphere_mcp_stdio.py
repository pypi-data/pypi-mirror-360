import os
import time
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP, Context
from agentsphere import AsyncSandbox
import logging
import pathlib


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
    # handlers=[
    #     logging.FileHandler('mcp_server.log'),
    #     # 对于 STDIO 传输，可以注释掉控制台输出避免干扰
    #     # logging.StreamHandler()
    # ]
)

logger = logging.getLogger(__name__)

# 创建 FastMCP 实例，声明依赖项
mcp = FastMCP(
    name="Agent Sphere STDIO MCP Server",
    dependencies=["agentsphere"]  # 声明依赖项
)


# 单沙箱管理器
class SingleSandboxManager:
    def __init__(self):
        # 存储沙箱实例和相关信息
        self._sandbox: Optional[AsyncSandbox] = None
        self._sandbox_info: Optional[Dict[str, Any]] = None
        self._api_key: Optional[str] = None
        logger.info("单沙箱管理器初始化完成")

    def _get_api_key(self) -> str:
        """从环境变量获取 API key"""
        if self._api_key:
            return self._api_key
            
        # 尝试从环境变量获取 API key
        api_key = os.getenv("AGENTSPHERE_API_KEY")
        
        if not api_key:
            raise Exception("未找到 AGENTSPHERE_API_KEY，请设置环境变量")
        
        self._api_key = api_key
        logger.info(f"成功获取 API key: ***{api_key[-4:]}")
        return api_key

    async def get_sandbox(self) -> AsyncSandbox:
        """获取或创建沙箱实例"""
        current_time = time.time()
        logger.debug("获取沙箱实例")

        # 检查是否已有沙箱实例
        if self._sandbox is not None:
            logger.debug("找到现有沙箱实例")
            
            # 检查沙箱是否仍然运行中
            try:
                if await self._sandbox.is_running(request_timeout=5.0):
                    # 更新最后使用时间
                    if self._sandbox_info:
                        self._sandbox_info["last_used"] = current_time
                    logger.info(f"复用现有沙箱: {self._sandbox.sandbox_id}")
                    return self._sandbox
                else:
                    # 沙箱已经停止，清除缓存
                    logger.info("现有沙箱已停止，将创建新沙箱")
                    self._sandbox = None
                    self._sandbox_info = None
            except Exception as e:
                # 沙箱连接异常，清除缓存
                logger.error(f"沙箱连接异常: {str(e)}")
                self._sandbox = None
                self._sandbox_info = None

        # 创建新的沙箱实例
        try:
            api_key = self._get_api_key()
            logger.info("创建新沙箱...")
            
            new_sandbox = await AsyncSandbox.create(
                api_key=api_key,
                template="agentsphere-code-interpreter-v1",
                domain="agentsphere.run",
                timeout=3600  # 60分钟超时
            )
            
            self._sandbox = new_sandbox
            self._sandbox_info = {
                "sandbox_id": new_sandbox.sandbox_id,
                "created_at": current_time,
                "last_used": current_time
            }
            
            logger.info(f"成功创建沙箱: {new_sandbox.sandbox_id}")
            return new_sandbox
            
        except Exception as e:
            logger.error(f"创建沙箱失败: {str(e)}")
            raise Exception(f"创建沙箱失败: {str(e)}")

    def get_sandbox_info(self) -> Optional[Dict[str, Any]]:
        """获取沙箱信息"""
        if self._sandbox_info:
            logger.debug(f"获取沙箱信息: {self._sandbox_info}")
            return self._sandbox_info.copy()
        logger.debug("没有沙箱信息")
        return None

    async def cleanup(self):
        """清理沙箱资源"""
        if self._sandbox:
            try:
                logger.info(f"正在清理沙箱: {self._sandbox.sandbox_id}")
                await self._sandbox.close()
                logger.info("沙箱清理完成")
            except Exception as e:
                logger.error(f"沙箱清理失败: {str(e)}")
            finally:
                self._sandbox = None
                self._sandbox_info = None


# 全局沙箱管理器实例
sandbox_manager = SingleSandboxManager()


def _read_local_file(file_path: str) -> bytes:
    """
    读取本地文件内容（适配Mac和Windows）
    
    Args:
        file_path: 绝对文件路径
        
    Returns:
        文件内容（字节格式）
        
    Raises:
        Exception: 文件不存在或无法读取
    """
    try:
        # 使用pathlib确保跨平台兼容性
        path = pathlib.Path(file_path).resolve()
        
        # 检查文件是否存在
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 检查是否为文件（不是目录）
        if not path.is_file():
            raise IsADirectoryError(f"路径不是文件: {file_path}")
        
        # 读取文件内容
        with open(path, 'rb') as f:
            content = f.read()
        
        logger.debug(f"成功读取文件: {file_path}, 大小: {len(content)} 字节")
        return content
        
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {str(e)}")
        raise Exception(f"读取文件失败: {str(e)}")


def _normalize_path(path: Optional[str]) -> str:
    """规范化路径格式
    
    Args:
        path: 原始路径
        
    Returns:
        规范化后的路径
    """
    # 处理空值情况
    if path is None or path == "":
        return "/user_uploaded_files/"
    
    # 特殊情况：根目录保持为 "/"
    if path == "/":
        return "/"
    
    # 确保路径以/开头和结尾
    if not path.startswith('/'):
        path = '/' + path
    if not path.endswith('/'):
        path = path + '/'
    
    return path


def _scan_directory(dir_path: str, target_base_path: str = "/user_uploaded_files/") -> List[Dict[str, str]]:
    """
    递归扫描目录，获取所有文件信息
    
    Args:
        dir_path: 绝对目录路径
        target_base_path: 沙箱中的目标基础路径，默认为 /user_uploaded_files/ 
        
    Returns:
        文件信息列表，包含local_path和sandbox_path
        
    Raises:
        Exception: 目录不存在或无法访问
    """
    try:
        # 使用pathlib确保跨平台兼容性
        root_path = pathlib.Path(dir_path).resolve()
        
        # 检查目录是否存在
        if not root_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        
        # 检查是否为目录
        if not root_path.is_dir():
            raise NotADirectoryError(f"路径不是目录: {dir_path}")
        
        files_info = []
        
        # 路径预处理
        target_base_path = _normalize_path(target_base_path)
        
        # 递归遍历目录中的所有文件
        for file_path in root_path.rglob('*'):
            if file_path.is_file():
                # 计算相对路径（保持目录结构）
                relative_path = file_path.relative_to(root_path)
                
                # 构建沙箱中的路径（使用Unix风格的路径分隔符）
                if target_base_path == '/':
                    sandbox_path = f"/{root_path.name}/{relative_path.as_posix()}"
                else:
                    # target_base_path 已经以/结尾，直接拼接目录名和文件路径
                    sandbox_path = f"{target_base_path}{root_path.name}/{relative_path.as_posix()}"
                
                files_info.append({
                    "local_path": str(file_path),
                    "sandbox_path": sandbox_path
                })
        
        logger.info(f"扫描目录完成: {dir_path}, 找到 {len(files_info)} 个文件，目标路径: {target_base_path}")
        return files_info
        
    except Exception as e:
        logger.error(f"扫描目录失败 {dir_path}: {str(e)}")
        raise Exception(f"扫描目录失败: {str(e)}")


def _prepare_file_upload_list(local_path: str, target_path: str) -> List[Dict[str, str]]:
    """准备文件上传列表
    
    Args:
        local_path: 本地文件或目录路径
        target_path: 沙箱目标路径
        
    Returns:
        包含local_path和sandbox_path的文件信息列表
        
    Raises:
        FileNotFoundError: 路径不存在
        Exception: 不支持的路径类型
    """
    path = pathlib.Path(local_path).resolve()
    
    # 检查路径是否存在
    if not path.exists():
        raise FileNotFoundError(f"路径不存在: {local_path}")
    
    files_to_upload = []
    
    if path.is_file():
        # 单个文件上传
        file_name = path.name
        if target_path == '/':
            sandbox_path = f"/{file_name}"
        else:
            sandbox_path = f"{target_path}{file_name}"
        
        files_to_upload.append({
            "local_path": str(path),
            "sandbox_path": sandbox_path
        })
        
        logger.info(f"准备上传单个文件: {file_name} 到 {sandbox_path}")
        
    elif path.is_dir():
        # 目录上传
        files_to_upload = _scan_directory(str(path), target_path)
        logger.info(f"准备上传目录: {path.name} 到 {target_path}, 包含 {len(files_to_upload)} 个文件")
        
    else:
        raise Exception(f"不支持的路径类型: {local_path}")
    
    return files_to_upload


async def _create_sandbox_directories(sandbox, target_path: str, files_to_upload: List[Dict[str, str]]):
    """在沙箱中创建必要的目录结构
    
    Args:
        sandbox: 沙箱实例
        target_path: 目标基础路径
        files_to_upload: 文件上传列表
    """
    # 创建目标基础目录
    target_dir_for_creation = target_path.rstrip('/') if target_path != '/' else '/'
    logger.info(f"创建目标目录: {target_dir_for_creation}")
    
    if target_dir_for_creation != '/':
        await sandbox.files.make_dir(target_dir_for_creation)
    
    # 创建文件所需的子目录
    created_dirs = {target_dir_for_creation}
    
    for file_info in files_to_upload:
        sandbox_dir = str(pathlib.Path(file_info["sandbox_path"]).parent)
        if sandbox_dir not in created_dirs and sandbox_dir != "/":
            try:
                await sandbox.files.make_dir(sandbox_dir)
                created_dirs.add(sandbox_dir)
            except Exception as e:
                logger.warning(f"创建目录失败 {sandbox_dir}: {str(e)}")


def _prepare_upload_entries(files_to_upload: List[Dict[str, str]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """准备上传条目和文件信息
    
    Args:
        files_to_upload: 文件上传列表
        
    Returns:
        (write_entries, uploaded_files) 元组
    """
    write_entries = []
    uploaded_files = []
    
    for file_info in files_to_upload:
        try:
            # 读取本地文件内容
            file_content = _read_local_file(file_info["local_path"])
            
            # 添加到上传列表
            write_entries.append({
                "path": file_info["sandbox_path"],
                "data": file_content
            })
            
            uploaded_files.append({
                "local_path": file_info["local_path"],
                "sandbox_path": file_info["sandbox_path"],
                "size": len(file_content)
            })
            
        except Exception as e:
            logger.warning(f"跳过文件 {file_info['local_path']}: {str(e)}")
            continue
    
    return write_entries, uploaded_files


@mcp.tool
async def exec_command(
    cmd: str,
    ctx: Context  # FastMCP 会自动注入，Context 参数对客户端不可见
) -> Dict[str, Any]:
    """在 sandbox 中执行 linux 系统命令

       注意：
        - 如果执行的命令会占用命令行窗口（如启动 web 服务），函数会一直等待
        - 对于需要持续运行的服务，建议使用 nohup 后台启动方式：
          * Next.js 示例: "nohup npm run dev > nextjs.log 2>&1 &"
        - 命令执行超时时间为 90 秒

    Args:
        cmd: 要执行的命令

    Returns:
        命令执行结果，包含 stdout、stderr 和 success 字段
    """
    try:
        # loguru 日志 - 服务器端可见
        logger.info(f"[MCP工具调用 exec_command] 请求执行命令: {cmd}")

        # 获取沙箱实例
        sandbox = await sandbox_manager.get_sandbox()

        # 执行命令
        logger.debug(f"开始执行命令: {cmd}")
        result = await sandbox.commands.run(cmd=cmd, timeout=60, request_timeout=60)

        # 记录执行结果
        logger.info(
            f"命令执行完成 - 退出码: {result.exit_code}, "
            f"stdout长度: {len(result.stdout)}, stderr长度: {len(result.stderr)}"
        )
        if result.stdout:
            logger.debug(f"命令输出 (stdout): {result.stdout}")
        if result.stderr:
            logger.warning(f"命令错误输出 (stderr): {result.stderr}")

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": "true" if result.exit_code == 0 else "false"
        }

    except Exception as e:
        # loguru 错误日志 - 服务器端可见，包含完整堆栈信息
        logger.error(f"[MCP工具错误] 命令执行失败: {str(e)}", exc_info=True)

        return {
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            }
        }


@mcp.tool
async def get_preview_link(
    port: int,
    ctx: Context  # FastMCP 会自动注入，Context 参数对客户端不可见
) -> Dict[str, Any]:
    """获取 sandbox 中 web 服务的 url。
       注意：需要先通过 exec_command 创建和启动 next.js, streamlit 等等 web 服务。
       请确保启动的 web 服务端口号没有被占用。
       因为沙箱有网络安全策略，所有 web 服务无法直接通过 ip + 端口号访问，需要调用此方法才能拿到外部可以访问的 url。

    Args:
        port: 端口号

    Returns:
        url 链接
    """
    try:
        # 服务器端日志
        logger.info(f"[MCP工具调用 get_preview_link] 请求获取端口 {port} 的预览链接")

        # 获取沙箱实例
        sandbox = await sandbox_manager.get_sandbox()

        # 获取主机地址
        host = sandbox.get_host(port)
        
        # 构建完整的 URL
        preview_url = f"https://{host}"

        logger.info(f"成功生成预览链接: {preview_url}")

        return {
            "url": preview_url
        }

    except Exception as e:
        logger.error(f"[MCP工具错误] 获取预览链接失败: {str(e)}", exc_info=True)
        return {
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            }
        }


@mcp.tool
async def upload_files_to_sandbox(
        local_path: str,
        ctx: Context,  # FastMCP 会自动注入，Context 参数对客户端不可见
        target_path: Optional[str] = "/user_uploaded_files/"
) -> Dict[str, Any]:
    """将用户本地文件或文件夹上传到沙箱中的指定目录。

    可以上传单个文件或整个文件夹，上传时会保持原有的目录结构。

    Args:
        local_path: 本地文件或文件夹的绝对路径
        target_path: 沙箱中的目标目录路径，默认为 /user_uploaded_files/ (以/结尾表示目录)

    Returns:
        上传结果，包含成功上传的文件列表或错误信息
    """
    try:
        # 路径预处理
        target_path = _normalize_path(target_path)
        logger.info(f"[MCP工具调用 upload_files_to_sandbox] 请求上传: {local_path} 到 {target_path}")

        # 获取沙箱实例
        sandbox = await sandbox_manager.get_sandbox()

        # 准备文件上传列表
        files_to_upload = _prepare_file_upload_list(local_path, target_path)
        
        if not files_to_upload:
            return {
                "success": "true",
                "message": "没有找到可上传的文件",
                "uploaded_files": []
            }

        # 创建沙箱目录结构
        await _create_sandbox_directories(sandbox, target_path, files_to_upload)

        # 准备上传条目
        write_entries, uploaded_files = _prepare_upload_entries(files_to_upload)

        if not write_entries:
            return {
                "success": "false",
                "message": "没有文件成功准备上传",
                "uploaded_files": []
            }

        # 批量上传文件到沙箱
        logger.info(f"开始批量上传 {len(write_entries)} 个文件到沙箱...")
        upload_results = await sandbox.files.write(write_entries)

        # 记录上传结果
        total_size = sum(f["size"] for f in uploaded_files)
        logger.info(f"文件上传完成 - 成功上传 {len(uploaded_files)} 个文件到 {target_path}，总大小: {total_size} 字节")

        return {
            "success": "true",
            "message": f"成功上传 {len(uploaded_files)} 个文件到 {target_path}",
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files),
            "total_size": total_size,
            "target_path": target_path
        }

    except Exception as e:
        logger.error(f"[MCP工具错误] 文件上传失败: {str(e)}", exc_info=True)
        return {
            "success": "false",
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            }
        }


def main():
    """主入口函数 - 供 uvx 和命令行调用"""
    logger.info("启动 Agent Sphere STDIO MCP 服务器...")
    
    try:
        # STDIO 是 FastMCP 的默认传输方式，适用于本地客户端（如 Claude Desktop）
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行失败: {str(e)}", exc_info=True)
    finally:
        logger.info("正在清理资源...")
        try:
            # 异步清理需要在事件循环中执行
            import asyncio
            asyncio.run(sandbox_manager.cleanup())
        except Exception as e:
            logger.error(f"资源清理失败: {str(e)}")
        logger.info("MCP STDIO 服务器已停止")


if __name__ == "__main__":
    main()
