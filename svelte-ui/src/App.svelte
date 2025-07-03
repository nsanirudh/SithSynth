<script lang="ts">
  import { tick } from 'svelte';
  import Panel1 from './Panel1.svelte';
  import Panel2 from './Panel2.svelte';
  import Panel3 from './Panel3.svelte';

  let isLoading = false;
  let error: string | null = null;
  let activePanel: number = 0;
  let panel2Component: Panel2;
  let panel3Component: Panel3;

  function togglePanel(panelNumber: number) {
    activePanel = activePanel === panelNumber ? 0 : panelNumber;
  }

  async function handleGenerate(event) {
    isLoading = true;
    error = null;
    const {
      complexity,
      timeSignatureNum,
      timeSignatureDen,
      valence,
      bars,
      density,
      model
    } = event.detail;
    const backendURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
    try {
      const res = await fetch(`${backendURL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          temp: complexity,
          timsig_n: timeSignatureNum,
          timsig_d: timeSignatureDen,
          num_bars: bars,
          val: valence.toString(),
          den: density,
          modl: model
        })
      });
      if (!res.ok) throw new Error(`Generate failed: ${res.statusText}`);
      // Fetch and display sheet music
      const xmlRes = await fetch(`${backendURL}/xml`);
      if (!xmlRes.ok) throw new Error(`XML fetch failed: ${xmlRes.statusText}`);
      const xmlText = await xmlRes.text();
      activePanel = 2;
      await tick();
      await panel2Component.displaySheetMusic(xmlText);
      // Fetch and play MIDI after visualizer panel is visible
      const midiRes = await fetch(`${backendURL}/midi`);
      if (!midiRes.ok) throw new Error(`MIDI fetch failed: ${midiRes.statusText}`);
      const midiBuffer = await midiRes.arrayBuffer();
      activePanel = 3;
      await tick();
      await panel3Component.playMidi(midiBuffer);
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

</script>

<main>
  <div class="app-container">
    <div class="sidebars">
      <div class="sidebar" class:active={activePanel === 1}>
        <button type="button" class="sidebar-tab" on:click={() => togglePanel(1)}>
          <div class="tab-content">
            <span class="material-icons">tune</span>
            <span class="tab-label">Controls</span>
          </div>
          <div class="arrow-container">
            <span class="material-icons arrow" class:open={activePanel === 1}>
              chevron_left
            </span>
          </div>
        </button>
        <Panel1
          isOpen={activePanel === 1}
          isLoading={isLoading}
          error={error}
          on:generate={handleGenerate}
        />
      </div>

      <div class="sidebar" class:active={activePanel === 3}>
        <button type="button" class="sidebar-tab" on:click={() => togglePanel(3)}>
          <div class="tab-content">
            <span class="material-icons">graphic_eq</span>
            <span class="tab-label">Visualizer</span>
          </div>
          <div class="arrow-container">
            <span class="material-icons arrow" class:open={activePanel === 3}>
              chevron_left
            </span>
          </div>
        </button>
        <Panel3
          bind:this={panel3Component}
          isOpen={activePanel === 3}
        />
      </div>

      <div class="sidebar" class:active={activePanel === 2}>
        <button type="button" class="sidebar-tab" on:click={() => togglePanel(2)}>
          <div class="tab-content">
            <span class="material-icons">music_note</span>
            <span class="tab-label">Sheet Music</span>
          </div>
          <div class="arrow-container">
            <span class="material-icons arrow" class:open={activePanel === 2}>
              chevron_left
            </span>
          </div>
        </button>
        <Panel2
          bind:this={panel2Component}
          isOpen={activePanel === 2}
        />
      </div>
    </div>

    {#if activePanel === 0}
      <div class="welcome-container">
        <div class="welcome-message">
          <div class="logo">
            <span class="material-icons">music_note</span>
          </div>
          <h1>Sen2Seq</h1>
          <p>A conditional lead sheet generator</p>
          <div class="instructions">
            <p>Click on either panel to get started:</p>
            <ul>
              <li>
                <span class="material-icons">tune</span>
                <strong>Controls:</strong> Configure and generate music
              </li>
              <li>
                <span class="material-icons">graphic_eq</span>
                <strong>Visualizer:</strong> View audio waveform
              </li>
              <li>
                <span class="material-icons">music_note</span>
                <strong>Sheet Music:</strong> View generated sheet music
              </li>
            </ul>
          </div>
        </div>
      </div>
    {/if}
  </div>
</main>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap');
  @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

  :global(body) {
    margin: 0;
    padding: 0;
    min-height: 100vh;
    background: linear-gradient(45deg, #0a0a1f 0%, #1a1a4f 100%);
    overflow-x: hidden;
    font-family: 'Roboto Mono', monospace;
  }

  .app-container {
    display: flex;
    min-height: 100vh;
    position: relative;
  }

  .sidebars {
    display: flex;
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
  }

  .sidebar {
    position: relative;
    display: flex;
  }

  .sidebar-tab {
    width: 40px;
    background: rgba(226, 238, 255, 0.1);
    border-right: 1px solid #e2eeff;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
  }

  .sidebar.active .sidebar-tab {
    background: rgba(226, 238, 255, 0.2);
    box-shadow: 0 0 15px rgba(226, 238, 255, 0.3);
  }

  .tab-content {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%) rotate(-90deg);
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .arrow-container {
    position: absolute;
    bottom: 10px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .arrow {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 18px;
    opacity: 0.7;
  }

  .arrow.open {
    transform: rotate(180deg);
  }

  .material-icons {
    color: #e2eeff;
    font-size: 24px;
  }

  .tab-label {
    color: #e2eeff;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .welcome-container {
    position: fixed;
    left: 120px;
    top: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(45deg, #0a0a1f 0%, #1a1a4f 100%);
    padding: 1rem;
  }

  .welcome-message {
    text-align: center;
    padding: 2rem;
    background: rgba(26, 31, 83, 0.8);
    border: 1px solid #e2eeff;
    border-radius: 8px;
    box-shadow: 0 0 20px rgba(226, 238, 255, 0.2);
    max-width: 600px;
    width: 90%;
    backdrop-filter: blur(10px);
  }

  .logo {
    margin-bottom: 1rem;
  }

  .logo .material-icons {
    font-size: 48px;
    animation: pulse 2s infinite;
  }

  .welcome-message h1 {
    font-family: 'Roboto Mono', monospace;
    font-size: clamp(2rem, 8vw, 4rem);
    color: #e2eeff;
    margin: 0;
    line-height: 1.2;
    text-shadow: 0 0 10px rgba(226, 238, 255, 0.5);
  }

  .welcome-message p {
    font-size: clamp(1rem, 3vw, 1.2rem);
    color: rgba(226, 238, 255, 0.87);
    margin: 1rem 0;
  }

  .instructions {
    margin-top: 2rem;
    text-align: left;
    padding: 1.5rem;
    background: rgba(10, 10, 31, 0.6);
    border-radius: 8px;
    border: 1px solid rgba(226, 238, 255, 0.3);
  }

  .instructions ul {
    list-style-type: none;
    padding: 0;
    margin: 1rem 0 0;
  }

  .instructions li {
    font-size: clamp(0.875rem, 2.5vw, 1rem);
    color: rgba(226, 238, 255, 0.87);
    margin: 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .instructions li .material-icons {
    font-size: clamp(16px, 4vw, 20px);
  }

  .instructions strong {
    color: #e2eeff;
    font-family: 'Roboto Mono', monospace;
    text-transform: uppercase;
    font-size: clamp(0.8rem, 2vw, 0.9rem);
    letter-spacing: 1px;
  }

  @keyframes pulse {
    0% {
      transform: scale(1);
      opacity: 1;
    }
    50% {
      transform: scale(1.1);
      opacity: 0.7;
    }
    100% {
      transform: scale(1);
      opacity: 1;
    }
  }

  @media (max-width: 768px) {
    .sidebars {
      flex-direction: column;
    }

    .sidebar-tab {
      width: 32px;
    }

    .tab-content {
      transform: translate(-50%, -50%) rotate(0);
    }

    .tab-label {
      display: none;
    }

    .welcome-container {
      left: 32px;
      padding: 0.5rem;
    }

    .welcome-message {
      padding: 1rem;
    }

    .instructions {
      padding: 1rem;
    }
  }
</style>