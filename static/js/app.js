document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('startOidc').addEventListener('click', () => startAuth('oidc'));
    document.getElementById('startSaml').addEventListener('click', () => startAuth('saml'));
});

function displayResults(data) {
    const resultsContainer = document.getElementById('results');
    let content = '';

    if (data.type === 'OIDC') {
        content = `
            <div class="row">
                <div class="col-md-4">
                    <h5>Raw Token</h5>
                    <pre class="bg-dark text-light p-2 rounded" id="raw-token">${data.raw_token}</pre>
                    <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('raw-token')">Copy</button>
                </div>
                <div class="col-md-4">
                    <h5>Payload</h5>
                    <pre class="bg-dark text-light p-2 rounded" id="token-payload">${JSON.stringify(data.payload, null, 2)}</pre>
                    <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('token-payload')">Copy</button>
                </div>
                <div class="col-md-4">
                    <h5>Claims</h5>
                    <table class="table table-sm table-striped">
                        <tbody>
                            ${Object.entries(data.payload).map(([key, value]) => `<tr><td>${key}</td><td>${JSON.stringify(value)}</td></tr>`).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    } else if (data.type === 'SAML') {
        content = `
            <div class="row">
                <div class="col-md-4">
                    <h5>Raw XML</h5>
                    <pre class="bg-dark text-light p-2 rounded" id="saml-xml">${data.raw_xml}</pre>
                    <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('saml-xml')">Copy</button>
                </div>
                <div class="col-md-4">
                    <h5>Parsed Attributes</h5>
                    <pre class="bg-dark text-light p-2 rounded">${JSON.stringify(data.parsed_data.attributes, null, 2)}</pre>
                </div>
                <div class="col-md-4">
                    <h5>Conditions</h5>
                    <pre class="bg-dark text-light p-2 rounded">${JSON.stringify(data.parsed_data.conditions, null, 2)}</pre>
                </div>
            </div>
        `;
    }
    resultsContainer.innerHTML = content;
}

async function startAuth(provider) {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').innerHTML = '';
    try {
        const res = await fetch(`/${provider}/login`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        displayResults(data);
        console.log('Mock success:', data);
    } catch (err) {
        document.getElementById('results').innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
        console.error('Mock error:', err);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

async function decodeJwt() {
    const token = document.getElementById('jwt-input').value.trim();
    if (!token) return alert('Veuillez entrer un token');
    document.getElementById('loading').style.display = 'block';
    const resultsContainer = document.getElementById('manual-results');
    resultsContainer.innerHTML = '';
    try {
        const res = await fetch('/decode-jwt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token })
        });
        if (!res.ok) throw new Error(`Erreur ${res.status}`);
        const data = await res.json();
        displayResults(data); // Re-use the same display function
        console.log('Décodage manuel OK:', data);
    } catch (err) {
        resultsContainer.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
        console.error('Erreur décodage:', err);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(text);
}
