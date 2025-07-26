# MIDI Text Notation Converter

A pair of Linux shell scripts that convert between text-based music notation and MIDI hex data for direct ALSA rawmidi communication. Features a simple, AI-friendly notation system using dots for note duration and minus signs for rests.

## 🎵 Features

* **Bidirectional conversion** between text notation and MIDI
* **Simple notation**: Note names + dots for duration, minus signs for rests
* **Direct ALSA rawmidi output** - no external dependencies
* **Multiple note-off modes** for different use cases
* **Configurable MIDI channels and velocity**
* **Musical timing resolution** (6 ticks per quarter note)
* **AI-friendly format** for automated music generation

## 📁 Files

* `notes2midi.sh` - Convert text notation to MIDI hex
* `midi2notes.sh` - Convert MIDI input to text notation
* `CLAUDE.md` - Complete notation format documentation for AI agents
* `README.md` - This file

## 🎼 Notation Format

### Basic Elements

* **Notes**: `C4`, `F#5`, `Bb3` (note + optional accidental + octave)
* **Duration**: Dots after notes (`.` = 1/6 quarter note = 1 sixteenth note)
* **Rests**: Minus signs (`-` = 1/6 quarter note of silence)

### Duration Reference

    C4.         # 1 tick  (sixteenth note)
    C4...       # 3 ticks (eighth note)  
    C4......    # 6 ticks (quarter note)
    C4........  # 12 ticks (half note)

### Examples

    # Simple melody - four quarter notes
    C4...... D4...... E4...... F4......
    
    # Rhythm with rests
    C4... --- D4. - E4......
    
    # Mixed durations
    C4. D4. E4... F4......

## 🛠️ Installation

1. **Download the scripts:**
  
      wget https://github.com/your-repo/notes2midi.sh
      wget https://github.com/your-repo/midi2notes.sh
  
2. **Make executable:**
  
      chmod +x notes2midi.sh midi2notes.sh
  
3. **Check MIDI devices:**
  
      ls -la /dev/snd/midi*
      cat /proc/asound/cards
  

## 🚀 Usage

### notes2midi.sh - Text to MIDI

**Syntax:**

    ./notes2midi.sh [channel] [velocity] [note_off] [bpm]

**Parameters:**

* `channel`: MIDI channel 1-16 (default: 1)
* `velocity`: Note velocity 0-127 (default: 64)
* `note_off`: Note-off handling mode (default: off)
* `bpm`: Beats per minute for timing calculations (default: 120)

**Note-off Modes:**

* `off` - Only note-on messages
* `on` - All note-on messages, then all note-off messages
* `auto` - Note-off immediately after each note-on
* `timed` - Note-on with timing comments for external processing

**Examples:**

    # Basic usage
    echo "C4...... D4...... E4...... F4......" | ./notes2midi.sh
    
    # Specify channel and velocity
    echo "C4... D4... E4..." | ./notes2midi.sh 1 127
    
    # Auto note-off mode
    echo "C4. D4. E4. F4." | ./notes2midi.sh 1 100 auto
    
    # Send directly to MIDI device
    echo "C4...... G4...... C5......" | ./notes2midi.sh 1 127 auto | xxd -r -p > /dev/snd/midiC1D0

### midi2notes.sh - MIDI to Text

**Syntax:**

    ./midi2notes.sh [midi_device] [channel_filter]

**Parameters:**

* `midi_device`: MIDI device path or `-` for stdin (default: /dev/snd/midiC1D0)
* `channel_filter`: Channel filter 0=all, 1-16=specific (default: 0)

**Examples:**

    # Read from MIDI device
    ./midi2notes.sh /dev/snd/midiC1D0
    
    # Filter specific channel
    ./midi2notes.sh /dev/snd/midiC1D0 1
    
    # Read from stdin
    cat /dev/snd/midiC1D0 | ./midi2notes.sh - 1
    
    # Save to file
    ./midi2notes.sh /dev/snd/midiC1D0 > recorded_melody.txt

## 🔄 Complete Workflow Examples

### 1. Play a Melody

    # Create melody
    echo "C4...... D4... E4... F4...... G4...... A4... B4... C5......" > melody.txt
    
    # Convert and play
    cat melody.txt | ./notes2midi.sh 1 127 auto | xxd -r -p > /dev/snd/midiC1D0

### 2. Record and Convert Back

    # Terminal 1: Start recording
    ./midi2notes.sh /dev/snd/midiC1D0 1 > captured.txt
    
    # Terminal 2: Play something via MIDI keyboard or software
    
    # Terminal 1: Stop with Ctrl+C, then view results
    cat captured.txt
    # Output: C4... D4...... E4... F4......

### 3. Round-trip Test

    # Original melody
    echo "C4... D4... E4...... F4... G4......" > original.txt
    
    # Convert to MIDI and back
    cat original.txt | ./notes2midi.sh 1 100 auto | xxd -r -p > /dev/snd/midiC1D0
    # (With midi2notes.sh running in background to capture)

