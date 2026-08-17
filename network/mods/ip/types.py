from typed import Str, Filtered, prop
from network.helper.ip import _is_ipv4, _is_ipv6

IPv4 = Filtered(Str, _is_ipv4)
IPv6 = Filtered(Str, _is_ipv6)

prop.set.nameof(IPv4, "IPv4")
prop.set.nameof(IPv6, "IPv6")

prop.set.nullof(IPv4, "127.0.0.1")
