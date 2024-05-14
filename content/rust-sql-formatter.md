Title: First steps with Rust
Date: 2024-05-13
Category: Rust
Tags: rust, programming, learning
Slug: first-steps-with-rust
Authors: François Leblanc
Summary: Documenting my first steps with Rust, from installation to running a simple script.

In this article, I document my initial steps with Rust. From installation to
running a simple script, I explore the foundational aspects of Rust and share
my journey as a newcomer to this language. As a newcomer to this fast and
efficient programming language, I've decided to document my initial foray from
scratch. Leveraging the capabilities of GPT-4, my aim isn’t to memorize Rust's
syntax right off the bat; instead, I'm focusing on setting up a foundational
environment conducive to experimentation and deeper understanding of the
language's core principles and primitives.

While I recognize that the internet is replete with tutorials and guides on
Rust, I'm just chronicling my own learning process, warts and all. I believe in
the power of learning by teaching and sharing, and though this document may not
offer groundbreaking insights, it certainly serves as a practical account of
one developer's journey through the, uh, "intriguing" complexities of Rust.


# Installation
I'm on a Mac and considered installing Rust using `brew`, but the official
installation instructions are so simple that I decided to go with that. I ran
the following command in my terminal:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

and went with the default options. This installed `rustc` and `cargo` on my machine.

# Hello world

I then created a new script with the following content:

```bash
echo 'fn main() { println!("Hello, world!"); }' > hello.rs
```

, compiled and ran it with:

```bash
rustc hello.rs
./hello
```

That's nice. Ok but also why the exclamations? From googling, that's a way to
tell the compiler that it's a macro, which in this case means "you can't know
in advance how many arguments you'll get, so just take them all". I'm sure I
don't fully understand that yet, but good to keep in mind.

## Using `cargo`
But if you're going to be doing more than just a one-liner, it
really sounds like you'll want to use `cargo`. Why? because it's a package
manager and build system for Rust. It's like `npm` for Node.js or `pip` for
Python. It's a tool that helps you build, test and run your Rust projects.

I started off in a newly created repo from Github I'd cloned, but `cargo new`
intends on creating a new directory for your project. Instead, you can just
call `cargo init` in the directory you're already in.

I already know I'll want to call mine `sqlf` (for SQL formatter), so I ran:

```sh
PROJECT_NAME=sqlf
gh repo create --add-readme --private --gitignore=rust $PROJECT_NAME
cd $PROJECT_NAME
cargo init
```

This creates a new directory with the following structure:

```bash
tree
.
├── Cargo.toml
├── LICENSE
├── README.md
└── src
    └── main.rs
```

and running `cargo run` will compile and run the project.

```
$ cargo run
   Compiling hello_world v0.1.0 (/Users/leblancfg/src/github.com/leblancfg/hello_world)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 2.29s
     Running `target/debug/hello_world`
Hello, world!
```

# SQL "formatter"

I ended up writing a slightly harder sql "formatter" whose job is to uppercase
sql keywords in a DDL statement. Here's the code:

```rust
fn main() {
    let input = "select * from users as u where u.id = 1;";
    let formatted = format_sql(input);
    println!("{}", formatted);
}

fn format_sql(input: &str) -> String {
    // TODO: Add like, wayyy more and make it a separate file
    let keywords = [
        "select", "from", "where", "insert", "update", "delete", "as", "order", "by", "group",
        "join", "having", "limit", "offset", "and", "or", "not", "in", "like", "is", "null",
        "true", "false", "between", "exists", "case", "when", "then", "else", "end", "distinct",
    ];

    input
        .split_whitespace()
        .map(|word| {
            if keywords.contains(&word.to_lowercase().as_str()) {
                word.to_uppercase()
            } else {
                word.to_string()
            }
        })
        .collect::<Vec<String>>()
        .join(" ")
}
```

The idea here is to have a slightly harder example to work with; we'll then
1. add tests
2. make it read from a file
3. make it glob a directory and run in parallel

I feel like that's a good first step to get a feel for the language!


## Testing
I'd be lost without tests, especially in a new language. So that was my next
step. Turns out in Rust, the recommended way to write tests in the same file as
your code, and they're only compiled when you run `cargo test`.

