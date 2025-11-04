import tkinter as tk
from tkinter import ttk
import random
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
import threading

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
        self.root.title("🧊 냉장고 시뮬레이터 - Step 6 (완전체)")
        self.root.geometry("900x750")
        
        # 물리 상태 변수
        self.fridge_temp = 7.0  # 초기 온도 (높게 시작)
        self.freezer_temp = -10.0
        self.fridge_target = 3.0  # 희망 온도
        self.freezer_target = -18.0
        
        # 액추에이터 상태
        self.compressor_on = False
        self.damper_open = False
        
        # 센서 상태
        self.fridge_sensor_ok = True
        self.freezer_sensor_ok = True
        self.arduino_connected = True
        
        # 장애 시뮬레이션
        self.fridge_sensor_fail_timer = 0
        self.freezer_sensor_fail_timer = 0
        self.arduino_fail_timer = 0
        
        # 데이터 기록 (그래프용)
        self.time_data = deque(maxlen=100)
        self.fridge_data = deque(maxlen=100)
        self.freezer_data = deque(maxlen=100)
        self.start_time = time.time()
        
        # 로그 기록
        self.logs = []
        
        # 통계 - NEW!
        self.fridge_temps = []
        self.freezer_temps = []
        
        # GUI 생성
        self.create_tabs()
        self.create_main_tab()
        self.create_graph_tab()
        self.create_log_tab()
        
        # 물리 엔진 시작 (별도 스레드) - NEW!
        self.running = True
        self.update_thread = threading.Thread(target=self.physics_loop, daemon=True)
        self.update_thread.start()
        
        # GUI 업데이트
        self.update_gui()
        
        # 종료 처리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.add_log("시스템 시작")
    
    def create_tabs(self):
        """탭 구조 생성"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.main_frame = ttk.Frame(self.notebook)
        self.graph_frame = ttk.Frame(self.notebook)
        self.log_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_frame, text="메인")
        self.notebook.add(self.graph_frame, text="실시간 그래프")
        self.notebook.add(self.log_frame, text="로그 & 통계")
    
    def create_main_tab(self):
        """메인 탭 GUI"""
        # === 냉장실 섹션 ===
        fridge_frame = ttk.LabelFrame(self.main_frame, text="냉장실", padding=10)
        fridge_frame.pack(fill='x', padx=10, pady=5)
        
        # 온도 표시
        temp_frame = ttk.Frame(fridge_frame)
        temp_frame.pack(fill='x', pady=5)
        
        self.fridge_temp_label = ttk.Label(temp_frame, text="온도: 0.0°C", font=('Arial', 14, 'bold'))
        self.fridge_temp_label.pack(side='left')
        
        self.fridge_status_label = ttk.Label(temp_frame, text="✅ 정상", font=('Arial', 12))
        self.fridge_status_label.pack(side='right')
        
        # 프로그레스바
        self.fridge_progress = ttk.Progressbar(fridge_frame, length=400, mode='determinate', maximum=15)
        self.fridge_progress.pack(fill='x', pady=5)
        
        # 희망 온도 슬라이더
        target_frame = ttk.Frame(fridge_frame)
        target_frame.pack(fill='x', pady=5)
        
        ttk.Label(target_frame, text="희망 온도:").pack(side='left')
        self.fridge_target_slider = ttk.Scale(target_frame, from_=0, to=10, orient='horizontal',
                                               command=self.update_fridge_target)
        self.fridge_target_slider.set(self.fridge_target)
        self.fridge_target_slider.pack(side='left', fill='x', expand=True, padx=5)
        
        self.fridge_target_label = ttk.Label(target_frame, text=f"{self.fridge_target}°C", width=8)
        self.fridge_target_label.pack(side='left')
        
        # === 냉동실 섹션 ===
        freezer_frame = ttk.LabelFrame(self.main_frame, text="냉동실", padding=10)
        freezer_frame.pack(fill='x', padx=10, pady=5)
        
        # 온도 표시
        temp_frame2 = ttk.Frame(freezer_frame)
        temp_frame2.pack(fill='x', pady=5)
        
        self.freezer_temp_label = ttk.Label(temp_frame2, text="온도: 0.0°C", font=('Arial', 14, 'bold'))
        self.freezer_temp_label.pack(side='left')
        
        self.freezer_status_label = ttk.Label(temp_frame2, text="✅ 정상", font=('Arial', 12))
        self.freezer_status_label.pack(side='right')
        
        # 프로그레스바
        self.freezer_progress = ttk.Progressbar(freezer_frame, length=400, mode='determinate', maximum=15)
        self.freezer_progress.pack(fill='x', pady=5)
        
        # 희망 온도 슬라이더
        target_frame2 = ttk.Frame(freezer_frame)
        target_frame2.pack(fill='x', pady=5)
        
        ttk.Label(target_frame2, text="희망 온도:").pack(side='left')
        self.freezer_target_slider = ttk.Scale(target_frame2, from_=-25, to=-10, orient='horizontal',
                                                command=self.update_freezer_target)
        self.freezer_target_slider.set(self.freezer_target)
        self.freezer_target_slider.pack(side='left', fill='x', expand=True, padx=5)
        
        self.freezer_target_label = ttk.Label(target_frame2, text=f"{self.freezer_target}°C", width=8)
        self.freezer_target_label.pack(side='left')
        
        # === 액추에이터 상태 ===
        actuator_frame = ttk.LabelFrame(self.main_frame, text="액추에이터 상태", padding=10)
        actuator_frame.pack(fill='x', padx=10, pady=5)
        
        status_frame = ttk.Frame(actuator_frame)
        status_frame.pack()
        
        self.compressor_label = ttk.Label(status_frame, text="압축기: ⚫ 꺼짐", font=('Arial', 12))
        self.compressor_label.pack(side='left', padx=20)
        
        self.damper_label = ttk.Label(status_frame, text="댐퍼: ⚫ 닫힘", font=('Arial', 12))
        self.damper_label.pack(side='left', padx=20)
        
        # === 장애 시뮬레이션 ===
        failure_frame = ttk.LabelFrame(self.main_frame, text="장애 시뮬레이션", padding=10)
        failure_frame.pack(fill='x', padx=10, pady=5)
        
        btn_frame = ttk.Frame(failure_frame)
        btn_frame.pack()
        
        self.fridge_fail_btn = ttk.Button(btn_frame, text="냉장실 센서 고장", 
                                          command=self.simulate_fridge_sensor_fail)
        self.fridge_fail_btn.pack(side='left', padx=5)
        
        self.freezer_fail_btn = ttk.Button(btn_frame, text="냉동실 센서 고장",
                                           command=self.simulate_freezer_sensor_fail)
        self.freezer_fail_btn.pack(side='left', padx=5)
        
        self.arduino_fail_btn = ttk.Button(btn_frame, text="제어기(Arduino) 고장",
                                           command=self.simulate_arduino_fail)
        self.arduino_fail_btn.pack(side='left', padx=5)
        
        # === 경고 메시지 ===
        warning_frame = ttk.Frame(self.main_frame)
        warning_frame.pack(fill='x', padx=10, pady=5)
        
        self.warning_label = ttk.Label(warning_frame, text="🚨 경고: (없음)", 
                                       font=('Arial', 11), foreground='green')
        self.warning_label.pack()
        
        # 설명
        info_label = ttk.Label(
            self.main_frame,
            text="Step 6: 통계 + 멀티스레딩 완전체",
            font=('Arial', 10),
            foreground='blue'
        )
        info_label.pack(pady=5)
    
    def create_graph_tab(self):
        """실시간 그래프 탭"""
        # Matplotlib Figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.ax.set_xlabel('시간 (초)')
        self.ax.set_ylabel('온도 (°C)')
        self.ax.set_title('실시간 온도 변화')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(['냉장실', '냉동실'])
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_log_tab(self):
        """로그 & 통계 탭"""
        # 통계 섹션 - NEW!
        stats_frame = ttk.LabelFrame(self.log_frame, text="통계", padding=10)
        stats_frame.pack(fill='both', padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=18, width=70)
        self.stats_text.pack()
        
        # 로그 섹션
        log_frame = ttk.LabelFrame(self.log_frame, text="이벤트 로그", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.log_text = tk.Text(log_frame, height=15, width=70, yscrollcommand=scrollbar.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.log_text.yview)
    
    # === 슬라이더 콜백 ===
    def update_fridge_target(self, value):
        self.fridge_target = round(float(value), 1)
        self.fridge_target_label.config(text=f"{self.fridge_target}°C")
        self.add_log(f"냉장실 희망 온도 변경: {self.fridge_target}°C")
    
    def update_freezer_target(self, value):
        self.freezer_target = round(float(value), 1)
        self.freezer_target_label.config(text=f"{self.freezer_target}°C")
        self.add_log(f"냉동실 희망 온도 변경: {self.freezer_target}°C")
    
    # === 장애 시뮬레이션 ===
    def simulate_fridge_sensor_fail(self):
        if self.fridge_sensor_fail_timer == 0:
            self.fridge_sensor_fail_timer = 50  # 5초 (0.1초 * 50)
            self.fridge_sensor_ok = False
            self.emergency_stop()
            self.add_log("🚨 냉장실 센서 고장 발생!")
            self.fridge_fail_btn.config(text="복구 중... 5초")
    
    def simulate_freezer_sensor_fail(self):
        if self.freezer_sensor_fail_timer == 0:
            self.freezer_sensor_fail_timer = 50
            self.freezer_sensor_ok = False
            self.emergency_stop()
            self.add_log("🚨 냉동실 센서 고장 발생!")
            self.freezer_fail_btn.config(text="복구 중... 5초")
    
    def simulate_arduino_fail(self):
        if self.arduino_fail_timer == 0:
            self.arduino_fail_timer = 50
            self.arduino_connected = False
            self.emergency_stop()
            self.add_log("🚨 제어기(Arduino) 통신 두절!")
            self.arduino_fail_btn.config(text="재연결 중... 5초")
    
    def emergency_stop(self):
        """긴급 정지"""
        self.compressor_on = False
        self.damper_open = False
        self.add_log("⚠️ 긴급 정지 실행")
    
    # === 물리 엔진 (별도 스레드) - NEW! ===
    def physics_loop(self):
        """물리 시뮬레이션 루프 (별도 스레드에서 실행)"""
        while self.running:
            # 장애 타이머 감소
            if self.fridge_sensor_fail_timer > 0:
                self.fridge_sensor_fail_timer -= 1
                if self.fridge_sensor_fail_timer == 0:
                    self.fridge_sensor_ok = True
                    self.add_log("✅ 냉장실 센서 복구 완료")
            
            if self.freezer_sensor_fail_timer > 0:
                self.freezer_sensor_fail_timer -= 1
                if self.freezer_sensor_fail_timer == 0:
                    self.freezer_sensor_ok = True
                    self.add_log("✅ 냉동실 센서 복구 완료")
            
            if self.arduino_fail_timer > 0:
                self.arduino_fail_timer -= 1
                if self.arduino_fail_timer == 0:
                    self.arduino_connected = True
                    self.add_log("✅ 제어기(Arduino) 재연결 완료")
            
            # 센서가 정상이고, Arduino 연결된 경우만 제어 로직 실행
            if self.fridge_sensor_ok and self.freezer_sensor_ok and self.arduino_connected:
                self.control_logic()
            
            # 물리 시뮬레이션
            self.update_physics()
            
            # 데이터 기록
            elapsed = time.time() - self.start_time
            self.time_data.append(elapsed)
            self.fridge_data.append(self.fridge_temp)
            self.freezer_data.append(self.freezer_temp)
            
            # 통계용 데이터
            self.fridge_temps.append(self.fridge_temp)
            self.freezer_temps.append(self.freezer_temp)
            
            time.sleep(0.1)  # 0.1초마다 업데이트
    
    def control_logic(self):
        """제어 로직 - 실제 냉장고 방식"""
        # === 1. 압축기 제어 ===
        prev_compressor = self.compressor_on
        
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
        
        # 상태 변경 시 로그
        if prev_compressor != self.compressor_on:
            if self.compressor_on:
                self.add_log("압축기 ON")
            else:
                self.add_log("압축기 OFF")
        
        # === 2. 댐퍼 제어 ===
        prev_damper = self.damper_open
        
        if self.compressor_on:
            # 압축기가 돌 때만 댐퍼 제어
            if self.fridge_temp > self.fridge_target + 1:
                self.damper_open = True
            elif self.fridge_temp < self.fridge_target - 1:
                self.damper_open = False
        else:
            # 압축기 안 돌면 댐퍼 닫음
            self.damper_open = False
        
        # 상태 변경 시 로그
        if prev_damper != self.damper_open:
            if self.damper_open:
                self.add_log("댐퍼 열림")
            else:
                if self.compressor_on:
                    self.add_log("댐퍼 닫힘")
                else:
                    self.add_log("댐퍼 닫힘 (압축기 정지)")
    
    def update_physics(self):
        """물리 시뮬레이션 - 실제 냉장고 물리"""
        # 자연 상승 (외부 열 유입)
        self.fridge_temp += 0.02
        self.freezer_temp += 0.01
        
        # 압축기 작동
        if self.compressor_on:
            self.freezer_temp -= 0.15  # 냉동실 냉각
            
            if self.damper_open:
                # 댐퍼 열림: 냉동실 찬 공기가 냉장실로 이동
                self.fridge_temp -= 0.08   # 냉장실 냉각
                self.freezer_temp += 0.05  # 냉동실 온도 상승 (찬 공기 손실!)
            else:
                # 댐퍼 닫혀도 약간 영향
                self.fridge_temp -= 0.01
        
        # 가우시안 노이즈 (센서 노이즈)
        self.fridge_temp += random.gauss(0, 0.05)
        self.freezer_temp += random.gauss(0, 0.05)
        
        # 온도 범위 제한
        self.fridge_temp = max(-5, min(15, self.fridge_temp))
        self.freezer_temp = max(-30, min(-5, self.freezer_temp))
    
    # === GUI 업데이트 (메인 스레드) ===
    def update_gui(self):
        """GUI 업데이트 (메인 스레드에서 실행)"""
        if not self.running:
            return
        
        # 온도 표시
        self.fridge_temp_label.config(text=f"온도: {self.fridge_temp:.1f}°C")
        self.freezer_temp_label.config(text=f"온도: {self.freezer_temp:.1f}°C")
        
        # 프로그레스바 (0-15°C 범위)
        fridge_progress_val = max(0, min(15, self.fridge_temp))
        freezer_progress_val = max(0, min(15, self.freezer_temp + 25))  # -25~-10 → 0~15
        self.fridge_progress['value'] = fridge_progress_val
        self.freezer_progress['value'] = freezer_progress_val
        
        # 상태 표시
        if self.fridge_sensor_ok:
            self.fridge_status_label.config(text="✅ 정상", foreground='green')
        else:
            self.fridge_status_label.config(text="❌ 센서 고장", foreground='red')
        
        if self.freezer_sensor_ok:
            self.freezer_status_label.config(text="✅ 정상", foreground='green')
        else:
            self.freezer_status_label.config(text="❌ 센서 고장", foreground='red')
        
        # 액추에이터 상태
        if self.compressor_on:
            self.compressor_label.config(text="압축기: 🔴 작동 중", foreground='red')
        else:
            self.compressor_label.config(text="압축기: ⚫ 꺼짐", foreground='gray')
        
        if self.damper_open:
            self.damper_label.config(text="댐퍼: 🔵 열림", foreground='blue')
        else:
            self.damper_label.config(text="댐퍼: ⚫ 닫힘", foreground='gray')
        
        # 경고 메시지
        warnings = []
        if not self.fridge_sensor_ok:
            warnings.append("냉장실 센서 고장")
        if not self.freezer_sensor_ok:
            warnings.append("냉동실 센서 고장")
        if not self.arduino_connected:
            warnings.append("제어기 통신 두절")
        
        if warnings:
            self.warning_label.config(text=f"🚨 경고: {', '.join(warnings)}", foreground='red')
        else:
            self.warning_label.config(text="🚨 경고: (없음)", foreground='green')
        
        # 장애 버튼 텍스트
        if self.fridge_sensor_fail_timer > 0:
            sec = self.fridge_sensor_fail_timer // 10
            self.fridge_fail_btn.config(text=f"복구 중... {sec}초")
        else:
            self.fridge_fail_btn.config(text="냉장실 센서 고장")
        
        if self.freezer_sensor_fail_timer > 0:
            sec = self.freezer_sensor_fail_timer // 10
            self.freezer_fail_btn.config(text=f"복구 중... {sec}초")
        else:
            self.freezer_fail_btn.config(text="냉동실 센서 고장")
        
        if self.arduino_fail_timer > 0:
            sec = self.arduino_fail_timer // 10
            self.arduino_fail_btn.config(text=f"재연결 중... {sec}초")
        else:
            self.arduino_fail_btn.config(text="제어기(Arduino) 고장")
        
        # 그래프 업데이트
        self.update_graph()
        
        # 통계 업데이트
        self.update_statistics()
        
        # 로그 업데이트
        self.update_log_display()
        
        # 다음 업데이트 예약
        self.root.after(100, self.update_gui)
    
    def update_graph(self):
        """실시간 그래프 업데이트"""
        if len(self.time_data) > 0:
            self.ax.clear()
            self.ax.plot(self.time_data, self.fridge_data, 'b-', label='냉장실', linewidth=2)
            self.ax.plot(self.time_data, self.freezer_data, 'r-', label='냉동실', linewidth=2)
            
            # 희망 온도 선
            self.ax.axhline(y=self.fridge_target, color='b', linestyle='--', alpha=0.5, label='냉장실 목표')
            self.ax.axhline(y=self.freezer_target, color='r', linestyle='--', alpha=0.5, label='냉동실 목표')
            
            self.ax.set_xlabel('시간 (초)')
            self.ax.set_ylabel('온도 (°C)')
            self.ax.set_title('실시간 온도 변화')
            self.ax.grid(True, alpha=0.3)
            self.ax.legend(loc='upper right')
            
            self.canvas.draw()
    
    def update_statistics(self):
        """통계 업데이트 - NEW!"""
        if len(self.fridge_temps) > 0:
            stats = f"""
