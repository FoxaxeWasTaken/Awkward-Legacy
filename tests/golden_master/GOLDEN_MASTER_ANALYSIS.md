# Golden Master Testing: Problems and Solutions

## The Golden Master Dilemma

Let's break down why HTML golden master testing is problematic and explore better alternatives.

## Current Golden Master Problems

### 1. HTML Fragility Example

**Scenario**: Developer changes a CSS class name
```html
<!-- Before -->
<div class="person-info">
  <h1>anthoine geruzet</h1>
  <p>Born: 1850</p>
</div>

<!-- After -->
<div class="person-details">  <!-- Just changed class name -->
  <h1>anthoine geruzet</h1>
  <p>Born: 1850</p>
</div>
```

**Result**: Every single test fails, even though functionality is identical.

### 2. Whitespace Hell
```html
<!-- Before -->
<div class="person">
<h1>anthoine geruzet</h1>
</div>

<!-- After (just added indentation) -->
<div class="person">
  <h1>anthoine geruzet</h1>  <!-- Added 2 spaces -->
</div>
```

**Result**: All tests fail due to whitespace differences.

### 3. Dynamic Content Issues
```html
<!-- Golden master captured this: -->
<div>Last updated: 2024-01-15 14:30:22</div>

<!-- Current test generates this: -->
<div>Last updated: 2024-01-15 14:30:23</div>  <!-- 1 second difference -->
```

**Result**: Test fails due to timestamp differences.

### 4. Vue.js Migration Apocalypse

**Current Geneweb**: Server-side rendered HTML
```html
<div class="person-list">
  <div class="person-item">anthoine geruzet</div>
  <div class="person-item">marie dupond</div>
</div>
```

**Future Vue.js**: Client-side rendered
```html
<div id="app">
  <!-- Vue.js renders this dynamically -->
  <person-list-component></person-list-component>
</div>
```

**Result**: ALL golden master files become useless. Every test fails.

## Why Golden Master Was Chosen (Historical Context)

### Original Bash Script Logic
```bash
# The original approach was simple but flawed
crl "m=S&n=$FN+$SN&p="  # Make request
if test "$test_diff"; then
    # Save HTML output
    mv /tmp/tmp.txt /tmp/run/$fn.txt
    # Later compare with diff
    diff $test_dir/ref/$xx /tmp/run/$xx
fi
```

### What They Were Actually Testing
The original developers were trying to catch:
1. **Crashes**: Server returning error pages
2. **Missing data**: Empty responses or "No results found"
3. **Broken links**: 404 errors or malformed URLs

But they accidentally created a system that also fails on:
1. **CSS changes**: Harmless styling updates
2. **Whitespace**: Formatting improvements
3. **Template updates**: UI modernization
4. **Dynamic content**: Timestamps, session IDs

## Better Testing Strategies

### 1. Functional Assertions (Recommended)

**Instead of**: Comparing entire HTML
**Do**: Assert specific functionality

```python
def test_person_search_functional():
    """Test that person search returns correct results."""
    response = client.get("/search?m=S&n=anthoine+geruzet")

    # Test HTTP success
    assert response.status_code == 200

    # Test functional behavior
    assert "anthoine geruzet" in response.text.lower()
    assert "search results" in response.text.lower()

    # Test no error messages
    assert "error" not in response.text.lower()
    assert "not found" not in response.text.lower()

    # Optional: Test HTML structure if needed
    soup = BeautifulSoup(response.text, 'html.parser')
    assert soup.select_one('.search-results')  # Results container exists
    assert len(soup.select('.person-item')) > 0  # At least one result
```

### 2. Semantic HTML Testing

**Instead of**: Exact HTML matching
**Do**: Test semantic content

```python
def test_person_display_semantic():
    """Test person display contains expected information."""
    response = client.get(f"/person/{person_id}")
    soup = BeautifulSoup(response.text, 'html.parser')

    # Test semantic content (survives CSS changes)
    person_name = soup.select_one('[data-testid="person-name"]')
    assert person_name and "anthoine geruzet" in person_name.text

    birth_date = soup.select_one('[data-testid="birth-date"]')
    assert birth_date and "1850" in birth_date.text

    # Test navigation links work
    ancestor_link = soup.select_one('a[href*="m=A"]')
    assert ancestor_link is not None
```

### 3. JSON API Testing (Future-Proof)

**Best approach**: Test data, not presentation

