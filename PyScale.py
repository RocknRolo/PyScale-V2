# PyScale-V2. A Python script that calculates musical scales and displays them on a guitar fretboard that is 
# printed to the shell.
# Author: Roel Kemp (github.com/RocknRolo)

# "sys" is imported so the user can supply command line arguments.
import sys

# A simple error handling function that shows a message and terminates the script.
def invalid_input():
    print("Invalid input")
    exit(1)

# Default values are defined in case the user does not supply them.
Root = "C"
Mode = 1 # 1 = Ionian, 2 = Dorian, 3 = Phrygian, 4 = Lydian, 5 = Mixolydian, 6 = Aeolian, 7 = Locrian

# If one value is supplied, only "Root" will be redefined.
if len(sys.argv) > 1:
    Root = sys.argv[1]

# If two values are suppied, both "Root" and "Mode" are redefined. If Mode is between 1 and 7 an int is parsed and 
# assigned to Mode.
if len(sys.argv) > 2:
    if sys.argv[2] in "1234567":
        Mode = int(sys.argv[2])
    else: invalid_input()

# A function to check if the Root string is supplied in the right format. The first char should be a capital between A 
# and G. If there are more chars they should all be either "b" or "#". Text[-1] is checked so the expression also works
# for len(Text) = 1. The maximum length is limited to 2 so the tones that need to be printed are max 3 characters long.
def check_text(text):
    if len(text) < 1 or len(text) > 2 or text[0] not in "CDEFGAB":
        return False
    if text[-1] == "b" or text[-1] == "#":
        for chi in range(1, len(text)):
            if text[1] != text[chi]:
                return False
    return True

# The above function is ran. If it returns false, invalid_input() is ran.
if not check_text(Root):
    invalid_input()

########################################################################################################################

# Blueprint for a Tone object with 2 attributes. "natural" is a single char between A and G. 
# "flat_sharp" is negative for number of flats (b) and positive for number of sharps (#).
# The class has methods so the input and output can be a string. I want input filtering to
# be done only once at the start of the script, so I left it out of the Tone class.
class Tone:
    def __init__(self, natural, flat_sharp):
        self.natural = natural
        self.flat_sharp = flat_sharp

    @classmethod
    def from_text(cls, text):
        natural = text[0]
        flat_sharp = len(text) - 1 if (len(text) > 1 and text[1] == "#") else -(len(text) - 1)
        return cls(natural, flat_sharp)

    def __str__(self):
        natural = self.natural
        flat_sharp = self.flat_sharp
        flat_sharp_str = flat_sharp * "#" if (flat_sharp > 0) else abs(flat_sharp) * "b"
        return natural + flat_sharp_str

########################################################################################################################

# These variables are used to calculate the next tone in a scale.
HALVES = "C D EF G A B"
WHOLES = HALVES.replace(" ", "")
Steps = 2, 2, 1, 2, 2, 2, 1

# The Mode variable is used to change the order of the whole and half tone steps.
Steps = Steps[Mode - 1:] + Steps[0:Mode - 1]

# The first Tone is defined from the filtered user input and added to a new list of Tone objects, called Scale.
PrevTone = Tone.from_text(Root)
Scale = [PrevTone]

# None objects are added to the Scale list, to represent the empty frets.
for i in range(Steps[0] - 1):
    Scale.append(None)

