/* global $ */
const API = {
  stations: "/fuel_stations",
  prices: "/fuel_prices",
  calculations: "/fuel_calculations"
};

const state = {
  stations: [],
  prices: [],
  recentPrices: [],
  averages: { all: [], petrol: [], diesel: [], lpg: [] },
  currentAverage: "all",
  authenticated: false,
  username: null
};

$(document).ready(function () {
  bindEvents();
  checkAuthStatus();
  loadInitialData();
});

function bindEvents() {
  $("#searchBtn").on("click", applyGlobalSearch);
  $("#globalSearch").on("keyup", function (event) {
    if (event.key === "Enter") applyGlobalSearch();
    if ($(this).val().trim() === "") clearSearchOnly();
  });
  $("#resetBtn").on("click", resetDashboard);
  $("#clearBtn").on("click", clearAllFormsAndTables);
  $("#clearLogBtn").on("click", () => $("#activityLog").text("Activity log cleared."));

  $("#refreshStationsBtn").on("click", refreshStations);
  $("#refreshPricesBtn, #loadAllPricesBtn").on("click", refreshPrices);
  $("#loginBtn").on("click", login);
  $("#signupBtn").on("click", signup);
  $("#logoutBtn").on("click", logout);
  $("#authPassword").on("keyup", function (event) { if (event.key === "Enter") login(); });
  $("#loadAveragesBtn").on("click", loadAllAverages);

  $("#stationForm").on("submit", saveStation);
  $("#priceForm").on("submit", savePrice);
  $("#localityDateForm").on("submit", findPricesByLocalityAndDate);
  $("#cheapestForm").on("submit", loadCheapestFuel);

  $("#newStationBtn").on("click", clearStationForm);
  $("#newPriceBtn").on("click", clearPriceForm);

  $(".tab").on("click", function () {
    state.currentAverage = $(this).data("average");
    $(".tab").removeClass("active");
    $(this).addClass("active");
    renderAveragesTable();
  });

  $(document).on("click", ".edit-station", function () { fillStationForm($(this).data("id")); });
  $(document).on("click", ".delete-station", function () { deleteStation($(this).data("id")); });
  $(document).on("click", ".edit-price", function () { fillPriceForm($(this).data("id")); });
  $(document).on("click", ".delete-price", function () { deletePrice($(this).data("id")); });
}

function checkAuthStatus() {
  return $.getJSON("/me").done(function (data) {
    state.authenticated = Boolean(data.authenticated);
    state.username = data.username || null;
    updateAuthUI();
  }).fail(function () {
    state.authenticated = false;
    state.username = null;
    updateAuthUI();
  });
}

function login() {
  const username = $("#authUsername").val().trim();
  const password = $("#authPassword").val();
  if (!username || !password) {
    showToast("Enter username and password", "error");
    return;
  }
  return ajaxRequest({
    url: "/login",
    method: "POST",
    data: JSON.stringify({ username, password })
  }).done(function (data) {
    state.authenticated = true;
    state.username = data.username || username;
    $("#authPassword").val("");
    updateAuthUI();
    showToast("Logged in", "success");
  });
}

function signup() {
  const username = $("#authUsername").val().trim();
  const password = $("#authPassword").val();
  if (!username || !password) {
    showToast("Enter username and password", "error");
    return;
  }
  return ajaxRequest({
    url: "/signup",
    method: "POST",
    data: JSON.stringify({ username, password })
  }).done(function (data) {
    state.authenticated = true;
    state.username = data.username || username;
    $("#authPassword").val("");
    updateAuthUI();
    showToast("Account created and signed in", "success");
  });
}

function logout() {
  return ajaxRequest({ url: "/logout", method: "POST" }).always(function () {
    state.authenticated = false;
    state.username = null;
    updateAuthUI();
    showToast("Logged out", "success");
  });
}

function updateAuthUI() {
  if (state.authenticated) {
    $("#loginBtn,#signupBtn,#authUsername,#authPassword").hide();
    $("#logoutBtn").show();
    $("#authStatus").text("Signed in as " + state.username);
  } else {
    $("#loginBtn,#signupBtn,#authUsername,#authPassword").show();
    $("#logoutBtn").hide();
    $("#authStatus").text("Read-only mode");
  }

  $("#stationForm input,#priceForm input,#priceForm select").prop("disabled", !state.authenticated);
  $("#stationForm,#priceForm").toggleClass("auth-disabled", !state.authenticated);
  $("#stationForm button,#priceForm button,.edit-station,.delete-station,.edit-price,.delete-price").prop("disabled", !state.authenticated);
}

