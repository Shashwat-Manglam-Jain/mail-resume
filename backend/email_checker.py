import re
import socket
import ssl
import smtplib
import logging
import random
import string
import dns.resolver

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9](?:[a-zA-Z0-9._%+\-]*[a-zA-Z0-9])?@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?\."
    r"(?:[a-zA-Z]{2,}\.?)+$"
)

_DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "tempmail.com", "throwaway.email",
    "10minutemail.com", "trashmail.com", "yopmail.com", "sharklasers.com",
    "guerrillamailblock.com", "grr.la", "dispostable.com", "maildrop.cc",
    "temp-mail.org", "fakeinbox.com", "mailnesia.com", "tempail.com",
    "tempr.email", "discard.email", "mailcatch.com", "getairmail.com",
    "mohmal.com", "getnada.com", "emailondeck.com", "crazymailing.com",
    "tmail.ws", "burnermail.io", "inboxkitten.com",
}

_ROLE_PREFIXES = {
    "noreply", "no-reply", "donotreply", "do-not-reply",
    "mailer-daemon", "postmaster", "abuse", "spam",
    "unsubscribe", "bounce", "bounces", "notifications",
    "alert", "alerts", "newsletter", "test", "demo",
}

# Common domain typos → correct domain
_DOMAIN_TYPOS = {
    "gmial.com": "gmail.com", "gmai.com": "gmail.com", "gmal.com": "gmail.com",
    "gmil.com": "gmail.com", "gamil.com": "gmail.com", "gnail.com": "gmail.com",
    "gmail.co": "gmail.com", "gmail.con": "gmail.com", "gmail.cm": "gmail.com",
    "gmail.om": "gmail.com", "gmail.cpm": "gmail.com", "gmail.vom": "gmail.com",
    "gmail.xom": "gmail.com", "gmaill.com": "gmail.com", "gmailcom": "gmail.com",
    "gmsil.com": "gmail.com", "gmali.com": "gmail.com", "gmaiil.com": "gmail.com",
    "hotmal.com": "hotmail.com", "hotmial.com": "hotmail.com",
    "hotmai.com": "hotmail.com", "hotmail.co": "hotmail.com",
    "hotmail.con": "hotmail.com", "hotmil.com": "hotmail.com",
    "hotmaill.com": "hotmail.com", "hitmail.com": "hotmail.com",
    "outloo.com": "outlook.com", "outlok.com": "outlook.com",
    "outllook.com": "outlook.com", "outlook.co": "outlook.com",
    "outlook.con": "outlook.com", "outlool.com": "outlook.com",
    "yaho.com": "yahoo.com", "yahooo.com": "yahoo.com",
    "yhoo.com": "yahoo.com", "yahoo.co": "yahoo.com",
    "yahoo.con": "yahoo.com", "yaoo.com": "yahoo.com",
    "yhaoo.com": "yahoo.com", "yaho.co.in": "yahoo.co.in",
    "rediffmal.com": "rediffmail.com", "reddifmail.com": "rediffmail.com",
    "redifmail.com": "rediffmail.com",
    "protonmal.com": "protonmail.com", "protonmai.com": "protonmail.com",
    "icoud.com": "icloud.com", "iclud.com": "icloud.com",
    "icloud.co": "icloud.com",
}

# Known free email providers where we can verify individual addresses
_FREE_PROVIDERS = {
    "gmail.com", "googlemail.com",
    "yahoo.com", "yahoo.co.in", "yahoo.co.uk", "ymail.com",
    "hotmail.com", "outlook.com", "live.com", "msn.com",
    "protonmail.com", "proton.me",
    "icloud.com", "me.com", "mac.com",
    "aol.com",
    "zoho.com", "zohomail.in",
    "rediffmail.com",
    "mail.com", "email.com",
}

_mx_cache: dict[str, list[str] | None] = {}
_vrfy_cache: dict[str, bool | None] = {}
_catchall_cache: dict[str, bool | None] = {}


