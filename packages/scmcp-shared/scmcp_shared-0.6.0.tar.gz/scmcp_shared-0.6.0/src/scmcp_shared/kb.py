from agno.document.chunking.agentic import AgenticChunking
from agno.embedder.openai import OpenAIEmbedder
from agno.models.deepseek import DeepSeek
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.agent import AgentKnowledge
import importlib.resources
import os
import requests
import zipfile
import tempfile
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

embedder_id = os.getenv("EMBEDDER_MODEL")
embedder_api_key = os.getenv("EMBEDDER_API_KEY")
embedder_base_url = os.getenv("EMBEDDER_BASE_URL")
model_id = os.getenv("MODEL")
model_api_key = os.getenv("API_KEY")
model_base_url = os.getenv("BASE_URL")

# 配置信息
config = {
    "local_dir": "vector_db",
    "huggingface_url": "https://huggingface.co/datasets/huangshing/scmcp_vector_db/resolve/main/vector_db.zip",
}


def download_vector_db(source="huggingface"):
    """
    下载向量数据库文件

    Args:
        source: 下载源 ("huggingface" 或 "github")
    """

    # 获取本地存储路径
    package_path = importlib.resources.path("scmcp_shared", "")
    local_dir = Path(package_path) / config["local_dir"]
    local_dir.mkdir(exist_ok=True)

    # 检查是否已存在
    if (local_dir / "scmcp.lance").exists():
        logger.info("Vector database already exists locally")
        return str(local_dir)

    logger.info(f"Downloading vector database from {source}...")

    # 创建临时目录用于下载和解压
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "vector_db.zip"

        try:
            # 下载文件
            if source == "huggingface":
                url = config["huggingface_url"]
            else:
                raise ValueError(f"Unsupported source: {source}")

            logger.info(f"Downloading from: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # 解压文件
            logger.info("Extracting downloaded archive...")
            _extract_archive(zip_path, local_dir)

            logger.info(f"Vector database downloaded and extracted to: {local_dir}")
            return str(local_dir)

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download vector database: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to process vector database: {e}")


def _extract_archive(archive_path, extract_dir):
    """解压归档文件"""
    with zipfile.ZipFile(archive_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # 如果解压后只有一个子目录，移动内容到目标目录
    extracted_items = list(Path(extract_dir).iterdir())
    if len(extracted_items) == 1 and extracted_items[0].is_dir():
        subdir = extracted_items[0]
        for item in subdir.iterdir():
            shutil.move(str(item), str(extract_dir / item.name))
        subdir.rmdir()


def load_kb(software=None, auto_download=True, download_source="huggingface"):
    """
    加载知识库

    Args:
        software: 软件名称
        auto_download: 是否自动下载向量数据库
        download_source: 下载源 ("huggingface" 或 "github")
    """
    # 获取向量数据库路径
    try:
        vector_db_path = importlib.resources.path("scmcp_shared", "vector_db")
    except FileNotFoundError:
        if auto_download:
            logger.info("Vector database not found in package, attempting download...")
            vector_db_path = download_vector_db(download_source)
        else:
            raise FileNotFoundError(
                "Vector database not found. Set auto_download=True to download automatically, "
                "or manually place the vector database in the scmcp_shared package."
            )

    vector_db = LanceDb(
        table_name=software,
        uri=vector_db_path,
        embedder=OpenAIEmbedder(
            id=embedder_id,
            base_url=embedder_base_url,
            api_key=embedder_api_key,
        ),
    )
    model = DeepSeek(
        id=model_id,
        base_url=model_base_url,
        api_key=model_api_key,
    )
    knowledge_base = AgentKnowledge(
        chunking_strategy=AgenticChunking(model=model),
        vector_db=vector_db,
    )

    return knowledge_base