function requireLogin() {
  if (!state.authenticated) {
    showToast("Please log in to make changes", "error");
    return false;
  }
  return true;
}

function refreshStations() {
  return loadStations().then(function () {
    state.recentPrices = state.prices.map(function (price) {
      return {
        name: stationName(price.station_id),
        locality: stationLocality(price.station_id),
        petrol_95: price.petrol_95,
        diesel: price.diesel,
        lpg: price.lpg,
        price_date: price.price_date,
        station_id: price.station_id,
        id: price.id
      };
    });
    renderPrices();
    renderRecentPrices(state.recentPrices, "Stations refreshed. Price station names updated.");
    showToast("Fuel stations refreshed", "success");
  });
}

function refreshPrices() {
  return loadStations().then(function () {
    return loadPrices();
  }).done(function () {
    showToast("Fuel prices refreshed", "success");
  });
}

function loadInitialData() {
  setTodayDefaults();

  // Load stations first so fuel price rows can resolve station_id to real station names.
  // Previously these calls ran in parallel, so prices sometimes rendered before stations existed
  // in state.stations, causing fallback labels such as "Station #1".
  return loadStations()
    .then(function () {
      return $.when(loadPrices(), loadAllAverages());
    })
    .always(function () {
      setStatus("API ready");
    });
}

function ajaxRequest(options) {
  setStatus("Calling API...");
  return $.ajax({
    url: options.url,
    method: options.method || "GET",
    data: options.data || undefined,
    contentType: options.contentType || "application/json",
    dataType: "json"
  }).done(function (response) {
    logActivity(options.method || "GET", options.url, response);
    setStatus("API ready");
  }).fail(function (xhr) {
    const message = xhr.responseJSON?.error || xhr.statusText || "API request failed";
    logActivity(options.method || "GET", options.url, { error: message, status: xhr.status });
    showToast(message, "error");
    setStatus("API error");
  });
}

function loadStations() {
  return ajaxRequest({ url: API.stations }).done(function (data) {
    state.stations = Array.isArray(data) ? data : [];
    renderStations();
    renderStationSelect();
  });
}

function loadPrices() {
  return ajaxRequest({ url: API.prices }).done(function (data) {
    state.prices = sortByDateDescending(Array.isArray(data) ? data : []);
    state.recentPrices = state.prices.map(price => ({
      name: stationName(price.station_id),
      locality: stationLocality(price.station_id),
      petrol_95: price.petrol_95,
      diesel: price.diesel,
      lpg: price.lpg,
      price_date: price.price_date,
      station_id: price.station_id
    }));
    renderPrices();
    renderRecentPrices(state.recentPrices, "All fuel prices loaded from /fuel_prices.");
  });
}

function saveStation(event) {
  event.preventDefault();
  if (!requireLogin()) return;
  const id = $("#stationId").val();
  const payload = {
    name: $("#stationName").val().trim(),
    brand: $("#stationBrand").val().trim(),
    locality: $("#stationLocality").val().trim(),
    postcode: $("#stationPostcode").val().trim()
  };
  const method = id ? "PUT" : "POST";
  const url = id ? `${API.stations}/${id}` : API.stations;
  ajaxRequest({ url, method, data: JSON.stringify(payload) }).done(function () {
    showToast(id ? "Station updated" : "Station created", "success");
    clearStationForm();
    loadStations().then(function () { loadPrices(); loadAllAverages(); });
  });
}

function deleteStation(id) {
  if (!requireLogin()) return;
  if (!window.confirm(`Delete station #${id}?`)) return;
  ajaxRequest({ url: `${API.stations}/${id}`, method: "DELETE" }).done(function () {
    showToast("Station deleted", "success");
    loadStations().then(function () { loadPrices(); loadAllAverages(); });
  });
}

