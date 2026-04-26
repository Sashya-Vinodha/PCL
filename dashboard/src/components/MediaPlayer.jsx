import React, { useState, useRef, useEffect } from 'react';

const PLAYLIST = [
  { id: '5qap5aO4i9A', title: 'Midnight City', artist: 'M83', prevLyric: 'The 1950s shit they want.....', activeLyric: 'Waiting in a car', nextLyric: 'Waiting for a ride in the dark', url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3' },
  { id: 'jfKfPfyJRdk', title: 'Lavender Haze', artist: 'Taylor Swift', prevLyric: 'Meet me at midnight', activeLyric: 'I just wanna stay in that lavender haze', nextLyric: 'Oooh oooh oooh woah', url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3' },
  { id: 'DWcJFNfaw9c', title: 'Nightcall', artist: 'Kavinsky', prevLyric: 'I\'m giving you a nightcall', activeLyric: 'To tell you how I feel', nextLyric: 'I want to drive you through the night', url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3' }
];

const glassStyle = {
  background: 'rgba(30, 35, 50, 0.45)',
  backdropFilter: 'blur(24px)',
  WebkitBackdropFilter: 'blur(24px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '24px',
  boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.25)',
};

export default function MediaPlayer() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const audioRef = useRef(null);
  const track = PLAYLIST[currentIndex];

  const togglePlay = () => {
    if (isPlaying) audioRef.current.pause();
    else audioRef.current.play();
    setIsPlaying(!isPlaying);
  };

  const nextTrack = () => setCurrentIndex((prev) => (prev + 1) % PLAYLIST.length);
  const prevTrack = () => setCurrentIndex((prev) => (prev - 1 + PLAYLIST.length) % PLAYLIST.length);

  useEffect(() => {
    if (isPlaying && audioRef.current) {
      audioRef.current.play().catch(e => console.log(e));
    }
  }, [currentIndex, isPlaying]);

  const handleTimeUpdate = () => {
    const current = audioRef.current.currentTime;
    const total = audioRef.current.duration;
    if (total) setProgress((current / total) * 100);
  };

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const newPercentage = (e.clientX - rect.left) / rect.width;
    audioRef.current.currentTime = newPercentage * audioRef.current.duration;
    setProgress(newPercentage * 100);
  };

  // CSS Waveform Generator
  const renderWaveform = () => {
    const bars = [];
    for(let i=0; i<30; i++) {
        // Randomize heights slightly based on playing state
        const height = isPlaying ? Math.floor(Math.random() * 20) + 10 : 5;
        bars.push(
            <div key={i} style={{ 
                width: '3px', 
                height: `${height}px`, 
                backgroundColor: 'rgba(255,255,255,0.4)', 
                borderRadius: '2px',
                transition: 'height 0.2s ease'
            }}></div>
        );
    }
    return <div style={{ display: 'flex', gap: '3px', alignItems: 'center', height: '40px' }}>{bars}</div>;
  };

  return (
    <div style={{ ...glassStyle, height: '100%', display: 'flex', alignItems: 'center', padding: '0 30px', justifyContent: 'space-between', position: 'relative' }}>
      
      <audio ref={audioRef} src={track.url} onTimeUpdate={handleTimeUpdate} onEnded={nextTrack} />

      {/* LEFT: Controls & Track Info */}
      <div style={{ display: 'flex', gap: '20px', alignItems: 'center', width: '300px' }}>
        <img src={`https://img.youtube.com/vi/${track.id}/maxresdefault.jpg`} alt="Cover" style={{ width: '75px', height: '75px', borderRadius: '16px', objectFit: 'cover', boxShadow: '0 5px 15px rgba(0,0,0,0.3)' }} />
        <div>
          <div style={{ fontWeight: 'bold', fontSize: '20px', color: '#fff' }}>{track.title}</div>
          <div style={{ color: '#8ba1b5', fontSize: '15px', marginTop: '4px' }}>{track.artist}</div>
          
          <div style={{ display: 'flex', gap: '15px', alignItems: 'center', marginTop: '12px' }}>
            <span style={{ opacity: 0.6, cursor: 'pointer' }}>🔀</span>
            <span onClick={prevTrack} style={{ cursor: 'pointer', fontSize: '18px' }}>⏮</span>
            <button onClick={togglePlay} style={{ background: '#4169E1', border: 'none', color: '#fff', width: '38px', height: '38px', borderRadius: '50%', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', boxShadow: '0 4px 10px rgba(65, 105, 225, 0.4)' }}>
              {isPlaying ? '⏸' : '▶'}
            </button>
            <span onClick={nextTrack} style={{ cursor: 'pointer', fontSize: '18px' }}>⏭</span>
            <span style={{ opacity: 0.6, cursor: 'pointer' }}>🔁</span>
          </div>
        </div>
      </div>

      {/* CENTER: Lyrics & Progress Bar */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '0 20px', position: 'relative' }}>
        
        <div style={{ textAlign: 'center', width: '100%' }}>
          <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.4)', marginBottom: '8px', transition: 'all 0.3s' }}>{track.prevLyric}</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#fff', textShadow: '0 2px 10px rgba(255,255,255,0.2)' }}>{track.activeLyric}</div>
          <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)', marginTop: '8px', transition: 'all 0.3s' }}>{track.nextLyric}</div>
        </div>
        
        {/* Progress Bar */}
        <div onClick={handleSeek} style={{ width: '80%', height: '4px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '2px', cursor: 'pointer', marginTop: '15px' }}>
          <div style={{ width: `${progress}%`, height: '100%', backgroundColor: '#fff', borderRadius: '2px', position: 'relative' }}>
             <div style={{ position: 'absolute', right: '-6px', top: '-4px', width: '12px', height: '12px', backgroundColor: '#fff', borderRadius: '50%', boxShadow: '0 0 8px rgba(255,255,255,0.8)' }}></div>
          </div>
        </div>
      </div>

      {/* RIGHT: Live Badge & Audio Waveform */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px', width: '250px', justifyContent: 'flex-end' }}>
         <div style={{ padding: '5px 12px', borderRadius: '15px', border: '1px solid rgba(255,255,255,0.2)', fontSize: '12px', color: 'rgba(255,255,255,0.7)', letterSpacing: '1px' }}>
             Live
         </div>
         {renderWaveform()}
      </div>

    </div>
  );
}