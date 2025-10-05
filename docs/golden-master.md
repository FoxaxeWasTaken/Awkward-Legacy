# Rethinking the Golden Master Approach

## Context

After some times exploring how to modernize the old **GeneWeb Golden Master script** (`run_gw_test.sh`), we realized that maintaining this approach no longer made sense for our modernization goals.

Originally, the plan was to rewrite the legacy test script in Python and keep its **Golden Master testing** strategy — i.e., capturing and comparing full HTML outputs for each page.
After deeper analysis, we decided **not to pursue the Golden Master approach** in the new version of GeneWeb.

This document explains **why** and what **alternative testing strategy** we’ll adopt instead.

---

## 1. Why We Dropped Golden Master Testing

### Legacy Behavior

The original shell script did this:
1. Load a GeneWeb page (e.g., `?m=S&n=anthoine+geruzet`)
2. Save the **entire HTML** output to a `.txt` file
3. Compare it byte-for-byte against a reference file

This helped detect regressions — but at a huge cost.

### Why It Doesn’t Work Anymore

| Problem | Description |
|----------|--------------|
| **1. HTML Fragility** | Any tiny change (CSS class name, whitespace, indentation) causes all tests to fail, even when functionality is identical. |
| **2. Dynamic Content** | Timestamps, session IDs, or localized strings constantly break diffs. |
| **3. No API Layer** | GeneWeb’s legacy backend doesn’t expose JSON or REST endpoints to test data semantically — only raw HTML. |
| **4. Migration Incompatibility** | The new version will move toward a **modern stack (Python + Vue.js)**; HTML golden masters would instantly become obsolete. |
| **5. Low ROI** | Huge maintenance cost for tests that don’t provide meaningful functional coverage. |

In short: **Golden Master tests are too brittle, too coupled to the presentation layer, and incompatible with the system we’re building.**

---

## 2. What We’ll Do Instead

### Focus on Behavior, Not Pixels

Our new strategy aligns with **modern software testing principles**:

#### **A. TDD (Test-Driven Development)**

We’ll:
- Start by observing **how the legacy feature behaves**
- Write **clear, functional tests** that describe this behavior
- Then reimplement the feature in the new codebase
- Validate with those same tests

This ensures we preserve **intended behavior** while modernizing the implementation.

#### **B. BDD (Behavior-Driven Development)**

We already have `.feature` files that describe scenarios in plain English.

Example:
```gherkin
Feature: Search for a person
  Scenario: Searching for Anthoine Geruzet
    Given I am on the search page
    When I search for "anthoine geruzet"
    Then I should see "Anthoine Geruzet" in the results
```

We’ll **keep these `.feature` files** as documentation and testing artifacts:
- They serve as **BDD specs** and human-readable test cases.
- We can later automate them using **Behave**, **Cucumber**, or **Playwright**.

#### **C. Functional & E2E Tests**

We’ll prioritize:
- **Unit tests** → For backend logic (Python)
- **Functional tests** → For routes, API endpoints, and database logic
- **E2E tests** → For user flows once the new frontend exists (with Playwright or Cypress)

Example (Functional Test in Python):
```python
def test_search_person(client):
    response = client.get("/search?name=anthoine+geruzet")
    assert response.status_code == 200
    assert "anthoine geruzet" in response.text.lower()
```

Example (E2E Test in Playwright):
```javascript
test('search for person', async ({ page }) => {
  await page.goto('/search');
  await page.fill('input[name="query"]', 'anthoine geruzet');
  await page.click('button[type="submit"]');
  await expect(page.locator('.results')).toContainText('Anthoine Geruzet');
});
```

## 3. How We’ll Handle Legacy Behavior

Even if we don’t use Golden Master testing, we still want to **understand and preserve the legacy behavior**.

For each feature we rebuild:
1. **Take notes** on how the old GeneWeb behaves (inputs, outputs, edge cases)
2. **Write tests** that describe that expected behavior
3. **Reimplement** the feature in the new codebase
4. **Validate** through those tests — not HTML diffs

This way, we still honor the *spirit* of Golden Master testing — preserving behavior — but in a **cleaner, more maintainable way**.

---

## 4. Summary of Our Testing Strategy

| Layer | Type | Tool / Example |
|--------|------|----------------|
| **Backend** | Unit tests | `pytest`, asserts on logic & DB |
| **Integration** | Functional tests | Test Flask/FastAPI routes |
| **Frontend** | Component tests | Vue Test Utils |
| **E2E** | User-flow tests | Playwright / Cypress |
| **Documentation** | BDD features | `.feature` files kept as reference |

---

## 5. Why This Makes More Sense

| Legacy Golden Master | New Testing Approach |
|-----------------------|----------------------|
| Brittle HTML comparisons | Stable, behavior-based assertions |
| Coupled to presentation | Tests logic, API, and user behavior |
| Difficult to maintain | Modular, automated, scalable |
| Obsolete after migration | Future-proof and tech-agnostic |
| No understanding of intent | Clear, human-readable scenarios |

---

## 6. Conclusion

The Golden Master approach was valuable for its time — it gave early GeneWeb developers a quick way to spot regressions.
But for our migration and modernization goals, it **adds more friction than value**.

We’ll instead:
- Observe legacy behavior
- Write behavior-driven tests (TDD + BDD)
- Reimplement features cleanly
- Keep `.feature` files as living documentation

This ensures our new version of GeneWeb is **better tested**, **easier to maintain**, and **future-proof** — without carrying over the fragility of HTML Golden Master testing.
