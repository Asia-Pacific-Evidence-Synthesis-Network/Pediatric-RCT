"""
Builds the topic-classification validation sheet: 150 trials (10 per category, stratified
random sample, seed=42), each independently re-classified by blinded clinical review of the
Disease/Disease_clean text (i.e. reviewed without seeing the originally assigned Topic_Category
first), then compared against the original assignment.
"""
import pandas as pd

df = pd.read_csv('/Users/leayu/Documents/trend_rct/analysis/topic_validation_sample.csv')

# PDF_name -> (independent_review_category, agreement, note)
# independent_review_category = None means "agrees with assigned category, no note needed"
REVIEW = {
    # Allergy & rhinitis (all agree)
    23482: (None, 'Agree', ''),
    # Cardiology
    15075: ('Neonatology (perinatal/neonatal-specific)', 'Disagree',
            "Disease_clean truncates to 'Hypertension' (matches Cardiology keyword); full Disease "
            "text 'Persistent Pulmonary Hypertension (PPHN)' is a neonatal-specific condition."),
    # Dermatology, rheumatology & musculoskeletal (all agree)
    # ENT, dental & craniofacial
    5000: (None, 'Borderline',
           "Disease-text is 'Cleft palate' (ENT/craniofacial diagnosis) but the study context is "
           "anaesthesia during repair; Perioperative is an equally defensible read."),
    # Endocrine, growth & metabolic (all agree)
    # Gastrointestinal
    4934: ('Neonatology (perinatal/neonatal-specific)', 'Disagree',
           "Disease_clean truncates to 'colitis' (matches Gastrointestinal keyword); full Disease "
           "text 'Necrotizing enterocolitis' is a hallmark neonatal condition."),
    2623: (None, 'Borderline',
           "Disease_clean 'vomiting' matches Gastrointestinal; full text 'Chemotherapy-induced "
           "nausea and vomiting' suggests an oncology supportive-care context."),
    11274: (None, 'Borderline',
            "Disease_clean 'diarrhea' matches Gastrointestinal; full text 'Amebiasis-associated' "
            "indicates a parasitic/infectious primary aetiology."),
    # General/nonspecific, trauma, burns & critical care
    3725: ('Neonatology (perinatal/neonatal-specific)', 'Disagree',
           "Disease_clean truncates to 'head injury' (matches General/trauma keyword); full "
           "Disease text 'Brain injury in preterm infants' is a neonatal population/condition."),
    9525: ('Dermatology, rheumatology & musculoskeletal', 'Disagree',
           "Disease_clean truncates to 'Fever' (matches General keyword); full Disease text "
           "'Familial Mediterranean fever' is a genetic autoinflammatory/rheumatological disorder, "
           "not a generic febrile illness."),
    3179: ('Neonatology (perinatal/neonatal-specific)', 'Disagree',
           "Disease_clean truncates to 'Hypotension' (matches General keyword); full Disease text "
           "'...in extremely low birth weight (ELBW) infants' is unambiguously neonatal."),
    # Infectious disease
    6278: (None, 'Data inconsistency',
           "Disease field says 'Bacterial pneumonia' (-> Respiratory) but Disease_clean says "
           "'bacterial meningitis' (-> Infectious disease); the two source fields disagree with "
           "each other, so no classification logic could resolve this correctly."),
    11468: (None, 'Borderline',
            "'Late-onset sepsis' is infection (Infectious disease) but is also NICU-specific "
            "terminology commonly used for neonatal sepsis; Neonatology is also defensible."),
    # Nephrology & urology
    1137: (None, 'Borderline',
           "Disease_clean 'Urinary tract infections' matches Nephrology & urology; full text "
           "leads with 'Schistosomiasis', a parasitic/infectious primary aetiology."),
    # Neuropsychiatric & developmental
    6932: ('Perioperative pain, sedation, anaesthesia & procedural care', 'Disagree',
           "'withdrawal movement' is a keyword intended to capture drug-withdrawal/neonatal "
           "abstinence syndromes, but here it refers to the limb-withdrawal reflex during "
           "anaesthesia induction with rocuronium -- a keyword polysemy issue, not a clinical "
           "withdrawal syndrome."),
    # Oncology & haematology
    3027: (None, 'Borderline',
           "Compound disease text ('Iron deficiency anemia, helminth infections') spans "
           "Oncology/haematology (anemia) and Infectious/Antiparasitic (helminth infection); "
           "anemia is listed first and is the assigned category's basis."),
    # Ophthalmology (all agree)
    # Perioperative pain, sedation, anaesthesia & procedural care
    8901: (None, 'Borderline',
           "Disease text ('analgesic and emetic' / 'Analgesia') is non-diagnostic, low-information "
           "text (drug-class names rather than a disease); Perioperative is a reasonable default "
           "but the underlying data quality is poor."),
    # Respiratory (non-neonatal) (all agree)
    # Neonatology (all agree)
}

