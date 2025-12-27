
import sys
import os
import json
import queue
from importlib import import_module
from typing import Tuple

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QListWidgetItem
from PySide6.QtCore import QThread, QObject, QTimer

from deepseek import DeepSeek
from GUI import Ui_MainWindow



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
# 后台 Worker（只负责生成代码）
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

    def run(self):
        try:
            print("🚀 开始调用 AI 接口")

            client = DeepSeek(
                base_url=self.baseurl,
                model=self.model,
                API_key=self.api_key
            )

            code = client.get_response(
                query=self.user_query,
                prompt=self.system_prompt,
                return_type="string"
            )

            print("✅ AI 返回完成，开始清理代码")

            code = code.strip()
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]

            self.result_queue.put(code)
            print("📦 代码已发送回主线程")

        except Exception as e:
            print(f"❌ 后台异常: {e}")


# =====================================================
# 主窗口
# =====================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.get_config()

        # ===== 队列 =====
        self.log_queue = queue.Queue()
        self.result_queue = queue.Queue()

        # stdout / stderr 重定向
        sys.stdout = EmittingStream(self.log_queue)
        sys.stderr = EmittingStream(self.log_queue)

        # ===== 定时器 =====
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.start(100)

        self.result_timer = QTimer(self)
        self.result_timer.timeout.connect(self.check_result)
        self.result_timer.start(100)

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

        self.thread = QThread(self)
        self.worker = AnalyseWorker(
            self.baseurl,
            self.model,
            self.api_key,
            user_query,
            system_prompt,
            self.result_queue
        )

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        print("🧵 启动后台线程")

        self.thread = QThread(self)
        self.worker = AnalyseWorker(
            self.baseurl,
            self.model,
            self.api_key,
            user_query,
            system_prompt,
            self.result_queue
        )

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.ui.pushButton_send_edit_query.setDisabled(True)
        # self.ui.pushButton_send_and_run_edit_query.setDisabled(True)

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

        print("▶ 在主线程执行生成代码")
        try:
            exec(code, {})
            print("完成")
        except Exception as e:
            print(f"❌ 执行代码失败，错误如下:\n {e}")
        self.ui.pushButton_analyse.setDisabled(False)
        self.ui.pushButton_send_edit_query.setDisabled(False)

    def direct_run(self):
        code = self.ui.plainTextEdit_code.toPlainText()
        print("▶ 在主线程执行生成代码")
        try:
            exec(code)
            print("完成")
        except Exception as e:
            print(f"❌ 执行代码失败，错误如下:\n {e}")

    # ---------------------
    # 启动后台分析
    # ---------------------
    def generate_code(self):
        self.ui.pushButton_analyse.setDisabled(True)
        user_query = self.ui.plainTextEdit_query.toPlainText()
        system_prompt = """你是一个python绘图代码生成工具，你能根据用户的输入直接生成代码。
你输出的内容只能有代码，不能有代码之外的其它东西。
输出必须是 markdown ``` ``` 包裹的代码。
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
scikit-learn
scikit-image
scipy
"""
        # 获取 listWidget_files 中的文件
        files = [self.ui.listWidget_files.item(i).text() for i in range(self.ui.listWidget_files.count())]
        if files:
            system_prompt += f"用户还提供了以下文件/文件夹和其路径，需要的时候在代码中写入读取对应文件的代码。路径如下：{files}"

        print("🧵 启动后台线程")

        self.thread = QThread(self)
        self.worker = AnalyseWorker(
            self.baseurl,
            self.model,
            self.api_key,
            user_query,
            system_prompt,
            self.result_queue
        )

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    # ---------------------
    # 配置文件
    # ---------------------
    def get_config(self) -> Tuple[str, str, str]:
        if not os.path.exists("config.json"):
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump({
                    "baseurl": "",
                    "model": "",
                    "api_key": ""
                }, f, indent=4)

        with open("config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)

        self.baseurl = cfg.get("baseurl", "")
        self.model = cfg.get("model", "")
        self.api_key = cfg.get("api_key", "")

        self.ui.lineEdit_baseurl.setText(self.baseurl)
        self.ui.lineEdit_model.setText(self.model)
        self.ui.lineEdit_key.setText(self.api_key)

    def save_config(self):
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump({
                    "baseurl": self.ui.lineEdit_baseurl.text(),
                    "model": self.ui.lineEdit_model.text(),
                    "api_key": self.ui.lineEdit_key.text()
                }, f, indent=4)
            print("✅ 配置保存成功")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

    def check_connection(self):
        """
        测试 API 连接：直接问 AI 你是谁，无需生成代码运行
        """
        self.ui.pushButton_analyse.setDisabled(True)
        user_query = '画一个正弦函数'
        system_prompt = """你是一个python绘图代码生成工具，你能根据用户的输入直接生成代码。
           你输出的内容只能有代码，不能有代码之外的其它东西。
           输出必须是 markdown ``` ``` 包裹的代码。
           禁止 if __name__ == "__main__",代码结尾不要带plt.close()，即使保存了图片，也要plt.show()。
           除非用户指定了其它语言或者字体，否则务必使用英文作为图注、图题。
           代码中的注释与用户输入的语言一致
           """
        # 获取 listWidget_files 中的文件
        # files = [self.ui.listWidget_files.item(i).text() for i in range(self.ui.listWidget_files.count())]
        # if files:
        #     system_prompt += f"用户还提供了以下文件/文件夹和其路径，需要的时候在代码中写入读取对应文件的代码。路径如下：{files}"

        print("🧵 启动后台线程")

        self.thread = QThread(self)
        self.worker = AnalyseWorker(
            self.baseurl,
            self.model,
            self.api_key,
            user_query,
            system_prompt,
            self.result_queue
        )

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

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
