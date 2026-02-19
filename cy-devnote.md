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
```
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