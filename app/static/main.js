setInterval(() => {

fetch("/api/tarjetas")
.then(res => res.json())
.then(data => {

let tabla = document.querySelector("#tabla tbody")

tabla.innerHTML = ""

data.forEach(t => {

tabla.innerHTML += `
<tr>
<td>${t.id}</td>
<td>${t.uid}</td>
<td>${t.fecha}</td>
</tr>
`

})

})

},2000)