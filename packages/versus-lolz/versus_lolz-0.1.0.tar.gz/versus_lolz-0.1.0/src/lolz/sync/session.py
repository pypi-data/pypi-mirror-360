import time
import requests
import threading

class RequestManager:
    __delay: float
    __last_request_time: float
    __lock: threading.Lock
    __session: requests.Session

    def __init__(self, delay: float):
        self.__delay = delay
        self.__last_request_time = 0
        self.__lock = threading.Lock()
        self.__session = requests.Session()
    
    def request(self, method, url, **kwargs):
        with self.__lock:
            current_time = time.time()
            time_since_last = current_time - self.__last_request_time

            if time_since_last < self.__delay:
                time.sleep(self.__delay - time_since_last)
            
            # if "headers" in kwargs:
            #     print("DEBUG: Headers = ", kwargs["headers"])

            response = self.__session.request(method, url, **kwargs)
            self.__last_request_time = time.time()
            return response


class BaseSession:
    __req_mgr: RequestManager
    __auth_token: str
    headers: dict

    # official API delay restriction is 0.2 seconds, but real is about 0.25
    def __init__(self, auth_token: str, delay: float = .25, headers: dict = None):
        self.__req_mgr = RequestManager(delay)
        if not auth_token.startswith("Bearer "):
            auth_token = "Bearer " + auth_token
        self.__auth_token = auth_token
        self.headers = {
            "Authorization": self.__auth_token,
            "Accept": "application/json",
        }
        self.headers.update(headers or {})
    
    def request(self, method, url, **kwargs):
        kwargs["headers"] = {**self.headers, **kwargs.get("headers", {})}
        return self.__req_mgr.request(method, url, **kwargs)
    
    def get(self, url, **kwargs):
        return self.request("get", url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.request("post", url, **kwargs)
    
    def put(self, url, **kwargs):
        return self.request("put", url, **kwargs)
    
    def delete(self, url, **kwargs):
        return self.request("delete", url, **kwargs)
    
    def head(self, url, **kwargs):
        return self.request("head", url, **kwargs)
