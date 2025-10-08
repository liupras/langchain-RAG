#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2025-01-04
# @Description:  自动根据有效期清理键值的缓存。
# @version : V0.5

import time
from threading import Lock, Thread

from enum import Enum

class Error(Enum):
    OK = 1
    FULL = -1
    EXPIRED = -2
    NOT_FOUND = -3

class Cache:
    def __init__(self, max_size, ttl):
        """
        初始化缓存类
        :param max_size: 缓存最大容量
        :param ttl: 每个缓存元素的生存时间（秒）
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}  # 存储缓存数据
        self.lock = Lock()  # 保证线程安全
        self._start_cleanup_thread()  # 启动自动清理线程

    def _start_cleanup_thread(self):
        """启动后台线程定期清理过期缓存"""
        def cleanup():
            while True:
                time.sleep(1)
                self._remove_expired_keys()

        thread = Thread(target=cleanup, daemon=True)
        thread.start()

    def _remove_expired_keys(self):
        """移除过期的缓存键"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expire_at) in self.cache.items()
                if expire_at <= current_time
            ]
            for key in expired_keys:
                del self.cache[key]
                print(f"清理过期键：{key}")

    def add(self, key, value):
        """
        添加缓存元素
        :param key: 缓存键
        :param value: 缓存值
        :raises CacheFullError: 当缓存已满时抛出
        """
        with self.lock:
            if key in self.cache:
                # 如果键已存在，更新值和过期时间
                self.cache[key] = (value, time.time() + self.ttl)
                return
            if len(self.cache) >= self.max_size:
                print("缓存已满，无法添加新元素")  
                return Error.FULL
            self.cache[key] = (value, time.time() + self.ttl)
            return Error.OK

    def get(self, key):
        """
        获取缓存值
        :param key: 缓存键
        :return: 缓存值
        :raises KeyError: 当键不存在或过期时抛出
        """
        with self.lock:
            if key in self.cache:
                value, expire_at = self.cache[key]
                if time.time() < expire_at:
                    return Error.OK, value
                else:
                    del self.cache[key]  # 自动清除过期键
                    return Error.EXPIRED,None
            return Error.NOT_FOUND,None

    def is_full(self):
        """检查缓存是否已满"""  
        with self.lock:
            return len(self.cache) >= self.max_size
        
    def __contains__(self, key):
        """
        检查键是否在缓存中
        :param key: 缓存键
        :return: True 如果键存在且未过期，否则 False
        """
        with self.lock:
            if key in self.cache:
                _, expire_at = self.cache[key]
                if time.time() < expire_at:
                    return True
                else:
                    del self.cache[key]
            return False

    def __len__(self):
        """获取缓存中当前的元素数量"""
        with self.lock:
            return len(self.cache)

    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()


# 示例使用
if __name__ == "__main__":
    cache = Cache(max_size=3, ttl=5)

    # 添加缓存
    cache.add("key1", "value1")
    print("key1" in cache)  # True

    time.sleep(6)
    print("key1" in cache)  # False，已过期

    # 添加多个元素
    cache.add("key2", "value2")
    cache.add("key3", "value3")
    cache.add("key4", "value4")
    result = cache.add("key5", "value5")  # 超过限制
    print(f'add key5:{result}')  


    # 获取缓存值
    result = cache.get("key2")  # 正常获取
    print(f'key2 is:{result}')
    time.sleep(6)
    result = cache.get("key2")  # 过期
    print(result)

