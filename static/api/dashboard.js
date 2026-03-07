const endpoints = {
    teams: "/api/teams/",
    players: "/api/players/",
    matches: "/api/matches/",
    leaderboard: "/api/analytics/leaderboard/",
    teamPerformance: "/api/analytics/team-performance/",
    seasonSummary: "/api/analytics/season-summary/",
    headToHead: "/api/analytics/head-to-head/",
};

const refs = {
    kpiTeams: document.getElementById("kpi-teams"),
    kpiPlayers: document.getElementById("kpi-players"),
    kpiMatches: document.getElementById("kpi-matches"),
    kpiAvgGoals: document.getElementById("kpi-avg-goals"),
    leaderboardForm: document.getElementById("leaderboard-form"),
    standingsForm: document.getElementById("standings-form"),
    summaryForm: document.getElementById("summary-form"),
    h2hForm: document.getElementById("h2h-form"),
    leaderboardBody: document.getElementById("leaderboard-body"),
    standingsBody: document.getElementById("standings-body"),
    summaryCard: document.getElementById("summary-card"),
    h2hResult: document.getElementById("h2h-result"),
    h2hMatchesBody: document.getElementById("h2h-matches-body"),
    team1Select: document.getElementById("team1-select"),
    team2Select: document.getElementById("team2-select"),
    toast: document.getElementById("toast"),
};

const state = {
    latestSeason: "",
};

function escapeHtml(text) {
    return String(text)
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
    if (data.detail && typeof data.detail === "string") {
        return data.detail;
    }
    if (data.error && typeof data.error === "string") {
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
        if (value !== null && value !== undefined && String(value).trim() !== "") {
            url.searchParams.set(key, String(value).trim());
        }
    }

    const response = await fetch(url.toString(), {
        headers: {
            Accept: "application/json",
        },
    });

    let data = null;
    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        throw new Error(parseApiError(data, response.status));
    }

    return data;
}

async function fetchAll(path, params = {}) {
    const seedUrl = new URL(path, window.location.origin);
    for (const [key, value] of Object.entries(params)) {
        if (value !== null && value !== undefined && String(value).trim() !== "") {
            seedUrl.searchParams.set(key, String(value).trim());
        }
    }

    const rows = [];
    let next = seedUrl.toString();
    let loops = 0;

    while (next && loops < 40) {
        loops += 1;
        const response = await fetch(next, { headers: { Accept: "application/json" } });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(parseApiError(data, response.status));
        }
        if (Array.isArray(data)) {
            return data;
        }
        if (Array.isArray(data.results)) {
            rows.push(...data.results);
            next = data.next ? new URL(data.next, window.location.origin).toString() : null;
        } else {
            return rows;
        }
    }

    return rows;
}

function setLoadingRow(target, colSpan, text = "Loading data...") {
    target.innerHTML = `<tr class="loading-row"><td colspan="${colSpan}">${escapeHtml(text)}</td></tr>`;
}

function renderEmptyRow(target, colSpan, text = "No data found.") {
    target.innerHTML = `<tr class="loading-row"><td colspan="${colSpan}">${escapeHtml(text)}</td></tr>`;
}

function wireRevealAnimations() {
    const reveals = [...document.querySelectorAll(".reveal")];
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }
                entry.target.classList.add("in");
                observer.unobserve(entry.target);
            });
        },
        { threshold: 0.2 }
    );

    reveals.forEach((el, index) => {
        el.style.transitionDelay = `${Math.min(index * 80, 320)}ms`;
        observer.observe(el);
    });
}

async function loadKpis() {
    const [teamsPage, playersPage, matchesPage] = await Promise.all([
        request(endpoints.teams),
        request(endpoints.players),
        request(endpoints.matches, { status: "COMPLETED" }),
    ]);

    const teamsCount = typeof teamsPage.count === "number" ? teamsPage.count : 0;
    const playersCount = typeof playersPage.count === "number" ? playersPage.count : 0;
    const completedCount = typeof matchesPage.count === "number" ? matchesPage.count : 0;
    const firstCompleted = Array.isArray(matchesPage.results) && matchesPage.results.length
        ? matchesPage.results[0]
        : null;

    state.latestSeason = firstCompleted?.season || "";
    refs.kpiTeams.textContent = teamsCount;
    refs.kpiPlayers.textContent = playersCount;
    refs.kpiMatches.textContent = completedCount;

    if (state.latestSeason) {
        try {
            const payload = await request(endpoints.seasonSummary, { season: state.latestSeason });
            refs.kpiAvgGoals.textContent = payload.average_goals_per_match ?? "--";
        } catch {
            refs.kpiAvgGoals.textContent = "--";
        }
    } else {
        refs.kpiAvgGoals.textContent = "--";
    }
}

