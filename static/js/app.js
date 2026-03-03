document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('startOidc').addEventListener('click', () => startAuth('oidc'));
    document.getElementById('startSaml').addEventListener('click', () => startAuth('saml'));
    document.getElementById('decodeJwtBtn').addEventListener('click', decodeManualJwt);

    function renderResults(data, containerId) {
        const container = document.getElementById(containerId);
        let content = '';

        if (data.type === 'OIDC') {
            content = `
                <div class="row">
                    <div class="col-md-6">
                        <h4>Raw Token</h4>
                        <pre class="bg-dark text-light p-3 rounded" id="raw-token">${data.raw_token}</pre>
                        <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('raw-token')">Copy</button>

                        <h4>Header</h4>
                        <pre class="bg-dark text-light p-3 rounded" id="token-header">${JSON.stringify(data.header, null, 2)}</pre>
                        <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('token-header')">Copy</button>
                    </div>
                    <div class="col-md-6">
                        <h4>Payload</h4>
                        <pre class="bg-dark text-light p-3 rounded" id="token-payload">${JSON.stringify(data.payload, null, 2)}</pre>
                        <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('token-payload')">Copy</button>

                        <h4>Claims</h4>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Claim</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(data.payload).map(([key, value]) => `<tr><td>${key}</td><td>${JSON.stringify(value)}</td></tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } else if (data.type === 'SAML') {
            content = `
                <h4>SAML Assertion</h4>
                <pre class="bg-dark text-light p-3 rounded" id="saml-xml">${data.raw_xml}</pre>
                <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('saml-xml')">Copy</button>
            `;
        }

        container.innerHTML = content;
    }

    async function startAuth(provider) {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('results').innerHTML = '';
        try {
            const res = await fetch(`/${provider}/login`, { credentials: 'include' });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            renderResults(data, 'results');
            console.log('Mock success:', data);
        } catch (err) {
            document.getElementById('results').innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
            console.error('Mock error:', err);
        } finally {
            document.getElementById('loading').style.display = 'none';
        }
    }

    function decodeManualJwt() {
        const token = document.getElementById('manualJwt').value;
        const resultsContainer = document.getElementById('manual-results');
        if (!token) {
            resultsContainer.innerHTML = '<div class="alert alert-warning">Please paste a JWT to decode.</div>';
            return;
        }

        try {
            const [header, payload, signature] = token.split('.');
            const decodedHeader = JSON.parse(atob(header.replace(/_/g, '/').replace(/-/g, '+')));
            const decodedPayload = JSON.parse(atob(payload.replace(/_/g, '/').replace(/-/g, '+')));

            const data = {
                type: 'OIDC',
                raw_token: token,
                header: decodedHeader,
                payload: decodedPayload
            };
            renderResults(data, 'manual-results');
        } catch (e) {
            resultsContainer.innerHTML = '<div class="alert alert-danger">Invalid JWT format.</div>';
        }
    }
});

function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(text);
}
