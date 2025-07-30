"""Tests for audio module."""

from unittest.mock import Mock, patch

import pytest

from claude_pyhooks.commands.audio import (
    DEFAULT_BEEP,
    ERROR_BEEP,
    SUCCESS_BEEP,
    WARNING_BEEP,
    BeepCommand,
    BeepSequence,
    SleepCommand,
    _make_beep,
)


class TestMakeBeep:
    @patch("claude_pyhooks.commands.audio.os.getenv")
    @patch("claude_pyhooks.commands.audio.platform.release")
    @patch("claude_pyhooks.commands.audio.os.system")
    def test_wsl_beep(self, mock_system, mock_release, mock_getenv):
        mock_getenv.return_value = "Ubuntu"
        mock_release.return_value = "5.4.0-microsoft-standard"

        _make_beep(800, 300)

        mock_system.assert_called_once_with(
            'powershell.exe -c "[console]::beep(800,300)"'
        )

    @patch("claude_pyhooks.commands.audio.os.getenv")
    @patch("claude_pyhooks.commands.audio.platform.release")
    @patch("claude_pyhooks.commands.audio.os.system")
    def test_microsoft_release_beep(self, mock_system, mock_release, mock_getenv):
        mock_getenv.return_value = None
        mock_release.return_value = "5.4.0-microsoft-standard"

        _make_beep(1000, 200)

        mock_system.assert_called_once_with(
            'powershell.exe -c "[console]::beep(1000,200)"'
        )

    @patch("claude_pyhooks.commands.audio.os.getenv")
    @patch("claude_pyhooks.commands.audio.platform.release")
    def test_windows_beep(self, mock_release, mock_getenv):
        mock_getenv.return_value = None
        mock_release.return_value = "10.0.19041"

        mock_winsound = Mock()
        with patch("claude_pyhooks.commands.audio.sys.platform", "win32"):
            with patch.dict("sys.modules", {"winsound": mock_winsound}):
                # Need to reload the function to pick up the mocked module
                from claude_pyhooks.commands.audio import _make_beep

                _make_beep(600, 400)
                mock_winsound.Beep.assert_called_once_with(600, 400)

    @patch("claude_pyhooks.commands.audio.os.getenv")
    @patch("claude_pyhooks.commands.audio.platform.release")
    @patch("claude_pyhooks.commands.audio.sys.stdout")
    @patch("claude_pyhooks.commands.audio.time.sleep")
    def test_posix_beep(self, mock_sleep, mock_stdout, mock_release, mock_getenv):
        mock_getenv.return_value = None
        mock_release.return_value = "5.4.0-generic"

        _make_beep(800, 300)

        mock_stdout.write.assert_called_once_with("\a")
        mock_stdout.flush.assert_called_once()
        mock_sleep.assert_called_once_with(0.3)

    @patch("claude_pyhooks.commands.audio.os.getenv")
    @patch("claude_pyhooks.commands.audio.platform.release")
    @patch("claude_pyhooks.commands.audio.sys.stdout")
    @patch("claude_pyhooks.commands.audio.time.sleep")
    def test_fallback_with_curses(
        self, mock_sleep, mock_stdout, mock_release, mock_getenv
    ):
        mock_getenv.return_value = None
        mock_release.return_value = "5.4.0-generic"
        mock_stdout.write.side_effect = Exception("stdout error")

        mock_curses = Mock()
        with patch.dict("sys.modules", {"curses": mock_curses}):
            from claude_pyhooks.commands.audio import _make_beep

            _make_beep(800, 300)
            mock_curses.setupterm.assert_called_once()
            mock_curses.beep.assert_called_once()
            mock_sleep.assert_called_once_with(0.3)

    @patch("claude_pyhooks.commands.audio.os.getenv")
    @patch("claude_pyhooks.commands.audio.platform.release")
    @patch("claude_pyhooks.commands.audio.sys.stdout")
    @patch("claude_pyhooks.commands.audio.time.sleep")
    def test_complete_fallback(
        self, mock_sleep, mock_stdout, mock_release, mock_getenv
    ):
        mock_getenv.return_value = None
        mock_release.return_value = "5.4.0-generic"
        mock_stdout.write.side_effect = Exception("stdout error")

        mock_curses = Mock()
        mock_curses.setupterm.side_effect = Exception("curses error")
        with patch.dict("sys.modules", {"curses": mock_curses}):
            from claude_pyhooks.commands.audio import _make_beep

            _make_beep(800, 300)
            mock_sleep.assert_called_once_with(0.3)