def validate_syntax(email: str) -> tuple[bool, str]:
    if not email or not isinstance(email, str):
        return False, "empty email"
    email = email.strip().lower()
    if len(email) > 254:
        return False, "email too long"
    if email.count("@") != 1:
        return False, "must contain exactly one @"
    local, domain = email.rsplit("@", 1)
    if not local or len(local) > 64:
        return False, "local part empty or too long"
    if not domain or len(domain) > 253:
        return False, "domain empty or too long"
    if ".." in email:
        return False, "consecutive dots"
    if not _EMAIL_RE.match(email):
        return False, "invalid format"
    parts = domain.split(".")
    if len(parts) < 2 or any(len(p) == 0 for p in parts) or len(parts[-1]) < 2:
        return False, "invalid domain"
    return True, "ok"


def check_typo(email: str) -> tuple[bool, str, str]:
    """Check for common domain typos. Returns (has_typo, suggestion, detail)."""
    local, domain = email.strip().lower().rsplit("@", 1)
    if domain in _DOMAIN_TYPOS:
        correct = _DOMAIN_TYPOS[domain]
        suggested = f"{local}@{correct}"
        return True, suggested, f"did you mean {correct}? (typed {domain})"
    # Check for missing dot before TLD
    for known in ("gmail.com", "yahoo.com", "hotmail.com", "outlook.com"):
        nodot = known.replace(".", "")
        if domain == nodot:
            return True, f"{local}@{known}", f"did you mean {known}?"
    return False, email, "ok"


def check_disposable(email: str) -> tuple[bool, str]:
    domain = email.strip().lower().rsplit("@", 1)[-1]
    if domain in _DISPOSABLE_DOMAINS:
        return False, f"disposable domain: {domain}"
    return True, "ok"


def check_role_address(email: str) -> tuple[bool, str]:
    local = email.strip().lower().rsplit("@", 1)[0]
    for prefix in _ROLE_PREFIXES:
        if local == prefix or local.startswith(prefix + ".") or local.startswith(prefix + "+"):
            return False, f"role/system address: {local}"
    return True, "ok"


def check_mx(domain: str) -> tuple[bool, str, list[str]]:
    if domain in _mx_cache:
        records = _mx_cache[domain]
        if records:
            return True, "ok", records
        return False, f"no MX records for {domain}", []
    try:
        answers = dns.resolver.resolve(domain, "MX")
        mx_hosts = [str(r.exchange).rstrip(".")
                    for r in sorted(answers, key=lambda r: r.preference)]
        _mx_cache[domain] = mx_hosts
        return True, "ok", mx_hosts
    except dns.resolver.NXDOMAIN:
        _mx_cache[domain] = None
        return False, "domain does not exist", []
    except dns.resolver.NoAnswer:
        try:
            dns.resolver.resolve(domain, "A")
            _mx_cache[domain] = [domain]
            return True, "fallback to A record", [domain]
        except Exception:
            _mx_cache[domain] = None
            return False, "no MX or A records", []
    except dns.resolver.NoNameservers:
        _mx_cache[domain] = None
        return False, "no nameservers respond", []
    except Exception as e:
        _mx_cache[domain] = None
        return False, f"DNS error: {e}", []


def check_dns_health(domain: str) -> tuple[bool, str]:
    """Check if domain has healthy DNS (A/AAAA records resolve)."""
    try:
        dns.resolver.resolve(domain, "A")
        return True, "ok"
    except Exception:
        try:
            dns.resolver.resolve(domain, "AAAA")
            return True, "ok (IPv6)"
        except Exception:
            return False, "domain has no A/AAAA records"


