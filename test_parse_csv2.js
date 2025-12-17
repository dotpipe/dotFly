// Minimal test for parseCSV implementation (version 2)
function parseCSV(text) {
    const rows = [];
    let cur = '';
    let curRow = [];
    let inQuote = false;

    for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        if (ch === '"') {
            if (inQuote && text[i + 1] === '"') { cur += '"'; i++; continue; }
            inQuote = !inQuote;
            continue;
        }
        if (ch === ',' && !inQuote) { curRow.push(cur); cur = ''; continue; }
        if ((ch === '\n' || ch === '\r') && !inQuote) {
            if (ch === '\r' && text[i + 1] === '\n') { curRow.push(cur); rows.push(curRow); curRow = []; cur = ''; i++; continue; }
            curRow.push(cur); rows.push(curRow); curRow = []; cur = ''; continue;
        }
        cur += ch;
    }
    if (cur !== '' || curRow.length > 0) { curRow.push(cur); rows.push(curRow); }

    const cleaned = rows.map(r => r.map(v => {
        v = String(v || '').trim();
        if (v.startsWith('"') && v.endsWith('"')) v = v.substring(1, v.length - 1).replace(/""/g, '"');
        return v;
    }));

    const result = { headers: [], rows: [] };
    if (cleaned.length === 0) return result;
    result.headers = cleaned[0];
    result.rows = cleaned.slice(1).filter(r => r.some(c => c !== ''));
    return result;
}

const sample = `id,name,notes\n1,Alice,"a, b, and c"\n2,Bob,none\n3,Carol,"line\nbreak"\n`;
console.log('Sample CSV:\n', sample);
console.log('Parsed:', JSON.stringify(parseCSV(sample), null, 2));
