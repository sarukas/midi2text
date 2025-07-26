# MIDI Text Notation Converter

A pair of Python scripts that convert between text-based music notation and MIDI hex data for direct ALSA rawmidi communication. Features a simple, AI-friendly notation system using dots for note duration, minus signs for rests, and real-time timing support.

## 🎵 Features

- **Bidirectional conversion** between text notation and MIDI
- **Simple notation**: Note names + dots for duration, minus signs for rests
- **Real-time timing**: Proper note durations and rest periods
- **Direct ALSA rawmidi output** - no external dependencies
- **Multiple timing modes** for different use cases
- **Configurable MIDI channels and velocity**
- **Musical timing resolution** (6 ticks per quarter note)
- **AI-friendly format** for automated music generation
- **Real-time pipeline support** for live MIDI processing

## 📁 Files

- `notes2midi.py` - Convert text notation to MIDI hex with timing
- `midi2notes.py` - Convert MIDI input to text notation in real-time
- `CLAUDE.md` - Complete notation format documentation for AI agents
- `README.md` - This file

## 🎼 Notation Format

### Basic Elements
- **Notes**: `C4`, `F#5`, `Bb3` (note + optional accidental + octave)
- **Duration**: Dots after notes (`.` = 1/6 quarter note = 1 sixteenth note)
- **Rests**: Minus signs (`-` = 1/6 quarter note of silence)

### Duration Reference
```
C4.         # 1 tick  (sixteenth note)
C4...       # 3 ticks (eighth note)  
C4......    # 6 ticks (quarter note)
C4........  # 12 ticks (half note)
```

### Examples
```bash
# Simple melody - four quarter notes
C4...... D4...... E4...... F4......

# Rhythm with rests
C4... --- D4. - E4......

# Mixed durations
C4. D4. E4... F4......
```

## 🛠️ Installation

1. **Download the scripts:**
```bash
wget https://github.com/your-repo/notes2midi.py
wget https://github.com/your-repo/midi2notes.py
```

2. **Make executable:**
```bash
chmod +x notes2midi.py midi2notes.py
```

3. **Check Python version (3.6+ required):**
```bash
python3 --version
```

4. **Check MIDI devices:**
```bash
ls -la /dev/snd/midi*
cat /proc/asound/cards
```

## 🚀 Usage

### notes2midi.py - Text to MIDI

**Syntax:**
```bash
python3 notes2midi.py [channel] [velocity] [note_off] [bpm]
```

**Parameters:**
- `channel`: MIDI channel 1-16 (default: 1)
- `velocity`: Note velocity 0-127 (default: 64)  
- `note_off`: Timing mode (default: off)
- `bpm`: Beats per minute for timing calculations (default: 120)

**Timing Modes:**
- `off` - Only note-on messages (no timing)
- `on` - All note-on messages, then all note-off messages
- `auto` - Note-off immediately after each note-on (fast triggers)
- `timed` - Sequential timing with actual delays between notes
- `realtime` - Real-time timing with background note-offs (allows polyphony)

**Examples:**
```bash
# Basic usage
echo "C4...... D4...... E4...... F4......" | python3 notes2midi.py

# Real-time mode with proper timing
echo "C4... D4... E4..." | python3 notes2midi.py 1 127 realtime 120

# Fast percussion mode
echo "C4. D4. E4. F4." | python3 notes2midi.py 1 100 auto

# Send directly to MIDI device
echo "C4...... G4...... C5......" | python3 notes2midi.py 1 127 realtime | xxd -r -p > /dev/snd/midiC2D0
```

### midi2notes.py - MIDI to Text

**Syntax:**
```bash
python3 midi2notes.py [midi_device] [channel_filter]
```

**Parameters:**
- `midi_device`: MIDI device path or `-` for stdin (default: /dev/snd/midiC2D0)
- `channel_filter`: Channel filter 0=all, 1-16=specific (default: 0)

