Title: Being a good UNIX neighbour
Date: 2023-04-29
Category: cli, unix
Tags: cli, unix, shell, bash, zsh, command line, terminal, productivity, click, python
Slug: level-up-your-command-line-skills-the-secret-to-being-a-good-unix-neighbour
Authors: François Leblanc
Summary: A few tips to be a good UNIX neighbour and make your scripts more portable.

The UNIX philosophy is a set of design principles that has had a huge impact on
the development of software systems. In essence, the UNIX philosophy stresses
the importance of keeping things simple and modular. You should think of the
shell as a programming language of its own! Take for example this one-liner:

```sh
curl -s 'https://www.example.com/query?symbol=GOOG&apikey=API_KEY' \
| jq '.["Global Quote"]["05. price"]' \
| sqlite3 stocks.db "UPDATE portfolio SET price = $(cat), time = CURRENT_TIMESTAMP WHERE symbol = 'GOOG'" \
&& sqlite3 stocks.db "SELECT price FROM portfolio WHERE symbol = 'GOOG' AND price > 9000" \
| xargs -I {} curl -X POST -H "Content-Type: application/json" -d '{"symbol": "GOOG", "price": "'{}'"}' https://example.com/api/sell
```

In this condensed program of 4 lines, the following happens:

1. We download the HTML page of Google Finance for the GOOG stock.
2. We extract the current price from the HTML page.
3. We update the price of the GOOG stock in our database.
4. If the price is above 9000, we send a notification to our API to sell stocks.

Getting back to the UNIX philosophy, this means writing small programs that do
one thing well and can be combined with other programs to achieve more complex
functionality. Other key principles of the UNIX philosophy include using plain
text as a universal interface, favoring simple implementations over more
complex ones, and using pipelines to combine simple programs into powerful
workflows.

If you're writing command line tools, it's important to consider how they fit
into the UNIX ecosystem. As part of this, it's helpful to ensure your tools can
be easily integrated into pipelines with other tools. A key way to achieve this
is by allowing your tool to accept input from other tools through standard
input and output.

## Example
Let's take a look at an example of a fictitious tool called `do_x`. In this
example, we define an argparse argument parser that allows the user to specify
an input file or to use standard input by default. We also provide an option to
output the results in JSON format. After processing the input data, we output
the results either as a string or as a JSON object, depending on the user's
choice.

### Starter code

Let's start off with an example of what I might have:

```py
import click


def do_stuff(input_data):
    """Do stuff."""
    return {'result': input_data}


@click.command()
@click.argument('filename')
def main(filename):
    with open(filename, 'r') as f:
        input_data = f.read()

    # Do something with input data and print it
    output_data = do_stuff(input_data)
    # Use `echo` for better compatibility
    click.echo(output_data)


if __name__ == '__main__':
    main()
```

Here this code is straightforward: this tool is meant to be called from the
command line with a simple filename argument. It reads the file, does something
with the data, and prints the result. This is a good start, but it's not very
flexible. What if we want to use this tool in a pipeline? What if we want to
use it with standard input? What if we want to use it in a script?

### Using standard input

The first item of business is to make this tool more flexible. Tools should
accept data from stdin and offer to read files from an argument. Your tool's
API should be flexible enough to handle both. In our case, we can implement
this by specifying the filename argument as optional and setting the default
value to stdin. This will allow us to call the tool with or without a filename
argument, and it will read from stdin if no filename is provided.

In general, the UNIX philosophy favors passing data via pipes and standard
input, as it allows for a more flexible and composable toolchain. This is
because a tool can be designed to read data from standard input, process it,
and then output the results to standard output, which can be used as input to
another tool in the pipeline.

However, there are situations where it may be more appropriate to pass
filepaths as arguments instead of reading data from standard input. For
example, if a tool needs to process multiple files, it may be more convenient
to pass the filepaths as arguments instead of requiring the user to redirect
the contents of each file to standard input.

A good tool can handle both cases, allowing the user to pass either filepaths
or data via standard input, depending on their preference or the specific use
case. This can be achieved by designing the tool to first check if a filepath
argument was passed, and if not, to read from standard input.

In our example in particular, the `click` package handles this for us with the
`click.File` type, which

1. Defaults to stdin if the input is set to `-`, and
2. Passes a subclass of `io.TextIOBase` (e.g. `StringIO`) in either case.

This makes it handy as it handles the best practice case by default:

```py
import click


def do_stuff(input_data):
    """Do stuff."""
    return


@click.command()
@click.argument(
    'filename',
    type=click.File,
    default=click.get_text_stream('stdin'),
)
def main(filename):
    if filename.name == '<stdin>':
        # Let the user know why we're waiting for input
        click.echo('Reading from STDIN')
        
    else:
        with open(filename.name) as f:
            # This works fine with both a file or STDIN
            input_data = f.read()

    # Do something with input data
    output_data = do_stuff(input_data)
    return output_data
```

By allowing the user to specify an input file or to use standard input, our
tool can be easily integrated into pipelines with other tools. For example,
let's say we have a file called `input.txt` containing some data that we want
to process with our tool called e.g. `cli` and then pipe the results into
another tool called `do_y`:

```sh
$ cat input.txt | cli | do_y
```

By default, `cli` will read from standard input, allowing us to pipe the
contents of `input.txt` into it. `cli` will then output the results to standard
output, which can be piped into `do_y`. This allows us to easily chain together
multiple tools to create powerful pipelines.

### Adding JSON support

Another important aspect of being a good UNIX neighbour is ensuring that the
fields in your output are standard enough that they can be easily translated
with other tools. This means using a standard delimiter, such as a tab or a
comma, and avoiding using special characters that may cause issues when parsing
the output with other tools.

Finally, if possible, it is also helpful to provide the option to output the
results in JSON format. JSON is a standard data format that can be easily
parsed and processed by many programming languages, making it a great option
for interoperability between tools. This can be achieved by adding a flag to
your tool that allows the user to specify the output format. Depending on the
API you strive to provide, you may also want it to become the default.

```py
import json
import click

def do_stuff(input_data):
    """Do stuff."""
    return {'result': input_data}

@click.command()
@click.argument(
    'filename',
    type=click.File,
    default=click.get_text_stream('stdin'),
)
@click.option(
    '--json',
    '-j',
    is_flag=True,
    help='Output results in JSON format',
)
def main(filename, json):
    if filename.name == '<stdin>':
        click.echo('Reading from STDIN')
        
    else:
        with open(filename.name) as f:
            input_data = f.read()

    output_data = do_stuff(input_data)

    if json:
        # Output results as JSON
        click.echo(json.dumps(output_data))

    else:
        # Output results as a string
        click.echo(output_data)
```

which makes it possible e.g. to use this tool in a pipeline with `jq`:

```sh
$ cat input.txt | cli --json | jq '.result' | do_y
```


## Conclusion

In conclusion, by designing our command line tools to be good UNIX neighbours,
we can create powerful pipelines that allow us to efficiently process and
analyze data. This means allowing our tools to accept input from other tools
through standard input and output, using standard delimiters in our output
fields, and providing the option to output results in JSON format. By following
these principles, we can create tools that work well with others and promote
the UNIX philosophy of modularity and simplicity.