=== 냉장실 통계 ===
현재 온도: {self.fridge_temp:.2f}°C
평균 온도: {sum(self.fridge_temps) / len(self.fridge_temps):.2f}°C
최고 온도: {max(self.fridge_temps):.2f}°C
최저 온도: {min(self.fridge_temps):.2f}°C

=== 냉동실 통계 ===
현재 온도: {self.freezer_temp:.2f}°C
평균 온도: {sum(self.freezer_temps) / len(self.freezer_temps):.2f}°C
최고 온도: {max(self.freezer_temps):.2f}°C
최저 온도: {min(self.freezer_temps):.2f}°C

=== 시스템 ===
가동 시간: {int(time.time() - self.start_time)}초
총 이벤트: {len(self.logs)}개
"""
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', stats)
    
    def update_log_display(self):
        """로그 디스플레이 업데이트"""
        # 최근 로그만 표시 (최대 100개)
        display_logs = self.logs[-100:]
        log_text = "\n".join(display_logs)
        
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert('1.0', log_text)
        self.log_text.see(tk.END)  # 자동 스크롤
    
    def add_log(self, message):
        """로그 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
    
    def on_closing(self):
        """종료 처리"""
        self.running = False
        self.root.destroy()

# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = RefrigeratorSimulator(root)
    root.mainloop()