import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'C:\ManuscriptDB'
S = r'C:\ManuscriptDB\import_manuscript.py'

MSS = [
    dict(docID=10012, id='P12',  name='Papyrus 12',
         date='c. 285 CE', found='Fayyum, Egypt',
         held='Morgan Library & Museum, New York (P. Amherst 3b)',
         content='Hebrews 1:1', book='Hebrews',
         lat=29.3084, lon=30.8428, pages=list(range(10,50,10))),

    dict(docID=10013, id='P13',  name='Papyrus 13',
         date='c. 225-250 CE', found='Oxyrhynchus, Egypt',
         held='British Library, London (Inv. 1532) & Egyptian Museum, Cairo (PSI 1292)',
         content='Hebrews 2:14-5:5; 10:8-22; 10:29-11:14; 11:28-12:17',
         book='Hebrews', lat=28.5383, lon=30.6765,
         pages=list(range(10,310,10))),

    dict(docID=10017, id='P17',  name='Papyrus 17',
         date='c. 4th century CE', found='Egypt',
         held='Cambridge University Library (Add. 5893)',
         content='Hebrews 9:12-19', book='Hebrews',
         lat=28.5383, lon=30.6765, pages=list(range(10,50,10))),

    dict(docID=10079, id='P79',  name='Papyrus 79',
         date='c. 7th century CE', found='Egypt',
         held='Staatliche Museen zu Berlin (Papyrus 6774)',
         content='Hebrews 10:10-12; 10:28-30', book='Hebrews',
         lat=28.5383, lon=30.6765, pages=list(range(10,50,10))),

    dict(docID=10089, id='P89',  name='Papyrus 89',
         date='c. 4th century CE', found='Egypt',
         held='Biblioteca Medicea Laurenziana, Florence (PL III/292)',
         content='Hebrews 6:7-9, 15-17', book='Hebrews',
         lat=28.5383, lon=30.6765, pages=list(range(10,50,10))),

    dict(docID=10114, id='P114', name='Papyrus 114',
         date='c. 3rd century CE', found='Oxyrhynchus, Egypt',
         held='Sackler Library, Oxford (P. Oxy. 4498)',
         content='Hebrews 1:7-12', book='Hebrews',
         lat=28.5383, lon=30.6765, pages=list(range(10,50,10))),

    dict(docID=10116, id='P116', name='Papyrus 116',
         date='c. 6th century CE', found='Egypt',
         held='Oesterreichische Nationalbibliothek, Vienna (P. Vindob. G 42417)',
         content='Hebrews 2:9-11; 3:3-6', book='Hebrews',
         lat=28.5383, lon=30.6765, pages=list(range(10,50,10))),

    dict(docID=10126, id='P126', name='Papyrus 126',
         date='c. 4th century CE', found='Egypt',
         held='Instituto Papirologico G. Vitelli, Florence (PSI inv. 2176)',
         content='Hebrews 13:12-13, 19-20', book='Hebrews',
         lat=28.5383, lon=30.6765, pages=list(range(10,50,10))),

    dict(docID=10130, id='P130', name='Papyrus 130',
         date='c. 3rd-4th century CE', found='Egypt',
         held='Museum of the Bible, Washington DC (MOTB.PAP.000401)',
         content='Hebrews 9:9-12, 19-23', book='Hebrews',
         lat=28.5383, lon=30.6765, pages=list(range(10,50,10))),
]

for m in MSS:
    print(f"\nImporting {m['id']}...", flush=True)
    cmd = ['python', S,
           '--docID', str(m['docID']), '--id', m['id'], '--name', m['name'],
           '--genre', 'new-testament', '--date', m['date'],
           '--found', m['found'], '--held', m['held'],
           '--content', m['content'], '--book', m['book'],
           '--lat', str(m['lat']), '--lon', str(m['lon']),
           '--pages', *[str(p) for p in m['pages']]]
    subprocess.run(cmd, cwd=BASE)

print("\n=== DONE ===")
