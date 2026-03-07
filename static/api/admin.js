const storageKeys = {
    token: "sportspulse_admin_token",
    user: "sportspulse_admin_user",
};

const refs = {
    authStatus: document.getElementById("auth-status"),
    loginForm: document.getElementById("login-form"),
    registerForm: document.getElementById("register-form"),
    tokenInput: document.getElementById("token-input"),
    useTokenBtn: document.getElementById("use-token-btn"),
    logoutBtn: document.getElementById("logout-btn"),
    resourceSelect: document.getElementById("resource-select"),
    newRecordBtn: document.getElementById("new-record-btn"),
    refreshBtn: document.getElementById("refresh-btn"),
    resourceHead: document.getElementById("resource-head"),
    resourceBody: document.getElementById("resource-body"),
    formTitle: document.getElementById("form-title"),
    formHint: document.getElementById("form-hint"),
    recordForm: document.getElementById("record-form"),
    cancelEditBtn: document.getElementById("cancel-edit-btn"),
    toast: document.getElementById("toast"),
};

const resourceConfigs = {
    teams: {
        label: "Teams",
        endpoint: "/api/teams/",
        columns: [
            { label: "ID", path: "id" },
            { label: "Name", path: "name" },
            { label: "Short", path: "short_name" },
            { label: "Country", path: "country" },
            { label: "Founded", path: "founded_year" },
            { label: "Stadium", path: "stadium" },
        ],
        fields: [
            { name: "name", label: "Team Name", type: "text", required: true },
            { name: "short_name", label: "Short Name", type: "text", required: true },
            { name: "country", label: "Country", type: "text" },
            { name: "founded_year", label: "Founded Year", type: "number", min: 1800, max: 2030 },
            { name: "stadium", label: "Stadium", type: "text" },
            { name: "crest_url", label: "Crest URL", type: "url" },
        ],
    },
    players: {
        label: "Players",
        endpoint: "/api/players/",
        columns: [
            { label: "ID", path: "id" },
            { label: "Name", path: "name" },
            { label: "Team", path: "team_detail.short_name" },
            { label: "Position", path: "position_display" },
            { label: "Nationality", path: "nationality" },
            { label: "No.", path: "jersey_number" },
        ],
        fields: [
            { name: "name", label: "Player Name", type: "text", required: true },
            { name: "team", label: "Team", type: "select", required: true, source: "teams", asNumber: true, readPath: "team_detail.id" },
            {
                name: "position",
                label: "Position",
                type: "select",
                required: true,
                options: [
                    { value: "GK", label: "GK - Goalkeeper" },
                    { value: "DF", label: "DF - Defender" },
                    { value: "MF", label: "MF - Midfielder" },
                    { value: "FW", label: "FW - Forward" },
                ],
            },
            { name: "nationality", label: "Nationality", type: "text" },
            { name: "date_of_birth", label: "Date of Birth", type: "date" },
            { name: "jersey_number", label: "Jersey Number", type: "number", min: 1, max: 99 },
        ],
    },
    matches: {
        label: "Matches",
        endpoint: "/api/matches/",
        columns: [
            { label: "ID", path: "id" },
            { label: "Date", render: (row) => formatDateTime(row.date) },
            { label: "Home", path: "home_team_detail.short_name" },
            { label: "Away", path: "away_team_detail.short_name" },
            { label: "Score", render: (row) => `${row.home_score} - ${row.away_score}` },
            { label: "Status", path: "status" },
            { label: "Season", path: "season" },
        ],
        fields: [
            { name: "home_team", label: "Home Team", type: "select", required: true, source: "teams", asNumber: true, readPath: "home_team_detail.id" },
            { name: "away_team", label: "Away Team", type: "select", required: true, source: "teams", asNumber: true, readPath: "away_team_detail.id" },
            { name: "date", label: "Match Date Time", type: "datetime-local", required: true },
            { name: "venue", label: "Venue", type: "text" },
            { name: "season", label: "Season", type: "text", required: true, placeholder: "2024/2025" },
            { name: "home_score", label: "Home Score", type: "number", min: 0 },
            { name: "away_score", label: "Away Score", type: "number", min: 0 },
            {
                name: "status",
                label: "Status",
                type: "select",
                required: true,
                options: [
                    { value: "SCHEDULED", label: "SCHEDULED" },
                    { value: "LIVE", label: "LIVE" },
                    { value: "COMPLETED", label: "COMPLETED" },
                    { value: "POSTPONED", label: "POSTPONED" },
                ],
            },
        ],
    },
    statistics: {
        label: "Statistics",
        endpoint: "/api/statistics/",
        columns: [
            { label: "ID", path: "id" },
            { label: "Player", path: "player_detail.name" },
            { label: "Match", render: (row) => `${row.match_detail.home_team_name} vs ${row.match_detail.away_team_name}` },
            { label: "Goals", path: "goals" },
            { label: "Assists", path: "assists" },
            { label: "Minutes", path: "minutes_played" },
        ],
        fields: [
            { name: "player", label: "Player", type: "select", required: true, source: "players", asNumber: true, readPath: "player_detail.id" },
            { name: "match", label: "Match", type: "select", required: true, source: "matches", asNumber: true, readPath: "match_detail.id" },
            { name: "goals", label: "Goals", type: "number", min: 0 },
            { name: "assists", label: "Assists", type: "number", min: 0 },
            { name: "minutes_played", label: "Minutes Played", type: "number", min: 0, max: 120 },
            { name: "yellow_cards", label: "Yellow Cards", type: "number", min: 0 },
            { name: "red_cards", label: "Red Cards", type: "number", min: 0 },
            { name: "shots_on_target", label: "Shots on Target", type: "number", min: 0 },
            { name: "passes_completed", label: "Passes Completed", type: "number", min: 0 },
            { name: "tackles", label: "Tackles", type: "number", min: 0 },
            { name: "saves", label: "Saves", type: "number", min: 0 },
        ],
    },
};

