import os
import time

import random
from functools import wraps

import natsort

from .logger import Logger

logger = Logger()


def makedirs(path):
    """"""
    if not os.path.isdir(path):
        os.makedirs(path)


def walk(path, types=None, max_depth=float("inf")):
    """"""
    depth = 0
    for root, dirs, filenames in os.walk(path):
        if depth >= max_depth:
            break
        depth += 1
        for filename in filenames:
            if types:
                type = filename.split(".")[-1]
                # type = os.path.splitext(filename)[1]
                # print(type)
                if type in types:
                    yield os.path.join(root, filename)
                    continue
            else:
                yield os.path.join(root, filename)


def walk_dirs(path, max_depth=float("inf")):
    """"""
    depth = 0
    yield path  # 返回根目录
    for root, dirs, filenames in os.walk(path):
        if depth >= max_depth:
            break
        depth += 1
        for dir in dirs:
            yield os.path.join(root, dir)


def probability_trigger(prob=0.5):
    """
    Args:
        prob: float, probability of triggering
    """
    if random.random() < prob:
        logger.info(f"probability_trigger: True, prob: {prob}")
        return True
    logger.info(f"probability_trigger: False, prob: {prob}")
    return False


def retry(retries=3, delay=1):
    """
    description:
    param:
    return:
    """

    def decorator(func):
        """
        description:
        param:
        return:
        """

        def wrapper(*args, **kwargs):
            """
            description:
            param:
            return:
            """

            attempts = retries
            while attempts > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts -= 1
                    if attempts == 0:
                        print("retry failed")
                        raise Exception("retry failed")
                        # return None

                    # 给delay加上25%的随机数，避免多个请求同时重试
                    r_delay = delay + delay * 0.25 * (1 - 2 * random.random())
                    r_delay = max(0, r_delay)

                    print(
                        f"{e}, retrying after {r_delay:.2f} seconds, {attempts} retries left"
                    )

                    time.sleep(r_delay)

        return wrapper

    return decorator


def return_on_error(default_value=None):
    """
    装饰器：当函数执行失败时返回指定的默认值

    Args:
        default_value: 发生异常时返回的默认值，默认为 None

    Example:
        @return_on_error(default_value=[])
        def process_data():
            # 如果发生异常，将返回 []
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Function {func.__name__} failed with error: {str(e)}")
                return default_value

        return wrapper

    return decorator


def sample_lines(lines, num, seed=None):
    if seed is not None:
        random.seed(seed)
    # 创建列表副本以避免修改原始列表
    lines_copy = lines.copy()
    # 对副本进行随机打乱
    random.shuffle(lines_copy)
    return lines_copy[:num]


def sample_files(files, num, seed=None):
    files = natsort.natsorted(files)
    files = sample_lines(files, num, seed)
    files = natsort.natsorted(files)
    return files


def run_cmd(cmd, shell=True, timeout=None):
    """
    执行命令并返回结果

    Args:
        cmd: 要执行的命令
        shell: 是否使用shell执行，默认为True
        timeout: 超时时间（秒），默认为None（不超时）

    Returns:
        tuple: (return_code, stdout, stderr)
            - return_code: 命令的返回码，0表示成功
            - stdout: 标准输出
            - stderr: 标准错误

    Example:
        code, out, err = run_cmd("ls -l")
        if code == 0:
            print("命令执行成功：", out)
        else:
            print("命令执行失败：", err)
    """
    import subprocess

    try:
        process = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        stdout, stderr = process.communicate(timeout=timeout)
        return_code = process.returncode

        return return_code, stdout.strip(), stderr.strip()

    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", f"命令执行超时（{timeout}秒）"
    except Exception as e:
        return -1, "", f"执行命令时发生错误：{str(e)}"
