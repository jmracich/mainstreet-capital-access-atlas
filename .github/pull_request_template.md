## Summary

- 

## Type of Change

- [ ] Data source or adapter
- [ ] Scoring or methodology
- [ ] Site/template/design
- [ ] Documentation
- [ ] Tests or workflow

## Data Provenance

- [ ] Uses only public, non-sensitive data.
- [ ] Does not fabricate official values.
- [ ] Adds or updates source manifest details when source behavior changes.
- [ ] Documents manual import format when automation is not reliable.

## Language and Limitations

- [ ] Does not frame the atlas as a credit model, underwriting tool, or directive for lending/investment decisions.
- [ ] Keeps missingness, source vintage, and limitations visible.
- [ ] Avoids stigmatizing labels for people, places, and communities.

## Verification

- [ ] `python -m mainstreet_atlas.cli all`
- [ ] `python -m pytest`
- [ ] `python -m ruff check .`
- [ ] Browser/site smoke check, if templates or static assets changed.

## Notes

Any known limitations, source caveats, or follow-up work:
