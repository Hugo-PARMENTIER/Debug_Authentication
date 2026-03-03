document.addEventListener('DOMContentLoaded', () => {
    const resultsContainer = document.getElementById('results');
    const loadingContainer = document.getElementById('loading');
    const startOidcBtn = document.getElementById('startOidc');
    if (startOidcBtn) {
        startOidcBtn.addEventListener('click', () => startFlow('/oidc/login'));
    }

    const startSamlBtn = document.getElementById('startSaml');
    if (startSamlBtn) {
        startSamlBtn.addEventListener('click', () => startFlow('/saml/login'));
    }

    async function startFlow(url) {
        loadingContainer.style.display = 'block';
        resultsContainer.innerHTML = '';

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }
            
            renderResults(data);

        } catch (error) {
            renderResults({type: 'error', message: 'Failed to initiate login: ' + error.message});
        } finally {
            loadingContainer.style.display = 'none';
        }
    }

    function renderResults(data) {
        if (!data || !data.type) {
            resultsContainer.innerHTML = `<div class="alert alert-danger">Invalid data received.</div>`;
            return;
        }

        if (data.type === 'error') {
            resultsContainer.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
            return;
        }

        if (data.type === 'OIDC') {
            resultsContainer.innerHTML = `
                <h3>OIDC Results</h3>
                <pre><code class="json">${JSON.stringify(data.payload, null, 2)}</code></pre>
            `;
        } else if (data.type === 'SAML') {
            resultsContainer.innerHTML = `
                <h3>SAML Results</h3>
                <pre><code class="xml">${data.raw_xml}</code></pre>
            `;
        }
        document.querySelectorAll('pre code').forEach((el) => {
            hljs.highlightElement(el);
        });
    }
});
