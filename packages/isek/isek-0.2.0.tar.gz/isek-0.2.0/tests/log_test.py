from isek.utils.log import LoggerManager, log, team_log


def test_loggers_exist():
    """Test that the default loggers can be imported and used."""
    assert log is not None
    assert team_log is not None
    log.info("Test agent logger.")
    team_log.info("Test team logger.")


def test_set_log_level(capsys):
    """Test setting the log level."""
    # Set level to DEBUG and check if debug message is printed
    LoggerManager.set_level("DEBUG", name="agent")
    log.debug("This is a debug message.")
    captured = capsys.readouterr()
    assert "This is a debug message." in captured.out

    # Set level to INFO and check if debug message is NOT printed
    LoggerManager.set_level("INFO", name="agent")
    log.debug("This should not be printed.")
    captured = capsys.readouterr()
    assert "This should not be printed." not in captured.out

    log.info("This should be printed.")
    captured = capsys.readouterr()
    assert "This should be printed." in captured.out


def test_print_method(capsys):
    """Test the custom .print() method."""
    message = "[bold green]This is a rich test message![/bold green]"
    log.print(message)
    captured = capsys.readouterr()
    # Rich adds its own formatting, so we check for the core text
    assert "This is a rich test message!" in captured.out


def test_team_logger_separate(capsys):
    """Test that agent and team loggers can have separate levels."""
    LoggerManager.set_level("INFO", name="agent")
    LoggerManager.set_level("DEBUG", name="team")

    log.debug("Agent debug should not appear.")
    captured = capsys.readouterr()
    assert "Agent debug should not appear." not in captured.out

    team_log.debug("Team debug should appear.")
    captured = capsys.readouterr()
    assert "Team debug should appear." in captured.out
