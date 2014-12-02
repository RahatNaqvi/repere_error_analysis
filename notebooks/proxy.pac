
function FindProxyForURL (url, host)
{
  if (
       // Les acces aux serveurs locaux passent en direct
       dnsDomainIs (host,".univ-lemans.fr") ||
       isPlainHostName (host) ||
       isInNet (host,"127.0.0.0","255.255.0.0")
      )
      return "DIRECT";
  else
      return "PROXY vproxy.univ-lemans.fr:3128";
}