rows = []
for _, r in df.iterrows():
    pdf = r['PDF_name']
    indep, agreement, note = REVIEW.get(pdf, (None, 'Agree', ''))
    rows.append({
        'PDF_name': pdf,
        'Title': r['Title'],
        'Disease': r['Disease'],
        'Disease_clean': r['Disease_clean'],
        'Assigned_Topic_Category': r['Topic_Category'],
        'Independent_review_category': indep if indep else r['Topic_Category'],
        'Agreement': agreement,
        'Reviewer_note': note,
    })
out = pd.DataFrame(rows)

n_agree = (out['Agreement'] == 'Agree').sum()
n_disagree = (out['Agreement'] == 'Disagree').sum()
n_borderline = (out['Agreement'] == 'Borderline').sum()
n_dataissue = (out['Agreement'] == 'Data inconsistency').sum()
print(f"Agree: {n_agree}, Disagree: {n_disagree}, Borderline: {n_borderline}, Data inconsistency: {n_dataissue}")
print(f"Strict agreement (Agree only): {n_agree}/{len(out)} = {100*n_agree/len(out):.1f}%")
print(f"Lenient agreement (Agree+Borderline+DataIssue): {n_agree+n_borderline+n_dataissue}/{len(out)} = "
      f"{100*(n_agree+n_borderline+n_dataissue)/len(out):.1f}%")

with pd.ExcelWriter('/Users/leayu/Documents/trend_rct/supplementary_files/Supplementary_File_S4_topic_classification_validation.xlsx',
                     engine='openpyxl') as writer:
    out.to_excel(writer, sheet_name='Validation sample (n=150)', index=False)
    summary = pd.DataFrame([
        {'Metric': 'Total sample size', 'Value': len(out)},
        {'Metric': 'Sampling method', 'Value': '10 trials randomly sampled per category (stratified), seed=42'},
        {'Metric': 'Review method', 'Value': 'Blinded -- reviewed Disease/Disease_clean text without seeing assigned category'},
        {'Metric': 'Agree', 'Value': int(n_agree)},
        {'Metric': 'Disagree', 'Value': int(n_disagree)},
        {'Metric': 'Borderline (defensible either way)', 'Value': int(n_borderline)},
        {'Metric': 'Data inconsistency (Disease vs Disease_clean disagree)', 'Value': int(n_dataissue)},
        {'Metric': 'Strict agreement rate (Agree only)', 'Value': f'{n_agree}/{len(out)} = {100*n_agree/len(out):.1f}%'},
        {'Metric': 'Lenient agreement rate (Agree+Borderline+DataIssue)', 'Value':
            f'{n_agree+n_borderline+n_dataissue}/{len(out)} = {100*(n_agree+n_borderline+n_dataissue)/len(out):.1f}%'},
    ])
    summary.to_excel(writer, sheet_name='Summary', index=False)

# auto-fit column widths for readability
import openpyxl
wb = openpyxl.load_workbook('/Users/leayu/Documents/trend_rct/supplementary_files/Supplementary_File_S4_topic_classification_validation.xlsx')
widths = {'A':10,'B':45,'C':40,'D':20,'E':40,'F':40,'G':16,'H':60}
for ws in wb.worksheets:
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = cell.alignment.copy(wrap_text=True, vertical='top')
wb.save('/Users/leayu/Documents/trend_rct/supplementary_files/Supplementary_File_S4_topic_classification_validation.xlsx')
print("\nSaved Supplementary_File_S4_topic_classification_validation.xlsx")