**Examples:**
```bash
# Read from MIDI device
python3 midi2notes.py /dev/snd/midiC2D0

# Filter specific channel
python3 midi2notes.py /dev/snd/midiC2D0 1

# Read from stdin
cat /dev/snd/midiC2D0 | python3 midi2notes.py - 1

# Save to file (real-time output)
python3 midi2notes.py /dev/snd/midiC2D0 > recorded_melody.txt
```

## 🔄 Complete Workflow Examples

### 1. Play a Melody with Timing
```bash
# Create melody with rests
echo "C4...... -- D4... - E4... --- F4......" > melody.txt

# Play with real-time timing
cat melody.txt | python3 notes2midi.py 1 127 realtime | xxd -r -p > /dev/snd/midiC2D0
```

### 2. Real-time MIDI Loop
```bash
# Record and play back simultaneously
python3 midi2notes.py /dev/snd/midiC2D0 1 | python3 notes2midi.py 1 127 realtime | xxd -r -p > /dev/snd/midiC2D0
```

### 3. Record and Analyze
```bash
# Terminal 1: Start recording with real-time output
python3 midi2notes.py /dev/snd/midiC2D0 1 | tee captured.txt

# Terminal 2: Play something via MIDI keyboard or software

# Terminal 1: Stop with Ctrl+C, then view results
cat captured.txt
# Output: C4... D4...... E4... F4......
```

### 4. Batch Processing with Timing
```bash
# Process multiple melodies with proper timing
for melody in melodies/*.txt; do
    echo "Playing: $melody"
    cat "$melody" | python3 notes2midi.py 1 127 realtime 120 | xxd -r -p > /dev/snd/midiC2D0
    sleep 1
done
```

## 🎹 Musical Examples

### Classical Patterns
```bash
# C Major Scale
echo "C4. D4. E4. F4. G4. A4. B4. C5." | python3 notes2midi.py 1 127 realtime

# Arpeggios with timing
echo "C4... E4... G4... C5... G4... E4... C4......" | python3 notes2midi.py 1 127 realtime

# Canon in D opening
echo "D4...... A4...... B4...... F#4...... G4...... D4...... G4...... A4......" | python3 notes2midi.py 1 127 realtime
```

### Modern Patterns
```bash
# Electronic beat with rests
echo "C4. - C4. - C4... C4. - C4......" | python3 notes2midi.py 1 127 realtime

# Pop chord progression
echo "C4...... G4...... Am4...... F4......" | python3 notes2midi.py 1 127 realtime

# Jazz syncopation
echo "C4... - E4. G4... - C5. - G4... E4......" | python3 notes2midi.py 1 127 realtime
```

## 🔧 Advanced Usage

### Custom Timing and Tempo
```bash
# Slow ballad (60 BPM)
echo "C4...... D4...... E4......" | python3 notes2midi.py 1 80 realtime 60

# Fast tempo (180 BPM)  
echo "C4. D4. E4. F4. G4. A4." | python3 notes2midi.py 1 120 realtime 180
```

### Multiple Channels
```bash
# Bass line on channel 2 (background)
echo "C2...... G2...... C2...... G2......" | python3 notes2midi.py 2 100 realtime &

# Melody on channel 1 (foreground)
echo "E4... G4... C5... G4... E4......" | python3 notes2midi.py 1 110 realtime
```

### Pipeline Processing
```bash
# Real-time MIDI effects loop
python3 midi2notes.py /dev/snd/midiC2D0 1 | \
while read note; do
    # Transpose up an octave
    echo "$note" | sed 's/\([A-G][#b]*\)\([0-9]\)/\1\$((\2+1))/g'
done | python3 notes2midi.py 1 127 realtime | xxd -r -p > /dev/snd/midiC2D0
```

