## Summary
For **all changes**, provide a concise overview of what's included in this PR.
For **larger changes**, explain the customer journey (CUJ) you're addressing and how these changes solve it.

- [ ] **Breaking Change**: This PR introduces backward incompatible changes (Attempting to use the API on resources created by previous versions results in an error.)
  - If checked, explain impact and migration plan:

## SDK Example
Demonstrate how users will use the new API feature in their code:

```python
# Example: Adding a new field in model_plan
model_plan.new_field = 'abc'
trainer = kumo.Trainer(model_plan)
trainer.fit(...)

# Example output (if applicable):
# > Training started with new_field: abc
