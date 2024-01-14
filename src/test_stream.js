const eventSource = new EventSource('http://127.0.0.1:8000/stream');

eventSource.onmessage = function(event) {
    console.log('Received message:', event.data);
};

eventSource.onerror = function(error) {
    console.error('Error:', error);
};