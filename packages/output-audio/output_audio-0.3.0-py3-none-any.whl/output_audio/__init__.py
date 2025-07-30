# output_audio/__init__.py
import logging
import os
import queue
import threading
import time
import typing
from enum import Enum

import azure.cognitiveservices.speech as speechsdk
import numpy as np
import openai
import pydantic
import sounddevice as sd
import typing_extensions
from google import genai
from google.cloud import texttospeech
from google.genai import types
from str_or_none import str_or_none

__version__ = "0.3.0"

# Audio Configuration Constants
SAMPLE_RATE: int = 24_000  # Hz (matches OpenAI PCM output)
CHANNELS: int = 1  # Mono audio
DTYPE: str = "int16"  # 16-bit PCM samples
BLOCK_FRAMES: int = 1024  # PortAudio callback buffer size
CHUNK_BYTES: int = 4096  # TTS HTTP chunk size

# Pre-buffering configuration
PRE_BUFFER_DURATION: float = 0.2  # Seconds of audio to buffer before playback starts

# Audio padding for seamless transitions
ITEM_SILENCE: bytes = b"\x00" * int(SAMPLE_RATE * 0.05) * 2  # 50ms between items
FINAL_SILENCE: bytes = b"\x00" * int(SAMPLE_RATE * 0.2) * 2  # 200ms at end

logger = logging.getLogger(__name__)


class ItemState(str, Enum):
    """Playback state for monitoring (not used for synchronization)."""

    IDLE = "idle"
    STREAMING = "streaming"
    READY = "ready"


class AudioConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True
    )

    # Retry configuration
    max_retries: int = pydantic.Field(
        default=3, ge=0, description="Maximum number of retries on failure"
    )
    retry_delay: float = pydantic.Field(
        default=1.0, ge=0.0, description="Delay between retries in seconds"
    )


class OpenAITTSAudioConfig(AudioConfig):
    # model: str = "tts-1"
    model: str = "gpt-4o-mini-tts"
    voice: str = "nova"
    speed: float = 1.0
    instructions: str = (
        "Voice: Warm, upbeat, and reassuring, with a steady and confident cadence that keeps the conversation calm and productive. "  # noqa: E501
        "Speak at a *very fast* pace while maintaining clarity and emotional warmth. "
        "Tone: Positive and solution-oriented, always focusing on the next steps rather than dwelling on the problem. "  # noqa: E501
        "Dialect: Neutral and professional, avoiding overly casual speech but maintaining a friendly and approachable style."  # noqa: E501
    ).strip()
    openai_client: typing.Union["openai.OpenAI", "openai.AzureOpenAI"] = pydantic.Field(
        default_factory=lambda: openai.OpenAI()
    )


class TTSAudioConfig(OpenAITTSAudioConfig):
    pass


class AzureTTSAudioConfig(AudioConfig):
    subscription: pydantic.SecretStr | None = pydantic.Field(
        default=None, description="Azure TTS subscription key"
    )
    region: str = pydantic.Field(default="eastasia", description="Azure TTS region")
    voice: (
        typing.Literal[
            "en-US-NovaTurboMultilingualNeural",
            "ja-JP-MayuNeural",
            "zh-TW-HsiaoChenNeural",
        ]
        | str
    ) = pydantic.Field(
        default="en-US-NovaTurboMultilingualNeural", description="Azure TTS voice"
    )


class GeminiTTSAudioConfig(AudioConfig):
    model: typing.Literal["gemini-2.5-flash-preview-tts"] | str = pydantic.Field(
        default="gemini-2.5-flash-preview-tts", description="Gemini TTS model"
    )
    voice: (
        typing.Literal[
            "Achernar",  # Soft
            "Achird",  # Friendly
            "Algenib",  # Gravelly
            "Algieba",  # Smooth
            "Alnilam",  # Firm
            "Aoede",  # Breezy
            "Autonoe",  # Bright
            "Callirrhoe",  # Easy-going
            "Charon",  # Informative
            "Despina",  # Smooth
            "Enceladus",  # Breathy
            "Erinome",  # Clear
            "Fenrir",  # Excitable
            "Gacrux",  # Mature
            "Iapetus",  # Clear
            "Kore",  # Firm
            "Laomedeia",  # Upbeat
            "Leda",  # Youthful
            "Orus",  # Firm
            "Puck",  # Upbeat
            "Pulcherrima",  # Forward
            "Rasalgethi",  # Informative
            "Sadachbia",  # Lively
            "Sadaltager",  # Knowledgeable
            "Schedar",  # Even
            "Sulafat",  # Warm
            "Umbriel",  # Easy-going
            "Vindemiatrix",  # Gentle
            "Zephyr",  # Bright
            "Zubenelgenubi",  # Casual
        ]
        | str
    ) = pydantic.Field(default="Leda", description="Gemini TTS voice")
    api_key: pydantic.SecretStr | None = pydantic.Field(
        default=None, description="Gemini API key"
    )


