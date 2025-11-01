import tkinter as tk
from tkinter import ttk
import random

class RefrigeratorSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("냉장고 시뮬레이터")
        self.root.geometry("600x400")
        
        # 온도 변수
        self.fridge_temp = 7.0
        self.freezer_temp = -10.0
        
        # GUI 생성
        self.create_gui()
        
        # 온도 변화 시작
        self.update_temperature()
    
    def create_gui(self):
        """기본 GUI 생성"""
        # 냉장실 섹션
        fridge_frame = ttk.LabelFrame(self.root, text="냉장실", padding=20)
        fridge_frame.pack(fill='x', padx=20, pady=10)
        
        self.fridge_temp_label = ttk.Label(
            fridge_frame, 
            text=f"온도: {self.fridge_temp:.1f}°C", 
            font=('Arial', 16, 'bold')
        )
        self.fridge_temp_label.pack(pady=10)
        
        # 냉동실 섹션
        freezer_frame = ttk.LabelFrame(self.root, text="냉동실", padding=20)
        freezer_frame.pack(fill='x', padx=20, pady=10)
        
        self.freezer_temp_label = ttk.Label(
            freezer_frame, 
            text=f"온도: {self.freezer_temp:.1f}°C", 
            font=('Arial', 16, 'bold')
        )
        self.freezer_temp_label.pack(pady=10)
        
        # 설명 라벨
        info_label = ttk.Label(
            self.root, 
            text="온도가 실시간으로 변합니다 (자연 상승)",
            font=('Arial', 10),
            foreground='blue'
        )
        info_label.pack(pady=20)
    
    def update_temperature(self):
        """온도 자연 상승 시뮬레이션"""
        # 자연스럽게 온도 상승 (문 열림 등)
        self.fridge_temp += 0.02
        self.freezer_temp += 0.01
        
        # 약간의 노이즈 추가 (실제 센서처럼)
        self.fridge_temp += random.gauss(0, 0.05)
        self.freezer_temp += random.gauss(0, 0.05)
        
        # 온도 범위 제한
        self.fridge_temp = min(15, self.fridge_temp)
        self.freezer_temp = min(-5, self.freezer_temp)
        
        # 화면 업데이트
        self.fridge_temp_label.config(text=f"온도: {self.fridge_temp:.1f}°C")
        self.freezer_temp_label.config(text=f"온도: {self.freezer_temp:.1f}°C")
        
        # 100ms 후 다시 호출
        self.root.after(100, self.update_temperature)

# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = RefrigeratorSimulator(root)
    root.mainloop()