function savePrice(event) {
  event.preventDefault();
  if (!requireLogin()) return;
  const id = $("#priceId").val();
  const payload = {
    station_id: Number($("#priceStationId").val()),
    petrol_95: $("#petrol95").val(),
    diesel: $("#diesel").val(),
    lpg: $("#lpg").val(),
    price_date: $("#priceDate").val()
  };
  const method = id ? "PUT" : "POST";
  const url = id ? `${API.prices}/${id}` : API.prices;
  ajaxRequest({ url, method, data: JSON.stringify(payload) }).done(function () {
    showToast(id ? "Fuel price updated" : "Fuel price created", "success");
    clearPriceForm();
    loadPrices();
    loadAllAverages();
  });
}

function deletePrice(id) {
  if (!requireLogin()) return;
  if (!window.confirm(`Delete fuel price #${id}?`)) return;
  ajaxRequest({ url: `${API.prices}/${id}`, method: "DELETE" }).done(function () {
    showToast("Fuel price deleted", "success");
    loadPrices();
    loadAllAverages();
  });
}

function findPricesByLocalityAndDate(event) {
  event.preventDefault();
  const locality = $("#filterLocality").val().trim();
  const priceDate = $("#filterDate").val();
  const url = `${API.calculations}/prices_by_locality?locality=${encodeURIComponent(locality)}&price_date=${encodeURIComponent(priceDate)}`;
  ajaxRequest({ url }).done(function (data) {
    state.recentPrices = Array.isArray(data) ? data : [];
    renderRecentPrices(state.recentPrices, `${state.recentPrices.length} result(s) for ${locality} on ${priceDate}.`);
  });
}

function loadLatestPricesByDate(priceDate) {
  const url = `${API.calculations}/latest_prices?price_date=${encodeURIComponent(priceDate)}`;
  return ajaxRequest({ url }).done(function (data) {
    state.recentPrices = Array.isArray(data) ? data : [];
    renderRecentPrices(state.recentPrices, `${state.recentPrices.length} latest price row(s) found for ${priceDate}.`);
  });
}

function loadCheapestFuel(event) {
  event.preventDefault();
  const priceDate = $("#cheapestDate").val();
  const requests = [
    ajaxRequest({ url: `${API.calculations}/cheapest_petrol_95?price_date=${encodeURIComponent(priceDate)}` }),
    ajaxRequest({ url: `${API.calculations}/cheapest_diesel?price_date=${encodeURIComponent(priceDate)}` }),
    ajaxRequest({ url: `${API.calculations}/cheapest_lpg?price_date=${encodeURIComponent(priceDate)}` })
  ];

  $.when(...requests).done(function (petrolRes, dieselRes, lpgRes) {
    const petrol = Array.isArray(petrolRes) ? petrolRes[0] : petrolRes;
    const diesel = Array.isArray(dieselRes) ? dieselRes[0] : dieselRes;
    const lpg = Array.isArray(lpgRes) ? lpgRes[0] : lpgRes;
    $("#cheapestPetrol").text(formatPrice(petrol.petrol_95));
    $("#cheapestPetrolStation").text(petrol.name || "Unknown station");
    $("#cheapestDiesel").text(formatPrice(diesel.diesel));
    $("#cheapestDieselStation").text(diesel.name || "Unknown station");
    $("#cheapestLpg").text(formatPrice(lpg.lpg));
    $("#cheapestLpgStation").text(lpg.name || "Unknown station");
    showToast("Cheapest fuel comparison loaded", "success");
  });

  loadLatestPricesByDate(priceDate);
}

function loadAllAverages() {
  const requests = {
    all: ajaxRequest({ url: `${API.calculations}/average_all_fuel_types_by_day` }),
    petrol: ajaxRequest({ url: `${API.calculations}/average_petrol_95_by_day` }),
    diesel: ajaxRequest({ url: `${API.calculations}/average_diesel_by_day` }),
    lpg: ajaxRequest({ url: `${API.calculations}/average_lpg_by_day` })
  };

  return $.when(requests.all, requests.petrol, requests.diesel, requests.lpg).done(function (allRes, petrolRes, dieselRes, lpgRes) {
    state.averages.all = Array.isArray(allRes[0]) ? allRes[0] : [];
    state.averages.petrol = Array.isArray(petrolRes[0]) ? petrolRes[0] : [];
    state.averages.diesel = Array.isArray(dieselRes[0]) ? dieselRes[0] : [];
    state.averages.lpg = Array.isArray(lpgRes[0]) ? lpgRes[0] : [];
    renderAveragesTable();
  });
}

