Title: The Data Bus: a helpful pattern for data engineering
Date: 2022-12-07
Category: Data Engineering
Tags: etl, data engineering, data bus
Slug: data-bus-pattern-for-data-engineering
Authors: François Leblanc
Summary: The Data Bus is a pattern that can help you tidy up data flows, and helps to keep track of the preprocessing steps taken. It is a simple, language-agnostic pattern that can be used to make sense when multiple transform steps are involved.

Working in data, I'm always looking for ways to make my code more organized and readable. One pattern that I've found particularly helpful is the "data bus" &mdash; a dictionary that acts as a central repository for all of the data and metadata in an ETL job.

I first started using the data bus in the ETL (Extract, Transform, Load) code for a job that's got heavy preprocessing. We want to be able to inspect and document the steps taken at each step in the process. Instead of having dozens of variables lying around, I assign them to keys in a dictionary. This allows me to easily inspect and manipulate the data, and makes the code much easier to read and understand.

Here's an example of what the data bus looks like in Python, but the pattern is language agnostic:

```python
databus = {
    'input_df': {
        'data': pd.DataFrame([0, 1, 2, 3, None]),
        'metadata': {
            'previous_step': None,
            'steps': ('read_csv', 'dropna',),
            'timestamp': '2022-12-07T12:34:56',
        }
    },
    'imputed_df': {
        'data': pd.DataFrame([0, 1, 2, 3, 4]),
        'metadata': {
            'previous_step': 'input_df',
            'steps': ({'impute_from_mean': 4,}),
            'timestamp': '2022-12-07T12:35:12',
        }
    },
    'transformed_df': {
        'data': pd.DataFrame([0, 2, 4, 6, 8]),
        'metadata': {
            'previous_step': 'imputed_df',
            'steps': ({'multiply_by': 2},),
            'timestamp': '2022-12-07T12:36:23',
        }
    }
}
```

In this example, the data bus dictionary has three datasets: input, imputed and output. Each contains a nested dictionary with the actual dataset, and metadata keys. This metadata key holds information about the data, such as its source and destination.

So if you need to pass a dataset to a function or method, you can pass the data bus and the key for the dataset you want to use:

```python
databus['input_df']['data'] = pd.DataFrame([0, 1, 2, 3, None])
...
databus['imputed_df']['data'] = impute_from_mean(databus['input_df']['data'])
```

A bit wordier, but we've found that using the data bus pattern has a few key benefits. First of all, it's much clearer and easier to understand than having a bunch of separate variables. It's also more organized, so it's easier to keep track of what's going on in our code. It also allows us to easily track the flow of data through our code. For example, we can see that the input data in the example above comes from a file called file.csv, and that it gets its missing data imputed, as well as having the `multiply_by` transformation step applied.

In our specific use case, we also needed to provide annotations to how some steps were performed, especially w.r.t. imputing missing values. So another benefit of the data bus is that it makes it easy to surface templated text that explains the steps taken:

```python
...
    'imputed_df': {
        'data': pd.DataFrame([0, 1, 2, 3, 4]),
        'metadata': {
            'previous_step': 'input_df',
            'steps': ({'impute_from_mean': 4,}),
            'timestamp': '2022-12-07T12:35:12',
        }
    },
...

imputation_steps = """
    The following steps were taken to impute missing values:
"""
for step in databus['imputed_df']['metadata']['steps']:
    for key, value in step.items():
        imputation_steps += f"""
            - {key}: {value}
        """
```

Means our output can be surfaced in an app like:

    The following steps were taken to impute missing values:

        - impute_from_mean: 4

So if you're working on similar projects, I hope I'll have convinced you that the data bus pattern is a simple but powerful way to organize and manage both the data and metadata in your code. Whether you're working on an ETL project or something else entirely, I highly recommend giving the data bus a try. It will make your code more readable, maintainable, and effective.
