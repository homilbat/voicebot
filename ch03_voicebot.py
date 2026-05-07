
# from 패키지 import 클래스/함수 → 패키지 전체 대신 필요한 것만 가져옴


import streamlit as st
# streamlit: 웹 UI를 파이썬으로 쉽게 만들어주는 라이브러리


from audiorecorder import audiorecorder
# audiorecorder: 브라우저에서 마이크 녹음 버튼을 만들어주는 streamlit 전용 패키지
# from A import B → A 패키지 안의 B 함수/클래스만 가져옴

import openai
# openai: OpenAI의 GPT, Whisper 등 AI 모델 API를 호출하는 공식 라이브러리

import os
# os: 운영체제(OS) 기능을 다루는 표준 라이브러리
# 여기서는 파일 삭제(os.remove)에 사용

from datetime import datetime
# datetime 패키지 안의 datetime 클래스만 가져옴
# 현재 시각을 얻어 채팅 메시지 옆에 시간을 표시하는 데 사용

from gtts import gTTS
# gTTS(Google Text-to-Speech): 텍스트를 구글 TTS로 음성 파일로 변환해주는 라이브러리

import base64
# base64: 바이너리 데이터(음악 파일 등)를 텍스트로 인코딩하는 표준 라이브러리
# 음성 파일을 HTML에 직접 삽입할 때 필요



# STT 함수: 음성 → 텍스트 변환 (Speech To Text)
def STT(audio, apikey):
    # audio : audiorecorder가 녹음한 오디오 객체
    # apikey: OpenAI API 인증 키 (문자열)

    # 파일 저장
    filename = 'input.mp3'
    # 변수 filename에 저장할 파일 이름을 문자열로 지정

    audio.export(filename, format="mp3")
    # → 녹음된 오디오 객체를 mp3 형식으로 filename 경로에 저장

    # 음원 파일 열기
    audio_file = open(filename, "rb")
    # open(파일경로, 모드): 파일을 열어 파일 객체를 반환
    # "rb" → 파일을 바이너리(이진) 읽기 모드로 열기
    # 음악/이미지 같은 바이너리 파일은 반드시 "rb" 모드로 열어야 함

    # Whisper 모델을 활용해 텍스트 얻기
    client = openai.OpenAI(api_key=apikey)
    #OpenAI 클라이언트 객체 생성

    response = client.audio.transcriptions.create(
        model="whisper-1",  #음성인식(STT) 모델 이름
        file=audio_file     #변환할 오디오 파일 객체 전달
    )
    # transcriptions.create() → Whisper 모델에 오디오를 보내 텍스트로 변환 요청
    # response: API 서버가 돌려준 결과 객체

    audio_file.close()
    # 파일 객체를 명시적으로 닫음

    # 파일 삭제
    os.remove(filename)
    # os.remove(경로): 해당 경로의 파일을 삭제

    return response.text
    # Whisper가 인식한 텍스트 결과 (문자열)호출한 곳으로 돌려줌


# ask_gpt 함수: 텍스트 → GPT 답변 생성
def ask_gpt(prompt, model, apikey):
    # prompt: 대화 전체 기록 (리스트 형태) → GPT에게 맥락을 전달
    # model : 사용할 GPT 모델 이름 (예: "gpt-4")

    client = openai.OpenAI(api_key=apikey)
    # OpenAI 클라이언트 객체 생성 (STT 함수와 동일한 방식)

    response = client.chat.completions.create(
        model=model,      # 선택한 GPT 모델 사용
        messages=prompt   # 지금까지의 대화 내역 전달 (리스트)
    )
    # chat.completions.create() → GPT 모델에게 대화 기록을 주고 다음 답변 요청

    gptResponse = response.choices[0].message.content
    # response.choices[0]     → GPT가 생성한 후보 답변 리스트 중 인덱스 0 답변 선택
    # .message             → 해당 답변의 메시지 객체
    # .content             → 메시지 텍스트 내용 (문자열)
    # gptResponse 변수에 GPT의 최종 답변 텍스트를 저장


    return gptResponse
    # GPT 답변 문자열을 호출한 곳으로 반환



