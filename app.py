from fastapi import FastAPI, Query, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import segno
try:
    import treepoem
    HAS_TREEPOEM = True
except Exception:
    HAS_TREEPOEM = False


app = FastAPI()
VERSION = "1.0.0"


BAR_KINDS = {"code128", "code39", "ean13", "upca", "itf"}
def barcode_class(kind: str):
    m = {
        "code128": barcode.get_barcode_class("code128"),
        "code39":  barcode.get_barcode_class("code39"),
        "ean13":   barcode.get_barcode_class("ean13"),
        "upca":    barcode.get_barcode_class("upc"),
        "itf":     barcode.get_barcode_class("itf"),
    }
    return m[kind]

@app.get("/version")
def version():
    return {"version": VERSION}

@app.get("/code")
def make_code(
    data: str = Query(..., min_length=1),
    type: str = Query("qr", pattern="qr|code128|code39|ean13|upca|itf|datamatrix"),
    fmt: str = Query("png", pattern="png|svg"),
    txt: bool = True,
    micro: bool = False,
    scale: int = 8,     # QR pixel size / barcode module size factor
    border: int = 2     # quiet zone (modules)
):
    # QR path
    if type == "qr":
        q = segno.make(data, error="M", micro=micro)
        buf = BytesIO()
        if fmt == "svg":
            q.save(buf, kind="svg", scale=scale, border=border)
            return Response(buf.getvalue(), media_type="image/svg+xml")
        else:
            q.save(buf, kind="png", scale=scale, border=border)
            return Response(buf.getvalue(), media_type="image/png")

    # DataMatrix path (2D)
    if type == "datamatrix":
        if not HAS_TREEPOEM:
            raise HTTPException(501, "DataMatrix requires 'treepoem' and Ghostscript installed")
        if fmt == "svg":
            raise HTTPException(406, "DataMatrix currently available as PNG only")
        img = treepoem.generate_barcode(barcode_type="datamatrix", data=data)
        out = BytesIO()
        img.save(out, format="PNG")
        return Response(out.getvalue(), media_type="image/png")

    # Barcode path
    if type in BAR_KINDS:
        if type in {"ean13", "upca"} and not data.isdigit():
            raise HTTPException(400, f"{type.upper()} requires digits only")
        writer_opts = {
            "module_width": max(0.2, 0.2 * (scale / 8)),  # mm-ish per module
            "module_height": 15 * (scale / 8),
            "quiet_zone": border,
            "write_text": txt,
        }
        cls = barcode_class(type)
        buf = BytesIO()
        if fmt == "svg":
            cls(data).write(buf, options=writer_opts)  # default writer = SVG
            return Response(buf.getvalue(), media_type="image/svg+xml")
        else:
            cls(data, writer=ImageWriter()).write(buf, options=writer_opts)
            return Response(buf.getvalue(), media_type="image/png")

    raise HTTPException(400, "Unsupported type")

app.mount("/", StaticFiles(directory="src", html=True), name="static")