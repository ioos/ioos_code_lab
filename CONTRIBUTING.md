# Contribution guidance

This page documents the procedures for:

1. [Requesting new notebooks](#requesting-new-notebooks) to be added to the [IOOS CodeLab](https://ioos.github.io/ioos_code_lab);
1. [Building](#building-new-notebooks) new notebooks;
1. [Reviewing](#reviewing) submitted notebooks;
1. [Merging](#merging) approved notebooks for inclusion into the Code Gallery;
1. [Announcing](#announcing) the new notebooks to the community; and
1. [Logging any bugs](#logging-bugs) that are found in the Code Gallery.
1. Managing the IOOS Data Demo Center [Project Board](#managing-ioos-data-demo-center-project-board).
1. [Local management](#local-management-of-notebooks_demo) of the notebooks_demo repository.

## Requesting new notebooks

- New notebooks should be requested by adding a [ticket](https://github.com/ioos/ioos_code_lab/issues/new) to this GitHub repository. The ticket should contain the following information:

```
- [ ] What is language(s) for used in the example?
- [ ] Is it focused on a particular module/software or an IOOS data service?
- [ ] Can you provide a minimum example of the expected code and results in a notebook?

Please provide a detailed description of the suggested example below:
```

### For the admin

When the ticket gets created, make the following additions to the ticket:

- Add the label [Notebook idea](https://github.com/ioos/ioos_code_lab/labels/Notebook%20idea).
- Add the ticket to the [IOOS CodeLab](https://github.com/orgs/ioos/projects/1#card-49928448) project.
- Put the card in the column [backlog](https://github.com/orgs/ioos/projects/1#column-5010196).

## Building new notebooks

If you would like to work on a notebook that has been proposed, follow these steps:

1. [Create a fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) of the [notebooks_demos](https://github.com/ioos/ioos_code_lab) repository.
1. On your fork, [create a branch](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-and-deleting-branches-within-your-repository) where you will start working on the new notebook.
   1. Give the branch a name that conveys what the new notebook is. For example, a notebook on converting data into Darwin Core could have a branch name of `data2dwc`. This makes it easier to know which branch is dedicated to which new notebook.
1. On the new branch in your fork, start creating the new notebook.
   1. Notebooks are kept in the [jupyterbook/content/code_gallery](https://github.com/ioos/ioos_code_lab/tree/main/jupyterbook/content/code_gallery) directory of this repository.
      1. There are three directories where notebooks can be placed:
         1. `data_access_notebooks` -
         1. `data_analysis_and_visualization_notebooks` -
         1. `data_management_notebooks` -
   1. Typically, it's best to copy an existing (working) notebook to a new file. If you are creating a python notebook, copy one of the python notebooks. If you are creating an R notebook, copy one of the R notebooks, etc
   1. Name the notebook following the convention `[date]-[short name].ipynb`. Where, `[date]` is the date (YYYY-MM-DD) you started the new notebook and `[short name]` is an abbreviation for what the notebook will cover. Look at the existing notebook filenames to get a sense of the short names used.
1. Edit the notebook following the [Jupyter Notebook documentation](https://jupyter-notebook.readthedocs.io/en/stable/notebook.html). The notebook should include the following information:
   1. Descriptive title for what the notebook is doing.
   1. A short summary providing context and expanding on the title.
   1. The date you started (or updated) the notebook.
1. Once you feel comfortable with your notebook, [commit](https://github.com/git-guides/git-commit) your work to the branch on your fork on your local machine.
1. [Push](https://github.com/git-guides/git-push) your commit up to the branch on your fork in GitHub.
1. [Create a Pull Request (PR)](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork).
1. Link the PR to the ticket requesting the new notebook.
   1. On the right hand side of the PR there is an option for `Linked issues`. Type the number for the issue there (or scroll through the tickets until you find the one of interest).
   1. **Admin** Move the Project card from `Backlog` to `Working`.
1. When you are ready for it to be merged, in the PR click `Ready for review`.
   1. **Admin** Move the Project card from `Working` to `Needs Review`.

## Reviewing

See [pull request reviews](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-request-reviews) for more information on reviewing PRs.

**Each new notebook needs at least one reviewer.**

1. When the PR is `Ready for review`, the reviewer should:
   1. Try running the entire notebook. Typically by selecting from the **Kernel** dropdown `Restart and Run All`.
      1. Any errors here should be logged and fixed or reported back to the PR. **Admin** move the Project card from `Needs Review` to `Working`.
   1. Review the notebook for understandability.
      1. Does the notebook clearly describe the processes happening in each cell? Does it provide context?
   1. Review the code to ensure it's doing what it's supposed to.
   1. Check for spelling errors.

## Merging

For Admins:

1. If the notebook looks good, the reviewer will [merge the PR](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/merging-a-pull-request).
1. This kicks off a series of [GitHub Actions](https://github.com/features/actions).
   1. You can see the workflows at https://github.com/ioos/notebooks_demos/actions
1. Once the workflows are complete, check the [IOOS CodeLab](https://ioos.github.io/ioos_code_lab/) for the new notebook.
1. Review the notebook for any display issues when presented on the web. Check for the extra cell at the bottom of the notebook.
   1. If there are issues, submit a new PR to resolve the issues.

## Announcing

When new notebooks, or significant changes to the site, are merged and pushed out, follow this procedure:

1. **Admin** Move the appropriate Project card to [Announcement](https://github.com/orgs/ioos/projects/1#column-13186308).
1. Draft announcement text.
   1. Include a brief summary of the new release.
   1. Include any relevant links to the demo center.
1. Distribute text through the following channels.
   1. IOOS bi-weekly
   1. EOTO
   1. ioos_tech mail list
   1. dmac mail list
   1. Twitter/FB.
   1. Appropriate slack channels

## Logging bugs or changes

1. Bugs should be reported through tickets in this repository. Be sure to include the notebook where the problem is found. Include a clear description of the issue or change that is needed.

## Managing IOOS Data Demo Center Project Board

The [project board](https://github.com/orgs/ioos/projects/1) captures the current progress on notebooks and adjustments to the IOOS Data Demo Center.

| **Column name** | **Purpose**                                                         |
| --------------- | ------------------------------------------------------------------- |
| Icebox          | Back burner tickets to keep in the fray.                            |
| Backlog         | Tickets to be worked on next.                                       |
| Working         | Tickets actively being contributed to.                              |
| Needs Review    | Tickets where a PR has been requested to merge.                     |
| Announcement    | Tickets that have been merged and an announcement needs to be made. |
| Done            | All completed tickets.                                              |

## Local management of notebooks_demo

This section walks through one way to manage the notebooks_demo git repository on your local machine.

Clone your fork of the notebooks_demo repository to a known location on your machine:

`$ git clone https://github.com/MathewBiddle/ioos_code_lab.git`

Set the upstream branch to the ioos/notebooks_demos repository:

`$ git remote add upstream https://github.com/ioos/ioos_code_lab.git`

Keep your local main up-to-date with the upstream main ([walkthough](https://stefanbauer.me/articles/how-to-keep-your-git-fork-up-to-date)):

```
$ git fetch upstream
$ git pull upstream/main main
```

OR

```
$ git merge upstream/main main
```

Rebase (if needed):

```
$ git rebase upstream/main
```

Push your local repo up to your fork in GitHub.

```
$ git push
```
