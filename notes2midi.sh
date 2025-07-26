if [ "$BPM" -lt 30 ] || [ "$BPM" -gt 300 ]; then
    echo "Error: BPM must be between 30 and 300" >&2
    exit 1
fi

# Calculate microseconds per tick for timing
MICROSECS_#!/bin/bash

# notes2midi.sh - Convert text music notes to MIDI hex output for ALSA rawmidi
# Usage: echo "C4.. D4. -. E4..." | ./notes2midi.sh [channel] [velocity] [note_off] [bpm]
# Notation:
#   C4, D4, etc. - Note names
#   . (dots) after notes - Note duration (each dot = 1/6 quarter note = 1 sixteenth note)
#   - (minus) - Silence/rest (each minus = 1/6 quarter note = 1 sixteenth note)
# Examples:
#   C4......  - C4 for 6 ticks (1 full quarter note)
#   C4.. --   - C4 for 2 ticks (1/3 quarter), then 2 ticks of silence
#   C4. D4. E4. F4. G4. A4. - Six sixteenth notes (1.5 quarter notes total)
#   At 120 BPM: 1 tick = ~83ms, 1 quarter note = 500ms

# Default parameters
CHANNEL=${1:-1}       # MIDI channel (1-16), default 1
VELOCITY=${2:-64}     # Note velocity (0-127), default 64
NOTE_OFF=${3:-off}    # Note-off handling: "on", "off", "auto", or "timed", default "off"
BPM=${4:-120}         # Beats per minute for timing calculations, default 120

# MIDI timing constants
PPQN=6                # Ticks per quarter note - coarse resolution (1 tick = 1 sixteenth note)
MICROSECS_PER_MIN=60000000  # Microseconds per minute

# Validate parameters
if [ "$CHANNEL" -lt 1 ] || [ "$CHANNEL" -gt 16 ]; then
    echo "Error: MIDI channel must be between 1 and 16" >&2
    exit 1
fi

if [ "$VELOCITY" -lt 0 ] || [ "$VELOCITY" -gt 127 ]; then
    echo "Error: Velocity must be between 0 and 127" >&2
    exit 1
fi

# Validate note-off parameter
case "$NOTE_OFF" in
    "on"|"off"|"auto")
        ;;
    *)
        echo "Error: Note-off parameter must be 'on', 'off', or 'auto'" >&2
        echo "  on   - Add note-off messages after all note-on messages" >&2
        echo "  off  - Only send note-on messages (default)" >&2
        echo "  auto - Send note-off immediately after each note-on" >&2
        exit 1
        ;;
if [ "$BPM" -lt 30 ] || [ "$BPM" -gt 300 ]; then
    echo "Error: BPM must be between 30 and 300" >&2
    exit 1
fi

# Calculate microseconds per tick for timing
MICROSECS_PER_QUARTER=$((MICROSECS_PER_MIN / BPM))
MICROSECS_PER_TICK=$((MICROSECS_PER_QUARTER / PPQN))

# Convert channel to 0-based (MIDI channels are 0-15 internally)
MIDI_CHANNEL=$((CHANNEL - 1))

# Note to MIDI number mapping
declare -A note_map=(
    ["C"]=0 ["C#"]=1 ["DB"]=1 ["D"]=2 ["D#"]=3 ["EB"]=3
    ["E"]=4 ["F"]=5 ["F#"]=6 ["GB"]=6 ["G"]=7 ["G#"]=8
    ["AB"]=8 ["A"]=9 ["A#"]=10 ["BB"]=10 ["B"]=11
)

