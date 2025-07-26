#!/bin/bash

# midi2notes.sh - Convert MIDI rawmidi input to text music notes
# Usage: ./midi2notes.sh [midi_device] [channel_filter]
# Output notation:
#   C4, D4, etc. - Note names
#   . (dots) after notes - Note duration (each dot = 1/6 quarter note = 1 sixteenth note)
#   - (minus) - Silence/rest between notes (each minus = 1/6 quarter note)
# Examples:
#   C4...... - C4 for 6 ticks (1 full quarter note)
#   C4.. -- D4. - C4 for 1/3 quarter, 1/3 quarter rest, then D4 for 1/6 quarter

# Default parameters
MIDI_DEVICE=${1:-/dev/snd/midiC1D0}  # MIDI device path
CHANNEL_FILTER=${2:-0}               # Channel filter (0=all, 1-16=specific channel)

# MIDI timing constants
PPQN=6                              # Ticks per quarter note (coarse resolution)
TICK_DURATION_MS=83                 # Approximate duration per tick at 120 BPM (~83ms)

# Validate channel filter
if [ "$CHANNEL_FILTER" -lt 0 ] || [ "$CHANNEL_FILTER" -gt 16 ]; then
    echo "Error: Channel filter must be between 0 (all) and 16" >&2
    exit 1
fi

# MIDI number to note name mapping
midi_to_note() {
    local midi_num=$1
    local octave=$(( (midi_num / 12) - 1 ))
    local note_index=$(( midi_num % 12 ))
    
    local notes=("C" "C#" "D" "D#" "E" "F" "F#" "G" "G#" "A" "A#" "B")
    echo "${notes[$note_index]}$octave"
}

# Convert hex byte to decimal
hex_to_dec() {
    echo $((0x$1))
}

# Global state tracking
declare -A active_notes  # Track active notes with timestamps
declare -A note_start_time  # Track when notes started

# Function to get current timestamp in milliseconds
get_timestamp() {
    echo $(($(date +%s%N) / 1000000))
}

# Function to calculate duration and output dots
output_note_with_duration() {
    local note=$1
    local start_time=$2
    local end_time=$3
    
    # Calculate duration in ticks (each tick = ~83ms at 120 BPM)
    local duration_ms=$((end_time - start_time))
    local ticks=$((duration_ms / TICK_DURATION_MS))
    
    # Minimum 1 tick, maximum 24 ticks for readability (4 quarter notes)
    if [ $ticks -lt 1 ]; then
        ticks=1
    elif [ $ticks -gt 24 ]; then
        ticks=24
    fi
    
    # Output note with dots and flush immediately using /dev/stdout
    printf "%s" "$note" > /dev/stdout
    for ((i=0; i<ticks; i++)); do
        printf "." > /dev/stdout
    done
    printf " " > /dev/stdout
}

# Function to process MIDI message
process_midi_message() {
    local status_byte=$1
    local data1=$2
    local data2=$3
    
    # Extract message type and channel
    local msg_type=$(( (status_byte & 0xF0) >> 4 ))
    local channel=$(( (status_byte & 0x0F) + 1 ))
    
    # Apply channel filter
    if [ "$CHANNEL_FILTER" -ne 0 ] && [ "$channel" -ne "$CHANNEL_FILTER" ]; then
        return
    fi
    
    local current_time=$(get_timestamp)
    
    case $msg_type in
        9)  # Note On (0x90-0x9F)
            if [ "$data2" -gt 0 ]; then  # Velocity > 0 means note on
                local note=$(midi_to_note $data1)
                active_notes["$data1"]="$note"
                note_start_time["$data1"]="$current_time"
            else  # Velocity = 0 means note off
                if [ -n "${active_notes[$data1]}" ]; then
                    local note="${active_notes[$data1]}"
                    local start_time="${note_start_time[$data1]}"
                    output_note_with_duration "$note" "$start_time" "$current_time"
                    unset active_notes["$data1"]
                    unset note_start_time["$data1"]
                fi
            fi
            ;;
        8)  # Note Off (0x80-0x8F)
            if [ -n "${active_notes[$data1]}" ]; then
                local note="${active_notes[$data1]}"
                local start_time="${note_start_time[$data1]}"
                output_note_with_duration "$note" "$start_time" "$current_time"
                unset active_notes["$data1"]
                unset note_start_time["$data1"]
            fi
            ;;
    esac
}

# Function to read MIDI data with direct file descriptor access
read_midi_data() {
    local byte_count=0
    local status_byte=""
    local data1=""
    local data2=""
    
    # Open MIDI device for reading
    if [ "$MIDI_DEVICE" = "-" ]; then
        exec 3</dev/stdin
    else
        # Check if MIDI device exists
        if [ ! -e "$MIDI_DEVICE" ]; then
            echo "Error: MIDI device $MIDI_DEVICE not found" >&2
            echo "Available MIDI devices:" >&2
            ls -la /dev/snd/midi* 2>/dev/null >&2 || echo "No MIDI devices found" >&2
            exit 1
        fi
        exec 3<"$MIDI_DEVICE"
    fi
    
    echo "Reading MIDI from $MIDI_DEVICE (Channel filter: ${CHANNEL_FILTER:-all})" >&2
    echo "Press Ctrl+C to stop" >&2
    echo "" >&2
    
    # Read bytes directly from file descriptor without pipeline
    while true; do
        # Read one byte using dd for unbuffered input
        byte=$(dd if=/proc/self/fd/3 bs=1 count=1 2>/dev/null | od -An -tx1)
        
        # Check if we got data
        if [ -z "$byte" ]; then
            continue
        fi
        
        # Clean up the byte (remove spaces)
        hex_byte=$(echo "$byte" | tr -d ' ' | tr 'a-f' 'A-F')
        
        # Skip if conversion failed  
        if [ ${#hex_byte} -ne 2 ]; then
            continue
        fi
        
        local dec_byte=$(hex_to_dec "$hex_byte")
        
        # Check if this is a status byte (bit 7 set)
        if [ $((dec_byte & 0x80)) -ne 0 ]; then
            # Process previous complete message if we have one
            if [ $byte_count -eq 3 ]; then
                process_midi_message $(hex_to_dec "$status_byte") $(hex_to_dec "$data1") $(hex_to_dec "$data2")
            fi
            
            # Start new message
            status_byte="$hex_byte"
            byte_count=1
        else
            # Data byte
            case $byte_count in
                1)
                    data1="$hex_byte"
                    byte_count=2
                    ;;
                2)
                    data2="$hex_byte"
                    byte_count=3
                    # Process complete 3-byte message immediately
                    process_midi_message $(hex_to_dec "$status_byte") $(hex_to_dec "$data1") $(hex_to_dec "$data2")
                    byte_count=1  # Reset for next message (keep status byte)
                    ;;
            esac
        fi
    done
    
    # Close file descriptor
    exec 3<&-
}

# Cleanup function
cleanup() {
    echo "" >&2
    echo "Cleaning up active notes..." >&2
    
    # Output any remaining active notes
    local current_time=$(get_timestamp)
    for midi_num in "${!active_notes[@]}"; do
        local note="${active_notes[$midi_num]}"
        local start_time="${note_start_time[$midi_num]}"
        output_note_with_duration "$note" "$start_time" "$current_time"
    done
    
    echo "" >&2
    echo "Done." >&2
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Start reading MIDI data
read_midi_data
