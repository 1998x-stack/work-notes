/* Work Notes: semantic HTML first, filter controls only enhance the static archive. */
(() => {
  "use strict";
  const form = document.querySelector("#archive-filters");
  const cards = Array.from(document.querySelectorAll(".note-card"));
  if (!form) return;
  const byId = (id) => document.getElementById(id);
  const search = byId("search");
  const month = byId("month");
  const topic = byId("topic");
  const kind = byId("kind");
  const from = byId("date-from");
  const to = byId("date-to");
  const count = byId("visible-count");
  const empty = byId("filter-empty");
  const topicButtons = Array.from(document.querySelectorAll("[data-topic-select]"));

  function setTopicActive() {
    for (const btn of topicButtons) {
      const active = btn.dataset.topicSelect === topic.value;
      btn.setAttribute("aria-pressed", String(active));
      btn.classList.toggle("is-active", active);
    }
  }
  function filter() {
    const q = search.value.trim().toLocaleLowerCase();
    let matched = 0;
    for (const card of cards) {
      const date = card.dataset.date || "";
      const cardTopics = (card.dataset.topics || "").split(" ").filter(Boolean);
      const show = (!q || (card.dataset.search || "").includes(q))
        && (!topic.value || cardTopics.includes(topic.value))
        && (!kind.value || card.dataset.kind === kind.value)
        && (!month.value || date.startsWith(month.value))
        && (!from.value || date >= from.value)
        && (!to.value || date <= to.value);
      card.hidden = !show;
      if (show) matched++;
    }
    document.querySelectorAll(".day-group").forEach((day) => {
      day.hidden = !day.querySelector(".note-card:not([hidden])");
    });
    document.querySelectorAll(".month-group").forEach((group) => {
      group.hidden = !group.querySelector(".note-card:not([hidden])");
    });
    if (count) count.textContent = String(matched);
    if (empty) empty.hidden = matched !== 0 || cards.length === 0;
    setTopicActive();
    const params = new URLSearchParams();
    if (q) params.set("q", search.value.trim());
    if (month.value) params.set("month", month.value);
    if (topic.value) params.set("topic", topic.value);
    if (kind.value) params.set("kind", kind.value);
    if (from.value) params.set("from", from.value);
    if (to.value) params.set("to", to.value);
    const url = window.location.pathname + (params.toString() ? "?" + params.toString() : "") + window.location.hash;
    window.history.replaceState(null, "", url);
  }
  const params = new URLSearchParams(window.location.search);
  search.value = params.get("q") || "";
  for (const [name, element] of [["month", month], ["topic", topic], ["kind", kind], ["from", from], ["to", to]]) {
    const value = params.get(name);
    if (value) element.value = value;
  }
  for (const el of [search, month, topic, kind, from, to]) {
    el.addEventListener(el === search ? "input" : "change", filter);
  }
  topicButtons.forEach((button) => button.addEventListener("click", () => {
    topic.value = button.dataset.topicSelect || "";
    filter();
    document.getElementById("archive").scrollIntoView({behavior: "smooth", block: "start"});
  }));
  form.addEventListener("reset", () => {
    /* A form reset applies after the event; clear URL and re-filter in the next microtask. */
    queueMicrotask(filter);
  });
  filter();
})();
