# Accessibility

Main Street Capital Access Atlas is intended for public-interest use by a wide range of community partners. Accessibility is part of the project quality bar, not a separate enhancement.

## Current Commitments

The project aims to:

- Use semantic HTML landmarks, headings, lists, tables, and links.
- Provide keyboard-friendly navigation and visible focus styles.
- Keep limitations, source notes, and non-map alternatives available without relying only on the interactive map.
- Preserve sufficient color contrast for text, controls, and data labels.
- Keep the static site responsive across mobile and desktop viewports.
- Avoid requiring user accounts, tracking scripts, private data, or paid services.

## Known Constraints

The homepage map is interactive and JavaScript-dependent. The site also provides non-map alternatives, including county search, county tables, downloadable CSV files, generated county briefs, and `noscript` fallback content.

County-level data can still be difficult to interpret with assistive technology when tables are wide or metrics are dense. Contributions that improve table semantics, text alternatives, keyboard flow, and plain-language summaries are welcome.

## Testing

The test suite includes static accessibility checks for representative generated pages. These checks cover landmarks, one H1, page metadata, skip-link targets, primary navigation labeling, mobile menu ARIA state, focus-visible CSS, and Escape-key menu support.

Manual browser checks should still be performed before public release, especially after template, CSS, JavaScript, or map changes.

## Report An Accessibility Issue

Open an accessibility issue with:

- The page URL or generated file path.
- The browser, device, assistive technology, or viewport involved.
- The expected behavior and observed behavior.
- Screenshots or short recordings when they help explain the issue and do not expose private information.

Do not include private, sensitive, or personally identifiable information in public issues.