async function populateTeamSelectors() {
    const teams = await fetchAll(endpoints.teams);
    const options = [
        `<option value="">Choose team</option>`,
        ...teams.map((team) => `<option value="${team.id}">${escapeHtml(team.name)}</option>`),
    ];
    refs.team1Select.innerHTML = options.join("");
    refs.team2Select.innerHTML = options.join("");

    if (teams.length > 1) {
        refs.team1Select.value = String(teams[0].id);
        refs.team2Select.value = String(teams[1].id);
    }
}

async function loadLeaderboard(params = {}) {
    setLoadingRow(refs.leaderboardBody, 6);
    const payload = await request(endpoints.leaderboard, params);
    const rows = payload.results || [];
    if (!rows.length) {
        renderEmptyRow(refs.leaderboardBody, 6, "No leaderboard records.");
        return;
    }
    refs.leaderboardBody.innerHTML = rows
        .map((row) => {
            return `
                <tr>
                    <td>${row.rank}</td>
                    <td>${escapeHtml(row.player_name)}</td>
                    <td>${escapeHtml(row.team_short || row.team || "-")}</td>
                    <td><span class="tag">${escapeHtml(row.position)}</span></td>
                    <td><strong>${row.total}</strong></td>
                    <td>${row.matches_played}</td>
                </tr>
            `;
        })
        .join("");
}

async function loadStandings(params = {}) {
    setLoadingRow(refs.standingsBody, 7);
    const payload = await request(endpoints.teamPerformance, params);
    const standings = payload.standings || [];
    if (!standings.length) {
        renderEmptyRow(refs.standingsBody, 7, "No standings found.");
        return;
    }

    refs.standingsBody.innerHTML = standings
        .map((team, index) => {
            return `
                <tr>
                    <td>${index === 0 ? '<span class="tag">#1</span> ' : ""}${escapeHtml(team.short_name || team.team_name)}</td>
                    <td>${team.played}</td>
                    <td>${team.wins}</td>
                    <td>${team.draws}</td>
                    <td>${team.losses}</td>
                    <td>${team.goal_difference}</td>
                    <td><strong>${team.points}</strong></td>
                </tr>
            `;
        })
        .join("");
}

function renderSummary(payload) {
    if (payload.message) {
        refs.summaryCard.innerHTML = `<p class="muted">${escapeHtml(payload.message)}</p>`;
        return;
    }

    const scorer = payload.top_scorer
        ? `${escapeHtml(payload.top_scorer.name)} (${escapeHtml(payload.top_scorer.team)}) - ${payload.top_scorer.goals}`
        : "N/A";
    const assister = payload.top_assister
        ? `${escapeHtml(payload.top_assister.name)} (${escapeHtml(payload.top_assister.team)}) - ${payload.top_assister.assists}`
        : "N/A";

    refs.summaryCard.innerHTML = `
        <div class="summary-metrics">
            <div class="summary-chip">
                <p>Total Matches</p>
                <strong>${payload.total_matches ?? "--"}</strong>
            </div>
            <div class="summary-chip">
                <p>Total Goals</p>
                <strong>${payload.total_goals ?? "--"}</strong>
            </div>
            <div class="summary-chip">
                <p>Average Goals / Match</p>
                <strong>${payload.average_goals_per_match ?? "--"}</strong>
            </div>
            <div class="summary-chip">
                <p>Top Scorer</p>
                <strong>${scorer}</strong>
            </div>
            <div class="summary-chip">
                <p>Top Assister</p>
                <strong>${assister}</strong>
            </div>
            <div class="summary-chip">
                <p>Season</p>
                <strong>${escapeHtml(payload.season || "--")}</strong>
            </div>
        </div>
    `;
}

async function loadSummary(season) {
    if (!season || !String(season).trim()) {
        refs.summaryCard.innerHTML = `<p class="muted">Please provide a season, e.g. 2024/2025.</p>`;
        return;
    }
    refs.summaryCard.innerHTML = `<p class="muted">Loading season summary...</p>`;
    const payload = await request(endpoints.seasonSummary, { season });
    renderSummary(payload);
}

