"""Genera las imagenes de contratos de prueba a partir de texto (requiere Pillow).

Uso: python data/test_contracts/generate_test_contracts.py
"""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE_SIZE = (1000, 1400)
MARGIN = 60
WRAP_WIDTH = 78
LINE_HEIGHT = 24
PARAGRAPH_GAP = 18

TITLE_FONT = ImageFont.load_default(size=26)
HEADER_FONT = ImageFont.load_default(size=20)
BODY_FONT = ImageFont.load_default(size=18)

OUTPUT_DIR = Path(__file__).parent


def render_contract(title: str, intro: str | None, clauses: list[tuple[str, str]], path: Path) -> None:
    img = Image.new("RGB", PAGE_SIZE, color="white")
    draw = ImageDraw.Draw(img)

    bbox = draw.textbbox((0, 0), title, font=TITLE_FONT)
    title_width = bbox[2] - bbox[0]
    y = MARGIN
    draw.text(((PAGE_SIZE[0] - title_width) // 2, y), title, fill="black", font=TITLE_FONT)
    y += 55

    if intro:
        wrapped_intro = textwrap.fill(intro, width=WRAP_WIDTH)
        draw.multiline_text((MARGIN, y), wrapped_intro, fill="black", font=BODY_FONT, spacing=6)
        y += (wrapped_intro.count("\n") + 1) * LINE_HEIGHT + PARAGRAPH_GAP + 10

    for header, body in clauses:
        draw.text((MARGIN, y), header, fill="black", font=HEADER_FONT)
        y += 28
        wrapped_body = textwrap.fill(body, width=WRAP_WIDTH)
        draw.multiline_text((MARGIN, y), wrapped_body, fill="black", font=BODY_FONT, spacing=6)
        y += (wrapped_body.count("\n") + 1) * LINE_HEIGHT + PARAGRAPH_GAP

    img.save(path)


# --- Par 1: cambios simples (contrato de servicios) ---

par1_dir = OUTPUT_DIR / "par1_servicios_simple"
par1_dir.mkdir(exist_ok=True)

render_contract(
    title="CONTRATO DE PRESTACION DE SERVICIOS",
    intro=None,
    clauses=[
        (
            "PRIMERA. PARTES.",
            "El presente contrato de prestacion de servicios se celebra entre "
            "LegalMove S.A., en adelante EL CLIENTE, y Consultora Andina SRL, en "
            "adelante EL PRESTADOR.",
        ),
        (
            "SEGUNDA. OBJETO.",
            "EL PRESTADOR se compromete a brindar servicios de consultoria en "
            "materia de cumplimiento normativo a EL CLIENTE, de acuerdo a los "
            "terminos aqui establecidos.",
        ),
        (
            "TERCERA. MONTO.",
            "EL CLIENTE abonara a EL PRESTADOR la suma mensual de USD 1.500 (mil "
            "quinientos dolares estadounidenses), pagaderos dentro de los primeros "
            "cinco dias habiles de cada mes.",
        ),
        (
            "CUARTA. VIGENCIA.",
            "El presente contrato entrara en vigencia a partir de su firma y "
            "mantendra su validez hasta el dia 30 de junio de 2026, fecha de "
            "vencimiento del presente acuerdo.",
        ),
        (
            "QUINTA. CONFIDENCIALIDAD.",
            "Ambas partes se comprometen a mantener confidencialidad respecto de "
            "toda informacion intercambiada en el marco de este contrato.",
        ),
        (
            "SEXTA. JURISDICCION.",
            "Para cualquier controversia derivada del presente contrato, las "
            "partes se someten a la jurisdiccion de los tribunales ordinarios de "
            "la Ciudad Autonoma de Buenos Aires.",
        ),
    ],
    path=par1_dir / "original.png",
)

render_contract(
    title="ENMIENDA N.1 AL CONTRATO DE PRESTACION DE SERVICIOS",
    intro=(
        "Las partes acuerdan modificar el contrato de prestacion de servicios "
        "suscripto oportunamente, unicamente en los terminos que se detallan a "
        "continuacion. El resto de las clausulas del contrato original mantienen "
        "plena vigencia."
    ),
    clauses=[
        (
            "TERCERA. MONTO (MODIFICADA).",
            "EL CLIENTE abonara a EL PRESTADOR la suma mensual de USD 1.800 (mil "
            "ochocientos dolares estadounidenses), pagaderos dentro de los "
            "primeros cinco dias habiles de cada mes.",
        ),
        (
            "CUARTA. VIGENCIA (MODIFICADA).",
            "El presente contrato mantendra su validez hasta el dia 31 de "
            "diciembre de 2026, fecha de vencimiento del presente acuerdo.",
        ),
    ],
    path=par1_dir / "amendment.png",
)

# --- Par 2: cambios complejos (contrato de confidencialidad) ---

par2_dir = OUTPUT_DIR / "par2_confidencialidad_compleja"
par2_dir.mkdir(exist_ok=True)

render_contract(
    title="CONTRATO DE CONFIDENCIALIDAD (NDA)",
    intro=None,
    clauses=[
        (
            "PRIMERA. PARTES.",
            "El presente acuerdo de confidencialidad se celebra entre Grupo "
            "Norte S.A., en adelante LA EMPRESA, y Tecnologia del Sur SRL, en "
            "adelante EL RECEPTOR.",
        ),
        (
            "SEGUNDA. OBJETO.",
            "LA EMPRESA compartira con EL RECEPTOR informacion confidencial "
            "relativa a sus procesos internos, con el unico fin de evaluar una "
            "eventual relacion comercial entre las partes.",
        ),
        (
            "TERCERA. ALCANCE TERRITORIAL.",
            "Las obligaciones de confidencialidad establecidas en el presente "
            "contrato seran aplicables unicamente dentro del territorio de la "
            "Republica Argentina.",
        ),
        (
            "CUARTA. RESTRICCION DE USO.",
            "EL RECEPTOR no podra utilizar la informacion confidencial para "
            "fines distintos a los establecidos en la Clausula Segunda, ni podra "
            "replicarla en ningun soporte fisico o digital sin autorizacion "
            "previa y por escrito de LA EMPRESA.",
        ),
        (
            "QUINTA. VIGENCIA.",
            "El presente acuerdo tendra una vigencia de veinticuatro (24) meses "
            "contados desde la fecha de su firma.",
        ),
        (
            "SEXTA. JURISDICCION.",
            "Ante cualquier controversia, las partes se someten a la "
            "jurisdiccion de los tribunales ordinarios de la Ciudad Autonoma de "
            "Buenos Aires.",
        ),
    ],
    path=par2_dir / "original.png",
)

render_contract(
    title="ENMIENDA N.1 AL CONTRATO DE CONFIDENCIALIDAD",
    intro=(
        "Las partes acuerdan modificar el contrato de confidencialidad "
        "suscripto oportunamente, en los terminos que se detallan a "
        "continuacion. El resto de las clausulas del contrato original "
        "mantienen plena vigencia, salvo lo indicado expresamente en el "
        "presente instrumento."
    ),
    clauses=[
        (
            "TERCERA. ALCANCE TERRITORIAL (MODIFICADA).",
            "Las obligaciones de confidencialidad establecidas en el presente "
            "contrato seran aplicables dentro del territorio de la Republica "
            "Argentina y de la Republica Oriental del Uruguay.",
        ),
        (
            "CUARTA. RESTRICCION DE USO (ELIMINADA).",
            "Las partes acuerdan eliminar en su totalidad la Clausula Cuarta "
            "del contrato original, referida a la restriccion de uso de la "
            "informacion confidencial, la cual queda sin efecto a partir de la "
            "firma de la presente enmienda.",
        ),
        (
            "SEPTIMA. PROPIEDAD INTELECTUAL (NUEVA).",
            "Toda informacion, desarrollo o material generado por EL RECEPTOR "
            "a partir del acceso a la informacion confidencial de LA EMPRESA "
            "sera propiedad exclusiva de LA EMPRESA, quien podra disponer de "
            "ella libremente.",
        ),
    ],
    path=par2_dir / "amendment.png",
)

print("Contratos de prueba generados en", OUTPUT_DIR)
