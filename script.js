const API = "http://localhost:5000/api";

function addQuestion() {
  const container = document.getElementById("questions");
  const input = document.createElement("input");
  input.placeholder = "Question text";
  input.className = "question";
  container.appendChild(input);
  container.appendChild(document.createElement("br"));
}

async function saveForm() {
  const title = document.getElementById("formTitle").value;
  const questions = [...document.getElementsByClassName("question")].map(q => q.value);
  const id = Date.now().toString(); // simple unique ID
  await fetch(`${API}/forms`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, title, questions })
  });
  alert(`Form created! Share this link: form.html?form_id=${id}`);
}

// Load form for students
async function loadForm() {
  const params = new URLSearchParams(window.location.search);
  const formId = params.get("form_id");
  if (!formId) return;
  const res = await fetch(`${API}/forms/${formId}`);
  const form = await res.json();

  document.getElementById("formTitle").innerText = form.title;
  const formEl = document.getElementById("responseForm");
  form.questions.forEach(q => {
    const input = document.createElement("input");
    input.placeholder = q;
    input.className = "answer";
    formEl.appendChild(input);
    formEl.appendChild(document.createElement("br"));
  });
  window.formId = formId;
}

async function submitResponse() {
  const answers = [...document.getElementsByClassName("answer")].map(a => a.value);
  await fetch(`${API}/forms/${window.formId}/responses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers })
  });
  alert("Response submitted!");
}

// Load responses
async function loadResponses() {
  const params = new URLSearchParams(window.location.search);
  const formId = params.get("form_id");
  if (!formId) return;
  const res = await fetch(`${API}/forms/${formId}/responses`);
  const data = await res.json();
  const div = document.getElementById("responses");
  div.innerHTML = data.map(r => `<p>${r.join(" | ")}</p>`).join("");

  document.getElementById("excelLink").href = `${API}/forms/${formId}/export/excel`;
  document.getElementById("pdfLink").href = `${API}/forms/${formId}/export/pdf`;
}

// Auto run based on page
if (document.body.contains(document.getElementById("responseForm"))) loadForm();
if (document.body.contains(document.getElementById("responses"))) loadResponses();
