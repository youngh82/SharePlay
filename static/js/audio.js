/**
 * Spotify Web Playback SDK Wrapper
 */
class SpotifySDKPlayer {
  constructor(token) {
    this.token = token;
    this.player = null;
    this.deviceId = null;
    this.isReady = false;
    this.currentTrackId = null;
    this.isPaused = false;
    this.isTrackEnding = false;

    this.initializePlayer();
  }

  initializePlayer() {
    console.log("Initializing Spotify SDK Player...");
    this.player = new Spotify.Player({
      name: "SharePlay Host Player",
      getOAuthToken: (cb) => {
        cb(this.token);
      },
      volume: 0.5,
    });

    // Error handling
    this.player.addListener("initialization_error", ({ message }) => {
      console.error("Initialization Error:", message);
    });
    this.player.addListener("authentication_error", ({ message }) => {
      console.error("Authentication Error:", message);
    });
    this.player.addListener("account_error", ({ message }) => {
      console.error("Account Error:", message);
    });
    this.player.addListener("playback_error", ({ message }) => {
      console.error("Playback Error:", message);
    });

    // Playback status updates
    this.player.addListener("player_state_changed", (state) => {
      console.log("Player state changed", state);
      if (!state) return;

      // Update UI based on state
      const playBtn = document.getElementById("btn-play");
      const pauseBtn = document.getElementById("btn-pause");

      if (state.paused) {
        // Only update UI if it's a manual pause (not track end)
        if (!this.isTrackEnding) {
          if (playBtn) playBtn.classList.remove("hidden");
          if (pauseBtn) pauseBtn.classList.add("hidden");
        }

        // Check if track ended (position is 0 and paused)
        if (
          state.position === 0 &&
          state.track_window.previous_tracks.length > 0
        ) {
          console.log("Track finished, auto-playing next...");
          this.isTrackEnding = true;
          this.playNextSongAuto();
        }
      } else {
        this.isTrackEnding = false;
        if (playBtn) playBtn.classList.add("hidden");
        if (pauseBtn) pauseBtn.classList.remove("hidden");
      }
    });

    // Ready
    this.player.addListener("ready", ({ device_id }) => {
      console.log("Ready with Device ID", device_id);
      this.deviceId = device_id;
      this.isReady = true;

      // Set initial volume from slider
      const volumeSlider = document.getElementById("volume-slider");
      if (volumeSlider) {
        const initialVolume = parseInt(volumeSlider.value);
        this.setVolume(initialVolume);
      }

      // Update UI
      const status = document.getElementById("player-status");
      if (status) status.textContent = "Player Ready ✓";
    });

    // Not Ready
    this.player.addListener("not_ready", ({ device_id }) => {
      console.log("Device ID has gone offline", device_id);
      this.isReady = false;
    });

    this.player.connect();
  }