class GoogleTTSAudioConfig(AudioConfig):
    language_code: (
        typing.Literal[
            "cmn-TW",
            "ja-JP",
            "en-US",
        ]
        | str
    ) = pydantic.Field(default="cmn-TW", description="Google TTS language code")
    voice: (
        typing.Literal[
            "cmn-TW-Wavenet-A",
            "ja-JP-Wavenet-A",
            "en-US-Wavenet-A",
        ]
        | str
    ) = pydantic.Field(default="cmn-TW-Wavenet-A", description="Google TTS voice")
    credentials_path: str | None = pydantic.Field(
        default=None, description="Path to Google Cloud service account JSON file"
    )
    speaking_rate: float = pydantic.Field(
        default=1.3,
        ge=0.25,
        le=2.0,
        description=(
            "Speaking rate/speed, in the range [0.25, 2.0]. "
            + "1.0 is the normal native speed supported by the specific voice."
        ),
    )


class AudioItem(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    audio_config: AudioConfig | None = None

    def read(
        self,
        chunk_size: int = CHUNK_BYTES,
    ) -> typing.Generator[bytes, None, None]:
        raise NotImplementedError


class OpenAITTSAudioItem(AudioItem):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    audio_config: TTSAudioConfig | None = None

    content: str

    @typing_extensions.override
    def read(
        self,
        chunk_size: int = CHUNK_BYTES,
    ) -> typing.Generator[bytes, None, None]:
        audio_config = (
            TTSAudioConfig() if self.audio_config is None else self.audio_config
        )
        openai_client = audio_config.openai_client

        with openai_client.audio.speech.with_streaming_response.create(
            input=self.content,
            model=audio_config.model,
            voice=audio_config.voice,
            instructions=audio_config.instructions,
            response_format="pcm",  # Raw PCM for direct playback
            speed=audio_config.speed,
        ) as response:
            # Stream chunks directly to queue as they arrive
            for chunk in response.iter_bytes(chunk_size=chunk_size):
                yield chunk


class AzureTTSAudioItem(AudioItem):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    audio_config: AzureTTSAudioConfig | None = None

    content: str

    @typing_extensions.override
    def read(
        self,
        chunk_size: int = CHUNK_BYTES,
    ) -> typing.Generator[bytes, None, None]:
        audio_config = (
            AzureTTSAudioConfig() if self.audio_config is None else self.audio_config
        )

        # Ensure subscription is available
        if audio_config.subscription is None:
            _might_subscription = str_or_none(os.getenv("AZURE_SUBSCRIPTION"))
            if not _might_subscription:
                raise ValueError("AZURE_SUBSCRIPTION is not set")
            audio_config.subscription = pydantic.SecretStr(_might_subscription)

        # Configure Azure Speech SDK
        speech_config = speechsdk.SpeechConfig(
            subscription=audio_config.subscription.get_secret_value(),
            region=audio_config.region,
        )

        # Set voice
        speech_config.speech_synthesis_voice_name = audio_config.voice

        # Set audio format to match our constants (16-bit PCM, 24kHz, mono)
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Raw24Khz16BitMonoPcm
        )

        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=None
        )

        # Perform synthesis and get result
        result = synthesizer.speak_text_async(self.content).get()

        if (
            result
            and result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
        ):
            # Get the audio data
            audio_data = result.audio_data

            # Yield audio data in chunks
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i : i + chunk_size]
                yield chunk

        elif result and result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            raise RuntimeError(
                f"Speech synthesis canceled: {cancellation_details.reason}, "
                f"{cancellation_details.error_details}"
            )
        else:
            reason = result.reason if result else "Unknown"
            raise RuntimeError(f"Speech synthesis failed with reason: {reason}")


