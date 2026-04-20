import sys
import atheris

def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    try:
        text = fdp.ConsumeString(100)
        _ = text.encode("utf-8")
    except UnicodeEncodeError:
        pass
    except Exception as e:
        # Catch all other exceptions explicitly rather than silently ignoring
        sys.stderr.write(f"Unexpected error: {e}\n")

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
