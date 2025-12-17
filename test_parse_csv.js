// Minimal test for parseCSV/parseCSVLine
function parseCSVLine(line) {
    const values = [];
    let inQuote = false;
    let currentValue = '';

    for (let i = 0; i < line.length; i++) {
        const char = line[i];

        if (char === '"') {
            inQuote = !inQuote;
        } else if (char === ',' && !inQuote) {
            values.push(currentValue);
            currentValue = '';
        } else {
            currentValue += char;
        }
    }

    values.push(currentValue);

    return values.map(val => {
        val = val.trim();
        if (val.startsWith('"') && val.endsWith('"')) {
            val = val.substring(1, val.length - 1);
        }
        return val;
    });
}

function parseCSV(text) {
    const lines = text.replace(/\r\n/g, '\n').split('\n');
    const result = { headers: [], rows: [] };
    if (lines.length === 0) return result;
    result.headers = parseCSVLine(lines[0]);
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim() === '') continue;
        result.rows.push(parseCSVLine(lines[i]));
    }
    return result;
}

const sample = `id,name,notes\n1,Alice,"a, b, and c"\n2,Bob,none\n3,Carol,"line\nbreak"\n`;
console.log('Sample CSV:\n', sample);
console.log('Parsed:', JSON.stringify(parseCSV(sample), null, 2));