def _smtp_connect(host: str, port: int, timeout: int = 10) -> smtplib.SMTP | None:
    """Try to open an SMTP connection on the given port."""
    try:
        if port == 465:
            ctx = ssl.create_default_context()
            smtp = smtplib.SMTP_SSL(host, port, timeout=timeout, context=ctx)
            smtp.ehlo_or_helo_if_needed()
            return smtp
        else:
            smtp = smtplib.SMTP(timeout=timeout)
            smtp.connect(host, port)
            smtp.ehlo_or_helo_if_needed()
            if port == 587:
                try:
                    smtp.starttls(context=ssl.create_default_context())
                    smtp.ehlo_or_helo_if_needed()
                except smtplib.SMTPNotSupportedError:
                    pass
            else:
                try:
                    smtp.starttls(context=ssl.create_default_context())
                    smtp.ehlo_or_helo_if_needed()
                except (smtplib.SMTPNotSupportedError, smtplib.SMTPException):
                    pass
            return smtp
    except Exception:
        return None


def _probe_rcpt(smtp: smtplib.SMTP, from_email: str, to_email: str) -> tuple[int, str]:
    """Send MAIL FROM + RCPT TO and return (code, message)."""
    try:
        code, _ = smtp.mail(from_email)
        if code != 250:
            return code, "MAIL FROM rejected"
        code, msg = smtp.rcpt(to_email)
        msg_str = msg.decode("utf-8", errors="replace") if isinstance(msg, bytes) else str(msg)
        return code, msg_str
    except smtplib.SMTPServerDisconnected:
        return -1, "server disconnected"
    except smtplib.SMTPException as e:
        return -1, str(e)


def detect_catchall(domain: str, mx_hosts: list[str], from_email: str = "",
                    timeout: int = 10) -> bool | None:
    """
    Detect if a domain is catch-all (accepts any address).
    Returns True if catch-all, False if not, None if can't determine.
    """
    if domain in _catchall_cache:
        return _catchall_cache[domain]

    # Don't test free providers — they're never catch-all
    if domain in _FREE_PROVIDERS:
        _catchall_cache[domain] = False
        return False

    rand_local = "xqz" + "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    fake_email = f"{rand_local}@{domain}"

    if not from_email:
        from_email = f"check@{domain}"

    for mx_host in mx_hosts[:2]:
        for port in (25, 587):
            smtp = _smtp_connect(mx_host, port, timeout)
            if not smtp:
                continue
            try:
                code, _ = _probe_rcpt(smtp, from_email, fake_email)
                smtp.quit()
                if code == 250:
                    _catchall_cache[domain] = True
                    return True
                elif code in (550, 551, 552, 553):
                    _catchall_cache[domain] = False
                    return False
                elif code in (421, 451, 452):
                    continue
            except Exception:
                try:
                    smtp.quit()
                except Exception:
                    pass
                continue

    _catchall_cache[domain] = None
    return None


def verify_smtp_rcpt(email: str, mx_hosts: list[str], from_email: str = "",
                     timeout: int = 10) -> tuple[bool, str]:
    cache_key = email.strip().lower()
    if cache_key in _vrfy_cache:
        cached = _vrfy_cache[cache_key]
        if cached is True:
            return True, "ok (cached)"
        elif cached is False:
            return False, "mailbox does not exist (cached)"

    if not from_email:
        from_email = "verify@gmail.com"

    domain = email.rsplit("@", 1)[-1]

    for mx_host in mx_hosts[:3]:
        for port in (25, 587):
            smtp = _smtp_connect(mx_host, port, timeout)
            if not smtp:
                continue

            try:
                code, msg_str = _probe_rcpt(smtp, from_email, email)
                smtp.quit()
            except Exception:
                try:
                    smtp.quit()
                except Exception:
                    pass
                continue

            msg_lower = msg_str.lower()

            if code == 250:
                _vrfy_cache[cache_key] = True
                return True, "ok"

            elif code in (550, 551, 552, 553):
                reject_phrases = (
                    "does not exist", "user unknown", "no such user",
                    "mailbox not found", "recipient rejected", "invalid",
                    "not found", "unknown user", "disabled", "inactive",
                    "doesn't exist", "is not valid", "not a valid",
                    "address rejected", "mailbox unavailable",
                    "user not found", "unknown recipient",
                    "undeliverable", "delivery not allowed",
                )
                if any(p in msg_lower for p in reject_phrases) or code == 550:
                    _vrfy_cache[cache_key] = False
                    return False, f"mailbox does not exist (code {code})"

                _vrfy_cache[cache_key] = False
                return False, f"rejected: {msg_str[:120]}"

            elif code in (451, 452):
                # Greylisting — server says "try later", address likely exists
                return True, "greylisted (temporarily deferred, likely valid)"

            elif code == 421:
                # Rate limited — try next MX
                continue

            elif code == -1:
                continue

            else:
                return True, f"inconclusive (code {code})"

    # All MX hosts unreachable on all ports
    # For free providers this is suspicious, for company domains it's common
    if domain in _FREE_PROVIDERS:
        return False, f"could not verify on {domain} (free provider — likely invalid)"
    return True, "could not connect to mail server (assuming valid for company domain)"


