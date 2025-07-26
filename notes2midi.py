#!/usr/bin/env python3
"""
notes2midi.py - Convert text music notes to MIDI hex output for ALSA rawmidi

Usage: echo "C4.. D4. -. E4..." | python3 notes2midi.py [channel] [velocity] [note_off] [bpm]

Notation:
  C4, D4, etc. - Note names
  . (dots) after notes - Note duration (each dot = 1/6 quarter note = 1 sixteenth note)
  - (minus) - Silence/rest (each minus = 1/6 quarter note = 1 sixteenth note)

Examples:
  C4......  - C4 for 6 ticks (1 full quarter note)
  C4.. --   - C4 for 2 ticks (1/3 quarter), then 2 ticks of silence
  C4. D4. E4. F4. G4. A4. - Six sixteenth notes (1.5 quarter notes total)
  At 120 BPM: 1 tick = ~83ms, 1 quarter note = 500ms
"""

import sys
import re
import argparse

# MIDI timing constants
PPQN = 6  # Ticks per quarter note (coarse resolution)
MICROSECS_PER_MIN = 60000000

# Note to MIDI number mapping
NOTE_MAP = {
    'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3,
    'E': 4, 'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8,
    'AB': 8, 'A': 9, 'A#': 10, 'BB': 10, 'B': 11
}

class MIDIConverter:
    def __init__(self, channel=1, velocity=64, note_off='off', bpm=120):
        # Validate parameters
        if not (1 <= channel <= 16):
            raise ValueError("MIDI channel must be between 1 and 16")
        if not (0 <= velocity <= 127):
            raise ValueError("Velocity must be between 0 and 127")
        if note_off not in ['on', 'off', 'auto', 'timed']:
            raise ValueError("Note-off parameter must be 'on', 'off', 'auto', or 'timed'")
        if not (30 <= bpm <= 300):
            raise ValueError("BPM must be between 30 and 300")
        
        self.channel = channel - 1  # Convert to 0-based (MIDI channels are 0-15 internally)
        self.velocity = velocity
        self.note_off = note_off
        self.bpm = bpm
        
        # Calculate timing
        self.microsecs_per_quarter = MICROSECS_PER_MIN // bpm
        self.microsecs_per_tick = self.microsecs_per_quarter // PPQN
        
        self.processed_notes = []
    
    def note_to_midi(self, note_input):
        """Convert note name to MIDI number and tick count"""
        note_input = note_input.strip()
        
        # Handle silence (minus signs)
        if re.match(r'^-+$', note_input):
            minus_count = note_input.count('-')
            return ('REST', minus_count)
        
        # Parse note with optional dots
        match = re.match(r'^([A-G][#B]?)([0-9])(\.*)$', note_input.upper())
        if not match:
            raise ValueError(f"Invalid note format '{note_input}'. Use format like C4, F#5.., Bb3..., or --- for rests")
        
        note_name, octave, dots = match.groups()
        octave = int(octave)
        dot_count = len(dots) if dots else 1  # Default to 1 tick if no dots
        
        # Get base note number
        if note_name not in NOTE_MAP:
            raise ValueError(f"Invalid note name '{note_name}'")
        
        base_note = NOTE_MAP[note_name]
        
        # Calculate MIDI note number (Middle C = C4 = 60)
        midi_note = base_note + (octave + 1) * 12
        
        # Validate MIDI note range (0-127)
        if not (0 <= midi_note <= 127):
            raise ValueError(f"Note '{note_input}' is out of MIDI range (0-127)")
        
        return (midi_note, dot_count)
    
    def generate_note_on(self, midi_note):
        """Generate MIDI note-on message"""
        status_byte = 0x90 + self.channel
        return f"{status_byte:02X} {midi_note:02X} {self.velocity:02X} "
    
    def generate_note_off(self, midi_note):
        """Generate MIDI note-off message"""
        status_byte = 0x80 + self.channel
        return f"{status_byte:02X} {midi_note:02X} 00 "
    
    def generate_timed_note(self, midi_note, ticks):
        """Generate timed note sequence"""
        duration_ms = (ticks * self.microsecs_per_tick) // 1000
        
        if self.note_off == 'auto':
            # Note-on followed immediately by note-off
            return self.generate_note_on(midi_note) + self.generate_note_off(midi_note)
        elif self.note_off == 'timed':
            # Note-on, then note-off after duration (requires external timing)
            result = self.generate_note_on(midi_note)
            if ticks > 0:
                result += f"# DELAY:{duration_ms}ms # " + self.generate_note_off(midi_note)
            return result
        else:
            # Just note-on
            return self.generate_note_on(midi_note)
    
    def convert_line(self, line):
        """Convert a line of text notation to MIDI hex"""
        line = line.strip()
        if not line:
            return ""
        
        output_hex = ""
        
        # Process each note in the line
        tokens = line.split()
        for token in tokens:
            if not token:
                continue
            
            try:
                note_info = self.note_to_midi(token)
                
                # Handle rests (silence)
                if note_info[0] == 'REST':
                    rest_ticks = note_info[1]
                    # For rests, we just add a comment or skip (no MIDI output for silence)
                    if self.note_off == 'timed':
                        rest_duration_ms = (rest_ticks * self.microsecs_per_tick) // 1000
                        output_hex += f"# REST:{rest_duration_ms}ms # "
                    continue
                
                midi_note, ticks = note_info
                
                # Generate appropriate MIDI output based on mode
                if self.note_off == 'timed' or (self.note_off == 'auto' and ticks > 0):
                    output_hex += self.generate_timed_note(midi_note, ticks)
                else:
                    output_hex += self.generate_note_on(midi_note)
                    self.processed_notes.append(midi_note)
                    
                    # If auto mode and no ticks, add note-off immediately
                    if self.note_off == 'auto' and ticks == 1:
                        output_hex += self.generate_note_off(midi_note)
                        
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                continue
        
        return output_hex
    
    def finalize(self):
        """Add final note-off messages if needed"""
        output_hex = ""
        
        # Add note-off messages for all notes if mode is "on"
        if self.note_off == 'on':
            for midi_note in self.processed_notes:
                output_hex += self.generate_note_off(midi_note)
        
        return output_hex

