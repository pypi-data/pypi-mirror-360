def morality():
    """

    I'm sorry Cady, I'm afraid I can't do that.

    In an early scene in the film M3GAN 2.0 (Blumhouse 2025),
    12-year-old Cady is seen attempting to import morality,
    and getting an error that the package does not exist.

    What is not shown is, if that system included *uncurated*
    third-party packages in its search, 'morality' could have
    done literally ANYTHING.

    Thankfully I managed to get there first in PyPI so this
    function does nothing.  But someone else could have given
    you a Trojan horse - which would eventually be removed
    from the library, but removal can take time, so you
    should always *check* packages before you use them!

    The purpose of *this* package is simply to serve as a
    gentle warning that you weren't supposed to imitate what
    Cady did in that scene.

    "So fill me in: did we save the world or what?" - M3GAN

    """
    import sys
    sys.stderr.write(morality.__doc__)

version = "0.0.2"
