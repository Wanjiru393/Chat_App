from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Chat, Message, Notification
from django.utils.html import escape
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def chat_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages = Message.objects.filter(chat=chat)
    # Mark messages as read when viewing the chat
    for message in messages.filter(sender__username=chat.participants.exclude(username=request.user.username)):
        message.is_read = True
        message.save()
    return render(request, 'chat/chat.html', {'chat': chat, 'messages': messages})

@login_required
def send_message(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id)
        content = escape(request.POST.get('content'))  # Escape user input for security
        sender = request.user
        message = Message.objects.create(chat=chat, sender=sender, content=content)
        
        # Create notifications for other participants
        other_participants = chat.participants.exclude(username=sender.username)
        for participant in other_participants:
            Notification.objects.create(user=participant, message=message)
        
        # Send WebSocket message for real-time update
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"chat_{chat_id}", {
            'type': 'chat.message',
            'message': f"{sender.username}: {content}",
        })
        
        return JsonResponse({'status': 'success'})
