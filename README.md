# Usage examples 

./midi2notes.sh [midi_device] [channel_filter]
./notes2midi.sh [midi_device] [channel_filter]

*Read from specific MIDI device, all channels*
./midi2notes.sh /dev/snd/midiC1D0 0

*Read from stdin, filter channel 1*
cat /dev/snd/midiC1D0 | ./midi2notes.sh - 1

*List available MIDI devices first*
ls /dev/snd/midi*

# Get started 
chmod +x notes2midi.sh midi2notes.sh

*Convert text to MIDI and play*
echo "C4. D4.. E4... F4." | ./notes2midi.sh 1 127 auto | xxd -r -p > /dev/snd/midiC1D0

*Record MIDI to text (in another terminal)*
./midi2notes.sh /dev/snd/midiC1D0 1 > recorded_notes.txt

*Test the round-trip*
echo "C4.. D4. E4... G4." > test_notes.txt
cat test_notes.txt | ./notes2midi.sh 1 100 auto | xxd -r -p > /dev/snd/midiC1D0

*Basic conversion with auto note-off*
echo "C4... D4. - E4...... --" | ./notes2midi.sh 1 127 auto 120

*Record MIDI and see the notation*
./midi2notes.sh /dev/snd/midiC1D0 1

# Complete round-trip test
echo "C4... D4... E4... F4..." > melody.txt
cat melody.txt | ./notes2midi.sh 1 100 auto | xxd -r -p > /dev/snd/midiC1D0

# Notation Examples 

## Quarter notes (6 dots each)
echo "C4...... D4...... E4...... F4......" | ./notes2midi.sh  1 100 auto | xxd -r -p > /dev/snd/midiC1D0

## Eighth notes (3 dots each)  
echo "C4... D4... E4... F4..." | ./notes2midi.sh  1 100 auto | xxd -r -p > /dev/snd/midiC1D0

## Sixteenth notes (1 dot each)
echo "C4. D4. E4. F4. G4. A4. B4. C5." | ./notes2midi.sh  1 100 auto | xxd -r -p > /dev/snd/midiC1D0

## Mixed durations with rests
echo "C4... --- D4. - E4...... --" | ./notes2midi.sh  1 100 auto | xxd -r -p > /dev/snd/midiC1D0

## Simple melody: quarter, eighth, eighth, half note
echo "C4...... D4... E4... F4............" | ./notes2midi.sh  1 100 auto | xxd -r -p > /dev/snd/midiC1D0
