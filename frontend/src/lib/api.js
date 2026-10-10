const API_URL = "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep default message.
    }

    throw new Error(message);
  }

  return response.json();
}

export async function listDocuments() {
  return request("/documents");
}

export async function getDocument(documentId) {
  return request(`/documents/${documentId}`);
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request("/documents", {
    method: "POST",
    body: formData,
  });
}

export async function createConversation(title = "New conversation") {
  return request("/chat/conversations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title }),
  });
}

export async function listConversations() {
  return request("/chat/conversations");
}

export async function getConversation(conversationId) {
  return request(`/chat/conversations/${conversationId}`);
}

export async function getMessages(conversationId) {
  return request(`/chat/conversations/${conversationId}/messages`);
}

export async function sendMessage(
  conversationId,
  content,
  topK = 5,
) {
  return request(
    `/chat/conversations/${conversationId}/messages`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content,
        top_k: topK,
      }),
    },
  );
}

export async function streamMessage(
  conversationId,
  content,
  {
    topK = 5,
    onSources,
    onToken,
    onDone,
    onError,
  } = {},
) {
  const response = await fetch(
    `${API_URL}/chat/conversations/${conversationId}/messages/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({
        content,
        top_k: topK,
      }),
    },
  );

  if (!response.ok) {
    let message = `Streaming request failed with status ${response.status}`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep default message.
    }

    throw new Error(message);
  }

  if (!response.body) {
    throw new Error("Streaming is not supported by this browser.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  try {
    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, {
        stream: true,
      });

      const events = buffer.split("\n\n");

      buffer = events.pop() || "";

      for (const event of events) {
        const line = event
          .split("\n")
          .find((item) => item.startsWith("data:"));

        if (!line) {
          continue;
        }

        const payload = line.slice(5).trim();

        if (!payload) {
          continue;
        }

        if (payload === "[DONE]") {
          continue;
        }

        const data = JSON.parse(payload);

        if (data.type === "sources") {
          onSources?.(data.sources || []);
        }

        if (data.type === "token") {
          onToken?.(data.content || "");
        }

        if (data.type === "done") {
          onDone?.(data);
        }

        if (data.type === "error") {
          onError?.(
            new Error(data.error || "Streaming failed."),
          );
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
