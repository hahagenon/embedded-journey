import tkinter as tk
from tkinter import ttk
import random

class RefrigeratorSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("냉장고 시뮬레이터")
        self.root.geometry("700x500")
        
        # 온도 변수
        self.fridge_temp = 7.0
        self.freezer_temp = -10.0
        self.fridge_target = 3.0
        self.freezer_target = -18.0
        
        # 압축기 상태
        self.compressor_on = False
        
        # GUI 생성
        self.create_gui()
        
        # 시뮬레이션 시작
        self.update_simulation()
    
    def create_gui(self):
        """GUI 생성"""
        # 냉장실 섹션
        fridge_frame = ttk.LabelFrame(self.root, text="냉장실", padding=20)
        fridge_frame.pack(fill='x', padx=20, pady=10)
        
        self.fridge_temp_label = ttk.Label(
            fridge_frame, 
            text=f"온도: {self.fridge_temp:.1f}°C", 
            font=('Arial', 16, 'bold')
        )
        self.fridge_temp_label.pack(pady=5)
        
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
        
        self.fridge_target_label = ttk.Label(slider_frame, text=f"{self.fridge_target}°C")
        self.fridge_target_label.pack(side='left')
        
        # 냉동실 섹션
        freezer_frame = ttk.LabelFrame(self.root, text="냉동실", padding=20)
        freezer_frame.pack(fill='x', padx=20, pady=10)
        
        self.freezer_temp_label = ttk.Label(
            freezer_frame, 
            text=f"온도: {self.freezer_temp:.1f}°C", 
            font=('Arial', 16, 'bold')
        )
        self.freezer_temp_label.pack(pady=5)
        
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
        
        self.freezer_target_label = ttk.Label(slider_frame2, text=f"{self.freezer_target}°C")
        self.freezer_target_label.pack(side='left')
        
        # 압축기 상태
        actuator_frame = ttk.LabelFrame(self.root, text="압축기 상태", padding=20)
        actuator_frame.pack(fill='x', padx=20, pady=10)
        
        self.compressor_label = ttk.Label(
            actuator_frame,
            text="압축기: 꺼짐",
            font=('Arial', 14)
        )
        self.compressor_label.pack()
        
        # 설명 라벨
        info_label = ttk.Label(
            self.root, 
            text="3단계: 슬라이더로 희망 온도 설정 + 압축기 자동 제어",
            font=('Arial', 10),
            foreground='blue'
        )
        info_label.pack(pady=10)

    def update_fridge_target(self, value):
        """냉장실 희망 온도 변경"""
        self.fridge_target = round(float(value), 1)
        self.fridge_target_label.config(text=f"{self.fridge_target}°C")
    
    def update_freezer_target(self, value):
        """냉동실 희망 온도 변경"""
        self.freezer_target = round(float(value), 1)
        self.freezer_target_label.config(text=f"{self.freezer_target}°C")

    def control_logic(self):
        """압축기 제어 로직"""
        # 냉동실 온도가 목표보다 2도 높으면 압축기 ON
        if self.freezer_temp > self.freezer_target + 2:
            self.compressor_on = True
        # 목표보다 2도 낮으면 압축기 OFF
        elif self.freezer_temp < self.freezer_target - 2:
            self.compressor_on = False

    def update_physics(self):
        """물리 시뮬레이션"""
        # 자연 상승 (외부 열 유입)
        self.fridge_temp += 0.02
        self.freezer_temp += 0.01
        
        # 압축기 작동 시 냉각
        if self.compressor_on:
            self.freezer_temp -= 0.15  # 냉동실 냉각
            self.fridge_temp -= 0.03   # 냉장실도 약간 냉각
        
        # 센서 노이즈
        self.fridge_temp += random.gauss(0, 0.05)
        self.freezer_temp += random.gauss(0, 0.05)
        
        # 온도 범위 제한
        self.fridge_temp = max(-5, min(20, self.fridge_temp))
        self.freezer_temp = max(-30, min(2, self.freezer_temp))

    def update_simulation(self):
        # 제어 로직 실행
        self.control_logic()

        # 물리 시뮬레이션
        self.update_physics()

        # 화면 업데이트
        self.fridge_temp_label.config(text=f"온도: {self.fridge_temp:.1f}°C")
        self.freezer_temp_label.config(text=f"온도: {self.freezer_temp:.1f}°C")

        if self.compressor_on:
            self.compressor_label.config(
                text="압축기: 작동 중",
                foreground='red'
            )
        else:
            self.compressor_label.config(
                text="압축기: 꺼짐",
                foreground='gray'
            )

        # 100ms 후 다시 호출
        self.root.after(100, self.update_simulation)

# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = RefrigeratorSimulator(root)
    root.mainloop()