# This loop runs one time less than the size "Steps". The first element is skipped as the first tone has already been 
# added to Scale. For clarity the computations are split out into seperate variables. The name of the current tone to be
# added is always one further in the cycle of "WHOLES". The distance between the previous and the current position of 
# "natural" in "HALVES" is compared to what this distance should be according to "Steps". The difference between these
# two distances added to the previous flat_sharp value is the new flat_sharp value.
for i in range(1, len(Steps)):
    PrevWholeIndex = WHOLES.find(PrevTone.natural)
    CurrWholeIndex = (PrevWholeIndex + 1) % len(WHOLES)
    CurrWholeNatural = WHOLES[CurrWholeIndex]

    PrevHalveIndex = HALVES.find(PrevTone.natural)
    CurrHalveIndex = (PrevHalveIndex + Steps[i - 1]) % len(HALVES)

    FlatSharp = PrevTone.flat_sharp

    if HALVES[CurrHalveIndex] != CurrWholeNatural:
        for j in range(len(HALVES)):
            if HALVES[(CurrHalveIndex + j) % len(HALVES)] == CurrWholeNatural:
                FlatSharp -= j
                break
            if HALVES[(CurrHalveIndex - j) % len(HALVES)] == CurrWholeNatural:
                FlatSharp += j
                break

    PrevTone = Tone(CurrWholeNatural, FlatSharp)
    Scale.append(PrevTone) 
    # None objects are added to the Scale list, to represent the empty frets.
    for i in range(Steps[i] - 1):
        Scale.append(None)

########################################################################################################################

# This function filters out the None objects and formats the remaining Tone objects to a space-seperated string.
def scale_to_str():
    ResultStr = ""
    for i in range(len(Scale)):
        if Scale[i] is not None:
            ResultStr += Scale[i].__str__()
            ResultStr += " " if i < len(Scale) - 1 else ""
    return ResultStr

scale_str = scale_to_str()
scale_str_list = scale_str.split(" ")

interval_numbers = "  "
for i in range(len(scale_str_list)):
    interval_numbers += str(i + 1)
    if i < len(scale_str_list) - 1:
        interval_numbers += (" " * len(scale_str_list[i]))

print("\n" + interval_numbers + "\n  " + scale_str + "\n")

# Tuning is defined in the order the strings are drawn. This corresponds to the common way of numbering guitar strings.
# The thinnest string is first, then the second thinnest, etc.
Tuning = ["E", "B", "G", "D", "A", "E"]
OCT_FRET = 12

# A guitar string str will be drawn for each Tone in tuning.
for fret0str in Tuning:
    fret0tone = Tone.from_text(fret0str)
    index = 0
    for i in range(len(Scale)):
        if Scale[i] is not None and Scale[i].natural is fret0tone.natural:
            index = i - Scale[i].flat_sharp

    # The scale is reordered based on the index calculated above.
    semitones = Scale[index:] + Scale[0:index]

    # If the tone on the open string is not in the scale it should be in parentheses.
    if semitones[0] is not None:
        tone_str = semitones[0].__str__()
    else:
        tone_str = fret0str

    # The number of spaces around the first Tone on the string depends on the str len of the first Tone.
    pre0str = ""
    if len(tone_str) == 1:
        pre0str += " "
    pre0str += " " if semitones[0] is not None else "("
    post0str = (" " if semitones[0] is not None else ")") + "|"

    if len(tone_str) == 2:
        pre0str = " " + pre0str
        post0str = post0str[1:]

    if len(tone_str) > 2:
        post0str = "|"

    # The guitar string str is composed in such a way that it's length is always the same.
    string_str = pre0str + tone_str + post0str

    # The loop that composes the rest of the guitar string runs twice + 1 so two octaves per string + fret 24 
    # are displayed. The "frets" of the second octave are drawn smaller to mimic a real guitar.
    # A more realistic text representation of a guitar was not practical.
    for i in range(1, len(semitones) * 2 + 1):
        if semitones[i % OCT_FRET] is None:
            tone_str = "-"
        else: 
            tone_str = semitones[i % OCT_FRET].__str__()
        padding = ""
        if len(tone_str) == 1: 
            padding += "-"
        if i < OCT_FRET:
            padding += "-"
        if len(tone_str) == 2:
            tone_str = "-" + tone_str

        string_str += padding + tone_str + padding
        string_str += "|"
    print(string_str)

fret_numbers = "                   3           5           7           9               " + \
"1 2         1 5     1 7     1 9         2 2     2 4"

print(fret_numbers)

# TODO:
# Add option for different tunings that checks if the tuning tones are max str length 2.
# Add option to display interval numbers instead of tones.
# Add option for harmonic and melodic minor scales and their modes.
# Add option for pentatonic scales.
# Add "Help".
# Fix bug extra interval number is added when mode is not 1.
