(function (global) {
  "use strict";

  var STORAGE_KEY = "routines.v1";
  var SLOTS = ["morning", "afternoon", "evening", "anytime"];

  /* ----- Pure helpers (unit-testable, no DOM) ----- */

  function dateKey(date) {
    var y = date.getFullYear();
    var m = String(date.getMonth() + 1).padStart(2, "0");
    var d = String(date.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + d;
  }

  function addDays(key, delta) {
    var parts = key.split("-");
    var dt = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    dt.setDate(dt.getDate() + delta);
    return dateKey(dt);
  }

  function isDoneOn(routine, key) {
    return routine.history.indexOf(key) !== -1;
  }

  // Consecutive completed days ending at today (or yesterday if today is not
  // yet done, so an in-progress streak isn't shown as broken before day's end).
  function computeStreak(routine, todayKey) {
    var set = {};
    routine.history.forEach(function (k) {
      set[k] = true;
    });

    var cursor;
    if (set[todayKey]) {
      cursor = todayKey;
    } else if (set[addDays(todayKey, -1)]) {
      cursor = addDays(todayKey, -1);
    } else {
      return 0;
    }

    var streak = 0;
    while (set[cursor]) {
      streak += 1;
      cursor = addDays(cursor, -1);
    }
    return streak;
  }

  function toggleDone(routine, key) {
    var idx = routine.history.indexOf(key);
    if (idx === -1) {
      routine.history.push(key);
      routine.history.sort();
    } else {
      routine.history.splice(idx, 1);
    }
    return routine;
  }

  function countDoneToday(routines, todayKey) {
    return routines.filter(function (r) {
      return isDoneOn(r, todayKey);
    }).length;
  }

  function makeRoutine(name, slot) {
    return {
      id: "r" + Date.now() + Math.random().toString(36).slice(2, 7),
      name: String(name).trim(),
      slot: SLOTS.indexOf(slot) === -1 ? "anytime" : slot,
      createdAt: new Date().toISOString(),
      history: [],
    };
  }

  var logic = {
    SLOTS: SLOTS,
    dateKey: dateKey,
    addDays: addDays,
    isDoneOn: isDoneOn,
    computeStreak: computeStreak,
    toggleDone: toggleDone,
    countDoneToday: countDoneToday,
    makeRoutine: makeRoutine,
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = logic;
  }

  /* ----- DOM wiring (browser only) ----- */

  if (typeof document === "undefined") {
    return;
  }

  var RING_CIRCUMFERENCE = 175.93; // 2 * pi * r (r = 28)
  var state = { routines: [], filter: "all" };
  var els = {};

  function load() {
    try {
      var raw = global.localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      var parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return [];
      return parsed.filter(function (r) {
        return r && typeof r.name === "string" && Array.isArray(r.history);
      });
    } catch (e) {
      return [];
    }
  }

  function save() {
    try {
      global.localStorage.setItem(STORAGE_KEY, JSON.stringify(state.routines));
    } catch (e) {
      /* storage unavailable — keep working in-memory */
    }
  }

  function todayKey() {
    return dateKey(new Date());
  }

  function visibleRoutines() {
    if (state.filter === "all") return state.routines;
    return state.routines.filter(function (r) {
      return r.slot === state.filter;
    });
  }

  function render() {
    var today = todayKey();
    var list = els.list;
    list.textContent = "";

    var items = visibleRoutines();
    els.empty.hidden = items.length !== 0;

    items.forEach(function (r) {
      list.appendChild(renderItem(r, today));
    });

    var done = countDoneToday(state.routines, today);
    var total = state.routines.length;
    els.progressLabel.textContent = done + "/" + total;
    var ratio = total === 0 ? 0 : done / total;
    els.ringFill.style.strokeDashoffset = String(
      RING_CIRCUMFERENCE * (1 - ratio)
    );

    var bestStreak = state.routines.reduce(function (max, r) {
      return Math.max(max, computeStreak(r, today));
    }, 0);
    els.streakSummary.textContent =
      total === 0 ? "" : "Best streak: " + bestStreak + " day" + (bestStreak === 1 ? "" : "s");
  }

  function renderItem(routine, today) {
    var li = document.createElement("li");
    li.className = "item" + (isDoneOn(routine, today) ? " is-done" : "");

    var check = document.createElement("input");
    check.type = "checkbox";
    check.className = "item__check";
    check.checked = isDoneOn(routine, today);
    check.setAttribute("aria-label", "Mark " + routine.name + " done for today");
    check.addEventListener("change", function () {
      toggleDone(routine, today);
      save();
      render();
    });

    var body = document.createElement("div");
    body.className = "item__body";

    var name = document.createElement("div");
    name.className = "item__name";
    name.textContent = routine.name;

    var meta = document.createElement("div");
    meta.className = "item__meta";

    var slot = document.createElement("span");
    slot.className = "item__slot";
    slot.textContent = routine.slot;
    meta.appendChild(slot);

    var streak = computeStreak(routine, today);
    if (streak > 0) {
      var streakEl = document.createElement("span");
      streakEl.className = "item__streak";
      streakEl.textContent = "🔥 " + streak + " day" + (streak === 1 ? "" : "s");
      meta.appendChild(streakEl);
    }

    body.appendChild(name);
    body.appendChild(meta);

    var del = document.createElement("button");
    del.className = "item__delete";
    del.type = "button";
    del.textContent = "×";
    del.setAttribute("aria-label", "Delete " + routine.name);
    del.addEventListener("click", function () {
      state.routines = state.routines.filter(function (r) {
        return r.id !== routine.id;
      });
      save();
      render();
    });

    li.appendChild(check);
    li.appendChild(body);
    li.appendChild(del);
    return li;
  }

  function init() {
    els.list = document.getElementById("list");
    els.empty = document.getElementById("empty");
    els.progressLabel = document.getElementById("progressLabel");
    els.ringFill = document.getElementById("ringFill");
    els.streakSummary = document.getElementById("streakSummary");
    els.todayLabel = document.getElementById("todayLabel");

    els.todayLabel.textContent = new Date().toLocaleDateString(undefined, {
      weekday: "long",
      month: "long",
      day: "numeric",
    });

    document.getElementById("addForm").addEventListener("submit", function (e) {
      e.preventDefault();
      var nameInput = document.getElementById("nameInput");
      var slotInput = document.getElementById("slotInput");
      var name = nameInput.value.trim();
      if (!name) return;
      state.routines.push(makeRoutine(name, slotInput.value));
      nameInput.value = "";
      nameInput.focus();
      save();
      render();
    });

    document.getElementById("filters").addEventListener("click", function (e) {
      var btn = e.target.closest(".filters__btn");
      if (!btn) return;
      state.filter = btn.dataset.filter;
      Array.prototype.forEach.call(
        e.currentTarget.querySelectorAll(".filters__btn"),
        function (b) {
          b.classList.toggle("is-active", b === btn);
        }
      );
      render();
    });

    document.getElementById("resetDay").addEventListener("click", function () {
      var today = todayKey();
      state.routines.forEach(function (r) {
        var idx = r.history.indexOf(today);
        if (idx !== -1) r.history.splice(idx, 1);
      });
      save();
      render();
    });

    state.routines = load();
    render();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : globalThis);
