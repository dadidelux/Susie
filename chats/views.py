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

# def create_new_chat(request):
#     new_chat = ChatSession.objects.create(
#         user=request.user,
#         title='default',
#             # other fields can go here
#         )

#     return new_chat


# @login_required
# def home(request):
#     # Retrieve chat history for the current user, sorted by timestamp in ascending order
#     #chat_history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')
#     create_new_chat(request)
#     chat_history = ChatHistory.objects.filter(chat_session__user=request.user, chat_session__title='default').order_by('timestamp')
#     return render(request, 'chats/home.html', {'chat_history': chat_history})


@login_required
def create_new_chat(request):
    new_chat = ChatSession.objects.create(
        user=request.user,
        title='default',
        # other fields can go here
    )

    return new_chat

@login_required
def home(request):
    
    latest_chat = ChatSession.objects.filter(user=request.user).order_by('-created_at').first()
    
    if latest_chat is None:
        create_new_chat(request)

    request.session['session_title'] = latest_chat.title

    # Retrieve chat history for the latest chat session
    chat_history = ChatHistory.objects.filter(
        chat_session__user=request.user, 
        chat_session__title=request.session['session_title']
    ).order_by('timestamp') if latest_chat else None
    
    # Retrieve all chat sessions for the user
    all_chat_sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'chat_history': chat_history,
        'all_chat_sessions': all_chat_sessions
    }
    return render(request, 'chats/home.html', context)



@login_required
def answer(request):
    question = request.POST.get('question')
    # Get session_id from Django session
    print("pass_1")
    # getting the session id submitted by the home view
    session_title = request.session.get('session_title','Default Title')
    print(session_title)
    print("pass_2")


    response = interact_with_openai(question)
    print(response)
    try:
        text = {"text":response["choices"][0]["message"]["content"]}
    except:
        # if not openai functions
        text = {"text":response}
    try:
        chat_session_instance = ChatSession.objects.get(title=session_title, user=request.user)
        
        #chat_session_instance = ChatSession.objects.get(id=session_id, user=request.user)
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
        
        # Check if the session variable 'session_title' has a value
        session_title = request.session.get('session_title')
        
        if session_title:
            # Find the existing chats with the same session title and user
            existing_chats = ChatSession.objects.filter(user=request.user, title__startswith=session_title).count()
            
            # Create new chat with incremented title
            new_chat_title = f"{session_title}-{existing_chats + 1}"
            
        else:
            # Use 'default' as the session title if the session variable is not set
            new_chat_title = 'default'
        
        # Create new chat session
        new_chat = ChatSession.objects.create(
            user=request.user,
            title=new_chat_title,
            # other fields can go here
        )
        
        # Update the session variable with the new chat title
        request.session['session_title'] = new_chat_title
        chat_history = ChatHistory.objects.filter(chat_session__user=request.user, chat_session__title=new_chat.title).order_by('timestamp')
        print(chat_history,"Success")
        return render(request, 'chats/home.html', {'chat_history': chat_history})
    
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
