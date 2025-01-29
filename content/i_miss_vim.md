Title: I miss vim
Date: 2025-01-29
Category: vim
Tags: vim, neovim
Slug: i-miss-vim
Authors: François Leblanc
Summary: A short reflection on neovim's extensibility vs simplicity tradeoff

I've been using [neovim](https://neovim.io/) for almost two years now and I'm
gonna go out come out and say it. **I miss vanilla
[vim](https://www.vim.org/)**.

Is neovim faster? Yes. Can it perform async tasks like a champ? Yes. Is lua
scripting way saner than the old hodgepodge of slow vimscript? Yes. Can I make
it do whatever the hell I want compared to Vim? Also yes.

But I miss the relative simplicity of my former vim setup. Is it just a "skill
issue"? Partly. But it's more than that.

My vim setup was relatively straightforward and could all fit inside of a
single, relatively large file that I could grok from top to bottom. I was using
the [ALE plugin](https://github.com/dense-analysis/ale) to contact formatters,
linters, and language servers to get an IDE-like editing experience inside of
Vim. It was slow and error-prone, but it took only a couple of lines to set up.
I was typically able to troubleshoot wonky behaviour within a couple minutes.
Coming into a new language or codebase was relatively straightforward as I
would just add a couple lines to my ALE setup and I would have language
specific plugins ready and opinionatedly set up.

In comparison, my new neovim settings are sprawled across 12 files, of which
I've copied and pasted and barely understand. I've got a bunch of plugins that
I don't even know what they do, but I'm too afraid to remove or modify them
because I might break something.

I need a Babel Tower's equivalent of plugins standing on top of each other to
work. For example, I use [lazy](https://github.com/folke/lazy.nvim) for plugin
management, [mason](https://github.com/williamboman/mason.nvim) for LSP server
management, [lsp-zero](https://github.com/VonHeikemen/lsp-zero.nvim) to be able
to call most of them, and the built-in LSP server support to capture what's
standard in many editors these days.

My initial reaction when first installing them is that they felt like magic!
But somehow, that was very disappointing, very fast. Especially Mason. Mason
would give you an opinionated list of all the available DSPs, formatters,
linters, etc. out there. It's great at installing and syncing, you have to give
it that. But actually using them? No, that's too much. You'll need to manually
configure each one of those packages by either copying and pasting something
from the plugins creator or finding some other neovim users settings to copy.

And it's been almost two years now, you'd think I'd be out of the
cargo-cult-config phase by now.

I'd also been using a vim color scheme that simply called one of the 16 ASCII
colors of my terminal. This had worked well for almost 8 years. In neovim,
somehow, I need to set up its own color scheme on top of the one that my
terminal has. Because otherwise I can't get proper syntax highlighting as it
talks to the language server. I find it preposterous that I would need to have
a theme installed in order for the language server support to be properly
shown.

I'm not saying that neovim plugins are bad. I think I'm pointing the finger at
an evolving set of standards or values that are part of the neovim developer
ethos vs Bram's, and bemoaning it &mdash; while I hypocritically use it and
don't participate in its development.

But if it can be distilled in a single sentence, it's this:

> Make developers think less.

Which, in a way, is saying

> Be more opinionated.

## Grievances
### I shouldn't need to manually customize most plugins
Users will write in a variety of languages. Most of them are very popular, and
they will use an opinionated set of packages for their linting, their DSP,
their LSP, and so forth. I don't need to use a neovim distribution to have an
opinionated set of how these packages work together and are set up.

### Why isn't it part of neovim core?
Plugin writers and maintainers have been an integral part of neovim's rise and
continued use. And I would understand why the neovim maintainers would not want
to necessarily. Fold in some of their capabilities into neovim core, but I
strongly think they should.

### Why do I need a color scheme?
Neovm did land default color scheme in the 0.10 version, but to me that is
still a non-sequitur. Why do I even need one in the first place when my
terminal has colors that I've chosen already?

I really want to be able to only map my editor colors to the terminal in which
I'm using. There should be no need for a color scheme in the first place to get
proper syntax highlighting. The reason behind my required use of it is that in
order to see language items in the "expanded universe" of LSP primitives that
aren't mapped to standard vim objects. What's a `@lsp.type.keyword` if not just
a `@keyword`? The standard vim syntax highlighting doesn't know what to do with
it.

## Hope
I'm actually very happy to [read the neovim
roadmap](https://neovim.io/roadmap/). The next releases are actually slated to
be "The year of the Nvim OOTB" (out of the box). I'm excited to see what that
means. I'm excited to see a plugin manager, an LSP config concept, and
auto-completion coming in the near-to-medium-term future.

I'm not calling neovim bankruptcy (yet?). I don't have the intention to move
over to a fully-managed neovim "distribution" like LazyVim, LunarVim, or
AstroVim. I find the thought a little bit ridiculous, really! I've spent years
customizing my editor in a way that fits my brain, and can make abstract,
complex changes to the codebases I work on with a few well-rehearsed keystrokes
whose aliases I wrote myself.

But if this essay can have any impact, it is this: **if you are contemplating
writing a neovim plugin, form some opinions on how you and others will use
it**, before you share it back to the world.
