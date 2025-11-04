import tkinter as tk
from tkinter import ttk
import random
import time
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import platform
import matplotlib.font_manager as fm

# OS별 한글 폰트 설정
system = platform.system()
if system == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'  # 맑은 고딕
elif system == 'Darwin':  # Mac
    plt.rcParams['font.family'] = 'AppleGothic'
else:  # Linux
    plt.rcParams['font.family'] = 'NanumGothic'

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

class RefrigeratorSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("🧊 냉장고 시뮬레이터 - Step 4")
        self.root.geometry("900x750")
        
        # 온도 변수
        self.fridge_temp = 7.0
        self.freezer_temp = -10.0
        self.fridge_target = 3.0
        self.freezer_target = -18.0
        
        # 액추에이터 상태
        self.compressor_on = False
        self.damper_open = False
        
        # 그래프 데이터
        self.time_data = deque(maxlen=100)
        self.fridge_data = deque(maxlen=100)
        self.freezer_data = deque(maxlen=100)
        self.start_time = time.time()
        
        # GUI 생성
        self.create_tabs()
        self.create_main_tab()
        self.create_graph_tab()
        
        # 시뮬레이션 시작
        self.update_simulation()
    
    def create_tabs(self):
        """탭 구조 생성"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.main_frame = ttk.Frame(self.notebook)
        self.graph_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_frame, text="메인")
        self.notebook.add(self.graph_frame, text="실시간 그래프")
    
    def create_main_tab(self):
        """메인 탭 GUI"""
        # === 냉장실 섹션 ===
        fridge_frame = ttk.LabelFrame(self.main_frame, text="냉장실", padding=10)
        fridge_frame.pack(fill='x', padx=10, pady=5)
        
        # 온도 표시
        temp_frame = ttk.Frame(fridge_frame)
        temp_frame.pack(fill='x', pady=5)
        
        self.fridge_temp_label = ttk.Label(
            temp_frame, 
            text="온도: 0.0°C", 
            font=('Arial', 14, 'bold')
        )
        self.fridge_temp_label.pack(side='left')
        
        self.fridge_status_label = ttk.Label(
            temp_frame, 
            text="✅ 정상", 
            font=('Arial', 12)
        )
        self.fridge_status_label.pack(side='right')
        
        # 프로그레스바
        self.fridge_progress = ttk.Progressbar(
            fridge_frame, 
            length=400, 
            mode='determinate', 
            maximum=15
        )
        self.fridge_progress.pack(fill='x', pady=5)
        
        # 희망 온도 슬라이더
        slider_frame = ttk.Frame(fridge_frame)
        slider_frame.pack(fill='x', pady=5)
        
        ttk.Label(slider_frame, text="희망 온도:").pack(side='left')
        self.fridge_slider = ttk.Scale(
            slider_frame, 
            from_=0, to=10, 
            orient='horizontal',
            command=self.update_fridge_target
        )
        self.fridge_slider.set(self.fridge_target)
        self.fridge_slider.pack(side='left', fill='x', expand=True, padx=5)
        
        self.fridge_target_label = ttk.Label(
            slider_frame, 
            text=f"{self.fridge_target}°C", 
            width=8
        )
        self.fridge_target_label.pack(side='left')
        
        # === 냉동실 섹션 ===
        freezer_frame = ttk.LabelFrame(self.main_frame, text="냉동실", padding=10)
        freezer_frame.pack(fill='x', padx=10, pady=5)
        
        # 온도 표시
        temp_frame2 = ttk.Frame(freezer_frame)
        temp_frame2.pack(fill='x', pady=5)
        
        self.freezer_temp_label = ttk.Label(
            temp_frame2, 
            text="온도: 0.0°C", 
            font=('Arial', 14, 'bold')
        )
        self.freezer_temp_label.pack(side='left')
        
        self.freezer_status_label = ttk.Label(
            temp_frame2, 
            text="✅ 정상", 
            font=('Arial', 12)
        )
        self.freezer_status_label.pack(side='right')
        
        # 프로그레스바
        self.freezer_progress = ttk.Progressbar(
            freezer_frame, 
            length=400, 
            mode='determinate', 
            maximum=15
        )
        self.freezer_progress.pack(fill='x', pady=5)
        
        # 희망 온도 슬라이더
        slider_frame2 = ttk.Frame(freezer_frame)
        slider_frame2.pack(fill='x', pady=5)
        
        ttk.Label(slider_frame2, text="희망 온도:").pack(side='left')
        self.freezer_slider = ttk.Scale(
            slider_frame2, 
            from_=-25, to=-10, 
            orient='horizontal',
            command=self.update_freezer_target
        )
        self.freezer_slider.set(self.freezer_target)
        self.freezer_slider.pack(side='left', fill='x', expand=True, padx=5)
        
        self.freezer_target_label = ttk.Label(
            slider_frame2, 
            text=f"{self.freezer_target}°C", 
            width=8
        )
        self.freezer_target_label.pack(side='left')
        
        # === 액추에이터 상태 ===
        actuator_frame = ttk.LabelFrame(
            self.main_frame, 
            text="액추에이터 상태", 
            padding=10
        )
        actuator_frame.pack(fill='x', padx=10, pady=5)
        
        status_frame = ttk.Frame(actuator_frame)
        status_frame.pack()
        
        self.compressor_label = ttk.Label(
            status_frame, 
            text="압축기: ⚫ 꺼짐", 
            font=('Arial', 12)
        )
        self.compressor_label.pack(side='left', padx=20)
        
        self.damper_label = ttk.Label(
            status_frame, 
            text="댐퍼: ⚫ 닫힘", 
            font=('Arial', 12)
        )
        self.damper_label.pack(side='left', padx=20)
        
        # 설명 라벨
        info_label = ttk.Label(
            self.main_frame,
            text="Step 4: 실제 냉장고 제어 로직 (댐퍼 + 압축기 연동)",
            font=('Arial', 10),
            foreground='blue'
        )
        info_label.pack(pady=10)
    
    def create_graph_tab(self):
        """실시간 그래프 탭"""
        # Matplotlib Figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.ax.set_xlabel('시간 (초)')
        self.ax.set_ylabel('온도 (°C)')
        self.ax.set_title('실시간 온도 변화')
        self.ax.grid(True, alpha=0.3)
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def update_fridge_target(self, value):
        """냉장실 희망 온도 변경"""
        self.fridge_target = round(float(value), 1)
        self.fridge_target_label.config(text=f"{self.fridge_target}°C")
    
    def update_freezer_target(self, value):
        """냉동실 희망 온도 변경"""
        self.freezer_target = round(float(value), 1)
        self.freezer_target_label.config(text=f"{self.freezer_target}°C")
    
    def control_logic(self):
        """제어 로직 - 실제 냉장고 방식 (간단 명확 버전)"""
        # === 1. 압축기 제어 ===
        
        # 압축기 ON 조건
        if self.freezer_temp > self.freezer_target + 2:
            # 냉동실이 더우면 무조건 ON
            self.compressor_on = True
        elif self.fridge_temp > self.fridge_target + 3:
            # 냉장실이 너무 더우면 강제 ON (안전장치)
            self.compressor_on = True
        
        # 압축기 OFF 조건
        elif self.freezer_temp < self.freezer_target - 2 and \
            self.fridge_temp < self.fridge_target - 1:
            # 둘 다 충분히 차가우면 OFF
            self.compressor_on = False
        
        # 그 외: 현재 상태 유지 (Hysteresis)
        
        # === 2. 댐퍼 제어 ===
        if self.compressor_on:
            # 압축기가 돌 때만 댐퍼 제어
            if self.fridge_temp > self.fridge_target + 1:
                self.damper_open = True
            elif self.fridge_temp < self.fridge_target - 1:
                self.damper_open = False
        else:
            # 압축기 안 돌면 댐퍼 닫음
            self.damper_open = False
    
    def update_physics(self):
        """물리 시뮬레이션 - 실제 냉장고 물리"""
        # 자연 상승 (외부 열 유입)
        self.fridge_temp += 0.02
        self.freezer_temp += 0.01
        
        # 압축기 작동 시
        if self.compressor_on:
            self.freezer_temp -= 0.15  # 냉동실 냉각
            
            if self.damper_open:
                # 댐퍼 열림: 냉동실 찬 공기가 냉장실로 이동
                self.fridge_temp -= 0.08   # 냉장실 냉각
                self.freezer_temp += 0.05  # 냉동실 온도 상승 (찬 공기 손실!)
            else:
                # 댐퍼 닫힘: 벽을 통한 약간의 열 전도
                self.fridge_temp -= 0.01
        
        # 센서 노이즈
        self.fridge_temp += random.gauss(0, 0.05)
        self.freezer_temp += random.gauss(0, 0.05)
        
        # 온도 범위 제한
        self.fridge_temp = max(-5, min(15, self.fridge_temp))
        self.freezer_temp = max(-30, min(-5, self.freezer_temp))
    

    def update_graph(self):
        """그래프 업데이트"""
        if len(self.time_data) > 0:
            self.ax.clear()
            self.ax.plot(
                self.time_data, 
                self.fridge_data, 
                'b-', 
                label='fridge', 
                linewidth=2
            )
            self.ax.plot(
                self.time_data, 
                self.freezer_data, 
                'r-', 
                label='freezer', 
                linewidth=2
            )
            
            # 목표 온도 선
            self.ax.axhline(
                y=self.fridge_target, 
                color='b', 
                linestyle='--', 
                alpha=0.5, 
                label='fridge goal'
            )
            self.ax.axhline(
                y=self.freezer_target, 
                color='r', 
                linestyle='--', 
                alpha=0.5, 
                label='freezer goal'
            )
            
            self.ax.set_xlabel('time (sec)')
            self.ax.set_ylabel('temperature (°C)')
            self.ax.set_title('realtime temperature change')
            self.ax.grid(True, alpha=0.3)
            self.ax.legend(loc='upper right')
            
            self.canvas.draw()
        
    
    def update_simulation(self):
        """시뮬레이션 업데이트"""
        # 제어 로직
        self.control_logic()
        
        # 물리 시뮬레이션
        self.update_physics()
        
        # 데이터 기록
        elapsed = time.time() - self.start_time
        self.time_data.append(elapsed)
        self.fridge_data.append(self.fridge_temp)
        self.freezer_data.append(self.freezer_temp)
        
        # GUI 업데이트
        self.fridge_temp_label.config(text=f"온도: {self.fridge_temp:.1f}°C")
        self.freezer_temp_label.config(text=f"온도: {self.freezer_temp:.1f}°C")
        
        # 프로그레스바 업데이트 (0-15°C 범위로 매핑)
        fridge_progress_val = max(0, min(15, self.fridge_temp))
        freezer_progress_val = max(0, min(15, self.freezer_temp + 25))  # -25~-10 → 0~15
        self.fridge_progress['value'] = fridge_progress_val
        self.freezer_progress['value'] = freezer_progress_val
        
        # 액추에이터 상태 표시
        if self.compressor_on:
            self.compressor_label.config(
                text="압축기: 🔴 작동 중",
                foreground='red'
            )
        else:
            self.compressor_label.config(
                text="압축기: ⚫ 꺼짐",
                foreground='gray'
            )
        
        # 댐퍼 상태 표시
        if self.damper_open:
            self.damper_label.config(
                text="댐퍼: 🔵 열림",
                foreground='blue'
            )
        else:
            self.damper_label.config(
                text="댐퍼: ⚫ 닫힘",
                foreground='gray'
            )
        
        # 그래프 업데이트
        self.update_graph()
        
        # 100ms 후 다시 호출
        self.root.after(100, self.update_simulation)

if __name__ == "__main__":
    root = tk.Tk()
    app = RefrigeratorSimulator(root)
    root.mainloop()

