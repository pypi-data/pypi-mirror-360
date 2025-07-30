import re

def to_snake(name):
    prev_capital = name[0].isupper()
    snake_name = name[0].lower()
    for c in name[1:]:
        if c.isupper() and not prev_capital:
            snake_name += '_'
        snake_name += c.lower()
        prev_capital = c.isupper()
    return snake_name

def to_snake_df(df):
    return df.rename(columns={c: to_snake(c) for c in df.columns})


def pascal_to_camel(name):
    if re.match('[A-Z][a-z].*', name):
        return name[0].lower() + name[1:]
    else:
        return name

def pascal_to_camel_df(df):
    return df.rename(columns={c: pascal_to_camel(c) for c in df.columns})


def camel_to_pascal(name):
    return name[0].upper() + name[1:]

def camel_to_pascal_df(df):
    return df.rename(columns={c: camel_to_pascal(c) for c in df.columns})


def snake_to_pascal(name):
    return "".join(x[0].upper() + x[1:] for x in name.split("_"))

def snake_to_pascal_df(df):
    return df.rename(columns={c: snake_to_pascal(c) for c in df.columns})


def snake_to_camel(name):
    return pascal_to_camel(snake_to_pascal(name))


def snake_to_camel_df(df):
    return df.rename(columns={c: snake_to_camel(c) for c in df.columns})
