const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const messageContainer = document.getElementById('message-container');

const chatSocket = new WebSocket(
  `ws://${window.location.host}/ws/chat/${chatId}/`
);

// Handle WebSocket connection open
chatSocket.onopen = (event) => {
  console.log('WebSocket connection opened:', event);
};

// Handle WebSocket message received
chatSocket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  // Append the new message to the message container
  const messageElement = document.createElement('div');
  messageElement.innerText = message.message;
  messageContainer.appendChild(messageElement);
};

// Handle WebSocket connection closed
chatSocket.onclose = (event) => {
  console.log('WebSocket connection closed:', event);
};

messageForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const content = messageInput.value;
  const response = await fetch(`/send-message/${chatId}/`, {
    method: 'POST',
    body: JSON.stringify({ content }),
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
  });
  if (response.status === 200) {
    messageInput.value = '';
  }
});

// Function to send WebSocket message
function sendMessage(content) {
  chatSocket.send(JSON.stringify({ message: content }));
}
