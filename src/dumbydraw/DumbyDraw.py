import sys
import os
import json
import queue
import tempfile
import subprocess
import threading
import signal
from importlib import import_module
from typing import Tuple

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QListWidgetItem, QListWidget, QSizePolicy, QPushButton
from PySide6.QtCore import QThread, QObject, QTimer

# from deepseek import DeepSeek
# from GUI import Ui_MainWindow
from .deepseek import DeepSeek
from .GUI import Ui_MainWindow

# =====================================================
# stdout / stderr 行缓冲重定向（关键修复点）
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
            # 与终端行为一致（保留空行可删 strip 判断）
            if line.strip():
                self.log_queue.put(line)

    def flush(self):
        if self._buffer.strip():
            self.log_queue.put(self._buffer)
        self._buffer = ""


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

            # 检查停止标志
            if self._stop_flag:
                print("⏹️ AI生成已被停止")
                return

            self.client = DeepSeek(
                base_url=self.baseurl,
                model=self.model,
                API_key=self.api_key
            )

            # 检查停止标志
            if self._stop_flag:
                print("⏹️ AI生成已被停止")
                return

            code = self.client.get_response(
                query=self.user_query,
                prompt=self.system_prompt,
                return_type="string"
            )

            # 检查停止标志
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

            # 检查停止标志
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
            self.log_queue.put("⚠️ 已有代码正在运行，请等待完成")
            return
            
        self.running = True
        self._stop_flag = False
        thread = threading.Thread(target=self._execute_code, args=(code,))
        thread.daemon = True
        thread.start()
    
    def _execute_code(self, code: str):
        """实际执行代码的方法"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file_path = f.name
            
            self.log_queue.put(f"📝 临时文件已创建: {temp_file_path}")
            
            # 获取Python解释器路径
            python_exe = sys.executable
            self.log_queue.put(f"🐍 使用Python解释器: {python_exe}")
            
            
            # 检查停止标志
            if self._stop_flag:
                self.log_queue.put("⏹️ 代码执行已被取消")
                self._cleanup_temp_file(temp_file_path)
                return
            
            # 启动子进程执行代码
            self.log_queue.put(f"⏹️ 代码正在后台运行...")
            self.process = subprocess.Popen(
                [python_exe, temp_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # 实时读取输出
            while True:
                # 检查停止标志
                if self._stop_flag:
                    self.log_queue.put("⏹️ 正在停止代码执行...")
                    self.process.terminate()
                    break
                
                # 读取标准输出
                stdout_line = self.process.stdout.readline()
                if stdout_line:
                    self.log_queue.put(stdout_line.rstrip('\n'))
                
                # 读取标准错误
                stderr_line = self.process.stderr.readline()
                if stderr_line:
                    self.log_queue.put(f"❌ {stderr_line.rstrip('\n')}")
                
                # 检查进程是否结束
                if self.process.poll() is not None:
                    # 读取剩余输出
                    for line in self.process.stdout.readlines():
                        if line.strip():
                            self.log_queue.put(line.rstrip('\n'))
                    for line in self.process.stderr.readlines():
                        if line.strip():
                            self.log_queue.put(f"❌ {line.rstrip('\n')}")
                    break
            
            # 检查停止标志
            if not self._stop_flag:
                # 获取返回码
                return_code = self.process.wait()
                if return_code == 0:
                    self.log_queue.put("✅ 代码执行完成")
                else:
                    self.log_queue.put(f"❌ 代码执行失败，返回码: {return_code}")
            
            # 清理临时文件
            # self._cleanup_temp_file(temp_file_path)
                
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
        self.__version__ = "1.4"
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

        # ===== 定时器 =====
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.start(100)

        self.result_timer = QTimer(self)
        self.result_timer.timeout.connect(self.check_result)
        self.result_timer.start(100)

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
        
        # ===== 添加停止按钮 =====
        self.setup_stop_buttons()

    def setup_stop_buttons(self):
        """设置停止按钮"""
        # 可以在UI中手动添加一个停止按钮，或者使用现有按钮
        # 这里展示两种方式：
        
        # 方式1：添加新的停止按钮（推荐）
        try:
            # 这里假设你在UI文件中已经添加了一个名为pushButton_stop的按钮
            self.ui.pushButton_stop.clicked.connect(self.stop_all_processes)
            self.ui.pushButton_stop.setEnabled(False)  # 初始不可用
        except AttributeError:
            # 如果UI中没有该按钮，可以动态创建一个
            self.stop_button = QPushButton("停止所有进程", self)
            self.stop_button.clicked.connect(self.stop_all_processes)
            self.stop_button.setEnabled(False)
            # 添加到现有布局中（这里需要根据你的UI结构调整位置）
            # 例如：self.ui.verticalLayout.addWidget(self.stop_button)
        
        # 方式2：复用现有按钮（在运行时切换）
        self.is_stopping = False

    def stop_all_processes(self):
        """停止所有正在运行的进程"""
        print("🛑 正在停止所有进程...")
        
        # 停止AI生成
        self.stop_ai_generation()
        
        # 停止代码执行
        self.stop_code_execution()
        
        print("✅ 已发送停止信号")

    def stop_ai_generation(self):
        """停止AI代码生成"""
        if self.ai_worker:
            self.ai_worker.stop()
            print("⏹️ AI生成已停止")
            
        if self.ai_thread and self.ai_thread.isRunning():
            # 等待线程安全结束
            self.ai_thread.quit()
            self.ai_thread.wait(1000)  # 等待1秒
            if self.ai_thread.isRunning():
                self.ai_thread.terminate()
            print("🧵 AI线程已停止")
            
        self.ai_worker = None
        self.ai_thread = None

    def stop_code_execution(self):
        """停止代码执行"""
        self.code_runner.stop_execution()

    def add_drag_file(self):
        """
        识别拖到self.ui.listWidget_files的文件/文件夹，获得它们的路径。然后把这些路径添加到self.ui.listWidget_files里
        :return:
        """
        pass  # 已在dropEvent中实现

    def edit_code(self):
        original_code = self.ui.plainTextEdit_code.toPlainText()
        user_query = self.ui.plainTextEdit_query.toPlainText()
        system_prompt = """你是一个python绘图代码生成工具，你能根据用户的输入直接生成代码。
        你输出的内容只能有代码，不能有代码之外的其它东西。
        输出必须是 markdown ``` ``` 包裹的代码。
        禁止 if __name__ == "__main__",代码结尾不要带plt.close()，即使保存了图片，也要plt.show()。
        除非用户指定了其它语言或者字体，否则务必使用英文作为图注、图题。
        代码中的注释与用户输入的语言一致
        """
        # 获取 listWidget_files 中的文件
        files = [self.ui.listWidget_files.item(i).text() for i in range(self.ui.listWidget_files.count())]
        if files:
            system_prompt += f"用户还提供了以下文件/文件夹和其路径，需要的时候在代码中写入读取对应文件的代码。路径如下：{files}"

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
        
        # 启用停止按钮
        self.enable_stop_button(True)

    def import_files(self):
        """
        打开一个文件选择窗口， 可以多选文件。然后返回这堆文件的绝对路径。
        然后将这个路径列表更新到ui.listwidget_files中
        """
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
        """
        读取现在ui.listwidget_files中选中了哪些item，然后将选中的item从列表中去除并更新列表。
        """
        for item in self.ui.listWidget_files.selectedItems():
            self.ui.listWidget_files.takeItem(self.ui.listWidget_files.row(item))

    def show_edit_code(self):
        if self.ui.radioButton_edit_code.isChecked():
            self.ui.frame_edit_code.show()
        else:
            self.ui.frame_edit_code.hide()

    # ---------------------
    # 按行刷新日志
    # ---------------------
    def update_log(self):
        lines = []
        while not self.log_queue.empty():
            lines.append(self.log_queue.get())

        if lines:
            self.ui.textBrowser_log.append("\n".join(lines))

    # ---------------------
    # 接收生成代码并执行
    # ---------------------
    def check_result(self):
        if self.result_queue.empty():
            return

        code = self.result_queue.get()
        self.ui.plainTextEdit_code.setPlainText(code)

        # 完成AI生成后禁用停止按钮
        self.enable_stop_button(False)
        
        # 检查是否需要自动执行
        try:
            if self.ui.checkBox_auto_execute.isChecked():
                print("▶ 在后台进程中执行生成代码")
                # 在后台进程中执行代码
                self.code_runner.run_code_in_background(code)
        except Exception as e:
            print(e)
            self.code_runner.run_code_in_background(code)


    def direct_run(self):
        code = self.ui.plainTextEdit_code.toPlainText()
        print("▶ 在后台进程中执行代码")
        # 在后台进程中执行代码
        self.code_runner.run_code_in_background(code)

    def enable_stop_button(self, enabled: bool):
        """启用或禁用停止按钮"""
        try:
            self.ui.pushButton_stop.setEnabled(enabled)
        except AttributeError:
            # 如果使用动态创建的按钮
            if hasattr(self, 'stop_button'):
                self.stop_button.setEnabled(enabled)

    # ---------------------
    # 启动后台分析
    # ---------------------
    def generate_code(self):
        user_query = self.ui.plainTextEdit_query.toPlainText()
        system_prompt = """你是一个python绘图代码生成工具，你能根据用户的输入直接生成代码。
