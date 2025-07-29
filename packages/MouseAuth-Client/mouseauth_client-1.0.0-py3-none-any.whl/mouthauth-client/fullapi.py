import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

from clients import MousePatternAuth, create_tracking_widget

def create_modern_style(root):
    """모던한 스타일 적용"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # 색상 설정
    style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
    style.configure('Subtitle.TLabel', font=('Arial', 10), foreground='#7f8c8d')
    style.configure('Status.TLabel', font=('Arial', 10, 'bold'))
    style.configure('Success.TLabel', font=('Arial', 10, 'bold'), foreground='#27ae60')
    style.configure('Error.TLabel', font=('Arial', 10, 'bold'), foreground='#e74c3c')
    style.configure('Warning.TLabel', font=('Arial', 10, 'bold'), foreground='#f39c12')
    
    # 버튼 스타일
    style.configure('Action.TButton', font=('Arial', 10, 'bold'), padding=10)
    style.configure('Primary.TButton', font=('Arial', 10, 'bold'), padding=10)
    
    root.configure(bg='#ecf0f1')

def create_registration_ui(server_url="http://localhost:8000"):
    """
    사용자 등록 UI 창 생성
    
    Args:
        server_url: 인증 서버 URL
    
    Returns:
        root 윈도우
    """
    root = tk.Tk()
    root.title("마우스 패턴 등록")
    root.geometry("700x600")
    root.resizable(False, False)
    
    # 스타일 적용
    create_modern_style(root)
    
    # 메인 프레임
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 제목
    title_label = ttk.Label(main_frame, text="🖱️ 마우스 패턴 등록", style='Title.TLabel')
    title_label.pack(pady=(0, 10))
    
    subtitle_label = ttk.Label(main_frame, 
                              text="마우스 움직임 패턴을 학습하여 개인 인증 프로필을 생성합니다", 
                              style='Subtitle.TLabel')
    subtitle_label.pack(pady=(0, 20))
    
    # 사용자 정보 입력 프레임
    info_frame = ttk.LabelFrame(main_frame, text="사용자 정보", padding="15")
    info_frame.pack(fill=tk.X, pady=(0, 15))
    
    # 사용자 ID 입력
    ttk.Label(info_frame, text="사용자 ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
    user_id_var = tk.StringVar()
    user_id_entry = ttk.Entry(info_frame, textvariable=user_id_var, width=30, font=('Arial', 11))
    user_id_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
    
    # 세션 수 설정
    ttk.Label(info_frame, text="학습 세션 수:").grid(row=1, column=0, sticky=tk.W, pady=5)
    session_count_var = tk.StringVar(value="3")
    session_count_spinbox = ttk.Spinbox(info_frame, from_=1, to=10, 
                                       textvariable=session_count_var, width=10)
    session_count_spinbox.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.W)
    
    # 패턴 수집 영역
    pattern_frame = ttk.LabelFrame(main_frame, text="패턴 수집 영역", padding="15")
    pattern_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    
    # 추적 캔버스
    canvas = tk.Canvas(pattern_frame, width=600, height=250, bg='#bdc3c7', 
                      relief=tk.SUNKEN, bd=2, highlightthickness=0)
    canvas.pack(pady=10)
    
    # 캔버스 초기 텍스트
    canvas_text = canvas.create_text(300, 125, 
                                   text="🖱️ 마우스 패턴 수집 영역\n\n자연스럽게 마우스를 움직여주세요\n클릭, 드래그, 스크롤 등 다양한 동작을 해보세요", 
                                   fill='#2c3e50', font=('Arial', 12), justify=tk.CENTER)
    
    # 인증 객체 생성
    auth = MousePatternAuth(server_url=server_url)
    auth.set_tracking_widget(canvas)
    
    # 상태 및 진행 상황
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=(0, 15))
    
    status_var = tk.StringVar(value="등록할 준비가 되었습니다")
    status_label = ttk.Label(status_frame, textvariable=status_var, style='Status.TLabel')
    status_label.pack(side=tk.LEFT)
    
    # 진행률 표시
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(status_frame, variable=progress_var, maximum=100, length=200)
    progress_bar.pack(side=tk.RIGHT)
    
    # 수집 상태 변수
    collection_state = {
        'current_session': 0,
        'total_sessions': 3,
        'collecting': False,
        'sessions_completed': []
    }
    
    def update_canvas_state(state):
        """캔버스 상태 업데이트"""
        if state == 'ready':
            canvas.configure(bg='#bdc3c7')
            canvas.itemconfig(canvas_text, text="🖱️ 마우스 패턴 수집 영역\n\n자연스럽게 마우스를 움직여주세요\n클릭, 드래그, 스크롤 등 다양한 동작을 해보세요")
        elif state == 'collecting':
            canvas.configure(bg='#a8e6cf')
            canvas.itemconfig(canvas_text, text="🔴 수집 중...\n\n다양한 마우스 동작을 해주세요\n(10-15초 후 자동으로 다음 세션)")
        elif state == 'completed':
            canvas.configure(bg='#81c784')
            canvas.itemconfig(canvas_text, text="✅ 세션 완료!\n\n잠시만 기다려주세요...")
    
    def start_collection_session():
        """단일 세션 수집 시작"""
        if not user_id_var.get().strip():
            messagebox.showerror("오류", "사용자 ID를 입력해주세요.")
            return False
        
        collection_state['collecting'] = True
        collection_state['current_session'] += 1
        
        # UI 업데이트
        update_canvas_state('collecting')
        status_var.set(f"세션 {collection_state['current_session']}/{collection_state['total_sessions']} 수집 중...")
        
        # 진행률 업데이트
        progress = (collection_state['current_session'] - 1) / collection_state['total_sessions'] * 100
        progress_var.set(progress)
        
        # 수집 시작
        auth.start_collection(user_id_var.get().strip())
        
        # 15초 후 자동 종료
        def auto_stop():
            time.sleep(15)
            if collection_state['collecting']:
                stop_collection_session()
        
        threading.Thread(target=auto_stop, daemon=True).start()
        return True
    
    def stop_collection_session():
        """단일 세션 수집 중지"""
        if not collection_state['collecting']:
            return
        
        collection_state['collecting'] = False
        session = auth.stop_collection()
        
        if session:
            collection_state['sessions_completed'].append(session)
            update_canvas_state('completed')
            
            # 진행률 업데이트
            progress = collection_state['current_session'] / collection_state['total_sessions'] * 100
            progress_var.set(progress)
            
            if collection_state['current_session'] >= collection_state['total_sessions']:
                # 모든 세션 완료
                status_var.set("모든 세션 완료! 등록 버튼을 눌러주세요.")
                start_button.configure(state='disabled')
                register_button.configure(state='normal')
            else:
                # 다음 세션 대기
                status_var.set(f"세션 {collection_state['current_session']}/{collection_state['total_sessions']} 완료. 다음 세션을 시작하세요.")
                start_button.configure(state='normal')
                
            # 2초 후 캔버스 상태 복원
            root.after(2000, lambda: update_canvas_state('ready'))
    
    def register_user():
        """사용자 등록"""
        try:
            register_button.configure(state='disabled')
            status_var.set("등록 중...")
            
            def do_register():
                try:
                    result = auth.register_user()
                    root.after(0, lambda: on_register_success(result))
                except Exception as e:
                    root.after(0, lambda: on_register_error(str(e)))
            
            threading.Thread(target=do_register, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("오류", f"등록 실패: {e}")
            register_button.configure(state='normal')
    
    def on_register_success(result):
        """등록 성공 콜백"""
        status_var.set("등록 완료!")
        progress_var.set(100)
        messagebox.showinfo("성공", f"사용자 '{user_id_var.get()}' 등록이 완료되었습니다!\n\n등록된 패턴: {len(collection_state['sessions_completed'])}개 세션")
        root.destroy()
    
    def on_register_error(error_msg):
        """등록 실패 콜백"""
        status_var.set("등록 실패")
        messagebox.showerror("오류", f"등록 실패: {error_msg}")
        register_button.configure(state='normal')
    
    def reset_registration():
        """등록 초기화"""
        collection_state['current_session'] = 0
        collection_state['collecting'] = False
        collection_state['sessions_completed'] = []
        auth.clear_sessions()
        
        progress_var.set(0)
        status_var.set("등록할 준비가 되었습니다")
        update_canvas_state('ready')
        
        start_button.configure(state='normal')
        register_button.configure(state='disabled')
    
    # 세션 수 변경 시 업데이트
    def on_session_count_change():
        collection_state['total_sessions'] = int(session_count_var.get())
        reset_registration()
    
    session_count_spinbox.configure(command=on_session_count_change)
    
    # 버튼 프레임
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(0, 10))
    
    start_button = ttk.Button(button_frame, text="🎯 세션 시작", 
                             command=start_collection_session, style='Primary.TButton')
    start_button.pack(side=tk.LEFT, padx=(0, 10))
    
    stop_button = ttk.Button(button_frame, text="⏹️ 세션 중지", 
                            command=stop_collection_session, style='Action.TButton')
    stop_button.pack(side=tk.LEFT, padx=(0, 10))
    
    register_button = ttk.Button(button_frame, text="📝 등록하기", 
                               command=register_user, style='Action.TButton', state='disabled')
    register_button.pack(side=tk.LEFT, padx=(0, 10))
    
    reset_button = ttk.Button(button_frame, text="🔄 초기화", 
                            command=reset_registration, style='Action.TButton')
    reset_button.pack(side=tk.LEFT)
    
    # 도움말 프레임
    help_frame = ttk.LabelFrame(main_frame, text="도움말", padding="10")
    help_frame.pack(fill=tk.X)
    
    help_text = """
    1. 사용자 ID를 입력하고 학습 세션 수를 선택하세요
    2. '세션 시작' 버튼을 누르고 마우스를 자연스럽게 움직이세요
    3. 각 세션은 15초간 진행되며, 다양한 마우스 동작을 해보세요
    4. 모든 세션이 완료되면 '등록하기' 버튼을 눌러 등록하세요
    """
    
    ttk.Label(help_frame, text=help_text, style='Subtitle.TLabel', justify=tk.LEFT).pack(anchor=tk.W)
    
    # 포커스 설정
    canvas.focus_set()
    
    return root

def create_authentication_ui(server_url="http://localhost:8000"):
    """
    사용자 인증 UI 창 생성
    
    Args:
        server_url: 인증 서버 URL
    
    Returns:
        root 윈도우
    """
    root = tk.Tk()
    root.title("마우스 패턴 인증")
    root.geometry("600x500")
    root.resizable(False, False)
    
    # 스타일 적용
    create_modern_style(root)
    
    # 메인 프레임
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 제목
    title_label = ttk.Label(main_frame, text="🔐 마우스 패턴 인증", style='Title.TLabel')
    title_label.pack(pady=(0, 10))
    
    subtitle_label = ttk.Label(main_frame, 
                              text="등록된 마우스 패턴으로 본인 인증을 수행합니다", 
                              style='Subtitle.TLabel')
    subtitle_label.pack(pady=(0, 20))
    
    # 사용자 정보 입력 프레임
    info_frame = ttk.LabelFrame(main_frame, text="인증 정보", padding="15")
    info_frame.pack(fill=tk.X, pady=(0, 15))
    
    # 사용자 ID 입력
    ttk.Label(info_frame, text="사용자 ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
    user_id_var = tk.StringVar()
    user_id_entry = ttk.Entry(info_frame, textvariable=user_id_var, width=30, font=('Arial', 11))
    user_id_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
    
    # 인증 임계값 설정
    ttk.Label(info_frame, text="인증 임계값:").grid(row=1, column=0, sticky=tk.W, pady=5)
    threshold_var = tk.DoubleVar(value=0.7)
    threshold_scale = ttk.Scale(info_frame, from_=0.1, to=1.0, variable=threshold_var, 
                               orient=tk.HORIZONTAL, length=200)
    threshold_scale.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.W)
    
    threshold_label = ttk.Label(info_frame, text="0.70")
    threshold_label.grid(row=1, column=2, padx=(10, 0), pady=5)
    
    def update_threshold_label(*args):
        threshold_label.config(text=f"{threshold_var.get():.2f}")
    
    threshold_var.trace('w', update_threshold_label)
    
    # 패턴 수집 영역
    pattern_frame = ttk.LabelFrame(main_frame, text="인증 패턴 수집", padding="15")
    pattern_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    
    # 추적 캔버스
    canvas = tk.Canvas(pattern_frame, width=500, height=200, bg='#bdc3c7', 
                      relief=tk.SUNKEN, bd=2, highlightthickness=0)
    canvas.pack(pady=10)
    
    # 캔버스 초기 텍스트
    canvas_text = canvas.create_text(250, 100, 
                                   text="🔒 인증 패턴 수집 영역\n\n등록할 때와 같은 방식으로\n마우스를 움직여주세요", 
                                   fill='#2c3e50', font=('Arial', 12), justify=tk.CENTER)
    
    # 인증 객체 생성
    auth = MousePatternAuth(server_url=server_url)
    auth.set_tracking_widget(canvas)
    
    # 상태 표시
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=(0, 15))
    
    status_var = tk.StringVar(value="인증할 준비가 되었습니다")
    status_label = ttk.Label(status_frame, textvariable=status_var, style='Status.TLabel')
    status_label.pack(side=tk.LEFT)
    
    # 타이머 표시
    timer_var = tk.StringVar(value="")
    timer_label = ttk.Label(status_frame, textvariable=timer_var, style='Warning.TLabel')
    timer_label.pack(side=tk.RIGHT)
    
    # 인증 상태 변수
    auth_state = {
        'collecting': False,
        'timer_thread': None,
        'collection_time': 10  # 10초간 수집
    }
    
    def update_canvas_state(state):
        """캔버스 상태 업데이트"""
        if state == 'ready':
            canvas.configure(bg='#bdc3c7')
            canvas.itemconfig(canvas_text, text="🔒 인증 패턴 수집 영역\n\n등록할 때와 같은 방식으로\n마우스를 움직여주세요")
        elif state == 'collecting':
            canvas.configure(bg='#ffeb3b')
            canvas.itemconfig(canvas_text, text="🔴 인증 패턴 수집 중...\n\n평소와 같이 자연스럽게\n마우스를 움직여주세요")
        elif state == 'success':
            canvas.configure(bg='#4caf50')
            canvas.itemconfig(canvas_text, text="✅ 인증 성공!\n\n패턴이 일치합니다")
        elif state == 'failure':
            canvas.configure(bg='#f44336')
            canvas.itemconfig(canvas_text, text="❌ 인증 실패\n\n패턴이 일치하지 않습니다")
    
    def start_timer():
        """타이머 시작"""
        def timer_countdown():
            remaining = auth_state['collection_time']
            while remaining > 0 and auth_state['collecting']:
                root.after(0, lambda t=remaining: timer_var.set(f"{t}초 남음"))
                time.sleep(1)
                remaining -= 1
            
            if auth_state['collecting']:
                root.after(0, stop_authentication_collection)
        
        auth_state['timer_thread'] = threading.Thread(target=timer_countdown, daemon=True)
        auth_state['timer_thread'].start()
    
    def start_authentication_collection():
        """인증 패턴 수집 시작"""
        if not user_id_var.get().strip():
            messagebox.showerror("오류", "사용자 ID를 입력해주세요.")
            return
        
        auth_state['collecting'] = True
        
        # UI 업데이트
        update_canvas_state('collecting')
        status_var.set("인증 패턴 수집 중...")
        
        # 수집 시작
        auth.start_collection(user_id_var.get().strip())
        
        # 타이머 시작
        start_timer()
        
        # 버튼 상태 변경
        start_auth_button.configure(state='disabled')
        stop_auth_button.configure(state='normal')
    
    def stop_authentication_collection():
        """인증 패턴 수집 중지"""
        if not auth_state['collecting']:
            return
        
        auth_state['collecting'] = False
        timer_var.set("")
        
        session = auth.stop_collection()
        
        if session:
            # 자동으로 인증 수행
            perform_authentication()
        
        # 버튼 상태 변경
        start_auth_button.configure(state='normal')
        stop_auth_button.configure(state='disabled')
    
    def perform_authentication():
        """인증 수행"""
        try:
            status_var.set("인증 중...")
            
            def do_authenticate():
                try:
                    result = auth.authenticate_user(threshold=threshold_var.get())
                    root.after(0, lambda: on_authentication_result(result))
                except Exception as e:
                    root.after(0, lambda: on_authentication_error(str(e)))
            
            threading.Thread(target=do_authenticate, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("오류", f"인증 실패: {e}")
    
    def on_authentication_result(result):
        """인증 결과 콜백"""
        if result['success']:
            update_canvas_state('success')
            status_var.set(f"인증 성공! (신뢰도: {result['confidence']:.2f})")
            messagebox.showinfo("인증 성공", 
                              f"사용자 '{user_id_var.get()}' 인증이 성공했습니다!\n\n"
                              f"신뢰도: {result['confidence']:.2f}\n"
                              f"임계값: {threshold_var.get():.2f}")
        else:
            update_canvas_state('failure')
            status_var.set(f"인증 실패 (신뢰도: {result['confidence']:.2f})")
            messagebox.showwarning("인증 실패", 
                                 f"인증에 실패했습니다.\n\n"
                                 f"신뢰도: {result['confidence']:.2f}\n"
                                 f"임계값: {threshold_var.get():.2f}\n\n"
                                 f"다시 시도해보세요.")
        
        # 3초 후 상태 복원
        root.after(3000, lambda: (update_canvas_state('ready'), 
                                 status_var.set("인증할 준비가 되었습니다")))
    
    def on_authentication_error(error_msg):
        """인증 오류 콜백"""
        update_canvas_state('failure')
        status_var.set("인증 오류")
        messagebox.showerror("오류", f"인증 중 오류가 발생했습니다: {error_msg}")
        
        # 3초 후 상태 복원
        root.after(3000, lambda: (update_canvas_state('ready'), 
                                 status_var.set("인증할 준비가 되었습니다")))
    
    # 버튼 프레임
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(0, 10))
    
    start_auth_button = ttk.Button(button_frame, text="🔍 인증 시작", 
                                  command=start_authentication_collection, style='Primary.TButton')
    start_auth_button.pack(side=tk.LEFT, padx=(0, 10))
    
    stop_auth_button = ttk.Button(button_frame, text="⏹️ 인증 중지", 
                                 command=stop_authentication_collection, style='Action.TButton', 
                                 state='disabled')
    stop_auth_button.pack(side=tk.LEFT, padx=(0, 10))
    
    # 도움말 프레임
    help_frame = ttk.LabelFrame(main_frame, text="도움말", padding="10")
    help_frame.pack(fill=tk.X)
    
    help_text = """
    1. 등록된 사용자 ID를 입력하세요
    2. 필요에 따라 인증 임계값을 조정하세요 (높을수록 엄격)
    3. '인증 시작' 버튼을 누르고 등록할 때와 같은 방식으로 마우스를 움직이세요
    4. 10초간 패턴을 수집한 후 자동으로 인증 결과를 확인합니다
    """
    
    ttk.Label(help_frame, text=help_text, style='Subtitle.TLabel', justify=tk.LEFT).pack(anchor=tk.W)
    
    # 포커스 설정
    canvas.focus_set()
    
    return root

def create_main_menu():
    """메인 메뉴 창 생성"""
    root = tk.Tk()
    root.title("마우스 패턴 인증 시스템")
    root.geometry("400x300")
    root.resizable(False, False)
    
    # 스타일 적용
    create_modern_style(root)
    
    # 메인 프레임
    main_frame = ttk.Frame(root, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 제목
    title_label = ttk.Label(main_frame, text="🖱️ 마우스 패턴 인증", style='Title.TLabel')
    title_label.pack(pady=(0, 20))
    
    subtitle_label = ttk.Label(main_frame, 
                              text="마우스 움직임 패턴을 이용한 생체 인증 시스템", 
                              style='Subtitle.TLabel')
    subtitle_label.pack(pady=(0, 30))
    
    # 서버 URL 입력
    url_frame = ttk.LabelFrame(main_frame, text="서버 설정", padding="10")
    url_frame.pack(fill=tk.X, pady=(0, 20))
    
    ttk.Label(url_frame, text="서버 URL:").pack(anchor=tk.W)
    server_url_var = tk.StringVar(value="http://localhost:8000")
    server_url_entry = ttk.Entry(url_frame, textvariable=server_url_var, width=40)
    server_url_entry.pack(fill=tk.X, pady=(5, 0))
    
    # 버튼들
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(expand=True)
    
    def open_registration():
        """등록 창 열기"""
        reg_window = create_registration_ui(server_url_var.get())
        reg_window.mainloop()
    
    def open_authentication():
        """인증 창 열기"""
        auth_window = create_authentication_ui(server_url_var.get())
        auth_window.mainloop()
    
    def exit_application():
        """애플리케이션 종료"""
        root.destroy()
    
    # 큰 버튼들
    register_button = ttk.Button(button_frame, text="📝 사용자 등록", 
                               command=open_registration, style='Primary.TButton')
    register_button.pack(pady=10, fill=tk.X)
    
    auth_button = ttk.Button(button_frame, text="🔐 사용자 인증", 
                           command=open_authentication, style='Primary.TButton')
    auth_button.pack(pady=10, fill=tk.X)
    
    exit_button = ttk.Button(button_frame, text="🚪 종료", 
                           command=exit_application, style='Action.TButton')
    exit_button.pack(pady=10, fill=tk.X)
    
    # 정보 표시
    info_frame = ttk.Frame(main_frame)
    info_frame.pack(fill=tk.X, pady=(20, 0))
    
    info_text = "v1.0 - 마우스 패턴 기반 생체 인증 시스템"
    ttk.Label(info_frame, text=info_text, style='Subtitle.TLabel').pack()
    
    return root

def create_user_management_ui(server_url="http://localhost:8000"):
    """
    사용자 관리 UI 창 생성
    
    Args:
        server_url: 인증 서버 URL
    
    Returns:
        root 윈도우
    """
    root = tk.Tk()
    root.title("사용자 관리")
    root.geometry("600x400")
    root.resizable(True, True)
    
    # 스타일 적용
    create_modern_style(root)
    
    # 메인 프레임
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 제목
    title_label = ttk.Label(main_frame, text="👥 사용자 관리", style='Title.TLabel')
    title_label.pack(pady=(0, 10))
    
    # 사용자 검색/조회 프레임
    search_frame = ttk.LabelFrame(main_frame, text="사용자 검색", padding="10")
    search_frame.pack(fill=tk.X, pady=(0, 15))
    
    ttk.Label(search_frame, text="사용자 ID:").pack(side=tk.LEFT)
    user_id_var = tk.StringVar()
    user_id_entry = ttk.Entry(search_frame, textvariable=user_id_var, width=30)
    user_id_entry.pack(side=tk.LEFT, padx=(10, 10))
    
    # 인증 객체 생성
    auth = MousePatternAuth(server_url=server_url)
    
    def search_user():
        """사용자 검색"""
        user_id = user_id_var.get().strip()
        if not user_id:
            messagebox.showerror("오류", "사용자 ID를 입력해주세요.")
            return
        
        try:
            result = auth.get_user_status(user_id)
            
            # 결과 표시
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"사용자 ID: {user_id}\n")
            result_text.insert(tk.END, f"등록 상태: {'등록됨' if result.get('registered', False) else '미등록'}\n")
            result_text.insert(tk.END, f"등록 일시: {result.get('registration_date', 'N/A')}\n")
            result_text.insert(tk.END, f"학습 세션 수: {result.get('session_count', 0)}\n")
            result_text.insert(tk.END, f"마지막 인증: {result.get('last_authentication', 'N/A')}\n")
            result_text.insert(tk.END, f"인증 성공률: {result.get('success_rate', 0):.1%}\n")
            
            delete_button.configure(state='normal')
            
        except Exception as e:
            messagebox.showerror("오류", f"사용자 조회 실패: {e}")
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"사용자 '{user_id}'를 찾을 수 없습니다.")
            delete_button.configure(state='disabled')
    
    def delete_user():
        """사용자 삭제"""
        user_id = user_id_var.get().strip()
        if not user_id:
            return
        
        if messagebox.askyesno("확인", f"사용자 '{user_id}'를 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다."):
            try:
                result = auth.delete_user(user_id)
                messagebox.showinfo("성공", f"사용자 '{user_id}'가 삭제되었습니다.")
                
                # 결과 창 초기화
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "사용자가 삭제되었습니다.")
                delete_button.configure(state='disabled')
                
            except Exception as e:
                messagebox.showerror("오류", f"사용자 삭제 실패: {e}")
    
    search_button = ttk.Button(search_frame, text="🔍 검색", command=search_user, style='Primary.TButton')
    search_button.pack(side=tk.LEFT, padx=(0, 10))
    
    delete_button = ttk.Button(search_frame, text="🗑️ 삭제", command=delete_user, 
                              style='Action.TButton', state='disabled')
    delete_button.pack(side=tk.LEFT)
    
    # 결과 표시 프레임
    result_frame = ttk.LabelFrame(main_frame, text="사용자 정보", padding="10")
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    
    # 텍스트 위젯과 스크롤바
    text_frame = ttk.Frame(result_frame)
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    result_text = tk.Text(text_frame, height=10, wrap=tk.WORD, font=('Arial', 10))
    scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=result_text.yview)
    result_text.configure(yscrollcommand=scrollbar.set)
    
    result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 초기 텍스트
    result_text.insert(tk.END, "사용자 ID를 입력하고 검색 버튼을 누르세요.")
    
    # 엔터 키로 검색
    user_id_entry.bind('<Return>', lambda e: search_user())
    
    return root

# 통합 실행 함수
def run_mouse_auth_demo():
    """마우스 패턴 인증 데모 실행"""
    try:
        main_window = create_main_menu()
        main_window.mainloop()
    except Exception as e:
        print(f"데모 실행 중 오류 발생: {e}")
        messagebox.showerror("오류", f"데모 실행 중 오류가 발생했습니다: {e}")

def create_quick_test_ui(server_url="http://localhost:8000"):
    """
    빠른 테스트용 UI (등록과 인증을 한 창에서)
    
    Args:
        server_url: 인증 서버 URL
    
    Returns:
        root 윈도우
    """
    root = tk.Tk()
    root.title("마우스 패턴 빠른 테스트")
    root.geometry("700x600")
    root.resizable(False, False)
    
    # 스타일 적용
    create_modern_style(root)
    
    # 메인 프레임
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 제목
    title_label = ttk.Label(main_frame, text="⚡ 빠른 테스트", style='Title.TLabel')
    title_label.pack(pady=(0, 10))
    
    # 사용자 ID 입력
    info_frame = ttk.LabelFrame(main_frame, text="테스트 정보", padding="10")
    info_frame.pack(fill=tk.X, pady=(0, 15))
    
    ttk.Label(info_frame, text="사용자 ID:").pack(side=tk.LEFT)
    user_id_var = tk.StringVar(value="test_user")
    user_id_entry = ttk.Entry(info_frame, textvariable=user_id_var, width=20)
    user_id_entry.pack(side=tk.LEFT, padx=(10, 20))
    
    # 상태 표시
    status_var = tk.StringVar(value="테스트 준비됨")
    status_label = ttk.Label(info_frame, textvariable=status_var, style='Status.TLabel')
    status_label.pack(side=tk.LEFT)
    
    # 패턴 수집 영역
    pattern_frame = ttk.LabelFrame(main_frame, text="패턴 수집 영역", padding="10")
    pattern_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    
    canvas = tk.Canvas(pattern_frame, width=600, height=200, bg='#ecf0f1', 
                      relief=tk.SUNKEN, bd=2, highlightthickness=0)
    canvas.pack(pady=10)
    
    canvas_text = canvas.create_text(300, 100, 
                                   text="🖱️ 마우스 패턴 수집 영역\n\n버튼을 눌러 테스트를 시작하세요", 
                                   fill='#2c3e50', font=('Arial', 12), justify=tk.CENTER)
    
    # 인증 객체 생성
    auth = MousePatternAuth(server_url=server_url)
    auth.set_tracking_widget(canvas)
    
    # 테스트 상태
    test_state = {
        'phase': 'ready',  # ready, register, authenticate
        'collecting': False,
        'registration_sessions': [],
        'collection_timer': None
    }
    
    def update_canvas_state(state, text=""):
        """캔버스 상태 업데이트"""
        colors = {
            'ready': '#ecf0f1',
            'register': '#e8f5e8',
            'authenticate': '#fff3e0',
            'success': '#e8f5e8',
            'failure': '#ffebee'
        }
        
        canvas.configure(bg=colors.get(state, '#ecf0f1'))
        if text:
            canvas.itemconfig(canvas_text, text=text)
    
    def start_collection_timer(duration, callback):
        """수집 타이머 시작"""
        def countdown():
            remaining = duration
            while remaining > 0 and test_state['collecting']:
                root.after(0, lambda t=remaining: canvas.itemconfig(canvas_text, 
                    text=f"🔴 수집 중... ({t}초 남음)\n\n자연스럽게 마우스를 움직여주세요"))
                time.sleep(1)
                remaining -= 1
            
            if test_state['collecting']:
                root.after(0, callback)
        
        test_state['collection_timer'] = threading.Thread(target=countdown, daemon=True)
        test_state['collection_timer'].start()
    
    def quick_register():
        """빠른 등록"""
        user_id = user_id_var.get().strip()
        if not user_id:
            messagebox.showerror("오류", "사용자 ID를 입력해주세요.")
            return
        
        test_state['phase'] = 'register'
        test_state['collecting'] = True
        test_state['registration_sessions'] = []
        
        update_canvas_state('register')
        status_var.set("등록용 패턴 수집 중...")
        
        # 수집 시작
        auth.start_collection(user_id)
        
        # 10초 타이머
        start_collection_timer(10, finish_registration)
        
        # 버튼 상태 변경
        register_button.configure(state='disabled')
        auth_button.configure(state='disabled')
    
    def finish_registration():
        """등록 완료"""
        test_state['collecting'] = False
        session = auth.stop_collection()
        
        if session:
            test_state['registration_sessions'].append(session)
            
            try:
                # 서버에 등록
                result = auth.register_user()
                
                update_canvas_state('success', "✅ 등록 완료!\n\n이제 인증을 테스트해보세요")
                status_var.set("등록 완료 - 인증 테스트 가능")
                
                # 버튼 상태 변경
                register_button.configure(state='normal')
                auth_button.configure(state='normal')
                
                messagebox.showinfo("성공", "등록이 완료되었습니다!\n이제 인증을 테스트해보세요.")
                
            except Exception as e:
                update_canvas_state('failure', f"❌ 등록 실패\n\n{str(e)}")
                status_var.set("등록 실패")
                messagebox.showerror("오류", f"등록 실패: {e}")
                
                # 버튼 상태 복원
                register_button.configure(state='normal')
                auth_button.configure(state='normal')
        
        test_state['phase'] = 'ready'
    
    def quick_authenticate():
        """빠른 인증"""
        user_id = user_id_var.get().strip()
        if not user_id:
            messagebox.showerror("오류", "사용자 ID를 입력해주세요.")
            return
        
        test_state['phase'] = 'authenticate'
        test_state['collecting'] = True
        
        update_canvas_state('authenticate')
        status_var.set("인증용 패턴 수집 중...")
        
        # 수집 시작
        auth.start_collection(user_id)
        
        # 8초 타이머
        start_collection_timer(8, finish_authentication)
        
        # 버튼 상태 변경
        register_button.configure(state='disabled')
        auth_button.configure(state='disabled')
    
    def finish_authentication():
        """인증 완료"""
        test_state['collecting'] = False
        session = auth.stop_collection()
        
        if session:
            try:
                # 서버에서 인증
                result = auth.authenticate_user(threshold=0.6)
                
                if result['success']:
                    update_canvas_state('success', 
                        f"✅ 인증 성공!\n\n신뢰도: {result['confidence']:.2f}")
                    status_var.set(f"인증 성공 (신뢰도: {result['confidence']:.2f})")
                    messagebox.showinfo("인증 성공", 
                        f"인증에 성공했습니다!\n신뢰도: {result['confidence']:.2f}")
                else:
                    update_canvas_state('failure', 
                        f"❌ 인증 실패\n\n신뢰도: {result['confidence']:.2f}")
                    status_var.set(f"인증 실패 (신뢰도: {result['confidence']:.2f})")
                    messagebox.showwarning("인증 실패", 
                        f"인증에 실패했습니다.\n신뢰도: {result['confidence']:.2f}")
                
            except Exception as e:
                update_canvas_state('failure', f"❌ 인증 오류\n\n{str(e)}")
                status_var.set("인증 오류")
                messagebox.showerror("오류", f"인증 중 오류: {e}")
        
        # 버튼 상태 복원
        register_button.configure(state='normal')
        auth_button.configure(state='normal')
        
        test_state['phase'] = 'ready'
        
        # 3초 후 초기 상태로
        root.after(3000, lambda: (
            update_canvas_state('ready', "🖱️ 마우스 패턴 수집 영역\n\n버튼을 눌러 테스트를 시작하세요"),
            status_var.set("테스트 준비됨")
        ))
    
    # 버튼 프레임
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(0, 10))
    
    register_button = ttk.Button(button_frame, text="📝 빠른 등록 (10초)", 
                               command=quick_register, style='Primary.TButton')
    register_button.pack(side=tk.LEFT, padx=(0, 10))
    
    auth_button = ttk.Button(button_frame, text="🔐 빠른 인증 (8초)", 
                           command=quick_authenticate, style='Primary.TButton')
    auth_button.pack(side=tk.LEFT, padx=(0, 10))
    
    # 도움말
    help_frame = ttk.LabelFrame(main_frame, text="빠른 테스트 가이드", padding="10")
    help_frame.pack(fill=tk.X)
    
    help_text = """
    1. 사용자 ID를 입력하세요 (기본값: test_user)
    2. '빠른 등록' 버튼을 눌러 10초간 마우스 패턴을 등록하세요
    3. 등록 완료 후 '빠른 인증' 버튼을 눌러 8초간 인증 테스트를 하세요
    4. 인증 결과를 확인하세요
    """
    
    ttk.Label(help_frame, text=help_text, style='Subtitle.TLabel', justify=tk.LEFT).pack(anchor=tk.W)
    
    # 포커스 설정
    canvas.focus_set()
    
    return root

# 메인 실행 함수들
if __name__ == "__main__":
    # 사용 예시
    print("마우스 패턴 인증 UI 데모")
    print("1. 메인 메뉴: run_mouse_auth_demo()")
    print("2. 등록 UI: create_registration_ui()")
    print("3. 인증 UI: create_authentication_ui()")
    print("4. 빠른 테스트: create_quick_test_ui()")
    print("5. 사용자 관리: create_user_management_ui()")
    
    # 메인 메뉴 실행
    run_mouse_auth_demo()