  async play(spotifyUri) {
    console.log("=== PLAY CALLED ===");
    console.log("Device ID:", this.deviceId);
    console.log("Player ready:", this.isReady);
    console.log("Spotify URI:", spotifyUri);

    if (!this.deviceId) {
      console.error("❌ Player not ready - Device ID is null");
      alert(
        "Spotify Player not ready yet. Please wait a few seconds and try again."
      );
      return;
    }

    // Validate Spotify URI format
    if (!spotifyUri || !spotifyUri.startsWith("spotify:")) {
      console.error("❌ Invalid Spotify URI:", spotifyUri);
      alert("Invalid song URI. Please try adding a different song.");
      return;
    }

    console.log("✓ Attempting playback...");

    try {
      // Use Spotify Web API to play on this device
      const url = `https://api.spotify.com/v1/me/player/play?device_id=${this.deviceId}`;
      console.log("API URL:", url);

      const response = await fetch(url, {
        method: "PUT",
        body: JSON.stringify({ uris: [spotifyUri] }),
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.token}`,
        },
      });

      console.log("Response status:", response.status);

      if (response.ok || response.status === 204) {
        console.log("✓ Playback started successfully");
        this.isPaused = false;
        // Update UI
        const playBtn = document.getElementById("btn-play");
        const pauseBtn = document.getElementById("btn-pause");
        if (playBtn) playBtn.classList.add("hidden");
        if (pauseBtn) pauseBtn.classList.remove("hidden");
      } else {
        const error = await response.text();
        console.error("❌ Playback failed:", response.status, error);

        // Show user-friendly error
        if (response.status === 403) {
          alert(
            "Spotify Premium required for playback. Please upgrade your account."
          );
        } else if (response.status === 404) {
          alert("Device not found. Try refreshing the page.");
        } else {
          alert(
            `Playback error: ${response.status}. Check console for details.`
          );
        }
      }
    } catch (err) {
      console.error("❌ Error starting playback:", err);
      alert("Network error. Please check your connection and try again.");
    }
  }

  resume() {
    if (this.player) {
      this.player.resume().then(() => {
        console.log("Resumed");
        this.isPaused = false;
        // Update UI
        const playBtn = document.getElementById("btn-play");
        const pauseBtn = document.getElementById("btn-pause");
        if (playBtn) playBtn.classList.add("hidden");
        if (pauseBtn) pauseBtn.classList.remove("hidden");
      });
    }
  }

  pause() {
    if (this.player) {
      this.player.pause().then(() => {
        console.log("Paused");
        this.isPaused = true;
        // Update UI
        const playBtn = document.getElementById("btn-play");
        const pauseBtn = document.getElementById("btn-pause");
        if (playBtn) playBtn.classList.remove("hidden");
        if (pauseBtn) pauseBtn.classList.add("hidden");
      });
    }
  }

  setVolume(volume) {
    if (!this.player) {
      console.warn("Player not initialized yet");
      return;
    }

    // Spotify SDK accepts volume from 0.0 to 1.0
    const volumeDecimal = Math.max(0, Math.min(1, volume / 100));
    console.log(`Setting volume to ${volume}% (${volumeDecimal})`);

    this.player
      .setVolume(volumeDecimal)
      .then(() => {
        console.log(`✓ Volume successfully set to ${volume}%`);

        // Verify the volume was set
        this.player.getVolume().then((vol) => {
          console.log(`Current volume: ${Math.round(vol * 100)}%`);
        });
      })
      .catch((err) => {
        console.error("Failed to set volume:", err);
      });
  }

  async playNextSong() {
    console.log("Requesting next song...");
    const roomCode =
      document.querySelector("[data-room-code]")?.dataset.roomCode;
    const authToken = sessionStorage.getItem("auth_token");

    if (!roomCode || !authToken) return;

    try {
      await fetch(`/api/playback/skip/${roomCode}`, {
        method: "POST",
        headers: {
          Authorization: "Bearer " + authToken,
        },
      });

      // Trigger UI updates
      if (typeof htmx !== "undefined") {
        htmx.trigger(document.body, "queueUpdate");
        htmx.trigger(document.body, "songUpdate");
      }
    } catch (err) {
      console.error("Error skipping song:", err);
    }
  }

  async playNextSongAuto() {
    console.log("Auto-playing next song after track end...");

    // Check if player is ready before attempting auto-play
    if (!this.isReady || !this.deviceId) {
      console.warn("Player not ready for auto-play");
      this.isTrackEnding = false;
      return;
    }

    const roomCode =
      document.querySelector("[data-room-code]")?.dataset.roomCode;
    const authToken = sessionStorage.getItem("auth_token");

    if (!roomCode || !authToken) {
      this.isTrackEnding = false;
      return;
    }

    try {
      const response = await fetch(`/api/playback/skip/${roomCode}`, {
        method: "POST",
        headers: {
          Authorization: "Bearer " + authToken,
        },
      });

      if (response.ok) {
        const data = await response.json();

        // Trigger UI updates - HTMX will handle auto-play via htmx:afterSwap
        if (typeof htmx !== "undefined") {
          htmx.trigger(document.body, "queueUpdate");
          htmx.trigger(document.body, "songUpdate");
        }

        // The htmx:afterSwap event listener will automatically play the new song
        // No need to manually call play() here to avoid duplicate attempts
      } else if (response.status === 404) {
        console.log("No more songs in queue");
        this.isTrackEnding = false;
      }
    } catch (err) {
      console.error("Error auto-playing next song:", err);
      this.isTrackEnding = false;
    }
  }
}

// Auto-play when now playing updates
document.addEventListener("htmx:afterSwap", (event) => {
  if (event.detail.target.id === "now-playing") {
    console.log("Now playing updated");

    // Get the Spotify URI from the updated HTML
    const audioElement = document.getElementById("audio-player");

    if (!audioElement) {
      console.log("No audio-player element found");
      return;
    }

    const uri = audioElement.dataset.spotifyUri;
    if (!uri) {
      console.log("No Spotify URI found in audio-player element");
      return;
    }

    // Wait for audioPlayer if not ready yet (with timeout)
    const tryAutoPlay = (retries = 0) => {
      if (window.audioPlayer && window.audioPlayer.isReady) {
        console.log("Auto-playing new song:", uri);
        window.audioPlayer.play(uri);
      } else if (retries < 10) {
        console.log(`Waiting for audioPlayer... (${retries + 1}/10)`);
        setTimeout(() => tryAutoPlay(retries + 1), 500);
      } else {
        console.warn(
          "❌ audioPlayer not ready after 5 seconds, skipping auto-play"
        );
      }
    };

    tryAutoPlay();
  }
});
