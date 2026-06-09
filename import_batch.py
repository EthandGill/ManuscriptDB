"""Batch import all 11 manuscripts."""
import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\ManuscriptDB'
SCRIPT = r'C:\ManuscriptDB\import_manuscript.py'

manuscripts = [
    dict(docID=10051, id='P51',  name='Papyrus 51',
         date='c. 4th-5th century CE', found='Oxyrhynchus, Egypt',
         held='Ashmolean Museum, Oxford (P. Oxy. 2157)',
         content='Galatians 1:2-10, 13, 16-20', book='Galatians',
         lat=28.5383, lon=30.6765, pages=[10,20]),

    dict(docID=10049, id='P49',  name='Papyrus 49',
         date='c. 3rd century CE', found='Egypt',
         held='Yale University Library, New Haven (P. Yale 415)',
         content='Ephesians 4:16-29; 4:31-5:13', book='Ephesians',
         lat=28.5383, lon=30.6765, pages=[10,20]),

    dict(docID=10092, id='P92',  name='Papyrus 92',
         date='c. 3rd century CE', found='Fayyum, Egypt',
         held='Egyptian Museum, Cairo (Inv. 69,39a + 69,229a)',
         content='Ephesians 1:11-13, 19-21; 2 Thessalonians 1:4-5, 11-12',
         book='Ephesians, 2 Thessalonians',
         lat=29.3084, lon=30.8428, pages=[10,20,30,40]),

    dict(docID=10132, id='P132', name='Papyrus 132',
         date='c. 3rd-4th century CE', found='Oxyrhynchus, Egypt',
         held='Sackler Library, Oxford (P. Oxy. 5258)',
         content='Ephesians 3:21-4:2, 14-16', book='Ephesians',
         lat=28.5383, lon=30.6765, pages=[10,20]),

    dict(docID=10016, id='P16',  name='Papyrus 16',
         date='c. 3rd-4th century CE', found='Oxyrhynchus, Egypt',
         held='Bibliotheca Alexandrina, Alexandria (BAAM 0544 / P. Oxy. 1009)',
         content='Philippians 3:10-17; 4:2-8', book='Philippians',
         lat=28.5383, lon=30.6765, pages=[10,20]),

    dict(docID=10030, id='P30',  name='Papyrus 30',
         date='c. 3rd century CE', found='Oxyrhynchus, Egypt',
         held='Ghent University Library (P. Oxy. 1598, Inv. 61)',
         content='1 Thessalonians 4:12-5:28; 2 Thessalonians 1:1-2',
         book='1 Thessalonians, 2 Thessalonians',
         lat=28.5383, lon=30.6765, pages=[10,20,30,40,50,60,70,80]),

    dict(docID=10065, id='P65',  name='Papyrus 65',
         date='c. 3rd century CE', found='Egypt',
         held='National Archaeological Museum, Florence (PSI 1373)',
         content='1 Thessalonians 1:3-2:1; 2:6-13', book='1 Thessalonians',
         lat=28.5383, lon=30.6765, pages=[10,20]),

    dict(docID=10133, id='P133', name='Papyrus 133',
         date='c. mid-3rd century CE', found='Oxyrhynchus, Egypt',
         held='Sackler Library, Oxford (P. Oxy. 5259)',
         content='1 Timothy 3:13-4:8', book='1 Timothy',
         lat=28.5383, lon=30.6765, pages=[10,20]),

    dict(docID=10032, id='P32',  name='Papyrus 32',
         date='c. 200 CE', found='Egypt',
         held='John Rylands University Library, Manchester (Gr. P. 5)',
         content='Titus 1:11-15; 2:3-8', book='Titus',
         lat=28.5383, lon=30.6765, pages=[10,20]),

    dict(docID=10087, id='P87',  name='Papyrus 87',
         date='c. 3rd century CE', found='Egypt',
         held='Institut fuer Altertumskunde, University of Cologne (P. Col. theol. 12)',
         content='Philemon 13-15, 24-25', book='Philemon',
         lat=28.5383, lon=30.6765, pages=[10,20]),

    dict(docID=10139, id='P139', name='Papyrus 139',
         date='c. 4th century CE', found='Oxyrhynchus, Egypt',
         held='Sackler Library, Oxford (P. Oxy. 5347)',
         content='Philemon 1:6-8; 1:18-20', book='Philemon',
         lat=28.5383, lon=30.6765, pages=[10,20]),
]

for m in manuscripts:
    print(f"\n{'='*50}")
    print(f"Importing {m['id']}...")
    cmd = [
        'python', SCRIPT,
        '--docID', str(m['docID']),
        '--id', m['id'],
        '--name', m['name'],
        '--genre', 'new-testament',
        '--date', m['date'],
        '--found', m['found'],
        '--held', m['held'],
        '--content', m['content'],
        '--book', m['book'],
        '--lat', str(m['lat']),
        '--lon', str(m['lon']),
        '--pages', *[str(p) for p in m['pages']],
    ]
    result = subprocess.run(cmd, capture_output=False, text=True, cwd=BASE)
    if result.returncode != 0:
        print(f"ERROR on {m['id']}")

print("\n=== ALL IMPORTS DONE ===")
