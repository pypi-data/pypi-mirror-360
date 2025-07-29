"""smokesign

A tiny helper library intended to establish WebRTC communication between peers
without relying on a central signalling / handshake server. Instead, it uses
Autonomi Scratchpads for exchanging the SDP offer/answer information.
"""

__all__ = [
    "__version__",
]

__version__: str = "0.0.1" 