# coding:utf-8
import logging
import re
import subprocess
from os import path


_log = logging.getLogger('analyze.apksigner')

apksigner_jar = path.join(path.dirname(__file__), "apksigner-wrapper-linux-x86_64.jar")

newest_sdk_version = 27

def run_cmd(*args, **kwargs):
    import subprocess
    _log.debug("Execute command: {}".format(" ".join(args)))
    input = kwargs.get('input')
    try:
        result = subprocess.run(args, input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        _log.error("Run subprocess error, return code {}".format(e.returncode))
        _log.debug("------ arguments ------")
        _log.debug(repr(e.args))
        _log.debug("------ stdout ------")
        _log.debug(repr(e.stdout))
        _log.debug("------ stderr ------")
        _log.debug(repr(e.stderr))
        _log.debug("------ end ------")
        raise

    if len(result.stderr) > 0:
        for line in result.stderr.decode(errors='replace').splitlines():
            _log.warning(line)

    return result.stdout

def run_apksigner(apk_path):
    # will throw an exception when failed to verify"
    try:
        return run_cmd("java", "-Xmx1024M", "-cp", apksigner_jar, "ApkSignerVerifier", apk_path)
    except subprocess.CalledProcessError as e:
        retry_min_sdk = False

        for line in e.stderr.decode(errors='replace').splitlines():
            if line.startswith('ERROR:'):
                _log.error(line)
                err = line.split(':')[1].strip()
                if err == 'ApkVerifierIssue 19': # retry with min_sdk_version
                    retry_min_sdk = True
            elif line.startswith('WARNING:'):
                _log.warning(line)
            else:
                _log.debug(line)

        if retry_min_sdk:
            # do not print error/warning message again after retrying
            return run_cmd("java", "-Xmx1024M", "-cp", apksigner_jar, "ApkSignerVerifier",
                       "--min-sdk-version", str(newest_sdk_version), apk_path)
        else:
            raise


def parse(output):
    ret = {}
    lines = output.decode('utf-8').splitlines()
    for l in lines:
        s = l.split(': ', 1)
        if len(s) > 1:
            k = s[0]
            v = s[1]
            if k == "Number of signers":
                num = int(v)
                if num != 1:
                    _log.warning("Number of singers is not 1 but {}".format(v))
            elif k == "Signer #1 certificate SHA-256 digest":
                assert re.match('^[a-z0-9]{64}$', v) is not None
                ret["sha256"] = v
            elif k == "Signer #1 certificate SHA-1 digest":
                assert re.match('^[a-z0-9]{40}$', v) is not None
                ret["sha1"] = v
            elif k == "Signer #1 certificate MD5 digest":
                assert re.match('^[a-z0-9]{32}$', v) is not None
                ret["md5"] = v
            elif k == "Signer #1 certificate DN":
                # Distinguished Name
                ret["dn"] = v
    assert all(k in ret for k in ("sha256", "sha1", "md5", "dn"))
    return ret


def apksigner(apk_path):
    print(parse(run_apksigner(apk_path)))


if __name__ == "__main__":
    apk_path = "test1.apk"
    apksigner(apk_path)
