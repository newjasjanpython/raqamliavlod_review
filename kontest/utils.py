from django.conf import settings
import requests
import time
import os
import shutil
import io
import pathlib
import subprocess


DFILES = pathlib.Path(settings.BASE_DIR / 'dfiles')

if not DFILES.exists():
    DFILES.mkdir(exist_ok=True)


class RunCmdGenerator:
    @staticmethod
    def python3(path, input_string):
        process = subprocess.Popen(
            ["python3", path],
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=input_string)
        process.wait()
        if process.returncode != 0:
            raise Exception(f"Error occurred: {stderr}")

        return "".join(stdout.split())

    @staticmethod
    def java(path, input_string):
        work_dir, _ = path.rsplit(os.sep, 1)
        if not os.path.exists(os.path.join(work_dir, 'Main.class')):
            os.rename(path, path.replace('script.file', 'Main.java'))
            path = path.replace('script.file', 'Main.java')
            compile_process = subprocess.Popen(
                ["javac", path],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=work_dir
            )
            stdout, stderr = compile_process.communicate()
            compile_process.wait()

            if compile_process.returncode != 0:
                raise Exception(f"Compilation error: {stderr}")

        run_process = subprocess.Popen(
            ["java", "Main"],
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=work_dir
        )
        stdout, stderr = run_process.communicate(input_string)
        run_process.wait()

        if run_process.returncode != 0:
            raise Exception(f"Runtime error: {stderr}")

        return "".join(stdout.split())

    @staticmethod
    def cpp(path, input_string):
        work_dir, _ = path.rsplit(os.sep, 1)
        binary_name = "a.out"
        if not os.path.exists(os.path.join(work_dir, binary_name)):
            os.rename(path, path.replace('script.file', 'main.cpp'))
            compile_process = subprocess.Popen(
                ["g++", path.replace('script.file', 'main.cpp'), "-o", binary_name],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=work_dir
            )
            stdout, stderr = compile_process.communicate()
            compile_process.wait()

            if compile_process.returncode != 0:
                raise Exception(f"Compilation error: {stderr}")

        run_process = subprocess.Popen(
            [os.path.join(work_dir, binary_name)],
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=work_dir
        )
        stdout, stderr = run_process.communicate(input=input_string)
        run_process.wait()

        if run_process.returncode != 0:
            raise Exception(f"Runtime error: {stderr}")

        return "".join(stdout.split())

    @staticmethod
    def c(path, input_string):
        work_dir, _ = path.rsplit(os.sep, 1)
        binary_name = "a.out"
        if not os.path.exists(os.path.join(work_dir, binary_name)):
            os.rename(path, path.replace('script.file', 'main.c'))
            compile_process = subprocess.Popen(
                ["gcc", path.replace('script.file', 'main.c'), "-o", binary_name],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=work_dir
            )
            stdout, stderr = compile_process.communicate()
            compile_process.wait()

            if compile_process.returncode != 0:
                raise Exception(f"Compilation error: {stderr}")

        run_process = subprocess.Popen(
            [os.path.join(work_dir, binary_name)],
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=work_dir
        )
        stdout, stderr = run_process.communicate(input=input_string)
        run_process.wait()

        if run_process.returncode != 0:
            raise Exception(f"Runtime error: {stderr}")

        return "".join(stdout.split())



class PaizaIO:
    api_key = "guest"
    headers = {}

    @staticmethod
    def send_request(code, language, stdin=None, options=None):
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
    def check_status(result_id: str):
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
    def terminal_output(result_id: str):
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
    def __init__(self, mid, inputs, outputs, code, language):
        self.mid = mid
        self.inputs = inputs
        self.outputs = outputs
        self.code = code
        self.language = language

    def precheck(self):
        print(self.inputs, self.outputs)
        first_input, first_output = self.inputs[0], self.outputs[0]

        output = self.send(first_input)
        print(output)
        print(output, first_output, "Precheck", first_input, first_output)
        if output == first_output:
            return "Correct code"
        elif output == "":
            return "Error code"
        else:
            return "Incorrect code"

    def check(self):
        # for index in range(len(self.inputs)):
        #     print("Print running test", index+1)
        #     file_input, file_output = self.inputs[index], self.outputs[index]
        #     output = self.send(file_input)
        #     print(output, index+1, "|", file_input, file_output)
        #     if output != file_output:
        #         return "Incorrect code"
        #     elif output == "":
        #         return "Error code"
        # return "Correct code"

        folder = DFILES / f"fl{self.mid}"
        folder.mkdir(exist_ok=True)
        script_file = str(folder / 'script.file')

        if hasattr(RunCmdGenerator, self.language):
            try:
                with open(script_file, 'w') as file:
                    file.write(self.code)

                func = getattr(RunCmdGenerator, self.language)

                for index in range(len(self.inputs)):
                    file_input, file_output = self.inputs[index], self.outputs[index]
                    output = func(script_file, file_input)
                    print(output, file_output)
                    if output == "":
                        shutil.rmtree(str(folder))
                        return "Error code"
                    elif output != file_output:
                        shutil.rmtree(str(folder))
                        return "Incorrect code"
                shutil.rmtree(str(folder))
                return "Correct code"
            except:
                shutil.rmtree(str(folder))
                return "Error code"
        shutil.rmtree(str(folder))

    def send(self, stdin):
        print(self.code)
        print(stdin)
        print(self.language)
        request_id = PaizaIO.send_request(self.code, self.language, stdin)
        while PaizaIO.check_status(request_id) != "completed":
            time.sleep(1)
            print(PaizaIO.check_status(request_id))
        print(PaizaIO.terminal_output(request_id))
        return PaizaIO.terminal_output(request_id).get("stdout").strip('\n').strip()

