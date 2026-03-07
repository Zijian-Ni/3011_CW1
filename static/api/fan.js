const refs = {
    kpiTeams: document.getElementById("fan-kpi-teams"),
    kpiPlayers: document.getElementById("fan-kpi-players"),
    kpiMatches: document.getElementById("fan-kpi-matches"),
    kpiSeason: document.getElementById("fan-kpi-season"),
    teamFilterForm: document.getElementById("team-filter-form"),
    teamCards: document.getElementById("team-cards"),
    matchFilterForm: document.getElementById("match-filter-form"),
    matchList: document.getElementById("match-list"),
    leaderboardForm: document.getElementById("fan-leaderboard-form"),
    leaderboardBody: document.getElementById("fan-leaderboard-body"),
    playerFilterForm: document.getElementById("player-filter-form"),
    playerTeamSelect: document.getElementById("player-team-select"),
    playerTableBody: document.getElementById("player-table-body"),
    profileCard: document.getElementById("player-profile-card"),
    profileSeasonBody: document.getElementById("profile-season-body"),
    toast: document.getElementById("toast"),
};

const state = {
    latestSeason: "",
    teams: [],
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
    }, 2400);
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

async function request(path, params = {}) {
    const url = new URL(path, window.location.origin);
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && String(value).trim() !== "") {
            url.searchParams.set(key, String(value).trim());
        }
    }

    const response = await fetch(url.toString(), {
        headers: { Accept: "application/json" },
    });
    const data = await response.json();

    if (!response.ok) {
        throw new Error(parseApiError(data, response.status));
    }
    return data;
}

async function fetchAll(path, params = {}) {
    const firstUrl = new URL(path, window.location.origin);
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && String(value).trim() !== "") {
            firstUrl.searchParams.set(key, String(value).trim());
        }
    }

    const rows = [];
    let next = firstUrl.toString();
    let guard = 0;
    while (next && guard < 40) {
        guard += 1;
        const response = await fetch(next, { headers: { Accept: "application/json" } });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(parseApiError(data, response.status));
        }
        if (Array.isArray(data)) {
            return data;
        }
        rows.push(...(data.results || []));
        next = data.next ? new URL(data.next, window.location.origin).toString() : null;
    }
    return rows;
}

function setEmpty(container, text) {
    container.innerHTML = `<div class="empty-state">${escapeHtml(text)}</div>`;
}

function setLoadingRow(target, colSpan, text = "Loading...") {
    target.innerHTML = `<tr><td colspan="${colSpan}" class="empty-state">${escapeHtml(text)}</td></tr>`;
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

function wireReveal() {
    const sections = [...document.querySelectorAll(".reveal")];
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("in");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.16 }
    );

    sections.forEach((section, index) => {
        section.style.transitionDelay = `${Math.min(index * 90, 320)}ms`;
        observer.observe(section);
    });
}

async function loadKpis() {
    const [teamsPage, playersPage, matchesPage] = await Promise.all([
        request("/api/teams/"),
        request("/api/players/"),
        request("/api/matches/"),
    ]);

    refs.kpiTeams.textContent = teamsPage.count ?? 0;
    refs.kpiPlayers.textContent = playersPage.count ?? 0;
    refs.kpiMatches.textContent = matchesPage.count ?? 0;

    const latest = Array.isArray(matchesPage.results) && matchesPage.results.length ? matchesPage.results[0].season : "";
    state.latestSeason = latest || "";
    refs.kpiSeason.textContent = state.latestSeason || "--";
}

async function loadTeams(filters = {}) {
    refs.teamCards.innerHTML = `<div class="empty-state">Loading teams...</div>`;
    const teams = await fetchAll("/api/teams/", filters);
    state.teams = teams;

    if (!teams.length) {
        setEmpty(refs.teamCards, "No teams found.");
        return;
    }

    refs.teamCards.innerHTML = teams
        .map((team) => {
            return `
                <article class="team-card">
                    <h4>${escapeHtml(team.name)} <span class="status-tag">${escapeHtml(team.short_name)}</span></h4>
                    <div class="team-meta">
                        <span>Country: ${escapeHtml(team.country || "-")}</span>
                        <span>Founded: ${escapeHtml(team.founded_year || "-")}</span>
                        <span>Stadium: ${escapeHtml(team.stadium || "-")}</span>
                        <span>Players: ${escapeHtml(team.player_count ?? "-")}</span>
                    </div>
                </article>
            `;
        })
        .join("");
}