def validate_email_full(email: str, from_email: str = "",
                        skip_smtp: bool = False) -> dict:
    email = email.strip().lower()
    result = {"email": email, "valid": True, "checks": [], "suggestion": None}

    # 1. Syntax
    ok, reason = validate_syntax(email)
    result["checks"].append({"name": "syntax", "ok": ok, "detail": reason})
    if not ok:
        result["valid"] = False
        result["reason"] = reason
        return result

    # 2. Typo detection
    has_typo, suggestion, typo_detail = check_typo(email)
    result["checks"].append({
        "name": "typo_check",
        "ok": not has_typo,
        "detail": typo_detail,
    })
    if has_typo:
        result["suggestion"] = suggestion
        result["valid"] = False
        result["reason"] = f"possible typo: {typo_detail}"
        return result

    # 3. Disposable domain
    ok, reason = check_disposable(email)
    result["checks"].append({"name": "disposable", "ok": ok, "detail": reason})
    if not ok:
        result["valid"] = False
        result["reason"] = reason
        return result

    # 4. Role address
    ok, reason = check_role_address(email)
    result["checks"].append({"name": "role_address", "ok": ok, "detail": reason})

    # 5. MX records
    domain = email.rsplit("@", 1)[-1]
    mx_ok, mx_reason, mx_hosts = check_mx(domain)
    result["checks"].append({"name": "mx_records", "ok": mx_ok, "detail": mx_reason})
    if not mx_ok:
        result["valid"] = False
        result["reason"] = mx_reason
        return result

    # 6. DNS health
    dns_ok, dns_reason = check_dns_health(domain)
    result["checks"].append({"name": "dns_health", "ok": dns_ok, "detail": dns_reason})
    if not dns_ok and not mx_ok:
        result["valid"] = False
        result["reason"] = "domain DNS is not healthy"
        return result

    if skip_smtp:
        result["reason"] = "passed (SMTP check skipped)"
        return result

    # 7. Catch-all detection
    is_catchall = detect_catchall(domain, mx_hosts, from_email)
    if is_catchall is True:
        result["checks"].append({
            "name": "catchall",
            "ok": True,
            "detail": "domain accepts all addresses (catch-all) — cannot verify individual mailbox",
        })
        result["reason"] = "domain is catch-all — address accepted but cannot confirm it actually exists"
        return result
    elif is_catchall is False:
        result["checks"].append({
            "name": "catchall",
            "ok": True,
            "detail": "not catch-all — individual verification possible",
        })
    else:
        result["checks"].append({
            "name": "catchall",
            "ok": True,
            "detail": "could not determine catch-all status",
        })

    # 8. SMTP RCPT TO verification
    ok, reason = verify_smtp_rcpt(email, mx_hosts, from_email)
    result["checks"].append({"name": "smtp_verify", "ok": ok, "detail": reason})
    if not ok:
        result["valid"] = False
        result["reason"] = reason
        return result

    result["reason"] = "all checks passed"
    return result
