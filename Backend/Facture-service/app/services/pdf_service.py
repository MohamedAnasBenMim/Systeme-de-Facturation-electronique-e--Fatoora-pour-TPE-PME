import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from app.core.config import settings

UNITS = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
TEN_TO_NINETEEN = ["dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
TENS = ["", "", "vingt", "trente", "quarante", "cinquante", "soixante"]


def _ensure_storage_dir():
    os.makedirs(settings.PDF_STORAGE_DIR, exist_ok=True)


def _deux_chiffres(n: int) -> str:
    if n < 10:
        return UNITS[n]
    if n < 20:
        return TEN_TO_NINETEEN[n - 10]
    if n < 70:
        d, u = divmod(n, 10)
        base = TENS[d]
        if u == 0:
            return base
        if u == 1:
            return f"{base} et un"
        return f"{base}-{UNITS[u]}"
    if n < 80:
        r = n - 60
        if r == 10:
            return "soixante-dix"
        if r == 11:
            return "soixante et onze"
        return f"soixante-{_deux_chiffres(r)}"
    r = n - 80
    if r == 0:
        return "quatre-vingts"
    if r == 1:
        return "quatre-vingt-un"
    return f"quatre-vingt-{_deux_chiffres(r)}"


def _trois_chiffres(n: int) -> str:
    c, r = divmod(n, 100)
    if c == 0:
        return _deux_chiffres(r)
    prefix = "cent" if c == 1 else f"{UNITS[c]} cent"
    if r == 0:
        return f"{prefix}s" if c > 1 else prefix
    return f"{prefix} {_deux_chiffres(r)}"


def _entier_en_lettres(n: int) -> str:
    if n == 0:
        return UNITS[0]
    parts = []
    millions, rem = divmod(n, 1_000_000)
    milliers, reste = divmod(rem, 1000)
    if millions:
        parts.append("un million" if millions == 1 else f"{_entier_en_lettres(millions)} millions")
    if milliers:
        parts.append("mille" if milliers == 1 else f"{_entier_en_lettres(milliers)} mille")
    if reste:
        parts.append(_trois_chiffres(reste))
    return " ".join(parts)


def _montant_en_lettres(montant: float) -> str:
    total = int(round(float(montant) * 1000))
    dinars, millimes = divmod(total, 1000)
    return f"{_entier_en_lettres(dinars)} dinars et {_entier_en_lettres(millimes)} millimes"


def _cadre_montant_lettres(montant: float) -> Table:
    texte = f"Arrêté à la somme de : {_montant_en_lettres(montant)}."
    style = ParagraphStyle("montant_lettres", fontSize=9, textColor=colors.black)
    table = Table([[Paragraph(texte, style)]], colWidths=[18 * cm])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#64748b")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def generer_pdf_facture(facture, entreprise: dict, client: dict) -> str:
 
    _ensure_storage_dir()

    filename = f"facture_{facture.id}.pdf"
    filepath = os.path.join(settings.PDF_STORAGE_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    bold   = ParagraphStyle("bold",   parent=styles["Normal"], fontName="Helvetica-Bold")
    small  = ParagraphStyle("small",  parent=styles["Normal"], fontSize=9)
    right  = ParagraphStyle("right",  parent=styles["Normal"], alignment=TA_RIGHT)
    center = ParagraphStyle("center", parent=styles["Normal"], alignment=TA_CENTER)
    title  = ParagraphStyle("title",  parent=styles["Heading1"], alignment=TA_CENTER, fontSize=16)

    story = []

    entreprise_lines = [
        Paragraph(f"<b>{entreprise.get('nom', '')}</b>", bold),
        Paragraph(entreprise.get("adresse", ""), small),
        Paragraph(f"Tél : {entreprise.get('telephone', '')}", small),
        Paragraph(f"Email : {entreprise.get('email', '')}", small),
        Paragraph(f"MF : {entreprise.get('matricule_fiscale', '')}", small),
    ]

    client_lines = [
        Paragraph("<b>Facturé à :</b>", bold),
        Paragraph(f"<b>{client.get('nom', '')} {client.get('prenom', '')}</b>", bold),
        Paragraph(client.get("adresse", ""), small),
        Paragraph(f"Tél : {client.get('telephone', '')}", small),
        Paragraph(f"Email : {client.get('email', '')}", small),
    ]

    header_data = [[entreprise_lines, client_lines]]
    header_table = Table(header_data, colWidths=[9 * cm, 9 * cm])
    header_table.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC")))
    story.append(Spacer(1, 0.5 * cm))

    # â”€â”€â”€ TITRE FACTURE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    story.append(Paragraph(f"FACTURE N° {facture.id}", title))
    story.append(Spacer(1, 0.3 * cm))

    meta_data = [
        [
            Paragraph(f"Date d'émission : <b>{facture.date_creation}</b>", small),
            Paragraph(
                f"Date d'échéance : <b>{facture.date_echeance or 'Non définie'}</b>",
                ParagraphStyle("sr", parent=small, alignment=TA_RIGHT)
            ),
        ]
    ]
    meta_table = Table(meta_data, colWidths=[9 * cm, 9 * cm])
    meta_table.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    # â”€â”€â”€ TABLEAU DES LIGNES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    col_headers = ["#", "N° BL", "Désignation", "Qté", "Prix Unitaire (DT)", "Montant (DT)"]
    rows = [col_headers]

    for i, ligne in enumerate(facture.lignes, start=1):
        designation = ligne.designation or ""
        bl_numero = ""
        m = re.match(r"^\[([^\]]+)\]\s*(.*)$", designation)
        if m:
            bl_numero = m.group(1)
            designation = m.group(2)

        rows.append([
            str(i),
            bl_numero,
            designation,
            str(ligne.quantite),
            f"{ligne.prix_unitaire:.3f}",
            f"{ligne.montant_ligne:.3f}",
        ])

    col_widths = [1 * cm, 2.7 * cm, 4.8 * cm, 2 * cm, 3.5 * cm, 3.5 * cm]
    lignes_table = Table(rows, colWidths=col_widths, repeatRows=1)
    lignes_table.setStyle(TableStyle([
        # En-tête
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        # Données
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("ALIGN",         (2, 1), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        # Grille
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ]))
    story.append(lignes_table)
    story.append(Spacer(1, 0.5 * cm))

    # â”€â”€â”€ TOTAUX â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    totaux_data = [
        ["Total HT",       f"{facture.total_ht:.3f} DT"],
        ["TVA (19%)",      f"{facture.tva:.3f} DT"],
        ["Timbre fiscal",  f"{facture.timbre_fiscal:.3f} DT"],
        ["TOTAL TTC",      f"{facture.total_ttc:.3f} DT"],
    ]
    totaux_table = Table(totaux_data, colWidths=[5 * cm, 4 * cm], hAlign="RIGHT")
    totaux_table.setStyle(TableStyle([
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ALIGN",         (1, 0), (1, -1), "RIGHT"),
        ("LINEABOVE",     (0, -1), (-1, -1), 1, colors.HexColor("#2C3E50")),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, -1), (-1, -1), 11),
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR",     (0, -1), (-1, -1), colors.white),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    story.append(totaux_table)
    story.append(Spacer(1, 0.35 * cm))
    story.append(_cadre_montant_lettres(facture.total_ttc))

    # â”€â”€â”€ PIED DE PAGE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC")))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"{entreprise.get('nom', '')} â€” {entreprise.get('adresse', '')}",
        ParagraphStyle("footer", parent=small, alignment=TA_CENTER, textColor=colors.grey)
    ))

    doc.build(story)
    return filepath


