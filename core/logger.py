

class Logger:
    
    @staticmethod
    def print(file_name: str, data: any, encoding: str = "utf-8"):
        with open(file_name, 'a', encoding=encoding) as file:
            file.write(f"{data}\n")
