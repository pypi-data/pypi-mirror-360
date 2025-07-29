Filing Tickets against Pyruvate
===============================

If you'd like to file a bug or a feature request for Pyruvate, the best option is to `open an issue on Gitlab <https://gitlab.com/tschorr/pyruvate/issues/new>`_.

If you're filing a feature request, please remember:

* Feature requests significantly expanding the scope of Pyruvate outside the description in `the readme <https://gitlab.com/tschorr/pyruvate/blob/master/README.rst>`_ will probably be rejected.
* Please check the previously opened issues to see if somebody else has suggested it first.
* Consider submitting a merge request to add the feature instead, if you're confident it fits within the above

If you're filing a bug, please remember:

* To provide detailed steps to reproduce the behaviour
* If possible, provide a test (Python or Rust) which reproduces the behaviour
* Consider submitting a merge request to fix the bug instead

Helping Develop Pyruvate
========================

If you'd like to help develop Pyruvate further, please consider submitting a merge request! I'm very keen to improve Pyruvate further and will enthusiastically merge good merge requests.
Before submitting a merge request to fix a bug or add a new feature, please check the lists above to ensure it'll be accepted.

To be more specific, before submitting your merge request please ensure:

* You haven't broken the existing tests.
* You've added relevant tests for the bug you're fixing/the new feature you're adding. The ultimate goal is to further increase test coverage, but it should at least be kept at the current level.
* You've updated the changelog (CHANGES.rst) to mention your contributions.
* You've updated the docs (README.rst) to detail any changes you've made to the public interface.
* Your change is backward compatible (or you've explicitly said if it's not; this isn't great, but will be considered).
