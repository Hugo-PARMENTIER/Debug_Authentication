document.addEventListener('DOMContentLoaded', () => {
   document.getElementById('startOidc').addEventListener('click', () => startAuth('oidc'));
   document.getElementById('startSaml').addEventListener('click', () => startAuth('saml'));
 })
 
 async function startAuth(provider) {
   document.getElementById('loading').style.display = 'block';
   document.getElementById('results').innerHTML = '';
   try {
     const res = await fetch(`/${provider}/login`, { credentials: 'include' });
     if (!res.ok) throw new Error(`HTTP ${res.status}`);
     const data = await res.json();
     document.getElementById('results').innerHTML = `
       <div class="alert alert-success">Mock ${provider.toUpperCase()} OK !</div>
       <pre>${JSON.stringify(data, null, 2)}</pre>
     `;
     console.log('Mock success:', data);
   } catch (err) {
     document.getElementById('results').innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
     console.error('Mock error:', err);
   } finally {
     document.getElementById('loading').style.display = 'none';
   }
 }
