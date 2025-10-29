// Audio player with gapless playback using Web Audio API
export interface AudioPlayerConfig {
  onTrackChange?: (verseNumber: number) => void;
  onPlayStateChange?: (isPlaying: boolean) => void;
  onError?: (error: Error) => void;
}

export class GaplessAudioPlayer {
  private audioContext: AudioContext | null = null;
  private currentSource: AudioBufferSourceNode | null = null;
  private nextSource: AudioBufferSourceNode | null = null;
  private currentBuffer: AudioBuffer | null = null;
  private nextBuffer: AudioBuffer | null = null;
  private gainNode: GainNode | null = null;
  
  private currentVerseIndex: number = 0;
  private verseUrls: string[] = [];
  private isPlaying: boolean = false;
  private config: AudioPlayerConfig;
  
  constructor(config: AudioPlayerConfig = {}) {
    this.config = config;
  }
  
  async initialize(verseUrls: string[]): Promise<void> {
    this.verseUrls = verseUrls;
    this.currentVerseIndex = 0;
    
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this.gainNode = this.audioContext.createGain();
      this.gainNode.connect(this.audioContext.destination);
    }
    
    // Preload first two audio files
    if (verseUrls.length > 0) {
      this.currentBuffer = await this.loadAudio(verseUrls[0]);
    }
    if (verseUrls.length > 1) {
      this.nextBuffer = await this.loadAudio(verseUrls[1]);
    }
  }
  
  private async loadAudio(url: string): Promise<AudioBuffer> {
    try {
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      return await this.audioContext!.decodeAudioData(arrayBuffer);
    } catch (error) {
      this.config.onError?.(error as Error);
      throw error;
    }
  }
  
  async play(): Promise<void> {
    if (!this.audioContext || !this.currentBuffer || !this.gainNode) {
      throw new Error('Audio player not initialized');
    }
    
    if (this.audioContext.state === 'suspended') {
      await this.audioContext.resume();
    }
    
    this.currentSource = this.audioContext.createBufferSource();
    this.currentSource.buffer = this.currentBuffer;
    this.currentSource.connect(this.gainNode);
    
    this.currentSource.onended = () => {
      this.onTrackEnded();
    };
    
    this.currentSource.start(0);
    this.isPlaying = true;
    this.config.onPlayStateChange?.(true);
    this.config.onTrackChange?.(this.currentVerseIndex + 1);
  }
  
  private async onTrackEnded(): Promise<void> {
    this.currentVerseIndex++;
    
    if (this.currentVerseIndex >= this.verseUrls.length) {
      // Reached end of surah
      this.stop();
      return;
    }
    
    // Move next buffer to current
    this.currentBuffer = this.nextBuffer;
    
    // Preload next buffer
    if (this.currentVerseIndex + 1 < this.verseUrls.length) {
      this.nextBuffer = await this.loadAudio(this.verseUrls[this.currentVerseIndex + 1]);
    } else {
      this.nextBuffer = null;
    }
    
    // Play next track seamlessly
    if (this.isPlaying) {
      await this.play();
    }
  }
  
  pause(): void {
    if (this.currentSource) {
      this.currentSource.stop();
      this.currentSource = null;
    }
    this.isPlaying = false;
    this.config.onPlayStateChange?.(false);
  }
  
  stop(): void {
    this.pause();
    this.currentVerseIndex = 0;
    this.config.onTrackChange?.(0);
  }
  
  async playVerse(verseIndex: number): Promise<void> {
    if (verseIndex < 0 || verseIndex >= this.verseUrls.length) {
      throw new Error('Invalid verse index');
    }
    
    this.pause();
    this.currentVerseIndex = verseIndex;
    this.currentBuffer = await this.loadAudio(this.verseUrls[verseIndex]);
    
    // Preload next
    if (verseIndex + 1 < this.verseUrls.length) {
      this.nextBuffer = await this.loadAudio(this.verseUrls[verseIndex + 1]);
    }
    
    await this.play();
  }
  
  getIsPlaying(): boolean {
    return this.isPlaying;
  }
  
  getCurrentVerseIndex(): number {
    return this.currentVerseIndex;
  }
  
  destroy(): void {
    this.pause();
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }
}
