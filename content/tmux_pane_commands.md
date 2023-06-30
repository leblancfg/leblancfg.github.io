Title: TIL: Automating Command Execution Across All Tmux Panes
Date: 2023-06-30
Category: Tmux
Tags: tmux, vim, shell
Slug: automating-command-execution-across-tmux-panes
Authors: François Leblanc
Summary: Learn how to automate the propagation of configuration changes across all tmux panes, saving time and enhancing productivity.

As developers, we often find ourselves working in multiple tmux panes, each
running different applications or instances of the same application. When we
make changes to a configuration file, such as `~/.vimrc` for Vim or `~/.aliases`
for our shell, we need to manually reload that configuration in each relevant
instance. This can be a time-consuming process, especially when working with a
large number of panes. But also, let's be wizards and automate this process!

In this post, we'll explore a simple automation that can save you a lot of time
and effort. We'll focus on a specific use case &mdash; reloading a `.vimrc`
file across all Vim instances in tmux panes &mdash; but the pattern can be
applied to a variety of scenarios.

## The Solution

Here's a shell function that reloads the `.vimrc` file in all Vim instances
across all tmux panes:

```sh
function reload-all-vim() {
    tmux list-panes -aF "#{pane_id} #{pane_current_command}" |
    awk '/vim|nvim/ {print $1}' |
    xargs -I {} tmux send-keys -t {} "C-[" ":so ~/.vimrc" "C-m"
}
```

Let's break down this function:

1. `tmux list-panes -aF "#{pane_id} #{pane_current_command}"`: This command lists all panes across all tmux sessions and windows. For each pane, it prints the pane ID and the current command running in the pane.
2. `awk '/vim|nvim/ {print $1}'`: This command filters the output to only include lines where the current command is either `vim` or `nvim`, and then it prints the pane ID of those panes.
3. `xargs -I {} tmux send-keys -t {} "C-[" ":so ~/.vimrc" "C-m"`: This command takes the pane IDs output by `awk` and for each pane ID, it sends a series of keys to that pane. The keys are:
    - `C-[` (equivalent to the `Esc` key) ensuring we're in normal mode
    - `:so ~/.vimrc` the command to reload the `.vimrc` file, and
    - `C-m` (equivalent to the `Enter` key) executing the command


## Conclusion

With this pattern, you can automate the process of propagating configuration
changes to all relevant instances across all tmux panes. This will save you the
time and effort of manually reloading configurations, allowing you to focus
more on your work and less on configuration management.

The pattern used in this function can be applied to a variety of scenarios.
Here are some examples:

* **Reloading Shell Aliases**: If you update your `~/.aliases` file, you can use a similar function to source this file in all shell panes.
* **Updating Environment Variables**: If you change an environment variable in your `~/.bashrc` or `~/.zshrc` file, you can propagate this change to all shell panes.
* **Updating Git Configuration**: If you change your Git configuration, you can use a similar function to propagate this change to all shell panes where you might run Git commands.
