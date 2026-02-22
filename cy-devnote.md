- base directory is `/Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses`
```sh
❯ pwd
/Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses
```

- check out and work on different courses with gwq
```
❯ gwq list
 ┌────────┬──────────────────────────────────────────────────────────────────┐
 │ BRANCH │ PATH                                                             │
 ├────────┼──────────────────────────────────────────────────────────────────┤
 │ ● main │ /Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses │
 └────────┴──────────────────────────────────────────────────────────────────┘
```

- first clone with https, then set remote origin to `github.com-cyng93` which used `~/.ssh/id_cyng93` ssh key to commit
```sh
❯ tail -n 5 /Users/ching_yi_ng.2026/.ssh/config

Host github.com-cyng93
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_cyng93

❯ git remote set-url origin git@github.com-cyng93:cyng93/online-courses.git
❯ git add README.md
❯ git commit -m "Add dummy readme"
[main (root-commit) c263241] Add dummy readme
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
❯ git push -u origin main
Enumerating objects: 3, done.
Counting objects: 100% (3/3), done.
Writing objects: 100% (3/3), 235 bytes | 235.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To github.com-cyng93:cyng93/online-courses.git
 * [new branch]      main -> main
```


```sh - Create directory for each steps, with Step N's inputs softlink to Step N-1 outputs
❯ cd /Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses/a-dummy-course-template
❯ ls
step0-input/  step0-output/ step1-output/ step2-output/ step3-output/ step4-output/
❯ ln -s step0-output step1-input
❯ ln -s step1-output step2-input
❯ ln -s step2-output step3-input
❯ ln -s step3-output step4-input
```


```sh - check after softlink is created
❯ ll -l --no-permissions --level=1 --icons --time modified --sort modified --reverse (pwd) | head -n10
- ching_yi_ng.2026 20 Feb 01:22 /Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses/a-dummy-course-template
- ching_yi_ng.2026 20 Feb 01:22 ├── step4-input -> step3-output
- ching_yi_ng.2026 20 Feb 01:22 ├── step3-input -> step2-output
- ching_yi_ng.2026 20 Feb 01:22 ├── step2-input -> step1-output
- ching_yi_ng.2026 20 Feb 01:22 ├── step1-input -> step0-output
- ching_yi_ng.2026 20 Feb 01:21 ├── step4-output
- ching_yi_ng.2026 20 Feb 01:21 ├── step3-output
- ching_yi_ng.2026 20 Feb 01:21 ├── step2-output
- ching_yi_ng.2026 20 Feb 01:20 ├── step1-output
- ching_yi_ng.2026 20 Feb 01:20 ├── step0-output
```

```sh - order by name
❯ ll -l --no-permissions --level=1 --icons --time modified (pwd) | head -n10
- ching_yi_ng.2026 20 Feb 01:22 /Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses/a-dummy-course-template
- ching_yi_ng.2026 20 Feb 01:20 ├── step0-input
- ching_yi_ng.2026 20 Feb 01:20 ├── step0-output
- ching_yi_ng.2026 20 Feb 01:22 ├── step1-input -> step0-output
- ching_yi_ng.2026 20 Feb 01:20 ├── step1-output
- ching_yi_ng.2026 20 Feb 01:22 ├── step2-input -> step1-output
- ching_yi_ng.2026 20 Feb 01:21 ├── step2-output
- ching_yi_ng.2026 20 Feb 01:22 ├── step3-input -> step2-output
- ching_yi_ng.2026 20 Feb 01:21 ├── step3-output
- ching_yi_ng.2026 20 Feb 01:22 ├── step4-input -> step3-output
```

```sh - copied needed tool mentioned in CLAUDE.md (tools/*.py & tools/*.sh)
# /Users/ching_yi_ng_groupDir/worktrees/github.com-cyng93/cyng93/brain-training/scientific-brain-training-method/src/tools
# - src/tools/extract_all.sh
# - src/tools/make_grids.sh (for grid composites)
# - src/tools/parse_srt.py
# - src/tools/generate_pages.py
❯ cp -R \
  /Users/ching_yi_ng_groupDir/worktrees/github.com-cyng93/cyng93/brain-training/scientific-brain-training-method/src/tools \
  /Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses/

❯ ll -l --no-permissions --level=1 --icons --time modified /Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses/tools | head -n10
   - ching_yi_ng.2026 20 Feb 02:01 /Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses/a-dummy-course-template/../tools
3.8k ching_yi_ng.2026 20 Feb 02:01 ├── extract_all.sh
 30k ching_yi_ng.2026 20 Feb 02:01 ├── generate_pages.py
1.4k ching_yi_ng.2026 20 Feb 02:01 ├── make_grids.sh
3.1k ching_yi_ng.2026 20 Feb 02:01 └── parse_srt.py
```