class GeminiTTSAudioItem(AudioItem):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    audio_config: GeminiTTSAudioConfig | None = None

    content: str

    @typing_extensions.override
    def read(
        self,
        chunk_size: int = CHUNK_BYTES,
    ) -> typing.Generator[bytes, None, None]:
        audio_config = (
            GeminiTTSAudioConfig() if self.audio_config is None else self.audio_config
        )
        if audio_config.api_key is None:
            # Get API key from environment
            _might_api_key = str_or_none(os.getenv("GEMINI_API_KEY"))
            if not _might_api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            audio_config.api_key = pydantic.SecretStr(_might_api_key)

        # Create Gemini client
        client = genai.Client(api_key=audio_config.api_key.get_secret_value())

        # Generate audio content
        response = client.models.generate_content(
            model=audio_config.model,
            contents=self.content,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=audio_config.voice,
                        )
                    )
                ),
            ),
        )

        # Extract audio data with proper error handling
        if (
            not response.candidates
            or not response.candidates[0].content
            or not response.candidates[0].content.parts
            or not response.candidates[0].content.parts[0].inline_data
        ):
            raise RuntimeError("Invalid response from Gemini TTS API")

        audio_data = response.candidates[0].content.parts[0].inline_data.data

        if audio_data is None:
            raise RuntimeError("No audio data received from Gemini TTS API")

        # Yield audio data in chunks
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i : i + chunk_size]
            yield chunk


class GoogleTTSAudioItem(AudioItem):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    audio_config: GoogleTTSAudioConfig | None = None

    content: str

    @typing_extensions.override
    def read(
        self,
        chunk_size: int = CHUNK_BYTES,
    ) -> typing.Generator[bytes, None, None]:
        audio_config = (
            GoogleTTSAudioConfig() if self.audio_config is None else self.audio_config
        )

        # Handle credentials explicitly
        credentials_path = audio_config.credentials_path
        if credentials_path is None:
            # Try to get from environment variable
            _might_credentials_path = str_or_none(
                os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            )
            if not _might_credentials_path:
                raise ValueError(
                    "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set"
                )
            credentials_path = _might_credentials_path

        from google.oauth2 import service_account

        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # Set up synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=self.content)

        # Set up voice selection
        voice = texttospeech.VoiceSelectionParams(
            language_code=audio_config.language_code, name=audio_config.voice
        )

        # Set up audio config to match our constants (24kHz, 16-bit PCM, mono)
        tts_audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,  # 24000 Hz
            speaking_rate=audio_config.speaking_rate,
        )

        # Perform synthesis (non-streaming for regular Google TTS)
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=tts_audio_config
        )

        # Get the audio data
        audio_data = response.audio_content

        # Yield audio data in chunks
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i : i + chunk_size]
            yield chunk


class PlaylistItem(pydantic.BaseModel):
    """A single text segment to be converted to speech and played."""

    idx: int = pydantic.Field(..., description="Zero-based position in playlist")
    audio_item: AudioItem = pydantic.Field(..., description="Audio item to play")
    audio_queue: "queue.Queue[bytes | None]" = pydantic.Field(
        default_factory=lambda: queue.Queue(maxsize=150)
    )
    state: ItemState = pydantic.Field(default=ItemState.IDLE)

    model_config = pydantic.ConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True
    )

    def set_state(self, new_state: ItemState) -> None:
        """Safely transition to a new state with validation."""
        valid_transitions = {
            ItemState.IDLE: [ItemState.STREAMING],
            ItemState.STREAMING: [ItemState.READY],
            ItemState.READY: [ItemState.IDLE],  # Allow reset
        }

        if new_state not in valid_transitions.get(self.state, []):
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Invalid state transition from {self.state} to {new_state} "
                f"for item {self.idx}"
            )

        self.state = new_state


