import typer
from dvd_logofier.dvd_logofier import dvd_logofier


app = typer.Typer()
app.command()(dvd_logofier)


if __name__ == "__main__":
    app()