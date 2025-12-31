import sys
import os
import json
import queue
import tempfile
import subprocess
import threading
import requests
import zipfile
import time
import atexit
from pathlib import Path
import pandas as pd
import webbrowser
import platform

from typing import Tuple, List

from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                               QFileDialog, QListWidgetItem, QListWidget,
                               QSizePolicy, QProgressDialog, QVBoxLayout,
                               QLabel, QDialog, QDialogButtonBox, QHBoxLayout,
                               QPlainTextEdit, QPushButton, QCheckBox)
from PySide6.QtCore import QThread, QObject, QTimer, Signal, Qt, QUrl
from PySide6.QtGui import QDesktopServices

# 根据你的导入方式选择
# from deepseek import DeepSeek
# from GUI import Ui_MainWindow
from .deepseek import DeepSeek
from .GUI import Ui_MainWindow


# =====================================================
# 表格文件处理函数
# =====================================================
def get_table_preview(file_path: str, max_rows: int = 15) -> str:
    """
    获取表格文件的前几行预览
    支持的文件格式：.xlsx, .xls, .csv, .tsv, .txt
    返回格式化的字符串
    """
    try:
        # 根据文件扩展名选择读取方式
        ext = os.path.splitext(file_path)[1].lower()

        if ext in ['.xlsx', '.xls']:
            # 读取Excel文件
            df = pd.read_excel(file_path, nrows=max_rows)
        elif ext == '.csv':
            # 读取CSV文件
            df = pd.read_csv(file_path, nrows=max_rows)
        elif ext == '.tsv':
            # 读取TSV文件
            df = pd.read_csv(file_path, sep='\t', nrows=max_rows)
        elif ext in ['.txt', '.data']:
            # 尝试读取文本文件
            try:
                df = pd.read_csv(file_path, nrows=max_rows)
            except:
                # 如果标准读取失败，尝试读取前几行纯文本
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = [f.readline().strip() for _ in range(max_rows)]
                    lines = [line for line in lines if line]
                return f"文本文件前{len(lines)}行预览：\n" + "\n".join(lines)
        else:
            return f"不支持的文件格式：{ext}"

        # 获取实际行数
        actual_rows = min(len(df), max_rows)

        # 构建预览字符串
        preview_lines = []
        preview_lines.append(f"表格文件：{os.path.basename(file_path)}")
        preview_lines.append(f"总行数：{len(df)}，列数：{len(df.columns)}")
        preview_lines.append(f"前{actual_rows}行数据预览：")
        preview_lines.append("=" * 50)
        
        # 添加数据行
        preview_lines.append(df.to_string(index=False))
        
        return "\n".join(preview_lines)

    except Exception as e:
        return f"读取表格文件时出错：{str(e)}"


def get_file_preview(file_path: str) -> str:
    """
    根据文件类型获取预览信息
    返回：
    1. 对于表格文件：返回 "文件路径：{file_path}\n{preview}\n请注意数据的格式，数据可能是文本格式需要进行转换\n"
    2. 对于非表格文件：只返回文件绝对路径
    """
    # 支持的表格文件扩展名
    table_extensions = ['.xlsx', '.xls', '.csv', '.tsv', '.txt', '.data']

    ext = os.path.splitext(file_path)[1].lower()

    if ext in table_extensions:
        preview = get_table_preview(file_path)
        return f"文件路径：{file_path}\n{preview}\n请注意数据的格式，数据可能是文本格式需要进行转换\n"
    else:
        # 非表格文件，只返回绝对路径
        return f"\n{file_path}"


# =====================================================
# stdout / stderr 行缓冲重定向
# =====================================================
class EmittingStream:
    def __init__(self, log_queue: queue.Queue):
        self.log_queue = log_queue
        self._buffer = ""

    def write(self, text):
        if not text:
            return

        self._buffer += text

        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                self.log_queue.put(line)

    def flush(self):
        if self._buffer.strip():
            self.log_queue.put(self._buffer)
        self._buffer = ""


