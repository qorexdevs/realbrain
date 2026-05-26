## Summary

What does this change?

## Type of change

- [ ] Docs
- [ ] Example / adapter
- [ ] Core library
- [ ] Tests / benchmarks
- [ ] Packaging / release
- [ ] Safety / privacy

## Checks

- [ ] `python -m unittest discover -s tests`
- [ ] `python -m compileall realbrain realbrain_server examples tests`
- [ ] `python examples/demo.py` if the demo path is affected
- [ ] No secrets, private vault contents, generated DBs, `.env` files, or user-specific paths are committed

## Safety boundaries

- [ ] This keeps RealBrain local-first by default
- [ ] This does not add autonomous external actions
- [ ] Dream/consolidation output remains hypothesis/suggestion only
- [ ] Host runtimes still own identity, approvals, secrets, and external tools
