import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from app.models.devis import Devis
from app.models.BonCommande import BonCommande
from app.models.BonLivraison import BonLivraison


class PdfService:
    _UNITS = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
    _TEN_TO_NINETEEN = ["dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
    _TENS = ["", "", "vingt", "trente", "quarante", "cinquante", "soixante"]

    def generer_pdf_devis(self, devis: Devis, client: dict | None) -> bytes:
        buffer = io.BytesIO()
        doc = self._create_doc_facture_style(buffer)
        elements = []

        styles = getSampleStyleSheet()
        title = ParagraphStyle("title_devis", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=16)
        small = ParagraphStyle("small_devis", parent=styles["Normal"], fontSize=9)

        elements += self._header_client_table(client, small)
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC")))
        elements.append(Spacer(1, 0.5 * cm))

        elements.append(Paragraph(f"DEVIS N° {devis.numero}", title))
        elements.append(Spacer(1, 0.3 * cm))

        meta_data = [[
            Paragraph(f"Date d'émission : <b>{self._format_date(getattr(devis, 'created_at', None))}</b>", small),
            Paragraph(
                f"Date d'expiration : <b>{self._format_date(getattr(devis, 'date_expiration', None)) or 'Non définie'}</b>",
                ParagraphStyle("small_devis_right", parent=small, alignment=TA_RIGHT),
            ),
        ]]
        meta_table = Table(meta_data, colWidths=[9 * cm, 9 * cm])
        meta_table.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        elements.append(meta_table)
        elements.append(Paragraph(f"Statut : <b>{str(devis.statut)}</b>", small))
        elements.append(Spacer(1, 0.5 * cm))

        data = [["#", "Désignation", "Qté", "Prix Unitaire (DT)", "TVA %", "Montant (DT)"]]
        for idx, l in enumerate(devis.lignes, start=1):
            montant_tva = getattr(l, "montant_tva", getattr(l, "taux_tva", 0))
            data.append([
                str(idx),
                l.description or "",
                str(l.quantite),
                f"{l.prix_unitaire:.3f}",
                f"{montant_tva}%",
                f"{l.montant_ht:.3f}",
            ])

        elements.append(self._build_table_devis_style_facture(data))
        elements.append(Spacer(1, 0.5 * cm))
        ttc_devis = self._ttc_sans_timbre(devis)
        elements.append(self._build_totaux_style_facture(devis.montant_ht, devis.montant_tva, ttc_devis))
        elements.append(Spacer(1, 0.35 * cm))
        elements.append(self._cadre_montant_lettres(ttc_devis))
        elements.append(Spacer(1, 1 * cm))
        elements.append(self._note("Devis valable 30 jours à compter de la date d'émission."))

        doc.build(elements)
        return buffer.getvalue()

    def generer_pdf_bc(self, bc: BonCommande, client: dict | None) -> bytes:
        buffer = io.BytesIO()
        doc = self._create_doc(buffer)
        elements = []

        elements.append(self._titre(f"BON DE COMMANDE N° {bc.numero}"))
        elements.append(Spacer(1, 0.5 * cm))
        elements += self._infos_client(client)
        elements += self._infos_document([
            ("Date", self._format_date(getattr(bc, "created_at", None))),
            ("Statut", str(bc.statut)),
            ("Livraison souhaitée", self._format_date(getattr(bc, "date_livraison_souhaitee", None))),
        ])
        elements.append(Spacer(1, 0.5 * cm))

        data = [["Désignation", "Qté", "Prix HT", "TVA %", "Montant HT"]]
        for l in bc.lignes:
            taux_tva = getattr(l, "taux_tva", getattr(l, "montant_tva", 0))
            data.append([
                l.description or "",
                str(l.quantite),
                f"{l.prix_unitaire:.3f} TND",
                f"{taux_tva}%",
                f"{l.montant_ht:.3f} TND",
            ])
        data += self._lignes_totaux(bc.montant_ht, bc.taux_tva, bc.montant_ttc)

        elements.append(self._build_table(data))
        elements.append(Spacer(1, 0.35 * cm))
        elements.append(self._cadre_montant_lettres(bc.montant_ttc))
        elements.append(Spacer(1, 1 * cm))
        if getattr(bc, "notes", None):
            elements.append(self._note(f"Notes : {bc.notes}"))

        doc.build(elements)
        return buffer.getvalue()

    def generer_pdf_bl(self, bl: BonLivraison, client: dict | None) -> bytes:
        buffer = io.BytesIO()
        doc = self._create_doc_facture_style(buffer)
        elements = []

        styles = getSampleStyleSheet()
        title = ParagraphStyle("title_bl", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=16)
        small = ParagraphStyle("small_bl", parent=styles["Normal"], fontSize=9)

        elements += self._header_client_table(client, small)
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC")))
        elements.append(Spacer(1, 0.5 * cm))

        elements.append(Paragraph(f"BON DE LIVRAISON N° {bl.numero}", title))
        elements.append(Spacer(1, 0.3 * cm))

        meta_data = [[
            Paragraph(f"Date de livraison : <b>{self._format_date(getattr(bl, 'date_livraison', None))}</b>", small),
            Paragraph(
                f"Source : <b>{str(bl.source)}</b>",
                ParagraphStyle("small_bl_right", parent=small, alignment=TA_RIGHT),
            ),
        ]]
        meta_table = Table(meta_data, colWidths=[9 * cm, 9 * cm])
        meta_table.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        elements.append(meta_table)
        elements.append(Paragraph(f"Statut : <b>{str(bl.statut)}</b>", small))
        elements.append(Spacer(1, 0.5 * cm))

        data = [["#", "Désignation", "Qté commandée", "Qté livrée", "Prix HT (DT)", "Montant (DT)"]]
        for idx, l in enumerate(bl.lignes, start=1):
            data.append([
                str(idx),
                l.description or "",
                str(l.quantite),
                str(l.quantite_livree),
                f"{l.prix_unitaire:.3f}",
                f"{l.montant_ht:.3f}",
            ])

        elements.append(self._build_table_bl_style_facture(data))
        elements.append(Spacer(1, 0.5 * cm))
        ttc_bl = self._ttc_sans_timbre(bl)
        elements.append(self._build_totaux_style_facture(bl.montant_ht, bl.montant_tva, ttc_bl))
        elements.append(Spacer(1, 0.35 * cm))
        elements.append(self._cadre_montant_lettres(ttc_bl))
        elements.append(Spacer(1, 1 * cm))
        if getattr(bl, "notes", None):
            elements.append(self._note(f"Notes : {bl.notes}"))

        doc.build(elements)
        return buffer.getvalue()

    def _create_doc(self, buffer) -> SimpleDocTemplate:
        return SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

    def _create_doc_facture_style(self, buffer) -> SimpleDocTemplate:
        return SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

    def _titre(self, texte: str) -> Paragraph:
        return Paragraph(texte, ParagraphStyle("titre", fontSize=18, fontName="Helvetica-Bold", spaceAfter=10, alignment=TA_CENTER))

    def _note(self, texte: str) -> Paragraph:
        return Paragraph(texte, ParagraphStyle("note", fontSize=8, textColor=colors.grey))

    def _cadre_montant_lettres(self, montant: float) -> Table:
        texte = f"Arrêté à la somme de : {self._montant_en_lettres(montant)}."
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

    def _header_client_table(self, client: dict | None, small_style: ParagraphStyle) -> list:
        if not client:
            return []
        bold_style = ParagraphStyle("bold_doc", parent=small_style, fontName="Helvetica-Bold")
        client_lines = [
            Paragraph("<b>Client :</b>", bold_style),
            Paragraph(f"<b>{client.get('nom', '')} {client.get('prenom', '')}</b>", bold_style),
            Paragraph(client.get("adresse", ""), small_style),
            Paragraph(f"Tél : {client.get('telephone', '')}", small_style),
            Paragraph(f"Email : {client.get('email', '')}", small_style),
        ]
        spacer_lines = [Paragraph("", small_style)]
        table = Table([[spacer_lines, client_lines]], colWidths=[9 * cm, 9 * cm])
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ]))
        return [table]

    def _infos_client(self, client: dict | None) -> list:
        styles = getSampleStyleSheet()
        elements = []
        if client:
            nom = f"{client.get('nom', '')} {client.get('prenom', '')}".strip()
            elements.append(Paragraph(f"<b>Client :</b> {nom}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Email :</b> {client.get('email', '')}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Téléphone :</b> {client.get('telephone', '')}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Adresse :</b> {client.get('adresse', '')}", styles["Normal"]))
        return elements

    def _infos_document(self, champs: list[tuple]) -> list:
        styles = getSampleStyleSheet()
        return [Paragraph(f"<b>{label} :</b> {valeur}", styles["Normal"]) for label, valeur in champs if valeur]

    def _format_date(self, date) -> str:
        if not date:
            return ""
        try:
            return date.strftime("%d/%m/%Y")
        except Exception:
            return str(date)

    def _lignes_totaux(self, ht, tva, ttc) -> list:
        return [
            ["", "", "", "Total HT :", f"{ht:.3f} TND"],
            ["", "", "", "TVA :", f"{tva:.3f} TND"],
            ["", "", "", "Total TTC :", f"{ttc:.3f} TND"],
        ]

    def _lignes_totaux_bl(self, ht, tva, ttc) -> list:
        return [
            ["", "", "", "", "Total HT :", f"{ht:.3f} TND"],
            ["", "", "", "", "TVA :", f"{tva:.3f} TND"],
            ["", "", "", "", "Total TTC :", f"{ttc:.3f} TND"],
        ]

    def _build_table(self, data: list) -> Table:
        table = Table(data, colWidths=[7 * cm, 2 * cm, 3 * cm, 2.5 * cm, 3.5 * cm])
        table.setStyle(self._style_table(nb_colonnes=5))
        return table

    def _build_table_bl(self, data: list) -> Table:
        table = Table(data, colWidths=[5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 3 * cm])
        table.setStyle(self._style_table(nb_colonnes=6))
        return table

    def _build_table_devis_style_facture(self, data: list) -> Table:
        table = Table(data, colWidths=[1 * cm, 6 * cm, 2 * cm, 3.4 * cm, 1.8 * cm, 3.8 * cm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))
        return table

    def _build_table_bl_style_facture(self, data: list) -> Table:
        table = Table(data, colWidths=[1 * cm, 5.4 * cm, 2.5 * cm, 2.5 * cm, 3.0 * cm, 3.6 * cm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))
        return table

    def _build_totaux_style_facture(self, ht, tva, ttc) -> Table:
        table = Table([
            ["Total HT", f"{ht:.3f} DT"],
            ["TVA", f"{tva:.3f} DT"],
            ["TOTAL TTC", f"{ttc:.3f} DT"],
        ], colWidths=[5 * cm, 4 * cm], hAlign="RIGHT")
        table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#2C3E50")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, -1), (-1, -1), 11),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        return table

    def _ttc_sans_timbre(self, doc) -> float:
        ttc = float(getattr(doc, "montant_ttc", 0) or 0)
        timbre = float(getattr(doc, "timbre_fiscal", 0) or 0)
        if timbre > 0 and ttc >= timbre:
            return ttc - timbre
        return ttc

    def _style_table(self, nb_colonnes: int) -> TableStyle:
        return TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -4), [colors.white, colors.HexColor("#f1f5f9")]),
            ("FONTNAME", (-2, -3), (-1, -1), "Helvetica-Bold"),
            ("LINEABOVE", (-2, -3), (-1, -3), 1, colors.black),
            ("GRID", (0, 0), (-1, -4), 0.5, colors.HexColor("#e2e8f0")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ])

    def _deux_chiffres(self, n: int) -> str:
        if n < 10:
            return self._UNITS[n]
        if n < 20:
            return self._TEN_TO_NINETEEN[n - 10]
        if n < 70:
            d, u = divmod(n, 10)
            base = self._TENS[d]
            if u == 0:
                return base
            if u == 1:
                return f"{base} et un"
            return f"{base}-{self._UNITS[u]}"
        if n < 80:
            r = n - 60
            if r == 10:
                return "soixante-dix"
            if r == 11:
                return "soixante et onze"
            return f"soixante-{self._deux_chiffres(r)}"
        r = n - 80
        if r == 0:
            return "quatre-vingts"
        if r == 1:
            return "quatre-vingt-un"
        return f"quatre-vingt-{self._deux_chiffres(r)}"

    def _trois_chiffres(self, n: int) -> str:
        c, r = divmod(n, 100)
        if c == 0:
            return self._deux_chiffres(r)
        prefix = "cent" if c == 1 else f"{self._UNITS[c]} cent"
        if r == 0:
            return f"{prefix}s" if c > 1 else prefix
        return f"{prefix} {self._deux_chiffres(r)}"

    def _entier_en_lettres(self, n: int) -> str:
        if n == 0:
            return self._UNITS[0]
        parts = []
        millions, rem = divmod(n, 1_000_000)
        milliers, reste = divmod(rem, 1000)
        if millions:
            parts.append("un million" if millions == 1 else f"{self._entier_en_lettres(millions)} millions")
        if milliers:
            parts.append("mille" if milliers == 1 else f"{self._entier_en_lettres(milliers)} mille")
        if reste:
            parts.append(self._trois_chiffres(reste))
        return " ".join(parts)

    def _montant_en_lettres(self, montant: float) -> str:
        total = int(round(float(montant) * 1000))
        dinars, millimes = divmod(total, 1000)
        return f"{self._entier_en_lettres(dinars)} dinars et {self._entier_en_lettres(millimes)} millimes"
