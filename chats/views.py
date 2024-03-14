from django.shortcuts import render, redirect, get_object_or_404
import openai
from django import template
from dotenv import load_dotenv
from datetime import datetime, timedelta

import os
from django.http import HttpResponseRedirect
from django.urls import reverse
from chats.openai import *

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.template.defaultfilters import stringfilter
from django.http import JsonResponse

import markdown as md
from django.shortcuts import render, get_object_or_404
from .models import ChatHistory, ChatSession  # Import your models accordingly

register = template.Library()
from .models import *

load_dotenv()
# Create your views here.
key = os.getenv("CPRAS_OPENAI_API_KEY")
openai.api_key = key

# defuest):
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
def create_new_chat_old(request):
    new_chat = ChatSession.objects.create(
        user=request.user,
        title="default",
        # other fields can go here
    )

    return new_chat


# @login_required
# def home(request):

#     latest_chat = ChatSession.objects.filter(user=request.user).order_by('-created_at').first()

#     if latest_chat is None:
#         create_new_chat(request)

#     request.session['session_title'] = latest_chat.title

#     # Retrieve chat history for the latest chat session
#     chat_history = ChatHistory.objects.filter(
#         chat_session__user=request.user,
#         chat_session__title=request.session['session_title']
#     ).order_by('timestamp') if latest_chat else None

#     # Retrieve all chat sessions for the user
#     all_chat_sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

#     context = {
#         'chat_history': chat_history,
#         'all_chat_sessions': all_chat_sessions
#     }
#     return render(request, 'chats/home.html', context)


@login_required
def answer(request):
    question = request.POST.get("question")
    # Get session_id from Django session
    print("pass_1")
    # getting the session id submitted by the home view
    session_title = request.session.get("session_title", "Default Title")
    print(session_title)
    print("pass_2")

    response = interact_with_openai(question)
    #print(response.get_response, "Look at me")
    print(type(response))
    try:
        text = {"text": response.choices[0].message.content}
    except:
        # if not openai functions
        text = {"text": response}
    try:
        chat_session_instance = ChatSession.objects.get(
            title=session_title, user=request.user
        )
        print("Type of system_response:", type(text))
        print("Value of system_response:", text)

        # chat_session_instance = ChatSession.objects.get(id=session_id, user=request.user)
        # Now, create a new ChatHistory entry with the obtained ChatSession instance
        ChatHistory.objects.create(
            chat_session=chat_session_instance,
            user=request.user,
            user_prompt=question,
            system_response=text,
        )
        # Retrieve chat history for the current user, sorted by timestamp in ascending order
        chat_history = ChatHistory.objects.filter(
            user=request.user, chat_session=chat_session_instance
        ).order_by("timestamp")
        # print(chat_history)

        responses = {
            "chat_history": chat_history,
        }
        return render(request, "chats/answer.html", responses)
    except ChatSession.DoesNotExist:
        print("Model Not Found")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            # Invalid login
            pass
    return render(request, "login/login.html")


def logout_view(request):
    logout(request)
    return redirect("/login")


@login_required
def upload_view(request):
    print("uploading...")
    response = {}
    return render(request, "chats/knowledgebase.html", response)


# def content(request):
#     return render(request, 'chats/markdown.html', {'content':
#         '# this is test title\n' +
#         '- list 1\n' +
#         '- list 2\n'
#     })


# @login_required
# def create_new_chat(request):
#     print("Create new chat accessed")
#     if request.method == 'GET':

#         # Check if the session variable 'session_title' has a value
#         session_title = request.session.get('session_title')

#         if session_title:
#             # Find the existing chats with the same session title and user
#             existing_chats = ChatSession.objects.filter(user=request.user, title__startswith=session_title).count()

#             # Create new chat with incremented title
#             new_chat_title = f"{session_title}-{existing_chats + 1}"

#         else:
#             # Use 'default' as the session title if the session variable is not set
#             new_chat_title = 'default'

#         # Create new chat session
#         new_chat = ChatSession.objects.create(
#             user=request.user,
#             title=new_chat_title,
#             # other fields can go here
#         )

#         # Update the session variable with the new chat title
#         request.session['session_title'] = new_chat_title
#         chat_history = ChatHistory.objects.filter(chat_session__user=request.user, chat_session__title=new_chat.title).order_by('timestamp')
#         print(chat_history,"Success chat history")
#           # Retrieve all chat sessions for the user
#         all_chat_sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
#         print(all_chat_sessions,"Empty chat sessions found")
#         print(all_chat_sessions,"Success")
#         context = {
#         'chat_history': chat_history,
#         'all_chat_sessions': all_chat_sessions,
#         }
#         return render(request, 'chats/home.html', context)


