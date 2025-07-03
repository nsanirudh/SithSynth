<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Midi } from '@tonejs/midi';
  import * as Tone from 'tone';

  export let isOpen: boolean;
  let canvas: HTMLCanvasElement;
  let analyser: AnalyserNode;
  let ctx: CanvasRenderingContext2D;
  let animationId: number;
  let part: Tone.Part | null = null;
  let isPlaying = false;

  onMount(() => {
    if (canvas) {
      ctx = canvas.getContext('2d');
      canvas.width = canvas.clientWidth;
      canvas.height = canvas.clientHeight;
    }
  });

  export async function playMidi(buffer: ArrayBuffer) {
    await Tone.start();
    // Resize canvas to visible dimensions and re-acquire context
    if (canvas) {
      canvas.width = canvas.clientWidth;
      canvas.height = canvas.clientHeight;
      ctx = canvas.getContext('2d');
    }
    const midi = new Midi(buffer);
    const now = Tone.now() + 0.5;
    const synth = new Tone.PolySynth().toDestination();
    analyser = Tone.context.createAnalyser();
    Tone.Destination.connect(analyser);

    const events: { time: number; note: string; duration: number }[] = [];
    midi.tracks.forEach(track => {
      track.notes.forEach(note => {
        events.push({
          time: now + note.time,
          note: note.name,
          duration: note.duration
        });
      });
    });

    part = new Tone.Part((time, value) => {
      synth.triggerAttackRelease(value.note, value.duration, time);
    }, events).start(now);

    Tone.Transport.start(now);
    isPlaying = true;
    visualize();
  }

  function visualize() {
    if (!analyser || !ctx) return;
    const bufferLength = analyser.fftSize;
    const dataArray = new Uint8Array(bufferLength);
    function draw() {
      analyser.getByteTimeDomainData(dataArray);
      ctx.fillStyle = '#0a0a1f';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#e2eeff';
      ctx.beginPath();
      const sliceWidth = canvas.width / bufferLength;
      let x = 0;
      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = v * (canvas.height / 2);
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
        x += sliceWidth;
      }
      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
      animationId = requestAnimationFrame(draw);
    }
    draw();
  }

  function togglePlayPause() {
    if (isPlaying) {
      Tone.Transport.pause();
    } else {
      Tone.Transport.start();
    }
    isPlaying = !isPlaying;
  }

  onDestroy(() => {
    if (part) {
      part.dispose();
      Tone.Transport.stop();
    }
    if (animationId) cancelAnimationFrame(animationId);
  });
</script>

<div class="panel" class:open={isOpen}>
  <div class="panel-content">
    <div class="visualizer-container">
      <h2>Audio Visualizer</h2>
      <canvas bind:this={canvas} class="waveform"></canvas>
      <div class="controls">
        <button class="control-btn" on:click={togglePlayPause}>
          <span class="material-icons">
            {isPlaying ? 'pause' : 'play_arrow'}
          </span>
        </button>
      </div>
    </div>
  </div>
</div>

<style>
  .panel {
    width: 0;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: linear-gradient(45deg, #0a0a1f 0%, #1a1a4f 100%);
    height: 100vh;
    position: fixed;
    left: 120px;
    z-index: 1;
    opacity: 0;
    visibility: hidden;
  }

  .panel.open {
    width: calc(100vw - 120px);
    opacity: 1;
    visibility: visible;
  }

  .panel-content {
    width: 100%;
    height: 100%;
    padding: 1rem;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .visualizer-container {
    max-width: 800px;
    margin: 0 auto;
    background: rgba(26, 31, 83, 0.8);
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e2eeff;
    box-shadow: 0 0 20px rgba(226, 238, 255, 0.2);
    backdrop-filter: blur(10px);
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .panel.open .visualizer-container {
    opacity: 1;
    transform: translateY(0);
  }

  h2 {
    color: #e2eeff;
    font-family: 'Roboto Mono', monospace;
    text-align: center;
    margin-bottom: 1.5rem;
    font-size: clamp(1.2rem, 4vw, 1.5rem);
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  .waveform {
    background: rgba(10, 10, 31, 0.6);
    width: 100%;
    height: 200px;
    border-radius: 8px;
    border: 1px solid rgba(226, 238, 255, 0.2);
    margin-bottom: 1rem;
  }

  .controls {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .control-btn {
    background: rgba(226, 238, 255, 0.1);
    border: 1px solid #e2eeff;
    border-radius: 50%;
    width: clamp(40px, 10vw, 48px);
    height: clamp(40px, 10vw, 48px);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .control-btn:hover {
    background: rgba(226, 238, 255, 0.2);
    box-shadow: 0 0 15px rgba(226, 238, 255, 0.3);
  }

  .material-icons {
    font-size: clamp(20px, 5vw, 24px);
    color: #e2eeff;
  }

  @media (max-width: 768px) {
    .panel {
      left: 64px;
    }

    .panel.open {
      width: calc(100vw - 64px);
    }

    .panel-content {
      padding: 0.5rem;
    }

    .visualizer-container {
      padding: 1rem;
    }

    .waveform {
      padding: 0.5rem;
    }
  }
</style>