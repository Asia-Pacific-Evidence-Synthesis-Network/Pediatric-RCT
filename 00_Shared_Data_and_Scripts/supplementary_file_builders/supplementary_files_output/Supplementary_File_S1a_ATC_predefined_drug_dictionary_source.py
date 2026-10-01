"""
Predefined keyword dictionary mapping commonly used drug names to WHO ATC first-level
groups (Supplementary File S1, dictionary-classified rows). Extracted from
analysis/rebuild_all_consolidated_v2.py (DRUG_KEYWORDS) and analysis/add_atc_level1.py
(CATEGORY_TO_LETTER + the 3 mixed-category keyword-level splits).
"""

DRUG_KEYWORDS = {
    'Anaesthetics, sedatives & perioperative analgesics (ATC N01/N05C/M03)': ['midazolam', 'ketamine', 'propofol', 'dexmedetomidine', 'sevoflurane', 'halothane', 'remifentanil', 'fentanyl', 'morphine', 'bupivacaine', 'ropivacaine', 'lidocaine', 'levobupivacaine', 'tramadol', 'nitrous oxide', 'rocuronium', 'emla', 'atropine', 'clonidine', 'diazepam', 'botulinum', 'isoflurane', 'desflurane', 'vecuronium', 'succinylcholine', 'suxamethonium', 'sugammadex', 'prilocaine', 'tetracaine', 'articaine', 'mepivacaine', 'sufentanil', 'alfentanil', 'pethidine', 'meperidine', 'chloral hydrate', 'droperidol', 'thiopental', 'thiopentone', 'methohexital', 'etomidate', 'glycopyrrolate', 'neostigmine', 'edrophonium', 'physostigmine', 'pyridostigmine', 'mivacurium', 'pancuronium', 'atracurium', 'cisatracurium', 'rapacuronium', 'ephedrine', 'phentolamine', 'xenon', 'ethyl chloride', 'dantrolene', 'baclofen', 'nalbuphine', 'butorphanol', 'buprenorphine', 'hydromorphone', 'oxycodone', 'dezocine', 'methadone', 'naloxone'],
    'Analgesics/antipyretics/NSAIDs (ATC N02)': ['acetaminophen', 'paracetamol', '\\bibuprofen\\b', 'indomethacin', 'diclofenac', 'naproxen', 'aspirin', 'ketorolac', 'codeine', 'ketoprofen', 'celecoxib', 'nimesulide', 'rofecoxib', 'propacetamol', 'meloxicam', 'piroxicam', 'tenoxicam', 'lornoxicam', 'dexibuprofen', 'acetylsalicylic acid', 'metamizole'],
    'Respiratory drugs: bronchodilators & inhaled corticosteroids (ATC R03)': ['salbutamol', 'albuterol', 'budesonide', 'fluticasone', 'beclomethasone', 'montelukast', 'theophylline', 'cromoglycate', 'cromolyn', 'ipratropium', 'terbutaline', 'formoterol', 'salmeterol', 'dextromethorphan', 'aminophylline', 'n-acetylcysteine', 'acetylcysteine', 'mometasone', 'ciclesonide', 'flunisolide', 'ambroxol', 'bambuterol', 'metaproterenol', 'isoproterenol', 'procaterol', 'tulobuterol', 'vilanterol', 'oxitropium', 'guaifenesin', 'dornase alfa', 'pranlukast', 'doxapram', 'fenoterol', 'tiotropium'],
    'Systemic corticosteroids (ATC H02)': ['dexamethasone', 'prednisolone', 'prednisone', 'methylprednisolone', 'hydrocortisone', 'deflazacort', 'betamethasone', 'triamcinolone', 'fludrocortisone', 'corticosteroid', 'corticosteroids'],
    'Antibacterials (ATC J01)': ['amoxicillin', 'azithromycin', 'penicillin', 'gentamicin', 'erythromycin', 'ceftriaxone', 'ampicillin', 'metronidazole', 'clarithromycin', 'clavulanate', 'clavulanic acid', 'cefixime', 'cefpodoxime', 'cefaclor', 'cefotaxime', 'piperacillin', 'tazobactam', 'vancomycin', 'antibiotic', 'trimethoprim', 'sulfamethoxazole', 'cefepime', 'cefuroxime', 'ceftazidime', 'clindamycin', 'meropenem', 'doxycycline', 'ciprofloxacin', 'ofloxacin', 'levofloxacin', 'nitrofurantoin', 'dapsone', 'cefdinir', 'cefprozil', 'ceftibuten', 'amikacin', 'tobramycin', 'minocycline', 'chloramphenicol', 'cephalexin', 'cefalexin', 'aztreonam', 'ertapenem', 'daptomycin', 'linezolid', 'sultamicillin', 'sulbactam', 'flucloxacillin', 'cloxacillin', 'ticarcillin', 'moxalactam', 'oxytetracycline', 'tetracycline', 'rifampicin', 'rifampin', 'isoniazid', 'pyrazinamide', 'mupirocin', 'bacitracin', 'polymyxin b', 'neomycin', 'fusidic acid', 'ceftaroline', 'loracarbef', 'cefetamet', 'cefadroxil', 'pivmecillinam'],
    'Antiparasitics: antimalarials & anthelmintics (ATC P01/P02)': ['artesunate', 'artemether', 'chloroquine', 'amodiaquine', 'sulfadoxine', 'pyrimethamine', 'quinine', 'praziquantel', 'albendazole', 'mebendazole', 'ivermectin', 'lumefantrine', 'piperaquine', 'dihydroartemisinin', 'levamisole', 'mefloquine', 'chlorproguanil', 'tinidazole', 'furazolidone', 'nitazoxanide', 'metrifonate', 'moxidectin', 'tribendimidine', 'ornidazole', 'oxantel', 'artemisinin', 'primaquine', 'pyronaridine', 'proguanil'],
    'CNS/psychiatric agents incl. psychostimulants (ATC N06B/N05A/N06A)': ['methylphenidate', 'atomoxetine', 'risperidone', 'fluoxetine', 'melatonin', 'aripiprazole', 'sertraline', 'valproate', 'valproic', 'carbamazepine', 'levetiracetam', 'gabapentin', 'phenobarbital', 'topiramate', 'lamotrigine', 'olanzapine', 'haloperidol', 'amitriptyline', 'naltrexone', 'guanfacine', 'piracetam', 'lisdexamfetamine', 'fenfluramine', 'dextroamphetamine', 'amphetamine', 'lithium', 'imipramine', 'quetiapine', 'lorazepam', 'hydroxyzine', 'citalopram', 'escitalopram', 'bupropion', 'venlafaxine', 'desipramine', 'clomipramine', 'nortriptyline', 'paroxetine', 'fluvoxamine', 'duloxetine', 'memantine', 'modafinil', 'pemoline', 'zolpidem', 'clobazam', 'oxcarbazepine', 'zonisamide', 'perampanel', 'pregabalin', 'phenytoin', 'vigabatrin', 'ethosuximide', 'clonazepam', 'temazepam', 'flunitrazepam', 'chlorpromazine', 'thioridazine', 'molindone', 'pimozide', 'ziprasidone', 'lurasidone', 'asenapine', 'clozapine', 'donepezil', 'selegiline', 'riluzole', 'tianeptine', 'buspirone', 'reboxetine', 'vilazodone', 'dasotraline', 'sodium oxybate', 'cannabidiol', 'nusinersen', 'viltolarsen', 'eteplirsen', 'ataluren', 'fingolimod', 'levodopa', 'carbidopa', 'ecopipam', 'dichloroacetate'],
    'Endocrine, growth & metabolic agents (ATC H01/A10)': ['growth hormone', 'somatropin', 'somatrogon', 'somapacitan', '\\binsulin\\b', 'desmopressin', 'metformin', 'levothyroxine', 'oxandrolone', 'liothyronine', 'testosterone', 'estradiol', 'ethinylestradiol', 'ethinyl estradiol', 'oxytocin', 'letrozole', 'calcitriol', 'cholecalciferol', 'mecasermin', 'liraglutide', 'exenatide', 'pioglitazone', 'rosiglitazone', 'empagliflozin', 'corticotropin', 'tetracosactide', 'leuprolide', 'triptorelin', 'deslorelin', 'gonadorelin', 'medroxyprogesterone', 'progesterone', 'flutamide', 'testolactone', 'anastrozole', 'sapropterin', 'idebenone', 'vosoritide', 'pramlintide', 'sibutramine', 'orlistat', 'carnitine'],
    'Antineoplastic & immunosuppressive agents (ATC L01/L04)': ['chemotherapy', 'methotrexate', 'vincristine', 'cyclophosphamide', 'tacrolimus', 'cyclosporine', 'ciclosporin', 'dexrazoxane', 'asparaginase', 'pegaspargase', 'dactinomycin', 'cisplatin', 'carboplatin', 'daunorubicin', 'doxorubicin', 'mercaptopurine', 'hydroxyurea', 'hydroxycarbamide', 'teniposide', 'everolimus', 'irinotecan', 'topotecan', 'tioguanine', 'thioguanine', 'fludarabine', 'dacarbazine', 'arsenic trioxide', 'thalidomide', 'temozolomide', 'mitomycin', 'bleomycin', 'idarubicin', 'gemtuzumab', 'azathioprine', 'mycophenolate', 'sirolimus', 'basiliximab', 'abatacept', 'anakinra', 'rasburicase', 'allopurinol', 'vinblastine', 'etoposide', 'ifosfamide', 'cytarabine', 'fluorouracil'],
    'Blood & haematologic agents (ATC B)': ['\\biron\\b', 'heparin', 'erythropoietin', 'folic acid', 'vitamin k', 'tranexamic acid', 'epoetin', 'darbepoetin', 'filgrastim', 'pegfilgrastim', 'sargramostim', 'romiplostim', 'eltrombopag', 'deferasirox', 'deferiprone', 'factor viii', 'plasminogen', 'aminocaproic acid', 'alteplase', 'enoxaparin', 'albumin', 'rivaroxaban', 'prasugrel', 'ferrous'],
    'Neonatal-specific pharmacotherapy (surfactant, caffeine for apnoea)': ['surfactant', '\\bcaffeine\\b', 'beractant', 'poractant', 'colfosceril', 'calfactant', 'lucinactant'],
    'Cardiovascular agents (ATC C)': ['propranolol', 'captopril', 'enalapril', 'furosemide', 'amlodipine', 'pravastatin', 'statin', 'milrinone', 'dopamine', 'dobutamine', 'sildenafil', 'phenylephrine', 'ephedrine', 'valsartan', 'timolol', 'levosimendan', 'diltiazem', 'metoprolol', 'atenolol', 'carvedilol', 'nicardipine', 'nitroglycerin', 'nitroprusside', 'digoxin', 'amiodarone', 'esmolol', 'bosentan', 'ambrisentan', 'ramipril', 'perindopril', 'doxazosin', 'midodrine', 'acetazolamide', 'hydrochlorothiazide', 'chlorothiazide', 'eplerenone', 'tadalafil', 'spironolactone', 'bumetanide', 'vasopressin'],
    'Vitamins/minerals/supplements (ATC A11/A12)': ['\\bvitamin\\b', 'fluoride', '\\bmagnesium\\b', 'zinc', 'ascorbic acid', 'pyridoxine', 'omega-3', 'coenzyme q10', 'myo-inositol', 'creatine', 'glutamine', 'carnosine', 'docosahexaenoic', 'inositol', 'calcium', '\\bglucose\\b'],
    'Vaccines/immunologicals (ATC J07)': ['vaccine', 'immunization', 'immunisation', 'immunoglobulin'],
    'Antiemetics & GI motility agents (ATC A03/A04)': ['ondansetron', 'granisetron', 'tropisetron', 'metoclopramide', 'domperidone', 'cisapride', 'dolasetron', 'palonosetron', 'racecadotril', 'dimenhydrinate', 'diosmectite', 'aprepitant', 'ramosetron', 'simethicone', 'loperamide', 'lubiprostone'],
    'Antihistamines & antiallergic agents (ATC R06)': ['cetirizine', 'ketotifen', 'nedocromil', 'loratadine', 'diphenhydramine', 'chlorpheniramine', 'desloratadine', 'fexofenadine', 'omalizumab', 'dupilumab', 'brompheniramine', 'astemizole', 'terfenadine', 'azelastine', 'bepotastine', 'olopatadine', 'levocabastine', 'alimemazine', 'trimeprazine', 'allergen'],
    'Antiulcer & acid-suppressant agents (ATC A02)': ['omeprazole', 'ranitidine', 'esomeprazole', 'lansoprazole', 'famotidine', 'pantoprazole', 'rabeprazole', 'cimetidine', 'dexlansoprazole', 'sucralfate'],
    'Antivirals: antiretrovirals (ATC J05C)': ['lamivudine', 'zidovudine', 'nevirapine', 'ritonavir', 'lopinavir', 'stavudine', 'abacavir', 'efavirenz', 'tenofovir', 'didanosine', 'antiretroviral'],
    'Antivirals: non-HIV (ATC J05B)': ['acyclovir', 'aciclovir', 'ribavirin', 'oseltamivir', 'ganciclovir', 'vidarabine', 'laninamivir'],
    'Ophthalmological agents (ATC S01)': ['tropicamide', 'cyclopentolate', 'proparacaine', 'fluorometholone', 'ranibizumab'],
    'Antiseptics & disinfectants (ATC D08/D09)': ['chlorhexidine', 'povidone-iodine', 'silver nitrate', 'silver sulfadiazine', 'sodium hypochlorite'],
    'Antifungals (ATC J02)': ['fluconazole', 'itraconazole', 'nystatin', 'amphotericin', 'voriconazole', 'ketoconazole', 'caspofungin', 'griseofulvin', 'terbinafine'],
    'Biologics/monoclonal antibodies & disease-modifying agents (ATC L04)': ['etanercept', 'infliximab', 'rituximab', 'adalimumab', 'tocilizumab', 'secukinumab', 'palivizumab', 'motavizumab', 'nirsevimab', 'bevacizumab', 'evolocumab', 'burosumab', 'idursulfase', 'drisapersen', 'edasalonexent'],
    'Topical dermatological agents (ATC D)': ['pimecrolimus', 'calcineurin', 'emollient', 'topical steroid', 'delgocitinib', 'crisaborole', 'cantharidin'],
}