- create softlink in each courses directory, first start with `a-dummy-course-template`
```sh -
❯ ll -l --no-permissions --level=3 --icons --time modified (pwd)
   - ching_yi_ng.2026 20 Feb 02:06  /Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses/a-dummy-course-template
   - ching_yi_ng.2026 20 Feb 02:06 ├── 󰣞 src -> ../src
   - ching_yi_ng.2026 20 Feb 02:01 │   └──  tools
3.8k ching_yi_ng.2026 20 Feb 02:01 │       ├──  extract_all.sh
 30k ching_yi_ng.2026 20 Feb 02:01 │       ├──  generate_pages.py
1.4k ching_yi_ng.2026 20 Feb 02:01 │       ├──  make_grids.sh
3.1k ching_yi_ng.2026 20 Feb 02:01 │       └──  parse_srt.py
   - ching_yi_ng.2026 20 Feb 01:20 ├──  step0-input
   - ching_yi_ng.2026 20 Feb 01:20 ├──  step0-output
   - ching_yi_ng.2026 20 Feb 01:22 ├──  step1-input -> step0-output
   - ching_yi_ng.2026 20 Feb 01:20 ├──  step1-output
   - ching_yi_ng.2026 20 Feb 01:22 ├──  step2-input -> step1-output
   - ching_yi_ng.2026 20 Feb 01:21 ├──  step2-output
   - ching_yi_ng.2026 20 Feb 01:22 ├──  step3-input -> step2-output
   - ching_yi_ng.2026 20 Feb 01:21 ├──  step3-output
   - ching_yi_ng.2026 20 Feb 01:22 ├──  step4-input -> step3-output
   - ching_yi_ng.2026 20 Feb 01:21 └──  step4-output
```

- copy `a-dummy-course-template/*` to `break-inner-conflict-loop/`
```sh
❯ pwd
/Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses

❯ cp -R ./a-dummy-course-template/* break-inner-conflict-loop/

❯ ll -l --no-permissions --level=3 --icons --time modified (pwd)/break-inner-conflict-loop/
   - ching_yi_ng.2026 20 Feb 02:13  /Users/ching_yi_ng_groupDir/ghq/github.com/cyng93/online-courses/break-inner-conflict-loop
   - ching_yi_ng.2026 20 Feb 02:13 ├── 󰣞 src -> ../src
   - ching_yi_ng.2026 20 Feb 02:01 │   └──  tools
3.8k ching_yi_ng.2026 20 Feb 02:01 │       ├──  extract_all.sh
 30k ching_yi_ng.2026 20 Feb 02:01 │       ├──  generate_pages.py
1.4k ching_yi_ng.2026 20 Feb 02:01 │       ├──  make_grids.sh
3.1k ching_yi_ng.2026 20 Feb 02:01 │       └──  parse_srt.py
   - ching_yi_ng.2026 20 Feb 02:13 ├──  step0-input
   - ching_yi_ng.2026 20 Feb 02:13 ├──  step0-output
   - ching_yi_ng.2026 20 Feb 02:13 ├──  step1-input -> step0-output
   - ching_yi_ng.2026 20 Feb 02:13 ├──  step1-output
   - ching_yi_ng.2026 20 Feb 02:13 ├──  step2-input -> step1-output
   - ching_yi_ng.2026 20 Feb 02:13 ├──  step2-output
   - ching_yi_ng.2026 20 Feb 02:13 ├──  step3-input -> step2-output
   - ching_yi_ng.2026 20 Feb 02:13 ├──  step3-output
   - ching_yi_ng.2026 20 Feb 02:13 ├──  step4-input -> step3-output
   - ching_yi_ng.2026 20 Feb 02:13 └──  step4-output
```