import psutil
import tkinter as tk
import cpuinfo
import subprocess
from datetime import datetime
import platform

# Próbáljuk meg importálni az Nvidia NVML modult
try:
    import py3nvml.py3nvml as nvml
    nvml_available = True
except ImportError:
    nvml = None
    nvml_available = False

# Próbáljuk meg importálni az OpenCL modult
try:
    import pyopencl as cl
    opencl_available = True
except ImportError:
    cl = None
    opencl_available = False

def get_cpu_info():
    try:
        cpu_info = cpuinfo.get_cpu_info()
        return cpu_info['brand_raw']
    except Exception as e:
        return "N/A"

def get_cpu_usage():
    try:
        return psutil.cpu_percent(interval=1)
    except Exception as e:
        return "N/A"

def get_cpu_temperature():
    try:
        if platform.system() == 'Linux':
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
        return "N/A"
    except Exception as e:
        return "N/A"

def get_memory_info():
    try:
        mem = psutil.virtual_memory()
        total_mem = mem.total / (1024 ** 3)
        available_mem = mem.available / (1024 ** 3)
        return f"Total: {total_mem:.2f} GB\nAvailable: {available_mem:.2f} GB"
    except Exception as e:
        return "N/A"

def get_nvidia_gpu_info():
    try:
        if nvml_available:
            nvml.nvmlInit()
            handle = nvml.nvmlDeviceGetHandleByIndex(0)
            gpu_name = nvml.nvmlDeviceGetName(handle)
            nvml.nvmlShutdown()
            return gpu_name.decode('utf-8')
        return None
    except Exception as e:
        return "Nvidia GPU hiba"

def get_opencl_gpu_info():
    try:
        if opencl_available:
            platforms = cl.get_platforms()
            if platforms:
                devices = platforms[0].get_devices(device_type=cl.device_type.GPU)
                if devices:
                    return devices[0].name
        return None
    except Exception as e:
        return "OpenCL GPU hiba"

def get_gpu_info():
    nvidia_info = get_nvidia_gpu_info()
    if nvidia_info:
        return nvidia_info
    opencl_info = get_opencl_gpu_info()
    if opencl_info:
        return opencl_info
    return "Nincs támogatott GPU"

def get_nvidia_gpu_usage():
    try:
        if nvml_available:
            nvml.nvmlInit()
            handle = nvml.nvmlDeviceGetHandleByIndex(0)
            utilization = nvml.nvmlDeviceGetUtilizationRates(handle)
            nvml.nvmlShutdown()
            return f"{utilization.gpu}%"
        return None
    except Exception as e:
        return "Nvidia GPU hiba"

def get_gpu_info():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"GPU információ lekérdezési hiba: {e}")
        return "N/A"

def get_gpu_usage():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader'],
                                stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"GPU terheltség lekérdezési hiba: {e}")
        return "N/A"

def get_gpu_temperature():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader'],
                                stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"GPU hőmérséklet lekérdezési hiba: {e}")
        return "N/A"


# Tkinter ablak létrehozása
root = tk.Tk()
root.title("Device Monitor")
root.configure(bg='black')

# Szöveg widget létrehozása
text_widget = tk.Label(root, font=("Helvetica", 12), fg="white", bg="black", anchor='w', justify='left')
text_widget.pack(padx=20, pady=20)

def update_information():
    # Aktuális idő lekérése
    current_time = datetime.now().strftime("%H:%M")
    
    # Hardver információk lekérése
    cpu_info = get_cpu_info()
    cpu_usage = get_cpu_usage()
    cpu_temp = get_cpu_temperature()
    memory_info = get_memory_info()
    gpu_info = get_gpu_info()
    gpu_usage = get_gpu_usage()
    gpu_temp = get_gpu_temperature()
    
    # Szöveg frissítése
    text_widget.config(text=f"{current_time}\n\nCPU\nType: {cpu_info}\nUsage: {cpu_usage}%\nTemperature: {cpu_temp}°C\n\nMemory\n{memory_info}\n\nGPU\nType: {gpu_info}\nUsage: {gpu_usage}\nTemperature: {gpu_temp}°C")
    
    # Következő frissítés 1 másodperc múlva
    root.after(1000, update_information)

# Első frissítés
update_information()

# Tkinter ablak megjelenítése
root.mainloop()
