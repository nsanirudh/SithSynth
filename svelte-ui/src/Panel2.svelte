<script lang="ts">
  import { onMount } from 'svelte';
  import { OpenSheetMusicDisplay } from 'opensheetmusicdisplay';

  export let isOpen: boolean;

  let osmd: OpenSheetMusicDisplay | null = null;
  let osmdContainer: HTMLElement;

  onMount(() => {
    initializeOSMD();
  });

  async function initializeOSMD() {
    if (osmdContainer) {
      osmd = new OpenSheetMusicDisplay(osmdContainer, {
        drawTitle: false,
        drawComposer: false,
        drawPartNames: false,
        drawingParameters: "compact",
        autoResize: true
      });
    }
  }

  export function displaySheetMusic(musicXML: string) {
    if (osmd) {
      return osmd.load(musicXML).then(() => osmd.render());
    }
  }
</script>

<div class="panel" class:open={isOpen}>
  <div class="panel-content">
    <div bind:this={osmdContainer} class="osmd"></div>
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
    left: 160px;
    z-index: 1;
    opacity: 0;
    visibility: hidden;
  }

  .panel.open {
    width: calc(100vw - 160px);
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

  .osmd {
    width: 100%;
    height: 100%;
    background: rgba(26, 31, 83, 0.8);
    border: 1px solid #e2eeff;
    border-radius: 8px;
    box-shadow: 0 0 20px rgba(226, 238, 255, 0.2);
    backdrop-filter: blur(10px);
    padding: 1rem;
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .panel.open .osmd {
    opacity: 1;
    transform: translateY(0);
  }

  :global(.osmd svg) {
    filter: invert(1) hue-rotate(180deg) brightness(1.2);
    max-width: 100%;
    height: auto;
  }

  @media (max-width: 768px) {
    .panel {
      left: 96px;
    }

    .panel.open {
      width: calc(100vw - 96px);
    }

    .panel-content {
      padding: 0.5rem;
    }

    .osmd {
      padding: 0.5rem;
    }
  }
</style>