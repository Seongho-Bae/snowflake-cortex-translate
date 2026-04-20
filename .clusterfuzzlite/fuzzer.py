import sys
import atheris

with atheris.instrument_imports():
    from cortex_translate_service.domain.models import TranslateRequest, TranslateResponse

def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    try:
        req = TranslateRequest(
            text=fdp.ConsumeString(100),
            source_language=fdp.ConsumeString(10),
            target_language=fdp.ConsumeString(10)
        )
    except Exception:
        pass

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