你输出的内容只能有完整的代码，不能有代码之外的其它东西。
输出必须是 markdown ``` ``` 包裹的代码，之外不能有任何说明，说明只能是代码里的注释。
禁止 if __name__ == "__main__",代码结尾不要带plt.close()，即使保存了图片，也要plt.show()。
除非用户指定了其它语言或者字体，否则务必使用英文作为图注、图题。
代码中的注释与用户输入的语言一致
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
"""
        # 获取 listWidget_files 中的文件
        files = [self.ui.listWidget_files.item(i).text() for i in range(self.ui.listWidget_files.count())]
        if files:
            system_prompt += f"用户还提供了以下文件/文件夹和其路径，需要的时候在代码中写入读取对应文件的代码,并注意处理路径中的空格。路径如下：{files}"

        print("🧵 启动后台线程")

        # 停止可能正在进行的AI生成
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
        
        # 连接线程完成的信号
        self.ai_thread.started.connect(self.ai_worker.run)
        self.ai_thread.finished.connect(lambda: self.enable_stop_button(False))
        
        self.ai_thread.start()
        
        # 启用停止按钮
        self.enable_stop_button(True)

    # ---------------------
    # 配置文件
    # ---------------------
    def get_config(self) -> Tuple[str, str, str]:
        # 获取家目录下的配置文件路径
        config_path = os.path.expanduser("~/.dumbdrawphd_config.json")

        if not os.path.exists(config_path):
            # 确保家目录存在
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
            config_path = os.path.expanduser("~/.dumbdrawphd_config.json")

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
        """
        测试 API 连接：直接问 AI 你是谁，无需生成代码运行
        """
        user_query = '画一个正弦函数'
        system_prompt = """你是一个python绘图代码生成工具，你能根据用户的输入直接生成代码。
           你输出的内容只能有代码，不能有代码之外的其它东西。
           输出必须是 markdown ``` ``` 包裹的代码。
           禁止 if __name__ == "__main__",代码结尾不要带plt.close()，即使保存了图片，也要plt.show()。
           除非用户指定了其它语言或者字体，否则务必使用英文作为图注、图题。
           代码中的注释与用户输入的语言一致
           """

        print("🧵 启动后台线程")

        # 停止可能正在进行的AI生成
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
        self.ai_thread.finished.connect(lambda: self.enable_stop_button(False))
        
        self.ai_thread.start()
        
        # 启用停止按钮
        self.enable_stop_button(True)


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
