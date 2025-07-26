# CLAUDE Music Notation Format

## Overview

This document describes a simple text-based music notation format designed for AI agents to read, understand, and generate musical sequences. The notation uses standard note names combined with dots and minus signs to represent duration and silence.

## Basic Elements

### Note Names
- **Format**: `[Note][Accidental][Octave]`
- **Note**: A, B, C, D, E, F, G (case insensitive)
- **Accidental**: `#` (sharp) or `b` (flat) - optional
- **Octave**: 0-9 (Middle C = C4)

**Examples**:
- `C4` - Middle C
- `F#5` - F sharp in the 5th octave
- `Bb3` - B flat in the 3rd octave

### Duration (Dots)
- Each dot (`.`) represents **1 tick = 1/6 of a quarter note = 1 sixteenth note**
- Dots immediately follow the note name with no spaces
- No dots = 1 tick (minimum duration)

**Duration Reference**:
- `C4.` - 1 tick (1 sixteenth note)
- `C4...` - 3 ticks (1 eighth note)
- `C4......` - 6 ticks (1 quarter note)
- `C4............` - 12 ticks (1 half note)
- `C4........................` - 24 ticks (1 whole note)

### Silence/Rests (Minus Signs)
- Each minus (`-`) represents **1 tick of silence**
- Multiple minus signs create longer rests
- Minus signs are standalone tokens (separated by spaces)

**Rest Examples**:
- `-` - 1 tick of silence (1 sixteenth rest)
- `---` - 3 ticks of silence (1 eighth rest)
- `------` - 6 ticks of silence (1 quarter rest)

## Timing Resolution

- **Base Resolution**: 6 ticks per quarter note
- **1 tick = 1/6 quarter note = 1 sixteenth note**
- **At 120 BPM**: 1 tick ≈ 83ms, 1 quarter note = 500ms

## Syntax Rules

1. **Tokens are separated by spaces**
2. **Notes and rests are individual tokens**
3. **Dots attach directly to notes** (no spaces)
4. **Minus signs can be grouped** for longer rests
5. **Case insensitive** for note names

## Musical Examples

### Simple Melodies
```
C4...... D4...... E4...... F4......
```
*Four quarter notes: C-D-E-F*

### Rhythm Patterns
```
C4... C4... C4...... C4......
```
*Two eighth notes, two quarter notes*

### With Rests
```
C4...... --- D4...... --- E4......
```
*Quarter note, eighth rest, quarter note, eighth rest, quarter note*

### Complex Rhythm
```
C4. D4. E4... F4. - G4......
```
*Two sixteenths, one eighth, one sixteenth, sixteenth rest, one quarter*

### Chromatic Scale
```
C4. C#4. D4. D#4. E4. F4. F#4. G4.
```
*Eight sixteenth notes ascending chromatically*

## AI Generation Guidelines

### When generating music notation:

1. **Use musically logical note sequences**
   - Prefer stepwise motion or small intervals
   - Consider key signatures and scales
   - Use common chord progressions

2. **Create rhythmic variety**
   - Mix different note durations
   - Use rests for phrasing and breathing
   - Consider meter and beat emphasis

3. **Follow notation rules strictly**
   - Always separate tokens with single spaces
   - Attach dots directly to notes
   - Use proper note naming (C4, not C-4 or C 4)

4. **Common duration patterns**:
   - **Sixteenth notes**: `C4. D4. E4. F4.`
   - **Eighth notes**: `C4... D4... E4...`
   - **Quarter notes**: `C4...... D4...... E4......`
   - **Mixed rhythm**: `C4...... D4... E4... F4......`

5. **Phrase structure**
   - Use rests to separate musical phrases
   - Consider 4, 8, or 16 beat patterns
   - End phrases with longer notes or rests

## Validation Rules

A valid CLAUDE notation string must:
- Contain only valid note names (A-G with optional #/b and octave 0-9)
- Use only dots (.) and minus signs (-) for timing
- Separate all tokens with single spaces
- Have dots immediately following note names
- Use minus signs as standalone tokens

## Examples by Musical Style

### Pop/Rock Rhythm
```
C4...... G4...... Am4...... F4......
```

### Classical Melody
```
C4... D4... E4...... F4... E4... D4...... C4......
```

### Jazz Syncopation
```
C4... - E4. G4... - C5. - G4... E4......
```

### Electronic Pattern
```
C4. - C4. - C4... C4. - C4......
```

## Usage in AI Systems

AI agents should:
1. **Parse** the notation by splitting on spaces and analyzing each token
2. **Validate** each token against the syntax rules
3. **Generate** new sequences following musical principles
4. **Convert** to/from other musical formats (MIDI, sheet music, etc.)
5. **Understand** the rhythmic and melodic content for analysis

This notation format provides a simple, human-readable, and AI-friendly way to represent musical sequences with precise timing information.