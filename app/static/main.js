// periodically refresh table
function updateCards(data) {
    const container = document.getElementById('cards-container')
    if (!container) return
    container.innerHTML = ''
    data.forEach(t => {
        container.innerHTML += `<div class="card">
<h3>${t.uid}</h3>
<p><strong>ID:</strong> ${t.id}</p>
<p><strong>Propietario:</strong> ${t.owner || '-'}</p>
<p><strong>Accesos:</strong> ${t.access || '-'}</p>
<p><strong>Registrado:</strong> ${t.registered_at || '-'}</p>
</div>`
    })
}

function updateTable() {
    fetch("/api/tarjetas")
    .then(res => res.json())
    .then(data => {
        const filter = document.getElementById('search-input')?.value.toLowerCase() || ''
        let filtered = data
        if (filter) {
            filtered = data.filter(t =>
                (t.uid && t.uid.toLowerCase().includes(filter)) ||
                (t.owner && t.owner.toLowerCase().includes(filter))
            )
        }

        let tabla = document.querySelector("#tabla tbody")
        tabla.innerHTML = ""
        filtered.forEach(t => {
            tabla.innerHTML += `
<tr>
<td>${t.id}</td>
<td>${t.uid}</td>
<td>${t.owner || ''}</td>
<td>${t.access || ''}</td>
<td>${t.registered_at || ''}</td>
<td>${t.fecha}</td>
</tr>
`
        })
        updateCards(filtered)
    })
}

setInterval(updateTable, 2000)
// periodically check for new UID and fill input if on alta page
function checkLastUid() {
    fetch('/api/last-uid')
    .then(r => r.json())
    .then(data => {
        if (data.uid) {
            updateLastUid(data.uid, data.id)
            // if on alta page, fill the UID input automatically
            const input = document.getElementById('uid')
            if (input && !input.value) {
                input.value = data.uid
            }
        }
    })
    .catch(() => {})
}
setInterval(checkLastUid, 1000)  // check every second

// manage last UID display
function updateLastUid(uid, id) {
    const div = document.getElementById('last-uid')
    if (div) div.textContent = id ? `Último ID: ${id} (UID ${uid})` : 'Último UID: ' + uid
}

// generic scan helper
function performScan(callback) {
    fetch('/api/scan', { method: 'POST' })
    .then(r => r.json())
    .then(resp => {
        if (resp.success) {
            updateLastUid(resp.uid, resp.id)
            if (callback) callback(resp.uid, resp.id)
        } else {
            if (callback) callback(null, null, resp.message)
        }
    })
    .catch(err => {
        if (callback) callback(null, null, 'error')
    })
}

// scan button on readings page
const btn = document.getElementById('btn-scan')
if (btn) {
    btn.addEventListener('click', () => {
        performScan()
    })
}

// scan button on alta page: fill and submit
const btnAlta = document.getElementById('btn-scan-alta')
if (btnAlta) {
    btnAlta.addEventListener('click', () => {
        performScan((uid, err) => {
            if (uid) {
                const input = document.getElementById('uid')
                if (input) input.value = uid
                const form = document.querySelector('.config-form')
                if (form) form.submit()
            } else {
                alert(err || 'Error al leer tarjeta')
            }
        })
    })
}