class Playlist(pydantic.BaseModel):
    items: typing.List[PlaylistItem] = pydantic.Field(
        default_factory=list, description="List of playlist items"
    )
    audio_producer_threads: typing.List[threading.Thread] = pydantic.Field(
        default_factory=list, description="List of audio producer threads"
    )
    start_event: threading.Event = pydantic.Field(
        default_factory=threading.Event,
        description="Event to signal when playback should start",
    )
    stop_event: threading.Event = pydantic.Field(
        default_factory=threading.Event,
        description="Event to signal when playback should stop",
    )
    current_idx: int = pydantic.Field(default=0, description="Next item to play")

    # References to playback queue and buffer
    playback_queue: "queue.Queue[bytes | None] | None" = pydantic.Field(
        default=None, description="Reference to playback queue"
    )
    buffer_remainder: "bytearray | None" = pydantic.Field(
        default=None, description="Reference to buffer remainder"
    )

    # Performance metrics
    metrics: typing.Dict[str, typing.Any] = pydantic.Field(
        default_factory=dict, description="Performance and status metrics"
    )

    model_config = pydantic.ConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True
    )

    def __iter__(self) -> typing.Generator[PlaylistItem, None, None]:
        for item in self.items:
            yield item

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> PlaylistItem:
        return self.items[idx]

    def __setitem__(self, idx: int, item: PlaylistItem) -> None:
        self.items[idx] = item

    def __delitem__(self, idx: int) -> None:
        del self.items[idx]

    def add_item(self, audio_item: AudioItem) -> None:
        """Dynamically add an item to the playlist."""

        item = PlaylistItem(idx=len(self.items), audio_item=audio_item)
        self.items.append(item)

        if self.start_event.is_set():
            thread = threading.Thread(target=self._run_audio_producer, args=(item,))
            self.audio_producer_threads.append(thread)
            thread.start()

    def is_all_items_ready(self) -> bool:
        """Check if all playlist items are done (basic check)."""
        return all(item.state == ItemState.READY for item in self.items)

    def is_playback_finished(self) -> bool:
        """Check if all playlist items are done AND all buffers are empty."""
        if not self.items:
            return True

        # Check if all items are done
        all_ready = all(item.state == ItemState.READY for item in self.items)

        # Check if playback queue and buffer are empty
        queue_empty = True
        buffer_empty = True

        if self.playback_queue is not None:
            queue_empty = self.playback_queue.empty()

        if self.buffer_remainder is not None:
            buffer_empty = not self.buffer_remainder

        return all_ready and queue_empty and buffer_empty

    def _set_playback_references(
        self, playback_queue: "queue.Queue[bytes | None]", buffer_remainder: bytearray
    ) -> None:
        """Internal method to set references to playback queue and buffer."""
        self.playback_queue = playback_queue
        self.buffer_remainder = buffer_remainder

    def get_metrics(self) -> typing.Dict[str, typing.Any]:
        """Get current performance and status metrics."""
        queue_size = 0
        buffer_size = 0

        if self.playback_queue is not None:
            queue_size = self.playback_queue.qsize()
        if self.buffer_remainder is not None:
            buffer_size = len(self.buffer_remainder)

        return {
            "total_items": len(self.items),
            "current_idx": self.current_idx,
            "active_threads": len(
                [t for t in self.audio_producer_threads if t.is_alive()]
            ),
            "queue_size": queue_size,
            "buffer_size": buffer_size,
            "items_by_state": {
                state.value: len([item for item in self.items if item.state == state])
                for state in ItemState
            },
            "is_playing": self.start_event.is_set() and not self.stop_event.is_set(),
            "playback_finished": self.is_playback_finished(),
        }

    def play(
        self,
        playback_queue: "queue.Queue[bytes | None]",
        *,
        max_playback_time: float = 10.0,
    ) -> None:
        """
        Merge individual item queues into a single playback_queue
        while allowing dynamic insertion of new items.
        """
        self.start_audio_producer()
        start_time = time.time()

        try:
            while True:
                # Wait until at least one un-played item is available
                while self.current_idx >= len(self.items):
                    if self.stop_event.is_set():
                        raise ManualStopException("Stop requested")

                    if time.time() - start_time > max_playback_time:
                        raise ManualStopException("Playback timed out")

                    time.sleep(0.05)  # small poll-sleep; keeps CPU low

                # Consume the next item
                audio_item = self.items[self.current_idx]
                self.current_idx += 1  # advance for the next loop

                while True:
                    if self.stop_event.is_set():
                        raise ManualStopException("Stop requested")

                    chunk = audio_item.audio_queue.get()

                    if chunk is None:  # end-of-item sentinel
                        playback_queue.put(ITEM_SILENCE)
                        break

                    playback_queue.put(chunk)

            # Add final silence once every queued item has finished
            playback_queue.put(FINAL_SILENCE)

        except ManualStopException:
            self.on_stop()

    def start_audio_producer(self):
        if self.start_event.is_set():
            return

        self.start_event.set()
        self.stop_event.clear()

        for item in self.items:
            thread = threading.Thread(target=self._run_audio_producer, args=(item,))
            self.audio_producer_threads.append(thread)
            thread.start()

    def on_stop(self):
        self.stop_event.set()
        for thread in self.audio_producer_threads:
            thread.join(timeout=0.1)
        # Ensure all threads have completed
        for thread in self.audio_producer_threads:
            if thread.is_alive():
                thread.join()

        for item in self.items:
            while not item.audio_queue.empty():
                item.audio_queue.get()
                item.set_state(ItemState.IDLE)

        self.audio_producer_threads.clear()
        self.start_event.clear()
        self.stop_event.clear()
        self.current_idx = 0

    def _run_audio_producer(self, item: PlaylistItem) -> None:
        """
        Streams TTS audio for a single item into its dedicated queue.
        """
        logger = logging.getLogger(__name__)

        # Update state for monitoring (non-blocking)
        item.set_state(ItemState.STREAMING)
        logger.debug(f"[Producer {item.idx}] Starting audio production")

        # Pre-buffering mechanism: accumulate initial data before playback
        initial_buffer = []
        # Calculate buffer size based on audio parameters
        bytes_per_sample = 2  # 16-bit PCM
        initial_buffer_size = int(
            SAMPLE_RATE * CHANNELS * bytes_per_sample * PRE_BUFFER_DURATION
        )
        current_buffer_size = 0

        try:
            for chunk in item.audio_item.read(chunk_size=CHUNK_BYTES):
                if self.stop_event.is_set():
                    logger.debug(f"[Producer {item.idx}] Stop event detected, breaking")
                    break

                # Accumulate initial buffer
                if current_buffer_size < initial_buffer_size:
                    initial_buffer.append(chunk)
                    current_buffer_size += len(chunk)

                    # Release all buffered data once we have enough
                    if current_buffer_size >= initial_buffer_size:
                        logger.debug(
                            f"[Producer {item.idx}] Pre-buffer complete, "
                            f"releasing {len(initial_buffer)} chunks"
                        )
                        for buffered_chunk in initial_buffer:
                            item.audio_queue.put(buffered_chunk)
                        initial_buffer = []  # Clear buffer list
                else:
                    # Initial buffer already released, put directly to queue
                    item.audio_queue.put(chunk)

        except Exception as exc:
            # On error, inject silence to keep playlist flowing
            logger.error(
                f"[Producer {item.idx}] Error during audio production: {exc!r}"
            )
            # Release any remaining buffered data
            for buffered_chunk in initial_buffer:
                item.audio_queue.put(buffered_chunk)
            item.audio_queue.put(ITEM_SILENCE)

        finally:
            # Ensure all buffered data is released
            for buffered_chunk in initial_buffer:
                item.audio_queue.put(buffered_chunk)
            # Signal completion with sentinel value
            item.audio_queue.put(None)  # Merger will recognize this as end-of-item
            item.set_state(ItemState.READY)
            logger.debug(f"[Producer {item.idx}] Audio production completed")


