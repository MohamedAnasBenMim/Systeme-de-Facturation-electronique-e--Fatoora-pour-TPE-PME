from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
from datetime import datetime


def generer_pdf_achat(achat_data: dict, fournisseur: dict, entreprise: dict) -> str:
    """
    Génère un PDF pour un achat.
    Retourne le chemin du fichier PDF généré.
    """
    # Créer le dossier storage s'il n'existe pas
    storage_dir = "storage/achats"
    os.makedirs(storage_dir, exist_ok=True)

    filename = f"{storage_dir}/achat_{achat_data['id']}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Styles personnalisés
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )

    elements = []

    # Titre
    elements.append(Paragraph("Facture d'Achat", title_style))
    elements.append(Spacer(1, 12))

    # Informations entreprise
    elements.append(Paragraph(f"<b>Entreprise Acheteuse:</b> {entreprise['nom']}", styles['Normal']))
    elements.append(Paragraph(f"Adresse: {entreprise['adresse']}, {entreprise['ville']}", styles['Normal']))
    elements.append(Paragraph(f"Matricule Fiscal: {entreprise.get('matricule_fiscal', 'N/A')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Informations fournisseur
    elements.append(Paragraph(f"<b>Fournisseur:</b> {fournisseur.get('nom', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"Adresse: {fournisseur.get('adresse', 'N/A')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Détails achat
    elements.append(Paragraph(f"Numéro d'Achat: {achat_data['id']}", styles['Normal']))
    elements.append(Paragraph(f"Date de Création: {achat_data['date_creation']}", styles['Normal']))
    elements.append(Paragraph(f"Date d'Échéance: {achat_data.get('date_echeance', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"Statut: {achat_data['statut']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tableau des lignes
    data = [['Produit', 'Quantité', 'Prix Unitaire', 'Montant']]
    for ligne in achat_data['lignes']:
        data.append([
            ligne['designation'],
            str(ligne['quantite']),
            f"{ligne['prix_unitaire']:.3f} DT",
            f"{ligne['montant_ligne']:.3f} DT"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Totaux
    elements.append(Paragraph(f"Total HT: {achat_data['total_ht']:.3f} DT", styles['Normal']))
    elements.append(Paragraph(f"TVA (19%): {achat_data['tva']:.3f} DT", styles['Normal']))
    elements.append(Paragraph(f"Timbre Fiscal: {achat_data['timbre_fiscal']:.3f} DT", styles['Normal']))
    elements.append(Paragraph(f"<b>Total TTC: {achat_data['total_ttc']:.3f} DT</b>", styles['Normal']))

    # Générer le PDF
    doc.build(elements)

    return filename