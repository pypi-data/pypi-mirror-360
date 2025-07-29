import time
import sys
import math
from datetime import datetime
import statistics
import string
import shutil 

# 1. consoleOutput
def consoleOutput(color: str, text: str, size: int = 12, bigTextFormat: bool = False,
                  align: str = "left", bold: bool = False, underline: bool = False,
                  width: int = 80, logFile: str = None):
    color_codes = {
        'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m',
        'yellow': '\033[33m', 'blue': '\033[34m', 'magenta': '\033[35m',
        'cyan': '\033[36m', 'white': '\033[37m', 'reset': '\033[0m'
    }
    bold_code = '\033[1m' if bold else ''
    underline_code = '\033[4m' if underline else ''

    if bigTextFormat:
        text = text.upper()
        border = '*' * (len(text) + 4)
        text = f"{border}\n* {text} *\n{border}"

    lines = text.split('\n')
    aligned_lines = []
    for line in lines:
        if align == "center":
            aligned_lines.append(line.center(width))
        elif align == "right":
            aligned_lines.append(line.rjust(width))
        else:
            aligned_lines.append(line.ljust(width))

    formatted_text = "\n".join(aligned_lines)
    start_codes = f"{color_codes.get(color.lower(), '')}{bold_code}{underline_code}"
    end_code = color_codes['reset']
    output = f"{start_codes}{formatted_text}{end_code}"
    print(output)

    if logFile:
        with open(logFile, "a", encoding="utf-8") as f:
            f.write(text + "\n")

# 2. styledInput
def styledInput(prompt: str, color: str = "white", align: str = "left",
                bordered: bool = False, width: int = 80, default: str = "") -> str:
    color_codes = {
        'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m',
        'yellow': '\033[33m', 'blue': '\033[34m', 'magenta': '\033[35m',
        'cyan': '\033[36m', 'white': '\033[37m', 'reset': '\033[0m'
    }

    if align == "center":
        prompt_line = prompt.center(width)
    elif align == "right":
        prompt_line = prompt.rjust(width)
    else:
        prompt_line = prompt.ljust(width)

    if bordered:
        border = "-" * len(prompt_line)
        prompt_line = f"{border}\n{prompt_line}\n{border}"

    styled_prompt = f"{color_codes.get(color.lower(), '')}{prompt_line}{color_codes['reset']}"
    print(styled_prompt)

    user_input = input("> ").strip()
    return user_input if user_input else default

# 3. progressBar
def progressBar(total: int = 20, delay: float = 0.1, message: str = "Loading"):
    for i in range(total + 1):
        percent = int((i / total) * 100)
        bar = '#' * i + '-' * (total - i)
        sys.stdout.write(f"\r{message}: [{bar}] {percent}%")
        sys.stdout.flush()
        time.sleep(delay)
    print("\nDone.")