const state = {
    token: "",
    user: null,
    activeResource: "teams",
    rows: [],
    editId: null,
    references: {
        teams: [],
        players: [],
        matches: [],
    },
};

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function showToast(message) {
    refs.toast.textContent = message;
    refs.toast.classList.add("show");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => {
        refs.toast.classList.remove("show");
    }, 2600);
}

function parseApiError(data, status) {
    if (!data) {
        return `Request failed (${status})`;
    }
    if (typeof data === "string") {
        return data;
    }
    if (typeof data.detail === "string") {
        return data.detail;
    }
    if (typeof data.error === "string") {
        return data.error;
    }
    for (const value of Object.values(data)) {
        if (Array.isArray(value) && value.length) {
            return String(value[0]);
        }
        if (typeof value === "string") {
            return value;
        }
    }
    return `Request failed (${status})`;
}

function formatDateTime(value) {
    if (!value) {
        return "-";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return value;
    }
    return date.toLocaleString();
}

function isoToDatetimeLocal(value) {
    if (!value) {
        return "";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return "";
    }
    const offset = date.getTimezoneOffset() * 60000;
    return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function getPathValue(obj, path) {
    if (!path) {
        return undefined;
    }
    return path.split(".").reduce((acc, key) => {
        if (acc === null || acc === undefined) {
            return undefined;
        }
        return acc[key];
    }, obj);
}

function getAuthHeaders(requireToken = false) {
    const headers = {
        Accept: "application/json",
    };
    if (state.token) {
        headers.Authorization = `Token ${state.token}`;
    }
    if (requireToken && !state.token) {
        throw new Error("Please login first to perform write operations.");
    }
    return headers;
}

async function request(path, { method = "GET", params, payload, requireToken = false } = {}) {
    const url = new URL(path, window.location.origin);
    if (params) {
        for (const [key, value] of Object.entries(params)) {
            if (value !== undefined && value !== null && String(value).trim() !== "") {
                url.searchParams.set(key, String(value).trim());
            }
        }
    }

    const headers = getAuthHeaders(requireToken);
    if (payload !== undefined) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(url.toString(), {
        method,
        headers,
        body: payload !== undefined ? JSON.stringify(payload) : undefined,
    });

    const contentType = response.headers.get("content-type") || "";
    let data = null;
    if (contentType.includes("application/json")) {
        data = await response.json();
    }

    if (!response.ok) {
        throw new Error(parseApiError(data, response.status));
    }

    return data;
}

async function fetchAll(path, params = {}) {
    const first = new URL(path, window.location.origin);
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && String(value).trim() !== "") {
            first.searchParams.set(key, String(value).trim());
        }
    }

    const rows = [];
    let nextUrl = first.toString();
    let guard = 0;

    while (nextUrl && guard < 40) {
        guard += 1;
        const response = await fetch(nextUrl, { headers: getAuthHeaders(false) });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(parseApiError(data, response.status));
        }
        if (Array.isArray(data)) {
            return data;
        }
        if (Array.isArray(data.results)) {
            rows.push(...data.results);
            nextUrl = data.next ? new URL(data.next, window.location.origin).toString() : null;
        } else {
            return rows;
        }
    }
    return rows;
}

