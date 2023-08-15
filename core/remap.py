from dataclasses import dataclass

@dataclass
class RemapUrl:
    url: str
    
    def add(self, url: str):
        self.url = f"{self.url}.{url}"
        return self
    
    def set(self, url: str):
        self.url = url
        return self
    
    def remove_last(self):
        self.url = ".".join(self.to_array()[:-1])
        return self
    
    def to_array(self):
        return self.url.split(".")
    
    def get_last(self):
        return self.to_array()[-1]
    
    def __str__(self):
        return f"{self.url}"
    
@dataclass
class RemapData:
    from_path: RemapUrl or str
    to_path: RemapUrl or str
    new_name: str or None = None
    def __str__(self) -> str:
        return f"{self.from_path} -> {self.to_path}"
    def __post_init__(self):
        if isinstance(self.from_path, str):
            self.from_path = RemapUrl(self.from_path)
        if isinstance(self.to_path, str):
            self.to_path = RemapUrl(self.to_path)

@dataclass
class Remap:
    data: dict
    
    def init(self, path: list[RemapData]):
        for item in path:
            value = self.get(item.from_path)
            tmp = self.get(item.to_path)
            if isinstance(value, dict):
                for v_key, v_value in value.items():
                    tmp[v_key] = v_value
            else:
                tmp[item.from_path.get_last() if not item.new_name else item.new_name] = value
            self.data = self.remove(item.from_path)
        return self.data
            
    def get(self, path: RemapUrl):
        arr = path.to_array()
        if len(arr) == 1 and arr[0] == "":
            return self.data
        tmp = self.data
        for url in arr:
            tmp = tmp[url]
        return tmp
    
    def remove(self, path: RemapUrl):
        first = True
        while True:
            last = path.get_last()
            if last == "":
                break
            parent = path.remove_last()
            if len(parent.to_array()) == 0:
                break
            data = self.get(parent)
            if isinstance(data[last], dict) and not first:
                return self.data if len(data[last].keys()) > 0 else data[last]
            else:
                del data[last]
            first = False
        return self.data
    
    def set(self, data: dict):
        self.data = data
        return self