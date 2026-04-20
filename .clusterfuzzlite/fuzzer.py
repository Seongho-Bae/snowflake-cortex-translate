import sys
import atheris

def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    try:
        text = fdp.ConsumeString(100)
        _ = text.encode("utf-8")
    except UnicodeEncodeError:
        return

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