function updateAuthStatus() {
    if (state.token) {
        const userText = state.user?.username ? ` as ${state.user.username}` : "";
        refs.authStatus.textContent = `Authenticated${userText}`;
        refs.authStatus.classList.add("ok");
        refs.tokenInput.value = state.token;
    } else {
        refs.authStatus.textContent = "Not authenticated";
        refs.authStatus.classList.remove("ok");
        refs.tokenInput.value = "";
    }
}

function saveAuthState() {
    if (state.token) {
        localStorage.setItem(storageKeys.token, state.token);
    } else {
        localStorage.removeItem(storageKeys.token);
    }
    if (state.user) {
        localStorage.setItem(storageKeys.user, JSON.stringify(state.user));
    } else {
        localStorage.removeItem(storageKeys.user);
    }
}

function setAuth(token, user = null) {
    state.token = token;
    state.user = user;
    saveAuthState();
    updateAuthStatus();
}

function clearAuth() {
    state.token = "";
    state.user = null;
    saveAuthState();
    updateAuthStatus();
}

function hydrateAuthFromStorage() {
    state.token = localStorage.getItem(storageKeys.token) || "";
    const rawUser = localStorage.getItem(storageKeys.user);
    state.user = rawUser ? JSON.parse(rawUser) : null;
    updateAuthStatus();
}

function getOptionsForField(field) {
    if (Array.isArray(field.options)) {
        return field.options;
    }

    if (field.source === "teams") {
        return state.references.teams.map((team) => ({
            value: String(team.id),
            label: `${team.name} (${team.short_name})`,
        }));
    }

    if (field.source === "players") {
        return state.references.players.map((player) => ({
            value: String(player.id),
            label: `${player.name} (${player.team_detail?.short_name || "-"})`,
        }));
    }

    if (field.source === "matches") {
        return state.references.matches.map((match) => ({
            value: String(match.id),
            label: `${match.home_team_detail?.short_name || "?"} ${match.home_score}-${match.away_score} ${match.away_team_detail?.short_name || "?"} (${match.season})`,
        }));
    }

    return [];
}

function renderField(field, value = "") {
    const id = `field-${field.name}`;
    const required = field.required ? "required" : "";
    const placeholder = field.placeholder ? `placeholder="${escapeHtml(field.placeholder)}"` : "";
    const min = field.min !== undefined ? `min="${field.min}"` : "";
    const max = field.max !== undefined ? `max="${field.max}"` : "";

    if (field.type === "select") {
        const options = getOptionsForField(field);
        const optionHtml = [`<option value="">Select...</option>`]
            .concat(
                options.map((option) => {
                    const selected = String(value) === String(option.value) ? "selected" : "";
                    return `<option value="${escapeHtml(option.value)}" ${selected}>${escapeHtml(option.label)}</option>`;
                })
            )
            .join("");

        return `
            <label for="${id}">
                ${escapeHtml(field.label)}
                <select id="${id}" name="${field.name}" ${required}>
                    ${optionHtml}
                </select>
            </label>
        `;
    }

    const type = field.type || "text";
    const inputValue = value === null || value === undefined ? "" : String(value);
    return `
        <label for="${id}">
            ${escapeHtml(field.label)}
            <input id="${id}" name="${field.name}" type="${type}" value="${escapeHtml(inputValue)}" ${placeholder} ${required} ${min} ${max}>
        </label>
    `;
}

function resolveFieldValue(record, field) {
    let value;
    if (field.readPath) {
        value = getPathValue(record, field.readPath);
    } else {
        value = record[field.name];
    }

    if (field.type === "datetime-local") {
        return isoToDatetimeLocal(value);
    }
    if (field.type === "date" && typeof value === "string") {
        return value.slice(0, 10);
    }
    return value ?? "";
}

