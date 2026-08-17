import re
from typed import typed, Any, TYPE, Dict, Regex, List, Str, Maybe
from urllib.parse import urlparse, parse_qs

class UrlErr(Exception): pass

class URL(TYPE(Str)):
    def __call__(cls, *schemes, pattern=None):
        if cls is Url:
            allowed_schemes = {str(s).lower() for s in schemes if s}

            if allowed_schemes:
                name = "Url(" + ",".join(sorted(allowed_schemes)) + ")"
            else:
                name = "Url"

            compiled_pattern = None
            if pattern is not None:
                if isinstance(pattern, str):
                    compiled_pattern = re.compile(pattern)
                else:
                    compiled_pattern = pattern

            attrs = {
                "__display__": name,
                "__null__": "",
                "_allowed_schemes": allowed_schemes or None,
                "_pattern_re": compiled_pattern,
            }
            return URL(name, (Url,), attrs)

        return super().__call__(*schemes, pattern=pattern)

    def __instancecheck__(cls, instance):
        if not isinstance(instance, Str):
            return False

        value = str(instance)

        if "://" not in value:
            return False

        parsed = urlparse(value)

        if not parsed.scheme or not parsed.netloc:
            return False

        allowed = getattr(cls, "_allowed_schemes", None)
        if allowed is not None and parsed.scheme.lower() not in allowed:
            return False

        pattern_re = getattr(cls, "_pattern_re", None)
        if pattern_re is not None:
            prefix = f"{parsed.scheme}://"
            rest = value[len(prefix):]
            if pattern_re.fullmatch(rest) is None:
                return False

        return True

Url = URL('Url', (Str,), {
    "__display__": "Url",
    "__null__": "",
    "_allowed_schemes": None,
    "_pattern_re": None
})

Hostname = Regex(r"^(?:[a-zA-Z-1-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
Hostname.__display__ = "Hostname"

class url:
    @typed
    def hostname(u: Url) -> Maybe(Hostname):
        try:
            return urlparse(u).hostname
        except Exception as e:
            raise UrlErr(e)
    domain = hostname

    @typed
    def tld(u: Url) -> Maybe(Str):
        try:
            return url.hostname(u).split('.')[-1]
        except Exception as e:
            raise UrlErr(e)

    @typed
    def subdomain(u: Url) -> Maybe(Str):
        try:
            parts = url.hostname(u).split('.')
            if len(parts) > 2:
                return '.'.join(parts[0: len(parts)-2])
            return None
        except Exception as e:
            raise UrlErr(e)

    @typed
    def scheme(u: Url) -> Str:
        try:
            return urlparse(u).scheme
        except Exception as e:
            raise UrlErr(e)
    protocol = scheme

    class query:
        @typed
        def __new__(cls: Any, u: Url) -> Str:
            try:
                return urlparse(u).query
            except Exception as e:
                raise UrlErr(e)

        @typed
        def params(u: Url) -> Dict(Str, List(Str)):
            try:
                query = parse_qs(urlparse(u).query)
                query_dict = {}
                for key, values in query.items():
                    if len(values) == 1:
                        query_dict[key] = values[0]
                    else:
                        query_dict[key] = values

                return query_dict

            except Exception as e:
                raise UrlErr(e)

    @typed
    def netloc(u: Url) -> Maybe(Str):
        try:
            return urlparse(u).netloc
        except Exception as e:
            raise UrlErr(e)

    @typed
    def path(u: Url) -> Maybe(Str):
        try:
            return urlparse(u).path
        except Exception as e:
            raise UrlErr(e)

    @typed
    def port(u: Url) -> Maybe(Str):
        try:
            return urlparse(u).port
        except Exception as e:
            raise UrlErr(e)

    @typed
    def base_url(u: Url) -> Maybe(Str):
        try:
            base_url = []
            if url.scheme(u): base_url.append(url.scheme(u) + "://")
            if url.netloc(u): base_url.append(url.netloc(u))
            if url.path(u):   base_url.append(url.path(u))
            return ''.join(base_url)
        except Exception as e:
            raise UrlErr(e)