function renderStations() {
  const rows = state.stations.map(s => `
    <tr>
      <td>${escapeHtml(s.id)}</td><td>${escapeHtml(s.name)}</td><td>${escapeHtml(s.brand)}</td><td>${escapeHtml(s.locality)}</td><td>${escapeHtml(s.postcode)}</td>
      <td class="row-actions"><button class="btn secondary edit-station" data-id="${s.id}">Edit</button><button class="btn danger delete-station" data-id="${s.id}">Delete</button></td>
    </tr>`).join("");
  $("#stationsTable tbody").html(rows || emptyRow(6, "No fuel stations found."));
  updateAuthUI();
}

function renderStationSelect() {
  const currentValue = $("#priceStationId").val();
  const options = state.stations
    .map(s => `<option value="${escapeHtml(s.id)}">#${escapeHtml(s.id)} — ${escapeHtml(s.name)} (${escapeHtml(s.locality)})</option>`)
    .join("");
  $("#priceStationId").html(`<option value="">Select station...</option>${options}`);
  if (currentValue && state.stations.some(s => Number(s.id) === Number(currentValue))) {
    $("#priceStationId").val(currentValue);
  }
}

function renderPrices() {
  const sorted = sortByDateDescending(state.prices);
  const cheapest = cheapestValuesByFuel(sorted);
  const rows = sorted.map(p => `
    <tr>
      <td>${escapeHtml(p.id)}</td><td>${escapeHtml(stationDisplayName(p.station_id))}</td>${priceCell(p.petrol_95, "petrol_95", cheapest)}${priceCell(p.diesel, "diesel", cheapest)}${priceCell(p.lpg, "lpg", cheapest)}<td>${formatDate(p.price_date)}</td>
      <td class="row-actions"><button class="btn secondary edit-price" data-id="${p.id}">Edit</button><button class="btn danger delete-price" data-id="${p.id}">Delete</button></td>
    </tr>`).join("");
  $("#pricesTable tbody").html(rows || emptyRow(7, "No fuel prices found."));
  updateAuthUI();
}

function renderRecentPrices(items, summary) {
  const sorted = sortByDateDescending(items);
  const cheapest = cheapestValuesByFuel(sorted);
  const rows = sorted.map(p => `
    <tr>
      <td>${escapeHtml(p.name || stationName(p.station_id))}</td><td>${escapeHtml(p.locality || stationLocality(p.station_id))}</td>${priceCell(p.petrol_95, "petrol_95", cheapest)}${priceCell(p.diesel, "diesel", cheapest)}${priceCell(p.lpg, "lpg", cheapest)}<td>${formatDate(p.price_date)}</td>
    </tr>`).join("");
  $("#recentPricesTable tbody").html(rows || emptyRow(6, "No recent prices found."));
  $("#recentPriceSummary").text(summary);
}

function renderAveragesTable() {
  const type = state.currentAverage;
  const data = state.averages[type] || [];
  let headers = "";
  let rows = "";

  if (type === "all") {
    const cheapestAverages = cheapestValuesByKeys(data, ["avg_petrol_95", "avg_diesel", "avg_lpg"]);
    headers = "<tr><th>Date</th><th>Avg Petrol 95</th><th>Avg Diesel</th><th>Avg LPG</th></tr>";
    rows = data.map(r => `
      <tr>
        <td>${formatDate(r.price_date)}</td>
        ${priceCell(r.avg_petrol_95, "avg_petrol_95", cheapestAverages)}
        ${priceCell(r.avg_diesel, "avg_diesel", cheapestAverages)}
        ${priceCell(r.avg_lpg, "avg_lpg", cheapestAverages)}
      </tr>`).join("");
  } else if (type === "petrol") {
    const cheapestAverages = cheapestValuesByKeys(data, ["avg_petrol_95"]);
    headers = "<tr><th>Date</th><th>Avg Petrol 95</th></tr>";
    rows = data.map(r => `<tr><td>${formatDate(r.price_date)}</td>${priceCell(r.avg_petrol_95, "avg_petrol_95", cheapestAverages)}</tr>`).join("");
  } else if (type === "diesel") {
    const cheapestAverages = cheapestValuesByKeys(data, ["avg_diesel"]);
    headers = "<tr><th>Date</th><th>Avg Diesel</th></tr>";
    rows = data.map(r => `<tr><td>${formatDate(r.price_date)}</td>${priceCell(r.avg_diesel, "avg_diesel", cheapestAverages)}</tr>`).join("");
  } else {
    const cheapestAverages = cheapestValuesByKeys(data, ["avg_lpg"]);
    headers = "<tr><th>Date</th><th>Avg LPG</th></tr>";
    rows = data.map(r => `<tr><td>${formatDate(r.price_date)}</td>${priceCell(r.avg_lpg, "avg_lpg", cheapestAverages)}</tr>`).join("");
  }

  $("#averagesTable thead").html(headers);
  $("#averagesTable tbody").html(rows || emptyRow(type === "all" ? 4 : 2, "No averages found."));
}

