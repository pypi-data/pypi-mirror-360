import typer
from ..auth import is_logged, auth, generate_logout_url, retrieve_credentials
from ..errors.auth import LoginError

app = typer.Typer(help="Authentication commands")


@app.command(help="Login to your account")
def login():
    try:
        user = auth()
        typer.echo(f"You are logged in as {user['email']}")
    except LoginError as e:
        typer.echo(e.message)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@app.command(help="Logout from your account")
def logout():
    user = is_logged()
    if user:
        typer.echo(f"You are logged in as {user['email']}")
        typer.confirm(f"Are you sure you want to logout?", abort=True)
        logout_url = generate_logout_url()
        typer.echo(f"You are logged out.")
        typer.echo(
            f"If you want to login with a different account, visit {logout_url} and login again."
        )
    else:
        typer.echo(f"You are not logged in.")


@app.command(help="Retrieve S3 credentials")
def credentials():
    try:
        user = auth()
        credentials = retrieve_credentials(user)
        typer.echo(f"Credentials retrieved for {user['email']}:\n")
        typer.echo(f"export AWS_ACCESS_KEY_ID={credentials['AWS_ACCESS_KEY_ID']}")
        typer.echo(
            f"export AWS_SECRET_ACCESS_KEY={credentials['AWS_SECRET_ACCESS_KEY']}"
        )
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
