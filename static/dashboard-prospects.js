function buildColdEmailPrompt(data) {
    const name = data.name || "Onbekend bedrijf";
    const region = data.region || "onbekende regio";
    const category = data.category || "onbekend type (leid af uit naam/regio)";
    const website = data.website && data.website.trim()
        ? data.website
        : "geen website gevonden door onze scraper, bevestig dit via eigen onderzoek (andere schrijfwijzes, Facebook/Instagram als site, Google Business Profile) voordat je concludeert dat ze er geen hebben";

    return `You are Sander Pelgrims, a freelance full stack web developer (sqnder.dev),
writing short, high-reply cold emails to local businesses in Flanders.

<context>
I need one cold email, ready to send, that opens a conversation with a
local business owner who has never heard of me. Before writing anything,
you must research the specific business so the email is grounded in real
findings instead of guesses. The final email must be copy-ready after
swapping placeholders, written in Dutch (informal "je" form, Flemish tone).
</context>

<inputs>
- Prospect: ${name}, ${category} in ${region}
- Known website (from our internal scrape, verify before relying on it): ${website}
- What I can offer, depending on what they actually need: a new or
  improved website, online ordering, a booking system, SEO, a digital
  menu, review management, or another technical upgrade
- Sender name and site: Sander Pelgrims, sqnder.dev
</inputs>

<research>
Before drafting the email, research ${name} using whatever is
available (web search, their website if one exists, Google Maps and
reviews, social media). Work out:

1. Problem: what is this business's concrete problem regarding online
   visibility, technology, or day-to-day operations?
2. Website: do they have one? If yes, assess it in depth, mobile-friendliness,
   load speed, how current the design looks, findability on Google,
   whether it supports online ordering or reservations, and whether it
   actually converts visitors (clear CTA, contact info, menu, hours).
   If no, note that explicitly, but also do more research before
   concluding they truly have no website (check variant spellings,
   Facebook/Instagram-as-site, Google Business Profile links, a parent
   company site) rather than taking one failed search as proof.
3. Opportunities: brainstorm every realistic way I could help this
   business with web development or a technology upgrade, then narrow
   it down to the 1-2 opportunities most relevant and convincing for
   this specific business.
4. Background and qualification: research the business's background
   (how long they've existed, number of locations or staff if findable,
   estimated revenue tier, reviews and reputation, competitive pressure)
   and judge whether this looks like a good or weak client, considering
   budget signals, whether they seem to invest in the business, and red
   flags such as a business that looks like it's struggling, closing,
   or too small to afford paid work.

Summarize this in a short internal brief for myself. This brief is not
sent to the business.
</research>

<task>
Based on the research and the 1-2 chosen opportunities, write a cold
email under 120 words: a personalized one-line opener tied to what you
found (not flattery), a one-sentence framing of the problem, a specific
value claim backed by the strongest opportunity, and one low-friction
interest-check CTA. Then give 3 subject line options and 2 alternate
first-line openers.
</task>

<constraints>
- Under 120 words; no "I hope this finds you well"; exactly one CTA.
- No em dashes, use commas instead.
- Specific and human, no buzzwords like "synergy" or "revolutionary".
- The CTA asks for interest, not a big time commitment.
- Only mention a mockup if one was actually made for this business,
  otherwise point to the portfolio at sqnder.dev instead.
</constraints>

<format>
Return two parts:

Part 1, Research brief (for me, not sent): the problem, the website
assessment (or "no website"), the 1-2 strongest opportunities, and a
one-line client-quality verdict (good / uncertain / weak fit, with why).

Part 2, Copy-ready email block: 3 subject lines, the email body, 2
alternate openers, and one note on how to personalize the opener at
scale.
</format>`;
}