async function loadMatches(filters = {}) {
    refs.matchList.innerHTML = `<div class="empty-state">Loading matches...</div>`;
    const matches = await fetchAll("/api/matches/", filters);

    if (!matches.length) {
        setEmpty(refs.matchList, "No matches found for this filter.");
        return;
    }

    refs.matchList.innerHTML = matches
        .slice(0, 40)
        .map((match) => {
            return `
                <article class="match-item">
                    <div class="match-score">
                        <span>${escapeHtml(match.home_team_detail?.short_name || "?")} ${match.home_score}</span>
                        <span>-</span>
                        <span>${match.away_score} ${escapeHtml(match.away_team_detail?.short_name || "?")}</span>
                        <span class="status-tag">${escapeHtml(match.status)}</span>
                    </div>
                    <div class="match-meta">
                        ${escapeHtml(formatDateTime(match.date))} | ${escapeHtml(match.venue || "-")} | Season ${escapeHtml(match.season)}
                    </div>
                </article>
            `;
        })
        .join("");
}

async function loadLeaderboard(params = {}) {
    setLoadingRow(refs.leaderboardBody, 6, "Loading leaderboard...");
    const payload = await request("/api/analytics/leaderboard/", params);
    const rows = payload.results || [];
    if (!rows.length) {
        setLoadingRow(refs.leaderboardBody, 6, "No leaderboard rows.");
        return;
    }

    refs.leaderboardBody.innerHTML = rows
        .map((row) => {
            return `
                <tr>
                    <td>${row.rank}</td>
                    <td>${escapeHtml(row.player_name)}</td>
                    <td>${escapeHtml(row.team_short || row.team || "-")}</td>
                    <td>${escapeHtml(row.position || "-")}</td>
                    <td>${row.total}</td>
                    <td>${row.matches_played}</td>
                </tr>
            `;
        })
        .join("");
}

function populateTeamSelect(teams) {
    const options = [`<option value="">All Teams</option>`]
        .concat(teams.map((team) => `<option value="${team.id}">${escapeHtml(team.name)}</option>`))
        .join("");
    refs.playerTeamSelect.innerHTML = options;
}

async function loadPlayers(filters = {}) {
    setLoadingRow(refs.playerTableBody, 5, "Loading players...");
    const players = await fetchAll("/api/players/", filters);
    if (!players.length) {
        setLoadingRow(refs.playerTableBody, 5, "No players found.");
        return;
    }

    refs.playerTableBody.innerHTML = players
        .slice(0, 80)
        .map((player) => {
            return `
                <tr>
                    <td>${escapeHtml(player.name)}</td>
                    <td>${escapeHtml(player.team_detail?.short_name || "-")}</td>
                    <td>${escapeHtml(player.position_display || player.position || "-")}</td>
                    <td>${escapeHtml(player.nationality || "-")}</td>
                    <td><button type="button" class="action-btn" data-player-id="${player.id}">View Profile</button></td>
                </tr>
            `;
        })
        .join("");
}

function renderProfile(payload) {
    const player = payload.player;
    const totals = payload.career_totals;

    refs.profileCard.innerHTML = `
        <h4>${escapeHtml(player.name)} <span class="status-tag">${escapeHtml(player.position)}</span></h4>
        <p class="muted">${escapeHtml(player.team)} | ${escapeHtml(player.nationality || "-")} | #${escapeHtml(player.jersey_number || "-")}</p>
        <div class="profile-grid">
            <div class="metric-chip">
                <p>Appearances</p>
                <strong>${totals.appearances}</strong>
            </div>
            <div class="metric-chip">
                <p>Goals</p>
                <strong>${totals.goals}</strong>
            </div>
            <div class="metric-chip">
                <p>Assists</p>
                <strong>${totals.assists}</strong>
            </div>
            <div class="metric-chip">
                <p>Avg Minutes</p>
                <strong>${totals.avg_minutes_per_match}</strong>
            </div>
            <div class="metric-chip">
                <p>Yellow Cards</p>
                <strong>${totals.yellow_cards}</strong>
            </div>
            <div class="metric-chip">
                <p>Red Cards</p>
                <strong>${totals.red_cards}</strong>
            </div>
        </div>
    `;

    const seasons = payload.by_season || [];
    if (!seasons.length) {
        refs.profileSeasonBody.innerHTML = `<tr><td colspan="4" class="empty-state">No season breakdown available.</td></tr>`;
        return;
    }

    refs.profileSeasonBody.innerHTML = seasons
        .map((season) => {
            return `
                <tr>
                    <td>${escapeHtml(season.season)}</td>
                    <td>${season.appearances}</td>
                    <td>${season.goals}</td>
                    <td>${season.assists}</td>
                </tr>
            `;
        })
        .join("");
}