function renderHeadToHead(payload) {
    refs.h2hResult.innerHTML = `
        <h4>${escapeHtml(payload.team1.name)} vs ${escapeHtml(payload.team2.name)}</h4>
        <div class="h2h-pill-row">
            <span class="pill">Matches: ${payload.total_matches}</span>
            <span class="pill">${escapeHtml(payload.team1.name)} Wins: ${payload.team1_wins}</span>
            <span class="pill">${escapeHtml(payload.team2.name)} Wins: ${payload.team2_wins}</span>
            <span class="pill warn">Draws: ${payload.draws}</span>
        </div>
    `;

    if (!payload.matches || !payload.matches.length) {
        renderEmptyRow(refs.h2hMatchesBody, 3, "No historical matches found.");
        return;
    }

    refs.h2hMatchesBody.innerHTML = payload.matches
        .map((match) => {
            return `
                <tr>
                    <td>${escapeHtml(match.date)}</td>
                    <td>${escapeHtml(match.score)}</td>
                    <td>${escapeHtml(match.venue || "-")}</td>
                </tr>
            `;
        })
        .join("");
}

async function loadHeadToHead({ team1, team2, season }) {
    refs.h2hResult.innerHTML = `<p class="muted">Comparing teams...</p>`;
    setLoadingRow(refs.h2hMatchesBody, 3);
    const payload = await request(endpoints.headToHead, { team1, team2, season });
    renderHeadToHead(payload);
}

function bindForms() {
    refs.leaderboardForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(refs.leaderboardForm);
        try {
            await loadLeaderboard({
                metric: formData.get("metric"),
                season: formData.get("season"),
                limit: formData.get("limit"),
            });
        } catch (error) {
            showToast(error.message);
            renderEmptyRow(refs.leaderboardBody, 6, "Unable to load leaderboard.");
        }
    });

    refs.standingsForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const season = new FormData(refs.standingsForm).get("season");
        try {
            await loadStandings({ season });
        } catch (error) {
            showToast(error.message);
            renderEmptyRow(refs.standingsBody, 7, "Unable to load standings.");
        }
    });

    refs.summaryForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const season = new FormData(refs.summaryForm).get("season");
        try {
            await loadSummary(season);
        } catch (error) {
            showToast(error.message);
            refs.summaryCard.innerHTML = `<p class="muted">Unable to load summary.</p>`;
        }
    });

    refs.h2hForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(refs.h2hForm);
        const team1 = formData.get("team1");
        const team2 = formData.get("team2");
        const season = formData.get("season");

        if (!team1 || !team2) {
            showToast("Please select two teams.");
            return;
        }
        if (team1 === team2) {
            showToast("Choose two different teams.");
            return;
        }

        try {
            await loadHeadToHead({ team1, team2, season });
        } catch (error) {
            showToast(error.message);
            refs.h2hResult.innerHTML = `<p class="muted">Unable to load head-to-head data.</p>`;
            renderEmptyRow(refs.h2hMatchesBody, 3, "No match history to display.");
        }
    });
}

async function bootstrap() {
    wireRevealAnimations();
    bindForms();

    setLoadingRow(refs.leaderboardBody, 6);
    setLoadingRow(refs.standingsBody, 7);
    setLoadingRow(refs.h2hMatchesBody, 3, "Select two teams and click Compare.");

    try {
        await Promise.all([loadKpis(), populateTeamSelectors()]);
    } catch (error) {
        showToast(`Startup load failed: ${error.message}`);
    }

    try {
        await loadLeaderboard({ metric: "goals", limit: 10 });
    } catch (error) {
        showToast(error.message);
        renderEmptyRow(refs.leaderboardBody, 6, "Unable to load leaderboard.");
    }

    try {
        await loadStandings();
    } catch (error) {
        showToast(error.message);
        renderEmptyRow(refs.standingsBody, 7, "Unable to load standings.");
    }

    if (state.latestSeason) {
        const summarySeasonInput = refs.summaryForm.querySelector("input[name='season']");
        summarySeasonInput.value = state.latestSeason;
        try {
            await loadSummary(state.latestSeason);
        } catch (error) {
            showToast(error.message);
        }
    }
}

document.addEventListener("DOMContentLoaded", bootstrap);
