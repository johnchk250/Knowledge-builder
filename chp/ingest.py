"""Local parsing. Originals and extracted evidence are immutable once registered."""
import csv
import hashlib
import io
import json
import os
import zipfile
from pathlib import Path
from .store import uid, now, dumps

SUPPORTED = {'.txt','.md','.csv','.tsv','.pdf','.xlsx','.png','.jpg','.jpeg'}
MAX_BYTES = 40 * 1024 * 1024
CHUNK = 6000



def decode_broken_cmap_text(text):
    if not text:
        return text
    # 1. Decode Windows Symbol / Private Use Area (0xF000-0xF0FF) shifted characters
    if any(0xF000 <= ord(c) <= 0xF0FF for c in text):
        out = []
        for c in text:
            code = ord(c)
            if 0xF080 <= code <= 0xF0FF and 32 <= (code - 0xF080) <= 126:
                out.append(chr(code - 0xF080))
            elif 0xF020 <= code <= 0xF07E:
                out.append(chr(code - 0xF000))
            else:
                out.append(c)
        text = "".join(out)
    # 2. Decode +29 ASCII ToUnicode CMap shift if high density of shifted uppercase tokens is present
    if "%220" in text or "+81$1" in text or "72 5$,/" in text:
        lines = []
        for line in text.splitlines():
            non_ws = [c for c in line if not c.isspace()]
            if non_ws and sum(32 <= ord(c) <= 68 for c in non_ws) / len(non_ws) > 0.65:
                lines.append("".join(chr(ord(c) + 29) if 32 <= ord(c) <= 93 else (" " if c == "\x03" else c) for c in line))
            else:
                lines.append(line)
        text = "\n".join(lines)
    return text


