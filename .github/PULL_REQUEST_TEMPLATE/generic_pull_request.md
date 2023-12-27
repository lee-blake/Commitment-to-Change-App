# Summary
<!--- Describe what this PR will change -->

# Feature/Issue
<!--- Link to the feature/issue that this PR is related to. GitHub will automatically create a link that will close your issue when the PR is merged if you use the following syntax:

Resolves [issue-path]

- If the issue and PR are in the same repository, just use [#issue-number] for the [issue-path]
  - For example: Resolves #35

- If the issue is in a different repository, use [repository-owner-name/repository-name#issue-number] for the [issue-path]
  - For example: Resolves lee-blake/CME-Commitment-to-Change#35

If your PR only makes partial progress on the feature/issue, use something like:

Part of [issue-path]

This will still link the issue and will show the PR in the issue log as a mention. DO NOT use language like "partially resolves" because it will automatically close the issue.

DO NOT use an actual URL for the [issue-path]. If you do, GitHub will not correctly link the issue to your PR.

If there's not a corresponding feature/issue, either make one if that makes sense or note why this change is worth making.
-->

# Documentation
<!--- You can delete this section if the documentation does not need to change. If it does, either link your documentation changes here in a pull request like so:

Changed in [link to documentation PR]

Otherwise note the general changes that still need to be written. -->

# Special Considerations 
<!--- This section can be discarded in none of the below headings are applicable. -->

## Migrations
<!--- Will this trigger migrations? If so, note it here. If the migrations include one or more new fields that are required, provide a one-off default that will work for them. -->

## Testing
<!--- Is anything special (beyond pytest) needed to test these changes? If so, note it here. -->

## Merging
<!--- Will merging this PR require anything special action from the team when they update their projects? If so, note it here. -->

## Additional dependencies 
<!--- If there's a new Python module needed, be sure to update requirements.txt. You should also include it in this section so people know they need to update their environment. If it's something else, be sure to note it here with any required instructions. -->

## Docker changes
<!--- If team members need to rebuild their Docker containers, note it here. -->

## Do not merge immediately
<!--- If you do not want someone to merge these changes as soon as reviews are done and tests pass, note it here with a quick sentence explaining why. -->

# Checklist 
- [ ] I ran the automated tests on my development environment before opening this PR.
- [ ] I manually tested that any features I implemented on this PR work.
- [ ] I have verified that any new code I have written has been covered with tests, if possible.
- [ ] I have done my best to leave the codebase better than I have found it with this PR.
