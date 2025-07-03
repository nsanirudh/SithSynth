<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  export let isOpen: boolean;
  export let isLoading: boolean;
  export let error: string | null;
  const dispatch = createEventDispatcher();

  let complexity = 0.9;
  let timeSignatureNum = 4;
  let timeSignatureDen = 4;
  let valence = 1;
  let bars = 16;
  let density = "low";
  let isLSTM = false;

  function toggleModel() {
    isLSTM = !isLSTM;
  }

  function handleGenerate() {
    dispatch('generate', {
      complexity,
      timeSignatureNum,
      timeSignatureDen,
      valence,
      bars,
      density,
      model: isLSTM ? 'lstm' : 'transformer'
    });
  }

  $: complexityDisplay = complexity.toFixed(2);
</script>

<div class="panel" class:open={isOpen}>
  <div class="panel-content">
    <div class="form-container">
      <section class="header">
        <h1>
          Sen2Seq
          <span>A conditional lead sheet generator</span>
        </h1>
      </section>

      <form on:submit|preventDefault>
        <div class="grid-container">
          <div class="form-group complexity">
            <label for="temp">
              <span class="material-icons">tune</span>
              Complexity
            </label>
            <div class="slider-container">
              <div class="slider">
                <div class="show-value">
                  <span class="value-bubble" style="left: {((complexity-0.7)/0.6 * 100)}%">
                    {complexityDisplay}
                  </span>
                </div>
                <input 
                  type="range" 
                  id="custom-slider" 
                  min="0.7" 
                  max="1.3" 
                  step="0.01"
                  bind:value={complexity}
                >
              </div>
            </div>
          </div>

          <div class="form-group time-sig">
            <label for="time-sig-num">
              <span class="material-icons">schedule</span>
              Time Signature
            </label>
            <div class="time-signature">
              <select id="time-sig-num" bind:value={timeSignatureNum}>
                <option value={3}>3</option>
                <option value={4}>4</option>
              </select>
              <span class="time-sig-divider">/</span>
              <select id="time-sig-den" bind:value={timeSignatureDen}>
                <option value={4}>4</option>
              </select>
            </div>
          </div>

          <div class="form-group valence">
            <label for="valence">
              <span class="material-icons">mood</span>
              Valence
            </label>
            <div class="mood-selector">
              {#each [-2, -1, 0, 1, 2] as value}
                <button
                  type="button"
                  class="mood-btn"
                  class:selected={valence === value}
                  on:click={() => valence = value}
                >
                  <span class="material-icons">
                    {value === -2 ? 'sentiment_very_dissatisfied' :
                     value === -1 ? 'sentiment_dissatisfied' :
                     value === 0 ? 'sentiment_neutral' :
                     value === 1 ? 'sentiment_satisfied' :
                     'sentiment_very_satisfied'}
                  </span>
                </button>
              {/each}
            </div>
          </div>

          <div class="form-group bars">
            <label for="numOfBars">
              <span class="material-icons">straighten</span>
              Bars
            </label>
            <div class="bars-input">
              <button 
                type="button" 
                class="bars-btn"
                on:click={() => bars = Math.max(8, bars - 4)}
              >
                <span class="material-icons">remove</span>
              </button>
              <input 
                id="numOfBars" 
                type="number" 
                min="8" 
                max="40" 
                bind:value={bars}
              />
              <button 
                type="button" 
                class="bars-btn"
                on:click={() => bars = Math.min(40, bars + 4)}
              >
                <span class="material-icons">add</span>
              </button>
            </div>
          </div>

          <div class="form-group density">
            <label for="density">
              <span class="material-icons">density_medium</span>
              Density
            </label>
            <div class="density-buttons">
              {#each ['low', 'med', 'high'] as level}
                <button
                  type="button"
                  class="density-btn"
                  class:selected={density === level}
                  on:click={() => density = level}
                >
                  {level}
                </button>
              {/each}
            </div>
          </div>
        </div>

        <div class="model-selection">
          <button 
            type="button"
            class={isLSTM ? 'model-select' : 'model-unselect'} 
            on:click={toggleModel}
          >
            <span class="material-icons">memory</span>
            LSTM
          </button>
          <button 
            type="button"
            class={!isLSTM ? 'model-select' : 'model-unselect'} 
            on:click={toggleModel}
          >
            <span class="material-icons">hub</span>
            Transformer
          </button>
        </div>
      </form>

      <div class="generate-btn">
        <button 
          on:click={handleGenerate} 
          class={isLoading ? "gen-btn-press" : "gen-btn"}
          disabled={isLoading}
        >
          {#if isLoading}
            <span class="material-icons loading">autorenew</span>
          {:else}
            <span class="material-icons">play_arrow</span>
            Generate
          {/if}
        </button>
      </div>
      
      {#if error}
        <p class="error">
          <span class="material-icons">error</span>
          {error}
        </p>
      {/if}
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
    left: 40px;
    opacity: 0;
    visibility: hidden;
  }

  .panel.open {
    width: calc(100vw - 40px);
    opacity: 1;
    visibility: visible;
  }

  .panel-content {
    width: 100%;
    height: 100%;
    padding: 2rem;
    overflow-y: auto;
  }

  .form-container {
    max-width: 800px;
    margin: 0 auto;
    background: rgba(26, 31, 83, 0.8);
    padding: 2rem;
    border-radius: 12px;
    border: 1px solid #e2eeff;
    box-shadow: 0 0 20px rgba(226, 238, 255, 0.2);
    backdrop-filter: blur(10px);
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .panel.open .form-container {
    opacity: 1;
    transform: translateY(0);
  }

  .header {
    text-align: center;
    margin-bottom: 2rem;
  }

  h1 {
    font-family: 'Roboto Mono', monospace;
    font-size: clamp(1.5rem, 5vw, 2.5rem);
    color: #e2eeff;
    margin: 0;
    text-shadow: 0 0 10px rgba(226, 238, 255, 0.5);
  }

  h1 span {
    font-size: clamp(0.8rem, 2.5vw, 0.9rem);
    font-style: italic;
    display: block;
    color: rgba(226, 238, 255, 0.87);
    margin-top: 0.5rem;
  }

  .grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .form-group {
    background: rgba(10, 10, 31, 0.6);
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid rgba(226, 238, 255, 0.2);
    transition: all 0.3s ease;
  }

  .form-group:hover {
    border-color: rgba(226, 238, 255, 0.4);
    box-shadow: 0 0 15px rgba(226, 238, 255, 0.1);
  }

  .complexity {
    grid-column: 1 / -1;
  }

  label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    color: #e2eeff;
    font-family: 'Roboto Mono', monospace;
    text-transform: uppercase;
    font-size: clamp(0.8rem, 2vw, 0.9rem);
    letter-spacing: 1px;
  }

  .material-icons {
    font-size: clamp(16px, 4vw, 20px);
  }

  .slider-container {
    padding: 0 1rem;
  }

  .slider {
    position: relative;
    padding-top: 1.5rem;
  }

  input[type="range"] {
    -webkit-appearance: none;
    width: 100%;
    height: 2px;
    background: rgba(226, 238, 255, 0.3);
    outline: none;
    border-radius: 2px;
  }

  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px;
    height: 24px;
    background: #e2eeff;
    border-radius: 2px;
    cursor: pointer;
    box-shadow: 0 0 10px rgba(226, 238, 255, 0.5);
  }

  .value-bubble {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    background: rgba(226, 238, 255, 0.1);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    color: #e2eeff;
    border: 1px solid rgba(226, 238, 255, 0.3);
  }

  .time-signature {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    justify-content: center;
  }

  .time-sig-divider {
    color: #e2eeff;
    font-size: 1.5rem;
    font-weight: bold;
  }

  select {
    padding: 0.5rem;
    border: 1px solid #e2eeff;
    border-radius: 4px;
    background: rgba(10, 10, 31, 0.6);
    color: #e2eeff;
    font-family: 'Roboto Mono', monospace;
    cursor: pointer;
    min-width: 60px;
    text-align: center;
  }

  .mood-selector {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
  }

  .mood-btn {
    background: none;
    border: none;
    padding: 0.5rem;
    cursor: pointer;
    opacity: 0.5;
    transition: all 0.3s ease;
  }

  .mood-btn:hover {
    opacity: 0.8;
  }

  .mood-btn.selected {
    opacity: 1;
    transform: scale(1.1);
  }

  .bars-input {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  input[type="number"] {
    width: 80px;
    padding: 0.5rem;
    border: 1px solid #e2eeff;
    border-radius: 4px;
    background: rgba(10, 10, 31, 0.6);
    color: #e2eeff;
    text-align: center;
    font-family: 'Roboto Mono', monospace;
  }

  .bars-btn {
    background: none;
    border: 1px solid rgba(226, 238, 255, 0.3);
    padding: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .density-buttons {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
  }

  .density-btn {
    flex: 1;
    background: rgba(226, 238, 255, 0.1);
    border: 1px solid rgba(226, 238, 255, 0.3);
    padding: 0.5rem 1rem;
    text-transform: uppercase;
    font-size: 0.8rem;
    opacity: 0.7;
  }

  .density-btn.selected {
    background: rgba(226, 238, 255, 0.2);
    border-color: #e2eeff;
    opacity: 1;
  }

  .model-selection {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  .model-select, .model-unselect {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    border-radius: 4px;
    border: 1px solid #e2eeff;
    font-family: 'Roboto Mono', monospace;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: clamp(0.8rem, 2vw, 0.9rem);
  }

  .model-select {
    background: rgba(226, 238, 255, 0.2);
    color: #e2eeff;
    box-shadow: 0 0 15px rgba(226, 238, 255, 0.3);
  }

  .model-unselect {
    background: rgba(10, 10, 31, 0.6);
    color: rgba(226, 238, 255, 0.5);
  }

  .generate-btn {
    text-align: center;
    margin-top: 2rem;
  }

  .gen-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(226, 238, 255, 0.2);
    padding: 1rem 2rem;
    border-radius: 4px;
    border: 1px solid #e2eeff;
    color: #e2eeff;
    font-size: clamp(0.9rem, 2.5vw, 1rem);
    font-family: 'Roboto Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 0 15px rgba(226, 238, 255, 0.3);
  }

  .gen-btn:hover {
    background: rgba(226, 238, 255, 0.3);
    box-shadow: 0 0 20px rgba(226, 238, 255, 0.4);
  }

  .gen-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .loading {
    animation: spin 1s linear infinite;
  }

  .error {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    justify-content: center;
    color: #ff6b6b;
    text-align: center;
    margin-top: 1rem;
    font-family: 'Roboto Mono', monospace;
    font-size: clamp(0.8rem, 2vw, 0.9rem);
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 768px) {
    .panel-content {
      padding: 1rem;
    }

    .form-container {
      padding: 1rem;
    }

    .grid-container {
      grid-template-columns: 1fr;
    }

    .model-selection {
      flex-direction: column;
    }

    .model-select, .model-unselect {
      width: 100%;
      justify-content: center;
    }
  }
</style>