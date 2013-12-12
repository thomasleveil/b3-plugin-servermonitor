import logging

if __name__ == '__main__':
    from tests import logging_disabled
    with logging_disabled():
        from b3.fake import fakeConsole
    from b3.output import VERBOSE
    logging.getLogger('output').setLevel(VERBOSE)

    print "\n" + "- " * 50
    from servermonitor import BF3ServerInfo
    s = BF3ServerInfo(fakeConsole, '109.70.149.112:47200', "{address} : {map} [{gamemode}] {players}/{max_players} {name}")
    s.update()
    print repr(s.data)
    print repr(s.info)
