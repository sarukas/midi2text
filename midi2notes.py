#!/usr/bin/env python3
"""
midi2notes.py - Convert MIDI rawmidi input to text music notes

Usage: python3 midi2notes.py [midi_device] [channel_filter]

Output notation:
  C4, D4, etc. - Note names
  . (dots) after notes - Note duration (each dot = 1/6 quarter note = 1 sixteenth note)
  - (minus) - Silence/rest between notes (each minus = 1/6 quarter note)

Examples:
  python3 midi2notes.py /dev/snd/midiC2D0 1
  cat /dev/snd/midiC2D0 | python3 midi2notes.py - 0
"""

import sys
import time
import argparse
import signal
from typing import Dict, Optional

# MIDI timing constants
PPQN = 6  # Ticks per quarter note (coarse resolution)
TICK_DURATION_MS = 83  # Approximate duration per tick at 120 BPM (~83ms)

class MIDIToNotesConverter:
    def __init__(self, midi_device: str = '/dev/snd/midiC2D0', channel_filter: int = 0):
        self.midi_device = midi_device
        self.channel_filter = channel_filter
        
        # Validate channel filter
        if not (0 <= channel_filter <= 16):
            raise ValueError("Channel filter must be between 0 (all) and 16")
        
        # State tracking
        self.active_notes: Dict[int, str] = {}  # MIDI note -> note name
        self.note_start_time: Dict[int, float] = {}  # MIDI note -> start timestamp
        self.last_note_end_time: float = 0  # Track when last note ended for rest detection
        self.any_notes_played: bool = False  # Track if we've had any notes yet
        
        # Setup signal handler for cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def midi_to_note(self, midi_num: int) -> str:
        """Convert MIDI number to note name"""
        octave = (midi_num // 12) - 1
        note_index = midi_num % 12
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return f"{notes[note_index]}{octave}"
    
    def get_timestamp(self) -> float:
        """Get current timestamp in milliseconds"""
        return time.time() * 1000
    
    def output_note_with_duration(self, note: str, start_time: float, end_time: float):
        """Output note with duration dots and flush immediately"""
        # Check for silence/rest before this note
        if self.any_notes_played and self.last_note_end_time > 0:
            silence_duration = start_time - self.last_note_end_time
            if silence_duration > TICK_DURATION_MS * 0.5:  # If silence is longer than half a tick
                silence_ticks = int(silence_duration / TICK_DURATION_MS)
                silence_ticks = max(1, min(silence_ticks, 24))  # Min 1, max 24 ticks
                
                # Output silence as minus signs followed by newline for pipeline compatibility
                silence_output = '-' * silence_ticks
                print(silence_output, flush=True)
        
        # Calculate duration in ticks (each tick = ~83ms at 120 BPM)
        duration_ms = end_time - start_time
        ticks = int(duration_ms / TICK_DURATION_MS)
        
        # Minimum 1 tick, maximum 24 ticks for readability (4 quarter notes)
        ticks = max(1, min(ticks, 24))
        
        # Output note with dots followed by newline for pipeline compatibility
        output = note + '.' * ticks
        print(output, flush=True)
        
        # Update tracking
        self.last_note_end_time = end_time
        self.any_notes_played = True
    
    def process_midi_message(self, status_byte: int, data1: int, data2: int):
        """Process a complete MIDI message"""
        # Extract message type and channel
        msg_type = (status_byte & 0xF0) >> 4
        channel = (status_byte & 0x0F) + 1
        
        # Apply channel filter
        if self.channel_filter != 0 and channel != self.channel_filter:
            return
        
        current_time = self.get_timestamp()
        
        if msg_type == 9:  # Note On (0x90-0x9F)
            if data2 > 0:  # Velocity > 0 means note on
                note = self.midi_to_note(data1)
                self.active_notes[data1] = note
                # Use current time as start time for the note
                self.note_start_time[data1] = current_time
            else:  # Velocity = 0 means note off
                if data1 in self.active_notes:
                    note = self.active_notes[data1]
                    start_time = self.note_start_time[data1]
                    self.output_note_with_duration(note, start_time, current_time)
                    del self.active_notes[data1]
                    del self.note_start_time[data1]
        
        elif msg_type == 8:  # Note Off (0x80-0x8F)
            if data1 in self.active_notes:
                note = self.active_notes[data1]
                start_time = self.note_start_time[data1]
                self.output_note_with_duration(note, start_time, current_time)
                del self.active_notes[data1]
                del self.note_start_time[data1]
    
    def read_midi_data(self):
        """Read and process MIDI data in real-time"""
        byte_count = 0
        status_byte = 0
        data1 = 0
        data2 = 0
        
        # Open MIDI device
        if self.midi_device == '-':
            print("Reading MIDI from stdin (Channel filter: {})".format(
                self.channel_filter if self.channel_filter else 'all'), file=sys.stderr)
            midi_file = sys.stdin.buffer
        else:
            try:
                print(f"Reading MIDI from {self.midi_device} (Channel filter: {self.channel_filter if self.channel_filter else 'all'})", file=sys.stderr)
                midi_file = open(self.midi_device, 'rb')
            except IOError as e:
                print(f"Error: Cannot open MIDI device {self.midi_device}: {e}", file=sys.stderr)
                print("Available MIDI devices:", file=sys.stderr)
                try:
                    import glob
                    midi_devices = glob.glob('/dev/snd/midi*')
                    for device in midi_devices:
                        print(f"  {device}", file=sys.stderr)
                except:
                    print("  No MIDI devices found", file=sys.stderr)
                sys.exit(1)
        
        print("Press Ctrl+C to stop", file=sys.stderr)
        print("", file=sys.stderr)
        
        try:
            # Read bytes one by one for real-time processing
            while True:
                byte_data = midi_file.read(1)
                if not byte_data:
                    if self.midi_device == '-':
                        break  # EOF on stdin
                    else:
                        continue  # Keep trying for device files
                
                byte_val = byte_data[0]
                
                # Check if this is a status byte (bit 7 set)
                if byte_val & 0x80:
                    # Process previous complete message if we have one
                    if byte_count == 3:
                        self.process_midi_message(status_byte, data1, data2)
                    
                    # Start new message
                    status_byte = byte_val
                    byte_count = 1
                else:
                    # Data byte
                    if byte_count == 1:
                        data1 = byte_val
                        byte_count = 2
                    elif byte_count == 2:
                        data2 = byte_val
                        byte_count = 3
                        # Process complete 3-byte message immediately
                        self.process_midi_message(status_byte, data1, data2)
                        byte_count = 1  # Reset for next message (keep status byte)
        
        except KeyboardInterrupt:
            pass
        finally:
            if self.midi_device != '-':
                midi_file.close()
            self._cleanup_active_notes()
    
    def _cleanup_active_notes(self):
        """Output any remaining active notes during cleanup"""
        print("", file=sys.stderr)
        print("Cleaning up active notes...", file=sys.stderr)
        
        current_time = self.get_timestamp()
        for midi_num in list(self.active_notes.keys()):
            note = self.active_notes[midi_num]
            start_time = self.note_start_time[midi_num]
            self.output_note_with_duration(note, start_time, current_time)
        
        print("", file=sys.stderr)
        print("Done.", file=sys.stderr)
    
    def _signal_handler(self, signum, frame):
        """Handle signals gracefully"""
        self._cleanup_active_notes()
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description='Convert MIDI rawmidi input to text music notes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 midi2notes.py /dev/snd/midiC2D0 1
  python3 midi2notes.py /dev/snd/midiC1D0 0  # All channels
  cat /dev/snd/midiC2D0 | python3 midi2notes.py - 1
  
Output format:
  C4......  - Quarter note (6 dots)
  C4...     - Eighth note (3 dots)
  C4.       - Sixteenth note (1 dot)
  Spaces separate notes (representing note-off periods)
        """)
    
    parser.add_argument('midi_device', nargs='?', default='/dev/snd/midiC2D0',
                       help='MIDI device path or "-" for stdin (default: /dev/snd/midiC2D0)')
    parser.add_argument('channel_filter', nargs='?', type=int, default=0,
                       help='Channel filter: 0=all, 1-16=specific channel (default: 0)')
    
    args = parser.parse_args()
    
    try:
        converter = MIDIToNotesConverter(args.midi_device, args.channel_filter)
        converter.read_midi_data()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
