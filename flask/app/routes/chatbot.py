import os
import json
import openai
from flask import Blueprint
from flask import request
from flask import Flask, render_template, render_template_string, jsonify
from flask_login import current_user, login_required
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from functools import wraps
from app.utils.db import execute_query


bp = Blueprint('chatbot', __name__)


file_path = os.path.join(os.getcwd(), "app", "utils", "filter_words.json")
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)
filter_words = data.get("filter_words", [])

llm = ChatOpenAI(temperature=0.7, openai_api_key="my-api-key", model_name="gpt-3.5-turbo")
memory1 = ConversationSummaryBufferMemory(llm=llm) # 문제풀이 메모리
memory2 = ConversationSummaryBufferMemory(llm=llm) # 일반질문 메모리


def check_authority(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            query = r"SELECT 1 FROM admin WHERE id=%s"
            if execute_query(query, (current_user.id,)):
                return func(*args, **kwargs)
            
            query = r"SELECT 1 FROM subscribe WHERE id=%s"
            if execute_query(query, (current_user.id,)):
                return func(*args, **kwargs)
        return redirect("/")
    return wrapper


@bp.route("/")
@login_required
@check_authority
def index():
    return render_template('chatbot/index.html')


@bp.route("/get_buttons/<btnType>")
@login_required
@check_authority
def get_buttons(btnType: str):
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
@login_required
@check_authority
def get_data(btnType: str):
    data = request.get_json()
    text=data.get('data')
    user_input = text

    if not current_user.is_authenticated:
        return jsonify({ "response": False, "message": "로그인 후 이용 가능한 서비스입니다!" })

    try:
        if (text == "처음으로"):
            output="무엇을 도와드릴까요?"
        elif (text == "start"):
            output="안녕하세요! Nouh 챗봇입니다. 무엇을 도와드릴까요?"
        elif (text == "내 정보 조회"):
            output="어떤 정보에 대해 궁금하세요?"
        elif (text == "이메일"):
            query = r"SELECT email FROM users WHERE id=%s"
            email = rows[0]["email"] if (rows:=execute_query(query, (current_user.id,))) else None
            if email is None:
                return jsonify({"response": False, "message":"잘못된 접근입니다"})
            if not email:
                return jsonify({"response": False, "message":"이메일 정보가 없습니다"})
            output = f"로그인한 계정의 이메일은 {email}입니다."
        elif(text == "전화번호"):
            query = r"SELECT phone FROM users WHERE id=%s"
            phone = rows[0]["phone"] if (rows:=execute_query(query, (current_user.id,))) else None
            if phone is None:
                return jsonify({"response": False, "message":"잘못된 접근입니다"})
            if not phone:
                return jsonify({"response": True, "message":"연락처 정보가 없습니다"})
            output = f"로그인한 계정의 연락처는 {phone}입니다."
        elif(text == "전체 정보"):
            query = r"SELECT name, email, phone FROM users WHERE id=%s"
            user = rows[0] if (rows:=execute_query(query, (current_user.id,))) else None
            if user is None:
                return jsonify({"response": False, "message":"잘못된 접근입니다"})
            output = "로그인한 계정의 정보입니다.\n"
            output += f"이름 : {user['name'] if user['name'] else '정보가 없습니다'}\n"
            output += f"이메일 : {user['email'] if user['email'] else '정보가 없습니다'}\n"
            output += f"연락처 : {user['phone'] if user['phone'] else '정보가 없습니다'}"
        elif(text == "사이트 설명"):
            output="어떤 정보에 대해 궁금하세요?"
        elif(text == "기능 설명"):
            output ="Nouh LMS의 기능은 다음과 같습니다.\n\n"
            output += "- 문제 추가\n"
            output += "4지 선다형 문제를 추가할 수 있습니다. 과목, 문제, 답, 해설을 설정해 업로드할 수 있습니다."
            output += "아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)\n"
            output += "- 나의 문제\n"
            output += "내가 작성한 문제를 확인하고 수정할 수 있습니다."
            output += "아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)\n"
            output += "- 문제 찾기\n"
            output += "서비스에 등록된 모든 문제를 확인할 수 있습니다. 문제는 과목별, 제목, 내용별로 검색이 가능합니다."
            output += "자신이 작성한 문제를 수정할 수 있습니다."
            output += "아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)\n"
            output += "- 시험 보기\n"
            output += "서비스에 등록된 문제들을 대상으로 과목별 시험 응시가 가능합니다."
            output += "시험 응시 후 점수를 확인할 수 있으며 엑셀 파일로 풀었던 문제를 확인할 수 있습니다."
            output += "아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)\n"
            output += "- 강의 보기\n"
            output += "구독자는 등록된 강의를 시청할 수 있습니다."
            output += "아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)\n"
            output += "- 자유게시판\n"
            output += "자유롭게 글을 작성할 수 있는 공간입니다."
            output += "아래 링크를 통해 문제 추가 페이지로 이동할 수 있습니다. (고정IP 할당 후 추가예정)"
        elif(text == "구독 설명"):
            output = "Nouh LMS의 구독 서비스\n\n"
            output += "1. 챗봇 이용\n"
            output += "챗봇 서비스 이용이 가능합니다. 챗봇을 통해 문제 해설을 빠르게 확인할 수 있습니다."
            output += "내 정보 조회, 사이트 설명 질문, 문제 질문을 할 수 있습니다.\n"
            output += "2. 강의 시청\n"
            output += "사이트 내 강의 보기 페이지를 사용할 수 있습니다. 강의 목록에서 원하는 강의를 시청할 수 있습니다."
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
                        return jsonify({ "response": True, "message": output})

                if len(output)<=0:
                    rend_output = render_template_string(user_input)
                    message = f"'{rend_output}'에 대해서는 잘 모르겠어요. 다시 질문해주세요!"
                    return jsonify({ "response": True, "message": message})                      

            #일반 질문
            conversation = ConversationChain(llm=llm,memory=memory2)
            output += conversation.predict(input=user_input)
            memory2.save_context({"input": user_input}, {"output": output})
        return jsonify({ "response": True, "message": output})
    except Exception as e:
        return jsonify({ "response":False, "message": f"ERROR: {str(e)}" })

