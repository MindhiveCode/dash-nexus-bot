import time
import os
import redis
import json


class UsefulFunctions:

    def __init__(self):
        pass

    @staticmethod
    def check_cache(cache_key):
        """
        Checks the cache to see if a key exists
        param cache_key: A string representing a key
        type cache_key: string
        """
        db = redis.from_url(os.environ.get("REDIS_URL"))
        if db.get(cache_key):
            return True
        else:
            return False

    @staticmethod
    def write_cache(data, cache_key, ex_time=300):
        """
        Write data with a key of cache_key to the redis cache
        param data: A python dictionary holding the data you want cached
        param cache_key: A string representing a key
        type data: dict
        type cache_key: string
        """
        db = redis.from_url(os.environ.get("REDIS_URL"))
        try:
            db.set(cache_key, json.dumps(data), ex=ex_time)
            return True
        except Exception as e:
            print(e)
            print("Failed to write to cache")

    @staticmethod
    def read_cache(cache_key):
        """
        Read data with a key of cache_key from the redis cache
        param cache_key: A string representing a key
        type cache_key: string
        """

        db = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
        data = json.loads(db.get(cache_key))

        return data
