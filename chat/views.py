import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.conf import settings
from .models import Conversation, Message

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def get_openai_client():
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return None
    if not OPENAI_AVAILABLE:
        return None
    return OpenAI(api_key=api_key)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})


@login_required
def index(request):
    conversations = Conversation.objects.filter(user=request.user)
    return render(request, 'chat/index.html', {
        'conversations': conversations,
        'active_conversation': None,
    })


@login_required
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversations = Conversation.objects.filter(user=request.user)
    messages = conversation.messages.all()
    return render(request, 'chat/index.html', {
        'conversations': conversations,
        'active_conversation': conversation,
        'messages': messages,
    })


@login_required
@require_http_methods(["POST"])
def new_conversation(request):
    conversation = Conversation.objects.create(user=request.user)
    return JsonResponse({'id': conversation.id, 'title': conversation.title})


@login_required
@require_http_methods(["POST"])
def send_message(request):
    data = json.loads(request.body)
    message_content = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')
    model = data.get('model', 'gpt-4o-mini')

    if not message_content:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Get or create conversation
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    else:
        # Auto-title from first message
        title = message_content[:50] + ('...' if len(message_content) > 50 else '')
        conversation = Conversation.objects.create(user=request.user, title=title, model=model)

    # Save user message
    Message.objects.create(
        conversation=conversation,
        role='user',
        content=message_content
    )

    # Update conversation title if it's the first message
    if conversation.messages.filter(role='user').count() == 1:
        title = message_content[:50] + ('...' if len(message_content) > 50 else '')
        conversation.title = title
        conversation.save()

    # Build message history for API
    history = []
    for msg in conversation.messages.all():
        history.append({'role': msg.role, 'content': msg.content})

    # Call OpenAI API
    client = get_openai_client()
    
    if client is None:
        # Demo mode - echo response
        assistant_reply = f"[DEMO MODE - No API Key] You said: \"{message_content}\"\n\nTo enable real AI responses, set your OPENAI_API_KEY environment variable and install openai: `pip install openai`"
    else:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=history,
                max_tokens=2048,
            )
            assistant_reply = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
        except Exception as e:
            assistant_reply = f"Error calling OpenAI API: {str(e)}"
            tokens_used = None

    # Save assistant message
    assistant_msg = Message.objects.create(
        conversation=conversation,
        role='assistant',
        content=assistant_reply
    )

    return JsonResponse({
        'conversation_id': conversation.id,
        'conversation_title': conversation.title,
        'reply': assistant_reply,
        'message_id': assistant_msg.id,
    })


@login_required
@require_http_methods(["DELETE"])
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["PATCH"])
def rename_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    data = json.loads(request.body)
    new_title = data.get('title', '').strip()
    if new_title:
        conversation.title = new_title
        conversation.save()
    return JsonResponse({'title': conversation.title})


@login_required
def get_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    messages = [
        {'role': m.role, 'content': m.content, 'id': m.id}
        for m in conversation.messages.all()
    ]
    return JsonResponse({'messages': messages, 'title': conversation.title})
