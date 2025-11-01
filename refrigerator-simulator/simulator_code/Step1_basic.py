import tkinter as tk
from tkinter import ttk

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
    
    def create_gui(self):
        """기본 GUI 생성"""
        # 냉장실 섹션
        fridge_frame = ttk.LabelFrame(self.root, text="냉장실", padding=20)
        fridge_frame.pack(fill='x', padx=20, pady=10)
        
        self.fridge_temp_label = ttk.Label(
            fridge_frame, 
            text=f"온도: {self.fridge_temp}°C", 
            font=('Arial', 16, 'bold')
        )
        self.fridge_temp_label.pack(pady=10)
        
        # 냉동실 섹션
        freezer_frame = ttk.LabelFrame(self.root, text="냉동실", padding=20)
        freezer_frame.pack(fill='x', padx=20, pady=10)
        
        self.freezer_temp_label = ttk.Label(
            freezer_frame, 
            text=f"온도: {self.freezer_temp}°C", 
            font=('Arial', 16, 'bold')
        )
        self.freezer_temp_label.pack(pady=10)
        


# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = RefrigeratorSimulator(root)
    root.mainloop()