@login_required
def get_chat_history(request, session_id):
    chat_history = [
        {
            "username": chat.user.username.upper(),
            "user_prompt": chat.user_prompt,
            "system_response": chat.system_response,
        }
        for chat in ChatHistory.objects.filter(chat_session_id=session_id)
    ]
    return JsonResponse({"chat_history": chat_history})


@login_required
def change_session(request, session_id):
    # Fetch the clicked session using session_id
    clicked_session = get_object_or_404(ChatSession, id=session_id, user=request.user)

    # Change the current session to the clicked session
    request.session["session_title"] = clicked_session.title

    # Retrieve chat history for the clicked chat session
    chat_history = ChatHistory.objects.filter(
        chat_session=clicked_session  # We filter by the actual session object here
    ).order_by("timestamp")

    # Retrieve all chat sessions for the user
    all_chat_sessions = ChatSession.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:10]

    # Get today's date
    today_date = datetime.now().date()

    # Retrieve chat sessions for today
    today_chat_sessions = ChatSession.objects.filter(
        user=request.user, created_at__date=today_date
    ).order_by("-created_at")[:2]

    # Calculate yesterday's date
    yesterday_date = today_date - timedelta(days=1)

    # Retrieve chat sessions for yesterday
    yesterday_chat_sessions = ChatSession.objects.filter(
        user=request.user, created_at__date=yesterday_date
    ).order_by("-created_at")[:2]

    context = {
        "chat_history": chat_history,
        "all_chat_sessions": all_chat_sessions,
        "today_chat_sessions": today_chat_sessions,
        "yesterday_chat_sessions": yesterday_chat_sessions,
    }

    # Render the home template with the updated context
    return render(request, "chats/home.html", context)


def create_new_chat_session(request):
    session_title = request.session.get("session_title")

    if session_title:
        existing_chats = ChatSession.objects.filter(
            user=request.user, title__startswith=session_title
        ).count()
        new_chat_title = f"{session_title}-{existing_chats + 1}"
    else:
        new_chat_title = "default"

    new_chat = ChatSession.objects.create(
        user=request.user,
        title=new_chat_title,
    )

    request.session["session_title"] = new_chat_title
    return new_chat_title


# View to explicitly create a new chat session
@login_required
def create_new_chat(request):
    print("Create new chat accessed")
    if request.method == "GET":
        new_chat_title = create_new_chat_session(request)
        return HttpResponseRedirect(reverse("home"))


# Home view
@login_required
def home(request):
    latest_chat = (
        ChatSession.objects.filter(user=request.user).order_by("-created_at").first()
    )

    if latest_chat is None:
        new_chat_title = create_new_chat_session(request)
        chat_history = ChatHistory.objects.filter(
            chat_session__user=request.user, chat_session__title=new_chat_title
        ).order_by("timestamp")
    else:
        request.session["session_title"] = latest_chat.title
        chat_history = ChatHistory.objects.filter(
            chat_session__user=request.user, chat_session__title=latest_chat.title
        ).order_by("timestamp")

    all_chat_sessions = ChatSession.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:10]

    print(latest_chat, "latest_chat")
    print(chat_history, "chat_history")
    print(all_chat_sessions, "all_chat_sessions")

    # make this a function
    # Get today's date
    today_date = datetime.now().date()

    # Retrieve chat sessions for today
    today_chat_sessions = ChatSession.objects.filter(
        user=request.user, created_at__date=today_date
    ).order_by("-created_at")[:2]

    # Calculate yesterday's date
    yesterday_date = today_date - timedelta(days=1)

    # Retrieve chat sessions for yesterday
    yesterday_chat_sessions = ChatSession.objects.filter(
        user=request.user, created_at__date=yesterday_date
    ).order_by("-created_at")[:2]

    context = {
        "chat_history": chat_history,
        "all_chat_sessions": all_chat_sessions,
        "today_chat_sessions": today_chat_sessions,
        "yesterday_chat_sessions": yesterday_chat_sessions,
    }
    return render(request, "chats/home.html", context)


from rest_framework import viewsets
from rest_framework.response import Response
from .models import ChatSession, ChatHistory
from .serializers import ChatSessionSerializer, ChatHistorySerializer


class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer


class ChatHistoryViewSet(viewsets.ModelViewSet):
    queryset = ChatHistory.objects.all()
    serializer_class = ChatHistorySerializer


class AllRecordsView(viewsets.ViewSet):
    def list(self, request):
        sessions = ChatSession.objects.all()
        histories = ChatHistory.objects.all()

        session_serializer = ChatSessionSerializer(sessions, many=True)
        history_serializer = ChatHistorySerializer(histories, many=True)

        return Response(
            {
                "chatsessions": session_serializer.data,
                "chathistories": history_serializer.data,
            }
        )