# 4. menuPrompt
def menuPrompt(options: list, title: str = "Select an option") -> int:
    print(f"\n{title}\n" + "-" * len(title))
    for i, opt in enumerate(options, start=1):
        print(f"{i}. {opt}")
    while True:
        choice = input("Enter number: ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(options):
                return index
        print("Invalid input. Try again.")

# 5. timestampedLog
def timestampedLog(message: str, logFile: str = "log.txt"):
    now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(logFile, "a", encoding="utf-8") as f:
        f.write(f"{now} {message}\n")

# 6. mathEval
def mathEval(expression: str) -> float:
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    try:
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return result
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

# 7. tableDisplay
def tableDisplay(data: dict, title: str = "Data Table", width: int = 30):
    border = "-" * (width * 2 + 5)
    print(f"\n{title.center(len(border))}\n{border}")
    for key, value in data.items():
        print(f"| {str(key).ljust(width)} | {str(value).ljust(width)} |")
    print(border)

# 8. confirmPrompt
def confirmPrompt(message: str = "Are you sure? (y/n)") -> bool:
    while True:
        response = input(f"{message} ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter y or n.")

# 9. countdown
def countdown(seconds: int):
    while seconds > 0:
        sys.stdout.write(f"\rTime remaining: {seconds} seconds")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
    print("\nTime's up!")

# 10. divider
def divider(char: str = "-", width: int = 80):
    print(char * width)

# 11. listToTable
def listToTable(data: list, columns: int = 2, width: int = 20):
    print("-" * (columns * (width + 3)))
    for i in range(0, len(data), columns):
        row = data[i:i+columns]
        print(" | ".join(str(cell).ljust(width) for cell in row))
    print("-" * (columns * (width + 3)))

# 12. yesNoInput
def yesNoInput(prompt: str = "Continue? (yes/no)") -> bool:
    response = input(prompt + " ").strip().lower()
    return response in ['yes', 'y']

# 13. boxText
def boxText(text: str):
    border = "+" + "-" * (len(text) + 2) + "+"
    print(border)
    print(f"| {text} |")
    print(border)

# 14. sectionHeader
def sectionHeader(title: str, width: int = 80):
    title = f" {title} "
    border = "=" * width
    mid = (width - len(title)) // 2
    print(border)
    print(" " * mid + title)
    print(border)

# 15. inputNumber
def inputNumber(prompt: str = "Enter a number: ", min_val=None, max_val=None) -> int:
    while True:
        try:
            num = int(input(prompt))
            if (min_val is not None and num < min_val) or (max_val is not None and num > max_val):
                print(f"Please enter a number between {min_val} and {max_val}.")
                continue
            return num
        except ValueError:
            print("That's not a valid number.")



# 16. clearScreen
def clearScreen():
    """Clears the terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

# 17. waitForEnter
def waitForEnter(prompt: str = "Press Enter to continue..."):
    """Waits for the user to press Enter."""
    input(prompt)

# 18. inputFloat
def inputFloat(prompt: str = "Enter a number: ", min_val=None, max_val=None) -> float:
    """Gets a float input with optional range validation."""
    while True:
        try:
            num = float(input(prompt))
            if (min_val is not None and num < min_val) or (max_val is not None and num > max_val):
                print(f"Enter a number between {min_val} and {max_val}.")
                continue
            return num
        except ValueError:
            print("That's not a valid number.")

# 19. charSpinner
def charSpinner(duration: float = 2.0, message: str = "Working..."):
    """Displays a spinning character animation."""
    spinner = ['|', '/', '-', '\\']
    t_end = time.time() + duration
    i = 0
    while time.time() < t_end:
        sys.stdout.write(f"\r{message} {spinner[i % 4]}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    print("\rDone!           ")

# 20. asciiArt
def asciiArt(text: str):
    """Prints stylized ASCII text using pyfiglet (requires install)."""
    try:
        from pyfiglet import figlet_format
        print(figlet_format(text))
    except ImportError:
        print("Install pyfiglet to use this feature: pip install pyfiglet")

# 21. printBoxList
def printBoxList(items: list):
    """Prints each item in a box."""
    for item in items:
        length = len(item) + 4
        print("+" + "-" * (length - 2) + "+")
        print(f"| {item} |")
        print("+" + "-" * (length - 2) + "+")

# 22. countdownTimer
def countdownTimer(minutes: int = 1):
    """Counts down from given minutes."""
    total_seconds = minutes * 60
    for remaining in range(total_seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        timer = f"{mins:02}:{secs:02}"
        sys.stdout.write(f"\rTimer: {timer}")
        sys.stdout.flush()
        time.sleep(1)
    print("\nTime's up!")

# 23. multiSelectPrompt
def multiSelectPrompt(options: list, prompt: str = "Select options (comma-separated):") -> list:
    """Prompts for multiple selections from a list."""
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    selection = input("Your choices: ")
    indices = [int(i.strip()) - 1 for i in selection.split(',') if i.strip().isdigit()]
    return [options[i] for i in indices if 0 <= i < len(options)]

# 24. drawProgressCircle
def drawProgressCircle(percent: float):
    """Simulates a circular progress (visual approximation)."""
    filled = int(percent // 10)
    bar = "●" * filled + "○" * (10 - filled)
    print(f"[{bar}] {percent:.0f}%")

# 25. truncateText
def truncateText(text: str, max_length: int = 40) -> str:
    """Truncates text with ellipsis if it exceeds max_length."""
    return text if len(text) <= max_length else text[:max_length - 3] + "..."



# 26. loadingDots
def loadingDots(duration: float = 3.0, message: str = "Loading"):
    """Prints a loading message with dots."""
    end = time.time() + duration
    while time.time() < end:
        for dots in range(4):
            sys.stdout.write(f"\r{message}{'.' * dots}{' ' * (3 - dots)}")
            sys.stdout.flush()
            time.sleep(0.5)
    print("\rDone!        ")

# 27. inputChoice
def inputChoice(prompt: str, choices: list) -> str:
    """Prompts the user until they enter one of the allowed choices."""
    choice_str = "/".join(choices)
    while True:
        response = input(f"{prompt} ({choice_str}): ").strip().lower()
        if response in choices:
            return response
        print(f"Invalid input. Please enter one of: {choice_str}")

# 28. printBanner
def printBanner(text: str, char: str = "#", padding: int = 2):
    """Prints a banner with the given character."""
    width = len(text) + padding * 2 + 2
    print(char * width)
    print(char + " " * padding + text + " " * padding + char)
    print(char * width)

# 29. formatBytes
def formatBytes(size: int) -> str:
    """Formats bytes to human-readable form."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

# 30. printError
def printError(message: str):
    """Prints an error message in red."""
    print(f"\033[31m[ERROR]\033[0m {message}")

# 31. printSuccess
def printSuccess(message: str):
    """Prints a success message in green."""
    print(f"\033[32m[SUCCESS]\033[0m {message}")

# 32. formatTime
def formatTime(seconds: int) -> str:
    """Formats time in seconds to H:M:S."""
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

# 33. waitWithMessage
def waitWithMessage(seconds: int = 3, message: str = "Waiting"):
    """Waits with a countdown message."""
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\r{message}... {i}s remaining")
        sys.stdout.flush()
        time.sleep(1)
    print("\nDone.")

# 34. logError
def logError(message: str, logFile: str = "error.log"):
    """Logs error messages to a file with a timestamp."""
    timestampedLog(f"[ERROR] {message}", logFile)

# 35. printWrapped
def printWrapped(text: str, width: int = 80):
    """Wraps and prints long text to fit the terminal width."""
    import textwrap
    for line in textwrap.wrap(text, width):
        print(line)







# 36. printInfo
def printInfo(message: str):
    """Prints an informational message in cyan."""
    print(f"\033[36m[INFO]\033[0m {message}")

# 37. inputPassword
def inputPassword(prompt: str = "Enter password: ") -> str:
    """Prompts user for password input without echoing."""
    import getpass
    return getpass.getpass(prompt)

# 38. typewriterPrint
def typewriterPrint(text: str, delay: float = 0.05):
    """Prints text like a typewriter."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# 39. statusBar
def statusBar(current: int, total: int, label: str = "Progress"):
    """Prints a simple status bar."""
    percent = int((current / total) * 100)
    bar = '=' * (percent // 5) + ' ' * (20 - percent // 5)
    sys.stdout.write(f"\r{label}: [{bar}] {percent}%")
    sys.stdout.flush()
    if current == total:
        print()

# 40. ordinal
def ordinal(n: int) -> str:
    """Converts number to its ordinal representation."""
    return f"{n}{'tsnrhtdd'[(n // 10 % 10 != 1)*(n % 10 < 4)*n % 10::4]}"

# 41. timeDelta
def timeDelta(start: datetime, end: datetime = None) -> str:
    """Returns human-readable time delta from start to end."""
    if end is None:
        end = datetime.now()
    delta = end - start
    return str(delta)

# 42. timeStamp
def timeStamp() -> str:
    """Returns current timestamp."""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

# 43. clipCopy
def clipCopy(text: str):
    """Copies text to the system clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        printSuccess("Copied to clipboard.")
    except ImportError:
        printError("Install pyperclip to use this feature.")

# 44. clipPaste
def clipPaste() -> str:
    """Pastes text from the system clipboard."""
    try:
        import pyperclip
        return pyperclip.paste()
    except ImportError:
        printError("Install pyperclip to use this feature.")
        return ""

# 45. printAlert
def printAlert(message: str):
    """Prints a yellow alert message."""
    print(f"\033[33m[ALERT]\033[0m {message}")

# 46. printTitle
def printTitle(text: str, char: str = "=", width: int = 80):
    """Prints a title with borders."""
    print(char * width)
    print(text.center(width))
    print(char * width)

# 47. reverseText
def reverseText(text: str) -> str:
    """Reverses the input string."""
    return text[::-1]

# 48. repeatText
def repeatText(text: str, times: int = 2) -> str:
    """Repeats a string n times."""
    return text * times

# 49. stringToHex
def stringToHex(text: str) -> str:
    """Converts string to its hexadecimal representation."""
    return text.encode().hex()

# 50. hexToString
def hexToString(hex_str: str) -> str:
    """Converts hex back to a string."""
    try:
        return bytes.fromhex(hex_str).decode()
    except Exception:
        raise ValueError("Invalid hex string")





# 36. printInfo
def printInfo(message: str):
    """Prints an informational message in cyan."""
    print(f"\033[36m[INFO]\033[0m {message}")

# 37. inputPassword
def inputPassword(prompt: str = "Enter password: ") -> str:
    """Prompts user for password input without echoing."""
    import getpass
    return getpass.getpass(prompt)

# 38. typewriterPrint
def typewriterPrint(text: str, delay: float = 0.05):
    """Prints text like a typewriter."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# 39. statusBar
def statusBar(current: int, total: int, label: str = "Progress"):
    """Prints a simple status bar."""
    percent = int((current / total) * 100)
    bar = '=' * (percent // 5) + ' ' * (20 - percent // 5)
    sys.stdout.write(f"\r{label}: [{bar}] {percent}%")
    sys.stdout.flush()
    if current == total:
        print()

# 40. ordinal
def ordinal(n: int) -> str:
    """Converts number to its ordinal representation."""
    return f"{n}{'tsnrhtdd'[(n // 10 % 10 != 1)*(n % 10 < 4)*n % 10::4]}"

# 41. timeDelta
def timeDelta(start: datetime, end: datetime = None) -> str:
    """Returns human-readable time delta from start to end."""
    if end is None:
        end = datetime.now()
    delta = end - start
    return str(delta)

# 42. timeStamp
def timeStamp() -> str:
    """Returns current timestamp."""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

# 43. clipCopy
def clipCopy(text: str):
    """Copies text to the system clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        printSuccess("Copied to clipboard.")
    except ImportError:
        printError("Install pyperclip to use this feature.")

# 44. clipPaste
def clipPaste() -> str:
    """Pastes text from the system clipboard."""
    try:
        import pyperclip
        return pyperclip.paste()
    except ImportError:
        printError("Install pyperclip to use this feature.")
        return ""

# 45. printAlert
def printAlert(message: str):
    """Prints a yellow alert message."""
    print(f"\033[33m[ALERT]\033[0m {message}")

# 46. printTitle
def printTitle(text: str, char: str = "=", width: int = 80):
    """Prints a title with borders."""
    print(char * width)
    print(text.center(width))
    print(char * width)

# 47. reverseText
def reverseText(text: str) -> str:
    """Reverses the input string."""
    return text[::-1]

# 48. repeatText
def repeatText(text: str, times: int = 2) -> str:
    """Repeats a string n times."""
    return text * times

# 49. stringToHex
def stringToHex(text: str) -> str:
    """Converts string to its hexadecimal representation."""
    return text.encode().hex()

# 50. hexToString
def hexToString(hex_str: str) -> str:
    """Converts hex back to a string."""
    try:
        return bytes.fromhex(hex_str).decode()
    except Exception:
        raise ValueError("Invalid hex string")