def main():
    parser = argparse.ArgumentParser(
        description='Convert text music notes to MIDI hex output for ALSA rawmidi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  echo "C4...... D4...... E4......" | python3 notes2midi.py
  echo "C4... D4... E4..." | python3 notes2midi.py 1 127 auto 120
  echo "C4. D4. E4. F4." | python3 notes2midi.py 2 100 auto
  
Note format:
  C4......  - Quarter note (6 dots)
  C4...     - Eighth note (3 dots)  
  C4.       - Sixteenth note (1 dot)
  ---       - Rest (3 sixteenth rests)
        """)
    
    parser.add_argument('channel', nargs='?', type=int, default=1,
                       help='MIDI channel (1-16), default: 1')
    parser.add_argument('velocity', nargs='?', type=int, default=64,
                       help='Note velocity (0-127), default: 64')
    parser.add_argument('note_off', nargs='?', default='off',
                       choices=['on', 'off', 'auto', 'timed'],
                       help='Note-off handling mode, default: off')
    parser.add_argument('bpm', nargs='?', type=int, default=120,
                       help='Beats per minute for timing calculations, default: 120')
    
    args = parser.parse_args()
    
    try:
        converter = MIDIConverter(args.channel, args.velocity, args.note_off, args.bpm)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process input from stdin
    output_hex = ""
    
    try:
        for line in sys.stdin:
            line_output = converter.convert_line(line)
            output_hex += line_output
        
        # Add final note-off messages if needed
        output_hex += converter.finalize()
        
        # Output the hex data
        if output_hex.strip():
            print(output_hex.strip())
        else:
            print("Error: No valid notes found in input", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        output_hex += converter.finalize()
        if output_hex.strip():
            print(output_hex.strip())
        sys.exit(0)
    except BrokenPipeError:
        # Handle broken pipe gracefully
        sys.exit(0)

if __name__ == '__main__':
    main()