function fillStationForm(id) {
  if (!requireLogin()) return;
  const station = state.stations.find(s => Number(s.id) === Number(id));
  if (!station) return showToast("Station not found in loaded data", "error");
  $("#stationId").val(station.id);
  $("#stationName").val(station.name);
  $("#stationBrand").val(station.brand);
  $("#stationLocality").val(station.locality);
  $("#stationPostcode").val(station.postcode);
  window.scrollTo({ top: $("#stationForm").offset().top - 120, behavior: "smooth" });
}

function fillPriceForm(id) {
  if (!requireLogin()) return;
  const price = state.prices.find(p => Number(p.id) === Number(id));
  if (!price) return showToast("Price not found in loaded data", "error");
  $("#priceId").val(price.id);
  $("#priceStationId").val(price.station_id);
  $("#petrol95").val(price.petrol_95);
  $("#diesel").val(price.diesel);
  $("#lpg").val(price.lpg);
  $("#priceDate").val(formatDate(price.price_date));
  window.scrollTo({ top: $("#priceForm").offset().top - 120, behavior: "smooth" });
}

function clearStationForm() {
  if (!state.authenticated) return; $("#stationForm")[0].reset(); $("#stationId").val(""); }
function clearPriceForm() {
  if (!state.authenticated) return; $("#priceForm")[0].reset(); $("#priceId").val(""); renderStationSelect(); setTodayDefaults(); }

function clearAllFormsAndTables() {
  clearStationForm();
  clearPriceForm();
  $("#localityDateForm")[0].reset();
  $("#cheapestForm")[0].reset();
  $("tbody").empty();
  $("#recentPriceSummary").text("Cleared. Use reset to reload data.");
  $("#globalSearch").val("");
  $("#cheapestPetrol,#cheapestDiesel,#cheapestLpg").text("—");
  $("#cheapestPetrolStation,#cheapestDieselStation,#cheapestLpgStation").text("No data loaded");
  logActivity("CLEAR", "dashboard", { message: "Forms and tables cleared" });
}

function resetDashboard() {
  clearStationForm();
  clearPriceForm();
  $("#globalSearch").val("");
  clearSearchOnly();
  loadInitialData();
  showToast("Dashboard reset", "success");
}

function applyGlobalSearch() {
  const rawQuery = $("#globalSearch").val().trim();
  const query = normaliseSearchText(rawQuery);
  if (!query) return clearSearchOnly();

  $("table tbody tr").each(function () {
    const searchableText = normaliseSearchText($(this).text());
    $(this).toggleClass("hidden-by-search", !searchableText.includes(query));
  });
}

function clearSearchOnly() {
  $("table tbody tr").removeClass("hidden-by-search");
}

function normaliseSearchText(value) {
  const text = String(value || "").toLowerCase().trim();
  const normalisedDates = extractDateSearchVariants(text).join(" ");
  return `${text} ${normalisedDates}`.replace(/\s+/g, " ").trim();
}

