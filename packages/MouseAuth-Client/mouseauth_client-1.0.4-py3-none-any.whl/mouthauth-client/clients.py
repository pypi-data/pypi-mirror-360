"""
Mouse Pattern Authentication API Client
========================================

A Python client library for mouse pattern-based user authentication.
Collects mouse movement patterns and communicates with authentication server.

Usage:
    from mouse_pattern_auth import MousePatternAuth
    
    # Initialize
    auth = MousePatternAuth(server_url="http://localhost:8000")
    
    # Start collecting patterns
    auth.start_collection(user_id="user123")
    
    # Your GUI code here...
    
    # Stop collection and register
    auth.stop_collection()
    auth.register_user()
"""

import tkinter as tk
from tkinter import ttk
import time
import json
import requests
import threading
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, asdict
import uuid
import os
from datetime import datetime
import queue
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MouseEvent:
    """마우스 이벤트 데이터 클래스"""
    timestamp: float
    x: int
    y: int
    event_type: str
    button: Optional[str] = None
    key: Optional[str] = None
    scroll_delta: Optional[int] = None
    pressure: Optional[float] = None
    tilt_x: Optional[float] = None
    tilt_y: Optional[float] = None

@dataclass
class MouseSession:
    """마우스 세션 데이터 클래스"""
    user_id: str
    session_id: str
    events: List[MouseEvent]
    duration: float
    metadata: Optional[Dict] = None

