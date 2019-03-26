"""Get version number from dvcs.

Try to follow gitflow worflow, see
https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow
"""
import subprocess


class VersionInfo:
    """Get version informations from dvcs."""

    hg_stable_branch = "default"
    git_stable_branch = "master"

    def __init__(self, dvcs=None):
        """Init for version Info class.

        :param str dvcs: either 'hg' or 'git'
        """
        if dvcs is None:
            dvcs = self._autodetect()
            # print("detected dvcs: %s" % dvcs)
        self.dvcs = dvcs

    def _popen(self, command_list):
        """Launch subprocess for given command.

        return a list of (returned) lines
        raise error if problem
        """
        p = subprocess.run(
            command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
            encoding="utf-8",
        )
        return p.stdout

    def _autodetect(self):
        """Try to autodetect which vcs is in use."""
        try:
            self._popen(["hg", "status"])
        except subprocess.CalledProcessError:
            pass
        else:
            return "hg"

        try:
            self._popen(["git", "status"])
        except subprocess.CalledProcessError:
            pass
        else:
            return "git"

    def _get_hg_version(self, branch=None):
        """Use mercurial to get last tag and last revision number.

        if repo has just been tagged, return 'lasttag'
        if not, return 'lasttag-lastrevnum'
        """
        cmd_hg_log = ["hg", "log", "--limit", "1", "--template", "{latesttag};{rev}"]
        if branch is not None and branch:
            cmd_hg_log += ["-b", branch]

        line = self._popen(cmd_hg_log).split("\n")[0]
        try:
            latest_tag, latest_rev = line.strip().split(";")
        except ValueError:
            return ""
        else:
            cmd_hg_log_rev = [
                "hg",
                "log",  # "--limit", "1",
                "-r",
                '"%s"' % latest_tag,
                "--template",
                "{rev}",
            ]
            # if branch is not None and branch:
            #    cmd_hg_log_rev += ["-b", branch]
            line = self._popen(cmd_hg_log_rev).split("\n")[0]
            latest_tag_rev = line.strip()

            if int(latest_tag_rev) == int(latest_rev) - 1:
                # here our version has just been tagged,
                # return only version number
                return latest_tag
            # we have commits since last tag
            # the return value will depends on the current branch:
            # if in stable branch, tag ".postXXXX"
            # otherwise (in dev branches), tag '.devXXXXX'
            if branch is not None and branch == self.hg_stable_branch:
                return "%s.post%s" % (latest_tag, latest_rev)
            return "%s.dev%s" % (latest_tag, latest_rev)

    def _hg_current_branch(self):
        """Use mercurial to get the current branch.

        In case of problem, returns empty string
        """
        return self._popen(["hg", "branch"]).split("\n")[0].strip()

    def _write_hg_changelog_rst(self, outputfile):
        """Output a rst file with the change log in compact version.

        :param str outputfile: output file path
        """
        result = self._popen(
            ["hg", "log", "--style", "build_scripts/hg_changelog.style"]
        )
        with open(outputfile, mode="w", encoding="utf-8") as fp:
            fp.write(u"=========\n")
            fp.write(u"Changelog\n")
            fp.write(u"=========\n\n")
            fp.write(result)

    def _get_git_version(self, branch=None, abbrev=4):
        """Use mercurial to get last tag and last revision number.

        if repo has just been tagged, return 'lasttag'
        if not, return 'lasttag-lastrevnum'
        """
        cmd_git_log = ["git", "describe", "--tags", "--abbrev=%d" % abbrev]
        try:
            version = self._popen(cmd_git_log).split("\n")[0]
        except subprocess.CalledProcessError:
            raise ValueError("Cannot find the version number, try to add a tag!")

        if branch is None or branch == self.git_stable_branch:
            # directly return version
            return version
        return "%s-%s" % (branch, version)

    def _git_current_branch(self):
        """Use git to get the current branch."""
        cmd_git = ["git", "symbolic-ref", "HEAD"]
        return self._popen(cmd_git).split("\n")[0].split("/")[-1]

    def _write_git_changelog_rst(self, outputfile):
        """Output a rst file with the change log in compact version.

        :param str outputfile: output file path
        """
        result = self._popen(
            [
                "git",
                "log",
                "--pretty=format:%cd - %h -%d %s",
                "--abbrev-commit",
                "--date=short",
            ]
        )
        with open(outputfile, mode="w", encoding="utf-8") as fp:
            fp.write(u"=========\n")
            fp.write(u"Changelog\n")
            fp.write(u"=========\n\n")
            for line in result.split("\n"):
                fp.write("- " + line + "\n")

    def write_changelog_rst(self, outputfile):
        """Write a change log rst file in the given outputfile path.

        :param str outputfile: file path
        """
        if self.dvcs == "hg":
            return self._write_hg_changelog_rst(outputfile)
        if self.dvcs == "git":
            return self._write_git_changelog_rst(outputfile)
        raise ValueError("unrecognized dvcs: %s" % self.dvcs)

    @property
    def current_branch(self):
        """Return the current working branch."""
        if self.dvcs == "hg":
            return self._hg_current_branch()
        if self.dvcs == "git":
            return self._git_current_branch()
        raise ValueError("unrecognized dvcs: %s" % self.dvcs)

    @property
    def version(self):
        """Return the calculed version number."""
        if self.dvcs == "hg":
            return self._get_hg_version(self.current_branch)
        if self.dvcs == "git":
            return self._get_git_version(self.current_branch)
        raise ValueError("unrecognized dvcs: %s" % self.dvcs)


if __name__ == "__main__":
    """Cmd line defaut."""
    print(VersionInfo().version)
