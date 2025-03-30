# 新增导入
from PIL import Image, ImageTk
import sys
import os
import threading  
import socket
import json
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from tkinter.scrolledtext import ScrolledText

class ExamClient:
    def __init__(self, root):
        self.root = root
        self.current_screen = "login"
        self.config_path = Path("config.json")
        self.default_ip = self.load_default_ip()
        self.server_ip = ""
        self.student_id = ""
        self.name = ""
        self.exam_paper = []
        self.current_question = 0
        self.answers = {}
        self.start_time = 0
        self.remaining_time = 0  # 新增初始化
        self.exam_duration = 0   # 新增考试总时长
        self.exam_rules  = {}  # 新增考试规则
            
        self.logo_photo = None  # 显式初始化
        # 新增资源路径处理
        self.base_dir = Path(__file__).parent if __name__ == "__main__" else Path(sys.executable).parent
        self.load_logo()  # 加载Logo
        
        self.setup_ui()
        
    def update_header_frame(self):
        """更新考试界面顶部信息栏"""
        if hasattr(self, 'header_frame'):  # 确保信息栏已创建
            # 清除旧内容
            for widget in self.header_frame.winfo_children():
                widget.destroy()     
            # 添加Logo
            if self.logo_photo is not None:  # 明确检查是否为 None
                logo_label = ttk.Label(self.header_frame, image=self.logo_photo).pack(side="left", padx=5, pady=5)       
            # 公司信息
            company_info = ttk.Label(self.header_frame, text="耒阳市天柱学校\n在线考试系统", 
                                   font=('微软雅黑', 12), justify="center")
            company_info.pack(side="left", padx=5, pady=5)
            # 考生信息
            info_text = f"""
            考生姓名：{self.name}
            考　　号：{self.student_id}
            考试时间：{self.exam_duration//60}分钟
            题型： 选择题{self.exam_rules["选择题数量"]}道 判断题{self.exam_rules["判断题数量"]}道"""
            ttk.Label(self.header_frame, text=info_text, font=('宋体', 10)).pack(side="right", padx=35)
            

        
    def load_logo(self):
        """加载并调整Logo大小"""
        self.logo_photo = None
        try:
            logo_path = self.base_dir / "images/company_logo.png"
            if logo_path.exists():
                # 打开图片并调整尺寸
                self.logo_image = Image.open(logo_path)
                
                # 定义目标尺寸（例如 宽度200px，高度按比例缩放）
                target_width = 90
                width_percent = target_width / float(self.logo_image.size[0])
                target_height = int(float(self.logo_image.size[1]) * width_percent)
                
                # 使用抗锯齿优化缩放效果
                self.logo_image = self.logo_image.resize(
                    (target_width, target_height), 
                    Image.Resampling.LANCZOS
                )
                
                # 转换为Tkinter可用的PhotoImage
                self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            else:
                print(f"警告：Logo文件未找到 {logo_path}")
        except Exception as e:
            print(f"Logo加载失败: {str(e)}")
        
        
    def set_close_handler(self):
        """根据当前界面动态设置关闭事件处理"""
        if self.current_screen == "exam":
            # 考试中：禁止直接关闭
            self.root.protocol("WM_DELETE_WINDOW", self.on_exam_close)
        else:
            # 登录界面或结果界面：允许直接关闭
            self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def on_exam_close(self):
        """考试中关闭事件处理"""
        messagebox.showwarning("警告", "考试进行中，请通过'交卷'按钮结束考试！")
        return  # 不执行任何关闭动作 
       
        
    def load_default_ip(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("default_ip", "")
        except FileNotFoundError:
            return ""
        
    def setup_ui(self):
        """登录界面初始化"""
        self.current_screen = "login"
        self.set_close_handler()  # 允许直接关闭
        
        # ...登录界面组件创建...
        self.root.title("在线考试系统-学生端")
        self.root.geometry("810x620")
        
        # 登录界面顶部区域
        self.header_frame = ttk.Frame(self.root)
        # 添加Logo
        if self.logo_photo is not None:  # 明确检查是否为 None
            logo_label = ttk.Label(self.header_frame, image=self.logo_photo).pack(side="left", padx=5, pady=5)       
        # 公司信息
        company_info = ttk.Label(self.header_frame, text="耒阳市天柱学校\n在线考试系统", 
                               font=('微软雅黑', 12), justify="center")
        company_info.pack(side="left", padx=5, pady=5)
        self.header_frame.pack(fill="x")
        
        # 原登录框代码保持不变...
        # 登录界面
        self.login_frame = ttk.Frame(self.root)
        ttk.Label(self.login_frame, text="服务器IP：").grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = ttk.Entry(self.login_frame)
        self.ip_entry.insert(0, self.default_ip)  # 插入默认IP
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
        # 增加"保存为默认"按钮
        ttk.Button(self.login_frame, text="保存为默认IP", command=self.save_default_ip).grid(row=0, column=2, padx=5)
        
        ttk.Label(self.login_frame, text="姓名：").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.login_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_frame, text="考号：").grid(row=2, column=0, padx=5, pady=5)
        self.id_entry = ttk.Entry(self.login_frame)
        self.id_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(self.login_frame, text="连接服务器", command=self.connect_server).grid(row=3, column=0, columnspan=2, pady=10)
        self.login_frame.pack(pady=50)
        
        # 考试界面
        self.exam_frame = ttk.Frame(self.root)
         
        # 原考试界面组件
        self.question_label = ttk.Label(self.exam_frame, wraplength=700, font=('Arial', 12))
        self.question_label.pack(pady=10)
        
        self.option_var = tk.StringVar()
        self.option_buttons = []
        for i in range(4):
            btn = ttk.Radiobutton(self.exam_frame, variable=self.option_var)
            btn.pack(anchor="w", padx=20, pady=5)
            self.option_buttons.append(btn)
        
        self.timer_label = ttk.Label(self.exam_frame, text="剩余时间: --:--", font=('Arial', 12))
        self.timer_label.pack(pady=10)
        
        btn_frame = ttk.Frame(self.exam_frame)
        ttk.Button(btn_frame, text="上一题", command=self.prev_question).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="下一题", command=self.next_question).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="交卷", command=self.submit_exam).pack(side="right", padx=10)
        btn_frame.pack(fill="x", pady=10)
        
        # 底部信息栏（在所有界面显示）
        footer = ttk.Frame(self.root)
        ttk.Label(footer, text="© 2025 耒阳市天柱学校 版权所有", 
                 font=('宋体', 10), foreground="gray").pack(pady=5)
        footer.pack(side="bottom", fill="x")
        
    def save_default_ip(self):
        new_ip = self.ip_entry.get()
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({"default_ip": new_ip}, f, indent=2)
            messagebox.showinfo("成功", "默认IP已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
        
    def connect_server(self):
        self.server_ip = self.ip_entry.get()
        self.name = self.name_entry.get()
        self.student_id = self.id_entry.get()
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.server_ip, 65432))
                s.sendall(json.dumps({
                    'cmd': 'verify_student',
                    'student_id': self.student_id,
                    'name': self.name
                }).encode('utf-8'))
                response = json.loads(s.recv(1024).decode('utf-8'))
                
                if response['status'] == 'success':
                    self.start_exam()
                else:
                    messagebox.showerror("错误", "考生信息验证失败")
        except Exception as e:
            messagebox.showerror("错误", f"连接失败：{str(e)}")
    
    def start_exam(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # 设置超时防止卡死
                s.connect((self.server_ip, 65432))
                
                # 新增 start_exam 命令
                start_request = {
                    'cmd': 'start_exam',
                    'student_id': self.student_id,
                    'name': self.name
                }
                s.sendall(json.dumps(start_request).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                # 获取考试规则（含时长）
                s.sendall(json.dumps({'cmd': 'get_exam_rules'}).encode('utf-8'))
                rules_response = json.loads(s.recv(1024).decode("utf-8"))
                # 检查规则是否有效
                #print(f"收到响应start_exam：{rules_response}")  # 调试输出
                if rules_response.get("status") != "success":
                    error_msg = rules_response.get("message", "未知错误")
                    raise ValueError(f"获取规则失败: {error_msg}")
                
                # 2. 检查必要字段
                required_fields = ["考试时长", "选择题数量", "判断题数量"]
                for field in required_fields:
                    if field not in rules_response["data"]:
                        raise ValueError(f"考试规则缺少必要字段: {field}")
                    
                # 3. 初始化考试时间
                self.exam_duration = rules_response["data"]["考试时长"] * 60
                self.remaining_time = self.exam_duration
                
                self.exam_rules = rules_response["data"]
                
                # 立即更新信息栏 显示考生姓名，考号，考试时间
                self.update_header_frame()  # 立即更新信息栏
                
                #  get_exam_paper 命令
                request = {
                'cmd': 'get_exam_paper',
                'student_id': self.student_id,
                'name': self.name
                }
                #print(f"发送请求：{request}")  # 调试输出
                s.sendall(json.dumps(request).encode('utf-8'))
                response = json.loads(s.recv(65535).decode('utf-8'))
                #print(f"收到响应：{response}")  # 调试输出
                print("[DEBUG] 接收到的试卷第一题：", response['questions'][0])  # 打印第一题详情
                
                if response['status'] == 'success':
                    self.exam_paper = response['questions']
                    self.login_frame.pack_forget()
                    self.exam_frame.pack(fill="both", expand=True)
                    self.start_time = time.time()
                    self.show_question(0)
                    self.update_timer()
                
                """进入考试界面"""
                self.current_screen = "exam"
                self.set_close_handler()  # 更新关闭事件处理                
        except Exception as e:
            messagebox.showerror("错误", f"开始考试失败：{str(e)}")
                     
            
    def show_question(self, index):
        self.current_question = index
        question = self.exam_paper[index]
        self.question_label.config(text=f"第{index+1}题：{question['题目内容']}")
        
        options = []
        if question['题型'] == '选择题':
            # 生成带ABCD前缀的选项文本
            for i in range(4):
                option_key = f'选项{chr(65 + i)}'  # 选项A、选项B等
                option_text = question.get(option_key, "")
                if option_text.strip():
                    options.append(f"{chr(65 + i)}. {option_text}")
        else:
            # 判断题直接显示正确/错误
            options = ['正确', '错误']
            
        # 更新选项按钮
        for i in range(4):
            if i < len(options):
                # 设置显示文本（带前缀）和实际值（A/B/C/D 或 对/错）
                display_text = options[i]
                actual_value = chr(65 + i) if question['题型'] == '选择题' else ('对' if i == 0 else '错')
                self.option_buttons[i].config(
                    text=display_text,
                    value=actual_value,
                    state="normal"
                )
            else:
                self.option_buttons[i].config(text="", value="", state="disabled")
        
        # 显示已保存的答案
        saved_answer = self.answers.get(question['题目ID'], "")
        self.option_var.set(saved_answer)

    def next_question(self):
        self.save_answer()
        if self.current_question < len(self.exam_paper) - 1:
            self.show_question(self.current_question + 1)

    def prev_question(self):
        self.save_answer()
        if self.current_question > 0:
            self.show_question(self.current_question - 1)

    def save_answer(self):
        current_q = self.exam_paper[self.current_question]
        self.answers[current_q['题目ID']] = self.option_var.get()

    def update_timer(self):
        if not hasattr(self, 'remaining_time'):  # 防御性编程
            self.remaining_time = self.exam_duration
        
        # 计算剩余时间
        mins, secs = divmod(self.remaining_time, 60)
        self.timer_label.config(text=f"剩余时间: {mins:02d}:{secs:02d}")
        
        # 持续倒计时
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.root.after(1000, self.update_timer)  # 每秒更新一次
        else:
            self.submit_exam()  # 时间到自动交卷

    def calculate_score(self):
        score = 0
        wrong_details = []
        for q in self.exam_paper:
            # 统一转换为大写并去除空格
            correct_answer = q['正确答案'].strip().upper()
            user_answer = self.answers.get(q['题目ID'], "").strip().upper()
            # 直接从试卷题目中获取动态分值
            question_score = int(q['分值'])  # 使用服务端生成的分值
            if user_answer == correct_answer:
                score += question_score
            else:
                # 记录错题详细信息
                wrong_details.append({
                    "题目ID": q['题目ID'],
                    "题目内容": q['题目内容'],
                    "学生答案": user_answer,
                    "正确答案": correct_answer,
                    "题型": q['题型']
                })
        return score, wrong_details # 返回得分和错题详情

        
    def show_result(self, score, wrong_details, time_used):
        self.exam_frame.pack_forget()
        
        result_frame = ttk.Frame(self.root)
        
        ttk.Label(result_frame, text="考试结果", font=('微软雅黑', 16)).pack(pady=10)
        ttk.Label(result_frame, text=f"姓名：{self.name}").pack()
        ttk.Label(result_frame, text=f"考号：{self.student_id}").pack()
        ttk.Label(result_frame, text=f"得分：{score}分").pack()
        ttk.Label(result_frame, text=f"考试用时：{int(time_used)}秒").pack()
        
        # 错题详情区域
        ttk.Label(result_frame, text="错题详情：").pack(pady=5)
        details_text = ScrolledText(result_frame, width=80, height=20, font=('宋体', 10))
        details_text.pack(padx=10)
        
        # 填充错题数据（新增选项值解析）
        for detail in wrong_details:
            # 获取题目完整数据
            question = next((q for q in self.exam_paper if q['题目ID'] == detail['题目ID']), None)
            
            # 解析选项值（仅选择题需要）
            if question and question['题型'] == '选择题':
                # 你的答案带选项值
                user_answer_key = detail['学生答案']  # 如 'B'
                #学生未作答
                if not user_answer_key:
                    user_answer_display = '未作答'
                else:
                    user_answer_value = question.get(f'选项{user_answer_key}', '无效选项')
                    user_answer_display = f"{user_answer_key}. {user_answer_value}"
                
                # 正确答案带选项值
                correct_answer_key = detail['正确答案']  # 如 'A'
                correct_answer_value = question.get(f'选项{correct_answer_key}', '无效选项')
                correct_answer_display = f"{correct_answer_key}. {correct_answer_value}"
            else:
                # 你的答案带选项值
                user_answer_key = detail['学生答案']  # 如 'B'
                # 判断题 学生没有作答，显示 "未作答"
                if not user_answer_key:
                    user_answer_display = '未作答'
                else:
                    # 判断题直接显示文字
                    user_answer_display = '对' if detail['学生答案'] == '对' else '错'
                correct_answer_display = '对' if detail['正确答案'] == '对' else '错'
            
            # 生成详情文本
            text = f"""
            [题目ID] {detail['题目ID']}
            [题目内容] {detail['题目内容']}
            [你的答案] {user_answer_display}
            [正确答案] {correct_answer_display}
            {'-'*50}
            """
            details_text.insert("end", text)
        
        ttk.Button(result_frame, text="退出", command=self.root.quit).pack(pady=10)
        result_frame.pack()

    def submit_exam(self):
        self.save_answer()
        # 提交试卷时间
        end_time = time.time()
        time_used = end_time - self.start_time
        score, wrong_details = self.calculate_score()
        
        # 提交结果到服务端
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.server_ip, 65432))
                try:
                    request_data = {
                        "cmd": "submit_result",
                        "student_id": self.student_id,
                        "name": self.name,
                        "score": score,
                        "start_time": self.start_time,  # 新增字段
                        "end_time": end_time,           # 新增字段
                        "time_used": int(time_used),
                        "wrong_details": wrong_details,
                        "exam_paper": self.exam_paper
                    }
                    
                    # 调试输出原始数据
                    #print(f"[DEBUG] 请求数据: {request_data}")
                    
                    # 手动转换为JSON并验证
                    json_data = json.dumps(request_data, ensure_ascii=False)
                    print(f"[DEBUG] JSON长度: {len(json_data)}")   
                except Exception as e:
                    print(f"JSON生成失败: {str(e)}")
                    
                s.sendall(json_data.encode('utf-8'))
                response = json.loads(s.recv(1024).decode('utf-8'))
                
                if response['status'] == 'success':
                    self.show_result(score, wrong_details, time_used)
                else:
                    print(f"提交试卷失败: {response.get('message', '未知错误')}")
                    messagebox.showerror("错误", "交卷失败，请重试")
        except Exception as e:
            messagebox.showerror("错误", f"提交失败：{str(e)}")
        finally:
            """进入考试结果界面"""
            self.current_screen = "result"
            self.set_close_handler()  # 允许直接关闭

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamClient(root)
    root.mainloop()
