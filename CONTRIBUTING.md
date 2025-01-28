# How to Contribute

We would love to accept your patches and contributions to this project.

## Contribution process

### :raised_hand: Self Assigning to an Issue

If you find an issue you'd like to work on, simply type and submit a comment
with the phrase `.take` in it to get assigned by our github actions.

### :pencil2: Pull Request Guidelines

1. Code must finish continuous integration steps before it will be reviewed.
2. Commit messages should follow these guidelines here
   https://cbea.ms/git-commit/.
3. Pull requests should contain a single commit
4. Pull requests should be small and implement a single feature where possible.
   If it can be broken up into separate parts it most likely should be.
5. Each PR should have an associated issue with it. Exceptions are made for very
   small PRs such as fixing typos, fixing up documentation or removing
   unnecessary headers.

### Code Reviews

All submissions, including submissions by project members, require review. We
use [GitHub pull requests](https://docs.github.com/articles/about-pull-requests)
for this purpose.

## How to test CI

In general, when you make PR, all you will need to perform a test is
`.github/workflows/self_check.yml`. If you added a new workflow action, make
sure to add it to the `self_check.yml` so it is tested in PRs and by the repo's
`cron` job.

### ⛔️ Testing failure modes

In many cases, you'll want to test what happens when something fails. Using
`self_test.yml` is not sufficient if all of the tests are passing on their main
branch. You technically "could" introduce a CI breaking change to a repo in
order to test CI, but that would be disruptive to developers.

Instead, to test this you can go to any repo that is using `libhal/ci` with
fully passing CI and introduce a change that will break your new CI. You will
need to change the workflow in the repo's `.github/` directory to point to your
fork or branch's changes.

To prove that a change successfully updates the failure mode of CI, one commit
should be pushed with the breaking change added, and another commit that
reverts the breaking change but add some other change that ensures that the PR
isn't identical to main. A link and screenshot of the github action showing the
successful failure mode should be added as a comment to the CI PR. Also include
a screenshot of the commit that reverts the change and show that the CI works
as intended when the code is conforming.