# TTS 함수: 텍스트 → 음성 재생 (Text To Speech)


def TTS(response):
    # response: GPT가 생성한 답변 텍스트 (문자열)

    # gTTS를 활용하여 음성 파일 생성
    filename = "output.mp3"
    # 저장할 음성 파일 이름 (고정값)

    tts = gTTS(text=response, lang="ko")
    # gTTS(text=..., lang="ko")→ 텍스트를 한국어("ko") 음성으로 변환할 준비를 하는 객체 생성 (lang="ko": 한국어 발음으로 읽어줌 (영어는 "en"))
    
    tts.save(filename)
    # tts.save(경로) → 변환된 음성을 mp3 파일로 저장

    # 음원 파일 자동 재생
    with open(filename, "rb") as f:
        # with open(파일경로, 모드) as 변수: → 파일을 열고 f 라는 이름으로 사용, 블록이 끝나면 자동으로 닫음
        # "rb" = read binary → 바이너리 읽기 모드

        data = f.read()
        # f.read() → 파일 전체를 바이트(bytes) 데이터로 읽음

        b64 = base64.b64encode(data).decode()
        # base64.b64encode(바이트) → 바이트 데이터를 base64 형식 바이트로 인코딩
        # .decode() → base64 바이트를 일반 문자열(str)로 변환
        # 결과: 음성 파일을 텍스트(문자열)로 표현 → HTML 태그 안에 직접 삽입 가능

        md = f"""
        <audio autoplay="True">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        
        # 삼중따옴표(""") → 여러 줄에 걸친 문자열(멀티라인 스트링)
        # <audio autoplay="True"> → 페이지 로딩 시 자동으로 음성 재생하는 HTML 태그
        # data:audio/mp3;base64,{b64} → 파일 없이 HTML에 오디오를 직접 삽입하는 방식
        # (Data URL 방식: 파일 경로 대신 파일 내용 자체를 텍스트로 넣음)

        st.markdown(md, unsafe_allow_html=True)
        # st.markdown(html문자열, unsafe_allow_html=True) → HTML 태그가 포함된 문자열을 그대로 렌더링(화면에 표시)
        # unsafe_allow_html=True 가 없으면 보안상 HTML 태그를 무시하고 텍스트로 출력


    os.remove(filename)
    # 재생이 끝난 임시 mp3 파일 삭제



# main 함수: 앱 전체 UI와 로직을 구성