# =====================================================
# 升级 Worker（负责在后台下载和解压）
# =====================================================
class UpgradeWorker(QObject):
    """后台升级工作者 - 只负责下载和解压"""
    progress_signal = Signal(str)  # 进度更新信号
    finished_signal = Signal(bool, str, str)  # 完成信号：成功/失败, 消息, 临时目录路径
    canceled_signal = Signal()  # 取消信号

    def __init__(self):
        super().__init__()
        self._stop_flag = False

    def stop(self):
        """停止升级"""
        self._stop_flag = True
        self.progress_signal.emit("🛑 Stopping upgrade...")

    def run(self):
        """执行升级任务 - 只下载和解压"""
        temp_dir = None
        try:
            # GitHub 上 DumbyDraw 的源码 zip 包 URL
            url = 'https://github.com/Masterchiefm/DumbyDraw/archive/refs/heads/main.zip'

            self.progress_signal.emit("🔗 Connecting to GitHub...")
            if self._stop_flag:
                self.finished_signal.emit(False, "Upgrade canceled", "")
                return

            # 下载源代码压缩包
            self.progress_signal.emit("📥 Downloading update package...")
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code != 200:
                self.finished_signal.emit(False, f"Download failed, status code: {response.status_code}", "")
                return

            # 获取总大小
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            # 创建临时目录存储下载的压缩包
            temp_dir = tempfile.mkdtemp(prefix="dumbydraw_upgrade_")
            zip_file_path = os.path.join(temp_dir, 'DumbyDraw.zip')

            with open(zip_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._stop_flag:
                        self.finished_signal.emit(False, "Upgrade canceled", "")
                        return

                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            self.progress_signal.emit(f"📥 Downloading: {percent:.1f}%")

            if self._stop_flag:
                self.finished_signal.emit(False, "Upgrade canceled", "")
                return

            self.progress_signal.emit("📦 Extracting files...")

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            self.progress_signal.emit("✅ Download and extraction complete")

            # 获取解压后的路径
            extracted_dir = os.path.join(temp_dir, 'DumbyDraw-main')
            self.finished_signal.emit(True, "✅ Download and extraction complete", extracted_dir)

        except requests.RequestException as e:
            self.finished_signal.emit(False, f"❌ Network error: {e}", "")
        except Exception as e:
            self.finished_signal.emit(False, f"❌ Error during upgrade: {e}", "")
            # 清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass


# =====================================================
# 升级对话框
# =====================================================
class UpgradeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Software Upgrade")
        self.setModal(True)
        self.resize(600, 500)

        layout = QVBoxLayout()

        self.status_label = QLabel("Preparing for upgrade...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        # 使用QPlainTextEdit代替QLabel，支持复制
        layout.addWidget(QLabel("Installation Instructions:"))
        self.instructions_text = QPlainTextEdit()
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setMinimumHeight(200)
        layout.addWidget(self.instructions_text)

        # 自动运行选项
        self.auto_run_checkbox = QCheckBox("Automatically run upgrade script after closing")
        self.auto_run_checkbox.setChecked(True)
        layout.addWidget(self.auto_run_checkbox)

        # 按钮
        button_layout = QHBoxLayout()
        
        # 复制按钮
        self.copy_button = QPushButton("Copy Instructions")
        self.copy_button.clicked.connect(self.copy_instructions)
        button_layout.addWidget(self.copy_button)
        
        # 打开文件夹按钮
        self.open_folder_button = QPushButton("Open Download Folder")
        self.open_folder_button.clicked.connect(self.open_download_folder)
        self.open_folder_button.setEnabled(False)
        button_layout.addWidget(self.open_folder_button)
        
        button_layout.addStretch()
        
        self.close_button = QDialogButtonBox(QDialogButtonBox.Close)
        self.close_button.clicked.connect(self.close)
        self.close_button.hide()
        
        self.cancel_button = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.cancel_button.clicked.connect(self.cancel_upgrade)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.upgrade_worker = None
        self.upgrade_thread = None
        self.upgrade_canceled = False
        self.extracted_dir = ""
        self.script_path = ""
        self.python_path = sys.executable

    def start_upgrade(self):
        """开始升级过程"""
        self.upgrade_thread = QThread()
        self.upgrade_worker = UpgradeWorker()
        self.upgrade_worker.moveToThread(self.upgrade_thread)

        # 连接信号
        self.upgrade_worker.progress_signal.connect(self.update_progress)
        self.upgrade_worker.finished_signal.connect(self.upgrade_finished)
        self.upgrade_thread.started.connect(self.upgrade_worker.run)

        # 启动线程
        self.upgrade_thread.start()

    def update_progress(self, message):
        """更新进度显示"""
        self.progress_label.setText(message)

    def upgrade_finished(self, success, message, extracted_dir):
        """升级完成"""
        if success:
            self.extracted_dir = extracted_dir
            self.status_label.setText("✅ Download and extraction complete")
            self.progress_label.setText(message)
            
            # 获取Python路径
            python_path = sys.executable
            
            # 修复：使用正确的字符串格式化方法
            if os.name == 'nt':  # Windows
                # 创建升级脚本
                self.create_windows_upgrade_script(extracted_dir, python_path)
                
                instructions = f"""✅ Download and extraction complete!

UPDATE INSTRUCTIONS:

Python Path: {python_path}
Extracted Directory: {extracted_dir}

1. 请自行关闭所有DumbyDraw窗口
2. Windows 会在窗口关了后自动运行升级
   OR
   手动运行该命令：{self.script_path}

脚本详情：
- 该脚本将使用当前的 Python 环境安装或升级 DumbyDraw
- 脚本会在新的终端窗口中运行，以便您能看到进度
- 安装完成后，请重新启动 DumbyDraw 使用新版本

自动升级：
✓ 选中复选框：关闭此窗口时脚本将自动运行
✓ 未选中时脚本将手动运行

重要事项：
- 在运行脚本之前，请确保完全关闭 DumbyDraw
- 如果出现权限错误，您可能需要以管理员身份运行
"""
                
            else:  # macOS/Linux
                # 创建升级脚本
                self.create_unix_upgrade_script(extracted_dir, python_path)
                
                instructions = f"""✅ Download and extraction complete!

UPDATE INSTRUCTIONS:

Python Path: {python_path}
Extracted Directory: {extracted_dir}

1. Close DumbyDraw program
2. Open Terminal
3. Make script executable: chmod +x "{self.script_path}"
4. Run script: "{self.script_path}"

Or run directly:
"{python_path}" -m pip install --upgrade "{extracted_dir}"

After installation, restart DumbyDraw to use the new version.
"""
            
            self.instructions_text.setPlainText(instructions)
            self.open_folder_button.setEnabled(True)
            
        else:
            self.status_label.setText("❌ Upgrade failed")
            self.progress_label.setText(message)
            self.instructions_text.setPlainText("Please check your network connection and try again.")

        # 显示关闭按钮，隐藏取消按钮
        self.cancel_button.hide()
        self.close_button.show()

        # 清理线程
        if self.upgrade_thread:
            self.upgrade_thread.quit()
            self.upgrade_thread.wait()

    def create_windows_upgrade_script(self, extracted_dir, python_path):
        """创建Windows升级脚本（使用当前Python环境）"""
        script_path = os.path.join(extracted_dir, "install_upgrade.bat")
        self.script_path = script_path
        
        # 对路径进行转义处理
        python_path_escaped = python_path.replace('"', '""')
        extracted_dir_escaped = extracted_dir.replace('"', '""')
        
        script_content = f"""@echo off
echo ========================================
echo   DumbyDraw Upgrade Installation Script
echo ========================================
echo.
echo Using Python: {python_path}
echo Installing DumbyDraw from: {extracted_dir}
echo.

REM 使用当前Python环境的pip进行安装
echo Checking Python installation...
if not exist "{python_path_escaped}" (
    echo ERROR: Python not found at: {python_path}
    pause
    exit /b 1
)

echo Installing/upgrading DumbyDraw...
taskkill /F /IM DumbDrawPhD.exe 2>nul
taskkill /F /IM DumbDrawPhD*.exe 2>nul
taskkill /F /IM DumbyDraw.exe 2>nul
taskkill /F /IM DumbyDraw*.exe 2>nul
"{python_path_escaped}" -m pip install --upgrade "{extracted_dir_escaped}"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ||======================================||
    echo ||  Installation complete! You can now restart DumbyDraw. ||
    echo ||======================================||
    echo.
    echo If you encounter any issues, try running as Administrator.
) else (
    echo.
    echo ||================================================||
    echo ||  Installation failed, please check the error above! ||
    echo ||================================================||
    echo.
    echo Troubleshooting steps:
    echo 1. Make sure DumbyDraw is completely closed
    echo 2. Try running this script as Administrator
    echo 3. Try running: "{python_path}" -m pip install --upgrade "{extracted_dir}"
)

echo Press any key to exit...
pause >nul
"""
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        self.progress_label.setText(f"📜 Upgrade script created: {script_path}")

    def create_unix_upgrade_script(self, extracted_dir, python_path):
        """创建Unix/Linux升级脚本（使用当前Python环境）"""
        script_path = os.path.join(extracted_dir, "install_upgrade.sh")
        self.script_path = script_path
        
        script_content = f"""#!/bin/bash

echo "========================================"
echo "  DumbyDraw Upgrade Installation Script"
echo "========================================"
echo ""
echo "Using Python: {python_path}"
echo "Installing DumbyDraw from: {extracted_dir}"
echo ""

# 检查Python是否存在
if [ ! -f "{python_path}" ]; then
    echo "ERROR: Python not found at: {python_path}"
    exit 1
fi

# 使用当前Python环境的pip进行安装
echo "Installing/upgrading DumbyDraw..."
"{python_path}" -m pip install --upgrade "{extracted_dir}"

if [ $? -eq 0 ]; then
    echo ""
    echo "||======================================||"
    echo "||  Installation complete! You can now restart DumbyDraw. ||"
    echo "||======================================||"
    echo ""
else
    echo ""
    echo "||================================================||"
    echo "||  Installation failed, please check the error above! ||"
    echo "||================================================||"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Make sure DumbyDraw is completely closed"
    echo "2. Try running with sudo if needed"
    echo "3. Try running: \\"{python_path}\\" -m pip install --upgrade \\"{extracted_dir}\\""
fi

echo "Press Enter to exit..."
read -r
"""
        
        # 给脚本添加执行权限
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        self.progress_label.setText(f"📜 Upgrade script created: {script_path}")

    def copy_instructions(self):
        """复制安装说明到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.instructions_text.toPlainText())
        self.progress_label.setText("✅ Instructions copied to clipboard!")

    def open_download_folder(self):
        """打开下载文件夹"""
        if self.extracted_dir and os.path.exists(self.extracted_dir):
            if platform.system() == "Windows":
                os.startfile(self.extracted_dir)
            elif platform.system() == "Darwin":
                subprocess.run(["open", self.extracted_dir])
            else:
                subprocess.run(["xdg-open", self.extracted_dir])

    def cancel_upgrade(self):
        """取消升级"""
        self.upgrade_canceled = True
        if self.upgrade_worker:
            self.upgrade_worker.stop()
        self.reject()

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 如果选择了自动运行，则在关闭时运行升级脚本
        if self.auto_run_checkbox.isChecked() and self.script_path and os.path.exists(self.script_path):
            self.run_upgrade_script()
        super().closeEvent(event)

    def run_upgrade_script(self):
        """运行升级脚本（在外部进程中）"""
        try:
            if platform.system() == "Windows":
                # 对于Windows，使用start命令在新窗口中运行
                subprocess.Popen(f'start "" cmd /k "{self.script_path}"', shell=True)
                self.progress_label.setText("🚀 Upgrade script is running in a new window...")
            else:
                # 对于macOS/Linux，在终端中运行
                if platform.system() == "Darwin":
                    # macOS使用open命令打开终端
                    subprocess.Popen(['osascript', '-e', f'tell app "Terminal" to do script "bash \\"{self.script_path}\\""'])
                else:
                    # Linux使用x-terminal-emulator
                    subprocess.Popen(['x-terminal-emulator', '-e', f'bash "{self.script_path}"'])
                self.progress_label.setText("🚀 Upgrade script is running in a new terminal...")
        except Exception as e:
            print(f"Error running upgrade script: {e}")


# =====================================================
# 后台 Worker（负责生成代码）
# =====================================================
class AnalyseWorker(QObject):
    def __init__(self, baseurl, model, api_key, user_query, system_prompt, result_queue):
        super().__init__()
        self.baseurl = baseurl
        self.model = model
        self.api_key = api_key
        self.user_query = user_query
        self.system_prompt = system_prompt
        self.result_queue = result_queue
        self._stop_flag = False
        self.client = None

    def stop(self):
        """停止AI生成"""
        self._stop_flag = True
        print("🛑 正在停止AI生成...")

    def run(self):
        try:
            print("🚀 开始调用 AI 接口")

            if self._stop_flag:
                print("⏹️ AI生成已被停止")
                return

            self.client = DeepSeek(
                base_url=self.baseurl,
                model=self.model,
                API_key=self.api_key
            )

            if self._stop_flag:
                print("⏹️ AI生成已被停止")
                return

            code = self.client.get_response(
                query=self.user_query,
                prompt=self.system_prompt,
                return_type="string",
                model=self.model
            )

            if self._stop_flag:
                print("⏹️ AI生成已被停止")
                return

            print("✅ AI 返回完成，开始清理代码")

            code = code.strip()
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]

            if not self._stop_flag:
                self.result_queue.put(code)
                print("📦 代码已发送回主线程")

        except Exception as e:
            if not self._stop_flag:
                print(f"❌ 后台异常: {e}")


# =====================================================
# 代码执行 Worker（在后台进程中执行代码）
# =====================================================
class CodeRunner:
    def __init__(self, log_queue: queue.Queue):
        self.log_queue = log_queue
        self.process = None
        self.running = False
        self._stop_flag = False

    def run_code_in_background(self, code: str):
        """在后台进程中执行代码"""
        if self.running:
            return

        self.running = True
        self._stop_flag = False
        thread = threading.Thread(target=self._execute_code, args=(code,))
        thread.daemon = True
        thread.start()

    def _execute_code(self, code: str):
        """实际执行代码的方法"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file_path = f.name

            self.log_queue.put(f"📝 临时文件已创建: {temp_file_path}")

            python_exe = sys.executable
            self.log_queue.put(f"🐍 使用Python解释器: {python_exe}")

            if self._stop_flag:
                self.log_queue.put("⏹️ 代码执行已被取消")
                self._cleanup_temp_file(temp_file_path)
                return

            self.log_queue.put(f"⏹️ 代码正在后台运行...")
            self.process = subprocess.Popen(
                [python_exe, temp_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )

            while True:
                if self._stop_flag:
                    self.log_queue.put("⏹️ 正在停止代码执行...")
                    self.process.terminate()
                    break

                stdout_line = self.process.stdout.readline()
                if stdout_line:
                    self.log_queue.put(stdout_line.rstrip('\n'))

                stderr_line = self.process.stderr.readline()
                if stderr_line:
                    e = stderr_line.rstrip('\n')
                    self.log_queue.put(f"❌ {e}")

                if self.process.poll() is not None:
                    for line in self.process.stdout.readlines():
                        if line.strip():
                            self.log_queue.put(line.rstrip('\n'))
                    for line in self.process.stderr.readlines():
                        if line.strip():
                            e = line.rstrip('\n')
                            self.log_queue.put(f"❌ {e}")
                    break

            if not self._stop_flag:
                return_code = self.process.wait()
                if return_code == 0:
                    self.log_queue.put("✅ 代码执行完成")
                else:
                    self.log_queue.put(f"❌ 代码执行失败，返回码: {return_code}")

        except Exception as e:
            self.log_queue.put(f"❌ 执行代码时发生错误: {e}")
        finally:
            self.running = False
            self.process = None

    def _cleanup_temp_file(self, temp_file_path: str):
        """清理临时文件"""
        try:
            os.unlink(temp_file_path)
            self.log_queue.put(f"🗑️ 临时文件已删除: {temp_file_path}")
        except Exception as e:
            self.log_queue.put(f"⚠️ 无法删除临时文件: {e}")

    def stop_execution(self):
        """停止正在执行的代码"""
        if self.running:
            self._stop_flag = True
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.log_queue.put("⏹️ 代码执行已停止")


class FileDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(False)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path and not self._is_in_list(path):
                self.addItem(QListWidgetItem(path))
        event.acceptProposedAction()

    def _is_in_list(self, path: str) -> bool:
        for i in range(self.count()):
            if self.item(i).text() == path:
                return True
        return False


# =====================================================
# 主窗口
# =====================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__version__ = "1.5"  # 更新版本号
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.get_config()

        # ===== 队列 =====
        self.log_queue = queue.Queue()
        self.result_queue = queue.Queue()

        # stdout / stderr 重定向
        sys.stdout = EmittingStream(self.log_queue)
        sys.stderr = EmittingStream(self.log_queue)

        # ===== 代码执行器 =====
        self.code_runner = CodeRunner(self.log_queue)

        # ===== AI生成相关 =====
        self.ai_worker = None
        self.ai_thread = None

        # ===== 升级相关 =====
        self.upgrade_dialog = None

        # ===== 定时器 =====
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.start(100)

        self.result_timer = QTimer(self)
        self.result_timer.timeout.connect(self.check_result)
        self.result_timer.start(100)

        # 更新文件列表小部件
        old_widget = self.ui.listWidget_files
        parent = old_widget.parent()
        layout = parent.layout()

        new_widget = FileDropListWidget(parent)
        new_widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        layout.replaceWidget(old_widget, new_widget)
        old_widget.deleteLater()
        self.ui.listWidget_files = new_widget

        # ===== 隐藏修改代码区域 ====
        self.ui.frame_edit_code.hide()

        # ===== 按钮 =====
        self.ui.pushButton_save_api.clicked.connect(self.save_config)
        self.ui.pushButton_analyse.clicked.connect(self.generate_code)
        self.ui.radioButton_edit_code.clicked.connect(self.show_edit_code)
        self.ui.pushButton_run_code.clicked.connect(self.direct_run)
        self.ui.pushButton_import.clicked.connect(self.import_files)
        self.ui.pushButton_remove.clicked.connect(self.remove_selection)
        self.ui.pushButton_send_edit_query.clicked.connect(self.edit_code)
        self.ui.pushButton_test_api.clicked.connect(self.check_connection)
        self.ui.pushButton_stop.clicked.connect(self.stop_all_processes)
        self.ui.actionupdate.triggered.connect(self.upgrade)

        # 显示版本号
        self.setWindowTitle(f"DumbyDraw v{self.__version__}")

        self.system_prompt = """你是一个python绘图代码生成工具，你能根据用户的输入直接生成代码。
你输出的内容只能有完整的代码，不能有代码之外的其它东西。
输出必须是 markdown ``` ``` 包裹的代码，之外不能有任何说明，说明只能是代码里的注释。
禁止 if __name__ == "__main__",代码结尾不要带plt.close()，即使保存了图片，也要plt.show().尽量只有一次plt.show(), 或者把需要生成的图做成一张大图和几张子图。
除非用户指定了其它语言或者字体，否则务必使用英文作为图注、图题。
代码中的注释与用户输入的语言一致
注意用户输入的第几第几是人类语言，是从1开始，而不是python的从0开始。
你代码中可以用python内置工具以及以下的第三方工具：
matplotlib==3.7.5
seaborn
pandas
openpyxl
pillow
requests
biopython
numpy
scipy
cartopy
你需要检查用的工具不在上表，如果不在，你需要在代码中使用try import，并在except中用sys.executable获取python路径，然后用python -m pip安装。并且指定用清华源https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
"""

    def upgrade(self):
        """在后台执行升级（只下载和解压，不安装）"""
        print("🔄 Starting upgrade...")

        # 创建并显示升级对话框
        self.upgrade_dialog = UpgradeDialog(self)
        self.upgrade_dialog.start_upgrade()
        result = self.upgrade_dialog.exec_()

        # 对话框关闭后清理
        if self.upgrade_dialog.upgrade_canceled:
            print("⏹️ Upgrade canceled")
        else:
            print("✅ Upgrade files ready")

        self.upgrade_dialog = None

    def detect_table_files(self):
        """
        检测列表中的文件是否是表格文件，并读取前15行内容
        返回包含表格信息的字典
        """
        table_info = {}
        files = [self.ui.listWidget_files.item(i).text() for i in range(self.ui.listWidget_files.count())]
        
        for file_path in files:
            # 检查文件扩展名是否是常见的表格文件
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in ['.csv', '.xlsx', '.xls', '.xlsm', '.xlsb', '.ods', '.tsv']:
                try:
                    print(f"📊 检测到表格文件: {file_path}")
                    
                    # 根据文件扩展名选择读取方式
                    if file_ext == '.csv':
                        # 尝试读取前5行
                        df = pd.read_csv(file_path, nrows=15)
                    elif file_ext in ['.xlsx', '.xls', '.xlsm', '.xlsb']:
                        # Excel文件读取第一个工作表的前15行
                        df = pd.read_excel(file_path, nrows=15, engine='openpyxl')
                    elif file_ext == '.ods':
                        # ODS文件
                        df = pd.read_excel(file_path, nrows=15, engine='odf')
                    elif file_ext == '.tsv':
                        # TSV文件
                        df = pd.read_csv(file_path, sep='\t', nrows=15)
                    else:
                        continue
                    
                    # 获取表格信息
                    num_rows, num_cols = df.shape
                    # columns = df.columns.tolist()
                    
                    # 将DataFrame转换为字符串表示
                    df_str = df.to_string(index=False)
                    
                    table_info[file_path] = {
                        'path': file_path,
                        'rows': num_rows,
                        'columns': num_cols,
                        'preview': df_str
                    }
                    
                    print(f"✅ 成功读取表格文件: {file_path} ({num_rows}行, {num_cols}列)")
                    
                except Exception as e:
                    print(f"⚠️ 读取表格文件 {file_path} 时出错: {e}")
                    # 如果文件不是有效的表格，继续下一个文件
                    continue
            else:
                table_info[file_path] = {
                    'path':file_path
                }
        return table_info

    def stop_all_processes(self):
        """停止所有正在运行的进程"""
        print("🛑 正在停止所有进程...")

        # 停止AI生成
        self.stop_ai_generation()

        # 停止代码执行
        self.stop_code_execution()

        # 停止升级（如果有）
        if self.upgrade_dialog and self.upgrade_dialog.upgrade_worker:
            self.upgrade_dialog.upgrade_worker.stop()

        print("✅ 已发送停止信号")

    def stop_ai_generation(self):
        """停止AI代码生成"""
        if self.ai_worker:
            self.ai_worker.stop()
            print("⏹️ AI生成已停止")

        if self.ai_thread and self.ai_thread.isRunning():
            self.ai_thread.quit()
            self.ai_thread.wait(1000)
            if self.ai_thread.isRunning():
                self.ai_thread.terminate()
            print("🧵 AI线程已停止")

        self.ai_worker = None
        self.ai_thread = None

    def stop_code_execution(self):
        """停止代码执行"""
        self.code_runner.stop_execution()

    def add_drag_file(self):
        """已通过dropEvent实现"""
        pass

    def build_file_previews(self, file_paths: List[str]) -> str:
        """
        构建文件预览信息
        返回：包含所有文件路径和表格预览的字符串
        """
        if not file_paths:
            return ""

        preview_parts = ["用户提供了以下文件，请根据需要读取："]

        for i, file_path in enumerate(file_paths, 1):
            preview = get_file_preview(file_path)
            # 检查是否为表格文件（包含预览内容）
            if os.path.splitext(file_path)[1].lower() in ['.xlsx', '.xls', '.csv', '.tsv', '.txt', '.data']:
                preview_parts.append(f"\n【文件{i}】")
                preview_parts.append(preview)
            else:
                # 非表格文件，只显示路径
                preview_parts.append(f"\n【文件{i}】")
                preview_parts.append(f"文件路径：{preview}")

        return "\n".join(preview_parts)

    def edit_code(self):
        original_code = self.ui.plainTextEdit_code.toPlainText()
        user_query = self.ui.plainTextEdit_query.toPlainText()
        system_prompt = self.system_prompt
        table_info = self.detect_table_files()
        if table_info:
            system_prompt += "\n\n用户上传的文件信息如下：\n"
            for file_path, info in table_info.items():
                system_prompt += f"\n文件：{file_path}\n"
                print(f"\n文件：{file_path}\n")
                try:
                    system_prompt += f"数据维度：{info['rows']}行 x {info['columns']}列\n"
                    system_prompt += f"前15行数据预览：\n{info['preview']}\n"
                    print(f"前15行数据预览：\n{info['preview']}\n")
                except:
                    print(f"{file_path}非表格数据")
                
                
                
        edit_query = self.ui.plainTextEdit_edit_query.toPlainText()
        user_query = f"你需要修改代码，这是原始需求：{user_query}, 这是原始代码：{original_code},这是修改的需求：{edit_query}"

        print("🧵 启动后台线程")

        self.ai_thread = QThread(self)
        self.ai_worker = AnalyseWorker(
            self.baseurl,
            self.model,
            self.api_key,
            user_query,
            system_prompt,
            self.result_queue
        )

        self.ai_worker.moveToThread(self.ai_thread)
        self.ai_thread.started.connect(self.ai_worker.run)
        self.ai_thread.start()

    def import_files(self):
        """导入文件"""
        file_urls, _ = QFileDialog.getOpenFileUrls(self, "选择文件")
        for url in file_urls:
            path = url.toLocalFile()
            if path and not self.is_in_list(path):
                item = QListWidgetItem(path)
                self.ui.listWidget_files.addItem(item)

    def is_in_list(self, path):
        for i in range(self.ui.listWidget_files.count()):
            if self.ui.listWidget_files.item(i).text() == path:
                return True
        return False

    def remove_selection(self):
        """移除选中的文件"""
        for item in self.ui.listWidget_files.selectedItems():
            self.ui.listWidget_files.takeItem(self.ui.listWidget_files.row(item))

    def show_edit_code(self):
        if self.ui.radioButton_edit_code.isChecked():
            self.ui.frame_edit_code.show()
        else:
            self.ui.frame_edit_code.hide()

    def update_log(self):
        lines = []
        while not self.log_queue.empty():
            lines.append(self.log_queue.get())

        if lines:
            self.ui.textBrowser_log.append("\n".join(lines))

    def check_result(self):
        if self.result_queue.empty():
            return

        code = self.result_queue.get()
        self.ui.plainTextEdit_code.setPlainText(code)

        try:
            self.code_runner.run_code_in_background(code)
        except Exception as e:
            print(e)

    def direct_run(self):
        code = self.ui.plainTextEdit_code.toPlainText()
        print("▶ 在后台进程中执行代码")
        self.code_runner.run_code_in_background(code)

    def generate_code(self):
        user_query = self.ui.plainTextEdit_query.toPlainText()
        system_prompt = self.system_prompt + "注意需要使用的包是否需要安装"
        table_info = self.detect_table_files()
        if table_info:
            system_prompt += "\n\n用户上传的文件信息如下：\n"
            for file_path, info in table_info.items():
                system_prompt += f"\n文件：{file_path}\n"
                print(f"\n文件：{file_path}\n")
                try:
                    system_prompt += f"数据维度：{info['rows']}行 x {info['columns']}列\n"
                    system_prompt += f"前15行数据预览：\n{info['preview']}\n"
                    print(f"前15行数据预览：\n{info['preview']}\n")
                except:
                    print(f"{file_path}非表格数据")

        print("🧵 启动后台线程")
        self.stop_ai_generation()

        self.ai_thread = QThread(self)
        self.ai_worker = AnalyseWorker(
            self.baseurl,
            self.model,
            self.api_key,
            user_query,
            system_prompt,
            self.result_queue
        )

        self.ai_worker.moveToThread(self.ai_thread)
        self.ai_thread.started.connect(self.ai_worker.run)
        self.ai_thread.start()

    def get_config(self) -> Tuple[str, str, str]:
        config_path = os.path.expanduser("~/.dumbydraw_config.json")  # 简化了配置文件名

        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "baseurl": "",
                    "model": "",
                    "api_key": ""
                }, f, indent=4)

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        self.baseurl = cfg.get("baseurl", "")
        self.model = cfg.get("model", "")
        self.api_key = cfg.get("api_key", "")

        self.ui.lineEdit_baseurl.setText(self.baseurl)
        self.ui.lineEdit_model.setText(self.model)
        self.ui.lineEdit_key.setText(self.api_key)

    def save_config(self):
        try:
            config_path = os.path.expanduser("~/.dumbydraw_config.json")

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "baseurl": self.ui.lineEdit_baseurl.text(),
                    "model": self.ui.lineEdit_model.text(),
                    "api_key": self.ui.lineEdit_key.text()
                }, f, indent=4)
            print("✅ 配置保存成功")
            self.get_config()
        except Exception as e:
            print(f"❌ 保存失败: {e}")

    def check_connection(self):
        user_query = '画一个正弦函数'
        system_prompt = """你是一个python绘图代码生成工具，你能根据用户的输入直接生成代码。
           你输出的内容只能有代码，不能有代码之外的其它东西。
           输出必须是 markdown ``` ``` 包裹的代码。
           禁止 if __name__ == "__main__",代码结尾不要带plt.close()，即使保存了图片，也要plt.show()。尽量只有一个plt.show(),这样我才能把图都显示出来
           除非用户指定了其它语言或者字体，否则务必使用英文作为图注、图题。
           代码中的注释与用户输入的语言一致
           """

        print("🧵 启动后台线程")
        self.stop_ai_generation()

        self.ai_thread = QThread(self)
        self.ai_worker = AnalyseWorker(
            self.baseurl,
            self.model,
            self.api_key,
            user_query,
            system_prompt,
            self.result_queue
        )

        self.ai_worker.moveToThread(self.ai_thread)
        self.ai_thread.started.connect(self.ai_worker.run)
        self.ai_thread.start()


# =====================================================
# main
# =====================================================
def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
