import typer

from goodbye import goodbye

app = typer.Typer()


@app.command()
def main(name: str):
    print(f"Hello {name}")


app.command()(goodbye)


if __name__ == "__main__":
    app()