function renderForm() {
    const config = resourceConfigs[state.activeResource];
    const editRecord = state.editId ? state.rows.find((row) => row.id === state.editId) : null;

    refs.formTitle.textContent = state.editId
        ? `Edit ${config.label.slice(0, -1)} #${state.editId}`
        : `Create ${config.label.slice(0, -1)}`;
    refs.formHint.textContent = state.editId
        ? "Update only the fields you want to change and save."
        : "Create a new record in the selected resource.";

    refs.recordForm.innerHTML = config.fields
        .map((field) => renderField(field, editRecord ? resolveFieldValue(editRecord, field) : ""))
        .join("");
}

function renderTableHead() {
    const config = resourceConfigs[state.activeResource];
    const columns = config.columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("");
    refs.resourceHead.innerHTML = `<tr>${columns}<th>Actions</th></tr>`;
}

function columnValue(row, column) {
    if (typeof column.render === "function") {
        return column.render(row);
    }
    const value = getPathValue(row, column.path);
    return value === null || value === undefined || value === "" ? "-" : value;
}

function renderTableRows() {
    if (!state.rows.length) {
        refs.resourceBody.innerHTML = `<tr class="loading-row"><td colspan="99">No records found.</td></tr>`;
        return;
    }

    const config = resourceConfigs[state.activeResource];
    refs.resourceBody.innerHTML = state.rows
        .map((row) => {
            const cells = config.columns
                .map((column) => `<td>${escapeHtml(columnValue(row, column))}</td>`)
                .join("");
            return `
                <tr>
                    ${cells}
                    <td>
                        <div class="row-actions">
                            <button type="button" class="mini-btn" data-action="edit" data-id="${row.id}">Edit</button>
                            <button type="button" class="mini-btn danger" data-action="delete" data-id="${row.id}">Delete</button>
                        </div>
                    </td>
                </tr>
            `;
        })
        .join("");
}

function setTableLoading(message = "Loading records...") {
    refs.resourceBody.innerHTML = `<tr class="loading-row"><td colspan="99">${escapeHtml(message)}</td></tr>`;
}

async function refreshReferences() {
    const [teams, players, matches] = await Promise.all([
        fetchAll("/api/teams/"),
        fetchAll("/api/players/"),
        fetchAll("/api/matches/"),
    ]);

    state.references.teams = teams;
    state.references.players = players;
    state.references.matches = matches;
}

async function loadResourceRows() {
    setTableLoading();
    const config = resourceConfigs[state.activeResource];
    state.rows = await fetchAll(config.endpoint);
    renderTableRows();
}

async function switchResource(resourceKey) {
    state.activeResource = resourceKey;
    state.editId = null;
    refs.resourceSelect.value = resourceKey;
    renderTableHead();
    renderForm();
    await loadResourceRows();
}

function normalizePayload(formData) {
    const config = resourceConfigs[state.activeResource];
    const payload = {};

    for (const field of config.fields) {
        const raw = formData.get(field.name);
        const value = typeof raw === "string" ? raw.trim() : raw;

        if (value === "" || value === null) {
            if (field.required) {
                throw new Error(`${field.label} is required.`);
            }
            continue;
        }

        if (field.type === "number") {
            const parsed = Number(value);
            if (Number.isNaN(parsed)) {
                throw new Error(`${field.label} must be a number.`);
            }
            payload[field.name] = parsed;
            continue;
        }

        if (field.type === "datetime-local") {
            const iso = new Date(value).toISOString();
            payload[field.name] = iso;
            continue;
        }

        if (field.type === "select" && field.asNumber) {
            payload[field.name] = Number(value);
            continue;
        }

        payload[field.name] = value;
    }

    if (state.activeResource === "matches" && payload.home_team && payload.away_team && payload.home_team === payload.away_team) {
        throw new Error("Home team and away team must be different.");
    }

    return payload;
}

