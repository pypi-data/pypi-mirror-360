#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import uuid
import hashlib
import datetime
from enum import Enum
from pathlib import Path
from loguru import logger
from loguru._logger import Logger


def ensure_dir(path: str) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_file(path: Path | str) -> Path:
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def init_logger(
    level: str = "WARNING",
    logs_path: Path = Path("logs"),
) -> Logger:
    logger.remove()

    # 控制台输出
    logger.add(
        sink=sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        level=level,
    )

    # 文件日志输出
    if logs_path:
        logs_path.mkdir(parents=True, exist_ok=True)
        log_path = logs_path / f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.log"
        logger.add(
            str(log_path),
            format="{time:YYYY-MM-DD HH:mm:ss} {level: <8} {message}",
            level=level,
            encoding="utf-8",
        )

    return logger


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


class NonSerializable:
    """标记字段为不可序列化：序列化时将跳过此字段"""

    def __repr__(self):
        return "<NonSerializable>"


NON_SERIALIZABLE = NonSerializable()


def serialize(obj):
    result = None
    # 基础类型或 None
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        result = obj
    # 字典
    elif isinstance(obj, dict):
        result = {k: serialize(v) for k, v in obj.items() if v is not NON_SERIALIZABLE}
    # 列表/元组/集合
    elif isinstance(obj, (list, tuple, set)):
        result = [serialize(v) for v in obj if v is not NON_SERIALIZABLE]
    # 普通对象
    elif hasattr(obj, "__dict__"):
        filtered = {
            k: v for k, v in vars(obj).items() if not isinstance(v, NonSerializable)
        }
        result = serialize(filtered)
    else:
        raise TypeError(f"Unsupported serialization type: {type(obj)}")
    return result


def write_json(data, json_path: Path, indent=2):
    with open(json_path, "w", encoding="utf8") as file:
        json.dump(data, file, ensure_ascii=False, indent=indent, default=serialize)


def partial_md5(file: Path, chunk_size=4 * 1024 * 1024) -> str:
    with file.open("rb") as f:
        size = file.stat().st_size
        md5 = hashlib.md5()

        # 读取前 4MB
        md5.update(f.read(chunk_size))

        # 读取中间 4MB
        if size > chunk_size * 2:
            f.seek(size // 2)
            md5.update(f.read(chunk_size))

        # 读取结尾 4MB
        if size > chunk_size:
            f.seek(-chunk_size, 2)
            md5.update(f.read(chunk_size))

        return md5.hexdigest()


def get_uuid():
    # 获取uuid
    random_uuid = uuid.uuid4()
    return str(random_uuid)


def get_timestamp():
    time = datetime.datetime.now()
    return time.strftime("%Y.%m.%d-%H:%M:%S.%f")
