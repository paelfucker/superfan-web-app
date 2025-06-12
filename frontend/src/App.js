import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";
import AudioMotionAnalyzer from "audiomotion-analyzer";

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [responseText, setResponseText] = useState("");
  const [isBlinking, setIsBlinking] = useState(false);
  const [talkFrame, setTalkFrame] = useState(-1);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [randomBlink, setRandomBlink] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 1023);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);
  const ambientAudioRef = useRef(null);
  const audioMotionRef = useRef(null);
  const [isFirstInteraction, setIsFirstInteraction] = useState(false);
  const mouthTimerRef = useRef(null);

  useEffect(() => {
    ambientAudioRef.current = new Audio("/ambient.mp3");
    ambientAudioRef.current.loop = true;
    ambientAudioRef.current.volume = 0.5;

    const handleFirstClick = () => {
      if (!isFirstInteraction) {
        setIsFirstInteraction(true);
        ambientAudioRef.current.play().catch((err) => {
          console.warn("Autoplay failed", err);
        });
      }
    };

    window.addEventListener("click", handleFirstClick);
    setIsMobile(window.innerWidth <= 1023);

    const blinkInterval = setInterval(() => {
      if (!isSpeaking) {
        setIsBlinking(true);
        setTimeout(() => setIsBlinking(false), 150);
      }
    }, Math.random() * 4000 + 2000);

    return () => {
      window.removeEventListener("click", handleFirstClick);
      clearInterval(blinkInterval);
    };
  }, [isFirstInteraction, isSpeaking]);

useEffect(() => {
  if (!isMobile) return;

  const container = document.querySelector(".app-container");
  const titles = 5;
  const duration = 3000; // 3s per title

  for (let i = 0; i < titles; i++) {
    const img = document.createElement("img");
    img.src = `/title_${i + 1}.png`;
    img.className = "title-image";
    img.style.opacity = 0;
    img.className = "title-image vhs-jitter"
    img.style.animation =
      `flickerFade 2s ease-in ${i * duration}ms forwards, ` +
      `fadeOut 1s ease-in-out ${i * duration + duration - 500}ms forwards`;
    container.appendChild(img);
  }

  // 12 second delay for title_6 (12000ms)
  const title6Delay = 15000;
  const timeout = setTimeout(() => {
    const img6 = document.createElement("img");
    img6.src = "/title_6.png";
    img6.className = "title-image title-looping";
    img6.style.opacity = 0;
    img6.className = "title-image vhs-jitter title-looping"
    img6.style.animation = `fadeIn .5s ease-in ${title6Delay}ms forwards`;
    container.appendChild(img6);
  }, title6Delay);

  return () => clearTimeout(timeout);
}, [isMobile]);



  useEffect(() => {
    const spawnButterfly = () => {
      const img = document.createElement("img");
      img.src = "/butterfly.png";
      img.className = "single-butterfly";

      const fromLeft = Math.random() > 0.5;
      const startX = fromLeft ? "-100px" : "110vw";
      const endX = fromLeft ? "110vw" : "-100px";

      img.style.setProperty("--startX", startX);
      const startY = Math.random() * 40 + 20;
      const endY = Math.random() * 40 + 20;
      img.style.setProperty("--startY", `${startY}vh`);
      img.style.setProperty("--endX", endX);
      img.style.setProperty("--endY", `${endY}vh`);

      const jitterX = `${(Math.random() - 0.5) * 20}px`;
      const jitterY = `${(Math.random() - 0.5) * 20}px`;
      img.style.setProperty("--jitterX", jitterX);
      img.style.setProperty("--jitterY", jitterY);

      document.body.appendChild(img);
      setTimeout(() => {
        img.remove();
      }, 12000);
    };

    const firstTimeout = setTimeout(spawnButterfly, 30000);
    const interval = setInterval(spawnButterfly, 180000);

    return () => {
      clearTimeout(firstTimeout);
      clearInterval(interval);
    };
  }, []);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunksRef.current = [];
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        audioChunksRef.current.push(e.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("file", audioBlob, "recording.webm");

      const response = await axios.post("http://localhost:8000/ask", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        responseType: "blob",
      });

      const audioURL = URL.createObjectURL(response.data);
      const audio = new Audio(audioURL);
      audioRef.current = audio;

      const context = new (window.AudioContext || window.webkitAudioContext)();
      const sourceNode = context.createMediaElementSource(audio);

      const analyzer = new AudioMotionAnalyzer(document.createElement("div"), {
        source: sourceNode,
        audioCtx: context,
        mode: 0,
        useCanvas: false,
        connectSpeakers: false,
      });

      sourceNode.connect(context.destination);
      audioMotionRef.current = analyzer;

      const checkSpeaking = () => {
  if (!audio || audio.paused || !audioMotionRef.current) {
    setIsSpeaking(false);
    setTalkFrame(-1);
    return;
  }

  const energy = audioMotionRef.current.getEnergy("lowMid") || 0;
  const volume = Math.min(1, Math.max(0, energy / 0.4));

  setIsSpeaking(volume > 0.5);

  if (volume > 0.5) {
    if (!mouthTimerRef.current) {
      mouthTimerRef.current = setInterval(() => {
        setTalkFrame(prev => (prev === 0 ? -1 : 0));
      }, 150);
    }
  } else {
    clearInterval(mouthTimerRef.current);
    mouthTimerRef.current = null;
    setTalkFrame(-1);
  }

  requestAnimationFrame(checkSpeaking);
};

      requestAnimationFrame(checkSpeaking);

      audio.onended = () => {
        clearInterval(mouthTimerRef.current);
        mouthTimerRef.current = null;
        analyzer.destroy();
        audioMotionRef.current = null;
        setTalkFrame(-1);
        setIsSpeaking(false);
        setRandomBlink(false);
      };

      audio.play();

      const responseTextFromHeader = response.headers["x-chat-response"];
      if (responseTextFromHeader) {
        setResponseText(responseTextFromHeader);
      }
    };

    mediaRecorder.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const getSuperfanImage = () => {
    if (isBlinking) return "/superfan_blink.png";
    if (isSpeaking) {
      if (randomBlink) return "/superfan_talk_1.png";
      if (talkFrame === 0) return "/superfan_talk_0.png";
    }
    return "/superfan_idle.png";
  };

  return (
    <div className="app-container">
      <video className="background-video" autoPlay loop muted playsInline>
        <source src="/background.mp4" type="video/mp4" />
      </video>

      <div className="content">
        <img
          src={getSuperfanImage()}
          className="superfan-image vhs-jitter"
          alt="Superfan"
        />

        <div className="button-container">
          <div className="vhs-jitter">
            <img
              src={isRecording ? "/listening.png" : "/question.png"}
              alt="Mic Button"
              className="mic-button"
              onClick={isRecording ? stopRecording : startRecording}
            />
          </div>
          {isMobile && (
            <img
              src="/english.png"
              alt="English Badge"
              className="english-badge"
            />
          )}
        </div>

        <img src="/copyright.png" alt="Copyright" className="copyright" />
      </div>
    </div>
  );
}

export default App;