class ManualStopException(Exception):
    pass


# ──────────────────────────────────────────────────────────────
# PortAudio Callback Builder
# ──────────────────────────────────────────────────────────────


def create_audio_callback(
    playback_queue: "queue.Queue[typing.Optional[bytes]]",
    buffer_remainder: bytearray,
    playback_started: threading.Event,
):
    """
    Creates PortAudio callback function for real-time audio output.

    Args:
        playback_queue: Source of audio data
        buffer_remainder: Carries over partial frames between callbacks
        playback_started: Event signaled when actual audio begins

    Returns:
        Configured callback function for PortAudio
    """

    def audio_callback(outdata, frames, time_info, status):
        bytes_needed = frames * CHANNELS * 2  # 16-bit samples = 2 bytes each

        # Start with any leftover data from previous callback
        audio_buffer = bytearray(buffer_remainder)
        buffer_remainder.clear()

        # Fill buffer from queue until we have enough data
        while len(audio_buffer) < bytes_needed:
            try:
                _might_bytes = playback_queue.get_nowait()
                if _might_bytes is not None:
                    audio_buffer.extend(_might_bytes)
            except queue.Empty:
                break  # No more data available right now

        # Handle buffer size mismatches
        if len(audio_buffer) < bytes_needed:
            # Pad with silence if insufficient data
            audio_buffer.extend(b"\x00" * (bytes_needed - len(audio_buffer)))
        elif len(audio_buffer) > bytes_needed:
            # Save excess for next callback
            buffer_remainder.extend(audio_buffer[bytes_needed:])
            audio_buffer = audio_buffer[:bytes_needed]

        # Convert to numpy array and output
        outdata[:] = np.frombuffer(audio_buffer, np.int16).reshape(-1, CHANNELS)

        # Signal when first real audio (non-silence) starts playing
        if not playback_started.is_set() and any(audio_buffer):
            playback_started.set()

    return audio_callback


