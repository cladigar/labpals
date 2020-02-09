# labpals
LabPals website repo

# GitHub cheatsheet: Shared repository model
_from https://uoftcoders.github.io/studyGroup/lessons/git/collaboration/lesson/_

- For small projects where you are basically in the same physical space (e.g. lab with offices near each other).
- Be careful! You are cloning the main repository.
- Everyone has push and pull access to the central repo, so be careful and:
  - Never commit to the master directly.
  - Always do your work on a different branch from master.

### Basic workflow

- update your local repo with `git pull origin master`
- create a working branch with `git checkout -b MyNewBranch`
- make your changes on your branch and stage them with `git add`
- commit your changes locally with `git commit -m "description of your commit"`
- upload the changes (including your new branch) to GitHub with `git push origin MyNewBranch`  
  
Go to the main repo on GitHub where you should now see your new branch
- click on your branch name
- click on “Pull Request” button (URC)
- click on “Send Pull Request”