class MousePatternAuth:
    """
    마우스 패턴 인증 클라이언트
    
    이 클래스는 마우스 패턴을 수집하고 서버와 통신하여 
    사용자 인증을 수행하는 기능을 제공합니다.
    """
    
    def __init__(self, server_url: str = "http://localhost:8000", 
                 tracking_widget: Optional[tk.Widget] = None):
        """
        Args:
            server_url: 인증 서버 URL
            tracking_widget: 마우스 이벤트를 추적할 tkinter 위젯
        """
        self.server_url = server_url.rstrip('/')
        self.tracking_widget = tracking_widget
        self.session = requests.Session()
        self.session.timeout = 30
        
        # 수집 상태
        self.is_collecting = False
        self.current_events = []
        self.current_session_id = None
        self.start_time = None
        self.user_id = None
        self.sessions = []
        
        # 콜백 함수들
        self.on_collection_start = None
        self.on_collection_stop = None
        self.on_event_collected = None
        self.on_authentication_result = None
        
        # 이벤트 큐 (thread-safe)
        self.event_queue = queue.Queue()
        self.processing_thread = None
        
    def set_tracking_widget(self, widget: tk.Widget):
        """추적할 위젯 설정"""
        self.tracking_widget = widget
        self._bind_events()
        
    def _bind_events(self):
        """위젯에 이벤트 바인딩"""
        if not self.tracking_widget:
            return
            
        # 마우스 이벤트
        self.tracking_widget.bind("<Motion>", self._on_mouse_move)
        self.tracking_widget.bind("<Button-1>", self._on_left_click)
        self.tracking_widget.bind("<Button-2>", self._on_middle_click)
        self.tracking_widget.bind("<Button-3>", self._on_right_click)
        self.tracking_widget.bind("<B1-Motion>", self._on_drag)
        self.tracking_widget.bind("<MouseWheel>", self._on_scroll)
        
        # 키보드 이벤트
        self.tracking_widget.bind("<KeyPress>", self._on_key_press)
        
        # 포커스 이벤트
        self.tracking_widget.bind("<FocusIn>", self._on_focus_in)
        self.tracking_widget.bind("<FocusOut>", self._on_focus_out)
        
    def start_collection(self, user_id: str, session_metadata: Optional[Dict] = None):
        """
        마우스 패턴 수집 시작
        
        Args:
            user_id: 사용자 ID
            session_metadata: 세션 메타데이터
        """
        if self.is_collecting:
            logger.warning("이미 수집 중입니다.")
            return
            
        self.user_id = user_id
        self.is_collecting = True
        self.current_events = []
        self.current_session_id = str(uuid.uuid4())
        self.start_time = time.time()
        
        # 처리 스레드 시작
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        
        logger.info(f"사용자 {user_id}의 패턴 수집 시작")
        
        if self.on_collection_start:
            self.on_collection_start(user_id, self.current_session_id)
    
    def stop_collection(self) -> Optional[MouseSession]:
        """
        마우스 패턴 수집 중지
        
        Returns:
            수집된 세션 데이터
        """
        if not self.is_collecting:
            logger.warning("수집 중이 아닙니다.")
            return None
            
        self.is_collecting = False
        duration = time.time() - self.start_time
        
        # 큐에 남은 이벤트 처리
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                self.current_events.append(event)
            except queue.Empty:
                break
        
        # 세션 생성
        session = MouseSession(
            user_id=self.user_id,
            session_id=self.current_session_id,
            events=self.current_events.copy(),
            duration=duration,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "event_count": len(self.current_events),
                "collection_duration": duration
            }
        )
        
        self.sessions.append(session)
        
        logger.info(f"패턴 수집 완료: {len(self.current_events)}개 이벤트, {duration:.1f}초")
        
        if self.on_collection_stop:
            self.on_collection_stop(session)
            
        return session
    
    def _process_events(self):
        """이벤트 처리 스레드"""
        while self.is_collecting:
            try:
                event = self.event_queue.get(timeout=0.1)
                self.current_events.append(event)
                
                if self.on_event_collected:
                    self.on_event_collected(event)
                    
            except queue.Empty:
                continue
    
    def _create_event(self, event_type: str, x: int, y: int, **kwargs) -> MouseEvent:
        """마우스 이벤트 생성"""
        return MouseEvent(
            timestamp=time.time(),
            x=x,
            y=y,
            event_type=event_type,
            **kwargs
        )
    
    def _on_mouse_move(self, event):
        """마우스 이동 이벤트"""
        if self.is_collecting:
            mouse_event = self._create_event("move", event.x, event.y)
            self.event_queue.put(mouse_event)
    
    def _on_left_click(self, event):
        """좌클릭 이벤트"""
        if self.is_collecting:
            mouse_event = self._create_event("click", event.x, event.y, button="left")
            self.event_queue.put(mouse_event)
    
    def _on_middle_click(self, event):
        """중간클릭 이벤트"""
        if self.is_collecting:
            mouse_event = self._create_event("click", event.x, event.y, button="middle")
            self.event_queue.put(mouse_event)
    
    def _on_right_click(self, event):
        """우클릭 이벤트"""
        if self.is_collecting:
            mouse_event = self._create_event("click", event.x, event.y, button="right")
            self.event_queue.put(mouse_event)
    
    def _on_drag(self, event):
        """드래그 이벤트"""
        if self.is_collecting:
            mouse_event = self._create_event("drag", event.x, event.y, button="left")
            self.event_queue.put(mouse_event)
    
    def _on_scroll(self, event):
        """스크롤 이벤트"""
        if self.is_collecting:
            mouse_event = self._create_event("scroll", event.x, event.y, 
                                           scroll_delta=event.delta)
            self.event_queue.put(mouse_event)
    
    def _on_key_press(self, event):
        """키보드 이벤트"""
        if self.is_collecting:
            mouse_event = self._create_event("key", 0, 0, key=event.keysym)
            self.event_queue.put(mouse_event)
    
    def _on_focus_in(self, event):
        """포커스 인 이벤트"""
        if self.is_collecting:
            mouse_event = self._create_event("focus", 0, 0, key="focus_in")
            self.event_queue.put(mouse_event)
    
    def _on_focus_out(self, event):
        """포커스 아웃 이벤트"""
        if self.is_collecting:
            mouse_event = self._create_event("focus", 0, 0, key="focus_out")
            self.event_queue.put(mouse_event)
    
    def register_user(self, user_id: Optional[str] = None, 
                     sessions: Optional[List[MouseSession]] = None) -> Dict:
        """
        사용자 등록
        
        Args:
            user_id: 사용자 ID (None이면 현재 사용자 ID 사용)
            sessions: 세션 리스트 (None이면 현재 세션들 사용)
        
        Returns:
            서버 응답
        """
        if user_id is None:
            user_id = self.user_id
        if sessions is None:
            sessions = self.sessions
            
        if not user_id:
            raise ValueError("사용자 ID가 필요합니다.")
        if not sessions:
            raise ValueError("등록할 세션이 없습니다.")
        
        # 세션 데이터를 딕셔너리로 변환
        sessions_data = []
        for session in sessions:
            session_dict = asdict(session)
            # 이벤트들도 딕셔너리로 변환
            session_dict['events'] = [asdict(event) for event in session.events]
            sessions_data.append(session_dict)
        
        payload = {
            "user_id": user_id,
            "sessions": sessions_data
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/register",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"사용자 {user_id} 등록 성공")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"등록 실패: {e}")
            raise
    
    def authenticate_user(self, user_id: Optional[str] = None, 
                         events: Optional[List[MouseEvent]] = None,
                         threshold: float = 0.7) -> Dict:
        """
        사용자 인증
        
        Args:
            user_id: 사용자 ID
            events: 인증용 이벤트 리스트
            threshold: 인증 임계값
        
        Returns:
            인증 결과
        """
        if user_id is None:
            user_id = self.user_id
        if events is None:
            events = self.current_events
            
        if not user_id:
            raise ValueError("사용자 ID가 필요합니다.")
        if not events:
            raise ValueError("인증할 이벤트가 없습니다.")
        
        # 이벤트를 딕셔너리로 변환
        events_data = [asdict(event) for event in events]
        
        payload = {
            "user_id": user_id,
            "events": events_data,
            "threshold": threshold
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/authenticate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"사용자 {user_id} 인증 결과: {result['success']}")
            
            if self.on_authentication_result:
                self.on_authentication_result(result)
                
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"인증 실패: {e}")
            raise
    
    def get_user_status(self, user_id: str) -> Dict:
        """
        사용자 상태 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            사용자 상태 정보
        """
        try:
            response = self.session.get(f"{self.server_url}/users/{user_id}/status")
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"상태 조회 실패: {e}")
            raise
    
    def delete_user(self, user_id: str) -> Dict:
        """
        사용자 삭제
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            삭제 결과
        """
        try:
            response = self.session.delete(f"{self.server_url}/users/{user_id}")
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"사용자 삭제 실패: {e}")
            raise
    
    def save_sessions(self, filepath: str, sessions: Optional[List[MouseSession]] = None):
        """
        세션을 파일로 저장
        
        Args:
            filepath: 저장할 파일 경로
            sessions: 저장할 세션 리스트
        """
        if sessions is None:
            sessions = self.sessions
        
        sessions_data = []
        for session in sessions:
            session_dict = asdict(session)
            session_dict['events'] = [asdict(event) for event in session.events]
            sessions_data.append(session_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sessions_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"세션 저장 완료: {filepath}")
    
    def load_sessions(self, filepath: str) -> List[MouseSession]:
        """
        파일에서 세션 로드
        
        Args:
            filepath: 로드할 파일 경로
        
        Returns:
            로드된 세션 리스트
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            sessions_data = json.load(f)
        
        sessions = []
        for session_dict in sessions_data:
            # 이벤트들을 MouseEvent 객체로 변환
            events = [MouseEvent(**event_dict) for event_dict in session_dict['events']]
            session_dict['events'] = events
            sessions.append(MouseSession(**session_dict))
        
        self.sessions = sessions
        logger.info(f"세션 로드 완료: {len(sessions)}개 세션")
        return sessions
    
    def clear_sessions(self):
        """모든 세션 삭제"""
        self.sessions = []
        self.current_events = []
        logger.info("세션 초기화 완료")
    
    def get_stats(self) -> Dict:
        """통계 정보 반환"""
        total_events = sum(len(session.events) for session in self.sessions)
        total_duration = sum(session.duration for session in self.sessions)
        
        return {
            "session_count": len(self.sessions),
            "total_events": total_events,
            "total_duration": total_duration,
            "current_events": len(self.current_events),
            "is_collecting": self.is_collecting,
            "user_id": self.user_id
        }

# 편의 함수들
def create_tracking_widget(parent, width=400, height=300, bg='#808080') -> tk.Canvas:
    """
    마우스 추적을 위한 캔버스 위젯 생성
    
    Args:
        parent: 부모 위젯
        width: 캔버스 너비
        height: 캔버스 높이
        bg: 배경색
    
    Returns:
        설정된 캔버스 위젯
    """
    canvas = tk.Canvas(parent, width=width, height=height, bg=bg, 
                      relief=tk.SUNKEN, bd=2)
    
    # 안내 텍스트 추가
    canvas.create_text(width//2, height//2, 
                      text="마우스 패턴 수집 영역\n여기서 마우스를 움직여주세요", 
                      fill='white', font=('Arial', 12), justify=tk.CENTER)
    
    # 포커스 설정 (키보드 이벤트를 위해)
    canvas.focus_set()
    
    return canvas

def create_simple_demo():
    """간단한 데모 애플리케이션 생성"""
    root = tk.Tk()
    root.title("마우스 패턴 인증 데모")
    root.geometry("600x500")
    
    # 인증 객체 생성
    auth = MousePatternAuth()
    
    # UI 구성
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 사용자 ID 입력
    ttk.Label(main_frame, text="사용자 ID:").pack(anchor=tk.W)
    user_id_var = tk.StringVar()
    ttk.Entry(main_frame, textvariable=user_id_var, width=30).pack(anchor=tk.W, pady=5)
    
    # 추적 영역
    canvas = create_tracking_widget(main_frame)
    canvas.pack(pady=10)
    
    # 인증 객체에 위젯 설정
    auth.set_tracking_widget(canvas)
    
    # 제어 버튼
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=10)
    
    def start_collection():
        user_id = user_id_var.get().strip()
        if not user_id:
            tk.messagebox.showerror("오류", "사용자 ID를 입력하세요.")
            return
        auth.start_collection(user_id)
        status_var.set("수집 중...")
        canvas.configure(bg='#60a060')
    
    def stop_collection():
        session = auth.stop_collection()
        if session:
            status_var.set(f"수집 완료: {len(session.events)}개 이벤트")
            canvas.configure(bg='#808080')
    
    def register():
        try:
            result = auth.register_user()
            tk.messagebox.showinfo("성공", f"등록 성공: {result}")
        except Exception as e:
            tk.messagebox.showerror("오류", f"등록 실패: {e}")
    
    def authenticate():
        try:
            result = auth.authenticate_user()
            msg = f"인증 {'성공' if result['success'] else '실패'}\n신뢰도: {result['confidence']:.2f}"
            tk.messagebox.showinfo("인증 결과", msg)
        except Exception as e:
            tk.messagebox.showerror("오류", f"인증 실패: {e}")
    
    ttk.Button(button_frame, text="수집 시작", command=start_collection).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="수집 중지", command=stop_collection).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="등록", command=register).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="인증", command=authenticate).pack(side=tk.LEFT, padx=5)
    
    # 상태 표시
    status_var = tk.StringVar(value="준비됨")
    ttk.Label(main_frame, textvariable=status_var).pack(pady=5)
    
    return root, auth

if __name__ == "__main__":
    # 데모 실행
    root, auth = create_simple_demo()
    root.mainloop()