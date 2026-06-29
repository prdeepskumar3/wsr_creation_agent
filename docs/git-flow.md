# Git Flow

## Branches

- `main`: production-ready history.
- `develop`: integration branch for accepted feature work.
- `feature/{story-id}-{short-name}`: normal story work, for example `feature/1-0-project-setup`.
- `release/{version}`: release hardening.
- `hotfix/{issue}`: urgent production fixes.

## Pull Requests

Every implementation change should be delivered through a pull request with:

- Story link.
- Summary of changes.
- Test evidence.
- Screenshots for UI changes.
- Migration notes when schema changes.
- Risk and rollback notes.

Direct pushes to `main` and `develop` should be disabled in the remote repository.