async function saveRecord(event) {
    event.preventDefault();

    const formData = new FormData(refs.recordForm);
    const payload = normalizePayload(formData);
    const config = resourceConfigs[state.activeResource];

    if (Object.keys(payload).length === 0) {
        showToast("No changes to save.");
        return;
    }

    if (state.editId) {
        await request(`${config.endpoint}${state.editId}/`, {
            method: "PATCH",
            payload,
            requireToken: true,
        });
        showToast(`Updated ${config.label.slice(0, -1)} #${state.editId}`);
    } else {
        await request(config.endpoint, {
            method: "POST",
            payload,
            requireToken: true,
        });
        showToast(`${config.label.slice(0, -1)} created successfully.`);
    }

    state.editId = null;
    await refreshReferences();
    await loadResourceRows();
    renderForm();
}

function enterCreateMode() {
    state.editId = null;
    renderForm();
}

function enterEditMode(id) {
    state.editId = id;
    renderForm();
}

async function deleteRecord(id) {
    if (!window.confirm(`Delete record #${id}? This action cannot be undone.`)) {
        return;
    }

    const config = resourceConfigs[state.activeResource];
    await request(`${config.endpoint}${id}/`, {
        method: "DELETE",
        requireToken: true,
    });
    showToast(`${config.label.slice(0, -1)} #${id} deleted.`);

    if (state.editId === id) {
        state.editId = null;
    }

    await refreshReferences();
    await loadResourceRows();
    renderForm();
}

function wireReveal() {
    const blocks = [...document.querySelectorAll(".reveal")];
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("in");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.18 }
    );

    blocks.forEach((block, index) => {
        block.style.transitionDelay = `${Math.min(index * 90, 320)}ms`;
        observer.observe(block);
    });
}

function bindHandlers() {
    refs.loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(refs.loginForm);
        try {
            const payload = await request("/api/auth/login/", {
                method: "POST",
                payload: {
                    username: formData.get("username"),
                    password: formData.get("password"),
                },
            });
            setAuth(payload.token, payload.user);
            refs.loginForm.reset();
            showToast("Login successful.");
        } catch (error) {
            showToast(error.message);
        }
    });

    refs.registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(refs.registerForm);
        try {
            const payload = await request("/api/auth/register/", {
                method: "POST",
                payload: {
                    username: formData.get("username"),
                    email: formData.get("email"),
                    password: formData.get("password"),
                },
            });
            setAuth(payload.token, payload.user);
            refs.registerForm.reset();
            showToast("Account created and authenticated.");
        } catch (error) {
            showToast(error.message);
        }
    });

    refs.useTokenBtn.addEventListener("click", () => {
        const token = refs.tokenInput.value.trim();
        if (!token) {
            showToast("Please paste a token first.");
            return;
        }
        setAuth(token, state.user);
        showToast("Token applied.");
    });

    refs.logoutBtn.addEventListener("click", () => {
        clearAuth();
        showToast("Logged out.");
    });

    refs.resourceSelect.addEventListener("change", async (event) => {
        try {
            await switchResource(event.target.value);
        } catch (error) {
            showToast(error.message);
            setTableLoading("Unable to load records.");
        }
    });

    refs.newRecordBtn.addEventListener("click", enterCreateMode);

    refs.refreshBtn.addEventListener("click", async () => {
        try {
            await refreshReferences();
            await loadResourceRows();
            renderForm();
            showToast("Resource refreshed.");
        } catch (error) {
            showToast(error.message);
            setTableLoading("Unable to refresh records.");
        }
    });

    refs.cancelEditBtn.addEventListener("click", enterCreateMode);
    refs.recordForm.addEventListener("submit", async (event) => {
        try {
            await saveRecord(event);
        } catch (error) {
            showToast(error.message);
        }
    });

    refs.resourceBody.addEventListener("click", async (event) => {
        const target = event.target;
        if (!(target instanceof HTMLElement)) {
            return;
        }
        const action = target.dataset.action;
        const id = Number(target.dataset.id);
        if (!action || Number.isNaN(id)) {
            return;
        }

        try {
            if (action === "edit") {
                enterEditMode(id);
                return;
            }
            if (action === "delete") {
                await deleteRecord(id);
            }
        } catch (error) {
            showToast(error.message);
        }
    });
}

async function bootstrap() {
    wireReveal();
    hydrateAuthFromStorage();
    bindHandlers();

    try {
        await refreshReferences();
        await switchResource(state.activeResource);
    } catch (error) {
        showToast(error.message);
        setTableLoading("Initial load failed.");
    }
}

document.addEventListener("DOMContentLoaded", bootstrap);