function buildBatchColdEmailPrompt(businesses) {
    const listing = businesses
        .map(function (b, index) {
            const name = b.name || "Onbekend bedrijf";
            const region = b.region || "onbekende regio";
            const category = b.category || "onbekend type (leid af uit naam/regio)";
            const website = b.website && b.website.trim()
                ? b.website
                : "geen website gevonden door onze scraper, bevestig dit via eigen onderzoek voordat je concludeert dat ze er geen hebben";
            return (index + 1) + ". " + name + ", " + category + " in " + region + "\n   Bekende website: " + website;
        })
        .join("\n");

    return `You are Sander Pelgrims, a freelance full stack web developer (sqnder.dev),
writing short, high-reply cold emails to local businesses in Flanders.

<context>
I'm giving you ${businesses.length} businesses below. For EACH one, independently
repeat the full process in this prompt: research it, then produce one
cold email. Do not skip any, and do not let one business's research bleed
into another's. Before writing anything for a given business, you must
research that specific business so its email is grounded in real findings
instead of guesses. Each final email must be copy-ready after swapping
placeholders, written in Dutch (informal "je" form, Flemish tone).
</context>

<businesses>
${listing}
</businesses>

<what_i_offer>
Depending on what each business actually needs: a new or improved
website, online ordering, a booking system, SEO, a digital menu, review
management, or another technical upgrade. Sender name and site: Sander
Pelgrims, sqnder.dev.
</what_i_offer>

<research_per_business>
Before drafting each email, research that business using whatever is
available (web search, their website if one exists, Google Maps and
reviews, social media). Work out:

1. Problem: what is this business's concrete problem regarding online
   visibility, technology, or day-to-day operations?
2. Website: do they have one? If yes, assess it in depth, mobile-friendliness,
   load speed, how current the design looks, findability on Google,
   whether it supports online ordering or reservations, and whether it
   actually converts visitors (clear CTA, contact info, menu, hours).
   If no, note that explicitly, but also do more research before
   concluding they truly have no website (check variant spellings,
   Facebook/Instagram-as-site, Google Business Profile links, a parent
   company site) rather than taking one failed search as proof.
3. Opportunities: brainstorm every realistic way I could help this
   business with web development or a technology upgrade, then narrow
   it down to the 1-2 opportunities most relevant and convincing for
   this specific business.
4. Background and qualification: research the business's background
   (how long they've existed, number of locations or staff if findable,
   estimated revenue tier, reviews and reputation, competitive pressure)
   and judge whether this looks like a good or weak client, considering
   budget signals, whether they seem to invest in the business, and red
   flags such as a business that looks like it's struggling, closing,
   or too small to afford paid work.

Summarize this in a short internal brief for myself, not sent to the
business.
</research_per_business>

<task_per_business>
Based on the research and the 1-2 chosen opportunities, write a cold
email under 120 words: a personalized one-line opener tied to what you
found (not flattery), a one-sentence framing of the problem, a specific
value claim backed by the strongest opportunity, and one low-friction
interest-check CTA. Then give 3 subject line options and 2 alternate
first-line openers.
</task_per_business>

<constraints>
- Under 120 words per email; no "I hope this finds you well"; exactly
  one CTA per email.
- No em dashes, use commas instead.
- Specific and human, no buzzwords like "synergy" or "revolutionary".
- The CTA asks for interest, not a big time commitment.
- Only mention a mockup if one was actually made for that business,
  otherwise point to the portfolio at sqnder.dev instead.
</constraints>

<format>
For each business, in order, output a heading with its name, then:

Part 1, Research brief (for me, not sent): the problem, the website
assessment (or "no website"), the 1-2 strongest opportunities, and a
one-line client-quality verdict (good / uncertain / weak fit, with why).

Part 2, Copy-ready email block: 3 subject lines, the email body, 2
alternate openers, and one note on how to personalize the opener at
scale.

Separate each business's output with a horizontal rule.
</format>`;
}

function setAllLeadCheckboxes(checked) {
    document.querySelectorAll(".lead-select-checkbox").forEach(function (box) {
        box.checked = checked;
    });
    syncSelectAllCheckbox();
    updateBulkCopyBar();
}

function syncSelectAllCheckbox() {
    const selectAll = document.getElementById("select-all-leads");
    const boxes = document.querySelectorAll(".lead-select-checkbox");
    if (!selectAll || !boxes.length) return;
    selectAll.checked = Array.from(boxes).every(function (box) {
        return box.checked;
    });
}

function updateBulkCopyBar() {
    const bar = document.getElementById("bulk-copy-bar");
    const countLabel = document.getElementById("bulk-copy-count");
    if (!bar || !countLabel) return;

    const checked = document.querySelectorAll(".lead-select-checkbox:checked");
    if (checked.length === 0) {
        bar.hidden = true;
        // Tailwind's .flex utility and the browser's [hidden] UA rule have
        // equal specificity, and author CSS always wins over UA CSS, so a
        // static "flex" class left on the element would keep it visible
        // regardless of the hidden attribute. Only add "flex" while shown.
        bar.classList.remove("flex");
        return;
    }
    bar.hidden = false;
    bar.classList.add("flex");
    countLabel.textContent = checked.length + " selected";
}

document.addEventListener("change", function (event) {
    if (event.target.id === "select-all-leads") {
        setAllLeadCheckboxes(event.target.checked);
        return;
    }
    if (event.target.classList.contains("lead-select-checkbox")) {
        syncSelectAllCheckbox();
        updateBulkCopyBar();
    }
});

document.addEventListener("click", function (event) {
    const btn = event.target.closest(".copy-lead-btn");
    if (btn) {
        const prompt = buildColdEmailPrompt(btn.dataset);
        navigator.clipboard.writeText(prompt).then(function () {
            const original = btn.textContent;
            btn.textContent = "Copied!";
            setTimeout(function () {
                btn.textContent = original;
            }, 1500);
        });
        return;
    }

    if (event.target.id === "select-all-visible-btn") {
        setAllLeadCheckboxes(true);
        return;
    }

    if (event.target.id === "bulk-copy-clear") {
        setAllLeadCheckboxes(false);
        return;
    }

    if (event.target.id === "bulk-copy-btn") {
        const businesses = Array.from(document.querySelectorAll(".lead-select-checkbox:checked")).map(
            function (box) {
                return box.dataset;
            }
        );
        if (!businesses.length) return;

        const prompt = buildBatchColdEmailPrompt(businesses);
        navigator.clipboard.writeText(prompt).then(function () {
            const original = event.target.textContent;
            event.target.textContent = "Copied!";
            setTimeout(function () {
                event.target.textContent = original;
            }, 1500);
        });
        return;
    }

    if (event.target.id === "bulk-delete-btn") {
        const ids = Array.from(document.querySelectorAll(".lead-select-checkbox:checked")).map(
            function (box) {
                return box.dataset.id;
            }
        );
        if (!ids.length) return;

        const confirmed = window.confirm(
            "Delete " + ids.length + " selected prospect(s)? This cannot be undone."
        );
        if (!confirmed) return;

        const form = document.getElementById("bulk-delete-form");
        if (!form) return;

        ids.forEach(function (id) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "ids";
            input.value = id;
            form.appendChild(input);
        });
        form.submit();
    }
});

const scrapeStatusBanner = document.getElementById("scrape-status-banner");
if (scrapeStatusBanner && scrapeStatusBanner.dataset.scrapeRunning === "true") {
    setTimeout(function () {
        window.location.reload();
    }, 12000);
}
