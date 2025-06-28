# 📦 Shipping Website – Customer Chat Feature

## 🧩 Overview

This document outlines the **structure**, **requirements**, and **design overview** for implementing a **real-time customer chat window** on a shipping service platform built with the **Django framework**. The chat will help customers get information, raise queries, or interact with a bot for automated help.

---

## 📌 Objectives

- Enable **real-time** interaction between customers and support agents (or chatbot).
- Provide **automated replies** using a simple **FAQ bot** (optional: upgrade to LLM later).
- Store chat history per user.
- Ensure responsive, mobile-friendly UI.

---

## 🏗️ System Architecture

```
Frontend (JS + HTML/CSS)
    ↓ WebSocket / HTTP
Django Channels (WebSocket Consumer)
    ↓
Django Backend (Views + Models)
    ↓
Database (MariaDB)
```

---

## 📂 Folder Structure

```
project_root/
│
├── chat/                      # Django app for chat
│   ├── consumers.py           # WebSocket logic
│   ├── models.py              # ChatMessage, ChatSession
│   ├── views.py               # Optional views
│   ├── routing.py             # WebSocket URL router
│   └── templates/chat/        # HTML files for chat UI
│
├── static/chat/               # JS/CSS for chat UI
│
├── project_name/
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py                # For WebSocket handling
│
└── templates/                 # Global templates
```

---

## 📄 Models

### `ChatSession`
```python
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### `ChatMessage`
```python
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

---

## 🌐 WebSocket Consumer (Django Channels)

- Handles real-time messaging.
- Authenticates users (optional).
- Sends response from bot or forwards to agent.

```python
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = f"chat_{self.scope['session'].session_key}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Save and send back a bot response
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": bot_reply(message)}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))
```

---

## 🧠 Bot Logic (Simple FAQ Bot)

```python
def bot_reply(message):
    faqs = {
        "how to ship": "You can start shipping by entering pickup and delivery address.",
        "cost": "Shipping cost depends on weight, size, and delivery speed.",
        "track": "Use the tracking ID sent to your email."
    }
    for key, response in faqs.items():
        if key in message.lower():
            return response
    return "Sorry, I didn't understand that. Please rephrase or contact support."
```

---

## 🖥️ Frontend (HTML + JS)

Embed chatbox UI in a base template:

```html
<div id="chat-box">
  <div id="chat-messages"></div>
  <input type="text" id="chat-input" placeholder="Type a message..." />
</div>

<script>
  const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/');

  chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    document.getElementById('chat-messages').innerHTML += '<div>' + data.message + '</div>';
  };

  document.getElementById('chat-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      chatSocket.send(JSON.stringify({ 'message': this.value }));
      this.value = '';
    }
  });
</script>
```

---

## ⚙️ Requirements

### 🛠 Backend

- Django 4.x
- Django Channels
- Redis (as a channel layer)
- MariaDB 
- Optional: Celery (for delayed responses or agent handover)

### 🎨 Frontend

- HTML5, CSS3
- Vanilla JS or React (optional)
- Tailwind/Bootstrap (for UI polish)

---

## 🔐 Security & Privacy

- Authenticate chats (optional).
- Anonymize session if unauthenticated.
- Sanitize input to prevent XSS.

---

## 🧪 Testing

- Test WebSocket connection under multiple tabs/users.
- Validate bot responses.
- Check UI responsiveness (mobile + desktop).

---

## 📈 Future Improvements

- Integrate GPT-based smart agent (OpenAI API).
- Saved context when signed in (like address)
- Human agent escalation flow.
- Multilingual support.
- Feedback rating after chat.