class TestBeepCommand:
    def test_default_values(self):
        cmd = BeepCommand()
        assert cmd.frequency == 800
        assert cmd.duration_ms == 300

    def test_custom_values(self):
        cmd = BeepCommand(frequency=1000, duration_ms=500)
        assert cmd.frequency == 1000
        assert cmd.duration_ms == 500

    @patch("claude_pyhooks.commands.audio._make_beep")
    def test_execute(self, mock_make_beep):
        cmd = BeepCommand(frequency=1200, duration_ms=400)
        cmd.execute()
        mock_make_beep.assert_called_once_with(1200, 400)

    def test_immutable(self):
        cmd = BeepCommand()
        with pytest.raises(AttributeError):
            cmd.frequency = 1000


class TestSleepCommand:
    def test_default_values(self):
        cmd = SleepCommand()
        assert cmd.duration_ms == 100

    def test_custom_values(self):
        cmd = SleepCommand(duration_ms=500)
        assert cmd.duration_ms == 500

    @patch("claude_pyhooks.commands.audio.time.sleep")
    def test_execute(self, mock_sleep):
        cmd = SleepCommand(duration_ms=300)
        cmd.execute()
        mock_sleep.assert_called_once_with(0.3)

    def test_immutable(self):
        cmd = SleepCommand()
        with pytest.raises(AttributeError):
            cmd.duration_ms = 200


class TestBeepSequence:
    def test_valid_commands(self):
        beep = BeepCommand(800, 200)
        sleep = SleepCommand(100)
        sequence = BeepSequence((beep, sleep))
        assert sequence.commands == (beep, sleep)

    def test_invalid_commands_raises_error(self):
        with pytest.raises(TypeError, match="BeepSequence only accepts"):
            BeepSequence(("invalid", BeepCommand()))

    def test_mixed_invalid_commands_raises_error(self):
        with pytest.raises(TypeError, match="BeepSequence only accepts"):
            BeepSequence((BeepCommand(), Mock()))

    @patch("claude_pyhooks.commands.audio._make_beep")
    @patch("claude_pyhooks.commands.audio.time.sleep")
    def test_execute_calls_all_commands(self, mock_sleep, mock_make_beep):
        beep1 = BeepCommand(800, 200)
        sleep1 = SleepCommand(100)
        beep2 = BeepCommand(1000, 300)

        sequence = BeepSequence((beep1, sleep1, beep2))
        sequence.execute()

        assert mock_make_beep.call_count == 2
        mock_make_beep.assert_any_call(800, 200)
        mock_make_beep.assert_any_call(1000, 300)
        mock_sleep.assert_called_once_with(0.1)

    def test_immutable(self):
        sequence = BeepSequence((BeepCommand(),))
        with pytest.raises(AttributeError):
            sequence.commands = (SleepCommand(),)


class TestPredefinedBeeps:
    def test_default_beep(self):
        assert isinstance(DEFAULT_BEEP, BeepCommand)
        assert DEFAULT_BEEP.frequency == 800
        assert DEFAULT_BEEP.duration_ms == 300

    def test_success_beep(self):
        assert isinstance(SUCCESS_BEEP, BeepSequence)
        assert len(SUCCESS_BEEP.commands) == 3
        assert isinstance(SUCCESS_BEEP.commands[0], BeepCommand)
        assert isinstance(SUCCESS_BEEP.commands[1], SleepCommand)
        assert isinstance(SUCCESS_BEEP.commands[2], BeepCommand)

    def test_error_beep(self):
        assert isinstance(ERROR_BEEP, BeepSequence)
        assert len(ERROR_BEEP.commands) == 2
        # Three beeps with two sleeps
        beep_count = sum(
            1 for cmd in ERROR_BEEP.commands if isinstance(cmd, BeepCommand)
        )
        sleep_count = sum(
            1 for cmd in ERROR_BEEP.commands if isinstance(cmd, SleepCommand)
        )
        assert beep_count == 2
        assert sleep_count == 0

    def test_warning_beep(self):
        assert isinstance(WARNING_BEEP, BeepSequence)
        assert len(WARNING_BEEP.commands) == 3
        # Two beeps with one sleep
        beep_count = sum(
            1 for cmd in WARNING_BEEP.commands if isinstance(cmd, BeepCommand)
        )
        sleep_count = sum(
            1 for cmd in WARNING_BEEP.commands if isinstance(cmd, SleepCommand)
        )
        assert beep_count == 3
        assert sleep_count == 0

    @patch("claude_pyhooks.commands.audio._make_beep")
    @patch("claude_pyhooks.commands.audio.time.sleep")
    def test_predefined_beeps_execute(self, mock_sleep, mock_make_beep):
        SUCCESS_BEEP.execute()
        assert mock_make_beep.call_count == 2
        assert mock_sleep.call_count == 1
