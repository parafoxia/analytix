# Copyright (c) 2021-present, Ethan Henderson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = (
    "BadRequest",
    "Unauthorised",
    "Forbidden",
    "NotFound",
)

from analytix.errors import APIError


class BadRequest(APIError):
    """Exception thrown when the YouTube Analytics API returns a 400.

    Parameters
    ----------
    code : str or int
        The error code.
    message : str
        The error message.

    !!! important
        This only happens when analytix has failed to catch an invalid
        request. If you see an error like this, report it!
    """


class Unauthorised(APIError):
    """Exception thrown when the YouTube Analytics API returns a 401.

    Parameters
    ----------
    code : str or int
        The error code.
    message : str
        The error message.
    """


class Forbidden(APIError):
    """Exception thrown when the YouTube Analytics API returns a 403.

    Parameters
    ----------
    code : str or int
        The error code.
    message : str
        The error message.
    """


class NotFound(APIError):
    """Exception thrown when the YouTube Analytics API returns a 404.

    Parameters
    ----------
    code : str or int
        The error code.
    message : str
        The error message.
    """
