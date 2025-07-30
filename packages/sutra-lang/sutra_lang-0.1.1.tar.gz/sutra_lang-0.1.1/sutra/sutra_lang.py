# sutra_lang.py
import sys

hindi_to_python = {
    "chapo": "print",
    "poochho": "input",
    "ager": "if",
    "nahi_to": "else",
    "jabtak": "while",
    "ke_liye": "for",
    "kaam": "def",
    "varg": "class",
    "lautao": "return",
    "sach": "True",
    "jhooth": "False",
    "tiyaag_kar": "exit",
    "sanganak": "os",
    "ganit": "math"
}

def translate_line(line):
    for hindi, py in hindi_to_python.items():
        line = line.replace(hindi, py)
    return line

def run_sutra(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code_lines = f.readlines()

        python_code = ""
        for line in code_lines:
            python_code += translate_line(line)

        exec(python_code, globals())

    except KeyboardInterrupt:
        print("\n⛔ आपने प्रोग्राम को रोक दिया (Ctrl+C दबाया गया)")
    except Exception as e:
        print("⚠️ त्रुटि:", e)


def main():
    if len(sys.argv) < 2:
        print("कृपया कोई .su फ़ाइल दें।")
    else:
        run_sutra(sys.argv[1])

if __name__ == "__main__":
    main()

