from abc import ABC
from dataclasses import dataclass

@dataclass
class Logger(ABC):
    DEBUG: bool = False
        
    def log(self, data: str):
        pass
    
@dataclass
class FileLogger(Logger):
    file_name: str = "log.txt"
    encoding: str = "utf-8"
    def log(self, data: str):
        if self.DEBUG:
            with open(self.file_name, 'a', encoding=self.encoding) as file:
                file.write(f"{data}\n")
                
@dataclass
class ConsoleLogger(Logger):
    def log(self, data: str):
        if self.DEBUG:
            print(data)