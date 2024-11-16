import requests
import time


class PaizaIO:
    api_key = "guest"
    headers = {}

    @staticmethod
    def send_request(code, language, stdin=None, options=None) -> (str | None):
        if stdin is None:
            stdin = ""
        if options is None:
            options = {'memory_limit': 1024**2, 'cpu_time_limit': 2.0}

        data = {
            "api_key": PaizaIO.api_key,
            "source_code": code,
            "language": language,
            "input": stdin,
            "options": options
        }

        response = requests.post("https://api.paiza.io/runners/create.json", data=data, headers=PaizaIO.headers)
        if response.status_code == 200:
            result = response.json()
            return result.get('id')
        return None

    @staticmethod
    def check_status(result_id: str) -> (str | None):
        data = {
            "api_key": PaizaIO.api_key,
            "id": result_id
        }

        response = requests.get("https://api.paiza.io/runners/get_status", json=data, headers=PaizaIO.headers)
        if response.status_code == 200:
            result = response.json()
            return result.get('status')
        return None

    @staticmethod
    def terminal_output(result_id: str) -> (dict | None):
        data = {
            "api_key": PaizaIO.api_key,
            "id": result_id
        }

        response = requests.get("https://api.paiza.io/runners/get_details", json=data, headers=PaizaIO.headers)
        if response.status_code == 200:
            result = response.json()
            return {
                "stdout": result.get("stdout"),
                "time": result.get("time"),
                "memory": result.get("memory")
            }
        return None

class Code:
    def __init__(self, inputs: list[str], outputs: list[str], code: str) -> None:
        self.inputs = []
        self.outputs = []
        self.code = code
        self.languge = "python3"

    def precheck(self):
        print(self.inputs, self.outputs)
        first_input, first_output = self.inputs[0], self.outputs[0]

        output = send(first_input)
        if output == first_output:
            return "Correct code"
        elif output == "":
            return "Error code"
        else:
            return "Incorrect code"

    def check(self):
        for index in range(0, len(self.inputs)):
            print("Print running test", index+1)
            file_input, file_output = self.inputs[index], self.outputs[index]
            output = self.send(file_input)
            if output != file_output:
                return "Incorrect code"
            elif output == "":
                return "Error code"
        return "Correct code"

    def send(self, stdin):
        request_id = PaizaIO.send_request(self.code, self.language, stdin)
        while PaizaIO.check_status(request_id) != "completed":
            time.sleep(1)
        return terminal_output().get('stdout')