### Integration with Other Tools
```bash
# Generate with AI and play
curl -s "http://your-ai-api/generate-melody" | python3 notes2midi.py 1 127 realtime | xxd -r -p > /dev/snd/midiC2D0

# Convert from other formats
cat score.txt | sed 's/quarter/....../g' | python3 notes2midi.py 1 127 realtime

# MIDI file analysis via virtual device
amidi -p hw:1,0 -d | python3 midi2notes.py - 1
```

## ⚠️ Troubleshooting

### MIDI Device Issues
```bash
# List available MIDI devices
aconnect -l
ls /dev/snd/midi*
cat /proc/asound/cards

# Test MIDI device
echo "90 60 7F 80 60 00" | xxd -r -p > /dev/snd/midiC2D0

# Check permissions
sudo chmod 666 /dev/snd/midi*
```

### Common Errors

**"MIDI device not found"**
- Check device path: `ls /dev/snd/midi*`
- Verify permissions: `ls -la /dev/snd/midi*`
- Try different device: `/dev/snd/midiC0D0`, `/dev/snd/midiC1D0`, etc.

**"Invalid note format"**
- Use proper format: `C4`, `F#5`, `Bb3`
- Check for typos in note names
- Ensure dots attach directly to notes: `C4...` not `C4 ...`

**"No output from pipeline"**
- Verify both scripts are working independently
- Check MIDI device is receiving: `cat /dev/snd/midiC2D0`
- Try different timing modes: `realtime`, `timed`, `auto`

**"Notes too fast/slow"**
- Adjust BPM: `python3 notes2midi.py 1 127 realtime 60` (slower)
- Use more/fewer dots: `C4......` (longer) vs `C4.` (shorter)
- Try different timing modes

## 🎯 Performance Tips

### Optimizing for Real-time
```bash
# Use realtime mode for live performance
echo "C4. D4. E4." | python3 notes2midi.py 1 127 realtime

# Use auto mode for percussion/triggers
echo "C4 D4 E4" | python3 notes2midi.py 1 127 auto
```

### Timing Accuracy
```bash
# For precise timing, use realtime mode
python3 notes2midi.py 1 127 realtime 120

# For sequential playback, use timed mode
python3 notes2midi.py 1 127 timed 120
```

## 🤖 AI Integration

For AI agents working with this notation, see `CLAUDE.md` for:
- Complete syntax specification
- Validation rules
- Generation guidelines
- Musical examples by style

**Quick AI Example:**
```bash
# AI generates melody in our format
echo "Generate a simple C major melody" | your-ai-tool
# Output: C4...... D4... E4... F4...... G4...... A4... B4... C5......

# Convert and play with proper timing
echo "C4...... D4... E4... F4...... G4...... A4... B4... C5......" | python3 notes2midi.py 1 127 realtime | xxd -r -p > /dev/snd/midiC2D0
```

## 📚 Technical Details

- **Resolution**: 6 ticks per quarter note (coarse, readable resolution)
- **MIDI Standard**: Uses standard MIDI note-on/note-off messages
- **Timing**: Real-time timing with background threading for note-offs
- **Range**: Full MIDI note range (0-127)
- **Channels**: All 16 MIDI channels supported
- **Python Version**: Requires Python 3.6+

## 🆕 What's New

### Version 2.0 - Python Rewrite
- **Complete Python rewrite** for better performance and reliability
- **Real-time timing support** with multiple timing modes
- **Background note-off threading** for polyphonic playback
- **Improved pipeline compatibility** with real-time output
- **Better error handling** and user feedback
- **Automatic rest detection** in midi2notes.py
- **Thread-safe operation** for concurrent note processing

### Timing Modes
- `realtime` - Background timing with polyphony support
- `timed` - Sequential timing with actual delays
- `auto` - Fast trigger mode for percussion
- Classic `on`/`off` modes for compatibility

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test with various MIDI devices and timing scenarios
4. Submit pull request

## 📄 License

MIT License - feel free to use, modify, and distribute.

---

**Happy music making with proper timing! 🎵⏰**
