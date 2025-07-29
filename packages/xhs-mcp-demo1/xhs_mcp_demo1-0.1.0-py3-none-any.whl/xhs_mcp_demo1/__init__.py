# 小红书自动发稿服务端脚本
# 该脚本提供API接口用于接收请求并调用小红书自动发稿功能

import os
import time
import requests
from mcp.server import FastMCP  # 导入FastMCP类用于创建MCP服务
from mcp.types import TextContent  # 导入TextContent类用于定义返回内容类型
from write_xiaohongshu import XiaohongshuPoster  # 导入小红书发布器类

# 创建FastMCP服务实例，服务名为"xhs"
mcp = FastMCP("xhs")

# 从环境变量中获取手机号，如果未设置则使用空字符串
phone = os.getenv("phone", "")
# 从环境变量中获取JSON文件路径，如果未设置则使用默认路径
path = os.getenv("json_path", "/Users/bruce/")
# 从环境变量中获取慢模式设置，如果未设置则为False
slow_mode = os.getenv("slow_mode", "False").lower() == "true"


def login():
    """
    登录小红书（示例函数，实际未在服务中使用）
    """
    poster = XiaohongshuPoster(path)
    poster.login(phone)
    time.sleep(1)
    poster.close()


def download_image(url):
    """
    下载图片到本地临时目录
    :param url: 图片URL
    :return: 本地图片路径
    """
    local_filename = url.split('/')[-1]  # 从URL中提取文件名
    temp_dir = tempfile.gettempdir()  # 获取系统临时目录
    local_path = os.path.join(temp_dir, local_filename)  # 拼接本地路径

    # 使用requests库下载图片
    with requests.get(url, stream=True) as r:
        r.raise_for_status()  # 如果请求失败则抛出异常
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):  # 分块写入文件
                f.write(chunk)
    return local_path


def download_images_parallel(urls):
    """
    并行下载多张图片到本地临时目录
    :param urls: 图片URL列表
    :return: 本地图片路径列表
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:  # 创建线程池
        results = list(executor.map(download_image, urls))  # 并行执行下载任务
    return results


@mcp.tool()
def create_note(title: str, content: str, images: list) -> list[TextContent]:
    """
    创建小红书图文笔记
    :param title: 笔记标题，不超过20字
    :param content: 笔记内容
    :param images: 图片路径或URL列表
    :return: 包含操作结果的TextContent列表
    """
    poster = XiaohongshuPoster(path)  # 创建小红书发布器实例
    res = ""
    try:
        # 如果图片URL以http开头，则下载到本地
        if len(images) > 0 and images[0].startswith("http"):
            local_images = download_images_parallel(images)
        else:
            local_images = images

        # 调用发布方法
        code, info = poster.login_to_publish(title, content, local_images, slow_mode)
        poster.close()
        res = info
    except Exception as e:
        res = "error:" + str(e)
    return [TextContent(type="text", text=res)]


@mcp.tool()
def create_video_note(title: str, content: str, videos: list) -> list[TextContent]:
    """
    创建小红书视频笔记
    :param title: 笔记标题，不超过20字
    :param content: 笔记内容
    :param videos: 视频路径或URL列表
    :return: 包含操作结果的TextContent列表
    """
    poster = XiaohongshuPoster(path)  # 创建小红书发布器实例
    res = ""
    try:
        # 如果视频URL以http开头，则下载到本地（注意：实际实现中应区分图片和视频下载）
        if len(videos) > 0 and videos[0].startswith("http"):
            local_videos = download_images_parallel(videos)  # 这里应改为专门的视频下载方法
        else:
            local_videos = videos

        # 调用视频发布方法
        code, info = poster.login_to_publish_video(title, content, local_videos, slow_mode)
        poster.close()
        res = info
    except Exception as e:
        res = "error:" + str(e)
    return [TextContent(type="text", text=res)]





def main() -> None:
    mcp.run(transport='stdio')
