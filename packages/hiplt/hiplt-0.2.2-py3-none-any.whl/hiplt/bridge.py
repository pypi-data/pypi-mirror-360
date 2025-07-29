# hiplt/bridge.py

import subprocess
import os

def call_java(jar_file, class_name, method=None, args=[]):
    # Если нужно вызвать конкретный метод, его можно передать в args
    cmd = ["java", "-cp", jar_file, class_name]
    if method:
        cmd.append(method)
    cmd.extend(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Ошибка: {e.stderr}"

def call_cpp(source_file, args=[]):
    exe_file = "temp_exe"
    # Компиляция
    compile_cmd = ["g++", source_file, "-o", exe_file]
    try:
        subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return f"Ошибка компиляции: {e.stderr}"

    # Запуск
    run_cmd = [f"./{exe_file}"] + args
    try:
        result = subprocess.run(run_cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Ошибка выполнения: {e.stderr}"
    finally:
        if os.path.exists(exe_file):
            os.remove(exe_file)

def call_csharp(assembly_file, args=[]):
    # dotnet должен быть установлен
    cmd = ["dotnet", assembly_file] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Ошибка: {e.stderr}"