from django.shortcuts import render, redirect
import openai
from django import template
from dotenv import load_dotenv
import os

from chats.openai import *

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.template.defaultfilters import stringfilter

import markdown as md

register = template.Library()
from .models import *
load_dotenv()
# Create your views here.
key=os.getenv('CPRAS_OPENAI_API_KEY')
openai.api_key = key

@login_required
def home(request):
    # Retrieve chat history for the current user, sorted by timestamp in ascending order
    #chat_history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')
    chat_history = ChatHistory.objects.filter(chat_session__user=request.user, chat_session__title='asd').order_by('timestamp')
    return render(request, 'chats/home.html', {'chat_history': chat_history})

@login_required
def answer(request):
    question = request.POST.get('question')
    # Get session_id from Django session
    print("pass_1")
    session_id = request.session.get('chat_session_id', None)
    print(session_id)
    print("pass_2")
    #session_id = request.POST.get('session_id')

    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo-16k", 
    #     messages=[
    #         {
    #         "role": "system", 
    #         "content": """
    #             You are a the AI serving CPRAS named as SUSIE and your CEO is 
    #             Richard Hallewell and your Developer is Bryan Dadiz The Data Scientist
    #             You are also Susie version 1.
    #             """
    #         }
    #         ,      
    #         {
    #         "role": "user", 
    #         "content": question
    #         }
    #     ],
    #     temperature=0.1,
    # )

    response = interact_with_openai(question)
    print(response)
    try:
        text = {"text":response["choices"][0]["message"]["content"]}
    except:
        # if not openai functions
        text = {"text":response}

    # Replace 'asd' with the actual chat session identifier
    #chat_session_title = 'asd'

    try:
        # Try to fetch the ChatSession instance based on the chat_session_id
        #chat_session_instance = ChatSession.objects.get(title=chat_session_title, user=request.user)
        chat_session_instance = ChatSession.objects.get(id=session_id, user=request.user)
        # Now, create a new ChatHistory entry with the obtained ChatSession instance
        ChatHistory.objects.create(
                    chat_session=chat_session_instance,
                    user=request.user,
                    user_prompt=question,
                    system_response=text
        )
        # Retrieve chat history for the current user, sorted by timestamp in ascending order
        chat_history = ChatHistory.objects.filter(user=request.user, chat_session=chat_session_instance).order_by('timestamp')
        #print(chat_history)
        responses = {
            'chat_history': chat_history,
        }
        return render(request, 'chats/answer.html', responses)
    except ChatSession.DoesNotExist:
        print('Model Not Found')
        # Handle the case where the chat_session_id doesn't exist or is invalid
        # You can raise an exception, return an error response, or take appropriate action

    # chat_history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')
    # print(chat_history)

    # # Extract only the 'system_response' fields (assuming 'system_response' holds the 'text')
    # text_responses = [chat.system_response for chat in chat_history]
    # import json
    # # Parse the JSON string
    # json_obj = json.loads(text_responses)

    # # Navigate to the nested structure to get the text
    # extracted_text = json_obj["text"][0][0]["text"]
    # responses = {
    #     'text_responses': extracted_text,
    # }

    # return render(request, 'chats/answer.html', responses)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            # Invalid login
            pass
    return render(request, 'login/login.html')


def logout_view(request):
    logout(request)
    return redirect('/login')

@login_required
def upload_view(request):
    print("uploading...")
    response = {

    }
    return render(request,'chats/knowledgebase.html', response)

# def content(request):
#     return render(request, 'chats/markdown.html', {'content': 
#         '# this is test title\n' + 
#         '- list 1\n' +
#         '- list 2\n'
#     })
from django.http import JsonResponse
@login_required
def create_new_chat(request):
    if request.method == 'POST':
        new_chat = ChatSession.objects.create(
            user=request.user,
            title='default',
            # other fields can go here
        )
        return JsonResponse({'status': 'success', 'chat_id': new_chat.id})
    else:
        return JsonResponse({'status': 'fail'})
    
@login_required
def get_chat_history(request, session_id):
    chat_history = [
        {
            'username': chat.user.username.upper(),
            'user_prompt': chat.user_prompt,
            'system_response': chat.system_response
        }
        for chat in ChatHistory.objects.filter(chat_session_id=session_id)
    ]
    return JsonResponse({'chat_history': chat_history})
