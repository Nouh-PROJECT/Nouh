from flask import Flask, render_template,jsonify,request, current_app
from flask import Blueprint
import requests,openai,os, json
from dotenv.main import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from app.utils.db import execute_query
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User

bp = Blueprint('chatbot', __name__)

file_path = os.path.join(os.path.dirname(__file__), "../utils/filter_words.json")
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)
filter_words = data.get("filter_words", [])

llm = ChatOpenAI(temperature=0.7, openai_api_key="my-api-key", model_name="gpt-3.5-turbo")
memory1 = ConversationSummaryBufferMemory(llm=llm) # 문제풀이 메모리
memory2 = ConversationSummaryBufferMemory(llm=llm) # 일반질문 메모리

@bp.route("/")
def index():
    return render_template('chatbot/chatbot.html')

@bp.route("/get_buttons/<btnType>")
def get_buttons(btnType):
    if btnType == "default":

        buttons = [
            {"idx":"myinfo",
            "name":"내 정보 조회",},

            {"idx":"site",
            "name":"사이트 설명",},
            
            {"idx":"quiz",
            "name":"문제 풀이",},   
        ]
        
    elif btnType == "myinfo":
        buttons = [
            {"idx":"default",
            "name":"이메일",},

            {"idx":"default",
            "name":"전화번호",},
            
            {"idx":"default",
            "name":"전체 정보",}, 

            {"idx":"default",
            "name":"처음으로",},    
        ]
        
    elif btnType == "site":
        buttons = [
            {"idx":"default",
            "name":"기능 설명",},

            {"idx":"default",
            "name":"구독 설명",},

            {"idx":"default",
            "name":"처음으로",}
        ]

    elif btnType == "quiz":
        buttons = [
            {"idx":"default",
            "name":"처음으로",}
        ]

    return buttons

@bp.route('/chatbot_response/<btnType>', methods=['POST'])
def get_data(btnType):
    data = request.get_json()
    text=data.get('data')
    user_input = text

    try:
        if(text == "처음으로"):
            output="무엇을 도와드릴까요?"

        elif(text == "start"):
            output="안녕하세요! Nouh 챗봇입니다. 무엇을 도와드릴까요?"

        elif(text == "내 정보 조회"):
            output="어떤 정보에 대해 궁금하세요?"
        
        elif(text == "이메일"):
            if current_user.is_authenticated:
                rows = execute_query(r"SELECT email FROM users WHERE id=%s", (current_user.id,))
                
                user = rows[0] if rows else None
                if not user:
                    return jsonify({"message":"존재하지 않는 유저입니다.","response":False})
                email = user['email']
                output = f"로그인한 계정의 이메일은 {email}입니다."
            else:
                output="로그인이 필요한 서비스입니다."

        elif(text == "전화번호"):
            if current_user.is_authenticated:
                rows = execute_query(r"SELECT phone FROM users WHERE id=%s", (current_user.id,))
                
                user = rows[0] if rows else None
                if not user:
                    return jsonify({"message":"존재하지 않는 유저입니다.","response":False})
                phone = user['phone']
                output = f"로그인한 계정의 전화번호는 {phone}입니다."
            else:
                output="로그인이 필요한 서비스입니다."

        elif(text == "전체 정보"):
            if current_user.is_authenticated:
                rows = execute_query(r"SELECT name, email, phone FROM users WHERE id=%s", (current_user.id,))

                user = rows[0] if rows else None
                if not user:
                    return jsonify({"message":"존재하지 않는 유저입니다.","response":False})
                name = user['name']
                email = user['email']
                phone = user['phone']
                output = f"로그인한 계정의 정보입니다.\n이름 : {name}\n이메일 : {email}\n전화번호 : {phone}"
            else:
                output="로그인이 필요한 서비스입니다."

        elif(text == "사이트 설명"):
            output="어떤 정보에 대해 궁금하세요?"

        elif(text == "기능 설명"):
            output="Nouh LMS의 기능은 다음과 같습니다.\n -문제 추가\n -나의 문제\n "
            output='''Nouh LMS의 기능은 다음과 같습니다.
- 문제 추가
4지 선다형 문제를 추가할 수 있습니다. 과목, 문제, 답, 해설을 설정해 업로드할 수 있습니다.
아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)
            
- 나의 문제
내가 작성한 문제를 확인하고 수정할 수 있습니다.
아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)

- 문제 찾기
서비스에 등록된 모든 문제를 확인할 수 있습니다. 문제는 과목별, 제목, 내용별로 검색이 가능합니다.
자신이 작성한 문제를 수정할 수 있습니다.
아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)

- 시험 보기
서비스에 등록된 문제들을 대상으로 과목별 시험 응시가 가능합니다.
시험 응시 후 점수를 확인할 수 있으며 엑셀 파일로 풀었던 문제를 확인할 수 있습니다.
아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)

- 강의 보기
구독자는 등록된 강의를 시청할 수 있습니다.
아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)

- 자유게시판
자유롭게 글을 작성할 수 있는 공간입니다. 
아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)
''' 
        elif(text == "구독 설명"):
            output = '''Nouh LMS의 구독 서비스
1.챗봇 이용
챗봇 서비스 이용이 가능합니다. 챗봇을 통해 문제 해설을 빠르게 확인할 수 있습니다.
내 정보 조회, 사이트 설명 질문, 문제 질문을 할 수 있습니다.
2.강의 시청
사이트 내 강의 보기 페이지를 사용할 수 있습니다. 강의 목록에서 원하는 강의를 시청할 수 있습니다.'''

        elif(text == "문제 풀이"):
            output="궁금한 문제에 대해 입력해보세요!"

        else:
            output = ""

            if btnType == "quiz":
                for word in filter_words:
                    if word in user_input:
                        output+= f"'{user_input}'에 대한 결과입니다.\n"
                        
                        #문제 질문
                        conversation = ConversationChain(llm=llm,memory=memory1)
                        output += conversation.predict(input=user_input)
                        memory1.save_context({"input": user_input}, {"output": output})
                        return jsonify({"response":True,"message":output})

                if len(output)<=0:
                    return jsonify({"response":True,"message":f"{user_input}에 대해서는 잘 모르겠어요. 다시 질문해주세요!"})                        
            
            #일반 질문   
            conversation = ConversationChain(llm=llm,memory=memory2)
            output += conversation.predict(input=user_input)
            memory2.save_context({"input": user_input}, {"output": output})
        return jsonify({"response":True,"message":output})
    except Exception as e:
        print(e)
        error_message = f'Error: {str(e)}'
        return jsonify({"message":error_message,"response":False})