### 4. Batch Processing

    # Process multiple melodies
    for melody in melodies/*.txt; do
        echo "Playing: $melody"
        cat "$melody" | ./notes2midi.sh 1 127 auto | xxd -r -p > /dev/snd/midiC1D0
        sleep 2
    done

## 🎹 Musical Examples

### Classical Patterns

    # C Major Scale
    echo "C4. D4. E4. F4. G4. A4. B4. C5." | ./notes2midi.sh
    
    # Arpeggios
    echo "C4. E4. G4. C5. G4. E4. C4." | ./notes2midi.sh
    
    # Canon in D opening
    echo "D4...... A4...... B4...... F#4...... G4...... D4...... G4...... A4......" | ./notes2midi.sh

### Modern Patterns

    # Electronic beat
    echo "C4. - C4. - C4... C4. - C4......" | ./notes2midi.sh
    
    # Pop chord progression
    echo "C4...... G4...... Am4...... F4......" | ./notes2midi.sh
    
    # Jazz syncopation
    echo "C4... - E4. G4... - C5. - G4... E4......" | ./notes2midi.sh

## 🔧 Advanced Usage

### Custom Timing

    # Slow ballad (60 BPM)
    echo "C4...... D4...... E4......" | ./notes2midi.sh 1 80 auto 60
    
    # Fast tempo (180 BPM)  
    echo "C4. D4. E4. F4. G4. A4." | ./notes2midi.sh 1 120 auto 180

### Multiple Channels

    # Bass line on channel 2
    echo "C2...... G2...... C2...... G2......" | ./notes2midi.sh 2 100 auto &
    
    # Melody on channel 1
    echo "E4... G4... C5... G4... E4......" | ./notes2midi.sh 1 110 auto

### Integration with Other Tools

    # Generate with AI and play
    curl -s "http://your-ai-api/generate-melody" | ./notes2midi.sh 1 127 auto | xxd -r -p > /dev/snd/midiC1D0
    
    # Convert from other formats
    cat score.txt | sed 's/quarter/....../g' | ./notes2midi.sh
    
    # MIDI file analysis
    amidi -p hw:1,0 -d | ./midi2notes.sh - 1

## ⚠️ Troubleshooting

### MIDI Device Issues

    # List available MIDI devices
    aconnect -l
    ls /dev/snd/midi*
    cat /proc/asound/cards
    
    # Test MIDI device
    echo "90 60 7F 80 60 00" | xxd -r -p > /dev/snd/midiC1D0
    
    # Check permissions
    sudo chmod 666 /dev/snd/midi*

### Common Errors

**"MIDI device not found"**

* Check device path: `ls /dev/snd/midi*`
* Verify permissions: `ls -la /dev/snd/midi*`
* Try different device: `/dev/snd/midiC0D0`, `/dev/snd/midiC1D0`, etc.

**"Invalid note format"**

* Use proper format: `C4`, `F#5`, `Bb3`
* Check for typos in note names
* Ensure dots attach directly to notes: `C4...` not `C4 ...`

**"No output"**

* Verify MIDI device is receiving: `cat /dev/snd/midiC1D0`
* Check if synthesizer/DAW is listening
* Try different note-off modes

## 🎯 Performance Tips

### Optimizing for Real-time

    # Use auto mode for immediate note-off
    echo "C4. D4. E4." | ./notes2midi.sh 1 127 auto
    
    # Minimize processing with simple patterns
    echo "C4 D4 E4" | ./notes2midi.sh 1 127 off

### Batch Processing

    # Pre-generate MIDI data
    echo "C4...... D4...... E4......" | ./notes2midi.sh 1 127 auto > melody.hex
    
    # Play pre-generated data
    xxd -r -p melody.hex > /dev/snd/midiC1D0

## 🤖 AI Integration

For AI agents working with this notation, see `CLAUDE.md` for:

* Complete syntax specification
* Validation rules
* Generation guidelines
* Musical examples by style

**Quick AI Example:**

    # AI generates melody in our format
    echo "Generate a simple C major melody" | your-ai-tool
    # Output: C4...... D4... E4... F4...... G4...... A4... B4... C5......
    
    # Convert and play
    echo "C4...... D4... E4... F4...... G4...... A4... B4... C5......" | ./notes2midi.sh 1 127 auto | xxd -r -p > /dev/snd/midiC1D0

## 📚 Technical Details

* **Resolution**: 6 ticks per quarter note (coarse, readable resolution)
* **MIDI Standard**: Uses standard MIDI note-on/note-off messages
* **Timing**: Based on BPM calculations (120 BPM default)
* **Range**: Full MIDI note range (0-127)
* **Channels**: All 16 MIDI channels supported

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test with various MIDI devices
4. Submit pull request

## 📄 License

MIT License - feel free to use, modify, and distribute.

* * *

**Happy music making! 🎵**