function extractDateSearchVariants(text) {
  const variants = [];

  const isoMatches = text.match(/\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b/g) || [];
  isoMatches.forEach(dateText => {
    const parts = dateText.split(/[-/.]/);
    const yyyy = parts[0];
    const mm = parts[1].padStart(2, "0");
    const dd = parts[2].padStart(2, "0");
    variants.push(`${yyyy}-${mm}-${dd}`, `${dd}/${mm}/${yyyy}`, `${dd}-${mm}-${yyyy}`, `${dd}.${mm}.${yyyy}`);
  });

  const europeanMatches = text.match(/\b\d{1,2}[-/.]\d{1,2}[-/.]\d{4}\b/g) || [];
  europeanMatches.forEach(dateText => {
    const parts = dateText.split(/[-/.]/);
    const dd = parts[0].padStart(2, "0");
    const mm = parts[1].padStart(2, "0");
    const yyyy = parts[2];
    variants.push(`${yyyy}-${mm}-${dd}`, `${dd}/${mm}/${yyyy}`, `${dd}-${mm}-${yyyy}`, `${dd}.${mm}.${yyyy}`);
  });

  return variants;
}

function sortByDateDescending(items) {
  return [...(items || [])].sort(function (a, b) {
    const dateCompare = dateSortValue(b.price_date) - dateSortValue(a.price_date);
    if (dateCompare !== 0) return dateCompare;
    const localityCompare = String(a.locality || "").localeCompare(String(b.locality || ""));
    if (localityCompare !== 0) return localityCompare;
    return Number(b.id || 0) - Number(a.id || 0);
  });
}

function dateSortValue(value) {
  if (!value) return 0;
  const text = String(value).trim();
  const isoMatch = text.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
  if (isoMatch) return new Date(Number(isoMatch[1]), Number(isoMatch[2]) - 1, Number(isoMatch[3])).getTime();
  const europeanMatch = text.match(/^(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{4})$/);
  if (europeanMatch) return new Date(Number(europeanMatch[3]), Number(europeanMatch[2]) - 1, Number(europeanMatch[1])).getTime();
  const parsed = Date.parse(text);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function findStationById(id) {
  return state.stations.find(s => Number(s.id) === Number(id));
}

function stationName(id) {
  return findStationById(id)?.name || "Unknown station";
}

function stationDisplayName(id) {
  const station = findStationById(id);
  return station ? `${station.name} (#${station.id})` : `Unknown station (#${id || "—"})`;
}

function stationLocality(id) {
  return findStationById(id)?.locality || "—";
}

function numericPrice(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function cheapestValuesByFuel(items) {
  return cheapestValuesByKeys(items, ["petrol_95", "diesel", "lpg"]);
}

function cheapestValuesByKeys(items, keys) {
  return keys.reduce(function (result, key) {
    const values = (items || [])
      .map(item => numericPrice(item[key]))
      .filter(value => value !== null);
    result[key] = values.length ? Math.min(...values) : null;
    return result;
  }, {});
}

function priceCell(value, priceKey, cheapest) {
  const number = numericPrice(value);
  const isCheapest = number !== null && cheapest[priceKey] !== null && number === cheapest[priceKey];
  const classes = `price-cell${isCheapest ? " cheapest-price" : ""}`;
  const title = isCheapest ? ` title="Cheapest price in this column"` : "";
  return `
    <td class="${classes}"${title}>
      <div class="price-inner">
        <span class="price-value">${formatPrice(value)}</span>
        ${isCheapest ? '<span class="cheap-label">CHEAPEST</span>' : ''}
      </div>
    </td>`;
}

function formatPrice(value) {
  if (value === null || value === undefined || value === "") return "—";
  const number = Number(value);
  return Number.isFinite(number) ? "€" + number.toFixed(2) + "/L" : escapeHtml(value);
}

function formatDate(value) {
  return value ? String(value).slice(0, 10) : "—";
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

function emptyRow(colspan, message) {
  return `<tr><td colspan="${colspan}" class="empty-state">${message}</td></tr>`;
}

function setTodayDefaults() {
  const today = new Date().toISOString().slice(0, 10);
  ["#filterDate", "#priceDate", "#cheapestDate"].forEach(selector => {
    if (!$(selector).val()) $(selector).val(today);
  });
}

function showToast(message, type = "success") {
  const toast = $("#toast");
  toast.removeClass("success error show").addClass(`${type} show`).text(message);
  setTimeout(() => toast.removeClass("show"), 3200);
}

function setStatus(text) { $("#apiStatus").text(text); }

function logActivity(method, url, payload) {
  const stamp = new Date().toLocaleTimeString();
  const entry = `[${stamp}] ${method} ${url}\n${JSON.stringify(payload, null, 2)}`;
  $("#activityLog").text(entry);
}