def output_audio(audio_items: typing.Sequence[AudioItem]) -> None:
    if not audio_items:
        return

    # Create playlist
    playlist = Playlist()
    for audio_item in audio_items:
        playlist.add_item(audio_item)

    # Start audio producers
    playlist.start_audio_producer()

    # Global queue that feeds the audio output device
    playback_queue: "queue.Queue[typing.Optional[bytes]]" = queue.Queue(maxsize=300)

    # Start playlist playback
    playlist_playback_thread = threading.Thread(
        target=playlist.play,
        args=(playback_queue,),
        name="Playlist Playback",
        daemon=True,
    )
    playlist_playback_thread.start()

    # Set up audio output
    buffer_remainder = bytearray()
    playback_started = threading.Event()

    # Start PortAudio stream - this begins immediate playback
    with sd.OutputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        blocksize=BLOCK_FRAMES,
        latency=0.2,  # 200ms latency works with pre-buffering mechanism
        callback=create_audio_callback(
            playback_queue, buffer_remainder, playback_started
        ),
    ):
        # Wait for first audio to start playing
        playback_started.wait()

        # Wait for playlist playback to finish
        playlist_playback_thread.join()

        # Continue playing until all audio data is consumed
        while not playback_queue.empty() or buffer_remainder:
            time.sleep(0.01)

        # Allow hardware buffer to drain completely
        time.sleep(0.5)

    # Clean up producer threads
    playlist.on_stop()


def output_playlist_audio(
    playlist: Playlist,
    *,
    playback_stop_event: threading.Event | None = None,
) -> None:
    # Start audio producers
    playlist.start_audio_producer()

    # Global queue that feeds the audio output device
    playback_queue: "queue.Queue[typing.Optional[bytes]]" = queue.Queue(maxsize=300)

    # Start playlist playback
    playlist_playback_thread = threading.Thread(
        target=playlist.play,
        args=(playback_queue,),
        name="Playlist Playback",
        daemon=True,
    )
    playlist_playback_thread.start()

    # Set up audio output
    buffer_remainder = bytearray()
    playback_started = threading.Event()

    # Set references in playlist so it can check buffer status
    playlist._set_playback_references(playback_queue, buffer_remainder)

    # Start PortAudio stream - this begins immediate playback
    with sd.OutputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        blocksize=BLOCK_FRAMES,
        latency=0.2,  # 200ms latency works with pre-buffering mechanism
        callback=create_audio_callback(
            playback_queue, buffer_remainder, playback_started
        ),
    ):
        # Wait for first audio to start playing
        playback_started.wait()

        # Wait for playlist playback to finish
        playlist_playback_thread.join()

        # Continue playing until all audio data is consumed
        while not playback_queue.empty() or buffer_remainder:
            time.sleep(0.01)

        if playback_stop_event is not None:
            playback_stop_event.wait()
        else:
            # Allow hardware buffer to drain completely
            time.sleep(0.5)

    # Clean up producer threads
    playlist.on_stop()
