const days = [
  ["Sunday", "July 26"], ["Monday", "July 27"], ["Tuesday", "July 28"],
  ["Wednesday", "July 29"], ["Thursday", "July 30"], ["Friday", "July 31"]
];

const state = days.map(([day, date]) => ({
  day, date, available: false, roles: [], ship: "", nol: false, standby: false, credit: false
}));
let activeDay = 0;

const compatibleNol = new Set([
  "Carrack: Balance", "Carrack: Advance", "Carrack: Valor", "Carrack: Volante", "Panokseon"
]);

function renderWeek() {
  const grid = document.querySelector("#week-grid");
  grid.innerHTML = state.map((entry, index) => {
    const details = entry.available
      ? `<strong>${entry.roles.join(" → ") || "Choose roles"}</strong>${entry.ship || "No ship selected"}${entry.standby ? " · Standby OK" : ""}`
      : "Mark available and choose your acceptable roles.";
    return `<article class="day-card ${entry.available ? "available" : ""}" data-day="${index}" tabindex="0">
      <div class="day-card-header"><div><h3>${entry.day}</h3><span class="date">${entry.date}</span></div>
      <span class="availability-pill">${entry.available ? "AVAILABLE" : "NOT SET"}</span></div>
      <div class="day-details">${details}</div>
      <span class="day-action">${entry.available ? "Edit preferences →" : "Add availability +"}</span>
    </article>`;
  }).join("");
  grid.querySelectorAll(".day-card").forEach(card => {
    card.addEventListener("click", () => openDay(Number(card.dataset.day)));
    card.addEventListener("keydown", event => { if (event.key === "Enter") openDay(Number(card.dataset.day)); });
  });
  document.querySelector("#available-count").textContent = state.filter(x => x.available).length;
  document.querySelector("#standby-count").textContent = state.filter(x => x.available && x.standby).length;
  updateSubmit();
}

function openDay(index) {
  activeDay = index;
  const entry = state[index];
  document.querySelector("#dialog-title").textContent = `${entry.day}, ${entry.date}`;
  document.querySelectorAll('input[name="role"]').forEach(input => input.checked = entry.roles.includes(input.value));
  document.querySelector("#ship-select").value = entry.ship;
  document.querySelector("#nol-check").checked = entry.nol;
  document.querySelector("#standby-check").checked = entry.standby;
  document.querySelector("#credit-check").checked = entry.credit;
  toggleShipFields();
  document.querySelector("#day-dialog").showModal();
}

function toggleShipFields() {
  const shipChosen = [...document.querySelectorAll('input[name="role"]:checked')].some(input => input.value === "Ship");
  const fields = document.querySelector("#ship-fields");
  fields.hidden = !shipChosen;
  const selectedShip = document.querySelector("#ship-select").value;
  const nol = document.querySelector("#nol-check");
  const supportsNol = compatibleNol.has(selectedShip);
  nol.disabled = !supportsNol;
  if (!supportsNol) nol.checked = false;
  document.querySelector("#nol-help").textContent = selectedShip && !supportsNol
    ? "This ship is eligible, but does not currently support a NOL option."
    : "NOL is optional and provides no selection priority.";
}

function saveDay(event) {
  event.preventDefault();
  const roles = [...document.querySelectorAll('input[name="role"]:checked')].map(input => input.value);
  if (!roles.length) return showToast("Choose at least one role.");
  const ship = document.querySelector("#ship-select").value;
  if (roles.includes("Ship") && !ship) return showToast("Choose an eligible ship.");
  state[activeDay] = {
    ...state[activeDay], available: true, roles,
    ship: roles.includes("Ship") ? ship : "",
    nol: roles.includes("Ship") && document.querySelector("#nol-check").checked,
    standby: document.querySelector("#standby-check").checked,
    credit: document.querySelector("#credit-check").checked
  };
  document.querySelector("#day-dialog").close();
  renderWeek();
}

function removeDay(event) {
  event.preventDefault();
  state[activeDay] = { ...state[activeDay], available: false, roles: [], ship: "", nol: false, standby: false, credit: false };
  document.querySelector("#day-dialog").close();
  renderWeek();
}

