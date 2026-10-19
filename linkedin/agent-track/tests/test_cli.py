from click.testing import CliRunner

from agent_track.cli import main


def test_cli_help_lists_feed_digest_flags() -> None:
    runner = CliRunner()
    root = runner.invoke(main, ["--help"])
    assert root.exit_code == 0
    assert "feed" in root.output

    feed = runner.invoke(main, ["feed", "--help"])
    assert feed.exit_code == 0
    assert "digest" in feed.output
    assert "career-job-applications" in feed.output

    digest = runner.invoke(main, ["feed", "digest", "--help"])
    assert digest.exit_code == 0
    assert "--limit" in digest.output
    assert "--persist-profile" in digest.output
    assert "--no-wait" in digest.output
