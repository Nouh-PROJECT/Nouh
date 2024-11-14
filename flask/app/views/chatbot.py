from flask import Flask, render_template,jsonify,request, current_app
from flask import Blueprint
import requests,openai,os
from dotenv.main import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory

bp = Blueprint('chatbot', __name__)

# load_dotenv()
# OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY')
# os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(temperature=0.7, openai_api_key="my api key", model_name="gpt-3.5-turbo")
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)

@bp.route("/")
def index():
    return render_template('chatbot/chatbot.html')

@bp.route('/chatbot_response', methods=['POST'])
def get_data():
    data = request.get_json()
    text=data.get('data')
    user_input = text
    try:
        conversation = ConversationChain(llm=llm,memory=memory)
        output = conversation.predict(input=user_input)
        memory.save_context({"input": user_input}, {"output": output})
        return jsonify({"response":True,"message":output})
    except Exception as e:
        print(e)
        error_message = f'Error: {str(e)}'
        return jsonify({"message":error_message,"response":False})