def chunks(text):
    if not text: return ['']
    result=[]
    while text:
        cut=min(len(text),CHUNK)
        if len(text)>CHUNK:
            end=text.rfind('\n',CHUNK//2,CHUNK)
            if end>0: cut=end+1
        result.append(text[:cut]); text=text[cut:]
    return result


def save_bytes(path, content):
    path=Path(path)
    if path.exists():
        if path.read_bytes()!=content: raise ValueError('Immutable file hash collision or storage corruption')
        return
    temp=path.with_suffix('.'+uid('tmp'))
    try:
        with open(temp,'xb') as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.chmod(temp,0o600)
        os.replace(temp,path)
    finally:
        temp.unlink(missing_ok=True)


def ingest(store, name, content, revision='', authority='Unclassified'):
    name=name.replace('\\','/').split('/')[-1]
    ext=Path(name).suffix.lower()
    if ext not in SUPPORTED: raise ValueError('Supported: PDF, TXT, MD, CSV, TSV, XLSX, PNG and JPEG. Export other formats first.')
    if not content or len(content)>MAX_BYTES: raise ValueError('File must contain data and be at most 40 MB.')
    if len(name)>200 or len(revision)>120 or len(authority)>120: raise ValueError('Source metadata is too long')
    sha=hashlib.sha256(content).hexdigest()
    found=store.rows('SELECT * FROM documents WHERE sha256=?',(sha,))
    if found: return {'document':found[0], 'duplicate':True}
    doc_id=uid('doc')
    segments=[]
    warnings=[]
    def add(page, locator, text, image=None, metadata=None):
        for n,part in enumerate(chunks(text)):
            segments.append({'id':uid('ev'),'page':page,'locator':locator+(f' · text block {n+1}' if len(text)>CHUNK else ''),'text':part,'image':image,'metadata':metadata or {}})
    if ext in ('.txt','.md'):
        try: text=content.decode('utf-8-sig')
        except UnicodeDecodeError: raise ValueError('Text files must use UTF-8 encoding; re-save the source as UTF-8.')
        add(1,'Text',text,metadata={'parser':'utf-8/1'})
    elif ext in ('.csv','.tsv'):
        try: text=content.decode('utf-8-sig')
        except UnicodeDecodeError: raise ValueError('CSV/TSV must use UTF-8 encoding.')
        # Retain exact cell strings and row locations; never evaluate spreadsheet expressions.
        rows=list(csv.reader(io.StringIO(text),delimiter='\t' if ext=='.tsv' else ','))
        for start in range(0,len(rows),40):
            add(1,f'Rows {start+1}–{min(start+40,len(rows))}', '\n'.join(f'Row {i+1}: '+dumps(row) for i,row in enumerate(rows[start:start+40],start)),metadata={'parser':'csv/2','table_header_candidate':rows[0] if rows else [],'table_rows':[{'row':i+1,'cells':row} for i,row in enumerate(rows[start:start+40],start)]})
    elif ext=='.xlsx':
        try: import openpyxl
        except ImportError: raise ValueError('XLSX support needs optional dependencies: run python -m pip install -r requirements.txt')
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            if len(z.infolist())>10000 or sum(x.file_size for x in z.infolist())>80*1024*1024:
                raise ValueError('Expanded spreadsheet exceeds the 80 MB parsing limit.')
        book=openpyxl.load_workbook(io.BytesIO(content),read_only=True,data_only=False,keep_links=False)
        try:
            for index,sheet in enumerate(book.worksheets,1):
                if (sheet.max_row or 0)>100000 or (sheet.max_column or 0)>500:
                    raise ValueError('Sheet exceeds 100,000 rows or 500 columns; export a smaller range.')
                buf=[]; table_rows=[]; header=None; start=1
                for rowno,row in enumerate(sheet.iter_rows(values_only=True),1):
                    if any(c is not None for c in row):
                        cells=[str(c) if c is not None else None for c in row]
                        if header is None: header=cells
                        buf.append(f'Row {rowno}: '+dumps(cells))
                        table_rows.append({'row':rowno,'cells':cells})
                    if rowno%30==0:
                        if buf: add(index,f'{sheet.title} · rows {start}–{rowno}','\n'.join(buf),metadata={'sheet':sheet.title,'parser':'openpyxl/'+openpyxl.__version__,'table_header_candidate':header,'table_rows':table_rows})
                        buf=[]; table_rows=[]; start=rowno+1
                if buf: add(index,f'{sheet.title} · rows {start}–{rowno}','\n'.join(buf),metadata={'sheet':sheet.title,'parser':'openpyxl/'+openpyxl.__version__,'table_header_candidate':header,'table_rows':table_rows})
        finally: book.close()
        warnings.append('Formula expressions are preserved as text; formulas are not calculated. Embedded drawings and charts are not extracted from XLSX.')
    else:
        try:
            import fitz
            has_fitz = True
        except ImportError:
            has_fitz = False
        if has_fitz:
            with fitz.open(stream=content,filetype=ext.lstrip('.')) as document:
                if document.needs_pass: raise ValueError('Encrypted PDF: provide a decrypted copy.')
                if len(document)>200: raise ValueError('This first version accepts at most 200 pages per document; split the file into related sections.')
                for index,page in enumerate(document,1):
                    scale=min(2.0,1600/max(page.rect.width,page.rect.height))
                    pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
                    png=pix.tobytes('png')
                    image=hashlib.sha256(png).hexdigest()+'.png'
                    save_bytes(store.root/'renders'/image,png)
                    text=decode_broken_cmap_text(page.get_text('text',sort=True)) if ext=='.pdf' else ''
                    metadata={'parser':'PyMuPDF/'+fitz.VersionBind,'width':page.rect.width,'height':page.rect.height,'render_width':pix.width,'render_height':pix.height,'render_sha256':hashlib.sha256(png).hexdigest()}
                    if ext=='.pdf' and text.strip() and hasattr(page,'find_tables'):
                        try:
                            tables=[]
                            for table in page.find_tables().tables:
                                rows=table.extract()
                                if rows:
                                    x0,y0,x1,y1=table.bbox
                                    tables.append({'region':[x0/page.rect.width,y0/page.rect.height,x1/page.rect.width,y1/page.rect.height],'rows':rows})
                            if tables: metadata['table_candidates']=tables
                        except Exception as exc:
                            warnings.append(f'Page {index}: table detection unavailable ({type(exc).__name__}); inspect text and page image.')
                    add(index,f'Page {index}',text,image,metadata)
                    if not text.strip(): warnings.append(f'Page {index} has no selectable text; enable vision to analyze it.')
        elif ext == '.pdf':
            try:
                import pypdfium2 as pdfium
                import pypdf
            except ImportError:
                raise ValueError('PDF/image support needs optional dependencies: run python -m pip install -r requirements.txt')
            reader = pypdf.PdfReader(io.BytesIO(content))
            if reader.is_encrypted: raise ValueError('Encrypted PDF: provide a decrypted copy.')
            pdf_doc = pdfium.PdfDocument(content)
            if len(pdf_doc)>200: raise ValueError('This first version accepts at most 200 pages per document; split the file into related sections.')
            for index in range(1, len(pdf_doc)+1):
                page = pdf_doc[index-1]
                w, h = page.get_size()
                scale = min(2.0, 1600 / max(w, h))
                bitmap = page.render(scale=scale)
                pil_img = bitmap.to_pil()
                buf = io.BytesIO()
                pil_img.save(buf, format='PNG')
                png = buf.getvalue()
                image = hashlib.sha256(png).hexdigest()+'.png'
                save_bytes(store.root/'renders'/image, png)
                raw_txt = reader.pages[index-1].extract_text() or ''
                text = decode_broken_cmap_text(raw_txt)
                metadata = {'parser':'pypdfium2+pypdf','width':w,'height':h,'render_width':pil_img.width,'render_height':pil_img.height,'render_sha256':hashlib.sha256(png).hexdigest()}
                add(index, f'Page {index}', text, image, metadata)
                if not text.strip(): warnings.append(f'Page {index} has no selectable text; enable vision to analyze it.')
        else:
            try:
                from PIL import Image
            except ImportError:
                raise ValueError('PDF/image support needs optional dependencies: run python -m pip install -r requirements.txt')
            pil_img = Image.open(io.BytesIO(content)).convert('RGB')
            w, h = pil_img.size
            buf = io.BytesIO()
            pil_img.save(buf, format='PNG')
            png = buf.getvalue()
            image = hashlib.sha256(png).hexdigest()+'.png'
            save_bytes(store.root/'renders'/image, png)
            metadata = {'parser':'Pillow','width':w,'height':h,'render_width':w,'render_height':h,'render_sha256':hashlib.sha256(png).hexdigest()}
            add(1, 'Page 1', '', image, metadata)
            warnings.append('Page 1 has no selectable text; enable vision to analyze it.')
        warnings.append('Full-page vision is available. Dense or large-format drawing details may require separately uploaded crops; local OCR and automatic drawing tiling are not included.')
    if not segments: raise ValueError('No readable evidence was found in this file.')
    if len(segments)>300: raise ValueError('Document exceeds 300 evidence blocks; split into smaller related documents.')
    save_bytes(store.root/'originals'/sha,content)
    media={'.pdf':'application/pdf','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg'}.get(ext,'application/octet-stream')
    with store.transaction() as db:
        # Two simultaneous identical uploads must return the existing document.
        found=store.rows('SELECT * FROM documents WHERE sha256=?',(sha,),db)
        if found: return {'document':found[0],'duplicate':True}
        db.execute('INSERT INTO documents VALUES(?,?,?,?,?,?,?,?,?)',(doc_id,sha,name,media,revision,authority,now(),len(content),dumps(warnings)))
        for e in segments:
            digest=hashlib.sha256(dumps([e['text'],e['page'],e['locator'],e['image'],e['metadata']]).encode()).hexdigest()
            db.execute('INSERT INTO evidence VALUES(?,?,?,?,?,?,?,?)',(e['id'],doc_id,e['page'],e['locator'],e['text'],e['image'],digest,dumps(e['metadata'])))
    return {'document':store.rows('SELECT * FROM documents WHERE id=?',(doc_id,))[0],'duplicate':False}