# Function to convert note name to MIDI number (updated to handle dots and minus signs)
note_to_midi() {
    local note_input="$1"
    
    # Handle silence (minus signs)
    if [[ $note_input =~ ^-+$ ]]; then
        local minus_count=$(echo "$note_input" | grep -o '-' | wc -l)
        echo "REST:$minus_count"
        return 0
    fi
    
    # Remove dots and extract note part
    local note_part=$(echo "$note_input" | sed 's/[.-]*$//')
    local note_upper=$(echo "$note_part" | tr '[:lower:]' '[:upper:]')
    
    # Count dots for duration
    local dots=$(echo "$note_input" | grep -o '\.' | wc -l)
    
    # Default to 1 tick if no dots specified
    if [ "$dots" -eq 0 ]; then
        dots=1
    fi
    
    # Parse note name and octave
    if [[ $note_upper =~ ^([A-G][#B]?)([0-9])$ ]]; then
        local note_name="${BASH_REMATCH[1]}"
        local octave="${BASH_REMATCH[2]}"
        
        # Get base note number
        local base_note=${note_map[$note_name]}
        if [ -z "$base_note" ]; then
            echo "Error: Invalid note name '$note_name'" >&2
            return 1
        fi
        
        # Calculate MIDI note number (Middle C = C4 = 60)
        local midi_note=$((base_note + (octave + 1) * 12))
        
        # Validate MIDI note range (0-127)
        if [ "$midi_note" -lt 0 ] || [ "$midi_note" -gt 127 ]; then
            echo "Error: Note '$note_input' is out of MIDI range (0-127)" >&2
            return 1
        fi
        
        echo "$midi_note:$dots"
        return 0
    else
        echo "Error: Invalid note format '$note_input'. Use format like C4, F#5.., Bb3..., or --- for rests" >&2
        return 1
    fi
}

# Function to convert decimal to hex
dec_to_hex() {
    printf "%02X" "$1"
}

# Function to generate timed note sequence
generate_timed_note() {
    local midi_note="$1"
    local ticks="$2"
    local duration_ms=$((ticks * MICROSECS_PER_TICK / 1000))
    
    case "$NOTE_OFF" in
        "auto")
            # Note-on followed immediately by note-off
            echo -n "$(generate_note_on $midi_note)$(generate_note_off $midi_note)"
            ;;
        "timed")
            # Note-on, then note-off after duration (requires external timing)
            echo -n "$(generate_note_on $midi_note)"
            # Add timing info as comment for external processing
            if [ "$ticks" -gt 0 ]; then
                echo -n "# DELAY:${duration_ms}ms # $(generate_note_off $midi_note)"
            fi
            ;;
        *)
            # Just note-on
            echo -n "$(generate_note_on $midi_note)"
            ;;
    esac
}

# Function to generate MIDI note-on message
generate_note_on() {
    local midi_note="$1"
    local status_byte=$((0x90 + MIDI_CHANNEL))  # Note-on message + channel
    
    # Output as hex bytes
    echo -n "$(dec_to_hex $status_byte) $(dec_to_hex $midi_note) $(dec_to_hex $VELOCITY) "
}

# Function to generate MIDI note-off message
generate_note_off() {
    local midi_note="$1"
    local status_byte=$((0x80 + MIDI_CHANNEL))  # Note-off message + channel
    
    # Output as hex bytes
    echo -n "$(dec_to_hex $status_byte) $(dec_to_hex $midi_note) 00 "
}

# Main processing
output_hex=""
note_count=0
processed_notes=()

# Read input from stdin and store for potential note-off processing
input_data=""
while read -r line; do
    input_data="$input_data$line"

# Output the hex data
if [ -n "$output_hex" ]; then
    echo "$output_hex"
else
    echo "Error: No valid notes found in input" >&2
    exit 1
fi\n'
done

# Process each note in the input
while read -r line; do
    # Skip empty lines
    [ -z "$line" ] && continue
    
    # Process each note in the line
    for note in $line; do
        # Skip empty tokens
        [ -z "$note" ] && continue
        
        # Convert note to MIDI number
        midi_note=$(note_to_midi "$note")
        if [ $? -eq 0 ]; then
            # Generate note-on message
            output_hex="$output_hex$(generate_note_on $midi_note)"
            processed_notes+=("$midi_note")
            note_count=$((note_count + 1))
            
            # If auto mode, add note-off immediately after note-on
            if [ "$NOTE_OFF" = "auto" ]; then
                output_hex="$output_hex$(generate_note_off $midi_note)"
            fi
        fi
    done
done <<< "$input_data"

# Add note-off messages for all notes if mode is "on"
if [ "$NOTE_OFF" = "on" ]; then
    for midi_note in "${processed_notes[@]}"; do
        output_hex="$output_hex$(generate_note_off $midi_note)"
    done
fi

# Output the hex data
if [ -n "$output_hex" ]; then
    echo "$output_hex"
else
    echo "Error: No valid notes found in input" >&2
    exit 1
fi