def main():

    # 기본 설정
    st.set_page_config(
        page_title="음성 비서 프로그램 by 종혁",
        # page_title: 브라우저 탭에 표시될 제목
        layout="wide"
        # layout="wide" → 화면 전체 너비 사용 (기본값은 중앙 정렬 좁은 레이아웃)
    )

    # 제목
    st.header("음성 비서 프로그램 by 종혁")
    # st.header: 큰 제목 텍스트 표시 (HTML의 <h1> 수준)

    # 구분선
    st.markdown("---")
    # st.markdown("---") → 수평선(가로 구분선) 표시

    # 기본 설명
    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        # st.expander: 클릭하면 접었다 펼 수 있는 영역
        # with 문법: 들여쓰기 블록 안의 내용이 expander 안에 들어감
        # expanded=True → 앱 시작 시 기본으로 펼쳐진 상태
        st.write(
            """
            - 음성 비서 프로그램의 UI는 스트림릿을 활용했습니다.
            - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했습니다.
            - 답변은 OpenAI의 GPT 모델을 활용했습니다.
            - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했습니다.
            """
            # st.write: 텍스트/데이터를 화면에 출력
        )
        st.markdown("")  # 빈 줄(여백) 추가

    # 세션 상태(session_state) 초기 설정
    # st.session_state: Streamlit에서 페이지가 새로고침되어도 값을 유지시켜 주는 딕셔너리 (브라우저 세션 단위로 저장됨)
    # "키 not in 딕셔너리" → 해당 키가 딕셔너리에 없으면 True
    # 처음 앱 실행 시에만 초기값을 설정하고, 이미 있으면 건너뜀

    if "chat" not in st.session_state:
        st.session_state["chat"] = []
        # chat: 화면에 표시할 대화 기록
        # 빈 리스트([])로 시작 → [(발신자, 시간, 메시지), ...] 형태로 쌓임

    if "OPENAI_API" not in st.session_state:
        st.session_state["OPENAI_API"] = ""
        # OPENAI_API: 사용자가 입력한 OpenAI API 키를 세션에 저장
        # 초기값은 빈 문자열("")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}
        ]
        # messages: GPT API에 전달할 전체 대화 기록 (리스트)
        # 딕셔너리(dict) 문법: {"키": 값}
        # role: 메시지 발신자 유형
        #   "system"    → GPT에게 역할/규칙을 알려주는 설정 메시지
        #   "user"      → 사용자가 보낸 메시지
        #   "assistant" → GPT가 보낸 메시지
        # content: 실제 메시지 내용 (문자열)
        # 시스템 메시지를 첫 번째로 넣어 GPT에게 역할을 부여

    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False
        # check_reset: 초기화 버튼이 눌렸는지 여부를 나타내는 플래그(flag)
        # 불리언(bool) 타입: True(참) 또는 False(거짓)
        # False = 정상 동작 상태
        # True  = 초기화 버튼이 눌린 직후 → GPT 응답을 잠시 차단

    # 사이드바 생성
    # with st.sidebar: → 들여쓰기 블록 안의 위젯이 사이드바(왼쪽 패널)에 배치됨

    with st.sidebar:

        # OpenAI API 키 입력받기
        st.session_state["OPENAI_API"] = st.text_input(
            label=" OPENAI API 키",            # 입력창 위에 표시할 라벨
            placeholder="Enter Your API Key",  # 아무것도 입력 안 했을 때 흐리게 보이는 안내 텍스트
            value="",                          # 입력창의 초기값 (빈 문자열)
            type="password"                    # 입력 내용을 **** 로 가려서 보안 강화
        )
        # st.text_input(): 한 줄 텍스트 입력창 위젯
        # 반환값: 사용자가 입력한 문자열 → session_state["OPENAI_API"]에 바로 저장

        st.markdown("---")  # 구분선

        # GPT 모델을 선택하기 위한 라디오 버튼 생성
        model = st.radio(
            label="GPT 모델",                        # 라디오 그룹 제목
            options=["gpt-4", "gpt-3.5-turbo"]      # 선택 가능한 항목 리스트
        )
        # st.radio(): 여러 옵션 중 하나만 선택할 수 있는 라디오 버튼 위젯
        # 반환값(model): 사용자가 선택한 항목 문자열 (예: "gpt-4")

        st.markdown("---")  # 구분선

        # 리셋 버튼 생성
        if st.button(label="초기화"):
            # st.button(label): 버튼을 화면에 표시
            # 반환값: 버튼이 눌리면 True, 안 눌리면 False
            # if st.button(...): → 버튼이 눌린 순간에만 if 블록 실행

            # 리셋 코드
            st.session_state["chat"] = []
            # 화면에 표시되던 대화 내용을 빈 리스트로 초기화

            st.session_state["messages"] = [
                {"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}
            ]
            # GPT에게 보내는 대화 기록도 시스템 프롬프트만 남기고 초기화

            st.session_state["check_reset"] = True
            # 초기화가 됐음을 표시 → True로 설정
            # 이후 새 녹음이 들어오면 아래 코드에서 다시 False로 복원됨

            st.rerun()
            # 페이지를 즉시 새로고침하여 초기화된 UI를 바로 반영
            # st.rerun(): Streamlit 전체 스크립트를 처음부터 다시 실행

    
    # 기능 구현 공간: 2열 레이아웃
    # st.columns(2): 화면을 2개의 동일한 너비 컬럼으로 분할
    # col1, col2 = ... → 반환된 컬럼 객체를 각각 변수에 언패킹(unpacking)
    col1, col2 = st.columns(2)

    # 왼쪽 열(col1): 질문하기 (음성 녹음)
    # with col1: → 들여쓰기 블록 안의 위젯이 왼쪽 열에 배치됨

    with col1:
        # 왼쪽 영역 작성
        st.subheader("질문하기")
        # st.subheader: 소제목 텍스트 (HTML의 <h3> 수준)

        # 음성 녹음 아이콘 추가
        audio = audiorecorder("클릭하여 녹음하기", "녹음 중...")
        # audiorecorder("시작 텍스트", "녹음 중 텍스트")
        # → 마이크 버튼을 화면에 렌더링
        # → 녹음이 끝나면 오디오 객체를 반환, 아직 녹음 안 했으면 빈 객체 반환

        if audio.duration_seconds > 0:
            # audio.duration_seconds: 녹음된 오디오의 길이(초, float)
            # > 0: 녹음이 완료된 상태 (0이면 아직 녹음 안 함)

            # [수정] 새 녹음이 들어오면 check_reset을 False로 복원
            # → 초기화 후에도 새로 녹음하면 정상 동작하도록 허용
            if st.session_state["check_reset"]:
                st.session_state["check_reset"] = False
                # check_reset이 True(초기화 직후 상태)였다면 False로 되돌림
                # 이후 col2의 if문 조건(check_reset == False)이 통과되어 GPT 응답 재개

        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            # 녹음 완료 + 초기화 직후가 아닐 때만 아래 로직 실행
            # and: 두 조건이 모두 True일 때만 if 블록 실행 (논리 AND 연산자)

            # 음성 재생 (녹음한 내용을 바로 들을 수 있게 플레이어 표시)
            st.audio(audio.export().read())
            # audio.export(): 오디오 객체를 파일 형태로 변환 (기본 포맷)
            # .read(): 변환된 파일을 바이트(bytes)로 읽음
            # st.audio(바이트): 오디오 플레이어 위젯을 화면에 표시

            # 음원 파일에서 텍스트 추출 (STT 함수 호출)
            question = STT(audio, st.session_state["OPENAI_API"])
            # STT 함수에 오디오 객체와 API 키를 전달
            # 반환값(question): Whisper가 인식한 텍스트 문자열

            # 채팅을 시각화하기 위해 질문 내용 저장
            now = datetime.now().strftime("%H:%M")
            # datetime.now(): 현재 날짜+시간 객체 반환
            # .strftime("%H:%M"): 원하는 형식의 문자열로 변환
            #   %H: 24시간제 시(hour), %M: 분(minute)
            #   예: "14:35"

            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            # 기존 chat 리스트에 새 튜플을 추가한 새 리스트를 만들어 저장
            # 튜플(tuple): (값1, 값2, 값3) → 순서가 있고 변경 불가한 묶음
            # ("user", "14:35", "오늘 날씨 어때?") 형태로 저장
            # ※ .append() 대신 + 연산자로 리스트 이어붙이기

            # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
            st.session_state["messages"] = st.session_state["messages"] + [
                {"role": "user", "content": question}
            ]
            # GPT API 형식에 맞게 사용자 메시지를 대화 기록에 추가
            # {"role": "user", "content": 질문내용} 딕셔너리를 리스트에 이어붙임


    # 오른쪽 열(col2): 답변 표시 및 채팅 UI

    with col2:
        # 오른쪽 영역 작성
        st.subheader("질문/답변")

        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            # 왼쪽 열과 동일한 조건: 녹음 완료 + 초기화 직후가 아닐 때

            # chatGPT에게 답변 얻기
            response = ask_gpt(
                st.session_state["messages"],   # 전체 대화 기록 전달
                model,                          # 선택한 GPT 모델
                st.session_state["OPENAI_API"]  # API 키
            )
            # ask_gpt 함수 호출 → GPT 답변 문자열 반환

            # GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장
            st.session_state["messages"] = st.session_state["messages"] + [
                {"role": "assistant", "content": response}
            ]
            # GPT 답변도 대화 기록에 추가 → 다음 질문 시 이전 맥락 유지
            # role: "assistant" → GPT(AI)가 보낸 메시지

            # 채팅 시각화를 위한 답변 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]
            # ("bot", "14:35", "내일은 맑겠습니다.") 형태로 저장

            # gTTS 활용해 음성 파일 생성 및 재생
            TTS(response)
            # TTS 함수 호출: GPT 답변 텍스트 → 한국어 음성으로 자동 재생


        # 채팅 형식으로 시각화하기 (말풍선 UI)
        # for 변수 in 리스트: → 리스트의 각 항목을 순서대로 꺼내 반복
        # sender, time, message = 튜플 언패킹 ("user", "14:35", "안녕") → sender="user", time="14:35", message="안녕"

        for sender, time, message in st.session_state["chat"]:

            if sender == "user":
                # 사용자 말풍선: 왼쪽 정렬, 파란 배경
                st.write(
                    f'<div style="display:flex;align-items:center;">'
                    # display:flex → 자식 요소들을 가로로 나란히 배치 (CSS Flexbox)
                    # align-items:center → 세로 중앙 정렬
                    f'<div style="background-color:#007AFF;color:white;border-radius:12px;'
                    f'padding:8px 12px;margin-right:8px;">'
                    # background-color:#007AFF → iOS 스타일 파란색 배경
                    # color:white → 글자색 흰색
                    # border-radius:12px → 모서리를 둥글게 (말풍선 모양)
                    # padding:8px 12px → 안쪽 여백 (상하 8px, 좌우 12px)
                    # margin-right:8px → 오른쪽 바깥 여백
                    f'{message}</div>'
                    # {message}: f-string으로 실제 메시지 내용 삽입
                    f'<div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                    # font-size:0.8rem → 시간 텍스트를 기본 크기의 80%로 작게 표시
                    # color:gray → 회색 글자
                    unsafe_allow_html=True
                    # unsafe_allow_html=True → HTML 태그를 그대로 렌더링 허용
                )
                st.write("")  # 말풍선 아래 빈 줄(여백) 추가

            else:
                # 봇(GPT) 말풍선: 오른쪽 정렬, 회색 배경
                st.write(
                    f'<div style="display:flex;align-items:center;justify-content:flex-end;">'
                    # justify-content:flex-end → 가로 오른쪽 정렬 (봇은 오른쪽에 배치)
                    f'<div style="background-color:lightgray;border-radius:12px;'
                    f'padding:8px 12px;margin-left:8px;">'
                    # background-color:lightgray → 연회색 배경 (봇 말풍선)
                    # margin-left:8px → 왼쪽 바깥 여백
                    f'{message}</div>'
                    f'<div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                    unsafe_allow_html=True
                )
                st.write("")  # 말풍선 아래 빈 줄(여백) 추가



#진입점 (Entry Point)
# __name__: 현재 파일이 어떻게 실행됐는지 알려주는 파이썬 내장 변수
#   직접 실행 (python ch03_voicebot.py) → __name__ == "__main__" → main() 호출
#   다른 파일에서 import로 사용             → __name__ == "파일명"   → main() 호출 안 함
# 이 패턴은 파이썬의 관용적 진입점 작성 방식

if __name__ == "__main__":
    main()