```python
def test_person_api():
    """Test person data via API (future-proof)."""
    response = client.get(f"/api/persons/{person_id}")
    data = response.json()

    # Test actual data (survives any frontend changes)
    assert data["id"] == person_id
    assert data["first_name"] == "anthoine"
    assert data["last_name"] == "geruzet"
    assert data["birth_year"] == 1850

    # Test relationships
    assert "families" in data
    assert "parents" in data
```

### 4. Component Testing (Vue.js Ready)

**For future Vue.js**: Test components directly

```javascript
// PersonDisplay.test.js
import { mount } from '@vue/test-utils'
import PersonDisplay from '@/components/PersonDisplay.vue'

test('PersonDisplay shows person information', () => {
  const person = {
    id: 26,
    firstName: "anthoine",
    lastName: "geruzet",
    birthYear: 1850
  }

  const wrapper = mount(PersonDisplay, {
    props: { person }
  })

  // Test component behavior, not HTML structure
  expect(wrapper.text()).toContain("anthoine geruzet")
  expect(wrapper.text()).toContain("1850")
  expect(wrapper.find('[data-testid="person-name"]').exists()).toBe(true)
})
```

## Migration Strategy

### Phase 1: Parallel Testing (Current)
- Keep HTML golden master for now (legacy compatibility)
- Add functional tests alongside HTML tests
- Start building confidence in functional tests

```python
def test_person_search():
    """Test person search with both approaches."""
    response = client.get("/search?m=S&n=anthoine+geruzet")

    # Legacy HTML comparison (fragile but familiar)
    if config.mode == TestMode.COMPARE:
        compare_html_output(response.text, "search_person.html")

    # New functional testing (robust)
    assert response.status_code == 200
    assert "anthoine geruzet" in response.text.lower()
    assert_no_error_messages(response.text)
```

### Phase 2: Functional First
- Run functional tests by default
- HTML golden master becomes optional
- Start identifying which HTML tests can be removed

### Phase 3: HTML Deprecation
- Mark HTML golden master as deprecated
- Focus on functional and API testing
- Prepare for Vue.js migration

### Phase 4: HTML Removal
- Remove HTML golden master entirely
- Pure functional/API/component testing
- Vue.js migration ready

## Practical Implementation

### Current Structure Enhancement
```python
class BetterTestRunner:
    def test_person_search(self):
        """Multi-layer testing approach."""
        response = self.client.get("/search", params={"m": "S", "n": "anthoine+geruzet"})

        # Layer 1: HTTP Success
        assert response.status_code == 200

        # Layer 2: No Server Errors
        assert "error" not in response.text.lower()
        assert "exception" not in response.text.lower()

        # Layer 3: Expected Content
        assert "anthoine geruzet" in response.text.lower()

        # Layer 4: Functional Elements (optional)
        soup = BeautifulSoup(response.text, 'html.parser')
        assert soup.select_one('.search-results')

        # Layer 5: HTML Golden Master (legacy, optional)
        if self.config.enable_html_comparison:
            self.compare_html(response.text, "search_person.html")
```

### Configuration for Gradual Migration
```python
@dataclass
class TestConfiguration:
    # Golden master controls
    enable_html_comparison: bool = False  # Disable by default
    html_comparison_mode: str = "optional"  # "required", "optional", "disabled"

    # Functional testing controls
    enable_functional_tests: bool = True
    strict_assertions: bool = True

    # Future API testing
    api_base_url: Optional[str] = None
    enable_api_tests: bool = False
```

## Conclusion

The HTML golden master approach is fundamentally flawed:

1. **Too fragile**: Breaks on harmless changes
2. **Not semantic**: Tests presentation, not function
3. **Vue.js incompatible**: Will become useless during migration
4. **High maintenance**: Requires constant reference file updates

### Recommended Approach

1. **Keep Python structure** - The organization is good
2. **Split into modules** - 850 lines is too much
3. **Replace golden master gradually** - Don't break existing workflow
4. **Focus on functional testing** - Test behavior, not HTML
5. **Prepare for Vue.js** - API and component testing

### The Real Value

The real value of the Python rewrite isn't the golden master - it's:
- **Better organization** than shell script
- **Easier to extend** with new test types
- **More robust error handling**
- **Foundation for modern testing** (functional, API, component)

The golden master was inherited from the bash script's flawed approach. The Python structure gives us the foundation to do much better testing.
