/**
 * WebSocket client for real-time room updates
 */
class RoomWebSocket {
  constructor(roomCode) {
    this.roomCode = roomCode;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.connect();
  }

  connect() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/${this.roomCode}`;

    console.log(`Connecting to WebSocket: ${wsUrl}`);
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (err) {
        console.error("Error parsing WebSocket message:", err);
      }
    };

    this.socket.onclose = () => {
      console.log("WebSocket disconnected");
      this.reconnect();
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  handleMessage(data) {
    console.log("WebSocket message received:", data);

    switch (data.type) {
      case "vote_changed":
        // Reload queue
        htmx.trigger("#queue-list", "queueUpdate");
        break;

      case "song_added":
        // Reload queue
        htmx.trigger("#queue-list", "queueUpdate");
        // Also update now playing if it should start playing
        if (data.should_play) {
          console.log("First song added - starting playback");
          htmx.trigger("#now-playing", "songUpdate");
        }
        break;

      case "song_removed":
        // Reload queue
        htmx.trigger("#queue-list", "queueUpdate");
        break;

      case "song_changed":
        // Update now playing
        htmx.trigger("#now-playing", "songUpdate");
        htmx.trigger("#queue-list", "queueUpdate");

        // If audio player exists, play next song
        if (data.next_song_id && window.audioPlayer) {
          // The audio player will auto-play when now_playing updates
          setTimeout(() => {
            const audioElement = document.getElementById("audio-player");
            if (audioElement && audioElement.dataset.previewUrl) {
              window.audioPlayer.play(audioElement.dataset.previewUrl);
            }
          }, 500);
        }
        break;

      case "user_joined":
        console.log("User joined:", data.user_name);
        // Reload user list
        htmx.trigger("#user-list", "userUpdate");
        // Update user count
        this.updateUserCount();
        break;

      case "user_left":
        console.log("User left");
        // Reload user list
        htmx.trigger("#user-list", "userUpdate");
        // Update user count
        this.updateUserCount();
        break;

      case "playback_play":
        // Resume playback
        if (window.audioPlayer) {
          window.audioPlayer.resume();
        }
        break;

      case "playback_pause":
        // Pause playback
        if (window.audioPlayer) {
          window.audioPlayer.pause();
        }
        break;

      default:
        console.log("Unknown message type:", data.type);
    }
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * this.reconnectAttempts;

      console.log(
        `Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`
      );

      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error("Max reconnection attempts reached");
      alert("Lost connection to server. Please refresh the page.");
    }
  }

  updateUserCount() {
    const authToken = sessionStorage.getItem("auth_token");
    if (!authToken) return;

    fetch(`/api/rooms/${this.roomCode}/status`, {
      headers: { Authorization: "Bearer " + authToken },
    })
      .then((res) => res.json())
      .then((data) => {
        const userCountElement = document.getElementById("user-count");
        if (userCountElement) {
          userCountElement.textContent = `(${data.users.length})`;
        }
      })
      .catch((err) => console.error("Error updating user count:", err));
  }

  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.error("WebSocket is not connected");
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }
}

// Initialize WebSocket when page loads
document.addEventListener("DOMContentLoaded", () => {
  const roomCode = document.querySelector("[data-room-code]")?.dataset.roomCode;
  if (roomCode) {
    window.roomWebSocket = new RoomWebSocket(roomCode);
  }
});

// Clean up on page unload
window.addEventListener("beforeunload", () => {
  if (window.roomWebSocket) {
    window.roomWebSocket.disconnect();
  }
});