CATEGORY_TO_LETTER = {
    'Analgesics/antipyretics/NSAIDs (ATC N02)': 'N',
    'Respiratory drugs: bronchodilators & inhaled corticosteroids (ATC R03)': 'R',
    'Systemic corticosteroids (ATC H02)': 'H',
    'Antibacterials (ATC J01)': 'J',
    'Antiparasitics: antimalarials & anthelmintics (ATC P01/P02)': 'P',
    'CNS/psychiatric agents incl. psychostimulants (ATC N06B/N05A/N06A)': 'N',
    'Antineoplastic & immunosuppressive agents (ATC L01/L04)': 'L',
    'Blood & haematologic agents (ATC B)': 'B',
    'Cardiovascular agents (ATC C)': 'C',
    'Vitamins/minerals/supplements (ATC A11/A12)': 'A',
    'Vaccines/immunologicals (ATC J07)': 'J',
    'Antiemetics & GI motility agents (ATC A03/A04)': 'A',
    'Antihistamines & antiallergic agents (ATC R06)': 'R',
    'Antiulcer & acid-suppressant agents (ATC A02)': 'A',
    'Antivirals: antiretrovirals (ATC J05C)': 'J',
    'Antivirals: non-HIV (ATC J05B)': 'J',
    'Ophthalmological agents (ATC S01)': 'S',
    'Antiseptics & disinfectants (ATC D08/D09)': 'D',
    'Antifungals (ATC J02)': 'J',
    'Biologics/monoclonal antibodies & disease-modifying agents (ATC L04)': 'L',
    'Topical dermatological agents (ATC D)': 'D',
}

# 3 categories above mix two ATC first-level groups; split at the individual-keyword level:
ANAESTHETICS_M03 = {'rocuronium', 'atracurium', 'baclofen', 'cisatracurium', 'alcuronium', 'vecuronium', 'pancuronium', 'doxacurium', 'suxamethonium', 'rapacuronium', 'mivacurium', 'sugammadex', 'succinylcholine', 'tubocurarine', 'dantrolene'}  # -> M (muscle relaxants); rest of category -> N
ENDOCRINE_A10 = {'empagliflozin', 'insulin', 'pioglitazone', 'exenatide', 'rosiglitazone', 'metformin', 'liraglutide'}  # -> A (antidiabetics); rest of category -> H
NEONATAL_R07 = {'beractant', 'poractant', 'colfosceril', 'calfactant', 'lucinactant', 'surfactant'}  # -> R (surfactant); rest of category -> N