function updateSubmit() {
  document.querySelector("#submit-week").disabled =
    !document.querySelector("#commitment").checked || !state.some(x => x.available);
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("show"), 2600);
}

function renderRoster() {
  const galley = [
    ["AS", "Aster", "Driver"], ["BR", "BroDogs", "Cannon"], ["CY", "Cyrus", "Cannon"],
    ["EZ", "Ezra", "Cannon"], ["KT", "Kitteh", "Cannon"], ["MN", "Moon", "Cannon"],
    ["NJ", "Ninjago", "Cannon"], ["OR", "Oruun", "Cannon"]
  ];
  const ships = [
    ["CE", "Christopher", "Carrack: Advance · NOL"], ["AK", "Akari", "Panokseon"],
    ["BL", "Bluejay", "Epheria Star"], ["DR", "Draxis", "Carrack: Valor"],
    ["EL", "Elara", "Epheria Galleass"], ["FS", "Frost", "Carrack: Volante · NOL"],
    ["GR", "Grey", "Carrack: Balance"], ["HX", "Hex", "Epheria Caravel"],
    ["IV", "Ivy", "Improved Frigate"], ["JR", "Jora", "Carrack: Advance"],
    ["KA", "Kade", "Panokseon · NOL"], ["LU", "Lumen", "Improved Sailboat"]
  ];
  const row = ([initials, name, role]) => `<div class="roster-row"><span class="avatar">${initials}</span><span><strong>${name}</strong><small>${role}</small></span><span class="role-tag">Scheduled</span></div>`;
  document.querySelector("#galley-list").innerHTML = galley.map(row).join("");
  document.querySelector("#ship-list").innerHTML = ships.map(row).join("");
  document.querySelector("#published-standbys").innerHTML = [
    ["1", "Sable", "Ship"], ["2", "Vesper", "Cannon / Ship"], ["3", "Rune", "Driver / Cannon"]
  ].map(([n, name, roles]) => `<span class="standby-chip"><strong>#${n}</strong> ${name} · ${roles}</span>`).join("");
}

function renderCoverage() {
  const coverage = [
    ["Sun", 7, 1, 12], ["Mon", 7, 1, 12], ["Tue", 7, 1, 11],
    ["Wed", 7, 1, 12], ["Thu", 6, 1, 12], ["Fri", 7, 0, 12]
  ];
  const cell = (value, max) => `<div class="coverage-cell"><strong>${value}/${max}</strong><div class="coverage-bar"><i style="width:${value/max*100}%"></i></div></div>`;
  document.querySelector("#coverage-table").innerHTML = coverage.map(([day,cannon,driver,ship]) => {
    const total = cannon + driver + ship;
    return `<div class="coverage-row"><strong>${day}</strong>${cell(cannon,7)}${cell(driver,1)}${cell(ship,12)}
      <span class="${total === 20 ? "ready" : "warning"}">${total === 20 ? "Ready" : `${20-total} open`}</span></div>`;
  }).join("");
}

document.querySelectorAll(".nav-item").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll(".nav-item, .view").forEach(node => node.classList.remove("active"));
  button.classList.add("active");
  document.querySelector(`#${button.dataset.view}`).classList.add("active");
  const titles = { availability: "Plan your BBF week", roster: "Published roster", fairness: "My fairness", dashboard: "Weekly readiness" };
  document.querySelector("#page-title").textContent = titles[button.dataset.view];
}));
document.querySelectorAll('input[name="role"]').forEach(input => input.addEventListener("change", toggleShipFields));
document.querySelector("#ship-select").addEventListener("change", toggleShipFields);
document.querySelector("#save-day").addEventListener("click", saveDay);
document.querySelector("#remove-date").addEventListener("click", removeDay);
document.querySelector("#commitment").addEventListener("change", updateSubmit);
document.querySelector("#submit-week").addEventListener("click", () => showToast("Weekly availability submitted. Your signup time will not affect priority."));
document.querySelector("#copy-week").addEventListener("click", () => showToast("Last week’s preferences copied as a draft."));

renderWeek();
renderRoster();
renderCoverage();