async function loadPlayerProfile(playerId) {
    refs.profileCard.innerHTML = `<p class="muted">Loading profile...</p>`;
    refs.profileSeasonBody.innerHTML = `<tr><td colspan="4" class="empty-state">Loading season splits...</td></tr>`;
    const payload = await request(`/api/analytics/player-profile/${playerId}/`);
    renderProfile(payload);
}

function bindHandlers() {
    refs.teamFilterForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const data = new FormData(refs.teamFilterForm);
        try {
            await loadTeams({
                search: data.get("search"),
                country: data.get("country"),
            });
        } catch (error) {
            showToast(error.message);
            setEmpty(refs.teamCards, "Unable to load teams.");
        }
    });

    refs.matchFilterForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const data = new FormData(refs.matchFilterForm);
        try {
            await loadMatches({
                season: data.get("season"),
                status: data.get("status"),
            });
        } catch (error) {
            showToast(error.message);
            setEmpty(refs.matchList, "Unable to load matches.");
        }
    });

    refs.leaderboardForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const data = new FormData(refs.leaderboardForm);
        try {
            await loadLeaderboard({
                metric: data.get("metric"),
                season: data.get("season"),
                limit: data.get("limit"),
            });
        } catch (error) {
            showToast(error.message);
            setLoadingRow(refs.leaderboardBody, 6, "Unable to load leaderboard.");
        }
    });

    refs.playerFilterForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const data = new FormData(refs.playerFilterForm);
        try {
            await loadPlayers({
                search: data.get("search"),
                team: data.get("team"),
                position: data.get("position"),
            });
        } catch (error) {
            showToast(error.message);
            setLoadingRow(refs.playerTableBody, 5, "Unable to load players.");
        }
    });

    refs.playerTableBody.addEventListener("click", async (event) => {
        const target = event.target;
        if (!(target instanceof HTMLElement)) {
            return;
        }
        const id = Number(target.dataset.playerId);
        if (Number.isNaN(id)) {
            return;
        }
        try {
            await loadPlayerProfile(id);
        } catch (error) {
            showToast(error.message);
            refs.profileCard.innerHTML = `<p class="muted">Unable to load profile.</p>`;
            refs.profileSeasonBody.innerHTML = `<tr><td colspan="4" class="empty-state">No profile data.</td></tr>`;
        }
    });
}

async function bootstrap() {
    wireReveal();
    bindHandlers();

    setEmpty(refs.teamCards, "Loading teams...");
    setEmpty(refs.matchList, "Loading matches...");
    setLoadingRow(refs.leaderboardBody, 6, "Loading leaderboard...");
    setLoadingRow(refs.playerTableBody, 5, "Loading players...");
    refs.profileSeasonBody.innerHTML = `<tr><td colspan="4" class="empty-state">Select a player to view season splits.</td></tr>`;

    try {
        await loadKpis();
    } catch (error) {
        showToast(error.message);
    }

    try {
        const teams = await fetchAll("/api/teams/");
        populateTeamSelect(teams);
        state.teams = teams;
    } catch (error) {
        showToast(error.message);
    }

    try {
        await Promise.all([
            loadTeams(),
            loadMatches({ status: "COMPLETED" }),
            loadLeaderboard({ metric: "goals", limit: 8 }),
            loadPlayers(),
        ]);
    } catch (error) {
        showToast(error.message);
    }

    if (state.latestSeason) {
        const seasonInput = refs.leaderboardForm.querySelector("input[name='season']");
        seasonInput.value = state.latestSeason;
        try {
            await loadLeaderboard({ metric: "goals", season: state.latestSeason, limit: 8 });
        } catch {
            // no-op
        }
    }
}

document.addEventListener("DOMContentLoaded", bootstrap);