So I added the following tests to my script:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_empty_string() {
        let query = "";
        assert_eq!(format_sql(query), "");
    }

    #[test]
    fn test_basic_keywords() {
        let query = "select * from users where id = 1";
        assert_eq!(format_sql(query), "SELECT * FROM users WHERE id = 1");
    }

    #[test]
    fn test_mixed_case_keywords() {
        let query = "SeLeCt * fRoM users where ID = 1";
        assert_eq!(format_sql(query), "SELECT * FROM users WHERE ID = 1");
    }

    #[test]
    fn test_no_keywords() {
        let query = "users * id = 1";
        assert_eq!(format_sql(query), "users * id = 1");
    }
}
```

## Reading from a file
Now, let's add reading in from a file. At this point we'll need to parse some
arguments, and coming from either Python or Ruby my prior assumption is that
the stdlib provides just enough to get you started (that's us!), but you'd
probably want to use a library for anything more complex than parsing an
argument or two. The situation seems similar in Rust, where the `std::env`
module provides the `args` function to get the command line arguments.

```rust
use std::env;
use std::fs;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Usage: {} <input file>", args[0]);
        std::process::exit(1);
    }

    let filename = &args[1];
    let contents = fs::read_to_string(filename).expect("Something went wrong reading the file");
    let formatted = format_sql(&contents);
    println!("{}", formatted);
}
```

And that's it for that. I won't add a test for this because the code we've just
added would basically mean testing the stdlib, which I'm not interested in
doing.

# Look, ma, no GIL!
I've been reading a bit about Rust's concurrency model, and it's pretty
interesting. Rust doesn't have a Global Interpreter Lock (GIL) like Python, so
you can write concurrent code without worrying about the GIL. This is a big
deal for performance, especially on multi-core systems.

What's neat about our little example is that it's already set up to be
concurrent. We can just use the `rayon` crate to parallelize the processing of
each file in a directory. I guess in Python, the equivalent would be using
`concurrent.futures` or `multiprocessing`.

From its documentation:
> Rayon is a data-parallelism library that makes it easy to convert sequential
> computations into parallel.

> It is lightweight and convenient for introducing parallelism into existing
> code. It guarantees data-race free executions and takes advantage of
> parallelism when sensible, based on work-load at runtime.

Anywho, here's how we can do that. Start by editing the `Cargo.toml` file with:

```toml
[dependencies]
rayon = "1.10.0"
```

then, in `main.rs`, add the following:

```rust
use rayon::prelude::*;

...

use rayon::prelude::*;
use std::env;
use std::fs;
use std::path::Path;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Usage: {} <input file>", args[0]);
        std::process::exit(1);
    }
    let paths: Vec<String> = args.into_iter().skip(1).collect();

    // Zoom through the vec with rayon
    paths.par_iter().for_each(|path| {
        let path = Path::new(path);
        if path.is_file() {
            process_file(path);
        } else {
            println!("{} is not a file", path.display());
        }
    });
}

fn process_file(path: &Path) {
    let contents = fs::read_to_string(path).expect("Failed to read file");
    let formatted = format_sql(&contents);
    println!("{}", formatted);
}
...
```


# Conclusion

> [Take a look at the whole repo at this point in the process here](https://github.com/leblancfg/sqlf/tree/f05b8f4a56a4b1cd45cbd1d1cb18978842e17200)

All very interesting! Nothing here we couldn't do with Python or Ruby quite yet, but very interesting set of first steps. I'm actually surprised by the ease of use of Rust so far. Given my past horrendous experience with C back in university, I was expecting a lot more pain. But so far, so good!

I'm looking forward to diving deeper into Rust and seeing how it can help me build more robust and efficient software. For thereon, I feel like it would be interesting to double down on the SQL formatter bit and see how far I can take it with a few hours here and there.

The idea of course is to get a fast SQL formatter wired up to my text editor, so I can format SQL on the fly. This has been a long-standing pain point in my `sqlfluff`-linted project, and I can't say I'm very happy.

Of course I'm aware of a handful of SQL formatters writtern in Rust already, but that's not the goal here; I'm just trying to learn Rust and have some fun with it. I'm sure I'll learn a lot along the way, and I'm excited to see where this journey takes me.

Until next time!
